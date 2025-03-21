import pathlib
import configparser
import os
from pdb import set_trace as bp
import logging
from typing import Dict, Literal, List
from functools import lru_cache
from collections.abc import Generator

import cx_Oracle
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import text as sql_text

from ..dtype_mapping import map_db_datatypes_to_dtype, get_column_names_and_date_types

_cache_mode_options = Literal[0,1,2]


def parse_db_access(config_path: str, section_name:str)->Dict:
    """parse the configuration file to acquire required information for connecting supporting DBs

    Args:
        config_path (str): path of configuration file
        section_name (str): section name for db access in config file

    Returns:
        Dict: access information
    """
    logger = logging.getLogger(__name__)
    try:
        config = configparser.ConfigParser()
        _ = config.read(config_path)

        db_access = config._sections[section_name]
        db_access["ssl"] = config._sections["SSL"]
        # db_access = {}
        # db_access["server_username"] = config.get(section_name, 'username')

        if "db_type" not in db_access.keys(): raise ValueError("db_type is mandatory for setting db.ini")
        if db_access["db_type"]=="mssql" and "driver" not in db_access.keys():
            db_access["driver"] = check_odbc_driver()[0]

        return db_access

    except Exception as e:
        print(f"function parse_db_access got exception message: {e}")
        logger.info(
            "unable to parse from configuration file:/n {config_path} for database access information"
        )

def estimate_chunk_size(
        conn_str: str, 
        query: str,  
        cached_file_type:str='parquet.gzip', 
        compression_method:str='gzip',
        threshold_size:float=10.0, 
        sample_nrow:int = 2000,
        **kwargs
        )->int:
    """This function will estimate the idea chunk size which will result the output file around desired size

    Args:
        conn_str (str): connection string for creating database connection object; it has to meet the requirement for sqlalchemy 
        query (str): query statement
        cached_file_type (str, optional): intended file type in these options ['parquet.gzip','pickle','csv']. Defaults to 'parquet.gzip'.
        compression_method (str, optional): compression method for output file. Defaults to 'gzip'.
        threshold_size (float, optional): desired size for output file in MB. Defaults to 10.0.
        sample_nrow (int, optional): sample size in number of rows. Defaults to 2000.

    Returns:
        int: number of rows as chunk size

    For more information regarding conn_str, see https://docs.sqlalchemy.org/en/20/core/engines.html    
    """
    logger = logging.getLogger(__name__)

    executor = {
        'parquet.gzip':pd.DataFrame.to_parquet,
        'pickle':pd.DataFrame.to_pickle,
        'csv':pd.DataFrame.to_csv
    }

    if cached_file_type not in executor.keys():
        logger.error(f"Receive unsupported value {cached_file_type} for argument cached_file_type; current supportting list:\n {executor.keys()}")
        raise ValueError(f"Receive unsupported value {cached_file_type} for argument cached_file_type; current supportting list:\n {executor.keys()}")
    
    eng = create_engine(conn_str)
    conn = eng.connect() 
    query = sql_text(query)
    logger.info(f"estimate chunk size for query {query} targeting on a threshold file size= {threshold_size}MB for {cached_file_type} using {sample_nrow} rows as sampling size")

    try:
        result = conn.execute(query)
        chunk = result.fetchmany(sample_nrow)
        actual_number_of_rows = len(chunk)
        sample_df = load_query_result_into_df_with_intended_dtypes(
                chunk,
                result
            )

    except Exception as e:
        logger.debug(f"not able to get sample dataframe for estimating the chunk size via following query \n {query} \n , got error message: {e}")
        conn.close()
    finally:
        conn.close()

    # Convert the sample data to desired format and get its size
    sample_file_path = f'sample.{cached_file_type}'
    executor[cached_file_type](sample_df, f'sample.{cached_file_type}', compression=compression_method)
    sample_file_size = os.path.getsize(sample_file_path)

    # Define the intended threshold file size in bytes (e.g., 15 MB)
    intended_threshold_size = threshold_size * 1024 * 1024  # threshold_size in bytes

    # Calculate the estimated chunk size based on the sample file size; be noticed that actual number of rows may be less than sample size
    if actual_number_of_rows< sample_nrow:
            sample_nrow = actual_number_of_rows
    estimated_chunk_size = int((intended_threshold_size / sample_file_size) * sample_nrow)

    # Cleanup: Remove the sample file
    os.remove(sample_file_path)
    logger.info(f"estimated chunk size is {estimated_chunk_size}")

    return estimated_chunk_size


