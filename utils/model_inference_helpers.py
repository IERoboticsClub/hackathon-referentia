import torch
from transformers import pipeline
from utils.common import LOG
import os
import openai
from openai.error import OpenAIError



def query_openai(gpt_engine: str, assistant_prompt: str, max_new_tokens: int): 
    """This function creates a query for the openai model"""
    LOG.info(f"Engine: {gpt_engine}")
    LOG.info(f"Assistant Prompt: {assistant_prompt}")
    LOG.info(f"Max Tokens: {max_new_tokens}")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORG")
    try:

        response = openai.Completion.create(
                    engine=gpt_engine,
                    prompt=assistant_prompt,
                    max_tokens=max_new_tokens,
                )
        
        LOG.info(f"Response: {response}")
        res = response.choices[0].text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
        LOG.info(f"Answer: {res}")
    except OpenAIError as e:
       LOG.info(f"OpenAIError: {e}")
       LOG.info("Error: Please check that your token is valid server!")
       res = "None"
    return res
   

def query_model(model:str, prompt: tuple, **args): 
    """ This function handles querying hugginface models"""
    if model != "openai":
        nlp = pipeline("question-answering", model=model)
        question = prompt[0]
        context = prompt[1]
        res = nlp(question, context)
        LOG.info(f"Question: {question}")
        LOG.info(f"Context: {context}")
        LOG.info(f"Answer: {res['answer']}")

    return res
    

    





