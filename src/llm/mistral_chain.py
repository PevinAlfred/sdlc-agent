
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain.chains import LLMChain

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize LangChain LLM for Mistral
llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-tiny")

def get_llm_decision(prompt, context=None):
    """
    Use LangChain to manage prompt and LLM call for agentic decision-making.
    Returns the LLM's response as a string.
    """
    template = PromptTemplate(
        input_variables=["prompt", "context"],
        template="""
You are an SDLC agent that makes deployment, monitoring, and incident decisions.\n
{prompt}
Context: {context}
"""
    )
    chain = LLMChain(llm=llm, prompt=template)
    result = chain.run({"prompt": prompt, "context": context or ""})
    return result.strip()
