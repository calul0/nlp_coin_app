from typing import Union

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from skmultilearn.model_selection import iterative_train_test_split

from dto.re_training_mapping import RETrainingMappingDTO


def default_train_test_split(matrix: pd.DataFrame) -> RETrainingMappingDTO:
    X_train, X_test, y_train, y_test = train_test_split(
        matrix[["design_id", "design_en"]],
        matrix[["design_id", "y"]],
        test_size=0.25,
        random_state=33
    )
    X_train.to_csv(f"../../results/trainings_set/data_for_training.csv")
    X_test.to_csv(f"../../results/trainings_set/data_for_testing.csv")

    return RETrainingMappingDTO(
        x_train=X_train,
        x_test=X_test,
        y_train=y_train,
        y_test=y_test
    )


def enhance_imbalanced_test_split(annotations: Union[list, str],
                                  matrix: pd.DataFrame,
                                  test_size: float = 0.25) -> RETrainingMappingDTO:
    """
    This function should use techniques, to reduce the imbalanced noise of test data. Due to the heavy majority of
    dedicated labels, others are in minority. Since This is a Multi-class Labeling problem, we would need to work out
    different solutions, to reduce or negate the noise.

    The TfidfVectorizer is used, to transform the textual descriptions into a vectorized format, while for the labels,
    we need a binary format.

    Due to issues with unique labels in this dataset, we can rarely use methods, such as SMOTE, MLSMOTE or something
    similiar, because they relly on a specific test suite. Hence, for current state, scikit-multilearn is used with the
    method of iterative_test_train_split, to try to reduce the imbalanced noise.

    TLDR: Since this is still in progress phase, it might not have the best effect.
    """

    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(annotations)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(matrix['design_en'])

    X_train, y_train, X_test, y_test = iterative_train_test_split(X, y, test_size=test_size)

    X_train_df = pd.DataFrame.sparse.from_spmatrix(X_train, columns=vectorizer.get_feature_names_out())
    X_test_df = pd.DataFrame.sparse.from_spmatrix(X_test, columns=vectorizer.get_feature_names_out())
    y_train_df = pd.DataFrame(y_train, columns=mlb.classes_)
    y_test_df = pd.DataFrame(y_test, columns=mlb.classes_)

    train_indices = np.where(np.isin(matrix.index, X_train_df.index))[0]
    test_indices = np.where(np.isin(matrix.index, X_test_df.index))[0]

    X_train_full = matrix.iloc[train_indices].reset_index(drop=True).join(X_train_df)
    X_test_full = matrix.iloc[test_indices].reset_index(drop=True).join(X_test_df)
    y_train_full = matrix.iloc[train_indices].reset_index(drop=True).join(y_train_df)
    y_test_full = matrix.iloc[test_indices].reset_index(drop=True).join(y_test_df)

    return RETrainingMappingDTO(
        x_test=X_test_full,
        y_test=y_test_full,
        x_train=X_train_full,
        y_train=y_train_full
    )
