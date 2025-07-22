import os
from dotenv import load_dotenv

load_dotenv()

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
JIRA_URL = os.getenv("JIRA_SERVER")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

