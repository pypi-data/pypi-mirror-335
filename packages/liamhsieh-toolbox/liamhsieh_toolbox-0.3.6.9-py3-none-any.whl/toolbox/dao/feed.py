'''
This script defines several classes that extend the functionality of Python's built-in dict type to allow attribute-style access and provide additional methods for handling data, particularly in the context of data transformation and storage. The Feed class serves as a container for data, with the option to have a hierarchical structure for managing multiple groups of data sets. The DataSet class and its nested classes provide methods for managing and transforming data within these sets. The JSE_4df class is a custom JSON encoder that handles the serialization of pandas DataFrame objects.
'''

from typing import (
    Dict,
    List,
    Literal,
    Iterable
)

import logging
import copy
import keyword
import datetime
import json
from collections import UserDict

from xmlrpc.client import boolean
from pandas.core.frame import DataFrame
import pandas as pd

from ..utility import all_dict_values_in_target_types
from ..watcher import get_obj_size
from .dtypes import dtype_auto_refine
from ..string.convert_functions import upper_and_replace_space_with_underscore

# Define a type for export mode which can be either 'stacked' or 'multi-column' while export DataFrame for PAR in DataSet
_export_mode = Literal["stacked","multi-column"]


# Define a custom dictionary class that behaves like a dictionary but allows attribute access
class liamDict(UserDict):
    # Allow attribute-style access to dictionary keys
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("liamDict object has no attribute '{key}'")
    
    # Allow attribute-style setting of dictionary keys
    def __setattr__(self, key, value):
        if key == 'data':   # <1>; Special handling for the 'data' attribute
            super().__setattr__(key, value)
            return
        self[key] = value
    
    # Override the setitem method to process keys and values before storing
    def __setitem__(self, key, value):
        key = self._get_key(key) # <2>
        value = self.handle_value(value) # <3>
        super().__setitem__(key, value) # <4>
    
    # Override the getitem method to process keys before retrieving
    def __getitem__(self, key):
        key = self._get_key(key)
        return super().__getitem__(key) # <5>
    
    # Process the key to avoid conflicts with class attributes or Python keywords
    def _get_key(self, key):
        if hasattr(self.__class__, key) or keyword.iskeyword(key): # <6>
            key += '_'
        return key

    # Recursively convert nested dictionaries to liamDict and process lists
    def handle_value(self, value):
        if isinstance(value, dict):
            value = liamDict(value)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                value[i] = self.handle_value(item)
        return value

# Define a dictionary class that allows attribute access and provides additional methods
class attrDict(dict):
    # Allow attribute-style access to dictionary keys
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("attrDict object has no attribute '%s'" % key)

    # Allow attribute-style setting of dictionary keys        
    def __setattr__(self, key, value):
        self[key] = value
    
    # Return a JSON representation of the dictionary, excluding private keys
    def __str__(self):
        temp_dict = {"avaliable keys":[k for k in self.keys() if not k.startswith('_')]}
        # temp_dict.update({k:self[k] for k in self.keys() if k[0]=='_' and k[1]!='_' and (not k.startswith('_logger'))} )
        temp_dict.update({k:self[k] for k in self.keys() if k[0]=='_' and k[1]!='_' and not isinstance(self[k],logging.Logger) } ) 
        temp_json = json.dumps(temp_dict,indent=2)
        return temp_json

    # Use the string representation for the repr method
    def __repr__(self):
        return self.__str__()

    @property
    def _pureDict(self):
        return {k:self[k] for k in self.keys() if k[0]!='_' and not isinstance(self[k],logging.Logger)}
    
    # Export a subset of the dictionary based on a list of keys
    def subset(self,key_list:Iterable):
        """Create a subset of the attrDict with the specified keys

        Args:
            key_list (Iterable): list of some existing keys

        Returns:
            attrDict: result
        """
        result = {k: self[k] for k in self.keys() if k in key_list}
        return attrDict(result)

    # Refine the data types of all DataFrame objects in the dictionary to save memory
    def df_dtype_refine(self, inplace: bool = False, ignored_dfs:list=[])->object:
        """batch refine all Pandas dataframes by data types which save more memory

        Args:
            inplace (bool, optional): affects original data or not. Defaults to False.
            ignored_dfs (list, optional): list of keys that will be ignored by this method.

        Returns:
            object: copy of effective instance
        """
        if inplace:
            new_one = self
        else:
            new_one = copy.deepcopy(self)

        for k,v in self.items():
            if isinstance(v,DataFrame) and (k not in ignored_dfs):
                new_one[k] = dtype_auto_refine(v)
        return new_one

    # Standardize dictionary keys using a provided function
    def key_standardization(
        self, 
        standardize_func:callable = upper_and_replace_space_with_underscore
    ):
        """standardize the dictionary key by standardize_func

        Args:
            standardize_func (callable, optional): string conversion function. Defaults to toolbox.string.convert_functions.upper_and_replace_space_with_underscore.
        """
        original_keys = list(self.keys())
        for k in original_keys:
            self[standardize_func(k)]=self.pop(k)

    # Approximate the size of each item in the dictionary
    @property
    def size_summary(self)->dict:
        """iteratively approximate the size of each item in an attrDict instance

        Returns:
            Dict: result
        """
        rs = {k:get_obj_size(v) for k,v in self.items() if not k.startswith('_')}
        return rs

