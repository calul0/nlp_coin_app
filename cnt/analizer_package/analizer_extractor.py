class AnalizerExtractor:
    def __init__(self):
        self.predNotInTest = dict()
        self.testNotInPred = dict()
        self.notIdenticalDesigns= dict()
        self.notIdentifiedDesign = dict()
    def appendNotIdenticalDesign(self, designId, relation):
        if designId not in self.notIdenticalDesigns:
            self.notIdenticalDesigns[designId] = []
        self.notIdenticalDesigns[designId].append(relation)

    def appendTestNotInPred(self, designId, relation):
        if designId not in self.testNotInPred:
            self.testNotInPred[designId] = []
        self.testNotInPred[designId].append(relation)

    def appendPredNotInTest(self, designId, relation):
        if designId not in self.predNotInTest:
            self.predNotInTest[designId] = []
        self.predNotInTest[designId].append(relation)

    def appendNotIdentifiedDesign(self, designId, relation):
        if designId not in self.notIdentifiedDesign:
            self.notIdentifiedDesign[designId] = []
        self.notIdentifiedDesign[designId].append(relation)
    def getPredNotInTest(self):
        return self.predNotInTest

    def getNotIdenticalDesigns(self):
        return self.notIdenticalDesigns

    def getNotIdentifiedDesigns(self):
        return self.notIdentifiedDesign

    def call_method_by_name(self, method_name, *args, **kwargs):
        method = getattr(self, method_name, None)
        if method:
            method(*args, **kwargs)
        else:
            print("Methode nicht gefunden!")