import logging
import os



def load_models(): 
    """This function returns a dictionary with all the models and their respective huggingface names"""
    return {
                'MarIA Base': 'PlanTL-GOB-ES/roberta-base-bne-sqac', # qa
                'MarIA large': 'PlanTL-GOB-ES/roberta-large-bne-sqac', # qa
                'Beto Base Spanish Sqac': 'IIC/beto-base-spanish-sqac', # qa

                'ChatGPT': 'openai', # paid token
                'GPT2 Base Spanish Fine tuned': 'xxxx/gpt2-large-bne', # tbd
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
