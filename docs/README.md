# CodeReviewProject

A minimal code review automation with a security focus. It ingests GitHub PR webhooks, clones the PR head, runs lightweight static checks (Semgrep, Bandit, OSV), aggregates findings, posts comments back to GitHub, and exposes simple metrics via a FastAPI dashboard.

## Prerequisites
- Git installed in the webhook container/host
- Optional CLIs available in PATH inside the webhook container/host:
  - `semgrep`
  - `bandit`

## Configuration
Create a `.env` file (see `ENV.example`):

```
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=changeme
LEARNING_DB=learning.db
# Optional LLM settings
USE_LLM=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Local (without Docker)
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.services.webhook.main:app --host 0.0.0.0 --port 8000
# in another terminal
uvicorn dashboard.main:app --host 0.0.0.0 --port 8080
```

## Docker
```bash
# Build and run both services
docker compose up --build
# Webhook: http://localhost:8000/health
# Dashboard: http://localhost:8080/health
```

## GitHub Webhook Setup
- Payload URL: `http://<your-host>:8000/webhook`
- Content type: `application/json`
- Secret: use `GITHUB_WEBHOOK_SECRET`
- Events: `Pull requests`

## Notes
- If `semgrep` or `bandit` binaries are missing, the pipeline returns empty results for them.
- Metrics persisted in SQLite (`LEARNING_DB`) and surfaced at `GET /metrics/top`.
- LLM is optional: set `USE_LLM=true` and provide `OPENAI_API_KEY` to enable short summaries; on errors or when disabled, static summaries are used.
