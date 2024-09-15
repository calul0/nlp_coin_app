import pandas as pd
import sklearn.pipeline
from sklearn.metrics import precision_recall_fscore_support

from dto.ner_training_mapping import NERTrainingMappingDTO
from dto.re_training_mapping import RETrainingMappingDTO
from evaluation.reports import EvaluationReports
from transformation.model import predict_re_single_sentence
from utils.logging import get_logger

LOG = get_logger(__name__)


def evaluate_model(model: sklearn.pipeline.Pipeline, training_data: RETrainingMappingDTO) -> None:
    """
    This function should take the already trained model, and compare it against test suites. So there will be a textual
    description, which needs to be verified against the model. Based on expected annotations, we will check, if the
    model actually correctly was trained or not.

    To have automation possible, we are fetching from y_test the true labels and afterward, match it against the
    predicted results.

    Args:
        model (sklearn.pipeline.Pipeline): the already trained model
        training_data (RETrainingMappingDTO): The test training dataset, mapped inside DTO

    Returns:
        None
    """

    results = list()
    for index, row in training_data.x_test.iterrows():
        sentence = row['design_en']
        design_id = row['design_id']

        true_label_row = training_data.y_test[training_data.y_test['design_id'] == design_id]
        expected = true_label_row['y'].values[0] if not true_label_row.empty else []

        predicted = predict_re_single_sentence(model, sentence, "design_id", "design_en")

        expected_entities = set(tuple(e) for e in expected)
        predicted_entities = set(tuple(p) for p in predicted)

        true_positives = expected_entities & predicted_entities
        false_positives = predicted_entities - expected_entities
        false_negatives = expected_entities - predicted_entities

        if len(expected_entities) > 0:
            y_true = [1] * len(true_positives) + [0] * len(false_positives) + [1] * len(false_negatives)
            y_pred = [1] * len(true_positives) + [1] * len(false_positives) + [0] * len(false_negatives)

            precision, recall, f1, _ = precision_recall_fscore_support(
                y_true,
                y_pred,
                average='binary',
                zero_division=0
            )
        else:
            precision, recall, f1 = 0.0, 0.0, 0.0

        results.append({
            "design_id": design_id,
            "sentence": sentence,
            "expected": expected,
            "predicted": list(predicted),
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        })

    evaluation_reports = EvaluationReports()
    evaluation_reports.generate_prediction_validation_csv_report(results)


# TODO: Probably need to check what kind of values needs to be passed accordingly
def get_text(design, ent_list):
    result = []
    for i in ent_list:
        result.append(design[i[0]:i[1]])
    return result


def verify_model_training(trained_data: NERTrainingMappingDTO) -> None:
    """
    Function to test the trained model.
    """
    LOG.info(f"Y_test Head 5: {trained_data.y_test.head(5)}")
    LOG.info(f"X_predict Head 5: {trained_data.x_predict.head(5)}")

    trained_data.x_test["annotation"] = trained_data.y_test["y"]
    trained_data.x_test["prediction"] = trained_data.x_predict["y"]
    LOG.info(f"Head 2 of x_test: {trained_data.x_test.head(2)}")

    trained_data.x_test["annotation_str"] = trained_data.x_test.apply(lambda row: get_text(row.design_en, row.annotation), axis=1)
    trained_data.x_test["prediction_str"] = trained_data.x_test.apply(lambda row: get_text(row.design_en, row.prediction), axis=1)

    LOG.info(f"Head 2 of x_test: {trained_data.x_test.head(2)}")
    trained_data.x_train["annotation"] = trained_data.y_train["annotations"]
    trained_data.x_train["annotation_str"] = trained_data.x_train.apply(lambda row: get_text(row.design_en, row.annotation), axis=1)

    labels = dict()
    for index, row in trained_data.x_test.iterrows():
        for i in row.annotation_str:
            labels[i] = [0, 0, 0]

    for index, row in trained_data.x_train.iterrows():
        for i in row.annotation_str:
            labels[i] = [0, 0, 0]

    for index, row in trained_data.x_test.iterrows():
        annot = row.annotation_str
        pred = row.prediction_str

        for i in annot:
            labels[i][0] += 1
            if i in pred:
                labels[i][1] += 1

    for index, row in trained_data.x_train.iterrows():
        annot = row.annotation_str

        for i in annot:
            labels[i][2] += 1

    label_scores = pd.DataFrame().from_dict(labels, orient="index").rename(columns={0: "Annotation",
                                                                                    1: "Prediction",
                                                                                    2: "Total_in_train"})
    label_scores["Accuracy"] = label_scores.apply(lambda row: row.Prediction/row.Annotation, axis=1)
    LOG.info(f"Label scores Alexander: {label_scores.loc[label_scores.index.str.contains('Alexander')]}")
    LOG.info(label_scores.sort_values("Accuracy").head(10))
