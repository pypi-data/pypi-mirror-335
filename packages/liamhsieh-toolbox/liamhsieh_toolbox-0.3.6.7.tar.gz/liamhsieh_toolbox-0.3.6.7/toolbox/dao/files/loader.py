from pdb import set_trace as bp
import json
import shutil
import tempfile
import pathlib
import glob
import logging


import pandas as pd
import dask.dataframe as dd
from pandas.core.frame import DataFrame


from ...dao.feed import attrDict
from .utility import (
    all_equal,
    count_folder_number,
    count_file_number,
)


# Exception class
class StructError(ValueError):
    """Raised when the composition of an archive is not supported by package"""
    _default_msg = "invalid composition of the archive"
    def __init__(self, message = None):
        self.message = self._default_msg if message is None else message
    def __str__(self):
        return self.message

class FormatError(StructError):
    def __init__(self, message = None):
        self.message = f"only support file format in {FileLoader.supported_format}" if message is None else message


class InconsistentError(StructError):
    def __init__(self, message = None):
        self.message = f"for multiple files, only support .csv, .pkl or .parquet" if message is None else message

def get_file_extension(file_path:str) -> str:
    return pathlib.Path(file_path).suffix

def ftype_detect(file_path:str) -> str:
    # TODO: additional checking for sqlite, json, and pkl
    return get_file_extension(file_path)

    # file_ext = get_file_extension(file_path)
    # if file_ext in warning_list:
    #     return file_ext
    # else:
    #     ftype = filetype.guess(file_path)
    #     file_ext =filetype.guess_extension(file_path)

    #     if type(ftype) not in ['Tar','Gz','Zip']:
    #         return ftype,filetype.guess_extension(file_path)

    # print('File extension: %s' % ftype.extension)
    # return filetype.guess_extension(file_path)
    # ftype = filetype.guess(file_path)
    # if ftype is None:
    #     logger.info(f"can't determine the file type for {file_path}")
    #     return None
    # else:
    #     logger.info(f"file type {ftype} is detected for {file_path}")
    #     return ftype
    
    # try:
    #     con = sqlite3.connect(file_path)
    #     cur = con.cursor()
    #     cur.execute("PRAGMA integrity_check")
    #     ftype = 'sqlite'
    #     return ftype
    # except sqlite3.DatabaseError:
    #     con.close()
    
    # try:
    #     pass
    # except ValueError:
    #     return ftype
        
        
    # file_ext = pathlib.Path(file_path).suffix
    # ftype = file_ext[1:]

    # return ftype

def update_target_dir(target_dir:str) -> str:
        """check target directory and return the correct path if subfolder exists

        Args:
            target_dir (str): path of target directory

        Raises:
            StructError: invalid composition of the archive

        Returns:
            str: path of target directory
        """
        #logger.info(f"check if subfolder exists in archive")
        contents = get_contents_list(target_dir)
        num_folder = count_folder_number(contents)
        num_file = count_file_number(contents)

        if num_folder>1: #more than two subfolder within original temp dir
            #logger.info(f"[Error]: more than one subfolder is found the archive {target_dir}")
            raise StructError(f"more than one subfolder is found in target directory {target_dir}")
        elif num_folder==1: #just one subfolder in original temp_dir
            if num_file>0: 
                #logger.info(f"[Error]: either single subfolder or files is allowed in target directory {temp_dir}")
                raise StructError("subfolder can't stand with files")
            else:
                target_dir = contents[0]  
        elif num_file==0: #no subfolder within temp dir
            raise ValueError("no contents in target directory or directory doesn't exist")
        return target_dir

def get_contents_list(path:str, recursive_search = False) -> list[str]:
    """Return contents under a given directory

    Args:
        path (str): path of a directory
        recursive_search (bool, optional): search recursively if subfolders exist. Defaults to False.

    Returns:
        list[str]: list of contents
    """
    if recursive_search:
        contents = glob.glob(f"{path}/**", recursive=True)[1:] #exculde path dir itself
    else:
        contents = glob.glob(f"{path}/**", recursive=False) 
    return contents


def load_json2ad(file_path):
    dicts_from_json = json.load(open(file_path))
    dfs2dict = {
        key: pd.DataFrame(dicts_from_json[key]) for key in dicts_from_json
    }
    return dfs2dict



