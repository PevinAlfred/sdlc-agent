# AI Agent: Deploy → Monitor → Incident — Suggested Tech Stack

| Aspect                | Recommended Option                                         | Why is this good?                                      |
|-----------------------|------------------------------------------------------------|--------------------------------------------------------|
| **Programming Language** | Python                                                | Simple, flexible, best for AI orchestration.          |
| **LLM**               | Mistral 7B (or Llama 3 8B)                                   | Open-weight, strong for multi-step reasoning.          |
| **LLM Runner & Hosting** | mistrai.ai                              | Runs the model in the cloud and can be called by scripts or an API, no local GPU needed.      |
| **Framework**         | LangChain OSS                                              | Connects LLM, tools, APIs, and workflows.              |
| **IDE**               | VS Code                                                    | Great for Python, virtualenvs, and REST calls.         |
| **Infra as Code**     | Terraform (or Helm)                                          | Automates cloud resources and app deploys.             |
| **Monitoring**        | Prometheus                                  | Collects metrics; open source.          |
| **Incident Mgmt**     | Jira API, Email, GitHub Issues              | Creates tickets or alerts automatically.               |
| **Version Control**   | Git + GitHub                                               | Tracks changes and supports collaboration.             |

## High-Level Design

![HLD Diagram](./docs/design/HLD.jpg)
