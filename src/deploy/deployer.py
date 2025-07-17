import subprocess
import logging

def deploy_application(script_path):
    """Deploy the application using the provided script."""
    try:
        logging.info(f"Executing deployment script: {script_path}")
        subprocess.run(["powershell.exe", script_path], check=True)
        logging.info("Deployment successful.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Deployment failed: {e}")
        raise
