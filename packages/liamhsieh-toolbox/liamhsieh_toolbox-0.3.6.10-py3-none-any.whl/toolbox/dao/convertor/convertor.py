from functools import partial
from .convertor_methods_mapper import MAPPER


class Convertor:

    def __init__(self, obj):
        obj_type = type(obj)
        self.obj_type = f"{obj_type.__module__}.{obj_type.__name__}"
        self.input_obj = obj
        self._initialize_avai_methods()
        

    def _initialize_avai_methods(self):
        for k,v in MAPPER[self.obj_type].items():
            setattr(self,k,partial(v,self.input_obj))
            