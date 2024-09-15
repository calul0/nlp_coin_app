from transformation.nlp.annotate import nlp_annotate_designs


class StemLemmaAnnotatizer:

	def __init__(self, method="lemma_stem", language="en", backbone="spacy_snowball"):
		self.method = method
		self.language = language
		self.backbone = backbone

	def annotate(self, designs, entities, id_col, design_col):
		return nlp_annotate_designs(entities, designs, self.language, self.method, id_col, design_col)
