from typing import List

import pandas as pd

from utils.logging import get_logger

LOG = get_logger(__name__)


class EvaluationReports:

    def generate_prediction_validation_csv_report(self,
                                                  evaluation_results: List[dict],
                                                  filename: str = 'model_evaluation_report.csv') -> None:
        """
        Should create a .csv report, which are representing the full textual description, with the expected and
        predicted labels and their respective metric scores.

        TODO: This report can be enhanced, to mark directly lines, which have empty predicted labels, to allow the focus
              on these specific items.

        Args:
            evaluation_results (List[dict]): List of dictionaries containing results for a particular evaluation.
            filename (str, optional): Filename of the .csv report.

        Returns:
            None
        """

        report = list()
        for result in evaluation_results:
            report.append([
                result["sentence"],
                result["expected"],
                result["predicted"],
                result["precision"],
                result["recall"],
                result["f1_score"]
            ])

        df_report = pd.DataFrame(report,
                                 columns=["Sentence",
                                          "Expected Annotations",
                                          "Predicted Annotations",
                                          "Precision",
                                          "Recall",
                                          "F1 Score"]
                                 )

        df_report.to_csv(f"../../results/{filename}", sep=';', index=False)
        LOG.debug(f"Report generated successfully: {filename}")
