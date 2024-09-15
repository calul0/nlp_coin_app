import streamlit as st
import pandas as pd
from streamlit.runtime.uploaded_file_manager import UploadedFile


def clean_df(df: pd.DataFrame, column_name_for_y: str) -> pd.DataFrame:
    """

    Args:
        df: A dataframe with columns: Unnamed: 0, design_id, y
        column_name_for_y: Given the name of the column is y, we need to rename it.

    Returns: A clean dataframe. Rename y and delete the column Unnamed: 0

    """
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)
    df.rename(columns={'y': column_name_for_y}, inplace=True)
    df.sort_values(by='design_id', ascending=True, inplace=True)
    df.drop_duplicates(keep='first', inplace=True)
    return df


def merge_df(first_df: pd.DataFrame, second_df: pd.DataFrame, column_name_second_df: str) -> pd.DataFrame:
    """

    Args:
        first_df:
        second_df:

    Returns:

    """
    prepare = second_df.groupby(['design_id'])[column_name_second_df].agg(lambda x: ', '.join(x)).reset_index()
    merge_df = pd.merge(first_df, prepare, on='design_id', how='left')
    return merge_df


def get_design_description_for_given_designs(nlp_training_csv, id_list: list) -> pd.DataFrame:
    """

    Args:
        nlp_training_csv:
        id_list:

    Returns:

    """
    nlp_training_df = pd.read_csv(nlp_training_csv)
    filter = nlp_training_df[nlp_training_df['id'].isin(id_list)]
    return filter


def aggregate_design_descriptions(df: pd.DataFrame, list_ids: list) -> pd.DataFrame:
    design_descriptions = get_design_description_for_given_designs(
        nlp_training_csv="results/trainings_set/nlp_id_design_en.csv", id_list=list_ids)
    aggregate_design_en = design_descriptions.groupby(['id'])['design_en'].agg(
        lambda x: ', '.join(x)).reset_index()
    aggregate_design_en.rename(columns={'id': 'design_id'}, inplace=True)
    return aggregate_design_en


def drop_columns_nlp_training(csv_file):
    df = pd.read_csv(csv_file)
    df.drop(columns=['design_de'], inplace=True)
    df.drop(columns=['comment'], inplace=True)
    df.drop(columns=['design_en_changed'], inplace=True)
    new_csv_file = df.to_csv("../results/trainings_set/nlp_id_design_en.csv")
    return new_csv_file


def iterate_uploaded_files(file: UploadedFile) -> pd.DataFrame:
    df = pd.read_csv(file)
    st.dataframe(df)
    return df


def get_file_name(file: UploadedFile) -> str:
    return file.name




