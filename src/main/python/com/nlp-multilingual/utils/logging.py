import logging
import logging.config

from utils.read_utils import read_config

logger_is_setup = False


def get_logger(name) -> logging:
    if not logger_is_setup:
        logger_setup()
    return logging.getLogger(name=name.replace("", ""))


def logger_setup():
    logging.config.dictConfig(config=read_config("resources/logger.yaml"))
