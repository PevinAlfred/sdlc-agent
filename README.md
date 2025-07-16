# AI Agent: Deploy → Monitor → Incident — Suggested Tech Stack

| Aspect                | Recommended Option                                         | Why is this good?                                      |
|-----------------------|------------------------------------------------------------|--------------------------------------------------------|
| **Programming Language** | Python                                                | Simple, flexible, best for AI orchestration.          |
| **LLM**               | Mistral 7B (or Llama 3 8B)                                   | Open-weight, strong for multi-step reasoning.          |
| **LLM Runner & Hosting** | mistrai.ai                              | Runs the model in the cloud and can be called by scripts or an API, no local GPU needed.      |
| **Framework**         | LangChain OSS                                              | Connects LLM, tools, APIs, and workflows.              |
| **IDE**               | VS Code                                                    | Great for Python, virtualenvs, and REST calls.         |
| **Notebook Tool**     | Jupyter Notebooks (or Colab)                                 | Test prompts and logic step by step.                   |
| **Infra as Code**     | Terraform (or Helm)                                          | Automates cloud resources and app deploys.             |
| **Monitoring**        | Prometheus, Grafana APIs                                   | Collects and visualizes metrics; open source.          |
| **Incident Mgmt**     | Jira API (or simple Email/Slack integration)               | Creates tickets or alerts automatically.               |
| **Version Control**   | Git + GitHub                                               | Tracks changes and supports collaboration.             |

### Why Mistral?
- Choosing Mistral 7B here because it is Light weight and less in cost compared to Meta's Llama 3 8B. 
- Llama is overkill for performing multi step chains. 
- Llama can be chosen if the instructions are complex or if code generation is involved.
- Since Mistral is light weight, it has low latency when compared to Llama

### LLM Runners and Hosting methods explored:
- Self Hosted: LLM is freeware but requires a strong CPU build with heavy VRAM ~12GB
- Cloud Hosted: Both paid and free versions of LLM are available, need to pay only for hosting (per token for paid LLM models; per hour for hosting)

## High-Level Design

![HLD Diagram](./docs/design/HLD.jpg)
