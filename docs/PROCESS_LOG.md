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

## 2026-11-23 -- Phase 4: Database and auth (backend half)

Built (branch `phase-4-db-auth`):
- SQLAlchemy base with UUID, timestamp and user-owned mixins; models for `users`,
  `user_settings`, `api_keys`, `tasks`, `activity_logs`; Alembic migration 0001 that enables
  RLS (no policies) on every table including `alembic_version`.
- `TokenVerifier` (FR-AUTH-3): JWKS-based ES256/RS256 verification with signature, expiry,
  issuer and audience checks; HS256 accepted only when `SUPABASE_JWT_SECRET` is set.
- `get_current_user` upserts the user and default settings on first sight.
- Tasks CRUD (`/tasks`), `/me`, `/dashboard` (greeting, tasks grouped by priority with
  totals, 10 latest activity entries), `/health` now reports `db`. Activity log entries for
  task create, complete, reopen and delete.
- Packages (all named in PRD 3.1): sqlalchemy, alembic, psycopg, pyjwt, tzdata.

Decisions and deviations:
- Test database: the existing Postgres 18 service on this laptop needs the `postgres`
  superuser password, which must not be shared in chat. A Supabase branch was priced at
  about EUR 0.01/hour, which breaks COST-1 without approval. Instead a private Postgres
  instance was created at `%LOCALAPPDATA%\JrSanzy\pgdata` on port 5433 (login role
  `jr_sanzy_local`, databases `jr_sanzy_dev` and `jr_sanzy_test`). The existing service is
  untouched. Start it with `pg_ctl -D "%LOCALAPPDATA%\JrSanzy\pgdata" start`; it does not
  auto-start after a reboot.
- `backend/.env` holds a generated local password and is git-ignored. `SUPABASE_URL` there
  is a placeholder until the real project exists.
- The test suite drops and recreates the `public` schema of `TEST_DATABASE_URL` on every run.
- Each test runs in a rolled-back transaction; the real migrations build the schema.
- `app.main:app` is built lazily so importing `create_app` needs no production settings.
- `/health` returns 200 with `db: "error"` when the database is down, so cold-start waits
  still see the server answer.

Verified locally: ruff clean, mypy strict clean, 146 tests pass against real Postgres,
98% coverage.

Done when (frontend half still to build):
- [ ] Log in, create, complete and delete tasks; the dashboard updates.
- [x] Request without a token returns 401 (checked for every non-public route).
- [x] Test confirms RLS is enabled on every table.
- [x] Integration tests for tasks CRUD pass.

## 2026-11-23 -- Phase 4: Database and auth (frontend half, Supabase project)

Supabase:
- Free project "Jr Sanzy" created in the Sanzy Org, region eu-west-1, quoted EUR 0/month
  (cost confirmed with the user first). Project ref `udwdtjoipzihxkyadskj`.
- Its JWKS endpoint serves one ES256 (P-256) key, which the backend verifier supports.
- The database password was not issued to us, so the backend still points at the local dev
  database. The Supabase migration run waits for the user to reset the DB password in the
  dashboard and put the connection string into `backend/.env`.
- Public URL and publishable key are in `frontend/.env.local` (git-ignored) and
  `frontend/.env.example` holds placeholders. `backend/.env` has the real `SUPABASE_URL`.

Built (branch `phase-4-frontend`):
- `lib/supabase.ts` (lazy client), `AuthProvider` + `useAuth`, `AuthGuard`, `/login` with
  `LoginForm`, `SignOutButton` in the header.
- `apiFetch` sends the bearer token; on 401 it refreshes the session once and retries, then
  signs out (FR-AUTH-4).
- Route groups: `app/(app)/` holds the shell (sidebar, header, bottom nav) behind the guard;
  `/login` sits outside it.
- Hooks `useDashboard` (refetch on focus and every 60 s), `useTasks` (cursor pagination),
  `useCreateTask`, `useUpdateTask` (optimistic status change with rollback), `useDeleteTask`.
