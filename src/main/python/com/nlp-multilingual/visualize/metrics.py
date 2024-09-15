import logging
from typing import List

import numpy as np
import seaborn as sns

from matplotlib import pyplot as plt


logging.getLogger('matplotlib.colorbar').setLevel(logging.ERROR)


class MetricsVisualizer:
    def __init__(self):
        self.path_to_save = '../../results'

    def visualize_individual_confusion_matrix(self, confusion_matrix, labels, class_index, class_name):
        plt.figure(figsize=(6, 4))
        sns.heatmap(confusion_matrix[class_index], annot=True, fmt="d",
                    xticklabels=['Not ' + labels[class_index], labels[class_index]],
                    yticklabels=['Not ' + labels[class_index], labels[class_index]], cmap='Blues')
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.title(f'Confusion Matrix for {labels[class_index]}')
        plt.savefig(f'{self.path_to_save}/confusion_matrix/{class_name}.png')
        plt.close()

    def plot_classification_report(self,
                                   labels_location: np.ndarray,
                                   precision: List[float],
                                   recall: List[float],
                                   f1_score: List[float],
                                   labels: List[str]) -> None:
        """
        Should visualize the classification report inside a plot. Uses the calculated scores from computation.

        Args:
            labels_location (np.ndarray): Positions of the labels
            precision (List[float]): Precision values
            recall (List[float]): Recall values
            f1_score (List[float]): F1 values
            labels (List[str]): Labels

        Returns:
            None
        """

        width = 0.25

        fig, ax = plt.subplots(figsize=(12, 8))
        precision_bar = ax.bar(labels_location - width, precision, width, label='Precision')
        recall_bar = ax.bar(labels_location, recall, width, label='Recall')
        f1_score_bar = ax.bar(labels_location + width, f1_score, width, label='F1 Score')

        ax.set_xlabel('Labels')
        ax.set_ylabel('Scores')
        ax.set_title('Classification Report Metrics by Label')
        ax.set_xticks(labels_location)
        ax.set_xticklabels(labels, rotation=45)
        ax.legend()

        self.autolabel(precision_bar, ax)
        self.autolabel(recall_bar, ax)
        self.autolabel(f1_score_bar, ax)

        plt.savefig(f'{self.path_to_save}/classification_report.png')
        plt.close()

    def autolabel(self, rects, ax):
        """
        Helper function. Attach a text label above each bar in *rects*, displaying its height.
        """
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(round(height, 2)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
