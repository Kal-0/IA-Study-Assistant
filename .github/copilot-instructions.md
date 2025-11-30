# GitHub Copilot Instructions for IsCoolGPT

These instructions describe how GitHub Copilot should behave inside this repository.

## Project overview

- Backend: Python 3.11, FastAPI, httpx, Pydantic, Uvicorn
- Frontend: React + Vite (JavaScript), `marked` for Markdown rendering
- Infra: Docker (multi-stage), Docker Compose, Render (Docker deploy), GitHub Actions CI
- Purpose: Study assistant that calls two LLM providers:
  - Gemma 3 worker via `GEMMA3_URL`
  - Gemini 2.0 Flash via `GEMINI_API_KEY`

## General style guidelines

- Default language for comments, docstrings and README-like documentation: **Português do Brasil**.
- Keep code clean and explicit; avoid over-abstractions for small features.
- Prefer clear, descriptive names in **snake_case** for Python and **camelCase** for JavaScript.
- When adding new modules, respect the existing structure:
  - Backend code under `app/`
  - React code under `frontend/src/`
  - Tests under `tests/`.

## Backend guidelines (FastAPI)

- Use async endpoints and `httpx.AsyncClient` for external HTTP calls.
- Use Pydantic models (v1 style) for request/response schemas.
- Do **not** hard-code secrets or URLs; always read them from environment variables
  (optionally using helpers already present in the project).
- When adding new endpoints, remember to:
  - Document them briefly via docstrings.
  - Write tests in `tests/` using `TestClient`.
- Keep error messages informative but not verbose with internal details.
- Prefer small service functions in `app/services/` instead of putting logic directly
  inside route handlers.

## Frontend guidelines (React + Vite)

- Components live under `frontend/src/`:
  - Keep `App.jsx` as a high-level composition component.
  - Extract reusable UI pieces into small components.
- Use functional components and React hooks (`useState`, `useEffect`) only.
- Keep the chat behavior consistent:
  - Messages have fields `{ id, role, text, modelId }`.
  - Chat history is stored in `localStorage` using the existing storage key.
- Use the existing `BASE_API_URL` constant and model configuration list when
  introducing new models or endpoints.
- When modifying keyboard behavior, preserve:
  - **Enter** -> send message
  - **Shift+Enter** -> new line

## Testing

- Use `pytest` for backend tests.
- Follow the existing pattern in `tests/test_api.py` when adding tests for new endpoints.
- Tests should be deterministic and should not depend on external LLMs when possible;
  prefer mocking HTTP calls or providing fallbacks.

## Docker / DevOps

- Do not break the multi-stage Dockerfile structure:
  - Stage 1: build frontend (Vite)
  - Stage 2: runtime image for FastAPI + static files.
- If you change the Dockerfile, make sure it still works with `docker compose up --build`.
- Avoid changing the name of the GitHub Actions workflow file (`ci.yml`)
  and its main job unless strictly necessary.

## What Copilot should avoid

- Do not suggest committing `.env`, API keys or secrets.
- Do not introduce new cloud providers or services unless explicitly requested.
- Do not remove CORS configuration or security-related environment variable usage.
- Avoid generating massive boilerplate; focus on what is clearly relevant for IsCoolGPT.

## When in doubt

- Prefer small, incremental changes that fit the existing architecture.
- Follow the conventions already present in the project before introducing new ones.
