# Copilot Instructions for refarctoring-swarm-llm

Short, actionable guidance for AI coding agents working in this repo.

1) Big picture
- Purpose: a small multi-agent refactoring pipeline (Auditor → Fixer → Judge) using LLM prompts.
- Entrypoints: `main.py` (simple CLI driver) and the prompt-test script `tests/test_prompts_openrouter.py`.
- Prompt modules live in `src/prompts/` and define three roles: Auditor, Fixer, Judge.

2) Important files (use these as canonical references)
- `main.py` — CLI startup and basic logging call.
- `check_setup.py` — environment sanity checks (.env expectations, Python versions).
- `src/prompts/auditor_prompts.py` — Auditor system prompt + `get_analysis_prompt()` (expects JSON output).
- `src/prompts/fixer_prompts.py` — Fixer system prompt + `get_fix_prompt()` (expects only corrected code in ```python blocks).
- `src/prompts/judge_prompts.py` — Judge prompt + `get_evaluation_prompt()` (expects JSON decision object).
- `src/utils/logger.py` — `log_experiment(...)` contract: must receive `details` containing `input_prompt` and `output_response`.

3) Agent conventions & constraints (do not deviate)
- Auditor: produce ONLY JSON (no extra prose). Follow the schema in `get_analysis_prompt()`.
- Fixer: return ONLY corrected Python source inside a ```python code block. No commentary or additional text.
- Judge: return ONLY JSON with `decision`, `reasoning`, `tests_passed`, `tests_failed`, `next_steps`.
- Severity levels (Auditor): `CRITICAL`, `MAJOR`, `MINOR` — use these exact tokens.

4) Developer workflows & run commands
- Sanity check: `python check_setup.py` (verifies .env and Python version).
- Run the prompt integration test script: `python tests/test_prompts_openrouter.py` (it calls OpenRouter models).
- Quick local run of the pipeline entry: `python main.py --target_dir <path>`.

5) Environment & integrations
- API key expected: `OPENROUTER_API_KEY` in `.env` for `tests/test_prompts_openrouter.py` (see the top of that file for recommended free models).
- `check_setup.py` also looks for `GOOGLE_API_KEY` in `.env` (copy from `.env.example` when needed).
- Primary external dependency: OpenRouter API (requests) — see `requirements.txt` for the exact packages.

6) Logging & telemetry
- Use `src/utils/logger.py::log_experiment(agent_name, model_used, action, details, status)`.
- `details` must include at least `input_prompt` and `output_response` for analysis actions, otherwise the logger raises ValueError.

7) Prompt engineering tips specific to this repo
- Always include file path and original code in prompts (see `get_analysis_prompt()` and `get_fix_prompt()` patterns).
- When asking for machine-readable output prefer the repo's explicit wrappers (Auditor JSON schema, Judge JSON schema).
- For Fixer, request only code in a ```python block — the test harness extracts that block.

8) Tests & expectations
- `tests/test_prompts_openrouter.py` demonstrates how prompts are constructed and how responses are parsed.
- The test script strips code blocks and JSON fences — maintain those exact output formats so parsing remains robust.

9) Common pitfalls discovered in the repo
- `log_experiment` expects a `details` dict; ensure calls pass the correct typed arguments (keys: `input_prompt`, `output_response`).
- The test script expects an `OPENROUTER_API_KEY` variable — missing key short-circuits network calls.

If any section is unclear or you want a different tone/level of detail, tell me which part to expand or adjust.