def read_sql_query_in_chunks_sqlalchemy(query, engine, chunk_size:int, enforce_dtype:bool)->Generator:
    """
    Retrieve data from a database in assigned-sized chunks.

    Parameters:
        query: SQL query to execute.
        engine: SQLAlchemy engine object.
        threshold: Maximum number of rows to fetch in each chunk.

    Returns:
        A generator that yields DataFrames for each chunk of data.
    """
        
    # Create a connection
    conn = engine.connect() 
    
    # Execute the query
    query = sql_text(query)
    result = conn.execute(query)

    # Get the column names from the cursor description
    column_names = result.keys()

    # Initialize variables for chunk iteration
    chunk = result.fetchmany(chunk_size)

    while chunk:
        if enforce_dtype:
            chunk_data = load_query_result_into_df_with_intended_dtypes(
                chunk,
                result
            )
        else:# Create a DataFrame from the fetched chunk
            chunk_data = pd.DataFrame(chunk, columns=column_names)
        
        # Convert numeric columns to either int or float
        #chunk_data = only_int_float_for_numeric_columns(chunk_data)

        yield chunk_data

        # Fetch the next chunk
        chunk = result.fetchmany(chunk_size)


def load_query_result_into_df_with_intended_dtypes(rs, result, mapper:dict = None)->pd.DataFrame:
    """Turn query record set into Pandas dataframe with intended dtype

    Args:
        rs : record set, i.e.,sequence[row]. Returns of sqlalchemy result.fetchall() or .fetchmany() 
        result : sqlalchemy CursorResult
        mapper (dict): map out database data type and dtypes for dataframe

    Returns:
        pd.DataFrame
    """
    if mapper is None:
        mapper = map_db_datatypes_to_dtype
    column_names, db_data_types = get_column_names_and_date_types(result)

    database_type = result.connection.dialect.name
    database_driver = result.connection.engine.driver

    # create intended dtype dict via iterating over column names and mapping the database data type
    intended_dtypes = {col_name:mapper(database_type,database_driver,db_data_type) for col_name, db_data_type in zip(column_names, db_data_types)}

    return pd.DataFrame(rs,columns=column_names).astype(intended_dtypes)

def read_sql_query_in_chunks_oracle(query:str, connection, chunk_size=20000):
    """
    Retrieve data from an Oracle database in adaptive-sized chunks using cx_Oracle.

    Parameters:
    - query: SQL query to execute.
    - connection: cx_Oracle Database connection object; Establish a connection to the Oracle database by cx_Oracle.connect(connection_string) and the format of connection_string is "user/password@hostname:1521/your_service_name"
    - threshold: Maximum number of rows to fetch in each chunk (default is 20,000).

    Returns:
    - A generator that yields DataFrames for each chunk of data.
    """

    # Create a cursor
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(query)

    # Get the column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Initialize variables for chunk iteration
    chunk = cursor.fetchmany(chunk_size)

    while chunk:
        # Create a DataFrame from the fetched chunk
        chunk_data = pd.DataFrame(chunk, columns=column_names)

        yield chunk_data

        # Fetch the next chunk
        chunk = cursor.fetchmany(chunk_size)



def check_odbc_driver():
    from pyodbc import drivers
    # Get a list of installed ODBC drivers
    odbc_drivers = drivers()
    found_drivers=[]
    # Check for SQL Server drivers and print their names
    sql_server_drivers = [driver for driver in odbc_drivers if 'SQL Server' in driver]
    if sql_server_drivers:
        
        for driver in sql_server_drivers:
            if "ODBC" in driver:
                found_drivers.append(driver)
    else:
        raise Exception("No SQL Server ODBC drivers are found. Please set availavble driver in db.ini file for your SQL Server")

    return found_drivers


