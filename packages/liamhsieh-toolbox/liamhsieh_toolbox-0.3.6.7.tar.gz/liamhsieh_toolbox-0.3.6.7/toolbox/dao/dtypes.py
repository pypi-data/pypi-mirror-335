# import functools
# func = functools.partialmethod(pd.to_numeric,downcast="unsigned")
from pandas.core.frame import DataFrame
import pandas as pd


def dtype_auto_refine(df: DataFrame)->DataFrame:
    """This function will automatically convert numeric data to the most general type
    Also, replace object by pyarrow string for string columns.

    Args:
        df (DataFrame): Pandas Dataframe instance

    Returns:
        DataFrame: Dataframe with new data types assigned
    """
    df = df.copy(deep=True)
    individual_dtype_cols = {d_type: df.select_dtypes(include=[d_type]).columns for d_type in ["int","float","object"]}
    for d_type, cols in individual_dtype_cols.items():
        match d_type:
            case "int":
                df.loc[:,cols]=df.loc[:,cols].apply(pd.to_numeric,downcast="unsigned")
            case "float":
                df.loc[:,cols]=df.loc[:,cols].apply(pd.to_numeric,downcast="float")
            case "object":
                df.loc[:,cols] = df.loc[:,cols].astype("string[pyarrow]")           
    return df



