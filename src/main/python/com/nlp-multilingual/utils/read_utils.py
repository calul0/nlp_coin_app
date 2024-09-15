from pathlib import Path

import os
import yaml


os.chdir(Path(__file__).resolve().parents[4])


def read_config(file) -> dict:
    """
        Read .yaml configuration files.
    """

    with open(file=file, mode="r", encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YamlError as err:
            raise err
