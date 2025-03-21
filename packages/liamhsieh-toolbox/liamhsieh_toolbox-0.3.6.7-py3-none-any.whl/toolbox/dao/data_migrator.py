from .connector import DBConnector,BlobConnector
import logging
from sqlalchemy.exc import DatabaseError


class DataMigrator:


    def __init__(self, blob_access, db_access):
        """
        Args:
            blob_access (toolbox.dao.connector.db_access): db_access for target blob storage
            db_access (toolbox.dao.connector.db_access): db_access for source database
        """
        self.logger = logging.getLogger(__name__)

        self._db_access = db_access

        self.DBC = DBConnector(db_access)
        self.BC = BlobConnector(blob_access)


    def check_folder(self, target_folder_path:str):
        if target_folder_path not in self.BC.get_blob_list():
            self.BC.add_folder(folder_path=target_folder_path)
            self.logger.info(f'folder `{target_folder_path}` has been created')
            return False
        else:
            self.logger.info('folder `{target_folder_path}` exists and following files are found:\n')
            self.logger.info(self.BC.get_blob_list(target_folder_path))
            return True


    def migrate(
            self,
            period:tuple,
            target_folder_path:str,
            predefined_query_name:str,
            cache_name:str,
            queires_dir: str="./queries",
            chunk_mode:bool=False,
            enforce_dtype:bool=True,
            **pars
    ):
        """migrate data from source db to target Azure Blob Storage

        Args:
            period (tuple(int,)): (start_week,end_week), e.g., (202201,202208)
            target_folder_path (str): path of the target folder
            predefined_query_name (str): name of predefined query for source db
            cache_name (str): label for the cache file(s) without timestamp
            queires_dir (str, optional): where to looking for predefined query. Defaults to "./queries".
            chunk_mode (bool, optional): pull data in chunk mode or not. Defaults to False.
            enforce_dtype (bool, optional): enforce to convert data type for resulted dataframe. Defaults to True.
        
        Example:
        ```python
        from toolbox.dao import DataMigrator
        from toolbox.dao.connector import BlobConnector,DBConnector,parse_db_access
        from toolbox.utility import set_logger

        logger = set_logger('DEBUG')

        blob_access = parse_db_access("db.ini","BLOB_Storage")
        BC = BlobConnector(blob_access)

        db_access = parse_db_access("db.ini","XEUS")
        DBC = DBConnector(db_access)

        DM=DataMigrator(
            blob_access=blob_access,
            db_access=db_access
        )

        DM.migrate(
            period=(202338,202339),
            target_folder_path="test",
            cache_name="test_df",
            queires_dir="./toolbox/dao/queries/",
            predefined_query_name="pull_raw_lot_flow",
            chunk_mode=True,
            enforce_dtype=True
        )
        ```
        """
        
        self.check_folder(target_folder_path)

        for ww in range(period[0],period[1]):

            pars["start_week"] = ww 
            pars["end_week"] = ww+1

            self.DBC.set_queries_dir(queires_dir=queires_dir,**pars)
            self.logger.info(f"Set pars ready for the query in week {ww}")

            try:
                if not chunk_mode:
                    result_df = self.DBC.pull_predefined_query(predefined_query_name,**pars)
                    file_name = f"{pars['start_week']}_{cache_name}.parquet.gzip"
                    self.BC.upload_parquet_from_df(result_df, target_folder_path, file_name, compression='gzip')
                else:
                    dfs_generator = self.DBC.pull_predefined_query(
                            query_name = predefined_query_name,
                            chunk_mode = chunk_mode,
                            enforce_dtype = enforce_dtype,
                            **pars
                    )
                  
                    for i, chunk_df in enumerate(dfs_generator):
                        file_name = f"{ww}_{cache_name}_{i}.parquet.gzip"
                        self.BC.upload_parquet_from_df(chunk_df, target_folder_path, file_name, compression='gzip')
                        self.logger.info(f"Regarding week {ww}: chunk {i} finished")

                self.logger.info(f"The query result of week {ww} is uploaded to Blob Storage")
                
            except DatabaseError as e:
                # Check if the error message contains "ORA-12170"
                if "ORA-12170" in str(e):
                    self.logger.error(f"Task for {ww} got ORA-12170: TNS:Connect timeout occurred")
                else:
                    # Handle other types of DatabaseError
                    self.logger.error(f"Task for {ww} got other DatabaseError: {e}")

        self.logger.info(f"Finish data migration")