class FileLoader(attrDict):
    """_summary_

    Supported format:
        excel(xlsx): default is to load all worksheets
        csv: separator can be assign to method `execute` as arg `sep` and its default is `','; note that `sep=None` means automatically detect 
    """
    supported_format = (     
        '.xlsx',
        '.xlsb',
        '.csv',
        '.json',
        '.db',
        '.parquet',
        '.pkl'
    )

    load_method = {
            ".csv":pd.read_csv,
            ".xlsx":pd.read_excel,
            ".parquet": pd.read_parquet,
            ".pkl": pd.read_pickle,
            ".json": load_json2ad
        }

    __slots__ = (
        "_input_path",
        "_archive",
        "_logger",
    )

    def __init__(self, path: str, archive = False):
        """Load source data to a dictionary.  
           path can only point to a file or directory(includes multiple identical files).
           Supporting file types:  
                - comma-separated values (.csv)
                - Excel (.xlsx, .xlsb)
                - Sqlite (.db, .sqlite)
                - JSON (.json)
                - Apache Parquet (.parquet)
                - Pytho pickle file (.pkl)

        For loading multiple files, only supports csv, pkl, or parquet.
        path can also point to an archive of file(s) of a folder, the compress method can be:  
                - tar.gz
                - tar.bz2
                - tar.xz
                - zip

        Args:
            path (str): a path to a file or directory
            archive (bool, optional): if an archive file is the target of the path. Defaults to False.

        All class properties should start with _ instead of those dataframes
        """
        self._input_path = path
        self._archive = archive 
        self._logger = logging.getLogger(__name__)

    def _parse_path(self):
        ftype = None
        if pathlib.Path(self._input_path).is_dir():
            path_is_for_dir = True
        elif pathlib.Path(self._input_path).is_file():
            path_is_for_dir = False
            ftype = ftype_detect(self._input_path)
        else:
            raise Exception("path can only be an existing file or path")
            
        return path_is_for_dir, ftype

    @property
    def _pureDict(self):
        return {k:self[k] for k in self.keys() if k not in self.__slots__ and not isinstance(self[k],logging.Logger)}


    def execute(self, **kwargs):
        path_is_for_dir, ftype = self._parse_path()

        if path_is_for_dir:
            self._load_when_path_is_folder(archive=False,**kwargs)

        elif ftype is not None:
            if self._archive:
                self._load_when_path_is_folder(archive=True, **kwargs)
            elif ftype in self.supported_format:
                self._load_to_attrDict([self._input_path,],True,ftype, **kwargs)

        else:
            exception_msg = "path should only point to a directory or a file (could be an archive with optional argument archive = True"
            self._logger.info(exception_msg)
            raise TypeError(exception_msg)
    

    def _load_to_attrDict(self,contents:list[str], single_file:bool, file_type:str, **kwargs):

        if single_file:
            match file_type:
                case '.xlsx':
                    _ = [self.update({k:v for k,v in  FileLoader.load_method[file_type](contents[0], sheet_name=None, **kwargs).items()})]
                case other:
                    self.update({pathlib.Path(contents[0]).stem.replace(' ', '_'):FileLoader.load_method[file_type](contents[0],**kwargs)})
        else:
            _ = [self.update({pathlib.Path(c).stem.replace(' ', '_'): FileLoader.load_method[file_type](c,**kwargs)}) for c in contents]


    def _load_when_path_is_folder(self, archive, **kwargs):
        temp_dir = None
        if archive:
            temp_dir = tempfile.TemporaryDirectory()
            target_dir = ""

            try:
                shutil.unpack_archive(self._input_path,temp_dir.name)
            except shutil.ReadError:
                self._logger.info(f"can't unpack the achive, check input file {self._input_path}")
                raise shutil.ReadError(f"can't unpack the achive, check input file {self._input_path}")

            target_dir = update_target_dir(temp_dir.name)
        else:
            target_dir = update_target_dir(self._input_path)

        self._load_feed_from_source_dir(target_dir)

        if temp_dir is not None: temp_dir.cleanup()

        


    def _load_feed_from_source_dir(self,target_dir:str, **kwargs) -> attrDict:
        """load data from files in target directory to an instance of attrDict

        Args:
            target_dir (str): path of target directory

        Raises:
            StructError: invalid composition of the archive
            InconsistentError: for multiple files, only support .csv, .pkl or .parquet
            FormatError: unsupported file type
            ValueError: no contents in target directory or directory doesn't exist

        Returns:
            attrDict: collections of input data
        """

        contents = get_contents_list(target_dir)
        num_folder = count_folder_number(contents)
        num_file = count_file_number(contents)
        file_type= ftype_detect(contents[0])
        identical_ftype = all_equal(get_file_extension(c) for c in contents)

        if num_folder>0:
            raise StructError("nested subfolder is not allowed")
        elif num_file<1:
            raise ValueError("no contents in target directory")
        elif (num_file>1) and (identical_ftype==False):
            raise InconsistentError
        elif (num_file>1) and (identical_ftype==True):
            if file_type in ['.csv','.parquet','.pkl']:
                self._load_to_attrDict(contents, single_file=False, file_type= file_type, **kwargs)
            else:
                raise FormatError
        elif num_file==1:
            if file_type in self.supported_format:
                self._load_to_attrDict(contents,single_file=True, file_type = file_type, **kwargs)
            else:
                raise FormatError
        else:
            raise Exception("exception happened during _load_feed_from_source_dir")

        

if __name__ == '__main__':
    pass