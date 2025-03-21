import os
import io
import csv
import logging
import zipfile
import logging

from azure.storage.blob import ContainerClient
import pandas as pd

from ..feed import attrDict
from ...utility import bp

class BlobConnector:
    def __init__(self, db_access):
        self.logger = logging.getLogger(__name__)
        self._db_access = db_access
        self.blob_container_client = self._get_container_client
        

    @property
    def _get_container_client(self,log_only_error=True):
        # Set the logging level for all azure-storage-* libraries

        if log_only_error:
            logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
        else:
            logger = logging.getLogger('azure-storage').setLevel(logging.ERROR)

        conn_str=''.join(
            [
            f'DefaultEndpointsProtocol={self._db_access["defaultendpointsprotocol"]};',
            f'AccountName={self._db_access["accountname"]};',
            f'AccountKey={self._db_access["accountkey"]};',
            f'EndpointSuffix={self._db_access["endpointsuffix"]}'
            ]
        )

        container_client = ContainerClient.from_connection_string(conn_str=conn_str,
                                                                   container_name=self._db_access["containername"],
                                                                   logger=logger)
        return container_client

    def walk_blob_container(self,*args,**kwargs):
        """returns a generator to list the blobs under the specified container. 
        The generator will lazily follow the continuation tokens returned by the service. 
        This operation will list blobs in accordance with a hierarchy, as delimited by the specified delimiter character.
        Args:
            name_starts_with (str): Filters the results to return only blobs whose names begin with the specified prefix.
            include (list[str] or str): Specifies one or more additional datasets to include in the response. 
                    Options include: 'snapshots', 'metadata', 'uncommittedblobs', 'copy', 'deleted', 'deletedwithversions', 'tags', 'versions', 'immutabilitypolicy', 'legalhold'.
            delimiter (str): When the request includes this parameter, the operation returns a BlobPrefix element in the response body that acts as a placeholder for all blobs whose 
                            names begin with the same substring up to the appearance of the delimiter character. The delimiter may be a single character or a string.
        Returns:
            generator: An iterable (auto-paging) response of BlobProperties.
        Check doc for blob_container_client.walk_blobs to learn more 
        """
        return self.blob_container_client.walk_blobs(args,kwargs)

    def get_blob_list(self,folder_path:str=None)->list[str]:
        """return list of blob names
        If folder_path is None, return all blob names in the container

        Args:
            folder_path (str, optional): path of a specific folder. Defaults to None. If it ends with '/', folder itself won't be included as part of results

        Returns:
            list[str]: list of blob names
        """
        if folder_path is None:
            blob_list = list(self.blob_container_client.list_blob_names())
        else:
            blob_list = [x for x in self.blob_container_client.list_blob_names() if x.startswith(folder_path)]
        return blob_list


    def check_blob_existance(self, blob_name:str)->bool:
        """check a blob exists or not

        Args:
            blob_name (str): path of target blob

        Returns:
            bool: exists or not
        """
        if blob_name.endswith("/"): blob_name=blob_name[:-1]
        return True if blob_name in self.get_blob_list() else False

    @classmethod
    def get_blob_name(cls,file_name:str, blob_path:str)->str:
        """blob_name is the path for accessing a specific blob via blob_container_client
        Conceptually, it will look like <folder_name>/<subfolder_name>/<file_name>
        it only provides file_name as blob_path, it sets container root as like 'working directory'

        Args:
            file_name (str): file name
            blob_path (str): blob path

        Returns:
            blob_name (str): blob_name
        """
        if blob_path is not None:
            if blob_path.startswith("/"): blob_path = blob_path[1:]
            
            if blob_path.endswith("/"):
                blob_name = f"{blob_path}{file_name}"
            else:
                blob_name = f"{blob_path}/{file_name}"
        else:
            blob_name=file_name
        return blob_name

    def del_blob(self,blob_name:str)->None:
        """delete a blob

        Args:
            blob_name (str): path of target blob
        """
        if blob_name.endswith("/"): blob_name=blob_name[:-1]
        if self.check_blob_existance(blob_name):
            container_client = self.blob_container_client
            container_client.delete_blob(blob_name)
        else:
            return None

    def add_folder(self,folder_path:str)->None:
        """Add a empty virtual folder. If the folder exists, all contents will be purged.
        For example, in target container, we already have a virtual folder called <folder_X> and you want to add a empty folder,<folder_Y>, under <folder_X>, set folder_name as '<folder_X>/<folder_Y>'.

        Args:
            folder_path (str): full path of intended virtual folder which should not end with `/`
        """
        if folder_path.endswith('/'):
            self.logger.warning("folder_path for BlobConnector.add_folder() should not end with `/`")
            
            while folder_path.endswith('/'):
                folder_path = folder_path[:-1]

        if self.check_blob_existance(folder_path):
            _ = [self.del_blob(x) for x in self.get_blob_list(folder_path)]
        else:
            dummy_blob = folder_path + "/dummy.txt"
            container_client = self.blob_container_client
            container_client.upload_blob(name=dummy_blob,data=" ")
            container_client.delete_blob(dummy_blob)

    def file_upload(self,file_path:str, blob_path:str=None)-> None:
        """upload local file to Azure Blob Storage; delete blob first, if same blob exists.
           When blob_path is None, file will be put right in the container
           To put file in a given folder, blob_path is required

        Args:
            file_path (str): file path
            blob_path (str): blob path; default in None
        """
        container_client = self.blob_container_client
        file_name = os.path.basename(file_path)
         
        blob_name = self.get_blob_name(file_name,blob_path)

        if self.check_blob_existance(blob_name):
            container_client.delete_blob(blob_name)

        _ = container_client.upload_blob(name=blob_name, data=file_path)

        

    
    def upload_csv_from_df(self, df:pd.DataFrame, blob_path:str, file_name:str, archive:bool=True)->None:
        """convert a DataFrame object to csv then upload to Azure Blob Storage; delete blob first, if same blob exists.
        This method is a stream-base operation. 
        Remember, blob only has virtual folder so files in a folder have blob name including folder name

        Args:
            df (pd.DataFrame): source dataframe
            blob_path (str): path points to the location for uploading the file 
            file_name (str): name of the file
            archive (bool, optional): zip it or not. Defaults to True.

        Raises:
            ValueError: file_name should end by .zip if archive
            ValueError: file_name should end by .csv if not archive
        """

        assert isinstance(file_name,str)
        assert isinstance(blob_path,str)
        blob_name = self.get_blob_name(file_name,blob_path)

        if archive:
            if not file_name.endswith(".zip"): raise ValueError("blob_name should end by .zip") 
        else:
            if not file_name.endswith(".csv"): raise ValueError("blob_name should end by .csv") 

        container_client = self.blob_container_client

        if self.check_blob_existance(blob_name):
            container_client.delete_blob(blob_name)
        
        
        in_memory_csv = io.BytesIO()
        
        if archive:
            df.to_csv(in_memory_csv,
                    compression={"method":'zip',
                    "archive_name":os.path.splitext(file_name)[0]+".csv"}
                    ) #use splitext in stead of basename because of virtual folder in Blob storage
        else:
            df.to_csv(in_memory_csv)

        in_memory_csv.seek(0)
        _ = container_client.upload_blob(name=blob_name, data=in_memory_csv)

    def upload_parquet_from_df(self, df:pd.DataFrame, blob_path:str, file_name:str, compression:str=None)->None:
        """convert a DataFrame object to parquet then upload to Azure Blob Storage; delete blob first, if same blob exists.
        This method is a stream-base operation. 
        Remember, blob only has virtual folder so files in a folder have blob name including folder name
        General Usage : gzip is often a good choice for cold data, which is accessed infrequently. snappy  are a better choice for hot data, which is accessed frequently.

        Args:
            df (pd.DataFrame): source dataframe
            blob_path (str): path points to the location for uploading the file 
            file_name (str): name of the file
            compression (str, optional): 'gzip' or 'snappy'. Defaults to None.

        Raises:
            ValueError: file_name should end by .gzip or .snappy if enable compression
            ValueError: file_name should end by .parquet if no compression
        """

        assert isinstance(file_name,str)
        assert isinstance(blob_path,str)


        match compression:
            case None:
                if not file_name.endswith(".parquet"): raise ValueError("blob_name should end by .parquet") 
            case "gzip":
                if not file_name.endswith(".parquet.gzip"): raise ValueError("blob_name should end by .parquet.gzip") 
            case "snappy":
                if not file_name.endswith(".parquet.snappy"): raise ValueError("blob_name should end by .parquet.snappy") 
            case _:
                raise ValueError("unsupported string is passed as compression") 
            
        blob_name = self.get_blob_name(file_name,blob_path)
        container_client = self.blob_container_client

        if self.check_blob_existance(blob_name):
            container_client.delete_blob(blob_name)
        
        in_memory_parquet = io.BytesIO()
        if compression is not None:
            df.to_parquet(in_memory_parquet,
                    compression={"method":compression}) 
        else:
            df.to_parquet(in_memory_parquet)
        in_memory_parquet.seek(0)
        _ = container_client.upload_blob(name=blob_name, data=in_memory_parquet)
        


    def blob_dump(self,blob_name:str, dir_path: str = ".", to_memory:bool=False, to_dataframe:bool=False,to_attrDict:bool=False):
        """download specified blob to the specified location

        Args:
            blob_name (str): blob_path+file_name, path of the blob because Blob storage uses virtual folder
            dir_path (str, optional): specified location of keeping the blob file. Defaults to ".".
            to_memory (bool, optional): assign in-momery zip object as return type if True. Defaults to False.
            to_dataframe (bool, optional): assign pandas dataframe as return type. It works only if the blob is csv/xlsx/parquet. Defaults to False.
            to_attrDict (bool, optional): assign toolbox.dao.feed.attrDict as return type if True. It works only if the blob is an archive of csv file(s). Defaults to False.

        Raises:
            ValueError: if target container doesn't have any blob named blob_name

        Returns:
            _type_: Defaults to None; But toolbox.dao.feed.attrDict if to_attrDict else in-momery zip object if to_memory 
        """

        if not self.check_blob_existance(blob_name):
            self.logger.info(f"target container doesn't have any blob named {blob_name}")
            raise ValueError(f"target container doesn't have any blob named {blob_name}")

        if not os.path.exists(dir_path): 
            os.makedirs(dir_path)
            self.logger.info(f"create required folder(s) because of non-exist path {dir_path}")
            
        blob_client=self.blob_container_client

        file_path = os.path.join(dir_path, os.path.basename(blob_name)) 
        download_stream = blob_client.download_blob(blob=blob_name)

        # Just download the original file to local
        if not (to_attrDict or to_memory or to_dataframe):
            with open(file_path, "wb") as target_blob:
                target_blob.write(download_stream.readall())
            return None

        # download zip file
        elif blob_name.endswith('.zip'):
            in_memory_zip = io.BytesIO(download_stream.readall())
            zf = zipfile.ZipFile(in_memory_zip)

            # further convert to dataframe
            if to_dataframe:
                if len(list(zf.namelist()))>1:
                    self.logger.error("only work with single file when to_dataframe=True")
                    raise Exception("only work with single file when to_dataframe=True")
                
                filename=list(zf.namelist())[0]
                file_ext = os.path.splitext(filename)[1]
                to_df = {
                    '.xlsx':pd.read_excel,
                    '.csv': pd.read_csv
                }

                try:
                    df = to_df[file_ext](zf.open(filename))
                except:
                    self.logger.error(f"Can't convert {filename} in zip blob {blob_name} to a dataframe")
                    raise Exception(f"Can't convert {filename} in zip blob {blob_name} to a dataframe")
                finally:
                    return df

            elif to_attrDict:
                
                dict_DF = attrDict(
                    {
                        os.path.splitext(os.path.basename(name))[0]: pd.read_csv(io.StringIO(str(zf.read(name),'utf-8'))) for name in zf.namelist() if name.endswith(".csv") 
                    }
                )

                return dict_DF
            
            elif to_memory:
                return zf


        elif blob_name.endswith(('.parquet.gzip','.parquet.snappy','.parquet')):
            if to_dataframe:
                try:
                    stream = io.BytesIO(download_stream.readall())
                    stream.seek(0)
                    return pd.read_parquet(stream)
                except Exception as e:
                
                    self.logger.error(e)
                    raise Exception(f"Fail to convert parquet blob {blob_name} to a dataframe")
            else:
                raise Exception("Only support directly dumping or converting to dataframe for parquet")

        else:
            if not (blob_name.endswith('.csv') or blob_name.endswith('.xlsx')):
                self.logger.error("Except an archive of csv/xlsx, it only accepts a single csv or xlsx")
                raise Exception("Except an archive of csv/xlsx, it only accepts a single csv or xlsx")

            elif (to_dataframe or to_attrDict):

                file_ext = os.path.splitext(blob_name)[1]
                to_df = {
                    '.xlsx':pd.read_excel,
                    '.csv': pd.read_csv
                }

                if file_ext == '.xlsx':
                    blob =download_stream.content_as_bytes()
                else:
                    stream = io.BytesIO()
                    download_stream.download_to_stream(stream)
                    stream.seek(0)
                    blob = stream
                
                try:
                    df = to_df[file_ext](blob)
                except:
                    self.logger.error(f"Can't convert spreadsheet blob {blob_name} to a dataframe")
                    raise Exception(f"Can't convert spreadsheet blob {blob_name} to a dataframe")

                return df

            elif to_memory:
                return download_stream



