# Deploying Jr Sanzy (Phase 5)

Backend on Render (free web service), frontend on Vercel (Hobby), database and login on
Supabase. All on free plans with no payment method (see
[ADR 0002](decisions/0002-free-tier-terms.md)). Secrets are typed into each provider's
dashboard by you; nothing secret goes in the repository.

Do the steps in order. Each URL you need is created by the step before it.

## 0. Before you start

- In GitHub: repo Settings -> Branches -> set the default branch to `main`. Render and
  Vercel deploy the default branch unless told otherwise.
- Keep `backend/.env` and `frontend/.env.local` open; several values are copied from them.

## 1. Render: the backend

New -> Web Service -> connect the `Jr-Sanzy-AI` repository, then:

| Field | Value |
|---|---|
| Name | `jr-sanzy-api` |
| Region | Frankfurt (closest to the Supabase project in Ireland) |
| Branch | `main` |
| Root Directory | `backend` |
| Language | Python 3 |
| Build Command | `pip install uv && uv sync --frozen` |
| Start Command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |
| Health Check Path (Advanced) | `/api/v1/health` |

Environment variables (Advanced -> Add Environment Variable):

| Key | Value |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | copy the whole `DATABASE_URL=` value from `backend/.env` (Supabase session pooler, ends `?sslmode=require`) |
| `SUPABASE_URL` | the `SUPABASE_URL=` value from `backend/.env` |
| `CORS_ORIGINS` | `http://localhost:3000` for now; step 3 adds the Vercel URL |

Leave `SUPABASE_JWT_SECRET` unset (the project signs tokens with JWKS keys). Do not set `PORT`.

When the deploy finishes, open `https://<your-service>.onrender.com/api/v1/health`. The
first request after idle takes about a minute (free instances spin down after 15 minutes).
Expected reply: `{"status":"ok","db":"ok","version":"0.1.0"}`.

## 2. Vercel: the frontend

Add New -> Project -> import `Jr-Sanzy-AI`, then:

| Field | Value |
|---|---|
| Framework Preset | Next.js (auto-detected) |
| Root Directory | `frontend` |
| Production Branch | `main` (Settings -> Git, if not already) |

Environment variables (all three are public by design; they are baked in at build time, so
set them before the first deploy or redeploy afterwards):

| Key | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | the Render URL from step 1, no trailing slash |
| `NEXT_PUBLIC_SUPABASE_URL` | from `frontend/.env.local` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | from `frontend/.env.local` (the publishable key) |

Never add the Supabase service-role key or the database URL here.

## 3. Connect the two

1. Render -> your service -> Environment -> set `CORS_ORIGINS` to
   `http://localhost:3000,https://<your-app>.vercel.app` (no trailing slashes, no spaces
   around the comma is fine). Render redeploys automatically.
2. Supabase -> Authentication -> URL Configuration: set Site URL to the Vercel URL and add
   `https://<your-app>.vercel.app/**` and `http://localhost:3000/**` to Redirect URLs.

## 4. Check it works

Open the Vercel URL, sign in, add a task, complete it, delete it. If the first screen says
the backend is unreachable, wait a minute for Render to wake and refresh.

Vercel preview deployments (on pull requests) use other domains, so they cannot call the API
unless you add their URL to `CORS_ORIGINS`.

## Database migrations

Not run on deploy. After adding a migration, apply it yourself before deploying code that
needs it:

```bash
cd backend
uv run alembic upgrade head
```

This uses `DATABASE_URL` from `backend/.env`, which points at Supabase.

## Troubleshooting

- **Browser shows a CORS error:** `CORS_ORIGINS` on Render does not contain the exact Vercel
  origin (scheme and host, no path, no trailing slash).
- **Login works but every API call is 401:** `SUPABASE_URL` on Render does not match the
  project that issued the token.
- **Health shows `"db":"error"`:** wrong `DATABASE_URL`, or the Supabase project is paused
  (free projects pause after a week of inactivity; restore it in the Supabase dashboard).
- **Build fails on Render at `uv sync`:** open the build log; if it complains about the Python
  version, add the environment variable `PYTHON_VERSION` set to a full 3.12.x version.
