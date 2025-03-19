import copy
import spacy
import re

from Orange.data import StringVariable, DiscreteVariable, Domain, Table

pos_tags = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
            "SCONJ", "SYM", "VERB", "X", "REF"]


def create_lemmes_and_tags(table, model_path, request=False, progress_callback=None, argself=None):
    if request:
        out_data = create_lemmes_and_tags_on_request(table, model_path)
    else:
        out_data = create_lemmes_and_tags_on_text(table, model_path, progress_callback, argself)
    return out_data


def create_lemmes_and_tags_on_text(table, model_path, progress_callback=None, argself=None):
    """
    Add lemmes and tags columns to an input Data Table.

    Parameters:
    table (Table): The input Table to process.
    model_path (str): The path to the NLP model.

    Returns:
    out_data (Table): Copy of the input Table with 2 additional columns - lemmes and tags
    """
    # Copy of input data
    data = copy.deepcopy(table)
    attr_dom = list(data.domain.attributes)
    metas_dom = list(data.domain.metas)
    class_dom = list(data.domain.class_vars)
    # Load the model
    model = spacy.load(model_path)
    # Generate lemmes & tags on column named "content"
    rows = []
    for i, row in enumerate(data):
        features = list(data[i])
        metas = list(data.metas[i])
        lemmes, tags = lemmatize(str(row["content"]), model)
        lemmes = [" ".join(lemmes)]
        tags = [" ".join(tags)]
        metas += lemmes
        metas += tags
        rows.append(features + metas)
        if progress_callback is not None:
            progress_value = float(100 * (i + 1) / len(data))
            progress_callback(progress_value)
        if argself is not None:
            if argself.stop:
                break
    # Generate new Domain to add to data
    var_lemmes = StringVariable(name="Lemmes")
    var_tags = StringVariable(name="Tags")
    domain = Domain(attributes=attr_dom, metas=metas_dom + [var_lemmes, var_tags], class_vars=class_dom)
    # Create and return table
    out_data = Table.from_list(domain=domain, rows=rows)
    return out_data


def create_lemmes_and_tags_on_request(table, model_path):
    # Assume the input Table contains only one row for the request
    request = table[0]["content"].value
    # Load the model
    model = spacy.load(model_path)
    # Generate lemmes & tags
    lemmes, tags = lemmatize(request, model)
    # Rearrange lemmes and tags to fit in a Table
    rows = [[tags[i], lemmes[i]] for i in range(len(lemmes))]
    # Create domain
    var_lemmes = StringVariable(name="Lemmes")
    var_tags = DiscreteVariable(name="Tags", values=pos_tags)
    domain = Domain(attributes=[var_tags], metas=[var_lemmes])
    # Create and return Table
    out_data = Table.from_list(domain=domain, rows=rows)
    return out_data


def lemmatize(text, model):
    """
    Computes the lemmes & tags of a text thanks to a Spacy model.

    Parameters:
    text (str): The text to process.
    model (Spacy model): The model to use for processing.

    Returns:
    2 lists: the lemmes and the tags of each word.
    """
    lemmes = []
    tags = []
    reference_pattern = r'(?=.*[A-Za-z])(?=.*\d)\w+'
    document = model(text)
    for token in document:
        if re.match(reference_pattern, token.text):
            tags.append("REF")
            lemmes.append(token.text)
        else:
            lemmes.append(token.lemma_)
            if token.tag_ not in pos_tags:
                tags.append("X")
            else:
                tags.append(token.tag_)
    return lemmes, tags

