"""
This mapper is for converting the database data type to intended dtype for Pandas Dataframe
"""
import sqlalchemy
import numpy as np

# This dtype_mapper plays as a default setting, but any specific version can be applied for map_db_datatypes_to_dtype by passing the following format as arg datatype_mapper
dtype_mapper = {
    ('oracle', 'cx_oracle'): {
        "<cx_Oracle.DbType DB_TYPE_NUMBER>": np.float32,
        "<cx_Oracle.DbType DB_TYPE_VARCHAR>": 'string',
        "<cx_Oracle.DbType DB_TYPE_TIMESTAMP_LTZ>": 'datetime64[ns]'
        # Add more mappings as needed
    },
    ('mssql', 'pyodbc'): {
        "<class 'int'>": np.int32,
        "<class 'str'>": 'string',
        "<class 'float'>": np.float32,
        # Add more mappings as needed
    }
    # Add mappings for other database types and drivers
}

def get_column_names_and_date_types(result: sqlalchemy.engine.CursorResult):
    column_names = [col[0] for col in result.cursor.description]
    db_data_types = [str(col[1]) for col in result.cursor.description]
    return column_names, db_data_types

def map_db_datatypes_to_dtype(
        database_type:str, 
        database_driver:str, 
        db_data_type:str,
        datatype_mapper:dict=dtype_mapper
        ):
    """map database data type to dtype for Pandas dataframe

    Args:
        database_type (str): engine.dialect.name where engine is Sqlalchemy Engine
        database_driver (str): engine.driver where where engine is Sqlalchemy Engine
        db_data_type (str): str(result.cursor.description[i][1]) for the ith columns of query result where result is the Sqlalchemy CursorResult
        datatype_mapper (dict): map out db data types to dtypes for dataframe

    Returns:
        type/str: dtype for Pandas
    """
    # Retrieve the intended dtype based on the provided database type, driver, and data type; 
    # NOTE: object is the default dtype if the key is not found 
    intended_dtype = datatype_mapper.get((database_type.lower(), database_driver.lower()), {}).get(db_data_type, object)

    return intended_dtype