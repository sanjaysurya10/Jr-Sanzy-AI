# Jr Sanzy -- process log

Running record of what was built, verified, decided and blocked. Newest phase at the
bottom. Add an entry at the end of every working session.

## 2026-11-16 -- PRD review

- Read all 49 pages of the PRD (13 phases: 0-11 plus 7b).
- Toolchain on the laptop: Git 2.53, uv 0.13, Python 3.12 (via uv), Node 24, npm 11.
  Missing: `gh` CLI, local Postgres. 40 GB free disk.
- PRD contradictions found, and how they will be resolved (the more specific requirement wins):
  - Phase 9 says triage uses `sensitive=True`; FR-EMAIL-6 sends job-alert senders with
    `sensitive=False`. Follow FR-EMAIL-6.
  - `food_logs.source` lists `photo`, `manual`; FR-VOICE-9 needs `voice`. Add it.
  - FR-WAKE-4 wake-type signals omit `laptop_logon` / `laptop_unlock`. Treat both as
    wake-type, per FR-DESK-1.
  - `wake_events.greeting_spoken` and `user_settings.laptop_greeting_enabled` are required
    by FR-DESK but missing from the section 5 tables. Add them.
- Open questions still needing an answer from Sanjay:
  - Voice transcripts: allowed on free-tier models, or sensitive? (before Phase 7b)
  - Phase 4 test database: install Postgres locally, or use a Supabase branch? (Docker is
    not allowed in V1.)

## 2026-11-16 -- Phase 0: Prep

Built:
- `git init` on `main`; `CLAUDE.md` (PRD 11.1), `.gitignore`, `README.md`.
- `docs/PRD.pdf` (authoritative) and `docs/PRD.md` (text extraction; tables scrambled).
- `docs/decisions/0001-option-c-architecture.md`. The "Alternatives considered" section is
  inferred, because the PRD does not record Options A and B.

Done when:
- [x] Repo has `docs/PRD.md`, `CLAUDE.md`, `.gitignore` (local).
- [x] GitHub repo created: https://github.com/sanjaysurya10/Jr-Sanzy-AI (set as `origin`;
      empty until the first push). Note: the PRD names it `jr-sanzy`.
- [ ] All tools install and run -- Git, Python, uv, Node confirmed; VS Code not checked.
- [x] ADR 0001 written (inferred section to be confirmed).

## 2026-11-16 -- Phase 1: Backend skeleton

Built:
- `backend/` with uv; FastAPI app factory (`app/main.py`), `core/config.py`,
  `core/errors.py` (standard error body, PRD 6.1), `core/logging.py` (JSON logs with
  request id, NFR-8).
- `GET /api/v1/health` returning `{status, version}`. The `db` field arrives in Phase 4.
- ruff, mypy (strict), pytest; `.github/workflows/ci.yml` backend job.

Verified locally: ruff clean, mypy clean, 13 tests pass, 98% coverage; a running uvicorn
returned `{"status":"ok","version":"0.1.0"}` and `/docs` returned 200.

Done when:
- [x] `uv run uvicorn app.main:app --reload` serves `/api/v1/health`.
- [x] `/docs` shows the OpenAPI page.
- [x] CI green on push -- backend job passed in run 43926855589 (see first push below).

## 2026-11-16 -- Phase 2: Frontend skeleton

Built:
- Scaffolded `frontend/` with create-next-app: Next.js 16.4, React 19.3, Tailwind 4,
  TypeScript strict, ESLint.
- Layout: `Sidebar` (icons at 768-1023 px, full at 1024 px and up), `BottomNav` (below
  768 px; Home, Tasks, Food, Decisions, More -- More opens Inbox, History, Settings),
  `Header` (local date, bell with pending-decision count, avatar). Safe-area padding,
  light and dark themes from the system setting.
- Dashboard with static placeholder data (`src/lib/placeholder.ts`): `BriefingCard`,
  `PriorityBoard` / `PriorityColumn` / `TaskItem`, `DecisionCentre`, `ActivityFeed`.
  UI primitives: `Card`, `Badge`, `EmptyState`.
