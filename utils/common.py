import logging
import os
import ast
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """
    Class for configuration of the environment
    """
    controller:str
    worker:str
    openapi:str
    org:str
    version:None
    endpoint:str 
    port:str
    username:str

 
# def config_local() -> Config:
#     """This function returns the configuration for the local environment"""
#     try:
#         return Config(openapi=os.getenv('OPENAI_API_KEY'),
#                     org=os.getenv('OPENAI_ORG'),
#                     type=os.getenv('OPENAI_API_TYPE'),
#                     version=os.getenv('OPENAI_API_VERSION'),
#                     controller=os.getenv('REDIS_CONTROLLER'),
#                     worker=os.getenv('REDIS_WORKER'), 
#                     endpoint=os.getenv('REDIS_ENDPOINT'),
#                     port=os.getenv('REDIS_PORT'),
#                     username=os.getenv('REDIS_USERNAME'))
    
#     except KeyError as ke:
#         raise ValueError(f'The env var {ke} is mandatory')


def config_from_env() -> Config:
    if os.environ['STATE'] == 'PROD' or os.getenv('STATE') == 'PROD':
        
        try:
            return Config(openapi=os.environ['OPEN_API_KEY'],
                        org=os.environ['OPENAI_ORG'])
        
        except KeyError as ke:
            raise ValueError(f'The env var {ke} is mandatory')
    else:
        try:
            return Config(openapi=os.getenv('OPENAI_API_KEY'),
                        org=os.getenv('OPENAI_ORG'),
                        controller=os.getenv('REDIS_CONTROLLER'),
                        worker=os.getenv('REDIS_WORKER'), 
                        version=ast.literal_eval(os.getenv('OPENAI_API_VERSION')),
                        endpoint=os.getenv('REDIS_ENDPOINT'),
                        port=os.getenv('REDIS_PORT'),
                        username=os.getenv('REDIS_USERNAME'))
        
        except KeyError as ke:
            raise ValueError(f'The env var {ke} is mandatory')


def load_models(): 
    """This function returns a dictionary with all the models and their respective huggingface names"""
    return {
                'MarIA Base': 'PlanTL-GOB-ES/roberta-base-bne-sqac', # qa
                'MarIA large': 'PlanTL-GOB-ES/roberta-large-bne-sqac', # qa
                'Beto Base Spanish Sqac': 'IIC/beto-base-spanish-sqac', # qa
                'ChatGPT': 'openai', # paid token
                'GPT2 Base Spanish Fine tuned': 'coming soon', # TODO: add model
            }

def create_logger(): 
    """This function creates a logger"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = logging.FileHandler('logs/assistente_privado.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger



# ------ CONSTANTS ------
LOG = create_logger()

env = config_from_env()

