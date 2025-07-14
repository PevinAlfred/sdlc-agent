## AI Agent: Deploy → Monitor → Incident — Suggested Tech Stack

| Aspect                | Recommended Option                                         | Why is this good?                                      |
|-----------------------|------------------------------------------------------------|--------------------------------------------------------|
| **Programming Language** | Python                                                | Simple, flexible, best for AI orchestration.          |
| **LLM**               | Mistral 7B or Llama 3 8B                                   | Open-weight, strong for multi-step reasoning.          |
| **LLM Runner & Hosting** | Replicate (pay-as-you-go)                              | Runs the model in the cloud, no local GPU needed.      |
| **Framework**         | LangChain OSS                                              | Connects LLM, tools, APIs, and workflows.              |
| **IDE**               | VS Code                                                    | Great for Python, virtualenvs, and REST calls.         |
| **Notebook Tool**     | Jupyter Notebooks or Colab                                 | Test prompts and logic step by step.                   |
| **Infra as Code**     | Terraform or Helm                                          | Automates cloud resources and app deploys.             |
| **Monitoring**        | Prometheus, Grafana APIs                                   | Collects and visualizes metrics; open source.          |
| **Incident Mgmt**     | Jira API, ServiceNow API, or simple Email/Slack integration | Creates tickets or alerts automatically.               |
| **Version Control**   | Git + GitHub                                               | Tracks changes and supports collaboration.             |