- Vitest + React Testing Library; frontend job added to `ci.yml`.

Decisions and deviations:
- Tailwind 4 is configured in CSS (`src/app/globals.css`), so there is no
  `tailwind.config.ts` as listed in PRD 3.3.
- Vitest 5 needs `@types/node` 22 or newer; the scaffold pinned 20. Bumped to 24 to match
  the installed Node, instead of forcing the install.
- `FoodSummary` and `UsageWidget` are left for Phases 8 and 7; Phase 2 does not list them.
- Nav links to `/tasks`, `/food`, `/inbox`, `/decisions`, `/history`, `/settings` return
  404 until those pages are built in later phases.
- CI runs `npx next typegen` before `tsc`, because `next-env.d.ts` is git-ignored.

Verified locally: ESLint clean, `tsc --noEmit` clean (also from a clean checkout state),
12 tests pass, `next build` succeeds. In the browser at each width, no horizontal scroll
and no console errors:
- 375 px: no sidebar, bottom nav shown, one column, Critical and High open, Normal and
  Low collapsed, smallest tap target 44 px.
- 768 px: 64 px icon sidebar, no bottom nav, priority columns 2 x 2.
- 1280 px: 224 px sidebar, four equal columns (239 px each).

Done when:
- [x] `npm run dev` shows the dashboard at localhost:3000.
- [x] Layout correct at 375 px, 768 px and 1280 px.
- [x] CI green -- run 43926855589 on `phase-2-frontend-skeleton` (commit 83a86cd):
      backend and frontend jobs both passed.

## 2026-11-16 -- Commits and first push

- Git identity set for this repo only (`git config` without `--global`).
- `phase-1-backend-skeleton` (c8f386d) and `phase-2-frontend-skeleton` (83a86cd) pushed to
  `origin`. `main` is not pushed; merging into it goes through a PR (PRD 10.6).
- GitHub started a CI run for the Phase 2 branch only. The Phase 1 "CI green on push" box
  is ticked on the strength of that run's backend job, which checks the same backend code.

## 2026-11-16 -- Phase 3: Connect frontend and backend

Built:
- Backend: `CORS_ORIGINS` setting (comma-separated, default `http://localhost:3000`) and
  CORS middleware as the outermost layer, so error responses carry CORS headers too.
- Frontend: `src/lib/api/client.ts` (`apiFetch` + typed `ApiError`), generated
  `src/lib/api/schema.d.ts`, `npm run gen:api`, TanStack Query provider, `useHealth` hook
  and `BackendStatus` in the header.
- `frontend/.env.example` with `NEXT_PUBLIC_API_URL`; `backend/.env.example` gains
  `CORS_ORIGINS`.

Decisions and deviations:
- `apiFetch` does not attach a bearer token yet; there is no session until Phase 4.
- `gen:api` reads `http://localhost:8000/openapi.json`, so the backend must be running.
  The URL is fixed in the script because `$API_URL` does not expand in npm scripts on Windows.
- A missing `NEXT_PUBLIC_API_URL` raises `CONFIG_ERROR` instead of silently falling back
  to localhost, so a misconfigured deploy is visible.
- New packages, both named in PRD 3.1: `@tanstack/react-query`, `openapi-typescript`.

Verified locally: backend ruff, mypy and 20 tests pass (99% coverage); frontend ESLint,
`tsc --noEmit` and 20 tests pass. In the browser: header shows "Backend: OK" from the
real API (also at 375 px, no overflow); with the backend stopped it shows
"Backend: unreachable" and the dashboard still renders, with no error overlay.

Done when:
- [x] Dashboard shows "Backend: OK" from the real API.
- [x] Stopping the backend shows an error state, not a crash.
- [x] `npm run gen:api` regenerates types.

CI: run 43927770255 on `phase-3-connect` (commit 329b22e) passed, backend and frontend jobs.

## Blockers

- None for Phase 3. Phase 4 needs the Supabase project and a test-database choice.
