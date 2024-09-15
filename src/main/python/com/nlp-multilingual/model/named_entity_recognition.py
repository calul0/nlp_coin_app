from typing import List, Dict, Tuple

import pandas as pd
from spacy import displacy

from dto.ner_training_mapping import NERTrainingMappingDTO
from evaluation.scoring import Metrics
from utils.logging import get_logger
from transformation.model import DesignEstimator, load_ner_model_v2

from sklearn.model_selection import train_test_split


LOG = get_logger(__name__)


class ModelTrainingNER:
    def __init__(self, id_col, design_col):
        self.id_col = id_col
        self.design_col = design_col

        # TODO: refactor proper dir implementation
        self.output_dir = "../../results/trained_model/ner/"
        self.model_name = "english_cno"

    def ner_model_training(self, annotated_designs: pd.DataFrame) -> Tuple[NERTrainingMappingDTO, List[Dict]]:
        """
        This method is splitting the dataset, trains the NER Model, evaluates it and returns training and testing
        along with predictions. It splits into a 75% train & 25% testing ratio.
        """

        x_train, x_test, y_train, y_test = train_test_split(annotated_designs[[self.id_col, self.design_col]],
                                                            annotated_designs[[self.id_col, "annotations"]],
                                                            test_size=0.25,
                                                            random_state=12)
        y_test = y_test.rename(columns={"annotations": "y"})
        x_test.index = [i for i in range(x_test.shape[0])]
        y_test.index = [i for i in range(y_test.shape[0])]

        my_estimator = DesignEstimator(4, self.output_dir, self.model_name, self.id_col, self.design_col)
        # TODO: Add consts
        my_estimator.set_labels("PERSON", "OBJECT", "ANIMAL", "PLANT")
        my_estimator.fit(x_train, y_train.annotations)

        # TODO: Call Model Evaluation - better to split later?
        x_predict = self.model_evaluation(x_test=x_test, y_test=y_test, estimator=my_estimator)

        misclassified_examples = self.collection_misclassifications(x_test, y_test, x_predict)

        return NERTrainingMappingDTO(
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
            x_predict=x_predict,
        ), misclassified_examples

    def model_evaluation(self, x_test: pd.DataFrame, y_test: pd.DataFrame, estimator: DesignEstimator) -> pd.DataFrame:
        """
        Evaluates trained NER Model on test data and logs performance metrics.
        """

        model = load_ner_model_v2(self.output_dir, self.model_name, self.id_col, self.design_col)
        x_predict = model.predict(x_test, as_doc=False)

        metrics = Metrics()
        scores_frame = metrics.create_score_frame(y_test, x_predict, estimator.get_labels())

        LOG.info(f"Show scores Frame: {scores_frame}")

        precision, recall = metrics.score_precision_recall(y_test, x_predict)
        F1 = (2 * precision * recall) / (precision + recall)

        LOG.info(f"Precision: {round(precision * 100,2)}")
        LOG.info(f"Recall: {round(recall * 100, 2)}")
        LOG.info(f"F1: {round(F1 * 100, 2)}")

        #misclassified_examples = self.collection_misclassifications(x_test, y_test, x_predict)
        #self.visualize_misclassified_examples(misclassified_examples, model)

        return x_predict

    def collection_misclassifications(self, x_test, y_test, x_predict):
        misclassified_examples = list()
        for idx, (true_labels, pred_labels) in enumerate(zip(y_test['y'], x_predict)):
            if true_labels != pred_labels:
                misclassified_examples.append({
                    'index': idx,
                    'input_text': x_test.iloc[idx][self.design_col],
                    'true_label': true_labels,
                    'pred_label': pred_labels,
                })

        return misclassified_examples

    def visualize_misclassified_examples(self, misclassified_examples, model):
        colors = {'PERSON': 'mediumpurple', 'OBJECT': 'greenyellow', 'ANIMAL': 'orange', 'PLANT': 'salmon'}
        options = {'ents': ['PERSON', 'OBJECT', 'ANIMAL', 'PLANT'], 'colors': colors}

        docs = []
        for example in misclassified_examples:
            doc = model.nlp(example['input_text'])
            docs.append(doc)

        html = displacy.render(docs, style='ent', page=True, options=options)

        with open(self.output_dir + 'misclassified_examples.html', 'w') as file:
            file.write(html)
            LOG.info(f"Misclassified examples visualization saved to {self.output_dir + 'misclassified_examples.html'}")
