
from jira import JIRA
from loguru import logger

def create_jira_ticket(jira_url, user, api_token, incident_data, project_key=None):
    """
    Create a Jira ticket for the incident using the jira package.
    project_key: e.g. 'PROJ'. If not provided, will use incident_data['project_key'].
    """
    try:
        logger.info("Creating Jira ticket...")
        jira = JIRA(server=jira_url, basic_auth=(user, api_token))
        key = project_key or incident_data.get("project_key")
        if not key:
            raise ValueError("Jira project key must be provided in incident_data['project_key'] or as project_key.")
        issue_dict = {
            'project': {'key': key},
            'summary': incident_data.get("title", "Incident Detected"),
            'description': incident_data.get("description", "No description provided."),
            'issuetype': {'name': 'Bug'},
        }
        issue = jira.create_issue(fields=issue_dict)
        logger.info(f"Jira ticket created: {issue.permalink()}")
        return issue.permalink()
    except Exception as e:
        logger.error(f"Failed to create Jira ticket: {e}")
        raise
