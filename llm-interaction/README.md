# LLM-Interaction: SDLC Agent Demo

This project demonstrates how to build an AI-powered SDLC agent that automates deployment, monitoring, and incident response using Large Language Models (LLMs).

## Features
- **LLM Integration:** Interact with Mistral LLM for deployment planning and incident decisions.
- **Config-driven Deployments:** Reads deployment configs and plans from YAML and LLM output.
- **Automated Actions:** Triggers deploy, monitors system status, and raises incidents based on LLM reasoning.
- **Robust Parsing:** Handles LLM JSON output, including markdown-fenced responses.
- **Logging:** Logs all key actions and LLM decisions for traceability.

## Project Structure
```
llm-interaction/
├── deploy/           # Deployment logic and scripts
├── llm/              # LLM client and prompt logic
├── monitoring/       # System monitoring logic
├── incident/         # Incident management and notifications
├── utils/            # Logging and helpers
├── orchestrator.py   # Main orchestration script
├── config/           # Deployment/config files
├── README.md         # This file
```

## Quick Start
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up your `.env` file:**
   - Add your Mistral API key: `MISTRAL_API_KEY=...`
3. **Prepare your config:**
   - Edit `config/deploy_config.yaml` with your service, version, and env.
4. **Run the orchestrator:**
   ```bash
   python orchestrator.py
   ```

## Example LLM Prompts
- Deployment plan: `You are a DevOps agent. Respond ONLY in JSON (no markdown fences) with this format: {"type":"<strategy>","flags":"<flags>","steps":["<step1>","<step2>"]}.`
- Incident decision: `You are an SDLC agent. Reply ONLY as JSON: {"decision": "yes" or "no"}`

## Research & Experiments
- See `docs/research_assets/` for prompt experiments, flowcharts, and notes.