import os
import requests
import base64
from src.llm.mistral_chain import get_llm_decision
from src.config.settings import GITHUB_TOKEN

GITHUB_API_URL = "https://api.github.com"

def fetch_file_from_github(repo_full_name, file_path, branch="main"):
    """
    Fetch a file's content from a GitHub repository using the API.
    Returns the decoded file content as a string.
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/contents/{file_path}?ref={branch}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        return base64.b64decode(content).decode()
    else:
        return None

def fetch_app_context(repo_full_name, branch="main"):
    """
    Fetches key files (e.g., requirements.txt, Dockerfile, package.json) from the repo for LLM context.
    Returns a string summary of the app context.
    """
    files_to_try = ["requirements.txt", "Dockerfile", "package.json", "Pipfile", "pyproject.toml", "README.md"]
    context = []
    for file in files_to_try:
        content = fetch_file_from_github(repo_full_name, file, branch)
        if content:
            context.append(f"# {file}\n{content}\n")
    return "\n".join(context)

def generate_deployment_script(repo_full_name, branch="main"):
    """
    Fetch app context, prompt LLM to generate a deployment script, and return the script.
    """
    app_context = fetch_app_context(repo_full_name, branch)
    if not app_context:
        app_context = "No context files found."
    prompt = f"""
You are an expert DevOps engineer. Generate a production-ready deployment script for the following app.\n
Here is the app context:\n{app_context}\n
The script should build and run the app in a production environment.\n
Output only the script, no explanations.\n"""
    script = get_llm_decision(prompt)
    return script

def save_deployment_script(script, path="generated_deploy.sh"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(script)
    os.chmod(path, 0o755)
    return path

def auto_deploy(repo_full_name, branch="main"):
    """
    Main entry: fetch context, generate script, save. Returns script path.
    """
    script = generate_deployment_script(repo_full_name, branch)
    script_path = save_deployment_script(script)
    return script_path
