from typing import List

import pandas as pd
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer

from dto.re_training_mapping import RETrainingMappingDTO
from utils.logging import get_logger

LOG = get_logger(__name__)

uppercase_classes = ['PERSON', 'OBJECT', 'ANIMAL', 'PLANT']


def filter_uppercase_classes(relations: List, classes_of_interest: List) -> List:
    """
    Filter out the uppercased words from the classes list.

    Args:
        relations (list): list of relations
        classes_of_interest (list): list of classes of interest

    Returns:
        filtered_relations (list): list of filtered relations
    """

    filtered_relations = []
    for relation in relations:
        filtered_relation = [label for label in relation if label in classes_of_interest]
        filtered_relations.append(filtered_relation)
    return filtered_relations


def extract_relations(df: pd.DataFrame) -> List:
    """
    Should extract all relations from a dataframe.

    Args:
        df (pd.DataFrame): dataframe, containing the data

    Returns:
        relations (list): list of relations
    """

    relations_list = []

    try:
        for relations in df['y']:
            for relation in relations:
                relations_list.append(relation)

    except KeyError as e:
        LOG.error(f"KeyError: The specified key does not exist in the dataframe. Details: {e}")

    except Exception as e:
        print(f"An error occurred while extracting relations: {e}")

    return relations_list


def prepare_dict_with_binary(pipeline: sklearn.pipeline, training_data: RETrainingMappingDTO) -> dict:
    """
    Prepare the data for scikit-learn by predicting, extracting and binarizing the relations.

    Args:
        pipeline (sklearn.pipeline.Pipeline): Pipeline with all classifier, estimators and transformers.
        training_data (RETrainingMappingDTO): Dataframe containing the training data.

    Returns:
        dict: Dictionary containing the prepared data.
    """

    y_pred = pipeline.predict(training_data.x_test)

    true_relations = extract_relations(df=training_data.y_test)
    pred_relations = extract_relations(df=y_pred)

    #filtered_true_relations = filter_uppercase_classes(true_relations, uppercase_classes)
    #filtered_pred_relations = filter_uppercase_classes(pred_relations, uppercase_classes)

    preprocessed_true_filtered = [list(relation) for relation in true_relations]
    preprocessed_pred_filtered = [list(relation) for relation in pred_relations]

    #mlb_filtered = MultiLabelBinarizer(classes=uppercase_classes)
    mlb_filtered = MultiLabelBinarizer()
    mlb_filtered.fit(preprocessed_true_filtered + preprocessed_pred_filtered)
    LOG.debug(f"classes: {mlb_filtered.classes_}")

    binary_true_filtered = mlb_filtered.transform(preprocessed_true_filtered)
    binary_pred_filtered = mlb_filtered.transform(preprocessed_pred_filtered)

    if binary_true_filtered.shape[0] != binary_pred_filtered.shape[0]:
        min_length = min(binary_true_filtered.shape[0], binary_pred_filtered.shape[0])
        binary_true = binary_true_filtered[:min_length]
        binary_pred = binary_pred_filtered[:min_length]

    return {
        'true_encoded': binary_true,
        'pred_encoded': binary_pred,
        'mlb': mlb_filtered,
    }
