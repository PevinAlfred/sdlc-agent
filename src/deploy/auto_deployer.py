import os
import subprocess
import logging
import shutil
from src.llm.mistral_chain import get_llm_decision
from src.config.settings import GITHUB_TOKEN

logger = logging.getLogger(__name__)

def clone_or_pull_repo(repo_full_name, branch, target_dir):
    """Clones or pulls a specific branch of a GitHub repository into a target directory."""
    os.makedirs(target_dir, exist_ok=True)
    repo_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{repo_full_name}.git"

    if os.path.exists(os.path.join(target_dir, ".git")):
        logger.info(f"Repository exists at {target_dir}. Fetching updates for branch '{branch}'.")
        try:
            subprocess.run(["git", "-C", target_dir, "fetch"], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", target_dir, "checkout", branch], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", target_dir, "pull", "origin", branch], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull updates for {repo_full_name}, attempting re-clone: {e.stderr}")
            shutil.rmtree(target_dir)
            subprocess.run(["git", "clone", "--branch", branch, repo_url, target_dir], check=True, capture_output=True, text=True)
    else:
        logger.info(f"Cloning repository {repo_full_name} (branch: {branch}) into {target_dir}.")
        try:
            subprocess.run(["git", "clone", "--branch", branch, repo_url, target_dir], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repository {repo_full_name}: {e.stderr}")
            raise

def fetch_app_context_from_local(local_repo_path):
    """Fetches key files from the local cloned repo for LLM context."""
    files_to_try = ["requirements.txt", "Dockerfile", "package.json", "Pipfile", "pyproject.toml", "README.md"]
    context = []
    for file_name in files_to_try:
        file_path = os.path.join(local_repo_path, file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context.append(f"# {file_name}\n{content}\n")
            except Exception as e:
                logger.warning(f"Could not read context file {file_path}: {e}")
    return "\n".join(context)

def generate_deployment_script(local_repo_path, container_name):
    """Fetch app context from local repo, prompt LLM to generate a deployment script, and return the script."""
    app_context = fetch_app_context_from_local(local_repo_path)
    if not app_context:
        app_context = "No context files found. Assume a generic Python/Flask web application with a Dockerfile."

    # A more robust prompt that generates a script resilient to zombie containers.
    prompt = f"""
Based on the application context provided, generate a complete, robust shell script to deploy a Docker application.

Instructions:
1.  **Use provided names and ports**:
    - Container Name: '{container_name}'
    - Image Name: '{container_name}'
    - Host Port: 5000 (or determine from Dockerfile if possible)
2.  **Start with `set -e`**: The script must exit immediately if any command fails.
3.  **Robust Cleanup**: Before building, the script MUST find and stop any container currently using the target host port.
    - Use `docker ps -q --filter "publish=<HOST_PORT>"` to find the container ID.
    - Check if a container ID was found before attempting to stop/remove it.
    - Provide clear `echo` statements for each step (e.g., "--- Cleaning up old containers ---").
4.  **Build Step**: Build the Docker image using `docker build -t <IMAGE_NAME> .`.
5.  **Deploy Step**: Run the new container using `docker run`.
    - It must be named (`--name <CONTAINER_NAME>`).
    - It must be detached (`-d`).
    - It must have a restart policy (`--restart always`).
    - It must map the correct port (`-p <HOST_PORT>:<CONTAINER_PORT>`).
6.  **Format**: The final output MUST be ONLY the raw shell script. Do not include markdown or explanations.
"""
    context = f"""
Application Context:
{app_context}
"""
    script = get_llm_decision(prompt, context).strip()
    # Clean up potential markdown code fences that LLMs sometimes add
    if script.startswith("```sh"): script = script[5:]
    if script.startswith("```bash"): script = script[7:]
    if script.startswith("```"): script = script[3:]
    if script.endswith("```"): script = script[:-3]

    return script.strip()

def save_deployment_script(script, path):
    with open(path, "w", encoding="utf-8", newline='\n') as f:
        f.write(script)
    return path

def auto_deploy(repo_full_name, branch="main"):
    """
    Main entry: clone repo, generate script, save in repo dir. Returns script path.
    """
    # Create a consistent, safe name for the container from the repo name.
    safe_repo_name = repo_full_name.replace('/', '_').lower()
    workspace_dir = os.path.abspath(os.path.join("workspace", safe_repo_name))
    clone_or_pull_repo(repo_full_name, branch, workspace_dir)
    script = generate_deployment_script(workspace_dir, container_name=safe_repo_name)
    script_path = save_deployment_script(script, path=os.path.join(workspace_dir, "generated_deploy.sh"))
    return script_path
