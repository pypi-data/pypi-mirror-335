import copy

import Orange
from Orange.data import Domain, Table, StringVariable, ContinuousVariable
from chonkie import TokenChunker, WordChunker, SentenceChunker


def create_chunks(table, model, chunk_size=500, overlap=125, mode="words", progress_callback=None, argself=None):
    """
    Chunk the text contained in the column "content" of an input table, with the help of an embedding model.

    Parameters:
        table (Table): The input table to process
        model (SentenceTransformer): The embeddings model to process the text.
        mode (str):

    Returns:
        out_data (Table): The data table with a column "Chunks" (and more row if several chunks were obtained per text)
    """
    # Copy of input data
    data = copy.deepcopy(table)

    # Chunking method
    if mode == "tokens":
        chunk_function = chunk_tokens
    elif mode == "words":
        chunk_function = chunk_words
    elif mode == "sentence":
        chunk_function = chunk_sentences
    elif mode == "semantic":
        chunk_function = chunk_semantic
    else:
        raise ValueError(f"Invalid mode: {mode}. Valid modes are: 'tokens', 'words', 'sentence', 'semantic'")

    # Create a new domain with the variable "Chunks"
    new_metas = list(data.domain.metas) + [StringVariable("Chunks")] + [ContinuousVariable("Chunks index")] + [StringVariable("Metadata")]
    new_domain = Domain(data.domain.attributes, data.domain.class_vars, new_metas)

    # Generate chunks on column named "content"
    new_rows = []
    for i, row in enumerate(data):
        content = row["content"].value
        chunks, metadata = chunk_function(content, tokenizer=model.tokenizer, chunk_size=chunk_size, chunk_overlap=overlap)
        # For each chunk in the chunked data
        for i, chunk in enumerate(chunks):
            # Build a new row with the previous data and the chunk
            new_metas_values = list(row.metas) + [chunk] + [i] + [metadata]
            new_instance = Orange.data.Instance(new_domain, [row[x] for x in data.domain.attributes] + [row[y] for y in data.domain.class_vars] + new_metas_values)
            new_rows.append(new_instance)

    # Retourner une nouvelle table avec toutes les instances générées
    out_data = Table.from_list(domain=new_domain, rows=new_rows)
    return out_data


def chunk_tokens(content, tokenizer, chunk_size=512, chunk_overlap=128, mode=None):
    chunker = TokenChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = chunker.chunk(content)
    chunks = [chunk.text for chunk in chunks]
    return chunks, []

def chunk_words(content, tokenizer, chunk_size=300, chunk_overlap=100):
    chunker = WordChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = chunker.chunk(content)
    chunks = [chunk.text for chunk in chunks]
    return chunks, []

def chunk_sentences(content, tokenizer, chunk_size=500, chunk_overlap=125):
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                              min_sentences_per_chunk=1)
    chunks = chunker.chunk(content)
    chunks = [chunk.text for chunk in chunks]
    return chunks, []

def chunk_semantic():
    pass



# def chunk_text(text):
#
#     # Basic initialization with default parameters
#     local_store_path = get_local_store_path()
#     model_name = "all-mpnet-base-v2"
#     model = os.path.join(local_store_path, "Models", "NLP", model_name)
#     chunker = SemanticChunker(
#         embedding_model=model,  # Default model
#         threshold=0.4,  # Similarity threshold (0-1)
#         similarity_window=3,
#         chunk_size=512,  # Maximum tokens per chunk
#         #min_chunk_size=300  # minimal chunk size
#     )
#
#     chunks = chunker.chunk(text)
#     chunks1 = []
#     for chunk in chunks:
#         chunks1.append(chunk.text)
#     return chunks1


    # @staticmethod
    # def chunk_data(data):
    #     """
    #     Takes a Table, segments the content of each instance into chunks of approximately
    #     400 words, stopping at sentence boundaries, and returns a new Table with the new instances.
    #
    #     :param data: The input Table.
    #     :return: A new Table with the segmented instances.
    #     """
    #
    #     new_instances = []
    #     domain = data.domain
    #
    #     # Créer un nouveau domaine avec une colonne "Chunks"
    #     new_metas = list(domain.metas) + [Orange.data.StringVariable("Chunks")]
    #     new_domain = Orange.data.Domain(domain.attributes, domain.class_vars, new_metas)
    #
    #     for instance in data:
    #         content = instance["content"].value  # Vérifie que "content" existe bien
    #         chunks = chunk_text(content)  # Découpe le texte en segments
    #
    #         for chunk in chunks:
    #             # Construire une nouvelle instance avec le segment
    #             new_metas_values = list(instance.metas) + [chunk]
    #             new_instance = Orange.data.Instance(new_domain, [instance[x] for x in domain.attributes] + [instance[y] for y in domain.class_vars] + new_metas_values)
    #             new_instances.append(new_instance)
    #
    #     # Retourner une nouvelle table avec toutes les instances générées
    #     return Orange.data.Table.from_list(new_domain, new_instances)