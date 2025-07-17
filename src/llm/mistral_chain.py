 
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

client = MistralClient(api_key=MISTRAL_API_KEY)

def get_llm_decision(prompt, context=None):
    """
    Use Mistral LLM to make a decision based on the prompt and context.
    Returns the LLM's response as a string.
    """
    messages = [ChatMessage(role="system", content="You are an SDLC agent that makes deployment and incident decisions."),
                ChatMessage(role="user", content=prompt)]
    if context:
        messages.append(ChatMessage(role="user", content=str(context)))
    response = client.chat(
        model="mistral-tiny",
        messages=messages
    )
    return response.choices[0].message.content.strip()
