import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple
from nlp_app_helper.common import get_file_name


def file_uploader() -> List[Dict]:
    upload_data = st.file_uploader(label="Choose CSV files", type="csv", accept_multiple_files=True)
    list_of_df = list()
    if upload_data is not None:
        try:
            for file in upload_data:
                current_df = pd.read_csv(file)
                file_name = get_file_name(file=file)
                dict_of_df = {
                    'file_name': file_name,
                    'df_content': current_df
                }
                list_of_df.append(dict_of_df)
            return list_of_df
        except Exception as e:
            st.error(f"Something went wrong. Please try again: {e}")


def two_uploaded_files_to_df(first_file_name: str, second_file_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    list_of_uploaded_files = file_uploader()
    first_ground_truth = pd.DataFrame()
    second_ground_truth = pd.DataFrame()
    if list_of_uploaded_files is not None:
        for df_dict in list_of_uploaded_files:
            if df_dict['file_name'] == first_file_name:
                first_ground_truth = df_dict['df_content']
            if df_dict['file_name'] == second_file_name:
                second_ground_truth = df_dict['df_content']
    return first_ground_truth, second_ground_truth


def x_uploaded_files_to_df() -> Tuple[List[pd.DataFrame], List[str]]:
    list_of_uploaded_files = file_uploader()  # Diese Funktion sollte definiert sein, um Dateien hochzuladen
    dataframes = []
    filenames = []

    if list_of_uploaded_files is not None:
        for df_dict in list_of_uploaded_files:
            dataframes.append(df_dict['df_content'])
            filenames.append(df_dict['file_name'].replace('.csv', ''))

    return dataframes, filenames

