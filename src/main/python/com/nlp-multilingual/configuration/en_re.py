from typing import List

from utils.read_utils import read_config
from utils.singleton import Singleton


class EnglishREConfiguration(metaclass=Singleton):
    """
    Singleton implementation for basic Relational Extraction configuration, which can be re-used. Only used here as
    getter class, to provide the configuration. 
    """

    def __init__(self) -> None:
        self._config = read_config("resources/en_re_config.yaml")

    @property
    def id_col(self) -> str:
        return self._config["re"]["id_col"]

    @property
    def design_col(self) -> str:
        return self._config["re"]["design_col"]

    @property
    def model_name(self) -> str:
        return self._config["re"]["model_name"]

    @property
    def model_directory(self) -> str:
        return self._config["re"]["model_directory"]

    @property
    def add_columns(self) -> List[str]:
        return self._config["re"]["add_columns"]
