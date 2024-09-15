import pandas as pd
import streamlit

from nlp_app_helper.streamlit_table import *
import streamlit as st
import pandas as pd


def load_csv_file(csv_file):
    data = pd.read_csv(csv_file)
    return data


def analyses():
    miss_table = load_csv_file(f"results/trainings_set/miss_table.csv")
    true_table = load_csv_file(f"results/trainings_set/true_table.csv")
    empty_table = load_csv_file(f"results/trainings_set/empty_table.csv")
    st.write("Missed Predictions")
    st.dataframe(miss_table)
    st.write('Empty Table')
    st.dataframe(empty_table)
    st.write('True table')
    st.dataframe(true_table)


def show_metrics():
    metrics_table = pd.read_csv(f"results/trainings_set/metrics_with_cat.csv")
    st.title('Metrics')
    show_multi_func_table(metrics_table, ['category'], options=True)
    #streamlit.table(metrics_table)
    #streamlit.dataframe(metrics_table)


show_metrics()
analyses()