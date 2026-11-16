# Jr Sanzy

Personal AI assistant: one FastAPI backend and one Next.js dashboard that runs on the
laptop and on the iPhone as a PWA. Full spec in [docs/PRD.md](docs/PRD.md); rules for
Claude Code in [CLAUDE.md](CLAUDE.md); decisions in [docs/decisions/](docs/decisions/).

Status: Phases 0-2 built locally (backend and frontend skeletons). See PRD section 9 and [docs/PROCESS_LOG.md](docs/PROCESS_LOG.md).

## Backend

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 itself).

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

- Health: http://localhost:8000/api/v1/health
- OpenAPI docs: http://localhost:8000/docs

Checks:

```bash
uv run ruff check && uv run mypy app && uv run pytest
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:3000

Checks:

```bash
npm run lint && npx tsc --noEmit && npm test
```
