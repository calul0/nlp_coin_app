import streamlit as st
import pandas as pd
import ydata_profiling
from nlp_app_helper.helper import two_uploaded_files_to_df, x_uploaded_files_to_df
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from streamlit_agraph import agraph, Config, Node, Edge
from streamlit_pandas_profiling import st_profile_report
import ast
from nlp_app_helper.common import clean_df, merge_df, aggregate_design_descriptions


def compare_ground_truth(row) -> pd.DataFrame:
    first_ground_truth_set = set(row['first_ground_truth'])
    second_ground_truth_set = set(row['second_ground_truth'])

    diff_first_to_second = first_ground_truth_set - second_ground_truth_set
    diff_second_to_first = second_ground_truth_set - first_ground_truth_set
    return pd.Series(data={'diff_first_to_second': diff_first_to_second, 'diff_second_to_first': diff_second_to_first})


def merge_ground_truth(first_ground_truth: pd.DataFrame, second_ground_truth: pd.DataFrame) -> pd.DataFrame:
    cleaned_first_ground_truth = clean_df(df=first_ground_truth, column_name_for_y="first_ground_truth")
    cleaned_second_ground_truth = clean_df(df=second_ground_truth, column_name_for_y="second_ground_truth")
    merged_df = pd.merge(cleaned_first_ground_truth, cleaned_second_ground_truth, on='design_id', how='outer')
    merged_df.fillna(value='[]', inplace=True)
    merged_df.drop_duplicates(keep='first', inplace=True)
    return merged_df


def convert_string_to_list_of_tuples(s):
    return ast.literal_eval(s)


def compare_ground_truth_action(first_ground_truth: pd.DataFrame, second_ground_truth: pd.DataFrame) -> pd.DataFrame:
    st.subheader('Calculation of the difference between the two ground truth')

    final_df = merge_ground_truth(first_ground_truth, second_ground_truth)
    st.info('Data Merged and Cleansed')
    st.write(final_df)
    final_df['first_ground_truth'] = final_df['first_ground_truth'].apply(ast.literal_eval)
    final_df['second_ground_truth'] = final_df['second_ground_truth'].apply(ast.literal_eval)
    comparison = final_df.apply(compare_ground_truth, axis=1)
    final_df = pd.concat([final_df, comparison], axis=1)

    list_of_design_ids = [i for i in final_df['design_id']]
    aggregate_design_en = aggregate_design_descriptions(final_df, list_of_design_ids)
    final_df = pd.merge(final_df, aggregate_design_en, on='design_id', how='left')
    st.info('Result')
    st.write(f'Number of rows of merged and cleaned data: {len(final_df)}')
    return final_df


def build_knowledge_graph(ground_truth_df: pd.DataFrame, column_name, user_input):
    st.subheader('Graph Result')

    st.write('Node Input')
    user_input_node = user_input
    nodes = []
    edges = []
    counter = 0
    node_labels = dict()
    preprocess_ground_truth = clean_df(df=ground_truth_df, column_name_for_y=column_name)
    st.info('Data Cleansed')
    st.write(preprocess_ground_truth)
    preprocess_ground_truth[column_name] = preprocess_ground_truth[column_name].apply(
        convert_string_to_list_of_tuples
    )
    for _, row in preprocess_ground_truth.iterrows():
        counter += 1

        for relation_tuple in row[column_name]:

            for i in range(2):
                if user_input_node == relation_tuple[2]:
                    original_label = relation_tuple[i * 3]

                    if original_label in node_labels:
                        node_labels[original_label] += 1
                        unique_label = f"{original_label}_{node_labels[original_label]}"
                    else:
                        node_labels[original_label] = 0
                        unique_label = original_label

                        nodes.append(Node(id=unique_label,
                                          label=relation_tuple[i * 3],
                                          size=5,
                                          shape='box'))
                    edges.append(Edge(source=relation_tuple[3], label=relation_tuple[2],
                                      target=relation_tuple[0]))

    config = Config(width=2050,
                    height=1050,
                    directed=True,
                    physics={
                        "enabled": True,
                        "barnesHut": {
                            "gravitationalConstant": -8000,
                            "centralGravity": 0.3,
                            "springLength": 500,
                            "springConstant": 0.04,
                            "damping": 0.09,
                        },
                        "minVelocity": 0.75,
                    },
                    hierarchical={
                        "enabled": True,
                        "levelSeparation": 150,
                        "nodeSpacing": 100,
                        "treeSpacing": 200,
                        "direction": "UD",
                        "sortMethod": "hubsize",
                    },
                    clustering={
                        "enabled": True,
                        "initialClusters": 6,
                    }, )
    with st.expander("Knowledge Graph", expanded=True):
        return_value = agraph(nodes=nodes, edges=edges, config=config)
        st.write(return_value)

