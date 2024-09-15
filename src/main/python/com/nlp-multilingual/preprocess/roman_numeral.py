import swifter
import pandas as pd

from configuration.en_ner import EnglishNERConfiguration
from configuration.en_re import EnglishREConfiguration

from dto.ner_training_mapping import NERTrainingMappingDTO
from preprocess.base import Preprocess
from transformation.annotator import annotate_designs
from utils.logging import get_logger

LOG = get_logger(__name__)


class RomanNumeralPreprocess:
    """
    This class contains the preprocess steps for Roman Numeral data set.
    """

    def __init__(self,
                 annotated_designs: pd.DataFrame,
                 ner_configuration: EnglishNERConfiguration,
                 re_configuration: EnglishREConfiguration) -> None:
        self.annotated_designs = annotated_designs
        self.en_ner_config = ner_configuration
        self.en_re_config = re_configuration
        self.roman_numerals = [" I.", " II.", " III.", " IV.", " V."]

        self._preprocess = Preprocess()

    @property
    def preprocess(self) -> Preprocess:
        """
        Getter method for the preprocess property.
        """
        return self._preprocess

    def apply_alternative_name_rule(self, entities: pd.DataFrame) -> Preprocess:
        """
        This method applies all alternative names into the rules list of the preprocessor.
        """

        self._preprocess.add_rule(original="horseman", preprocessed="horse man")
        self._preprocess.add_rule(original="horsemen", preprocessed="horse men")

        for _, row in entities.iterrows():

            if row["alternativenames_en"] is not None:
                standard_name = row["name_en"]
                alt_names = row["alternativenames_en"].split(", ")

                for alt_name in alt_names:
                    self._preprocess.add_rule(alt_name, standard_name)

        return self._preprocess

    def remove_roman_numerals(self):
        """
        Rules are getting deleted, related to roman numerals.
        """

        self._preprocess.rules = {rule: value for rule, value in self._preprocess.rules.items() if not any(roman in rule for roman in self.roman_numerals)}

    def replace_roman_numerals_in_design(self, designs) -> None:
        """
        Replacing roman numerals at designs.

        Args:
            designs: This contains dataframe, holding the designs. Important, different input for NER and RE.

        Returns:
            None
        """

        for index, row in self.annotated_designs.iterrows():
            for roman in self.roman_numerals:
                if roman in row["design_en"]:
                    designs.at[index, "design_en"] = row["design_en"].replace(roman, roman.strip('.'))

    def filter_characters(self, attr: str = 'ner'):

        try:
            if attr == 'ner':
                design_col = self.en_ner_config.design_col
                id_col = self.en_ner_config.id_col
                column_annotation = 'annotations'
            elif attr == 're':
                design_col = self.en_re_config.design_col
                id_col = self.en_re_config.id_col
                column_annotation = 'y'
            else:
                LOG.error("Others not implemented...")
                raise

            self.annotated_designs["design_en_changed"] = self.annotated_designs.swifter.apply(
                lambda row: self._preprocess.preprocess_design(
                    getattr(row, design_col), getattr(row, id_col))[0],
                axis=1
            )
            self.annotated_designs["design_en_changed"] = self.annotated_designs.swifter.apply(
                lambda row: row["design_en_changed"].replace("?", "").replace("(", "").replace(")", ""), axis=1)

            self.annotated_designs.rename(
                columns={"design_en": "design_en_orig",
                         "design_en_changed": "design_en",
                         column_annotation: "annotations_orig"},
                inplace=True
            )
        except Exception as e:
            LOG.error(f"Following warning: {e}")
            raise

    def mapping_gt(self) -> pd.DataFrame:
        self.annotated_designs["y"] = self.annotated_designs.swifter.apply(
            lambda row: self._preprocess.preprocess_re(
                row["annotations_orig"],
                getattr(row, self.en_re_config.id_col)),
            axis=1
        )

        return self.annotated_designs

    def annotating_designs(self, entities: dict) -> pd.DataFrame:
        train_designs = annotate_designs(entities,
                                         self.annotated_designs[["id", "design_en"]],
                                         "id",
                                         "design_en")
        train_designs = train_designs[
            train_designs.annotations.map(len) > 0]
        annotated_designs = self.annotated_designs.merge(train_designs[["id", "annotations"]], left_on="id", right_on="id")

        LOG.info(f"Head of Annotate after training: {annotated_designs.head(5)}")
        LOG.info(f"Annotated_designs shape: {annotated_designs.shape}")

        return annotated_designs

def map_back_original(preprocess: Preprocess, trained_data: NERTrainingMappingDTO) -> NERTrainingMappingDTO:
    trained_data.x_test['y'] = trained_data.y_test['y']

    trained_data.x_test["design_en_orig"] = trained_data.x_test.swifter.apply(
        lambda row: preprocess.map_back_design(
            row.design_en,
            row.id
        )
        if row.id in preprocess.rules_applied else row.design_en, axis=1
    )

    trained_data.x_test["y_orig"] = trained_data.x_test.swifter.apply(
        lambda row: preprocess.map_result_ner(
            row.design_en,
            row.y,
            row.id
        )
        if row.id in preprocess.rules_applied else row.y, axis=1
    )

    trained_data.x_test.loc[trained_data.x_test.design_en.str.contains("Alexander III")]
    #LOG.info({trained_data.x_test.loc[trained_data.x_test.design_en.str.contains("Veil")].head(5)})

    return trained_data