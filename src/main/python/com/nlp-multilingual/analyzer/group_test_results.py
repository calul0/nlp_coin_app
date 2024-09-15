import ast

import pandas as pd

from configuration.en_ner import EnglishNERConfiguration
from configuration.en_re import EnglishREConfiguration
from database.connector import DatabaseConnector
from database.operations import load_entities_from_db, DatabaseOperations
from model.pipeline_functions import load_pipeline
from preprocess.roman_numeral import RomanNumeralPreprocess
from preprocess.split_train_test import default_train_test_split
from transformation.aggregation import aggregate_design_data
from utils.logging import get_logger
from ast import literal_eval

LOG = get_logger(__name__)


def clean_rows(csv_file, column_name: str) -> pd.DataFrame:
    df = pd.read_csv(csv_file)
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)
    df.rename(columns={"y": column_name}, inplace=True)
    df.sort_values(by=['design_id'], inplace=True)
    df.drop_duplicates(keep='first', inplace=True)
    return df


def merge_prediction_and_ground_truth(prediction_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> pd.DataFrame:
    prepare_to_merge = ground_truth_df.groupby(['design_id'])['ground_truth'].agg(lambda x: ', '.join(x)).reset_index()
    merged_df = pd.merge(prediction_df, prepare_to_merge, on='design_id', how='left')
    return merged_df

def divide_result(prediction_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> pd.DataFrame:
    combined_predictions_ground_truth = merge_prediction_and_ground_truth(prediction_df, ground_truth_df)
    empty_predictions = combined_predictions_ground_truth[(combined_predictions_ground_truth['prediction'] == '[]')]
    not_empty_predictions = combined_predictions_ground_truth[
        (combined_predictions_ground_truth['prediction'] != '[]')]
    true = not_empty_predictions.where(
        not_empty_predictions['ground_truth'] == not_empty_predictions['prediction']).dropna()
    miss = not_empty_predictions.where(
        not_empty_predictions['ground_truth'] != not_empty_predictions['prediction']).dropna()
    count_miss_true = len(miss) + len(true)

    if ((count_miss_true == len(not_empty_predictions)) and (
            (len(empty_predictions) + len(not_empty_predictions)) == len(combined_predictions_ground_truth))):
        LOG.info('The total number of lines matches')
        LOG.info('Number of empty lines: %d', len(empty_predictions))
        LOG.info('Number of missed lines: %d', len(miss))
        LOG.info('Number of true lines: %d', len(true))
    else:
        LOG.error('The total number of lines do not match')
        LOG.info('Number of empty lines: %d', len(empty_predictions))
        LOG.info('Number of missed lines: %d', len(miss))
        LOG.info('Number of true lines: %d', len(true))

    return empty_predictions, miss, true

def compare_prediction_ground_truth(row):
    prediction_set = set(row['prediction'])
    ground_truth_set = set(row['ground_truth'])

    false_predictions = prediction_set - ground_truth_set
    missing_predictions = ground_truth_set - prediction_set

    return pd.Series(data={'not_in_ground_truth_predictions': false_predictions, 'missing_predictions': missing_predictions})

def get_description_and_filter(database_ops: DatabaseOperations, id_list: list) -> pd.DataFrame:
    query = """SELECT id, design_en FROM nlp_training_designs"""
    result_query = database_ops.execute_custom_sql_query(query=query)
    filter = result_query[result_query['id'].isin(id_list)]
    return filter
def analyze_misses(y_pred: pd.DataFrame, y_test: pd.DataFrame, database_ops: DatabaseOperations) -> pd.DataFrame:
    _, miss, _ = divide_result(y_pred, y_test)

    missed_prediction_design_ids = [i for i in miss['design_id']]
    filter_missed_predictions = get_description_and_filter(database_ops, missed_prediction_design_ids)
    aggregate_design_en = filter_missed_predictions.groupby(['id'])['design_en'].agg(
        lambda x: ', '.join(x)).reset_index()
    aggregate_design_en.rename(columns={"id": 'design_id'}, inplace=True)
    misses_to_analyze = pd.merge(miss, aggregate_design_en, on='design_id', how='left')

    # compare the GT and prediction and filter false predictions and missing prediction
    misses_to_analyze['prediction'] = misses_to_analyze['prediction'].apply(ast.literal_eval)
    misses_to_analyze['ground_truth'] = misses_to_analyze['ground_truth'].apply(ast.literal_eval)

    comparison_result = misses_to_analyze.apply(compare_prediction_ground_truth, axis=1)
    misses_to_analyze = pd.concat([misses_to_analyze, comparison_result], axis=1)
    return misses_to_analyze

def analyze_empty(y_pred: pd.DataFrame, y_test: pd.DataFrame, database_ops: DatabaseOperations) -> pd.DataFrame:
    empty_predictions, _, _ = divide_result(y_pred, y_test)

    empty_predictions_design_ids = [i for i in empty_predictions['design_id']]
    filter_empty_predictions = get_description_and_filter(database_ops, empty_predictions_design_ids)
    aggregate_design_en = filter_empty_predictions.groupby(['id'])['design_en'].agg(
        lambda x: ', '.join(x)
    ).reset_index()

    aggregate_design_en.rename(columns={"id": 'design_id'}, inplace=True)
    empty_to_analyze = pd.merge(empty_predictions, aggregate_design_en, on='design_id', how='left')
    return empty_to_analyze

def filter_alternative_name(df: pd.DataFrame, word_list: list) -> pd.DataFrame:
    filtered_alternative_name = df[df['design_en'].str.contains('|'.join(word_list))]
    return filtered_alternative_name

def analyze_true(y_pred: pd.DataFrame, y_test: pd.DataFrame, database_ops: DatabaseOperations) -> pd.DataFrame:
    _, _, true = divide_result(y_pred, y_test)
    true_predictions_design_ids = [i for i in true['design_id']]
    filter_true_predictions = get_description_and_filter(database_ops, true_predictions_design_ids)
    aggregate_design_en = filter_true_predictions.groupby(['id'])['design_en'].agg(
        lambda x: ', '.join(x)
    ).reset_index()
    aggregate_design_en.rename(columns={"id": 'design_id'}, inplace=True)
    true_to_analyze = pd.merge(true, aggregate_design_en, on='design_id', how='left')
    return true_to_analyze

def main():
    en_ner_config = EnglishNERConfiguration()
    en_re_config = EnglishREConfiguration()

    with DatabaseConnector() as db:
        database_operations = DatabaseOperations(connector=db)

        #entities = database_operations.load_from_db(table_name="nlp_list_entities",
        #                                            column_list=en_re_config.add_columns)
        y_pred = clean_rows(f"../../results/trainings_set/y_pred.csv", "prediction")
        y_test = clean_rows(f"../../results/trainings_set/y_test.csv", "ground_truth")
        miss_table = analyze_misses(y_pred, y_test, database_operations)
        miss_table.to_csv("../../results/trainings_set/miss_table.csv")
        LOG.info('Created csv file for the missed predictions.')
        empty_table = analyze_empty(y_pred, y_test, database_operations)
        empty_table.to_csv("../../results/trainings_set/empty_table.csv")
        LOG.info('Created csv file for the empty predictions.')
        true_table = analyze_true(y_pred, y_test, database_operations)
        true_table.to_csv("../../results/trainings_set/true_table.csv")
        LOG.info('Created csv file for the true predictions.')

        # TODO: do this for all the relations. Get all alt names for each rel from db then call func.
        # TODO: What kind of metrics can we apply?
        # TODO: How can we visualize this better? Should we use Streamlit?
        holding_alt_names = ['ploughing',  'removing', 'covering',  'containing',  'brandishing',  'carrying',  'forming',
                             'raising',  'cradling',  'touching',  'drawing', 'supporting', 'hanging']

        holding_alt_name_in_empty = filter_alternative_name(empty_table, holding_alt_names)
        holding_in_empty = filter_alternative_name(empty_table, ['holding'])
        holding_alt_name_in_true = filter_alternative_name(true_table, holding_alt_names)
        holding_in_true = filter_alternative_name(true_table, ['holding'])
        holding_alt_name_in_miss = filter_alternative_name(miss_table, holding_alt_names)
        holding_in_miss = filter_alternative_name(miss_table, ['holding'])
        LOG.info(f"Number of missed predictions for alternative names to holding: {len(holding_alt_name_in_miss)}")
        LOG.info(f"Number of true predictions for alternative names to holding: {len(holding_alt_name_in_true)}")
        LOG.info(f"Number of empty predictions for alternative names to holding: {len(holding_alt_name_in_empty)}")
        LOG.info('_______Results for only holding______')
        LOG.info(f"Number of missed predictions for holding: {len(holding_in_miss)}")
        LOG.info(f"Number of true predictions for holding: {len(holding_in_true)}")
        LOG.info(f"Number of empty predictions for holding: {len(holding_in_empty)}")

        print('hi')

main()
