# Jr Sanzy -- rules for Claude Code

Full spec: docs/PRD.md. Read the section for the current phase before writing code.

## Project
Personal AI assistant. FastAPI backend (backend/), Next.js PWA frontend (frontend/),
Supabase Postgres + Auth. Single user now, multi-user-ready schema.

## Non-negotiable rules
1. All business logic in FastAPI. Next.js renders and calls the API only.
   No Next.js API routes or server actions with logic.
2. All endpoints under /api/v1. Frontend types are generated from /openapi.json
   into frontend/src/lib/api/schema.d.ts. Never hand-write API types.
3. Auth = Supabase JWT as Bearer token. Shortcuts use X-API-Key. Jobs use X-Job-Secret.
4. Supabase = Postgres + Auth only. Access the DB via SQLAlchemy. Enable RLS (no policies)
   on every new table in its migration.
5. Every LLM call goes through app/llm/router.py generate(). Never import a provider SDK
   outside app/llm/providers/.
6. Budget controller checks cost BEFORE each call. Never add code that bypasses it.
7. sensitive=True data (email content) must never reach a free-tier provider.
8. AI output never changes user data directly. It creates a decision; the user approves.
9. Never store secrets in code. Add every new env var to .env.example.
10. Never log tokens, keys, prompts, email snippets or images.
11. No LangGraph, Docker, local models or new dependencies without asking me first.
12. Build only what the current phase lists. Put new ideas in docs/ideas.md.

## Conventions
- Python: type hints everywhere, ruff + mypy clean, services hold logic,
  routers stay thin, Pydantic schemas in app/schemas/.
- TypeScript: strict, no `any`, TanStack Query hooks in src/hooks/.
- Tests: every new service function gets unit tests; every endpoint gets an
  integration test. Use FakeProvider, never real AI calls in tests.
- Commits: Conventional Commits with requirement IDs, e.g.
  feat(food): photo endpoint [FR-FOOD-1].
- Product name is "Jr Sanzy" everywhere.
- Process log: at the end of every session, add an entry to docs/PROCESS_LOG.md with what
  was built, what was verified, the phase's "Done when" status, decisions and blockers.

## Commands
- Backend: cd backend && uv run uvicorn app.main:app --reload
- Backend checks: uv run ruff check && uv run mypy app && uv run pytest
- Migrations: uv run alembic revision --autogenerate -m "..." && uv run alembic upgrade head
- Frontend: cd frontend && npm run dev
- Frontend checks: npm run lint && npx tsc --noEmit && npm test
- API types: npm run gen:api

## Before saying a task is done
Run all checks above, then list which "Done when" items in docs/PRD.md are met
and which are not.
