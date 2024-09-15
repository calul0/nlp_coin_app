import pandas as pd


class SingleSentenceTransformerMixin:
    def transform(self, X):
        """
        transforms a list of sentences into NER objects
        with sentence = spacy.doc, subj and obj = spacy.span

        Parameters
        -----------

        X: list of strings

        Returns
        -------

        list of lists of NER objects
        """
        trans = X[self.KEY].map(self.transform_single_sentence)
        return pd.DataFrame({self.id_col: X[self.id_col], "y": trans})
