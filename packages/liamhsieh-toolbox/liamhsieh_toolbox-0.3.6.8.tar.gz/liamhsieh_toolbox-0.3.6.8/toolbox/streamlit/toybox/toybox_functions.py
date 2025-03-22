import re
import os

def get_projects(folder:str, suffix : str='_st')->dict:
    """scan streamlit Apps (folder with suffix under root directory
    Args:
        folder (str): path of root diretory
    Returns:
        dict: pairs of App name and its path; App name is folder name without suffix
    """
    return {
        re.split(suffix,item)[0]:os.path.join(folder, item) 
        for item in sorted(os.listdir(folder))
        if item.endswith(suffix)
        }

def get_versions(prj_path:str, suffix:str='_app'):
    return {
        re.split(suffix,item)[0]:os.path.join(prj_path, item) 
        for item in sorted(os.listdir(prj_path))
        if item.endswith(f'{suffix}.py')
        }