def read_json(json_file):
    df = pd.read_json(json_file)
    return st.write(df)


def old_ground_truth(gt_csv):
    df = pd.read_csv(gt_csv)
    df.sort_values(by='design_id', inplace=True)
    st.write(df)
    st.write(len(df))


def new_ground_truth(gt_json):
    # JSON-Daten direkt in einen DataFrame einlesen
    df = pd.read_json(gt_json)
    st.write(df)
    # Filtern der Daten, um nur die Tupel zu behalten, bei denen validity_pred == 1 ist
    df_filtered = df[df['validity_pred'] == 1]

    # Alle eindeutigen Einträge für jede design_id beibehalten
    unique_entries = df_filtered.drop_duplicates(
        subset=['design_id', 's', 'subject_class', 'p', 'o', 'object_class'], keep='first')

    # Umstrukturieren der Daten zu Tupeln
    result = unique_entries[['design_id', 's', 'subject_class', 'p', 'o', 'object_class']].copy()
    result['y'] = result.apply(lambda x: (x['s'], x['subject_class'], x['p'], x['o'], x['object_class']),
                               axis=1)

    # Gruppieren nach design_id und die Tupel als Listen zusamnlp_list_entities_v3menfassen
    grouped_result = result.groupby('design_id')['y'].apply(list).reset_index()
    grouped_result.sort_values(by='design_id', inplace=True)

    #grouped_result.to_csv("results/trainings_set/new_gt_group_2.csv", index=False)
    st.write(grouped_result)
    st.write(f"Len of New GT: {len(grouped_result)}")

def merge_multiple_df(list_of_df: list) -> pd.DataFrame:
    merged_df = pd.merge(list_of_df[0], list_of_df[1], on='design_id', how='right')
    merged_df.sort_values(by='design_id', inplace=True)
    return merged_df


def show_pandas_profiling_report(df):
    pd_profiling_report = df.profile_report()
    return st_profile_report(pd_profiling_report)


def show_ground_truth_comparison():
    st.title('Ground Truth Comparison')
    first_ground_truth, second_ground_truth = two_uploaded_files_to_df(first_file_name='first_ground_truth.csv',
                                                                       second_file_name='second_ground_truth.csv')

    first_gt_for_graph = first_ground_truth.copy()
    second_gt_for_graph = second_ground_truth.copy()
    if not first_ground_truth.empty and not second_ground_truth.empty:
        st.success('Files uploaded successfully!')
        st.info('Here are your uploaded files. You can now perform various actions on your data.')
        st.write(f'Number of rows first ground truth: {len(first_ground_truth)}')
        st.write(f'Here is the first Ground Truth:')
        st.write(first_ground_truth)
        st.write(f'Number of rows second ground truth: {len(second_ground_truth)}')
        st.write(f'Here is the second Ground Truth:')
        st.write(second_ground_truth)

        with st.form(key='compare_form'):
            submit_compare = st.form_submit_button(label='Compare Ground Truth')
            if submit_compare:
                comparison = compare_ground_truth_action(first_ground_truth, second_ground_truth)
                st.write(comparison)

        with st.form(key='knowledge_graph'):
            gt_graph_options = st.selectbox('Select Ground Truth', options=['first_ground_truth',
                                                                            'second_ground_truth'])
            selected_ground_truth = first_gt_for_graph if gt_graph_options == 'first_ground_truth' else second_gt_for_graph
            col_graph_options = selected_ground_truth.columns.tolist()
            col_option = st.selectbox('Select the column containing the option',
                                      options=col_graph_options)

            user_input_node = st.text_input(label='Type in the relation', value='')
            submit_knowledge = st.form_submit_button(label='Build Graph')
            if submit_knowledge:
                build_knowledge_graph(selected_ground_truth, col_option, user_input_node)


show_ground_truth_comparison()
#new_ground_truth(gt_json="results/trainings_set/RE_new_datachallenge.json")
#read_json(json_file="results/trainings_set/RE_compare_groundtruth_vs_datachallenge.json")
#old_ground_truth(gt_csv="results/trainings_set/nlp_relation_extraction_en_v2.csv")
