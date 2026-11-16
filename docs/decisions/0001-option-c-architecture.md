# 0001 -- Option C architecture: one FastAPI backend, one Next.js PWA

- Status: accepted
- Date: 2026-11-16

## Context

Jr Sanzy must work on a Windows laptop and an iPhone with the same data, cost nothing to
run during development, and leave the door open for a native iOS app later. There is no
Mac, about 4 GB of free RAM, and no budget (PRD 2.2).

## Decision

One backend, two interfaces, one database (PRD 2.3 and 3):

- All business logic in a FastAPI service under `/api/v1`. The OpenAPI spec is the
  contract; frontend types are generated from it.
- One Next.js app that only renders and calls the API. It serves the desktop browser and
  the iPhone as an installable PWA. No Next.js API routes or server actions with logic.
- Supabase for Auth and hosted Postgres only, reached through SQLAlchemy. RLS on with no
  policies, so nothing reads tables directly from the browser.
- Bearer-token auth (Supabase JWT) for the app, `X-API-Key` for iOS Shortcuts,
  `X-Job-Secret` for GitHub Actions cron. Same public API for every caller.
- Every model call through one router with a budget controller in front of it.

## Alternatives considered

The PRD names this choice "Option C" but does not record the other options. As understood
from its constraints and non-goals, they were:

- A native iOS app first: needs a Mac and the Apple Developer Program. Ruled out by PRD 1.4.
- A full-stack Next.js app with logic in API routes or Supabase Edge Functions: quicker to
  start, but ties logic to the web frontend, so a native app could not reuse it.

Replace this section if the original options were different.

## Consequences

- A native app (V2) can use the same API unchanged.
- Two deployments (Vercel, Render) and a cold-start delay on Render's free tier; Shortcuts
  call `/health` first and scheduled work is triggered by GitHub Actions.
- No Docker, LangGraph or local models in V1.

## Free-tier terms

Record each provider's free-tier terms and the date checked here when the account is
created (PRD 2.2). None created yet.
