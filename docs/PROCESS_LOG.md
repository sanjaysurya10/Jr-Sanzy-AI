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
- [ ] CI green on push -- not run yet; nothing has been pushed.

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
- [ ] CI green -- not run yet; nothing has been pushed.

## Blockers

- Git has no `user.name` / `user.email` on this laptop, so nothing is committed or pushed
  yet. This also blocks the "CI green" boxes for Phases 1 and 2.
