import ast
import streamlit as st
import pandas as pd
import sklearn.pipeline
import time
from model.pipeline_functions import load_pipeline
from nlp_app_helper.helper import two_uploaded_files_to_df
from nlp_app_helper.common import clean_df, merge_df, aggregate_design_descriptions
from transformation.model import predict_re_single_sentence


def compare_prediction_and_ground_truth(row) -> pd.DataFrame:
    prediction_set = set(row['prediction'])
    ground_truth_set = set(row['ground_truth'])

    not_in_ground_truth_prediction = prediction_set - ground_truth_set
    missing_predictions = ground_truth_set - prediction_set
    return pd.Series(data={'not_in_ground_truth': not_in_ground_truth_prediction,
                           'missing_predictions': missing_predictions})


def merge_prediction_and_ground_truth(prediction_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> pd.DataFrame:
    cleaned_prediction_df = clean_df(prediction_df, column_name_for_y='prediction')
    cleaned_ground_truth_df = clean_df(ground_truth_df, column_name_for_y='ground_truth')
    merged_df = merge_df(first_df=cleaned_prediction_df, second_df=cleaned_ground_truth_df,
                         column_name_second_df='ground_truth')
    return merged_df


def predict_single_description():
    st.subheader('Single Prediction')
    st.write("""With this feature, you can generate a prediction for your coin description. 
                Just insert the description in the field and click enter.""")
    model = load_pipeline(model_dir="results/trained_model/re/", model_name="english_cno")
    id_col = "design_id"
    design_col = "design_en"
    user_input_text = st.text_input(label='Type the description to get the prediction.', value="")
    prediction = predict_re_single_sentence(model=model, sentence=user_input_text, id_col=id_col, design_col=design_col)
    return st.write(prediction)


def predict(X_test, clean: bool):
    with st.form(key='prediction_for_X_test'):
        st.subheader('Prediction for Test Data')
        st.write("""This feature allows you to generate predictions for test data. 
                    Simply click the button below.""")
        submit_prediction_test = st.form_submit_button(label='Prediction for test data')
        if submit_prediction_test:
            df = pd.read_csv(X_test)
            if clean:
                df.drop(columns=['Unnamed: 0'], inplace=True)
                df.sort_values(by='design_id', ascending=True, inplace=True)
            else:
                st.write('Your X_test data is correctly formatted with the required columns: design_id and y')

            with st.spinner('Loading predictions...'):
                time.sleep(5)
                model = load_pipeline(model_dir="results/trained_model/re/", model_name="english_cno")
                pred = model.predict(df)
            return st.write(pred)


def show_ground_truth_prediction_comparison():
    st.title('Prediction - Ground Truth Comparison')
    prediction, ground_truth = two_uploaded_files_to_df(first_file_name='y_pred.csv', second_file_name='y_test.csv')

    if not prediction.empty and not ground_truth.empty:
        st.success('Files uploaded successfully!')
        st.info('Here are your uploaded files. You can now perform various actions on your data. ')
        st.write('Here is the data you uploaded for prediction:')
        st.write(prediction)
        st.write('Here is the data you uploaded for ground truth:')
        st.write(ground_truth)

        with st.form(key='prediction_ground_truth_comparison'):
            submit_comparison_pred_gt = st.form_submit_button(label='Compare Ground Truth and Prediction')
            if submit_comparison_pred_gt:
                st.subheader('Calculation of the difference between prediction and ground truth')
                st.info('Now you can compare your uploaded prediction data against the uploaded ground truth data.')
                final_df = merge_prediction_and_ground_truth(prediction_df=prediction, ground_truth_df=ground_truth)

                final_df['prediction'] = final_df['prediction'].apply(ast.literal_eval)
                final_df['ground_truth'] = final_df['ground_truth'].apply(ast.literal_eval)
                comparison = final_df.apply(compare_prediction_and_ground_truth, axis=1)
                final_df = pd.concat([final_df, comparison], axis=1)

                list_of_design_ids = [i for i in final_df['design_id']]
                aggregate_design_en = aggregate_design_descriptions(final_df, list_of_design_ids)
                final_df = pd.merge(final_df, aggregate_design_en, on='design_id', how='left')
                st.write(final_df)


show_ground_truth_prediction_comparison()
predict_single_description()
predict(X_test="results/trainings_set/data_for_testing.csv", clean=True)
