import logging
import math
logger = logging.getLogger("InputstreamClient")

from acelerai_inputstream import QUERY_MANAGER, VERIFY_HTTPS
from acelerai_inputstream.cache_manager import CacheManager
from acelerai_inputstream.http_aceler import AcelerAIHttpClient
from acelerai_inputstream.utils import CustomJSONEncoder, CustomJsonDecoder, load_full_object
import asyncio
from datetime import datetime
import hashlib
import os
import json
import requests
from acelerai_inputstream.models.inputstream import INSERTION_MODE, ExternalDataConnectionDTO, Inputstream, InputstreamStatus, InputstreamType


class InputstreamClient:
    """
    Client to interact with ACELER.AI inputstreams
    """

    def __init__(self, token:str, cache_options:dict = None):
        """
        Constructor for LocalInputstream
        :param token: Token to authenticate with ACELER.AI
        :param cache_options: { duration_data: int, duration_inputstream: int } | None
        """        
        self.acelerai_client = AcelerAIHttpClient(token) 
        self.cache_manager = CacheManager(cache_options)
        self.__mode = os.environ.get("EXEC_LOCATION", "LOCAL")


    def __get_inputstream(self, ikey:str) -> Inputstream:
        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        return inputstream
    
    def __get_external_connection(self, conn_key:str) -> ExternalDataConnectionDTO:
        external_connection = self.acelerai_client.get_external_data_conn_by_connkey(conn_key)
        return external_connection

    async def __allPages(self, ikey:str, query:dict, delete_id:bool) -> bool:
        headers = {
            "Authorization": f"A2G {self.acelerai_client.token}",
            "ikey": ikey,
            'Content-Type': 'application/json'
        }

        logger.info("Getting Execution Planning...")
        logger.info(f"Query: {json.dumps(query, cls=CustomJSONEncoder)}")

        res = requests.post(f"{QUERY_MANAGER}/QueryData/ExecutionPlanningFind", 
            data = json.dumps(query, cls=CustomJSONEncoder), 
            headers=headers, 
            verify=VERIFY_HTTPS
        )

        if res.status_code != 200: raise Exception(f"{res.status_code} {res.text}")

        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        logger.info(f"Getting inputstream with ikey: {ikey}, Name {inputstream.Name}  from ACELER.AI...")
        
        content = res.json(cls=CustomJsonDecoder)

        total_query     = content["data"]["total"]
        page_size:int   = content["data"]["size"]

        if total_query == 0:
            logger.info("No data found with the query provided.")
            return False
        
        page: int = 1

        if content['data']['stage'] != None:
            stage = content['data']['stage'].replace('_',' -> ')
            logger.info(f"The query stages are {stage}")
            logger.info(F"The index used in query is {content['data']['indexName']}")
        
        elif inputstream.InputstreamType !=InputstreamType.Native:
            logger.info(f"Complex query the explain was not saved")
        
        tasks = []
        total_pages:int = math.ceil(total_query / page_size)
        if total_query == 0: return False

        logger.info('Downloading data, please wait...')
        logger.info(f"Total pages: {total_pages}")
        start_time = datetime.utcnow()
        for page in range(1, total_pages + 1):
            tasks.append(self.acelerai_client.fetch_page(ikey, query, delete_id, page, page_size))
        await asyncio.gather(*tasks)

        end_time = datetime.utcnow()
        logger.info(f"Total time for downloading {total_pages} pages: {round((end_time - start_time).total_seconds()/60, 2)} minutes")

        return True


    async def __allData(self, ikey, query):
        headers = {
            "Authorization": f"A2G {self.acelerai_client.token}",
            "ikey": ikey,
            'Content-Type': 'application/json'
        }

        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        logger.info(f"Getting inputstream with ikey: {ikey}, Name {inputstream.Name}  from ACELER.AI...")
        
        if not os.path.exists(f".acelerai_cache/")               : os.mkdir(f".acelerai_cache/")
        if not os.path.exists(f".acelerai_cache/data/")          : os.mkdir(f".acelerai_cache/data/")
        if not os.path.exists(f".acelerai_cache/data/{ikey}/")   : os.mkdir(f".acelerai_cache/data/{ikey}/")

        logger.info('Downloading data, please wait...')
        start_time = datetime.utcnow()
        
        tasks = []
        tasks.append(self.acelerai_client.fetch_bigpage(ikey, query))            
        await asyncio.gather(*tasks)

        query_str = json.dumps(query, cls=CustomJSONEncoder)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()
        file_name = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"
        if not os.path.exists(file_name)   : return False

        end_time = datetime.utcnow()
        logger.info(f"Total time for downloading all data: {round((end_time - start_time).total_seconds()/60, 2)} minutes")
    
        return True


    async def __get_data(self, ikey:str, query:str | dict, mode:str, cache:bool, delete_id:bool=True) -> list[dict]:
        try:
            logger.info(f"Cache: {cache}")
            logger.info(f"Mode: {self.__mode}")
            # TODO: si el find y el find_one pueden compartir el mismo query_hash, dando error
            query_str = json.dumps(query, cls=CustomJSONEncoder)
            query_hash = hashlib.sha256(query_str.encode()).hexdigest()

            logger.info(f"Getting data...")

            if not cache:
                if os.path.exists(f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"):
                    os.remove(f".acelerai_cache/data/{ikey}/{query_hash}.msgpack")

            data = self.cache_manager.get_data(ikey, query_hash) if cache and self.__mode=='LOCAL' else None
            if data is None:
                has_data = False
                if   mode == "find"     :         has_data = await self.__allPages(ikey, query, delete_id)
                elif mode == "find_one" :         has_data = await self.acelerai_client.find_one(ikey, query)
                elif mode == "aggregate":         has_data = await self.acelerai_client.aggregate(ikey, query)
                if   mode == "find_singlethread": has_data = await self.__allData(ikey, query)
                
                # if the query or result is empty, return empty list
                if has_data:
                    self.cache_manager.set_data(ikey, query_hash)
                    output_file = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"
                    data = load_full_object(output_file)
                else:
                    return []

            return data
        except Exception as e:
            raise e


    def get_inputstream_schema(self, ikey:str) -> dict:
        """
        return Inputstream schema
        params:
            ikey: str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        inputstream = self.__get_inputstream(ikey)
        return json.loads(inputstream.Schema)


    async def find_internal(self, ikey:str, query:dict, cache:bool=True, delete_id:bool=True, slow_query:bool=False):
        """
        return data from inputstream
        params:
            ikey: str
            query: dict
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        if slow_query == True:
            mode = "find_singlethread"
        else:
            mode = "find"
        return await self.__get_data(ikey, query, mode, cache, delete_id)
    
    
    async def find_external(self, ikey:str, dynamic_values:str | dict = {}, cache:bool=True, slow_query:bool=False):
        """
        return data from inputstream
        params:
            ikey: str
            query: dict
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        if slow_query == True:
            mode = "find_singlethread"
        else:
            mode = "find"
        return await self.__get_data(ikey, dynamic_values, mode, cache, False)


    async def find_one(self, ikey:str, query:dict, cache:bool=True):
        """
        return one data from inputstream
        params:
            collection: str
            query: dict
        """
        mode = "find_one"

        data = await self.__get_data(ikey, query, mode, cache)
        if len(data) == 0: return None
        return data[0]


    async def execute_query_external(self, conn_key:str, query:str | dict, cache:bool=True):
        """
        return data from external inputstream
        Please note: if your connection is to MongoDB, the query must be as follows: {"collection_name":"your_collection", "query":'{your_query}'}
        params:
            conn_key: str
            query: dict | str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        try:   
            if isinstance(query, dict):
                query = json.dumps(query, cls=CustomJSONEncoder)
            if not isinstance(query, str): raise Exception("Query must be a string or a dictionary")
        
            query_str = json.dumps(query, cls=CustomJSONEncoder)
            query_hash = hashlib.sha256(query_str.encode()).hexdigest()
            
            logger.info('Downloading data, please wait...')
            start_time = datetime.utcnow()

            if not cache:
                if os.path.exists(f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack"):
                    os.remove(f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack")
                    
            data = self.cache_manager.get_data(conn_key, query_hash) if cache and self.__mode=='LOCAL' else None
            has_data = False
            if data is None:
                tasks = []
                tasks.append(self.acelerai_client.execute_external_query(conn_key, query))
                await asyncio.gather(*tasks)
                has_data = True

                if has_data: 
                    self.cache_manager.set_data(conn_key, query_hash)
                    output_file = f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack"
                    data = load_full_object(output_file)
                            
            end_time = datetime.utcnow()
            logger.info(f"Total time for downloading all data: {round((end_time - start_time).total_seconds()/60, 2)} minutes")
            
            return data

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
    

    async def execute_command_external(self, conn_key:str, query:str | dict):
        """
        return if command was executed successfully or not
        params: 
            conn_key: str
            query: dict | str
            cache: bool = True -> if True, use cache if exists and is not expired 
        """
        try:     
            if isinstance(query, dict):
                query = json.dumps(query, cls=CustomJSONEncoder)
            if not isinstance(query, str): raise Exception("Query must be a string or a dictionary")
            
            result = await self.acelerai_client.execute_external_command(conn_key, query)
            if result: return True
            return False
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False
        
        
    async def get_data_aggregate(self, ikey:str, pipeline: list[dict], cache:bool=True):
        """
        return data from inputstream
        params:
            ikey: str
            query: list[dict]
        """
        if not all(isinstance(x, dict) for x in pipeline):      raise Exception("Invalid pipeline, the steps must be dictionaries")
        if len(pipeline) == 0:                                  raise Exception("Invalid pipeline, length must be greater than 0" )
        if any("$out" in x or "$merge" in x for x in pipeline): raise Exception("Invalid pipeline, write operations not allowed"  )

        mode = "aggregate"
        return await self.__get_data(ikey, pipeline, mode, cache)  


    async def __validate_data_async(self, d, schema, schema_validator):
        try:
            schema_validator(d)
            return None  # Si no hay errores, retornamos None
        except Exception as e:
            return f"Error validating data: {e}"  # Devolvemos el error


    # TODO: remplazar el ikey por el conn_key
    async def insert_data_external(self, conn_key:str, data:list[dict], table: str, batch_size:int=1000, slow_insert:bool=False):
        """
        insert data into external connection
        params:
            ikey: str -> key connection
            data: list[dict] -> data to insert
            table: str -> table name
            batch_size: int = 1000 -> batch size for insert data
        """
        
        # validate
        if not isinstance(data, list): raise Exception("Data must be a list of dictionaries")
        if table == '': raise Exception("Table name is required when inserting to a native inputstream")

        logger.info('Inserting data, please wait...')
        
        if slow_insert == True:
            start_time = datetime.utcnow()
            result = await self.acelerai_client.insert_data_big_external(conn_key, table, data)
            endt = datetime.utcnow()
            if result:
                logger.info(f'SUCCESS: {len(data)} registries inserted successfully in {(endt - start_time).total_seconds() / 60} minutes')
            else:
                logger.info(f'FAIL: inserting {len(data)} records, total time:  {(endt - start_time).total_seconds() / 60} minutes, please see messages for more info.')
        else:
            start_time = datetime.utcnow()
            tasks, batch_idx = [], 1
            batch_idx = 1
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                tasks.append(self.acelerai_client.insert_data_external(conn_key, table, batch, batch_idx, batch_size))
                batch_idx += 1
            result = await asyncio.gather(*tasks)
            endt = datetime.utcnow()
            if False not in result:
                logger.info(f'SUCCESS: {len(data)} registries inserted successfully in {(endt - start_time).total_seconds() / 60} minutes')
            else:
                logger.info(f'FAIL: inserting {len(data)} records, total time:  {(endt - start_time).total_seconds() / 60} minutes, please see messages for more info.')


    async def insert_data(self, 
        ikey:str, 
        data:list[dict], 
        mode:INSERTION_MODE = INSERTION_MODE.REPLACE, 
        wait_response = True, 
        batch_size:int = 10000,
        validate_schema = True
    ):
        """
        validate data against inputstream JsonSchema and insert into inputstream collection
        params:
            ikey: str
            data: list[dict]
            mode: INSERTION_MODE = INSERTION_MODE.REPLACE -> insertion mode
            wait_response: bool = True -> if True, wait for response from server
            batch_size: int = 1000 -> batch size for insert data
            cache: bool = True -> if True, use cache if exists and is not expired
            validate_schema: bool = True -> if True, validate data against inputstream schema
        """
        
        start = datetime.utcnow()
        inputstream:Inputstream = self.__get_inputstream(ikey)
        logger.debug(f'Demoró {(datetime.utcnow() - start).total_seconds()} segs en obtener el inputstream')

        if inputstream.InputstreamType == InputstreamType.Native:  raise Exception("Inputstream must be type InSystem, please use the insert_data_external method")
        if not isinstance(data, list):  raise Exception("Data must be a list of dictionaries")
        if inputstream.Status != InputstreamStatus.Exposed:
            logger.warning(f"Inputstream is not exposed, status: {inputstream.Status}")
            self.acelerai_client.send_example(ikey, data[0])
            logger.info(f"Example data sent to ACELER.AI for schema validation, please expose the inputstream to insert data.")
            return

        # if validate_schema:
        #     start = datetime.utcnow()
        #     schema = json.loads(inputstream.Schema)
        #     schema_validator = fastjsonschema.compile(schema)
        #     resultados = await asyncio.gather(*(self.__validate_data_async(d, schema, schema_validator) for d in data))

        #     # Manejo de errores
        #     errores = [error for error in resultados if error is not None]
        #     if errores:
        #         for error in errores:
        #             logger.error(error)
        #         raise Exception("Hubo errores durante la validación de datos.")
            
        #     logger.debug(f'Demoró {(datetime.utcnow() - start).total_seconds()} segs en validar los datos')

        logger.info('Inserting data, please wait...')
        start = datetime.utcnow()
        tasks, batch_idx = [], 1
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            tasks.append(self.acelerai_client.insert_data(ikey, batch, mode, wait_response, batch_idx, len(batch)))
            batch_idx += 1
        await asyncio.gather(*tasks)
        
        logger.info(f'{len(data)} registries sent successfully in {(datetime.utcnow() - start).total_seconds() / 60} minutes')
        

    async def remove_documents(self, ikey:str, query:dict) -> int:
        """
        delete data from inputstream
        params:
            ikey: str
            query: dict
        """
        docs = await self.acelerai_client.remove_documents(ikey, query)
        return docs
 

    async def clear_inputstream(self, ikey:str) -> int:
        """
        delete all data from inputstream
        params:
            ikey: str
        """
        docs = await self.acelerai_client.clear_inputstream(ikey)
        return docs