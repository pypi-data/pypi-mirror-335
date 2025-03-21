from json import JSONEncoder
from pandas import DataFrame

class DataFrameJSONEncoder(JSONEncoder):
    """
    Custom JSON Encoder subclass that converts pandas DataFrame objects to JSON.

    This encoder extends the default JSONEncoder and provides a custom
    serialization strategy for pandas DataFrame objects. When a DataFrame
    is encountered, it is converted to a dictionary with an orientation
    that lists each row as a dictionary (record).

    Any other object types will be handled by the default JSONEncoder
    implementation.
    """
    
    def default(self, obj):
        """
        Override the default method to serialize additional types.

        Args:
            obj (any): The object to serialize.

        Returns:
            any: A serializable object for obj, or calls the superclass
                 method for unsupported types.
        """
        if isinstance(obj, DataFrame):
            # Convert DataFrame to a list of dictionaries (one per row)
            return obj.to_dict(orient='records')
        # Use the default serialization for other types
        return JSONEncoder.default(self, obj)