- `/tasks` page: add, edit, complete, reopen, delete (two-step confirm), filters, search,
  load more. Dashboard now shows real data: greeting, priority columns with true totals,
  real activity feed. Briefing and decisions show empty states until Phases 9-10.
- `lib/api/types.ts` only aliases generated types; `placeholder.ts` is deleted.
- CI: backend job gets a Postgres 17 service container and `TEST_DATABASE_URL` (PRD 10.2).

Verified locally: ESLint, `tsc --noEmit` and `next build` clean; 38 frontend tests pass.
Against the running app: an unauthenticated visit to `/tasks` or `/` redirects to `/login`;
the login form renders without overflow at 375 px with 44 px targets.

NOT verified: signing in and the create/complete/delete flow in the browser, because that
needs the user's Supabase login. No credentials were entered anywhere.

Done when:
- [~] Log in, create, complete and delete tasks; the dashboard updates. Login, create and
      complete confirmed with the user's real Supabase login on 2026-11-23 (see below);
      delete not yet tried in the browser, though covered by integration tests.
- [x] Request without a token returns 401.
- [x] Test confirms RLS is enabled on every table.
- [x] Integration tests for tasks CRUD pass.

Security note for the user: Supabase allows public sign-ups by default. Every valid token
creates a backend user, so after creating the real login, disable "Allow new users to sign
up" in Supabase Auth settings.

## 2026-11-23 -- Phase 4: first real login

The user created their Supabase Auth user and signed in themselves in the browser pane
(no credentials were handled by Claude). Observed afterwards:
- Dashboard loaded with greeting "Good afternoon." and four empty priority columns; header
  showed "Backend: OK".
- Network log: OPTIONS then POST /api/v1/tasks returned 201, PATCH /api/v1/tasks/{id} returned
  200, and /api/v1/dashboard was refetched after each change. All calls were authorised by
  the real Supabase token, so the JWKS verification path works against the live project.
- Activity feed showed "Created" then "Completed" for the user's test task.
- Supabase reports `disable_signup: true`, so public sign-ups are already off.

Dev-only console error: Next.js logs "Could not validate that a segment in your UI has
instant navigation" for `/` and `/tasks`, because the login guard renders "Loading..." before
the pages. Added the documented opt-out `export const instant = false` to
`app/(app)/layout.tsx`. Could not confirm in the pane that the message stopped (the pane's
console log is cumulative); it is dev-only and harmless. Lint, `tsc`, 38 tests and
`next build` pass with the change.

## 2026-11-23 -- Merge to main

- The user approved merging. History was a single linear chain, so `main` was created at the
  tip of `phase-4-frontend` (d2cf24f) with each phase's commits intact; no merge commits.
  Pushed with tags `v0.1.0` (Phases 0-1), `v0.2.0` (Phase 2) and `v0.3.0` (Phase 3).
- `v0.4.0` deliberately not tagged: Phase 4 still has an unticked box (delete not tried in the
  UI, migration not yet run on Supabase).
- CI on `main` (run 45211654332) passed, backend and frontend.
- Findings, for the user to decide:
  - The GitHub repo is **public**, but PRD 9 says private until Phase 11.
  - GitHub's default branch is still `phase-1-backend-skeleton`; it should be `main`
    (repo Settings -> Branches).
  - Commits carry the user's Gmail address as author; that is visible while the repo is public.
- Secret scan of all history: no `.env` files, keys, tokens or real connection strings. Only
  placeholders in `*.env.example` and dummy URLs in tests and CI. The Supabase project ref
  appears in this log; it is not a secret.
- No PRs were used (no `gh` CLI), so PRD 10.6's PR step was skipped at the user's request.

## Blockers

- Needs the user: reset the Supabase DB password and put the connection string into
  `backend/.env` so the migration can run on Supabase; try deleting a task in the UI.
- Decide: make the repo private and switch the default branch to `main` (see Merge to main).
