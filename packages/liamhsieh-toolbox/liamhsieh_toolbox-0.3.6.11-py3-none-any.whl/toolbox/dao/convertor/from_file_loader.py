import json
import pathlib
import os

from sqlalchemy import create_engine
from pandas import ExcelWriter
from ..files.utility import ensure_directory_exists
#from ...container import namedtuple_from_dict, BoundFuncAsClsMethod
from .utility import DataFrameJSONEncoder

def fl_to_json(self, output_path: str = './output.json',**kwargs):
    try:
        ensure_directory_exists(output_path)
        export_file_name = f'{output_path}'

        with open(export_file_name, 'w') as fp:
            json.dump(self._pureDict, fp, cls=DataFrameJSONEncoder, indent = 4,**kwargs)
        return True
    except Exception as e:
        raise e
        

def fl_to_csv(self, output_path: str = './output.csv', index=False,**kwargs):
    """
    Save a dictionary of DataFrames to separate CSV files, with each key appended to the filename.

    Args:
        self (FileLoader): instance of FileLoader
        output_path (str): The file path for the CSV files to save.
        index (bool): insert index to csv, default is False
    """
    
    try:
        ensure_directory_exists(output_path)
        base_file_name = f"{pathlib.Path(output_path).parent.__str__()}{os.sep}{pathlib.Path(output_path).stem}"
        for key, df in self._pureDict.items():
            csv_filename = f"{base_file_name}_{key}.csv"
            df.to_csv(csv_filename, index=index,**kwargs)
        return True
    except Exception as e:
        raise e

def fl_to_sqlite(self, output_path: str = './output.db', if_exists='replace',**kwargs):
    """
    Save a dictionary of DataFrames to an SQLite database file, with each key as a table name.

    Args:
        self (FileLoader): instance of FileLoader
        output_path (str): The file path of the SQLite database file to save.
        if_exists (str) : what to do when table exists. default is 'replace'
    """
    try:
        ensure_directory_exists(output_path)
        # Create a SQLite engine that represents the database connection
        engine = create_engine(f'sqlite:///{output_path}')
        
        with engine.connect() as connection:
            for table_name, df in self._pureDict.items():
                df.to_sql(table_name, con=connection, if_exists=if_exists, index=False,**kwargs)
        return True
    except Exception as e:
        raise e


def fl_to_excel(self, output_path: str = './output.xlsx',index=False, engine='openpyxl',**kwargs):
    """
    Save a dictionary of DataFrames to an Excel file, with each key as a worksheet name.

    Args:
        self (FileLoader): instance of FileLoader
        output_path (str): The file path of the Excel file to save.
        index (bool): insert index to csv, default is False
    """
    try:
        ensure_directory_exists(output_path)
        with ExcelWriter(output_path, engine=engine) as writer:
            for sheet_name, df in self._pureDict.items():
                df.to_excel(writer, index = index, sheet_name=sheet_name,**kwargs)
        return True
    except Exception as e:
        raise e
