import redis
from redis.commands.search.query import Query
from redis.commands.search.field import VectorField, TextField
import numpy as np
import hashlib
from utils.ocr import get_embedding, load_tokenizer_database
import os
from utils.common import LOG

# Redis connection details
endpoint = "127.0.0.1"
port = 6379
username = "default"


def connect_redis():
    """Connect to Redis and return the connection object."""
 
    redis_conn = redis.Redis(host=endpoint, port=port, username=username)
    return redis_conn


def upload_to_redis(id_sentence: str, sourcepage: str, sourcefile: str, text: str, embedded_text: list, redis_conn: redis.Redis):
    """Upload a document to Redis."""
    key_doc = {
    "id": id_sentence,
    "sourcepage": sourcepage,
    "sourcefile": sourcefile,
    "content": text,
    "embeddings": np.array(embedded_text).astype(dtype=np.float32).tobytes(), 
    }
    # Store a blob of a random vector of type float32 under a field named 'vector' in Redis hash.
    hash_key = hashlib.md5(text.encode()).hexdigest()
    key = f"embedding:{hash_key}"
    redis_conn.hset(key, mapping=key_doc)


# Helper function to print results
def print_results(res):
    docs = [doc.id for doc in res.docs]
    dists = [float(doc.dist) if hasattr(doc, 'dist') else '-' for doc in res.docs]
    LOG.info(f"GOT {len(docs)} doc ids: ", docs)
 
def reformat_redis(redis_conn: redis.Redis):
    """Reformat the Redis database to use the new schema."""
    # Cleans the Redis database
    redis_conn.flushall()

    


    vector_field = "embeddings"

    schema = (TextField("id"),
                TextField("content"),
                TextField("sourcepage"),
                TextField("sourcefile"),
                VectorField(vector_field,  "FLAT", {"TYPE": "FLOAT32", "DIM": 768 , "DISTANCE_METRIC": "COSINE"}))
    redis_conn.ft().create_index(schema, "index")
    redis_conn.ft().config_set("default_dialect", 2)




def get_top_n(n: int, redis_conn: redis.Redis , vector_query: np.array) -> dict: 
    #q = Query(f'*=>[KNN {5} @embedding $vec_param]=>{{$yield_distance_as: dist}}') 
    q = Query(f'*=>[KNN {n} @embeddings $vec_param]=>{{$yield_distance_as: dist}}').sort_by(f'dist')
    res = redis_conn.ft().search(q, query_params = {'vec_param': vector_query})
    
    return res


def create_query_context(redis_conn: redis.Redis, user_query: str, model: str) -> tuple:
    """ Here we structure the context of the query depending on wether the model is an enocoder or decoder based model. """
    tokenizer = load_tokenizer_database()
    LOG.info(f"Model for query context: {tokenizer}") 
    embedded_query = get_embedding(user_query, tokenizer)
    vector_query = np.array(embedded_query).astype(dtype=np.float32).tobytes()
    print(redis_conn)
    search_result = get_top_n(5, redis_conn, vector_query)

    context = ""
    
    if model == "openai":
        for doc in search_result.docs:
            context = context + f"""Ref: [{doc.sourcefile}, page {doc.sourcepage}] Content: {doc.content}\n"""
        prompt = f""""Como asistente inteligente, tu tarea es responder a las preguntas utilizando los datos proporcionados en el contexto de la fuente dada. Si la información necesaria no está disponible en las fuentes proporcionadas, puedes apoyarte en tu propio conocimiento y hacer referencia a la fuente 'modelo' en tu respuesta.  Cada fuente se identifica por un nombre de archivo, número de página y contenido correspondiente. Asegúrate de citar el archivo de origen cada vez que lo utilices en tu respuesta. Dado que debes utilizar la fuente 'modelo', por favor asegúrate de citarla correctamente. "

        Pregunta: {user_query}\n\n
        Datos de la fuente:\n{context}\n\n
        Respuesta:"""
        return prompt
    
        
    else: 
        context = f"{search_result.docs[0].content}, \n"

    return user_query, context


def create_reviews_query_context(redis_conn: redis.Redis, user_query: str):
    model = load_tokenizer_database()
    embedded_query = get_embedding(model, user_query)
    vector_query = np.array(embedded_query).astype(dtype=np.float32).tobytes()
    search_result = get_top_n(10, redis_conn, vector_query)
    context = ""
    for doc in search_result.docs:
        # Merge the variables of the doc into a single string
        context = context + f"""Review {doc.uid} Content: {doc.content}\n"""
    
    prompt = f""""As an intelligent chatbot, your role is to assist users asking questions about an Airbnb listing. You will respond to questions using only the data provided in the given source context. If the necessary information is not available in the provided sources, say I don't know."\n\n
    Question: {user_query}\n\n
    Source data:\n{context}\n\n
    Answer:"""
    print(prompt)
    return prompt