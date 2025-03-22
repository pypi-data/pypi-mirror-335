import os
import __main__


class ToyboxApp:

    def __init__(self, script_path:str):
        """ to set a client streamlit script correctly  

        Args:
            script_path (str): path specified script
        """

        self.script_path = script_path
        self.script_dir = os.path.dirname(script_path) #it returns abspath
        if os.path.islink(self.script_dir):
            self.script_dir = os.readlink(self.script_dir) # if script_dir is a link, set script_dir to which the link points
        self.system_dir = os.path.dirname(__main__.__file__) 
        
        
    def set_working_dir(self):
        """ set working directory to correctly import local modules or load files

        Returns:
            dict: information
        """
        os.chdir(self.script_dir)
        return {
            "script_path":self.script_path,
            "script_dir":self.script_dir,
            "system_dir": self.system_dir
        }

    def get_realpath(self, filename:str)->str:
        """in case local files can't be read correctly when adding a project using softlink 

        Args:
            filename (str): file name

        Returns:
            str: real path of that file
        """
        return os.path.join(self.script_dir,filename)

