from dto.re_training_mapping import RETrainingMappingDTO
from dto.ner_training_mapping import NERTrainingMappingDTO
from preprocess.base import Preprocess


def convert_re_mapping_to_original_state(
        preprocess: Preprocess,
        trained_data: RETrainingMappingDTO
) -> RETrainingMappingDTO:
    """
    This helper function converts back to original state.
    """
    trained_data.x_test["y"] = trained_data.y_test["y"]
    trained_data.x_test["y_mapped"] = trained_data.x_test.swifter.apply(
        lambda row: preprocess.map_re(
            row["y"],
            row.design_id
        ),
        axis=1
    )

    return trained_data


def convert_nre_mapping_to_original_state(
        preprocess: Preprocess,
        trained_data: NERTrainingMappingDTO
) -> NERTrainingMappingDTO:
    # TODO: Is this not used anymore? Need to check this function
    trained_data.x_test['y'] = trained_data.y_test['y']
    LOG.info(f"Checking x_test: {trained_data.x_test}")

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