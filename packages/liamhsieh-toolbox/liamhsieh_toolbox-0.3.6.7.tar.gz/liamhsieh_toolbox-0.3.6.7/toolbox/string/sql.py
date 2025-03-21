from typing import List

def str_list_for_IN_condition(str_list:List[str])->str:
    """convert a string list to the format for putting between the bracket () for IN condition while doing SQL query.
    For example, str_list,["A1","A2,"A3"], will be convert to 'A1','A2','A3' and we can inject this result to a predefined sql query like follows:  

            with ARGS AS ( 
                SELECT
                    {str_list} as str_list 
                from DUAL
                )

            SELECT
                column1,
                column2,
            FROM
                table1, ARGS
            WHERE table1.column1 is not NULL
                and table1.column2 in (ARGS.str_list)


    Args:
        str_list (List[str]): a string list

    Returns:
        str: string variable with the format for  IN condition while doing SQL query
    """
    return ','.join(f"'{item}'" for item in str_list) 