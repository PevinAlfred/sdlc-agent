import logging
import os
import re
import requests
import time
from src.config.settings import PROMETHEUS_URL, GITHUB_TOKEN, JIRA_URL, JIRA_USER, JIRA_API_TOKEN, JIRA_PROJECT_KEY, EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, LOG_LEVEL
from src.deploy.deployer import deploy_application
from src.deploy.auto_deployer import auto_deploy, fetch_app_context_from_local
from src.monitor.prometheus_client import fetch_metrics
from src.incident.github_issues import create_github_issue
from src.incident.jira_client import create_jira_ticket
from src.incident.email_notifier import send_email_notification
from src.llm.mistral_chain import get_llm_decision

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("SDLC-Agent")

def _summarize_pr_for_llm(pr_event):
    """Summarizes a GitHub PR event into a structured string for LLM analysis."""
    try:
        pr_title = pr_event.get("title", "N/A")
        pr_body = pr_event.get("body") or "No description provided."
        author = pr_event.get("user", {}).get("login", "N/A")
        additions = pr_event.get("additions", 0)
        deletions = pr_event.get("deletions", 0)
        changed_files_count = pr_event.get("changed_files", 0)

        summary = f"""
        Pull Request Summary:
        - Title: {pr_title}
        - Author: {author}
        - Description: {pr_body}
        - Changes: +{additions} lines added, -{deletions} lines removed, across {changed_files_count} file(s).
        """
        return summary.strip()
    except Exception as e:
        logger.error(f"Failed to summarize PR event: {e}")
        return "Could not summarize PR event."

