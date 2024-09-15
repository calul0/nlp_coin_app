from sklearn.base import TransformerMixin, BaseEstimator


class Path2Str(TransformerMixin, BaseEstimator):
    def __init__(self, pos=False, dep=False, ent=False):
        self.pos = pos
        self.dep = dep
        self.ent = ent

    def fit(self, X, y):
        return self

    def transform_single(self, x):
        #
        # Feature(subj=Herakles, path=[Herakles, Nackter, stehend, vorn], obj=vorn, doc=Nackter, bärtiger
        # Herakles, stehend von vorn, Kopf nach links, mit der rechten Hand sich auf die Keule stützend, mit dem linken Arm das
        # Löwenfell haltend.Bildleiste.Perlkreis., verbs = ['stehend'])
        #
        if self.ent and not self.dep and not self.pos:
            x_vect = " ".join(map(lambda t: t.text.replace(" ", "_") + "\\" + t.ent_type_, x.path))
        elif self.pos and not self.dep and not self.ent:
            x_vect = " ".join(map(lambda t: t.text.replace(" ", "_") + "\\" + t.pos_, x.path))
        elif self.dep and not self.pos and not self.ent:
            x_vect = " ".join(map(lambda t: t.text.replace(" ", "_") + "\\" + t.dep_, x.path))
        elif self.pos and self.dep and not self.ent:
            x_vect = " ".join(map(lambda t: t.text.replace(" ", "_") + "\\" + t.pos_ + "\\" + t.dep_, x.path))
        elif self.ent and self.pos and not self.dep:
            x_vect = " ".join(map(lambda t: t.text.replace(" ", "_") + "\\" + t.ent_type_ + "\\" + t.pos_, x.path))
        elif self.ent and self.dep and not self.pos:
            x_vect = " ".join(map(lambda t: t.text.replace(" ", "_") + "\\" + t.ent_type_ + "\\" + t.dep_, x.path))
        elif self.ent and self.dep and self.pos:
            x_vect = " ".join(
                map(lambda t: t.text.replace(" ", "_") + "\\" + t.ent_type_ + "\\" + t.pos_ + "\\" + t.dep_, x.path))
        else:
            x_vect = " ".join(map(str, x.path))

        return x_vect

    def transform(self, X):
        """
        builds a list of words as input for vectorization

        Parameters
        ----------

        X: list of Feature objects
        """
        return [self.transform_single(x) for x in X]
