import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin


class RelationExtractor(BaseEstimator, ClassifierMixin):
    NONEXISTINGRELATION = "nonexisting_relation"
    KEY = "y"

    def __init__(self, pipeline, output_dir, model_name, id_col):
        self.pipeline = pipeline
        self.output_dir = output_dir
        self.model_name = model_name
        self.id_col = id_col

    def fit(self, X, y):
        """
        fits the model

        Parameters
        ----------

        X: list of lists of Feature objects
        y: list of lists of (subj, relation_class_label, obj)
        """
        X_features = []
        y_for_classification = []
        for list_of_features, list_of_annotations in zip(X["y"], y["y"]):
            dict_of_annotations = {(subj, obj): label for subj, _, label, obj, _ in list_of_annotations}
            for feature in list_of_features:
                label = dict_of_annotations.get((feature.subj.text, feature.obj.text), self.NONEXISTINGRELATION)
                y_for_classification.append(label)
                X_features.append(feature)

        self.pipeline.fit(X_features, y_for_classification)
        return self

    def predict(self, X):
        """
        predicts the models' output for a list of sentences

        Parameters
        ----------

        X: list of lists of Feature objects
        """
        trans = X[self.KEY].map(self.predict_single)
        return pd.DataFrame({self.id_col: X[self.id_col], "y": trans})

    def predict_single(self, x):
        """
        predicts the models' output for a single sentence

        Parameters
        ----------

        X: list of Feature objects
        """
        if len(x) == 0:
            return []

        list_of_predicted_relations = self.pipeline.predict(x)
        prediction = []
        for feature, rel in zip(x, list_of_predicted_relations):
            if rel != self.NONEXISTINGRELATION:
                prediction.append((feature.subj.text, feature.subj.label_, rel, feature.obj.text, feature.obj.label_))

        return prediction
