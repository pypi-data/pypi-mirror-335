from collections import namedtuple

def namedtuple_from_dict(source_dict:dict,name:str)->namedtuple:
    """Create and return a namedtuple instance with fields populated from a dictionary.
    This function dynamically creates a new namedtuple class with a given name and fields corresponding to the keys of the source dictionary. The values of the namedtuple are filled with the values from the source dictionary.

    Args:
        source_dict (dict): The dictionary whose keys and values are to be used to create the namedtuple.
        name (str): The name of the new namedtuple class to be created.

    Returns:
        namedtuple: An instance of the newly created namedtuple class, populated with data from the source_dict.
    """

    return namedtuple(name,source_dict.keys())(**source_dict)