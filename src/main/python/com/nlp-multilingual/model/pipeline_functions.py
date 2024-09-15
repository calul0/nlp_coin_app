import pickle

from typing import Any
from sklearn.pipeline import Pipeline


def save_pipeline(pipeline: Pipeline, model_dir: str, model_name: str) -> None:
    """
    Save a machine learning pipeline to a file using pickle.

    Args:
        pipeline (sklearn.pipeline): The machine learning pipeline object to save.
        model_dir (str): The directory where the model will be saved.
        model_name (str): The name of the file to save the model as.

    Returns:
        None
    """

    with open(model_dir + model_name, "wb") as file:
        pickle.dump(pipeline, file, protocol=4)


def load_pipeline(model_dir: str, model_name: str) -> Any:
    """
    Load a machine learning pipeline from a file using pickle.

    Args:
        model_dir (str): The directory where the model is saved.
        model_name (str): The name of the file to load the model from.

    Returns:
        Any: The loaded machine learning pipeline object.
    """

    with open(model_dir + model_name, "rb") as file:
        return pickle.load(file)
