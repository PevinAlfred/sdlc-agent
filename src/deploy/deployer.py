import subprocess
import logging
import os
import sys
import shutil

def _find_bash_on_windows():
    """Find a reliable bash executable on Windows, preferring Git Bash."""
    # Common locations for Git for Windows' bash.exe
    possible_paths = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Git", "bin", "bash.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Git", "bin", "bash.exe"),
        os.path.join(os.environ.get("LocalAppData"), "Programs", "Git", "bin", "bash.exe")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    # If not found in common locations, fall back to searching the PATH.
    return shutil.which("bash")

def deploy_application(script_path):
    """Deploy the application by executing the provided script file."""
    try:
        # Ensure the script exists before trying to execute it
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Deployment script not found at path: {script_path}")

        logging.info(f"Executing deployment script: {script_path}")

        # Make the script executable (only necessary on non-Windows systems)
        if sys.platform != "win32" and os.path.exists(script_path):
            os.chmod(script_path, 0o755)

        # Determine the directory of the script to use as the current working directory.
        # This ensures that commands inside the script (like `docker build .`) run from the correct location.
        cwd = os.path.dirname(os.path.abspath(script_path))
        script_name = os.path.basename(script_path)

        # Find the bash executable in a robust, cross-platform way.
        if sys.platform == "win32":
            bash_executable = _find_bash_on_windows()
        else:
            bash_executable = shutil.which("bash")
        if not bash_executable:
            raise FileNotFoundError(
                "bash executable not found in PATH. "
                "Please install Git for Windows or WSL and ensure 'bash.exe' is in your system's PATH."
            )

        # Execute the script using the found 'bash' executable. This is the most robust
        # method for cross-platform compatibility.
        command = [bash_executable, script_name]
        logging.info(f"Executing command: '{' '.join(command)}' in '{cwd}'")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=cwd
        )
        logging.info("Deployment successful.")
        logging.info(f"Script output:\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        # e.cmd is a list when shell=False, so we join it for logging.
        logging.error(f"Deployment script failed: Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}.")
        if e.stdout: logging.error(f"STDOUT:\n{e.stdout}")
        if e.stderr: logging.error(f"STDERR:\n{e.stderr}")
        raise  # Re-raise the exception so the caller knows it failed.
    except (FileNotFoundError, Exception) as e:
        logging.error(f"An unexpected error occurred during deployment: {e}")
        raise
