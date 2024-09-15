import ast

import streamlit as st
import pandas as pd
from annotated_text import annotated_text
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
import streamlit.components.v1 as components


def initSearchFields(list_of_column_names):
    # Session State für Suchfelder
    for column_name in list_of_column_names:
        session_state_name = 'search_' + column_name
        if session_state_name not in st.session_state:
            st.session_state[session_state_name] = ''

        # Suchfelder für jede Spalte hinzufügen
        st.text_input('Suche ' + column_name,
                      key='new_' + session_state_name,
                      on_change=update_search,
                      args=(session_state_name,)
                      )


def filterDataInFrameBySearch(df, col_name):
    st_session_state_name = 'search_' + col_name
    session_state = st.session_state[st_session_state_name]
    if session_state:
        df = df[df[col_name].astype(str).str.contains(session_state, case=False, na=False)]
    return df


def update_search(session_state_name):
    new_session_state_name = 'new_' + session_state_name
    st.session_state[session_state_name] = st.session_state[new_session_state_name]

def make_grid_initial(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filterable=True, sortable=True, editable=True)
    gb.configure_selection('single')
    grid_options = gb.build()
    grid_options["domLayout"] = "normal"

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filterable=True, sortable=True, editable=True)
    gb.configure_selection('single')  # Erlaube Einzelzeilenauswahl


    # CSS für die Badges
    custom_css = {
        ".badge": {
            "display": "inline-block",
            "padding": "0.25em 0.4em",
            "margin": "0.1em",
            "font-size": "75%",
            "font-weight": "700",
            "line-height": "1",
            "text-align": "center",
            "white-space": "nowrap",
            "vertical-align": "baseline",
            "border-radius": "0.25rem",
            "color": "#fff",
            "background-color": "#007bff"
        }
    }

    grid_options = gb.build()

    # Zeige die Tabelle an
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme='streamlit',
        # Gültige Themen: 'streamlit', 'light', 'dark', 'fresh', 'material'
        enable_enterprise_modules=True,
        height=350,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        custom_css=custom_css
    )

    return grid_response


def show_html_oriented_table(df):
    # Convert DataFrame to HTML table
    table_html = df.to_html(index=False)

    # JavaScript for selecting rows
    script = """
    <script>
    const rows = document.querySelectorAll("tr");
    rows.forEach(row => {
        row.addEventListener("click", () => {
            rows.forEach(r => r.style.backgroundColor = "");
            row.style.backgroundColor = "lightblue";
            const selectedRow = [...row.children].map(cell => cell.innerText);
            const selectedRowStr = JSON.stringify(selectedRow);
            document.getElementById("selectedRow").innerText = selectedRowStr;
        });
    });
    </script>
    """

    # Display HTML and JavaScript in Streamlit
    components.html(f"""
    <div>
        {table_html}
        <p id="selectedRow"></p>
        {script}
    </div>
    """, height=600)

    st.write("Ausgewählte Zeilen:")
    selected_rows_str = st.text_area("Ausgewählte Zeile", key="selectedRowStr", height=100)
    if selected_rows_str:
        selected_rows = eval(selected_rows_str)  # Konvertiere die Zeichenkette zurück in eine Liste
        selected_df = pd.DataFrame([selected_rows], columns=df.columns)
        st.table(selected_df)


def show_table_with_style(df):
    grid_response = make_grid_initial(df)

    selected_rows = grid_response['selected_rows']
    # Zeige die ausgewählten Zeilen an
    print(selected_rows)
    if not selected_rows.empty:
        st.write('Ausgewählte Zeilen:')
        selected_df = pd.DataFrame(selected_rows)
        st.dataframe(selected_df)


def annotate_content(df):
    count_col_idx = 0
    for index, row in df.iterrows():
        for col_name in df.columns:
            st.text(f"{col_name}:")
            if count_col_idx >= 1:
                relations = row[col_name]
                for relation in ast.literal_eval(relations):
                    st.write(relation)

            else:
                st.write(f"{row[col_name]}")
            count_col_idx = count_col_idx + 1

def show_table_with_style_annotation(df):
    grid_response = make_grid_initial(df)

    selected_rows = grid_response['selected_rows']
    # Zeige die ausgewählten Zeilen an
    print(selected_rows)
    if not selected_rows.empty:
        st.write('Ausgewählte Zeilen:')
        selected_df = pd.DataFrame(selected_rows)
        annotate_content(selected_df)
        st.dataframe(selected_df)


def show_multi_func_table(df, search_able_columns, options=False):
    initSearchFields(search_able_columns)

    # Filterfunktion für jede Spalte
    filtered_df = df.copy()
    for column in search_able_columns:
        filtered_df = filterDataInFrameBySearch(filtered_df, column)

    if options:
        # Konfiguriere die AgGrid-Tabelle
        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_default_column(editable=True, sortable=True, filter=True, resizable=True)
        gridOptions = gb.build()

        # Tabelle auf volle Breite setzen

        st.markdown("<style>div[data-testid='stHorizontalBlock'] div[role='grid'] {width: 100% !important;}</style>",
                    unsafe_allow_html=True)


        # AgGrid Tabelle anzeigen
        AgGrid(filtered_df,
               gridOptions=gridOptions,
               height=400,
               width='80%',
               fit_columns_on_grid_load=True
               )

    else:
        st.dataframe(filtered_df)
