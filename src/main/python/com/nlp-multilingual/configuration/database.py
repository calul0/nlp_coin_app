from utils.read_utils import read_config
from utils.singleton import Singleton


class DatabaseConfiguration(metaclass=Singleton):
    """
    Configuration of database settings, which is not checked into git. Please ensure to have a database.yaml with
    proper data included. Take getter methods as reference.
    """

    def __init__(self):
        self._config = read_config("resources/database.yaml")

    @property
    def host(self) -> str:
        return self._config['mysql']['host']

    @property
    def port(self) -> str:
        return self._config['mysql']['port']

    @property
    def database(self) -> str:
        return self._config['mysql']['database']

    @property
    def username(self) -> str:
        return self._config['mysql']['username']

    @property
    def password(self) -> str:
        return self._config['mysql']['password']
