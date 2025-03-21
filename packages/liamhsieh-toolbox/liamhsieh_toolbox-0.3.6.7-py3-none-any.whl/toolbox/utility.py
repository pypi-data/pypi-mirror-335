import os
import datetime
import pickle
import time
import logging
from logging.config import fileConfig
import logging
from pdb import set_trace as bp
from decimal import Decimal
from typing import (
    Literal,
    Optional
)

import numpy as np
import pandas as pd
import IPython


LOGGING_LEVEL = Literal['DEBUG','INFO','WARNING','ERROR','CRITICAL']

def file_last_update_datetime(filepath:str, datetime_only:bool=False):
    modTimesinceEpoc = os.path.getmtime(filepath)
    modificationTime = datetime.datetime.utcfromtimestamp(modTimesinceEpoc).strftime('%Y-%m-%d %H:%M')
    if datetime_only:
        return modificationTime
    else:
        return 'Last Update: \n' + modificationTime + ' UTC'


def all_dict_values_in_target_types(
    input_dict: dict,
    target_types: list,
    visible_key_only = True
) -> bool:
    """check if all values of input dictionary are in target types

    Args:
        input_dict (dict): dictionary wait to check
        target_types (list): list of types
        visible_key_only (bool, optional): only check dictionary keys not starting from underscore. Defaults to True.

    Returns:
        bool : True or False
    """
    if visible_key_only:
        return all(type(v) in target_types for k,v in input_dict.items() if not k.startswith('_'))
    else:
        return all(type(v) in target_types for k,v in input_dict.items())
    


def from_cache_if_possible(df_name:str, cache_dir:str, refresh_func:callable,**kwarg):
    """provide basic functionality to load pickle file as a variable if it exists; otherwise, call refresh_func to return the data

    Args:
        df_name (str): variable name
        cache_dir (str): path for checking the existance of pickle file
        refresh_func (callable): function to return the intended data

    Returns:
        obj: instance of intended data
    """
    cache_path=os.path.join(
        cache_dir,
        f"{df_name}.pkl"
    )
    if os.path.exists(cache_path):
        file = open(cache_path, 'rb')
        df = pickle.load(file)
        file.close()
        #df = pd.read_pickle(cache_path)
    else:
        df = refresh_func(**kwarg)
        file = open(cache_path, 'wb')
        pickle.dump(df, file)
        file.close()
        #pd.to_pickle(df, cache_path)
    return df



def adjust_decimal_types(df, precision:int=8):
    precision_str = '0.' + '0' * (precision - 1) + '1'  # Construct precision string
    for col in df.select_dtypes(include=[np.number], exclude=[np.bool_]).columns:
        df[col] = df[col].apply(lambda x: round(x, precision) if isinstance(x, float) else Decimal(x).quantize(Decimal(precision_str)))

    return df



def set_logger(log_level: LOGGING_LEVEL = 'INFO', use_file_config: bool = False, config_file: Optional[str] = None):
    """quick solution for setting/initializing a logger
    For a basic setup without a configuration file such as for Jupyter notebook:
            set_logget(log_level='DEBUG')
    For setting up using a configuration file:
            set_logger(use_file_config=True, config_file='logging.ini')

    Args:
        log_level (LOGGING_LEVEL, optional): level of log. Defaults to 'INFO'.
        use_file_config (bool, optional): use configuration file or not. Defaults to False.
        config_file (Optional[str], optional): path of configuration file. Defaults to None.

    Returns:
        logger


    """
    logger = logging.getLogger()
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    if use_file_config and config_file:
        fileConfig(config_file, disable_existing_loggers=False)

    return logger


def autosave_notebook():
    IPython.display.Javascript('IPython.notebook.save_notebook()')