# Prompt Experiments

## 1. Basic LLM Prompt
**Prompt:**
```
Should I deploy version 2.1 to production?
```
**Result:**
LLM returns a plain text answer.

---

## 2. Yes/No Decision as JSON
**Prompt:**
```
You are an SDLC agent. Reply ONLY as JSON: {"decision": "yes" or "no"}
The system status is: FAIL.
```
**Result:**
LLM sometimes returns JSON, sometimes wraps it in markdown code fences (```json ... ```), requiring code to strip fences before parsing.

---

## 3. Deployment Plan as JSON (with steps)
**Prompt:**
```
You are a DevOps agent. Respond ONLY in JSON (no markdown fences) with this format: {"type":"<strategy>","flags":"<flags>","steps":["<step1>","<step2>"]}.
Service: my-service, Version: 1.0.0, Env: staging. Suggest a deployment plan.
```
**Result:**
LLM sometimes still returns markdown-fenced JSON. Regex added to strip code fences before parsing. Steps are now reliably a list.

---

## 4. Lessons Learned
- LLMs often wrap JSON in markdown code fences, even when instructed not to.
- Always strip code fences and whitespace before parsing JSON.
- Be explicit in prompt about required keys and types (e.g., steps as a list).
- Print and inspect LLM output structure before using in automation.
