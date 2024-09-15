from typing import List

from utils.read_utils import read_config
from utils.singleton import Singleton


class EnglishNERConfiguration(metaclass=Singleton):
    """
    Singleton implementation of English configuration settings. For future perspective, if more language needs to
    be implemented, it would be good to create an .yaml parser, which can hold generic placeholder inside a .yaml
    template.
    """

    def __init__(self) -> None:
        self._config = read_config("resources/en_ner_config.yaml")

    @property
    def id_col(self) -> str:
        return self._config["ner"]["id_col"]

    @property
    def design_col(self) -> str:
        return self._config["ner"]["design_col"]

    @property
    def language(self) -> str:
        return self._config["ner"]["language"]

    @property
    def add_columns(self) -> List[str]:
        return self._config["ner"]["add_columns"]

    @property
    def model_directory(self) -> str:
        return self._config["ner"]["model_directory"]
