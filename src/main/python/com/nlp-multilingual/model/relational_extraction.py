import numpy as np
import pandas as pd
import sklearn

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report

from configuration.en_re import EnglishREConfiguration
from dto.re_training_mapping import RETrainingMappingDTO
from model.pipeline_functions import save_pipeline, load_pipeline
from preprocess.split_train_test import enhance_imbalanced_test_split, default_train_test_split

from transformation.extractor.feature import FeatureExtractor
from transformation.extractor.relation import RelationExtractor
from transformation.transformer.ner import NERTransformer
from transformation.prepare_data_for_sklearn import prepare_dict_with_binary
from utils.helper_functions import safe_eval

from utils.logging import get_logger
from transformation.transformer.path_too_string import Path2Str
from visualize.metrics import MetricsVisualizer

LOG = get_logger(__name__)

pd.set_option("display.max_colwidth", None)
pd.set_option('display.max_rows', 600)


uppercase_classes = ['PERSON', 'OBJECT', 'ANIMAL', 'PLANT']


class ModelTrainingRelationalExtraction:
    def __init__(self):
        self.en_re_config = EnglishREConfiguration()
        self.classifier = None
        self.feature = None
        self.pipeline = None
        self.re_map_dto = None

    def define_logistic_regression_as_classifier(self, iterations: int = 1000) -> None:
        """
        Initialize the Logistic Regression model, which is used for the sklearn pipeline.

        Args:
            iterations (int, optional): Number of maximum iterations for the regression model.

        Returns:
            None
        """

        self.classifier = LogisticRegression(max_iter=iterations, verbose=0)
        LOG.debug(f"Logistic Regression classifier defined with max_iter={iterations}")

    def construct_feature_pipeline(self, verbose: bool = True) -> None:
        """
        Uses the scikit learn make_pipeline method to construct a Pipeline object from the list of Estimators.

        Args:
            verbose (bool, optional): Option to turn on verbose mode.

        Returns:
            None
        """

        string_converter = Path2Str(pos=True)
        vectorizer = CountVectorizer(ngram_range=(1, 3))
        self.feature = make_pipeline(string_converter, vectorizer, verbose=verbose)
        LOG.debug("Feature pipeline constructed with Path2Str and CountVectorizer")

    def prepare_test_and_train_data(self, matrix: pd.DataFrame) -> RETrainingMappingDTO:
        """
        This method will use the train_test_split() method from scikit learn to distribute into random train and test
        subsets.

        Returns:
            RETrainingMappingDTO: DTO mapped with all dataframes.
        """

        label_counts = matrix["y"].apply(pd.Series).stack().value_counts()
        LOG.info(f"Label counts before training: {label_counts}")

        if 'y' in matrix.columns:
            annotations = matrix['y'].apply(safe_eval)
            #self.re_map_dto = enhance_imbalanced_test_split(annotations=annotations, matrix=matrix)
            self.re_map_dto = default_train_test_split(matrix=matrix)
        else:
            print("Column 'y' not found in the DataFrame.")

        return self.re_map_dto

    def finalize_pipeline_definition(self, ner_model_directory: str, exModelname="") -> None:
        """
        Method is preparing the pipelines with the method of sklearn. There is a difference in using Pipeline and
        the method make_pipeline from documentation of sklearn. Since Pipeline needs to be defined more granularity,
        here it's decided to use the make_pipeline method. In case of fine-tuning, it would make sense to check this
        step.

        Args:
            ner_model_directory (str): Directory where NER model is stored.

        Returns:
            None
        """

        inner_pipeline = make_pipeline(self.feature, self.classifier, verbose=True)
        modelname = self.en_re_config.model_name + exModelname
        self.pipeline = make_pipeline(
            NERTransformer(
                model_dir=ner_model_directory,
                model_name=modelname,
                id_col=self.en_re_config.id_col,
                design_col=self.en_re_config.design_col
            ),
            FeatureExtractor(
                model_dir=ner_model_directory,
                model_name=modelname,
                id_col=self.en_re_config.id_col,
                design_col=self.en_re_config.design_col
            ),
            RelationExtractor(
                pipeline=inner_pipeline,
                output_dir=self.en_re_config.model_directory,
                model_name=modelname,
                id_col=self.en_re_config.id_col
            ),
            verbose=True
        )

    def train_model(self) -> None:
        """
        Should take the pipeline, which has all transformers, estimators, classifiers defined and trains
        in iterations. With pipeline verbose mode enabled, it's possible to see the stages.

        Returns:
            None
        """

        self.pipeline.fit(self.re_map_dto.x_train, self.re_map_dto.y_train)
        LOG.debug(f"Pipeline trained successfully")

    def compute_classification_report(self) -> None:
        """
        Method will flatten the data accordingly, so that it can be ingested into the classification report of sklearn.
        This flattening is required due to the fact, that the data is now in the right structure, as sklearn methods
        are expecting.

        Returns:
            None
        """

        trained_data_for_sklearn = prepare_dict_with_binary(pipeline=self.pipeline, training_data=self.re_map_dto)
        class_report = classification_report(trained_data_for_sklearn['true_encoded'],
                                             trained_data_for_sklearn['pred_encoded'],
                                             target_names=trained_data_for_sklearn['mlb'].classes_,
                                             output_dict=True,
                                             zero_division=0)
        LOG.debug(f"Classification Report:\n{class_report}")

        labels = list(class_report.keys())[:-3]
        precision = [class_report[label]['precision'] for label in labels]
        recall = [class_report[label]['recall'] for label in labels]
        f1_score = [class_report[label]['f1-score'] for label in labels]
        labels_location = np.arange(len(labels))

        metrics_visualizer = MetricsVisualizer()
        metrics_visualizer.plot_classification_report(labels_location=labels_location,
                                                      precision=precision,
                                                      recall=recall,
                                                      f1_score=f1_score,
                                                      labels=labels)

    def save_model(self,  exModelname = "") -> None:
        """
        Wrapper method to save the model by calling the save_pipeline method.

        Returns:
            None
        """

        save_pipeline(self.pipeline, self.en_re_config.model_directory, self.en_re_config.model_name + exModelname)

    def load_model(self,exModelname = "") -> sklearn.pipeline.Pipeline:
        """
        Wrapper method to load existing saved pipeline.

        Returns:
            pipeline_mode (sklearn.pipeline): Pipeline object, storing the model.
        """

        pipeline_model = load_pipeline(self.en_re_config.model_directory, self.en_re_config.model_name + exModelname)
        return pipeline_model
