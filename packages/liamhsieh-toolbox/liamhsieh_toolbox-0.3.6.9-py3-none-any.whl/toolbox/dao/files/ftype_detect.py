import sqlite3
import logging
import pathlib

import filetype
from filetype.types.archive import *

# determine file type via Magic number may sometime be tricky 
# so the following extensions are reported by developer community. 
# Depends on the way you generate these files, fieltype won't always determine correctly.
# For those internal programs, we should just trust the file ext 
# really tells the right file type, and the program will focus on determine the compression algorithm
 
warning_list = [
    'xlsx',
    'xlsb',
    'csv',
    'json'
]

def get_file_extension(file_path:str) -> str:
    return pathlib.Path(file_path).suffix

def ftype_detect(file_path) -> str:
    logger = logging.getLogger(__name__)
    file_ext = get_file_extension(file_path)
    if file_ext in warning_list:
        return file_ext
    else:
        ftype = filetype.guess(file_path)
        file_ext =filetype.guess_extension(file_path)

        if type(ftype) not in ['Tar','Gz','Zip']:
            return ftype,filetype.guess_extension(file_path)

    print('File extension: %s' % ftype.extension)
    return filetype.guess_extension(file_path)
    ftype = filetype.guess(file_path)
    if ftype is None:
        logger.info(f"can't determine the file type for {file_path}")
        return None
    else:
        logger.info(f"file type {ftype} is detected for {file_path}")
        return ftype
    
    try:
        con = sqlite3.connect(file_path)
        cur = con.cursor()
        cur.execute("PRAGMA integrity_check")
        ftype = 'sqlite'
        return ftype
    except sqlite3.DatabaseError:
        con.close()
    
    try:
        pass
    except ValueError:
        return ftype
        
        
    file_ext = pathlib.Path(file_path).suffix
    ftype = file_ext[1:]

    return ftype

if __name__ == '__main__':
    ftype_detect()