class DBConnector:
    default_port = {
            "ORACLE":1521,
            "MSSQL":1433,
            "AZURE-BLOB":None,
            "MARIADB":3307,
            "SNOWFLAKE":443
        }

    def __init__(self, db_access, via_ssl = False, **kwargs):
        """connecting object for a database

        Args:
            db_access (dict): return of parse_db_access()
            via_ssl (bool): connect via ssl
        """
        self.logger = logging.getLogger(__name__)
        self.cache_mode = 0
        self.cache_dir = "."

        
        self._db_access = db_access
        self._via_ssl = via_ssl
        if self._via_ssl:
            if "ssl" not in self._db_access.keys():
                self.logger.error("Please check db.ini and ensure secton SSL is set correctly while connecting via_ssl")

        self.queries_dir = None             
        self.__not_yet_purge = True

        self._db_type, self._port = self._check_nondefault_port()
            
    def set_cache_dir(self, cache_dir: str, cache_mode: _cache_mode_options = 1)->None:
        """set up path for directory where cached files are stored

        Args:
            cache_mode (int, optional): 0: always pull data from db
                                1: only pull data if cache doesn't exist
                                2: refresh cache before using 
                                Defaults to 0.
            cache_dir (str): directory for keeping/searching cache files; only works if cache_mode in {1,2}
        """

        self.cache_dir = cache_dir
        self.cache_mode = cache_mode
        

    def _check_nondefault_port(self)-> List:
        db_type = self._db_access["db_type"].upper()
        
        if "port" in self._db_access.keys():
            port = self._db_access["port"]
        else:
            port = self.default_port[db_type]

        return [db_type, port]
        
    def set_queries_dir(self,queires_dir: str, **kwargs)->None:
        """set up path for directory where predefined sql statement files are stored

        Args:
            queires_dir (str): path of directory
        **kwargs:
            all variables within predefiend sql queries can pass to DBConnector via keyword arguments
        """
        self.queries_dir = queires_dir
        self.query_args = dict(kwargs)

    def del_cache(self)->None:        
        """delete all cache files in cache directory
        """     
        dir = self.cache_dir
        for f in os.listdir(dir):
            if f.endswith(".pkl"):
                os.remove(os.path.join(dir, f))

    def _check_cache_dir(self)->None:
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _correct_datetime_format_for_mssql(self):
        for k,v in self.query_args.items():
            if type(v)==np.datetime64: 
                self.query_args[k] = str(v.astype('M8[D]'))

    
    def create_engine(self,**kwargs):
        if self._via_ssl:
            return create_engine(self._conn_str, connect_args = self._ssl_args,**kwargs)
        else:
            return create_engine(self._conn_str,**kwargs)
    
    def _get_mssql_conn_str(self,):
        driver_name = self._db_access["driver"]
        match driver_name:
            case str() as s if "ODBC" in s:
                conn_str=''.join(
                    [
                    'DRIVER={'+ driver_name +'};',
                    f'SERVER={self._db_access["server"]},{self._port};',
                    f'DATABASE={self._db_access["database_name"]};UID={self._db_access["server_username"]};PWD={self._db_access["server_password"]}'
                    ]
                )
                conn_str = URL.create("mssql+pyodbc", query={"odbc_connect": conn_str})

            case "FreeTDS":
                conn_str = URL.create(
                    'mssql+pyodbc',
                    username=self._db_access["server_username"],
                    password=self._db_access["server_password"],
                    host=self._db_access["server"],
                    port=self._port,
                    database=self._db_access["database_name"],
                    query={
                        "driver": "FreeTDS",
                        "TrustServerCertificate": "yes"  
                    })
        return conn_str

    def _get_conn_str_for_cx_Oracle(self):
        return f"{self._db_access.server_username}/{self._db_access.server_password}@{self._db_access.server}:{self._port}/{self._db_access.service_name}"
        
    def _get_oracle_conn_str(self):
        return f'oracle+cx_oracle://{self._db_access["server_username"]}:{self._db_access["server_password"]}@{self._db_access["server"]}:{self._port}/?service_name={self._db_access["service_name"]}'

    def _get_snowflake_conn_str(self):
        return URL.create(
            'snowflake',
            username = self._db_access["user"],
            password = self._db_access["password"],
            host = self._db_access["account"] + '.snowflakecomputing.com',
            #database = 'SUPPLY_CHAIN',
            query = {
                #"role":'if so',
                "warehouse": self._db_access["warehouse"],
                "account": self._db_access["account"].split("-")[1].upper(),
                #"authenticator":'externalbrowser'
            }
        )

    
    def _get_mariadb_conn_str(self):
        return f"mysql+pymysql://{self._db_access['user']}:{self._db_access['password']}@{self._db_access['host']}:{self._db_access['port']}/{self._db_access['database']}"

    @property
    def _ssl_args(self):    
        return {"ssl":self._db_access["ssl"]}

    @property
    def _conn_str(self):

        conn_str = {
            "MSSQL": self._get_mssql_conn_str,
            "ORACLE": self._get_oracle_conn_str,
            "MARIADB": self._get_mariadb_conn_str,
            "SNOWFLAKE": self._get_snowflake_conn_str
        }

        return conn_str[self._db_type]()

    def load_args_for_predefined_query(
            self, 
            query_file: str,
            query_args:dict=None
            )->str:
        """This method returns the query statement for pulling data by filling in query arguments for predefined query

        Args:
            query_file (str): name of predifined query file (extension should be .sql)
            query_args (dict, optional): dictionary of query arguments. Defaults to None.

        Returns:
            str: sql query statement
        """
        
        if query_args is None:
            query_args = self.query_args

        if  self.queries_dir not in query_file:
            query_file = os.path.join(self.queries_dir, f"{query_file}.sql")

        with open(query_file, 'r') as fname:
            query = fname.read()
            query_str = query.format(
            **query_args
            )
        return query_str

    def dump_to_db(
            self,
            df,
            dest_tb_name,
            is_fast_executemany = True,
            index = False,
            index_label=None,
            if_exists = 'append',
            dtype = None,
            chunksize = None,
            method=None,
    ):
        """dump a dataframe to a specific table

        Args:
            df (_type_): _description_
            dest_tb_name (_type_): _description_
            is_fast_executemany (bool, optional): _description_. Defaults to True.
            is_index (bool, optional): add index automatically. Defaults to False.
            if_exists (str, optional): what to do while data exists in table. 'fail', 'replace', 'append'. Defaults to 'append'.
                                    How to behave if the table already exists.
                                    fail: Raise a ValueError.
                                    replace: Drop the table before inserting new values.
                                    append: Insert new values to the existing table.
            dtype (dict, optional): dict to dedicate the dtype for each columns. Defaults to None.
                                    example dtype:
                                    using df column names as keys
                                    {
                                    'datefld': sqlalchemy.DateTime(), 
                                    'intfld':  sqlalchemy.types.INTEGER(),
                                    'strfld': sqlalchemy.types.NVARCHAR(length=255)
                                    'floatfld': sqlalchemy.types.Float(precision=3, asdecimal=True)
                                    'booleanfld': sqlalchemy.types.Boolean
                                    }   
        """
        try: 
            # conn_str = self._conn_str
            # eng = create_engine(conn_str)

            eng = self.create_engine()

            with eng.connect() as conn:
                df.to_sql(dest_tb_name, conn, if_exists = if_exists, index = index, index_label=index_label, chunksize=chunksize, dtype=dtype,method=method)
        
        except Exception as e:
            self.logger.error(e) 


    def exec_SQL(self,statement):
        """execute general sql statement

        Args:
            statement (str): SQL statement

        Returns:
            CursorResult: instance of sqlalchemy.engine.cursor.CursorResult
        """
        eng = self.create_engine()
        try:
            with eng.connect() as conn:
                rs = conn.execute(sql_text(statement))
                conn.commit()
                return rs
        except Exception as e:
            self.logger.error(e)

    def pull_SQL(
            self,
            query,
            chunk_size:int=None,
            **kwargs
    ):
        """simply pulling data with SQL query; efficient pulling by chunks should consider using method pull_predefined_query  
        Args:
            query (str): sql statement
            chunk_size (int): pull by chunk if assigned (optional); using Pandas implementation for pulling by chunks
        Return:
            df (DataFrame): results of executing SQL statement if it has return and chunk_size<2 or None
            dfs_generator (Generator): generator for all resulted chunks if chunk_size>1
        """
        try:
            # conn_str = self._conn_str
            # eng = create_engine(conn_str)

            eng = self.create_engine()

            with eng.connect() as conn:
                if chunk_size in (None,1):
                    df = pd.read_sql(
                        sql_text(query),
                        conn,
                    )
                    return df
                else:
                    dfs_generator = pd.read_sql(
                        sql_text(query),
                        conn,
                        chunksize=chunk_size
                    )
                    return dfs_generator
        except Exception as e:
            self.logger.error(e)       

    @staticmethod
    def dump_dfs_generator(dfs_generator, keys:list=None):
        """Dump DataFrames from a generator into a dictionary.

        Args:
            dfs_generator (generator): A generator that yields DataFrames.
            keys (list or None, optional): List of keys for the generated dictionary.
                If None, numerical indices will be used as keys. Default is None.

        Returns:
            dict: A dictionary containing DataFrames from the generator, with keys as specified.

        Example:
        ```
        # Generate sample DataFrames
        num_dataframes = 5
        rows_per_dataframe = 10
        dataframes = generate_dfs(num_dataframes, rows_per_dataframe)

        # Test the dump_dfs_generator method
        keys = ['DF1', 'DF2', 'DF3', 'DF4', 'DF5']  # Example keys
        result = dump_dfs_generator(dataframes, keys)
        print(result)
        ```

        This function takes a generator yielding DataFrames and returns a dictionary
        with specified keys (or numerical indices if keys are not provided), where each
        key corresponds to a DataFrame yielded by the generator.
        """

        if keys is None:
            return {i: chunk_df for i, chunk_df in enumerate(dfs_generator)}
        else:
            return {i: chunk_df for i, chunk_df in zip(keys,dfs_generator)}

    def pull_predefined_query(
        self,
        query_name,
        chunk_mode:bool=False,
        **kwargs
    ):
        """pull data by predefined sql statement file including variables.

        Args:
            query_name (str): name of a predefined sql statement file; no extension needed
            chunk_mode (bool): pull data by chunk mode or not
            
            kwargs: 
                    - chunk_size (int): number of rows for a chunk; estimate_chunk_size() will be trigger when chunk_size is not assigned. Therefore, more details for accepted kwargs could check description of function estimate_chunk_size()
                    - capitalize_column_name (bool): convert all column name to uppercase or not
                    - enforce_dtype (bool): convert database data types to intended dtypes for resulted dataframe; only enables for chunk_mode
        Raises:
            Exception: queries_dir can't be empty, set by method set_queries_dir() first
            ValueError: if <query_name>.sql can't be found in queries_dir

        Returns:
            DataFrame: result of executing SQL statement
        """
        if self.queries_dir is None:
            self.logger.error("Use method set_queries_dir(queries_dir:str) to enable method pull_predefined_query") 
            raise Exception("Use method set_queries_dir(queries_dir:str) to enable method pull_predefined_query")
        
        if f"{query_name}.sql" not in os.listdir(self.queries_dir):
            self.logger.error('Query for {} is undefined'.format(query_name))
            raise ValueError('Query for {} is undefined'.format(query_name))
        
        executor = {
            "do_chunk":self._run_chunk_mode,
            0: self._run_cache_mode_0,
            1: self._run_cache_mode_1,
            2: self._run_cache_mode_2,
        }

        if chunk_mode:    
            dfs_generator = executor["do_chunk"](query_name,**kwargs)
            return dfs_generator
        else:
            df = executor[self.cache_mode](query_name,**kwargs)
            if "capitalize_column_name" in kwargs and kwargs["capitalize_column_name"]:
                df.columns = df.columns.str.upper()
            
            return df

    def _run_chunk_mode(self, query_name:str, chunk_size:int=None, enforce_dtype: bool=False, **kwargs)->Generator:

        conn_str = self._conn_str

        query_file = os.path.join(self.queries_dir, f"{query_name}.sql")
        query_str= self.load_args_for_predefined_query(query_file,{**self.query_args,**kwargs})
     
        if chunk_size is None:
            eng = self.create_engine()
            chunk_size = estimate_chunk_size(
                conn_str,
                query_str,
                **kwargs
            )

        eng = self.create_engine()
        
        dfs_generator = read_sql_query_in_chunks_sqlalchemy(
                            query = query_str,
                            engine = eng,
                            chunk_size = chunk_size,
                            enforce_dtype = enforce_dtype
                        )

        return dfs_generator

        
    def _run_cache_mode_0(self,query_name, **kwargs):
        query_file = os.path.join(self.queries_dir, f"{query_name}.sql")
        query_str= self.load_args_for_predefined_query(query_file,{**self.query_args,**kwargs})

        try:
            df = self.pull_SQL(query_str)
        except Exception as e:
            self.logger.info(f"predefined query {query_name} got exception message: {e}")
        return df

    def _run_cache_mode_1(self,query_name, **kwargs):
        pickle_path = os.path.join(self.cache_dir, f"{query_name}.pkl")
        if f"{query_name}.pkl" in os.listdir(self.cache_dir):  
            df = pd.read_pickle(pickle_path)
        else:
            df = self._run_cache_mode_0(query_name)
            df.to_pickle(pickle_path)
        return df

    def _run_cache_mode_2(self,query_name, **kwargs):
        if self.__not_yet_purge: 
            self._del_cache()
            self.__not_yet_purge = False

        df = self._run_cache_mode_1(query_name)
        return df

if __name__ == "__main__":
    pass 