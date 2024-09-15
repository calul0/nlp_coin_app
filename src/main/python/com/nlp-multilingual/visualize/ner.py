import os
from pathlib import Path

from spacy import displacy

from utils.logging import get_logger

LOG = get_logger(__name__)


class VisualizeNER:
    """
    This is the base class for NER visualization. Abstracted part will do the rendering through spacy library.
    """

    def __init__(self):
        self.output_path = "../../results/reports/"

    def visualize(self, docs, output_file_name):
        LOG.info(f"Current path: {os.getcwd()}")
        colors = {'PERSON': 'mediumpurple', 'OBJECT': 'greenyellow', 'ANIMAL': 'orange', 'PLANT': 'salmom',
                  'VERBS': 'skyblue'}
        options = {'ent': ['PERSON', 'OBJECT', 'ANIMAL', 'PLANT'], 'colors': colors}

        html = displacy.render(docs, style='ent', page=True, options=options)

        with open(self.output_path + output_file_name, 'w') as file:
            file.write(html)
            LOG.info(f"Visualization saved to {self.output_path + output_file_name}")
