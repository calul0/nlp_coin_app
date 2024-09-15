from nlp_app_helper.gui_elements import get_gui_select_box_comparison
from nlp_app_helper.helper import x_uploaded_files_to_df
from nlp_app_helper.streamlit_table import *
from nlp_app_helper.styles.styles_markdown import *
from nlp_app_helper.word_analyser_2 import analyze_word_frequency
from nlp_app_helper.word_metrics_analyser import *


def get_analyse_options():
    return ['Relation', 'Word']


def render_checkbox_with_analyse_option():
    st.title("Analyse Tool")
    # Layout mit zwei Spalten
    col1, col2 = st.columns([1, 2])

    # Text in der ersten Spalte
    with col1:
        st.write("choose your analyse option:")

    # Selectbox in der zweiten Spalte
    with col2:
        analyse_option = st.selectbox('', get_analyse_options())

    return analyse_option

def render_calculated_styled_diff_acc_df(df, left_column, right_column, showCalc = False):
    df['Diff'] = df[left_column] - df[right_column]
    df['Acc'] = (df[left_column] / df[right_column]) * 1

    if showCalc:
        st.write(df)

    return (df.style
            .applymap(highlight_accuracy, subset=['Acc'])
            .applymap(highlight_difference, subset=['Diff'])
            .format(precision=1))
def show_detailed_relation_frame(df):
    # Gruppierung nach Design_id und Berechnung der Summe
    #df = df.drop('words', axis=1)
    #df = df.drop('relation_key', axis=1)

    # Selectboxen zur Auswahl der zu vergleichenden Spalten mit Pfeil
    # Berechnungen durchführen
    left_column, right_column = get_gui_select_box_comparison(df.columns[2:],df.columns[2:])

    # summarized table preprocessing:
    grouped_df = df.groupby('relation').agg({
        'design_id': lambda x: ', '.join(map(str, x)),
        left_column: 'sum',
        right_column: 'sum'
    }).reset_index()

    # Berechnungen durchführen
    styled_df = render_calculated_styled_diff_acc_df(df, left_column, right_column, showCalc=True)
    styled_grouped_df = render_calculated_styled_diff_acc_df(grouped_df, left_column, right_column)

    # Anzeige der Ergebnisse
    st.subheader("Total results")
    st.dataframe(styled_grouped_df)

    st.subheader("result per design id:")
    st.dataframe(styled_df)

def show_detailed_word_frames(df):
    #st.write(df)
    word_df = analyze_word_frequency(df)
    st.subheader("Total Word Count:")
    # Selectboxen zur Auswahl der zu vergleichenden Spalten mit Pfeil
    # Berechnungen durchführen
    left_column, right_column = get_gui_select_box_comparison(word_df.columns[2:], word_df.columns[2:])
    styled_df = render_calculated_styled_diff_acc_df(word_df, left_column, right_column, showCalc=True)
    st.write(styled_df)

def show_word_metrics():
    st.title('Word Metrics')
    list_of_dfs, list_of_names = x_uploaded_files_to_df()

    if len(list_of_names) > 1:
        st.write('Files uploaded successfully!')
        # prepare analyse title
        analyse_option = render_checkbox_with_analyse_option()
        # Auswahl anzeigen
        st.write(f'You selected: {analyse_option}')
        combined_df = merge_dataframes(list_of_dfs, list_of_names)

        relation_count_df = calculate_relations(combined_df)
        if analyse_option == 'Relation':
            show_detailed_relation_frame(relation_count_df)
        elif analyse_option == 'Word':
            show_detailed_word_frames(relation_count_df)
        else:
            pass

        st.markdown(
            """
            <div style="border:1px solid #ddd; padding: 10px; border-radius: 5px;">
                <h3>Legende</h3>
                <ul style="list-style-type:none;">
                    <li style="margin: 5px 0;">
                        <span style="background-color: red; color: white; padding: 5px; border-radius: 3px;">Linker Vergleich hat weniger Elemente als Rechter</span>
                    </li>
                    <li style="margin: 5px 0;">
                        <span style="background-color: green; color: white; padding: 5px; border-radius: 3px;">Linker Vergleich hat genausoviele Elemente</span>
                    </li>
                    <li style="margin: 5px 0;">
                        <span style="background-color: yellow; color: black; padding: 5px; border-radius: 3px;">Linker Vergleich hat einige Elemente</span>
                    </li>
                    <li style="margin: 5px 0;">
                        <span style="background-color: blue; color: white; padding: 5px; border-radius: 3px;">Linker Vergleich hat mehr Elemente</span>
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )


show_word_metrics()
