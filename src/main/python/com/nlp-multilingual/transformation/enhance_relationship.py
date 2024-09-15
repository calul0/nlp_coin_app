import sklearn
import pandas as pd

#from ydata_profiling import ProfileReport

from configuration.en_re import EnglishREConfiguration
from dto.re_training_mapping import RETrainingMappingDTO
from transformation.model import relations_from_adjectives_df, relations_from_adjectives_single, \
    predict_re_single_sentence, concat_relations
from utils.logging import get_logger

LOG = get_logger(__name__)


def enhance_relationship(y_pred: pd.DataFrame,
                         trained_data: RETrainingMappingDTO,
                         pipeline_model: sklearn.pipeline.Pipeline) -> None:
    """
    This function will provide the auto relations. It's about enhancing the relationship extraction process, by
    automatically identifying and mapping specific adjectives to predefined relationships. This can help in situations
    where the model might miss certain relations that are easily inferred from common adjectives. The purpose of this
    function serves as an additional layer of relationship extraction that complements the model's prediction.
    """

    en_re_config = EnglishREConfiguration()
    ner_model_directory = "../../results/trained_model/ner/"

    obj_list = {
        "veiled": ("wearing", "Veil", "before"),
        "draped": ("wearing", "Clothing", "before"),
        "helmeted": ("wearing", "Helmet", "before"),
        "diademed": ("wearing", "Diadem", "before"),
        "turreted": ("wearing", "Mural crown", "before"),
        "enthroned": ("seated_on", "Throne", "after"),
    }

    y_pred["design_en"] = getattr(trained_data.x_test, en_re_config.design_col)
    y_pred = relations_from_adjectives_df(df =y_pred,
                                          design_column="design_en",
                                          pred_column="y",
                                          ner_model_directory=ner_model_directory,
                                          ner_model_name=en_re_config.model_name,
                                          id_col=en_re_config.id_col,
                                          design_col=en_re_config.design_col,
                                          obj_list=obj_list,
                                          entities_to_consider=["PERSON"])
    #LOG.info(f"y_predictions: {y_pred}")

    design = "Diademed Athena to the left and helmeted Ares to the right, holding swo."
    auto_relations = relations_from_adjectives_single(design=design,
                                                      ner_model_directory=ner_model_directory,
                                                      ner_model_name=en_re_config.model_name,
                                                      id_col=en_re_config.id_col,
                                                      design_col=en_re_config.design_col,
                                                      obj_list=obj_list)
    model_relations = predict_re_single_sentence(model=pipeline_model,
                                                 sentence=design,
                                                 id_col=en_re_config.id_col,
                                                 design_col=en_re_config.design_col)
    concat_result = concat_relations(auto_relations=auto_relations, model_relations=model_relations)
    LOG.info(f"Result of concat relations: {concat_result}")

    #profile = ProfileReport(y_pred, title="Auto Relations of RE")
    #profile.to_file("../../results/reports/profiling/re_auto_relations.html")
    #profile.to_file("../../results/reports/profiling/re_auto_relations.json")
