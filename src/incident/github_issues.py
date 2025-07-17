
from github import Github
from loguru import logger

def create_github_issue(token, incident_data, repo_full_name=None):
    """
    Create a GitHub issue for the incident using PyGithub.
    repo_full_name: e.g. 'owner/repo'. If not provided, will use incident_data['repo'].
    """
    try:
        logger.info("Creating GitHub issue...")
        g = Github(token)
        repo_name = repo_full_name or incident_data.get("repo")
        if not repo_name:
            raise ValueError("Repository name must be provided in incident_data['repo'] or as repo_full_name.")
        repo = g.get_repo(repo_name)
        issue = repo.create_issue(
            title=incident_data.get("title", "Incident Detected"),
            body=incident_data.get("description", "No description provided."),
            labels=[repo.get_label("incident")] if "incident" in [l.name for l in repo.get_labels()] else []
        )
        logger.info(f"GitHub issue created: {issue.html_url}")
        return issue.html_url
    except Exception as e:
        logger.error(f"Failed to create GitHub issue: {e}")
        raise
