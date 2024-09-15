from transformation.model import load_ner_model_v2


def make_my_estimator(model_directory, model_name, id_col, design_col):
    model = load_ner_model_v2(model_directory, model_name, id_col, design_col)
    return model


def path(subj, obj):
    """
    determines the least common ancestor of two nodes
    and prints the whole path between them

    Parameters
    -----------

    subj: token
        word in the sentence / node in the tree
        to start the path
    obj: token
        word in the sentence / node in the tree
        to end the path

    Returns
    -------

    list of spacy.Token
    """
    up_from_obj = []  # Amphora
    up_from_subj = []
    # adps = ["in","im","mit","auf"]
    current_token = obj  # Amphora, Apollo
    while True:
        up_from_obj.append(current_token)
        if current_token == current_token.head:
            break
        current_token = current_token.head

    up_from_obj = list(reversed(up_from_obj))

    current_token = subj
    while current_token not in up_from_obj and current_token != current_token.head:
        up_from_subj.append(current_token)
        current_token = current_token.head
    try:
        intersection = up_from_obj.index(current_token)
    except ValueError:  # current_token not in up_from_obj
        return []

    path = up_from_subj + up_from_obj[intersection:]
    return path