import pandas as pd
def get_text(design, ent_list):
    result = []
    for i in ent_list:
        result.append(design[i[0]:i[1]])
    return result

def setLabelContentWithAnnotation(dt_table, labels):
    for index, row in dt_table.iterrows():
        for i in row.annotation_str:
            labels[i] = [0, 0, 0]
    return labels

def countAnnotations(true, labels):
    for index, row in true.iterrows():
        annot = row.annotation_str
        pred = row.prediction_str

        for i in annot:
            labels[i][0] += 1
            if i in pred:
                labels[i][1] += 1

def countTotalAnnotations(X_train, labels):
    for index, row in X_train.iterrows():
        annot = row.annotation_str

        for i in annot:
            labels[i][2] += 1
def detemineLabelScore(columns, labels):
    label_scores = pd.DataFrame().from_dict(labels, orient="index").rename(columns=columns)
    label_scores["Accuracy"] = label_scores.apply(lambda row: row.Prediction / row.Annotation, axis=1)
    return label_scores

def getLabelScores(X_train, X_test):
    #prepare annotation str for label keys
    X_train["annotation_str"] = X_train.apply(lambda row: get_text(row.design_en, row.annotation), axis=1)
    X_test["annotation_str"] = X_test.apply(lambda row: get_text(row.design_en, row.annotation), axis=1)

    true_labels = setLabelContentWithAnnotation(X_test, {})
    labels = setLabelContentWithAnnotation(X_train, true_labels)
    countAnnotations(X_test, labels)
    countTotalAnnotations(X_train, labels)
    return detemineLabelScore(columns={0:"Annotation", 1:"Prediction", 2:"Total_in_train"})
