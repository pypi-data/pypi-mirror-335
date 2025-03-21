from pympler import asizeof

def get_obj_size(obj)->str:
    """return the size of given object

    Args:
        obj (object): any Python object

    Returns:
        str: size of the object
    """
    obj_size_byte = asizeof.asizeof(obj)

    if (obj_size_byte<1000):
        return f'{obj_size_byte:.3f} bytes'
    elif (obj_size_byte<1000000) and (obj_size_byte>=1000):
        return f'{obj_size_byte/1000:.2f} KB'
    elif (obj_size_byte<1000000000) and (obj_size_byte>=1000000):
        return f'{obj_size_byte/1000000:.2f} MB'
    elif (obj_size_byte>=1000000000):
        return f'{obj_size_byte/1000000000:.2f} GB'
    else:
        return f'{obj_size_byte/1000000000000:.2f} TB'

