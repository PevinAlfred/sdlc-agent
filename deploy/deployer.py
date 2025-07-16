# This script deploys a service based on a configuration file.
# It reads the configuration from a YAML file and runs a deployment command.
import yaml
import subprocess

def load_deploy_config(path="./config/deploy_config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def run_deploy(deploy_plan: dict):
    strategy = deploy_plan.get("type", "rolling")
    flags = deploy_plan.get("flags", "")
    steps = deploy_plan.get("steps", ["echo No steps given"])

    print(f"Using strategy: {strategy}, flags: {flags}")
    for step in steps:
        print(f"Running step: {step}")
        #subprocess.run(step, shell=True, check=True)
        print(f"Simulated step: {step}")

if __name__ == "__main__":
    cfg = load_deploy_config()
    run_deploy(cfg)
