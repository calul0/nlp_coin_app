import pandas as pd
import ast

def drop_unnamed_columns(df):
    if 'Unnamed: 0' in df:
        df.drop(columns=['Unnamed: 0'], inplace=True)


# Funktion, um die Summe der Wörter in einem Dictionary zu berechnen
def sum_words_in_df(df):
    # Alle Wörter und ihre Summen sammeln
    word_totals = {}
    column_total = {}

    # Spalten 'design_id' und 'relation' entfernen
    column_names = df.columns.tolist()
    column_names.remove('design_id')
    column_names.remove('relation')
    column_names.remove('relation_key')
    column_names.remove('words')
    for index, row in df.iterrows():
        word_dict = row['words']
        for word, count in word_dict.items():
            # Wörter summieren
            word_totals[word] = word_totals[word] + count if word in word_totals else count

            # Summen für jede Spalte
            for col in column_names:
                count_elem = row[col]
                if col in column_total and col != "words":
                    inner_dict = column_total[col]
                    inner_dict[word] = inner_dict[word] + count_elem * count if word in inner_dict else count_elem * count
                else:
                    inner_dict = dict()
                    inner_dict[word] = count_elem * count
                    column_total[col] = inner_dict

    # In ein neues DataFrame umwandeln
    return generate_word_df_from_data(word_totals, column_total)



def generate_word_df_from_data(total_words_dict, col_with_total_words_dict):
    # prepare result with columns
    columns = ["Word", "Total"] + list(col_with_total_words_dict.keys())
    new_df = pd.DataFrame(columns=columns)
    total_word_df = pd.DataFrame(list(total_words_dict.items()), columns=['word', 'total'])

    # iterate over all words
    for idx, word_row in total_word_df.iterrows():
        result_row_dict = dict()
        word = word_row['word']
        result_row_dict["Word"] = word
        result_row_dict["Total"] = word_row['total']
        for col in col_with_total_words_dict:
            word_dict = col_with_total_words_dict[col]
            result_row_dict[col] = word_dict[word] if word in word_dict else 0
        new_df = pd.concat([new_df,
                            pd.DataFrame([result_row_dict])], ignore_index=True)
    return new_df


def merge_dataframes(list_of_dfs, list_of_columns_name):
    # Initialisiere combine_df mit dem ersten DataFrame in der Liste
    combine_df = list_of_dfs[0]
    drop_unnamed_columns(combine_df)

    # Iteriere über die restlichen DataFrames und füge sie zusammen
    for df_value in list_of_dfs[1:]:
        drop_unnamed_columns(df_value)
        combine_df = pd.merge(combine_df, df_value, on='design_id', how='outer')

    # Entferne doppelte design_id Einträge und behalte die erste Zeile
    combine_df = combine_df.drop_duplicates(subset=['design_id'], keep='first').reset_index(drop=True)

    # Benennen der Spalten
    new_list_col = ['design_id'] + list_of_columns_name
    combine_df.columns = new_list_col

    return combine_df

def get_str_val(val):
    if val is None:
        return ""
    return val

def createRelationKey(design_id, relation):
    subject, subject_label, predicate, object, object_label = relation
    return ("{}".format(design_id)
            + "#"
            + get_str_val(subject)
            + "#"
            + get_str_val(subject_label)
            + "#"
            + get_str_val(predicate)
            + "#"
            + "VERB"
            + "#"
            + get_str_val(object)
            + "#"
            + get_str_val(object_label))

def update_word_counts(dict, relation):
    for word in relation:
        dict[word] =  dict[word] + 1 if word in dict else 1
    return dict

def count_relations(df):
    relation_dict = dict()
    for index, row in df.iterrows():
        design_id = row['design_id']
        relation = row['relation']
        column = row['column']

        relation_key = createRelationKey(design_id, relation)
        if relation_key not in relation_dict:
            column_dict = dict()
            column_dict['design_id'] = design_id
            column_dict['relation'] = relation
            column_dict[column] = 1
            column_dict['words'] = update_word_counts(dict(), relation)
            relation_dict[relation_key] = column_dict
        else:
            column_dict = relation_dict[relation_key]
            column_dict['design_id'] = design_id
            column_dict['relation'] = relation
            column_dict[column] = column_dict[column] + 1 if column in column_dict else 1
            column_dict["words"] = update_word_counts(column_dict["words"], relation)
            relation_dict[relation_key] = column_dict
    return relation_dict

def get_data_frame_from_relation_count(relation_dict):
    # Umwandlung in DataFrame
    df = pd.DataFrame.from_dict(relation_dict, orient='index')

    # Hinzufügen einer Spalte für den relationkey
    df['relation_key'] = df.index

    # Resetting index to get a clean numerical index
    df.reset_index(drop=True, inplace=True)

    # Gewünschte Reihenfolge der Spalten
    columns = [col for col in df.columns if col not in ['words', 'relation_key']] + ['words', 'relation_key']
    df = df[columns]

    return df

def calculate_relations(df):
    # Liste zur Speicherung der Tupel
    df.fillna(value='[]', inplace=True)
    relations = []
    # Iteriere über die Zeilen des DataFrames
    for idx, row in df.iterrows():
        design_id = row['design_id']
        # Iteriere über die Spalten ab der zweiten Spalte und füge jede Relation einzeln hinzu
        for col in df.columns[1:]:
            relations_from_col = ast.literal_eval(row[col]) if '[]' not in row[col] else []
            for relation in relations_from_col:
                relations.append({'design_id': design_id, 'relation': relation, 'column': col})

    # DataFrame aus den gesammelten Tupeln erstellen
    relations_df = pd.DataFrame(relations)

    # Gruppieren nach 'design_id', 'relation', und 'column' dann die Größe zählen und neu indexieren
    relation_counts = relations_df.groupby(['design_id', 'relation', 'column']).size().reset_index(name='count')
    relations_counts2 = count_relations(relations_df)
    relations_count_df = get_data_frame_from_relation_count(relations_counts2)
    relations_count_df.fillna(0, inplace=True)

    # Pivotieren, um die Spalten darzustellen
    relation_pivot = relation_counts.pivot_table(index=['design_id', 'relation'], columns='column', values='count',
                                                 fill_value=0).reset_index()

    # Spaltennamen anpassen
    relation_pivot.columns.name = None

    return  relation_pivot


