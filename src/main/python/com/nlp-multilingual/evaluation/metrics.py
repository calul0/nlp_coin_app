from typing import List

from sklearn.metrics import (hamming_loss,
                             accuracy_score,
                             jaccard_score,
                             multilabel_confusion_matrix,
                             precision_score,
                             recall_score,
                             f1_score)

from visualize.metrics import MetricsVisualizer


class MetricsEvaluation:
    def __init__(self, pipeline, training_data: dict):
        self.pipeline = pipeline
        self.training_data = training_data

    def precision(self, average: str = 'samples') -> float:
        """
        Should calculate the precision score.

        Args:
            average (str): Different approaches options such as samples, weighted, micro, macro

        Returns:
            precision (float): Precision score
        """

        precision = precision_score(self.training_data['true_encoded'],
                                    self.training_data['pred_encoded'],
                                    average=average)

        return precision

    def recall(self, average: str = 'samples') -> float:
        """
        Should calculate the recall score.

        Args:
            average (str): Different approaches options such as samples, weighted, micro, macro

        Returns:
            recall (float): Recall score
        """

        recall = recall_score(self.training_data['true_encoded'],
                              self.training_data['pred_encoded'],
                              average=average)

        return recall

    def f1_score(self, average: str = 'samples') -> float:
        """
        Should calculate the f1 score.

        Args:
            average (str): Different approaches options such as samples, weighted, micro, macro

        Returns
            f1 (float): F1 score
        """
        f1 = f1_score(self.training_data['true_encoded'],
                      self.training_data['pred_encoded'],
                      average=average)

        return f1

    def hamming_loss(self):
        """
        Should measure the fraction of labels that are incorrectly predicted.
        """

        loss = hamming_loss(self.training_data['true_encoded'], self.training_data['pred_encoded'])
        return loss

    def subset_accuracy(self):
        """
        The proportion of instances where all labels are correctly predicted.
        """

        subset_accuracy = accuracy_score(self.training_data['true_encoded'], self.training_data['pred_encoded'])
        return subset_accuracy

    def jaccard_index(self):
        """
        Should measure the similarity between predicted and true set of labels.

        Returns:
            score (int): Jaccard index
        """

        score = jaccard_score(self.training_data['true_encoded'], self.training_data['pred_encoded'], average='samples')
        return score

    def confusion_matrix(self) -> List:
        """
        Should create the confusion matrix. Since it's not directly applicable to MultiBinaryLabels, it's necessary to
        iterate on the object differently.
        """

        cm_list = list()

        true_encoded = self.training_data['true_encoded']
        pred_encoded = self.training_data['pred_encoded']

        mlb_confusion_matrix = multilabel_confusion_matrix(true_encoded, pred_encoded)

        metrics_visualizer = MetricsVisualizer()

        for label_name in self.training_data['mlb'].classes_:
            class_index = list(self.training_data['mlb'].classes_).index(label_name)
            metrics_visualizer.visualize_individual_confusion_matrix(confusion_matrix=mlb_confusion_matrix,
                                                                     labels=self.training_data['mlb'].classes_,
                                                                     class_index=class_index,
                                                                     class_name=label_name)

        return cm_list
