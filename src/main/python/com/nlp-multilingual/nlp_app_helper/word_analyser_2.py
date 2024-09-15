import pandas as pd
import streamlit as st
from collections import Counter


def analyze_word_frequency(df):
    relation_columns = [col for col in df.columns if col != 'design_id' and col != 'relation']
    word_freq_per_design = []

    # calculate the words per design_id
    for design_id, group in df.groupby('design_id'):
        words = []
        for relation in group['relation']:
            words.extend(relation)  # Tupel in Wörter umwandeln und hinzufügen
        word_count = Counter(words)
        word_freq_per_design.append({'design_id': design_id, **word_count})

    # make lst to dataframe
    word_freq_df = pd.DataFrame(word_freq_per_design).fillna(0).astype(int)

    # calculate count of words
    total_word_count = Counter()
    for relation in df['relation']:
        total_word_count.update(relation)

    total_word_freq_df = pd.DataFrame(list(total_word_count.items()), columns=['Word', 'Total'])

    # Combine total word count with each column's word count
    combined_freq = total_word_freq_df.copy()

    for col in relation_columns:
        col_word_count = Counter()
        for _, row in df.iterrows():
            if row[col] == 1:
                col_word_count.update(row['relation'])
        col_word_freq_df = pd.DataFrame(list(col_word_count.items()), columns=['Word', col])

        # Merge with the combined DataFrame
        combined_freq = combined_freq.merge(col_word_freq_df, on='Word', how='outer').fillna(0)

    combined_freq = combined_freq.astype({col: int for col in combined_freq.columns if col != 'Word'})

    # Display results in Streamlit
    st.subheader("Kombinierte Wortfrequenzen")
    st.dataframe(combined_freq)
    return combined_freq

