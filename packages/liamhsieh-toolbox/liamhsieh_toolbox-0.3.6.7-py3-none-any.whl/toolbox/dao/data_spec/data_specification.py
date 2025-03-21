from dataclasses import dataclass, field
from typing import List
from collections import namedtuple
import json
import logging
import os

@dataclass
class _DataSpecification:
    """This data class provides a hirachecal sturcture to organize the data specification for the input data verification.
    In order to align with the property _fields for namedtuple, we also implement the one for this class
    """
    # FINANCE_INPUT:namedtuple
    # SOLVER_OUTPUT:namedtuple
    # FROM_PRODSQLAG01:namedtuple
    __data: dict = field(init=False)

    def __post_init__(self):
        for key, value in self.__data.items():
            setattr(self, key, value)

    def __iter__(self) -> List[namedtuple]:
        return iter([getattr(self, field) for field in self._fields])

    def __next__(self) -> str:
        raise StopIteration
        
    @property
    def _fields(self):
        #return tuple(self.__dataclass_fields__.keys())
        return tuple(self.__data.keys())
    

# Conver manual Data Spec (nested namedtuple) to json
def export_data_spec_to_json(DS:_DataSpecification, file_name: str="data_specification", DS_def_folder_name="data_spec") -> None:
    
    data_spec_dict = {
        type(data_source).__name__: {
            type(flat_file).__name__:flat_file._asdict() for flat_file in data_source
        } for data_source in DS
    }

    with open(os.path.join(DS_def_folder_name,f"{file_name}.json"), "w") as f:
        json.dump(data_spec_dict, f, indent=4)



# load data spec from json
def load_data_spec_from_json(json_path:str):
    logger = logging.getLogger(__name__)

    try:
        with open(json_path) as f:
            data_spec_dict = json.load(f)
    except Exception as e:
        logger.error("Please make sure data_specification.json exists and the format is appropriate")
        raise e


    def dict_to_namedtuple(d, name='Data'):
        fields = []
        values = []
        
        for k, v in d.items():
            if isinstance(v, dict):
                v = dict_to_namedtuple(v, k)
            fields.append(k)
            values.append(v)
        
        return namedtuple(name, fields)(*values)
        
    return dict_to_namedtuple(data_spec_dict,)
    