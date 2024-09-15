from typing import List, Dict

from transformation.model import DesignEstimator
from visualize.ner import VisualizeNER
from utils.logging import get_logger

LOG = get_logger(__name__)


class VisualizeIncorrectPredictions(VisualizeNER):
    """
    Class representing the implementation for any incorrect prediction visualization.
    """

    def generate_report(self, incorrect_predictions: List[Dict], model: DesignEstimator, file_name: str) -> None:
        """
        Generate a report of the incorrect predictions, which happened after the model training.
        """

        docs = [model.nlp(example['input_text']) for example in incorrect_predictions]

        LOG.info("Start preparing rendering...")
        self.visualize(docs=docs, output_file_name=file_name)
