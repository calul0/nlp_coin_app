from ast import literal_eval
from typing import Union


def safe_eval(val: str) -> Union[list, str]:
    """
    Input data contains annotations, stored as strings, that represent lists. Hence, safe_eval function is used to
    convert these string representations into Python lists.

    Args:
        val (str): The string, which needs to be evaluated.

    Returns:
        Union[list, str]: The evaluated list if successful, otherwise the original string.
    """

    try:
        return literal_eval(val)
    except (ValueError, SyntaxError):
        return val
