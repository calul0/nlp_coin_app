import unittest
import pandas as pd
from cnt.analyze_relation_extraction import RelationExtractionAnalizer
from transformation.extractor import relation


class TestRelationExtractionAnalizer(unittest.TestCase):

    def setUp(self):
        self.re = RelationExtractionAnalizer(pd.DataFrame(), pd.DataFrame())

    def test_create_relation_key(self):
        desing_id = 20
        relation = ['Athena', 'PERSON', 'wearing', 'helmet', 'OBJECT']
        expected_result = "20#Athena#PERSON#wearing#VERB#helmet#OBJECT"

        result = self.re.createRelationKey(desing_id, relation)
        self.assertEqual(result,expected_result)

    def test_count_elem_dict(self):
        # TEST 1:
        expected_result = {"Das": 2, "ist": 3, "ein": 2, "erfolgreicher": 1, "Test": 2, "springt": 1, "variiert": 1}
        dict = { "Das": 2, "ist": 2, "ein": 2, "erfolgreicher": 1, "Test": 2}
        elems = ["ist", "variiert", "springt"]
        result = {}

        for elem in elems:
            result = self.re.countElemInDict(dict, elem)

        self.assertEqual(expected_result, result)

    def test_count_word_in_relation(self):
        # TEST 1:
        expected_result = {"Athena": 2, "PERSON": 2, "VERB": 2, "OBJECT": 2,
                           "holding": 1, "helmet": 1, "wearing": 1, "garmet": 1}
        relations = [("Athena", "PERSON", "holding", "helmet", "OBJECT"),
                     ("Athena", "PERSON", "wearing", "garmet", "OBJECT")]
        result = {}

        for relation in relations:
            result = self.re.countWordsOfARelation(result, relation)

        self.assertEqual(expected_result, result)
    def test_combine_dataframes(self):
        expected_result = pd.DataFrame({
            'design_id': [1, 2, 3, 4],
            'relation': [
                [(1, 'a', 2, 'b', 3), (10, 'g', 11, 'h', 12)],
                [(4, 'c', 5, 'd', 6)],
                [(7, 'e', 8, 'f', 9)],
                [(13, 'i', 14, 'j', 15)]
            ]
        })

        result = self.re.combine_dataframes(self.df1, self.df2)

        # Konvertiere die Spalte 'relation' zu einer sortierten Liste von Tupeln, um die Vergleichbarkeit zu gewährleisten
        result['relation'] = result['relation'].apply(lambda lst: sorted(lst))
        expected_result['relation'] = expected_result['relation'].apply(lambda lst: sorted(lst))

        pd.testing.assert_frame_equal(result, expected_result)


if __name__ == '__main__':
    unittest.main()
