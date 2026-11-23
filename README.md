# Jr Sanzy

Personal AI assistant: one FastAPI backend and one Next.js dashboard that runs on the
laptop and on the iPhone as a PWA. Full spec in [docs/PRD.md](docs/PRD.md); rules for
Claude Code in [CLAUDE.md](CLAUDE.md); decisions in [docs/decisions/](docs/decisions/).

Status: Phases 0-3 done; Phase 4 (database and auth) built, awaiting a Supabase login to verify end to end. See PRD section 9 and [docs/PROCESS_LOG.md](docs/PROCESS_LOG.md).

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
cp .env.example .env.local
npm install
npm run dev
```

Fill in `.env.local` with your Supabase project URL and publishable key. Dashboard: http://localhost:3000. The header shows "Backend: OK" when the backend is running.

Regenerate API types after any backend API change (backend must be running on port 8000):

```bash
npm run gen:api
```

Checks:

```bash
npm run lint && npx tsc --noEmit && npm test
```
