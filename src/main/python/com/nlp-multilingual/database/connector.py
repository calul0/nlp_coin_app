import mysql.connector

from configuration.database import DatabaseConfiguration
from utils.logging import get_logger
from utils.singleton import Singleton

LOG = get_logger(__name__)


class DatabaseConnector(metaclass=Singleton):
    """
    Database connector as context manager implementation. This will provide secure way of opening and closing a mysql
    connection. The idea of the context manager is, to have a clean I/O operation, otherwise many database connections
    would be established.
    """

    def __init__(self):
        self._db_config = DatabaseConfiguration()

    def __enter__(self):
        try:
            self.database_connection = mysql.connector.connect(user=self._db_config.username,
                                                               password=self._db_config.password,
                                                               host=self._db_config.host,
                                                               port=self._db_config.port,
                                                               database=self._db_config.database,
                                                               auth_plugin='mysql_native_password')
            LOG.info('Database connection established successfully.')
        except IOError as ie:
            raise ie

        return self.database_connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.database_connection.close()
        LOG.info("Database connection closed successfully.")

        if exc_type is not None:
            raise
