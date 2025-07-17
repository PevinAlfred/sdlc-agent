import logging
from src.config.settings import PROMETHEUS_URL, GRAFANA_URL, GITHUB_TOKEN, JIRA_URL, JIRA_USER, JIRA_API_TOKEN, EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, DEPLOYMENT_SCRIPT_PATH, LOG_LEVEL
from src.deploy.deployer import deploy_application
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
            pr_event
        )
        logger.info(f"LLM deploy decision: {deploy_decision}")
        if 'deploy' in deploy_decision.lower():
            deploy_application(DEPLOYMENT_SCRIPT_PATH)
            logger.info("Deployment triggered by LLM.")

            # Step 2: Monitor after deploy
            metrics = fetch_metrics(PROMETHEUS_URL)
            analysis = get_llm_decision(
                "Analyze these metrics and decide if an incident should be raised. Reply with 'incident' or 'healthy' and a short reason.",
                metrics
            )
            logger.info(f"LLM post-deploy analysis: {analysis}")
            if 'incident' in analysis.lower():
                # Step 3: LLM decides incident response channels
                incident_channels = get_llm_decision(
                    "Which incident channels should be used? Reply with a comma-separated list from: github, jira, email.",
                    pr_event
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
