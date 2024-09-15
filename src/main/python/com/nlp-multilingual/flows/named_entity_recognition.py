from configuration.en_ner import EnglishNERConfiguration
from configuration.en_re import EnglishREConfiguration
from database.connector import DatabaseConnector
from database.operations import load_entities_from_db, DatabaseOperations
from dto.entities import EntitiesDTO
from model.named_entity_recognition import ModelTrainingNER
from preprocess.roman_numeral import RomanNumeralPreprocess, map_back_original
from transformation.annotator import annotate_designs
from transformation.model import load_ner_model_v2
from transformation.stem_lemma_annotation import StemLemmaAnnotatizer
from utils.logging import get_logger
from verification.model_training import verify_model_training
from visualize.prediction import VisualizePrediction
from visualize.incorrect_predictions import VisualizeIncorrectPredictions

LOG = get_logger(__name__)


class WorkflowNamedEntityRecognition:
    def __init__(self):
        self.mapped_back_training_data = None
        self.en_ner_config = EnglishNERConfiguration()
        self.en_re_config = EnglishREConfiguration()

        self.mysql_connection = None
        self.database_operations = None
        self.designs = None
        self.df_entities = None
        self.dict_of_entities = None
        self.annotated_designs = None
        self.incorrect_predictions_data = None
        self.mapped_trained_data = None
        self.roman_preprocess = None

    def run_process(self) -> None:
        with DatabaseConnector() as self.mysql_connection:
            self.database_operations = DatabaseOperations(connector=self.mysql_connection)

            self.fetch_designs()
            self.fetch_entities()
            self.execute_annotation_step()
            self.run_stem_lemma_annotation_step()
            self.fetch_plain_entities()
            self.run_roman_numeral_step()
            self.run_ner_training_step()
            self.run_verification_step()
            self.map_back_to_original_step()
            self.visualize_step()
            LOG.info("Successfully finished all NER English Training steps...")

    def fetch_designs(self) -> None:
        """
        This step is fetching the designs from the nlp_training_designs table.
        """

        self.designs = self.database_operations.load_from_db(
            table_name="nlp_training_designs",
            column_list=[self.en_ner_config.id_col, self.en_ner_config.design_col]
        )

    def fetch_entities(self) -> None:
        tmp_add_cols = ["id", "name_en", "alternativenames_en"]
        entities = EntitiesDTO(
            person=load_entities_from_db(table_name="nlp_list_entities",
                                         entity="PERSON",
                                         column_list=tmp_add_cols,
                                         mysql_connection=self.mysql_connection,
                                         columns_multi_entries=[tmp_add_cols[1]],
                                         delimiter=",",
                                         has_delimiter=True),
            object=load_entities_from_db(table_name="nlp_list_entities",
                                         entity="OBJECT",
                                         column_list=tmp_add_cols,
                                         mysql_connection=self.mysql_connection,
                                         columns_multi_entries=[tmp_add_cols[1]],
                                         delimiter=",",
                                         has_delimiter=True),
            animal=load_entities_from_db(table_name="nlp_list_entities",
                                         entity="ANIMAL",
                                         column_list=tmp_add_cols,
                                         mysql_connection=self.mysql_connection,
                                         columns_multi_entries=[tmp_add_cols[1]],
                                         delimiter=",",
                                         has_delimiter=True),
            plant=load_entities_from_db(table_name="nlp_list_entities_v3",
                                        entity="PLANT",
                                        column_list=tmp_add_cols,
                                        mysql_connection=self.mysql_connection,
                                        columns_multi_entries=[tmp_add_cols[1]],
                                        delimiter=",",
                                        has_delimiter=True)
        )
        self.dict_of_entities = entities.dict()
        self.dict_of_entities = {key.upper(): value for key, value in self.dict_of_entities.items()}

    def execute_annotation_step(self):
        self.annotated_designs = annotate_designs(entities=self.dict_of_entities,
                                                  designs=self.designs,
                                                  id_col=self.en_ner_config.id_col,
                                                  design_col=self.en_ner_config.design_col)
        self.annotated_designs = self.annotated_designs[self.annotated_designs.annotations.map(len) > 0]

        LOG.info(f"Verification check for Shape: {self.annotated_designs.shape}")

    def run_stem_lemma_annotation_step(self):
        use_lemma_stem = False

        if use_lemma_stem:
            # TODO: Also need to run: python -m spacy download de_core_news_sm ||| and with en_core_web_sm
            annotater = StemLemmaAnnotatizer()
            self.annotated_designs = annotater.annotate(self.annotated_designs,
                                                        self.dict_of_entities,
                                                        self.en_ner_config.id_col,
                                                        self.en_ner_config.design_col)

    def fetch_plain_entities(self) -> None:
        # TODO: column list is hardcoded, can be fixed with .yaml file
        self.df_entities = self.database_operations.load_from_db(
            table_name="nlp_list_entities",
            column_list=self.en_ner_config.add_columns
        )

    def run_roman_numeral_step(self):
        self.roman_preprocess = RomanNumeralPreprocess(annotated_designs=self.annotated_designs,
                                                       ner_configuration=self.en_ner_config,
                                                       re_configuration=self.en_re_config)
        # TODO: Is getter method working here?
        self.roman_preprocess.apply_alternative_name_rule(entities=self.df_entities)
        self.roman_preprocess.remove_roman_numerals()
        self.roman_preprocess.replace_roman_numerals_in_design(designs=self.designs)
        self.roman_preprocess.filter_characters()
        self.annotated_designs = self.roman_preprocess.annotating_designs(entities=self.dict_of_entities)

        LOG.info(f"Annotation Designs Head 5: {self.annotated_designs.head(5).style}")

    def run_ner_training_step(self):
        model_ner_training = ModelTrainingNER(id_col=self.en_ner_config.id_col,
                                              design_col=self.en_ner_config.design_col)
        self.mapped_trained_data, self.incorrect_predictions_data = model_ner_training.ner_model_training(
            annotated_designs=self.annotated_designs)

    def run_verification_step(self):
        verify_model_training(trained_data=self.mapped_trained_data)

    def map_back_to_original_step(self):
        self.mapped_back_training_data = map_back_original(preprocess=self.roman_preprocess.preprocess,
                                                           trained_data=self.mapped_trained_data)

    def visualize_step(self):
        output_dir = "../../results/trained_model/ner/"
        model_name = "english_cno"
        model = load_ner_model_v2(output_dir, model_name, self.en_ner_config.id_col, self.en_ner_config.design_col)

        LOG.info("Visualize Prediction...")
        prediction = VisualizePrediction()
        prediction.generate_report(model=model,
                                   trained_data=self.mapped_back_training_data.x_test,
                                   file_name='snapshot_prediction_report.html')
        # incorrect_prediction = VisualizeIncorrectPredictions()
        # incorrect_prediction.generate_report(incorrect_predictions=incorrect_predictions_data,
        #                                     model=model,
        #                                     file_name='incorrect_predictions.html')
