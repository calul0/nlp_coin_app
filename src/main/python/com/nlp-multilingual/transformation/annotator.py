import re
import pandas as pd


def annotate_designs(entities, designs, id_col, design_col):
    """
    Given the entities, annotate a list of design.

    Parameters
    ----------

    entities: dict
        Dictionary whose keys are the labels and whose values
        are the corresponding lists of entities.

    design: list
        List of sentences.
    """

    annotated_designs = pd.DataFrame({
        design_col: designs[design_col],
        id_col: designs[id_col],
        "annotations": list(map(lambda x:
                                annotate_single_design(entities, x), designs[design_col]))})
    return annotated_designs


def annotate_single_design(entities, design):
    """
    Given the entities, annotate a concrete design.

    Parameters
    ----------

    entities: dict
        Dictionary whose keys are the labels and whose values
        are the corresponding lists of entities.

    design: str
        The input sentence.
    """
    annotations = []
    for label, entities in entities.items():
        annotations += annotate(design, label, entities)
    annotations = sorted(annotations, key=lambda x: x[0])
    # UM Problem [(0, 11, 'OBJECT'), (0, 4, 'PLANT')] übertraining auf teilworte
    annotations = find_max_entity(annotations)
    return annotations


def annotate(sentence, label, entities):
    """
    Given the entities, annotate a sentence with a label.

    Parameters
    ----------

    sentence: str
        The sentence to be annotated.

    label: str
        The label, e.g. "PERSON", "ANIMAL", ...

    entities: list
        List of entities belonging to the label.
        E.g. ["Aphrodite", "Apollo", ...]
    """
    regex = r'\b' + '(' + "|".join(entities) + ')' + r'\b'
    occurences = re.finditer(regex, sentence)
    annotation = [(match.start(), match.end(), label) for match in occurences]
    return annotation

def find_max_entity(my_list):
    """
    Builds a list of non overlapping entities
    :param my_list:
    :return:
    """
    if len(my_list) == 0:
        return []
    else:
        list_without_overlaps = []
        list_with_overlaps = []
        increment = None
        for i in range(0, len(my_list)):
            overlap = False
            start, end, entity = my_list[i]
            if increment and i < increment:
                continue
            for j in range(i, len(my_list)):
                if i == j:
                    continue
                jstart, jend, jentity = my_list[j]
                if (start >= jstart and start <= jend) or (end >= jstart and end <= jend):
                        overlap = True
                        list_with_overlaps.append((start, end, entity))
                        list_with_overlaps.append((jstart, jend, jentity))
                        increment = j+1
            if not overlap:
                list_without_overlaps.append((start, end, entity))
            else:
                list_without_overlaps.append(get_max_overlap(list_with_overlaps))
    return list_without_overlaps

def get_max_overlap(my_list):
    max_len = 0
    max_entity = None

    for i in my_list:
        temp_len = i[1] - i[0]

        if temp_len > max_len:
            max_len = temp_len
            max_entity = i

    return max_entity


def find_max_entity(my_list):
    """
    Builds a list of non overlapping entities
    :param my_list:
    :return:
    """
    if len(my_list) == 0:
        return []
    else:
        list_without_overlaps = []
        list_with_overlaps = []
        increment = None
        for i in range(0, len(my_list)):
            overlap = False
            start, end, entity = my_list[i]
            if increment and i < increment:
                continue
            for j in range(i, len(my_list)):
                if i == j:
                    continue
                jstart, jend, jentity = my_list[j]
                if (start >= jstart and start <= jend) or (end >= jstart and end <= jend):
                        overlap = True
                        list_with_overlaps.append((start, end, entity))
                        list_with_overlaps.append((jstart, jend, jentity))
                        increment = j+1
            if not overlap:
                list_without_overlaps.append((start, end, entity))
            else:
                list_without_overlaps.append(get_max_overlap(list_with_overlaps))
    return list_without_overlaps

def map_find_max_entity(my_list):
    return tuple(map(find_max_entity, my_list))