# Define a JSON encoder subclass to handle DataFrame objects
class JSE_4df(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataFrame):
            return obj.to_dict(orient='records')
        return json.JSONEncoder.default(self, obj)

# Define a class that represents properties of a dataset with type enforcement
class Property4DataSet(attrDict):
    # Initialize the class with type checking and assignment logic
    def __init__(self, value_type:type, input_dict:dict = None):
        _target_types = (
            datetime.date,
            datetime.datetime,
            datetime.time,
            str, 
            int, 
            float, 
            bool
            )

        if input_dict is None:
            pass
        elif value_type is None:
            
            if all_dict_values_in_target_types(input_dict, _target_types, visible_key_only=True):
                _ = [self.add(v, i) for i,v in input_dict.items() if not i.startswith('_')]
        elif isinstance(input_dict, Dict):
            if all_dict_values_in_target_types(input_dict, [List,], visible_key_only=True):
                input_dict = {i:v[0] for i,v in input_dict.items() if not i.startswith('_')}
            if all_dict_values_in_target_types(input_dict, [value_type,], visible_key_only=True):
                _ = [self.add(v, i) for i,v in input_dict.items() if not i.startswith('_')]
            else:
                raise TypeError(f'Not all values in attrDict are {value_type}')

    # Add a new property to the dataset
    def add(self,var, property_name):
        setattr(self,property_name, var)

    # Delete a property from the dataset    
    def delete(self,property_name):
        del self[property_name]

    # Return a list of all items excluding private and special attributes    
    @property    
    def allitems(self):
        return [x for x in list(self.keys()) if (x !=__name__) and (not x.startswith('_')) ] 
        #return [x for x in list(self.__dict__.keys()) if (x !=__name__) and (not x.startswith('_')) ] 

