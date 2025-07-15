# orchestrator.py

from deploy.deployer import run_deploy
from monitoring.monitor import check_system_status
from llm.llm_client import ask_llm_decision, ask_llm_deploy_plan
from incident.incident_manager import raise_incident
from incident.notifier import notify_developer
from deploy.deployer import load_deploy_config
from utils.logger import log

def main():
    # Load base config (service, version, env)
    base_config = load_deploy_config()

    # Ask LLM for deployment strategy
    deploy_plan = ask_llm_deploy_plan(base_config)
    log(f"LLM Deployment Plan: {deploy_plan}")

    # Deploy based on LLM plan
    run_deploy(deploy_plan)
    log("Deployment complete.")

    # Monitor system status
    status = check_system_status()
    log(f"System status: {status}")

    # Ask LLM if incident needed
    decision = ask_llm_decision(
        "You are an SDLC agent. Reply ONLY as JSON: {\"decision\": \"yes\" or \"no\"}",
        f"The system status is: {status}."
    )
    log(f"LLM Decision: {decision}")

    if decision.get("decision", "").lower() == "yes":
        raise_incident(f"Status {status} for {base_config['service']}")
        notify_developer("Incident created.")
    else:
        log("No incident needed. System healthy!")

if __name__ == "__main__":
    main()
