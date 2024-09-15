from collections import namedtuple

from sklearn.base import TransformerMixin, BaseEstimator

from transformation.helper import make_my_estimator
from transformation.transformer.single_sentence import SingleSentenceTransformerMixin

NER = namedtuple("NER", ["doc", "subj", "obj"])


class NERTransformer(SingleSentenceTransformerMixin, TransformerMixin, BaseEstimator):
    KEY = "Design"

    def __init__(self, model_dir, model_name, id_col, design_col):
        self.model_dir = model_dir
        self.model_name = model_name
        self.id_col = id_col
        self.design_col = design_col
        self.KEY = self.design_col

        self.my_estimator = None

    def fit(self, X, y):
        """
        fits the model

        Parameters
        -----------

        X: list of designs
        y: list of lists of (subj, relation_class_label, obj)
        """
        self.my_estimator = make_my_estimator(self.model_dir, self.model_name, self.id_col, self.KEY)

        return self

    def transform_single_sentence(self, x):
        """
        transforms a sentence into a NER object
        with sentence = spacy.doc, subj and obj = spacy.span

        Parameters
        -----------

        x: string
        """
        doc = self.my_estimator.predict_single_sentence(x, as_doc=True)

        sent_subj_obj = []
        my_label_subj = ["PERSON", "OBJECT", "ANIMAL"]
        my_label_obj = ["PERSON", "OBJECT", "ANIMAL", "PLANT"]
        doc_list = list(doc.ents)
        for subj in doc_list:
            if subj.label_ in my_label_subj:
                for obj in doc_list:
                    if subj != obj:
                        if obj.label_ in my_label_obj:
                            sent_subj_obj.append(NER(doc, subj, obj))

        return sent_subj_obj
