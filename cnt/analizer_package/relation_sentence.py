class RelationSentence:

    def __init__(self, ne1, alpha, ne2):
        self.n1_label = ne1[1]
        self.ne2_label = ne2[1]
        self.n1=ne1[0]
        self.n2=ne2[0]
        self.alpha=alpha

    def hasSameRelation(self, relationSentence):
        return (self.n1_label == relationSentence.n1_label
                and self.ne2_label == relationSentence.ne2_label
                and self.n1 == relationSentence.n1
                and self.n2 == relationSentence.n2)

    def sameLabel(self, relationSentence):
        return (self.n1_label == relationSentence.n1_label
                and self.ne2_label == relationSentence.ne2_label)

    def toTupel(self):
        return (self.n1, self.n1_label, self.alpha, self.n2, self.ne2_label)
