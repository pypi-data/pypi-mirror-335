import logging

from .db_connector import DBConnector

class NoSqlDBConnector(DBConnector):
    default_port = {
            "REDIS":6380,
            "MONGODB":7374,
        }

    def __init__(self, db_access, via_ssl = False, **kwargs):
        """connecting object for a NoSQL database

        Args:
            db_access (dict): return of parse_db_access()
            via_ssl (bool): connect via ssl
        """
        self.logger = logging.getLogger(__name__)
        self.cache_mode = 0
        self.cache_dir = "."

        
        self._db_access = db_access
        self._via_ssl = via_ssl

        self.queries_dir = None             
        self.__not_yet_purge = True

        self._db_type, self._port = self._check_nondefault_port()