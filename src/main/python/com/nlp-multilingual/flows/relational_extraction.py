from typing import Tuple, Any, Dict, Union, Set
import pandas as pd
import sklearn

from configuration.en_ner import EnglishNERConfiguration
from configuration.en_re import EnglishREConfiguration

from database.connector import DatabaseConnector
from database.operations import DatabaseOperations

from dto.re_training_mapping import RETrainingMappingDTO
from evaluation.metrics import MetricsEvaluation
from evaluation.scoring import Metrics
from model.relational_extraction import ModelTrainingRelationalExtraction
from preprocess.roman_numeral import RomanNumeralPreprocess

from transformation.aggregation import aggregate_design_data
from transformation.enhance_relationship import enhance_relationship
from transformation.map_to_original_state import convert_re_mapping_to_original_state
from transformation.prepare_data_for_sklearn import prepare_dict_with_binary
from utils.logging import get_logger
from verification.model_training import evaluate_model

LOG = get_logger(__name__)


class WorkflowRelationalExtraction:
    def __init__(self):
        self.en_ner_config = EnglishNERConfiguration()
        self.en_re_config = EnglishREConfiguration()

        self.roman_preprocess = None

    def run_process_with_path_and_data_and_entites(self, query_option="all"):
        with DatabaseConnector() as mysql_connection:
            database_operations = DatabaseOperations(connector=mysql_connection)

            train = self.fetch_from_training(database_ops=database_operations, query_option=query_option)
            entities = self.fetch_entities(database_ops=database_operations)

            if len(train) == 0:
                return pd.DataFrame(), pd.DataFrame(), self.getEmptyModelMetrics()

            X = self.run_data_aggregation(train=train)
            X = self.roman_numeral_steps(X=X, entities=entities)

            trained_data, pipeline_model = self.train_model_steps(X=X)
            model_metrics = self.model_verification_step(training_data=trained_data, model=pipeline_model)
            trained_data = self.map_back_to_original(trained_data=trained_data)
            y_pred = pipeline_model.predict(trained_data.x_test)
            self.enhance_relationship_step(trained_data=trained_data, pipeline_model=pipeline_model)
            return y_pred, trained_data, model_metrics

    def run_process(self):
        with DatabaseConnector() as mysql_connection:
            database_operations = DatabaseOperations(connector=mysql_connection)

            train = self.fetch_from_training(database_ops=database_operations)
            entities = self.fetch_entities(database_ops=database_operations)

            X = self.run_data_aggregation(train=train)
            X = self.roman_numeral_steps(X=X, entities=entities)

            trained_data, pipeline_model = self.train_model_steps(X=X)

            self.model_verification_step(training_data=trained_data, model=pipeline_model)

            trained_data = self.map_back_to_original(trained_data=trained_data)

            self.enhance_relationship_step(trained_data=trained_data, pipeline_model=pipeline_model)

    def fetch_from_training(self, database_ops: DatabaseOperations, query_option="all") -> pd.DataFrame:
        if query_option == "all":
            query = """
                        SELECT 
                            re.design_id, 
                            nlp.design_en,
                            ner_s.name_en AS s, 
                            ner_s.class AS subject_class, 
                            ner_p.name_en AS p, 
                            ner_o.name_en AS o, 
                            ner_o.class AS object_class
                        FROM 
                            nlp_relation_extraction_en_v2 AS re
                            JOIN nlp_training_designs AS nlp ON re.design_id = nlp.id
                            JOIN nlp_list_entities_v2 AS ner_s ON re.subject = ner_s.id
                            JOIN nlp_list_entities_v2 AS ner_p ON re.predicate = ner_p.id
                            JOIN nlp_list_entities_v2 AS ner_o ON re.object = ner_o.id;
                    """
        else:
            query = """
                                    SELECT 
                                        re.design_id, 
                                        nlp.design_en,
                                        ner_s.name_en AS s, 
                                        ner_s.class AS subject_class, 
                                        ner_p.name_en AS p, 
                                        ner_o.name_en AS o, 
                                        ner_o.class AS object_class
                                    FROM 
                                        nlp_relation_extraction_en_v2 AS re
                                        JOIN nlp_training_designs AS nlp ON re.design_id = nlp.id
                                        JOIN nlp_list_entities AS ner_s ON re.subject = ner_s.id
                                        JOIN nlp_list_entities AS ner_p ON re.predicate = ner_p.id
                                        JOIN nlp_list_entities AS ner_o ON re.object = ner_o.id
                                        WHERE nlp.comment='%s';
                                """ % query_option
        return database_ops.execute_custom_sql_query(query=query)

    def fetch_entities(self, database_ops: DatabaseOperations) -> pd.DataFrame:
        return database_ops.load_from_db(table_name="nlp_list_entities", column_list=self.en_re_config.add_columns)

    def run_data_aggregation(self, train: pd.DataFrame) -> pd.DataFrame:
        return aggregate_design_data(train=train)

    def roman_numeral_steps(self, X: pd.DataFrame, entities: pd.DataFrame) -> pd.DataFrame:
        LOG.info(f"Starting preprocessing...")
        self.roman_preprocess = RomanNumeralPreprocess(annotated_designs=X,
                                                       ner_configuration=self.en_ner_config,
                                                       re_configuration=self.en_re_config)

        self.roman_preprocess.apply_alternative_name_rule(entities=entities)
        self.roman_preprocess.remove_roman_numerals()
        self.roman_preprocess.replace_roman_numerals_in_design(designs=X)
        self.roman_preprocess.filter_characters(attr='re')
        return self.roman_preprocess.mapping_gt()

    def train_model_steps(self, X: pd.DataFrame) -> Tuple[RETrainingMappingDTO, Any]:
        """
        Step to receive model and trained data back.
        # TODO: Type hinting Any is just temporary. Needs proper Type hint edit.

        Args:
            X (pd.DataFrame): Dataframe containing training data.

        Returns
            Tuple[RETrainingMappingDTO, Any]
        """

        LOG.info(f"Starting training...")
        re_model_training = ModelTrainingRelationalExtraction()
        re_model_training.define_logistic_regression_as_classifier()
        re_model_training.construct_feature_pipeline()
        trained_data = re_model_training.prepare_test_and_train_data(matrix=X)
        re_model_training.finalize_pipeline_definition(ner_model_directory=self.en_ner_config.model_directory)

        re_model_training.train_model()
        re_model_training.compute_classification_report()

        re_model_training.save_model()
        pipeline_model = re_model_training.load_model()

        return trained_data, pipeline_model

    def getEmptyModelMetrics(self):
        return {
            "Hamming Loss": round(0, 2),
            "Subset Accuracy": round(0, 2),
            "Jaccard Index": round(0, 2),
            "Precision (scikit-learn)": round(0, 2),
            "Recall (scikit-learn)": round(0, 2),
            "F1 Score (scikit-learn)": round(0, 2),
            "Precision": round(0,2),
            "Recall": round(0,2),
            "F1": round(0,2)
        }

    def model_verification_step(self, training_data: RETrainingMappingDTO, model: sklearn.pipeline.Pipeline) -> Dict[
        str, Union[Union[float, Set[Union[int, Any]], Set[Union[Union[int, float], Any]]], Any]]:
        """
        This method is initializing the model verification step and calls the methods to retrieve respective metrics for
        the full training set. Furthermore, Metrics can be only calculated with the help of scikit-learn, if the data
        is accordingly transformed to binary values. Any textual description would need to be vectorized.

        Args:
            training_data (RETrainingMappingDTO): Dataframe containing training data.
            model (sklearn.pipeline.Pipeline): Model, which is already trained.

        Returns:
            None
        """

        evaluate_model(model=model, training_data=training_data)

        data_prepared_for_sklearn_format = prepare_dict_with_binary(pipeline=model, training_data=training_data)

        metrics_evaluation = MetricsEvaluation(pipeline=model, training_data=data_prepared_for_sklearn_format)
        metrics_evaluation.confusion_matrix()
        hamming_loss = metrics_evaluation.hamming_loss()
        subset_accuracy = metrics_evaluation.subset_accuracy()
        jaccard_index = metrics_evaluation.jaccard_index()
        precision = metrics_evaluation.precision(average='samples')
        recall = metrics_evaluation.recall(average='samples')
        f1 = metrics_evaluation.f1_score(average='samples')

        LOG.info(f"Hamming Loss: {hamming_loss}")
        LOG.info(f"Subset Accuracy: {subset_accuracy}")
        LOG.info(f"Jaccard Index: {jaccard_index}")
        LOG.info(f"Precision: {round(precision * 100, 2)}")
        LOG.info(f"Recall: {round(recall * 100, 2)}")
        LOG.info(f"F1 Score: {round(f1 * 100, 2)}")

        LOG.info(f"Karstens Scores")
        carstens_metrics = Metrics()

        y_pred = model.predict(training_data.x_test)
        carsten_precision, carsten_recall = carstens_metrics.score_precision_recall(y_true=training_data.y_test,
                                                                                    y_pred=y_pred)
        LOG.info(f"Carsten Precision: {carsten_precision*100}")
        LOG.info(f"Carsten Recall: {carsten_recall*100}")
        LOG.info(f"Carsten F1: {100 * ((carsten_precision * 2 * carsten_recall) / (carsten_recall + carsten_precision))}")

        # TODO: Need to be segregated from this place due to fast implementation
        #y_pred.to_csv(f"../../results/trainings_set/y_pred.csv")
        #training_data.y_test.to_csv(f"../../results/trainings_set/y_test.csv")

        model_metrics = {
            "Hamming Loss": round(hamming_loss*100,2),
            "Subset Accuracy": round(subset_accuracy*100,2),
            "Jaccard Index": round(jaccard_index*100,2),
            "Precision (scikit-learn)": round(precision * 100, 2),
            "Recall (scikit-learn)": round(recall * 100, 2),
            "F1 Score (scikit-learn)": round(f1 * 100, 2),
            "Precision": round(carsten_precision*100, 2),
            "Recall": round(carsten_recall*100, 2),
            "F1": round(100 * ((carsten_precision * 2 * carsten_recall) / (carsten_recall + carsten_precision)) , 2)
        }
        return model_metrics

    def map_back_to_original(self, trained_data: RETrainingMappingDTO) -> RETrainingMappingDTO:
        return convert_re_mapping_to_original_state(preprocess=self.roman_preprocess.preprocess,
                                                    trained_data=trained_data)

    def enhance_relationship_step(self,
                                  trained_data: RETrainingMappingDTO,
                                  pipeline_model: Any) -> None:
        y_pred = pipeline_model.predict(trained_data.x_test)
        enhance_relationship(y_pred=y_pred, trained_data=trained_data, pipeline_model=pipeline_model)