import pathlib
import os
from collections.abc import KeysView
import pandas as pd


def all_equal(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)

    
def count_folder_number(contents:list) -> int:
    #return sum(os.path.isdir(c) for c in contents)
    return sum(pathlib.Path(c).is_dir() for c in contents)

def count_file_number(contents:list) -> int:
    return sum(pathlib.Path(c).is_file() for c in contents)

def create_nonduplicated_dict_key(dict_key:str,keys:KeysView, addition = "_") -> str:
    """If dict_key has not existed in keys, directly return, otherwise, keep adding additional string as suffix until no duplication is confirmed

    Args:
        dict_key (str): dictionary key that plans to add
        keys (KeysView): keys of target dictionary
        addition (str, optional): aditional string as suffix to avoid duplication. Defaults to "_".

    Raises:
        TypeError: keys needs to be a dict_keys

    Returns:
        str: confirmed key for futher insert 
    """
    if not isinstance(dict_key.keys(),KeysView):
        raise TypeError('keys needs to be a dict_keys')

    if dict_key not in list(keys):
        return dict_key
    else:
        return create_nonduplicated_dict_key(''.join((dict_key,addition)),keys)

def ensure_directory_exists(output_path: str, create_if_nonexistence:bool=True):
    """
    Check if the directory for the output path exists, and create it if it doesn't.

    Args:
        output_path (str): The path where the output will be saved.
    """
    directory = os.path.dirname(output_path)

    # handle the case if only file name provided as output path, set it as current working directory
    if directory=='': 
        directory='.'

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory):
        if create_if_nonexistence:
            os.makedirs(directory, exist_ok=True)
        return False
    else:
        return True
    

def df_dq_check(df, spec):
    """
    Perform data quality checks on a DataFrame based on the provided specification.

    Parameters:
    df (pd.DataFrame): The DataFrame to validate.
    spec (pd.DataFrame): A DataFrame containing the specification for validation. 
        It must have the following columns:
        - column_name (str): The expected column names in the DataFrame.
        - data_type (str): The expected data type for each column. Supported types are:
            - 'str': String type.
            - 'int': Integer type.
            - 'float': Float type.
            - 'datetime64[ns]': Datetime type.
        - re_pattern (str, optional): A regular expression pattern to validate string columns. 
          This is only applicable for columns with 'str' data_type.

    Raises:
    ValueError: If the number of columns in the DataFrame does not match the specification.
    ValueError: If the column names in the DataFrame do not match the expected column names.

    Returns:
    pd.DataFrame: The validated and transformed DataFrame. If any rows are invalid, an 
    'Invalid_Row_Message' column is added to indicate the issues.
    # Example: Creating a data specification for a CSV file using JSON

    ## Step 1: Define the data specification in JSON format
    data_spec_json = {
        "Corridor_LT": [
            {
                "column_name": "Corridor",
                "data_type": "str",
                "re_pattern": "LIAM\\s*[A-Za-z0-9]+-\\d+$"
            },
            {
                "column_name": "Location",
                "data_type": "str",
                "re_pattern": "^[A-Z0-9]{3}$"
            },
            {
                "column_name": "LT",
                "data_type": "int",
                "re_pattern": None
            }
        ]
    }

    ## Step 2: Save the JSON to a file
    with open('data_spec.json', 'w') as json_file:
        json.dump(data_spec_json, json_file, indent=4)

    ## Step 3: Load the JSON file and extract the required specification
    with open('data_spec.json', 'r') as json_file:
        loaded_spec = json.load(json_file)

    ## Extract the specification for the desired CSV file
    spec = pd.DataFrame(loaded_spec["Corridor_LT"])
    print(spec)
    """
    # Check if the number of columns matches the expected number
    if len(df.columns) < len(spec.column_name):
        raise ValueError(f"Expected {len(spec.column_name)} columns for the input file or dataframe, which are: {spec.column_name}")

    # assign column names based on their order
    df = df.iloc[:, :spec.column_name.size]
    df.columns = spec.column_name

    # Add a column to indicate if the row is invalid
    df['Invalid_Row_Message'] = ""



    # Validate and transform columns based on the configuration
    for row in spec.itertuples():
        dtype = row.data_type
        re_pattern = row.re_pattern
        if dtype == 'datetime64[ns]':
            df[row.column_name] = pd.to_datetime(df[row.column_name], errors='coerce')
            invalid_rows = df[row.column_name].isnull()
            if invalid_rows.any():
                error_msg_list = [f"Invalid date format in column '{row.column_name}'"] * sum(invalid_rows)
                existing_msg_list = list(df.loc[invalid_rows, 'Invalid_Row_Message'])
                df.loc[invalid_rows, 'Invalid_Row_Message'] = list(map(lambda x:''.join([x[0],";",x[1]]), zip(existing_msg_list,error_msg_list)))
        elif dtype == 'str' and re_pattern:
            invalid_rows = ~df[row.column_name].str.match(re_pattern)
            if invalid_rows.any():
                error_msg_list = [f"Values do not match the expected pattern in column '{row.column_name}'"] * sum(invalid_rows)
                existing_msg_list = list(df.loc[invalid_rows, 'Invalid_Row_Message'])
                df.loc[invalid_rows, 'Invalid_Row_Message'] = list(map(lambda x:''.join([x[0],";",x[1]]), zip(existing_msg_list,error_msg_list)))
        elif dtype in ('int','float'):
            invalid_rows = pd.to_numeric(df[row.column_name], errors='coerce').isnull()
            if invalid_rows.any():
                error_msg_list = [f"Column '{row.column_name}' could not be converted to {dtype}"] * sum(invalid_rows)
                existing_msg_list = list(df.loc[invalid_rows, 'Invalid_Row_Message'])
                df.loc[invalid_rows, 'Invalid_Row_Message'] = list(map(lambda x:''.join([x[0],";",x[1]]), zip(existing_msg_list,error_msg_list)))
        
        if sum(invalid_rows) == 0:
            df[row.column_name] = df[row.column_name].astype(dtype)


    # Drop the Invalid_Row_Message column if it is empty for all rows
    if df['Invalid_Row_Message'].isna().all():
        df.drop(columns=['Invalid_Row_Message'], inplace=True)
    else:
        # Remove trailing semicolon and space from Invalid_Row_Message if any
        df['Invalid_Row_Message'] = df['Invalid_Row_Message'].str.lstrip('; ')

    return df