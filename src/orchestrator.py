import logging
from src.config.settings import PROMETHEUS_URL, GITHUB_TOKEN, JIRA_URL, JIRA_USER, JIRA_API_TOKEN, EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, LOG_LEVEL
from src.deploy.deployer import deploy_application
from src.deploy.auto_deployer import auto_deploy
from src.monitor.prometheus_client import fetch_metrics
from src.incident.github_issues import create_github_issue
from src.incident.jira_client import create_jira_ticket
from src.incident.email_notifier import send_email_notification
from src.llm.mistral_chain import get_llm_decision

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("SDLC-Agent")

def orchestrate_pipeline(pr_event):
    """Main pipeline logic for handling PR events, fully LLM-driven."""
    try:
        logger.info("Starting AI agent pipeline...")

        # Step 1: LLM decides whether to deploy
        deploy_decision = get_llm_decision(
            "Should we deploy this PR? Reply with 'deploy' or 'skip' and a short reason.",
            context=pr_event
        )
        logger.info(f"LLM deploy decision: {deploy_decision}")

        if 'deploy' in deploy_decision.lower():
            # Extract repo and branch from pr_event (GitHub PR event structure)
            repo = None
            branch = None
            try:
                repo = pr_event["base"]["repo"]["full_name"]
                branch = pr_event["base"]["ref"]
            except Exception:
                logger.warning("Could not extract repo/branch from PR event, using defaults.")
                repo = None
                branch = None
            if repo and branch:
                script_path = auto_deploy(repo, branch)
                deploy_application(script_path)
                logger.info(f"Deployment triggered by LLM for {repo}@{branch}.")
            else:
                logger.error("Repository or branch information missing. Deployment skipped.")

            # Step 2: Monitor after deploy
            metrics = fetch_metrics(PROMETHEUS_URL)
            analysis = get_llm_decision(
                "Analyze these metrics and decide if an incident should be raised. Reply with 'incident' or 'healthy' and a short reason.",
                context={
                    "metrics": metrics,
                    "pr_event": pr_event
                }
            )
            logger.info(f"LLM post-deploy analysis: {analysis}")
            if 'incident' in analysis.lower():
                # Step 3: LLM decides incident response channels
                incident_channels = get_llm_decision(
                    "Which incident channels should be used? Reply with a comma-separated list from: github, jira, email.",
                    context={
                        "metrics": metrics,
                        "pr_event": pr_event,
                        "analysis": analysis
                    }
                )
                logger.info(f"LLM incident channels: {incident_channels}")
                if 'github' in incident_channels.lower():
                    create_github_issue(GITHUB_TOKEN, {"title": "Incident detected", "description": analysis})
                if 'jira' in incident_channels.lower():
                    create_jira_ticket(JIRA_URL, JIRA_USER, JIRA_API_TOKEN, {"title": "Incident detected", "description": analysis})
                if 'email' in incident_channels.lower():
                    send_email_notification(EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, {"recipient": EMAIL_USER, "title": "Incident detected", "description": analysis})
                logger.warning("Incident created and notifications sent as per LLM decision.")
            else:
                logger.info("No incident detected. System healthy as per LLM.")
        else:
            logger.info("Deployment skipped by LLM decision.")

        logger.info("AI agent pipeline execution completed.")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise
