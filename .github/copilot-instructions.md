## Copilot / AI-agent instructions for IsCoolGPT

This file gives focused, actionable guidance for AI coding agents working on the IsCoolGPT repository.

High level
- IsCoolGPT is an LLM-backed study assistant (see `README.md`). The architecture is a small web API (FastAPI is referenced in the README), containerized with Docker and intended to be deployed via GitHub Actions to AWS (ECR + ECS).
- Primary responsibilities for an agent: implement or modify the FastAPI backend endpoints, create/update Dockerfile and CI workflow, and wire LLM integration (Gemini API) safely.

Where to look first
- `README.md` — project overview and target infra (FastAPI, Docker, GitHub Actions, AWS ECR/ECS).
- Look for these expected files/locations; they may be missing in this repo snapshot — if they are missing, create them with the standard conventions below and ask the maintainer for preferences:
  - `app/` or `src/` containing FastAPI app, commonly `main.py` or `app/main.py`.
  - `requirements.txt` or `pyproject.toml` for Python deps.
  - `Dockerfile` at repo root for containerization.
  - `.github/workflows/` for CI/CD (deploy workflow should reference ECR/ECS).

Project-specific patterns & conventions
- README language and naming: repository uses Portuguese in README and calls the assistant "IsCoolGPT" — prefer descriptive Portuguese variable/doc strings where appropriate, but keep code comments English if the project already uses English code comments.
- Security: Gemini API keys or other secrets must be stored in GitHub Actions secrets or environment variables — never hardcode credentials.
- Minimal, modular API: prefer small, testable endpoints (single responsibility). When adding routes, follow a module-per-feature pattern (e.g., `app/routes/qa.py`).

Examples (concrete guidance)
- When creating an API entrypoint, add `app/main.py` with a FastAPI instance and an example route:
  - Provide an HTTP POST `/query` or `/ask` that accepts JSON { "question": "..." } and returns an LLM-generated answer.
- When adding Docker support, create a `Dockerfile` that installs requirements and runs `uvicorn app.main:app --host 0.0.0.0 --port 8080`.
- When adding CI/CD, create `.github/workflows/deploy.yml` that builds the Docker image, pushes to ECR, and updates ECS service — follow the README's intent and prompt the maintainer if region/account details are missing.

What to avoid / agent guardrails
- Do not commit any secret values (API keys, AWS credentials). If you need to provide an example, use placeholder names like `GEMINI_API_KEY` or `AWS_ECR_REPO` and reference environment variables.
- Do not assume file names—verify by searching the repo. If files are missing, create minimal stubs and add a short TODO comment referencing the `README.md` and ask the user for confirmation.

If you change behavior
- Add or update a small test (pytest) under `tests/` that exercises the new endpoint or function. If tests don't exist, create one simple smoke test that starts the FastAPI TestClient and asserts a 200 response.
- Update `README.md` with a short usage snippet showing how to run locally (example: `docker build -t iscoolgpt . && docker run -p 8080:8080 iscoolgpt`).

When in doubt
- If the repo lacks implementation files, ask the maintainer: do they want a Python/FastAPI implementation, or are they expecting a prototype with only docs and workflows?
- Always reference `README.md` when deciding infra choices (CI provider, AWS target). If values are missing for deployment (AWS account, region, repo name), create placeholders and clearly mark them as TODO.

Feedback
- After applying changes, briefly describe the edits and ask which piece to implement next (API endpoint, Dockerfile, or CI workflow).
