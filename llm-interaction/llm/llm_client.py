#parsing an LLM response to JSON

import os
import json
import re
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env file!")

client = Mistral(api_key=api_key)

def ask_llm_decision(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    raw_output = response.choices[0].message.content
    try:
        # Ensure the output is a valid JSON object
        raw_output = raw_output.strip()
        result = json.loads(raw_output)        
    except json.JSONDecodeError:
        result = {"error": "Invalid JSON", "raw_output": raw_output}
    return result

def ask_llm_deploy_plan(base_config: dict) -> dict:

    system_prompt = "You are a DevOps agent. Respond ONLY in JSON (no markdown fences) with this format: {\"type\":\"<strategy>\",\"flags\":\"<flags>\",\"steps\":[\"<step1>\",\"<step2>\"]}."
    user_prompt = f"Service: {base_config['service']}, Version: {base_config['version']}, Env: {base_config['env']}. Suggest strategy"
    
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    raw_output = response.choices[0].message.content
    try:
        raw_output = raw_output.strip()
    # Remove markdown code fences if present
        raw_output = re.sub(r"^```(?:json)?\\n|```$", "", raw_output, flags=re.IGNORECASE).strip()
        plan = json.loads(raw_output)
    except json.JSONDecodeError:
        plan = {"error": "Invalid JSON", "raw_output": raw_output}
    return plan

if __name__ == "__main__":
    decision = ask_llm_decision(
        "Respond ONLY in JSON. Do not use markdown fences. Return a response like an API: {\"decision\": \"yes\" or \"no\"}",
        "System status is: FAIL. Should we raise an incident?"
    )
    print(decision)