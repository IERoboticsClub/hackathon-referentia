

import openai
import streamlit as st
from utils.common import LOG


def query_openai(prompt, **args):
    """This function creates a query for the openai model"""
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = "org-z1xMbou2zvfWdtaTwCDYFEsX"
    openai.api_key = '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'
    gpt_engine = args.get("gpt_engine", "text-davinci-002")
    max_new_tokens = args.get("max_new_tokens", 100)
    assistant_prompt = prompt

    
    LOG.info(f"Prompt: {gpt_engine}")

    try:
        LOG.info(f"Sending req to openai")
        response = openai.Completion.create(
            engine=gpt_engine,
            prompt=assistant_prompt,
            max_tokens=max_new_tokens,
        )
        output = response.choices[0].text

        
    except:
        st.warning("Error: Please check that your token is valid server!")
        output = "None"
    return output
