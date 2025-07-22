
import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize LangChain LLM for Mistral
llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-tiny")

def get_llm_decision(prompt, context=None):
    """
    Use LangChain to manage prompt and LLM call for agentic decision-making.
    Returns the LLM's response as a string.
    """
    system_prompt = """You are an SDLC agent that makes deployment, monitoring, and incident decisions.
Your response must be concise and directly answer the user's prompt.
Do not include any conversational filler, explanations, or justifications.
Output only the direct decision, command, or requested information."""

    human_template = """{prompt}
Context: {context}"""

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_template)
    ])

    chain = chat_prompt | llm | StrOutputParser()
    result = chain.invoke({"prompt": prompt, "context": context or ""})
    return result.strip()
