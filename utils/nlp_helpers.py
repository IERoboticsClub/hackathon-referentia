import os
from io import StringIO
from sentence_transformers import SentenceTransformer
from utils.redis_helpers import load_tokenizer_database

def get_reviews_sentences(reviews):
    # Join the reviews array into one string
    reviews = " ".join(reviews)
    sentences = reviews.replace(".  \n", ".").replace(".\n", ".").split(".")
    # Remove empty sentences
    sentences = [sentence for sentence in sentences if len(sentence) > 0]
    return sentences


def get_embedding(model, sentence):
    """This function returns the embedding of a sentence"""
    embedding = model.encode(sentence)
    return embedding


def get_db_schema(reviews):
    """This function returns a dictionary with all db schema values (including embeddings) for each sentence"""
    aux_dict = dict()
    model = load_tokenizer_database()
    for i in range(0, len(reviews)):
        embedded_text = get_embedding(model, reviews[i])
        aux_dict[i] = [i, reviews[i], embedded_text]
    return aux_dict