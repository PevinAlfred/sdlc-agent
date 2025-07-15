# a simple prompter that interacts with the Mistral LLM
# it sends a prompt and prints the response
import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model="mistral-small-latest",
    messages=[        
        {
            "role": "user",
            "content": "Reply with \"Yes\" if France won all the wars it fought, otherwise reply with \"No\".",
        },
    ]
)

print(chat_response.choices[0].message.content)