def _perform_health_check(url, retries=5, delay=5):
    """Pings a URL to check if the application is responsive after deployment."""
    logger.info(f"Performing health check on {url}...")
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            # Check for any 2xx success status code
            if 200 <= response.status_code < 300:
                logger.info(f"Health check successful! Status code: {response.status_code}")
                return True
            else:
                logger.warning(f"Health check attempt {i+1}/{retries} failed with status code: {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"Health check attempt {i+1}/{retries} failed with exception: {e}")
        time.sleep(delay)
    logger.error(f"Health check failed after {retries} attempts for URL: {url}")
    return False

def _get_port_from_script(script_path):
    """Parses the generated deployment script to find the exposed host port."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Regex to find patterns like -p 8080:80 or -p 5000:5000 and capture the host port.
        match = re.search(r"-p\s+(?:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:)?([0-9]+):", script_content)
        if match:
            port = match.group(1)
            logger.info(f"Extracted host port {port} from deployment script.")
            return port
    except Exception as e:
        logger.warning(f"Could not parse port from deployment script: {e}")
    
    logger.warning("Could not determine port from script, falling back to default 5000.")
    return "5000" # Fallback to default

def orchestrate_pr_merge_pipeline(pr_event):
    """Main pipeline for handling PR merge events, with LLM-driven checks."""
    try:
        logger.info("Starting AI agent pipeline...")

        # Step 1: LLM decides whether to deploy based on a structured checklist
        pr_summary = _summarize_pr_for_llm(pr_event)
        
        deployment_checklist_prompt = """
You are an expert SDLC gatekeeper. Your task is to decide if a Pull Request is safe to deploy.
Analyze the provided PR summary and make a decision based on the following checklist. Provide a clear reason for your choice.

Deployment Checklist:
1.  **Clarity and Intent**: Does the PR title and description clearly explain the purpose of the change?
2.  **Risk Assessment**: Does the change appear to be high-risk? (e.g., modifying critical configuration, core logic, or database schemas). Small bug fixes are low-risk. Large new features are higher risk.
3.  **"Work in Progress" Check**: Are there any keywords like 'WIP', 'Draft', 'Do Not Merge' in the title or body? If so, it should be skipped.
4.  **Sanity Check**: Does the change seem reasonable and complete?

Based on this checklist, should we deploy this PR? Reply with only 'deploy' or 'skip' and a concise reason based on the checklist items.
"""
        
        deploy_decision = get_llm_decision(
            deployment_checklist_prompt,
            context=pr_summary
        )
        logger.info(f"LLM deploy decision: {deploy_decision}")

        if 'deploy' in deploy_decision.lower():
            # Extract repo and branch from pr_event (GitHub PR event structure)
            repo = None
            branch = None
            repo = pr_event.get("base", {}).get("repo", {}).get("full_name")
            branch = pr_event.get("base", {}).get("ref")

            if repo and branch:
                script_path = auto_deploy(repo, branch)
                deploy_application(script_path)
                logger.info(f"Deployment triggered by LLM for {repo}@{branch}.")
                
                # Step 2: Perform post-deployment health check.
                port = _get_port_from_script(script_path)
                health_check_url = f"http://localhost:{port}"
                if not _perform_health_check(health_check_url):
                    raise Exception(f"Post-deployment health check failed for {health_check_url}")

                # Step 3: Check if monitoring is applicable before proceeding
                local_repo_path = os.path.dirname(script_path)
                app_context = fetch_app_context_from_local(local_repo_path)
                
                monitoring_prompt = "Based on the context (e.g., requirements.txt, Dockerfile), does this application seem to be instrumented to expose a /metrics endpoint for Prometheus? Look for dependencies like 'prometheus-flask-exporter'. Reply with only 'yes' or 'no'."
                
                monitoring_decision = get_llm_decision(monitoring_prompt, app_context)
                logger.info(f"LLM monitoring applicability decision: {monitoring_decision}")

                if 'yes' in monitoring_decision.lower():
                    # --- NEW: Post-deployment Smoke Test ---
                    logger.info("Running post-deployment smoke test by generating traffic...")
                    # A more advanced agent could ask the LLM for likely test endpoints.
                    # We will try a common /error endpoint first, then the root.
                    test_endpoints = ["/error", "/"] 
                    test_url_base = f"http://localhost:{port}"
                    
                    for endpoint in test_endpoints:
                        test_url = test_url_base + endpoint
                        logger.info(f"Generating 20 requests to {test_url} to check for errors.")
                        for _ in range(20):
                            try:
                                # We don't care about the response, just that the request is made.
                                requests.get(test_url, timeout=2)
                            except requests.RequestException:
                                # Ignore exceptions; we want to see them as error metrics in Prometheus.
                                pass
                    
                    scrape_interval = 15 # This value should be >= your Prometheus scrape_interval.
                    logger.info(f"Waiting {scrape_interval} seconds for Prometheus to scrape new metrics...")
                    time.sleep(scrape_interval)

                    # Step 4: Monitor after deploy
                    logger.info("Application appears to be instrumented. Proceeding with monitoring.")
                    metrics = fetch_metrics(PROMETHEUS_URL)

                    analysis_prompt = """
You are a Site Reliability Engineer (SRE). Your task is to analyze Prometheus metrics and determine if an incident should be declared.

**Analysis Checklist:**
1.  **HTTP Server Errors (5xx)**: Are there any metrics indicating HTTP 5xx server errors? A non-zero count of 5xx errors is a strong indicator of an incident.
2.  **HTTP Client Errors (4xx)**: Is there an unusually high rate of 4xx errors? A few are normal, but a sudden spike can indicate a problem.
3.  **Request Latency**: Is the request latency (e.g., `http_requests_latency_seconds_bucket`) abnormally high?

**Decision:**
Based on the checklist and the provided context, is the system 'healthy' or is there an 'incident'? Provide a concise reason for your decision based on the metrics.
"""

                    analysis = get_llm_decision(
                        analysis_prompt,
                        context={
                            "metrics": metrics,
                            "pr_summary": pr_summary
                        }
                    )
                    logger.info(f"LLM post-deploy analysis: {analysis}")
                    if 'incident' in analysis.lower():
                        # Step 5: LLM decides which channels to notify
                        incident_channels = get_llm_decision(
                            "Which incident channels should be used? Reply with a comma-separated list from: github, jira, email.",
                            context={
                                "metrics": metrics,
                                "pr_summary": pr_summary,
                                "analysis": analysis
                            }
                        )
                        logger.info(f"LLM incident channels: {incident_channels}")

                        # Create a detailed incident payload for consistent reporting
                        incident_title = f"AI-Detected Incident in {repo}"
                        incident_description = f"**AI SRE Analysis:**\n{analysis}\n\n**Triggering Pull Request:**\n{pr_summary}"
                        incident_payload = {
                            "title": incident_title,
                            "description": incident_description,
                            "repo": repo, # For GitHub Issues
                            "recipient": EMAIL_USER, # For Email Notifier
                            "project_key": JIRA_PROJECT_KEY # For Jira Tickets
                        }

                        logger.warning("Incident detected. Sending notifications...")
                        if 'github' in incident_channels.lower():
                            try:
                                create_github_issue(GITHUB_TOKEN, incident_payload)
                            except Exception as e:
                                logger.error(f"Failed to create GitHub issue: {e}")
                        if 'jira' in incident_channels.lower():
                            try:
                                create_jira_ticket(JIRA_URL, JIRA_USER, JIRA_API_TOKEN, incident_payload)
                            except Exception as e:
                                logger.error(f"Failed to create Jira ticket: {e}")
                        if 'email' in incident_channels.lower():
                            try:
                                send_email_notification(EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, incident_payload)
                            except Exception as e:
                                logger.error(f"Failed to send email notification: {e}")
                        logger.info("Incident response process completed.")
                    else:
                        logger.info("No incident detected. System healthy as per LLM.")
                else:
                    logger.info("Monitoring skipped: LLM determined the application does not expose a /metrics endpoint.")
            else:
                logger.error("Repository or branch information missing. Deployment skipped.")

        else:
            logger.info("Deployment skipped by LLM decision.")

        logger.info("AI agent pipeline execution completed.")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

def orchestrate_branch_push_pipeline(repo, branch):
    """Pipeline for handling direct pushes to feature branches."""
    try:
        logger.info(f"Starting direct deployment pipeline for {repo}@{branch}...")
        # For direct pushes, we bypass the LLM approval and go straight to deployment.
        # The full monitoring and incident response could be added here if desired.
        script_path = auto_deploy(repo, branch)
        deploy_application(script_path)

        # Perform post-deployment health check
        port = _get_port_from_script(script_path)
        health_check_url = f"http://localhost:{port}"
        if not _perform_health_check(health_check_url):
            # A more advanced implementation could trigger a rollback here.
            raise Exception(f"Post-deployment health check failed for {health_check_url}")

        logger.info(f"Deployment successful for {repo}@{branch}.")
        logger.info("Direct deployment pipeline execution completed.")
    except Exception as e:
        logger.error(f"Direct deployment pipeline for {repo}@{branch} failed: {e}")
        raise