# Define a class to represent a dataset with predefined structures for dataframes, parameters, and mappings
class DataSet:
    __slots__ = (
        "DF",
        "PAR",
        "MAP"
    )
    # Initialize the dataset with optional dictionaries for each section
    def __init__(self, dict_PAR=None, dict_DF=None, dict_MAP=None):
        self.DF = self._DF(value_type = DataFrame, input_dict = dict_DF)
        self.PAR = self._PAR(value_type = None, input_dict = dict_PAR)
        self.MAP = Property4DataSet(value_type = dict, input_dict = dict_MAP)

    # Set or update the dataset sections with new dictionaries
    def set(self, dict_PAR:DataFrame=None, dict_DF:DataFrame=None, dict_MAP:DataFrame=None)->None:
        """assign dataframes to DataSet

        Args:
            dict_PAR (DataFrame, optional): DataFrame for PAR. Defaults to None.
            dict_DF (DataFrame, optional): DataFrame for Df. Defaults to None.
            dict_MAP (DataFrame, optional): DataFrame for MAP. Defaults to None.

        Raises:
            ValueError: when all Args are None
        """
        if all({(dict_PAR is None),(dict_DF is None),(dict_MAP is None)}): 
            raise ValueError("No attrDict instance has been assigned")
        if dict_DF:
            self.DF = self._DF(value_type = DataFrame, input_dict = dict_DF)
        if dict_PAR:
            self.PAR = self._PAR(value_type = None, input_dict = dict_PAR)
        if dict_MAP:
            self.MAP = Property4DataSet(value_type = dict, input_dict = dict_MAP)

    # Nested class for handling DataFrame properties
    class _DF(Property4DataSet):
        # Dump the DataFrame properties to a JSON file
        def dump2json(self, output_path: str = None):
            if not output_path:
                output_path = 'feed.DF.json'

            with open(output_path, 'w') as fp:
                json.dump(self, fp, cls=JSE_4df, indent = 2)

        # Standardize column names in all DataFrames
        def column_standardization(
                self,
                standardize_func:callable = upper_and_replace_space_with_underscore,
                inplace: bool = False
            ):
            """standardize the column name for each dataframe under DF by standardize_func

            Args:
                standardize_func (callable, optional): string conversion function. Defaults to upper_and_replace_space_with_underscore.
                inplace (bool, optional): Whether to modify the DataFrame rather than creating a new one. Defaults to False.

            Returns:
                Dataframe: it would be different than original DF property if `inplace=False`
            """
            if inplace:
                new_one = self
            else:
                new_one = copy.deepcopy(self)
           
            for df_name in new_one.allitems:
                col_names = list(new_one[df_name].columns)
                new_one[df_name].rename(
                    {col:standardize_func(col) for col in col_names},
                    axis='columns',
                    inplace=True
                )

            return new_one

    # Nested class for handling Parameter properties
    class _PAR(Property4DataSet):   
        # Export the parameters as a DataFrame
        def export_df(self, format: _export_mode = "multi-column"):
            """return a DataFrame by gathering all parameter:value within PAR  

            Args:
                format (_export_mode, optional): Literal["stacked","multi-column"]. Defaults to "multi-column".

            Returns:
                DataFrame
            """
            if format=="multi-column":
                df = pd.DataFrame(
                    [
                        [getattr(self,x) for x in self.allitems]
                    ],
                    columns = self.allitems
                    )
            if format=="stacked":
                df = pd.DataFrame(
                                zip(
                                    self.allitems,
                                    [getattr(self,x) for x in self.allitems]
                                ),
                                columns = ["parameter","value"]
                            )
            return df
    
# Define a class to represent a feed of data, which can be a simple or hierarchical structure
class Feed(DataSet):
    def __init__(self, multi_group = False, **kwargs):
        """Feed has a simple but organized structure to store the data

        Args:
            multi_group (bool, optional): Allows a hierarchical stucture. Defaults to False.
        """
        self.__multi_group = multi_group
        if multi_group:
            # If multi_group is True, provide a method to add new groups
            self.add_new_group = self.__add_new_group
        else:
            # Otherwise, initialize as a regular DataSet
            super().__init__(**kwargs)

    def __add_new_group(self, group_name, **kwargs):
        """Add a new group to the Feed if it's in multi-group mode.

        Args:
            group_name: The name of the new group.
            **kwargs: Additional arguments to pass to the DataSet initializer.
        """
        setattr(self, group_name, DataSet(**kwargs))

    # Get the names of all groups in the Feed if it's in multi-group mode.
    def __get_group_names(self):
        if self.__multi_group:
            return [g for g in list(self.__dict__.keys()) if g not in ('add_new_group','__add_new_group','__get_group_names','_Feed__multi_group')]
        else:
            return None

    def __str__(self):
        """String representation of the Feed, showing the data structure.

        Returns:
            A JSON-formatted string representation of the Feed's data.
        """
        if self.__multi_group:
            temp_dict = {
                g:[{x:[s for s in getattr(getattr(self,g),x).allitems]} for x in getattr(self,g).__slots__] 
                for g in self.__get_group_names()
            }
        else:
            temp_dict = {
                k:[x for x in getattr(self,k).allitems] 
                for k in self.__slots__
            }

        temp_json = json.dumps(temp_dict,indent=2)
        return "data attributes: \n" + temp_json
    
    # Representational string of the Feed, using the string representation.
    def __repr__(self):
        return self.__str__()


