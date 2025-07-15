# Research Notes

## LLM Automation Learnings (Session Summary)

- **LLM Output Handling:**
  - LLMs often return JSON wrapped in markdown code fences (```json ... ```), even when asked not to.
  - Always strip code fences and whitespace before parsing JSON responses.
  - Use regex to robustly clean LLM output before `json.loads()`.

- **Prompt Engineering:**
  - Be explicit about the required output format (e.g., keys, types, and that steps must be a list).
  - Provide example JSON in the prompt for best results.
  - Even with clear prompts, LLMs may not always follow instructions exactly.

- **Deployment Automation:**
  - Print and inspect the LLM output before using it in automation.
  - Check for key presence and type (e.g., steps as a list) before executing commands.
  - Use robust extraction logic to handle possible nesting or missing keys.

- **Config and Paths:**
  - Prefer relative paths or resolve paths based on script location for portability.
  - Avoid hardcoding absolute paths in code.

- **Best Practices:**
  - Add `__pycache__/` and `.env` to `.gitignore` to keep the repo clean.
  - Document prompt experiments and lessons learned for future reference.
