import streamlit as st

from nlp_app_helper.styles.styles_markdown import get_style_selct_box_comparison


def get_gui_select_box_comparison(df_columns_left, df_columns_right):
    # CSS für Gitlab-ähnliche Darstellung
    st.markdown(get_style_selct_box_comparison(), unsafe_allow_html=True)

    # Selectboxen zur Auswahl der zu vergleichenden Spalten mit Pfeil
    col1, col2, col3 = st.columns([1, 0.1, 1])

    with col1:
        left_column = st.selectbox("Select left column", df_columns_left, index=0)
    with col2:
        st.markdown("<div class='arrow_class'>➡️</div>", unsafe_allow_html=True)
    with col3:
        right_column = st.selectbox("Select right column", df_columns_right, index=1)

    return left_column, right_column
