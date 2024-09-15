from transformation.model import DesignEstimator
from visualize.ner import VisualizeNER

from utils.logging import get_logger

LOG = get_logger(__name__)


class VisualizePrediction(VisualizeNER):
    """
    Class visualizing any predictions, made by the NER model training.
    """

    def generate_report(self, model: DesignEstimator, file_name: str, trained_data) -> None:
        """
        Visualizes model predictions for the provided designs.
        """

        x_predict_as_doc = model.predict(trained_data, as_doc=True)

        LOG.info("Start preparing rendering...")
        self.visualize(docs=x_predict_as_doc.y[:10], output_file_name=file_name)
