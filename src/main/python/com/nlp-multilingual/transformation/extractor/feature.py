from collections import namedtuple

from sklearn.base import TransformerMixin, BaseEstimator

from transformation.helper import path
from transformation.transformer.single_sentence import SingleSentenceTransformerMixin

Feature = namedtuple("Feature", ["subj", "path", "obj", "doc", "verbs"])


class FeatureExtractor(SingleSentenceTransformerMixin, TransformerMixin, BaseEstimator):
    KEY = "y"

    def __init__(self, model_dir, model_name, id_col, design_col):
        self.model_dir = model_dir
        self.model_name = model_name
        self.id_col = id_col
        self.design_col = design_col

    def fit(self, X, y):
        return self

    def transform_single_sentence(self, x):
        """
        transforms a sentence into a Feature object
        with sentence = spacy.doc, subj and obj = spacy.span

        Parameters
        -----------

        X: list of NER objects
        """
        extracted_paths = []
        for ner in x:
            p = path(ner.subj.root, ner.obj.root)
            verbs = self.extract_verbs_single_sentence(p)
            extracted_paths.append(Feature(ner.subj, p, ner.obj, ner.doc, verbs))

        return extracted_paths

    def extract_verbs_single_sentence(self, p):
        verbs = []
        for token in p:
            if token.pos_ == "VERB":
                verbs.append(token.text)
        return verbs



