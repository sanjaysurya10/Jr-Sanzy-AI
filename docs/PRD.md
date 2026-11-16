> Auto-extracted from docs/PRD.pdf with pdftotext. Multi-column tables are scrambled by the extraction; where this file and the PDF disagree, the PDF is authoritative.

```text
Jr Sanzy — Product Requirements Document (V1)

Jr Sanzy — Product Requirements
Document (V1)

 Nov 15, 2026 · @​ Sanjay surya

1. Overview

Jr Sanzy V1 is a personal AI assistant made of one FastAPI backend and one Next.js
dashboard that runs on the laptop and on the iPhone as a PWA. It ships three AI features:
food photo logging, Gmail job-email triage and a morning briefing. Every AI-proposed
change goes through an approval step, and every model call goes through a budget
controller.

1.1 Problem

Tasks, deadlines, job emails and diet tracking are spread across Gmail, notes and memory.
Nothing pulls them into one place, ranks what matters today, or acts on routine items
without being asked.

1.2 Vision vs V1

The long-term vision is a chief-of-staff AI: a master agent (Jr Sanzy) that supervises
specialist agents, learns routines, and handles routine work with permission. V1 builds the
foundation that vision needs, with real data and real users (one), and nothing speculative.

Area       In V1                                 Later (see section 12)
Dashboard  Briefing card, 4 priority columns,    Life at a glance, goals, opportunity
           activity log, decision centre, usage  radar, finance overview
Phone      widget
AI         PWA + iOS Shortcuts                   Native iOS app (React Native +
Models                                           Expo), HealthKit
           Model router, 3 single-call features  Multi-agent orchestration
                                                 (LangGraph), memory, learning
           Cloud APIs (Gemini first)             Ollama local models as an optional
                                                 provider

                                                 Page 1 of 49
Jr Sanzy — Product Requirements Document (V1)

Area      In V1                                Later (see section 12)
                                               Google Calendar, finance CSV import
Data      Manual tasks, food photos, Gmail
sources   (read-only), wake signals            Rule-based auto-actions, later Level 4
Autonomy  Suggest, then the user approves

1.3 Goals

     One place to see what matters today, on laptop and iPhone, with the same data.
     Three AI features that are useful every day, not demos.
     No AI action changes user data without approval.
     €0 running cost during development, with hard limits on any paid usage.
     A live, documented, tested project that works as a portfolio piece.

1.4 Non-goals for V1

     Native iOS app, App Store release, HealthKit.
     Reading other apps' notifications or app usage on iPhone (iOS does not allow this).
     Local AI models, Docker, multi-agent orchestration, agent group chat, dynamic agent
     creation.
     Finance tracking and investment advice.
     Sending, deleting or modifying emails.
     Guaranteed 24/7 uptime (free tiers sleep).

1.5 Success metrics (targets)

Metric                                         Target
Daily use
Food log round trip                            Dashboard opened on at least 12 of 14 consecutive
Email triage usefulness                        days

                                               Under 15 s from photo to reply when the backend is
                                               awake

                                               At least 70% of suggested tasks approved after
                                               week 2

    Page 2 of 49
Jr Sanzy — Product Requirements Document (V1)

Metric                                         Target

Briefing timing                                Delivered after a genuine wake on at least 10 of 14
                                               days

Unapproved AI changes 0

Paid AI spend                                  Never above the configured budget

Backend test coverage At least 70% of app/services and app/llm

Portfolio                                      Live URL, README with architecture diagram, 2-
                                               minute demo video

2. Users, constraints and principles

V1 has one user, but every user-owned row carries a user_id so the system can support
more users without a schema change.

2.1 User

Sanjay, based in Dublin (timezone Europe/Dublin ), on a Windows laptop and an iPhone.
Uses the dashboard to plan the day, logs food from the phone, and is running a job search
where job emails matter.

2.2 Constraints

Constraint                                             Impact on design

Windows 11 laptop (MSI Modern 15, i5-1334U,            No Docker and no local models in V1. Free at
16 GB RAM, about 4 GB free RAM, about 10               least 30 GB of disk before starting.
GB free disk)

No Mac                                                 No native iOS build in V1. Phone = PWA + iOS
                                                       Shortcuts.

€0 budget during development                           Free tiers only: Vercel, Render, Supabase,
                                                       Gemini free tier, GitHub Actions.

Render free tier sleeps after about 15 min             First request can be slow. Scheduled work is
idle                                                   triggered externally by GitHub Actions.

    Page 3 of 49
Jr Sanzy — Product Requirements Document (V1)

Constraint                                     Impact on design

Supabase free tier pauses inactive projects,   Store results, not raw images or full emails.
500 MB storage

Gemini free tier may use submitted content     Free tier only for non-sensitive data. Email
to improve Google products                     content needs a paid tier.

iOS: no access to other apps' notifications or Wake detection uses Shortcuts

usage                                          automations, not monitoring.

PWA push on iOS needs iOS 16.4+ and Home Notifications work only after install and

Screen install                                 permission.

Gmail OAuth app in testing mode                Refresh tokens may expire after about 7
                                               days. Reconnect flow required.

Free-tier terms change. Check each provider's pricing page when signing up and record
the date in docs/decisions/ .

2.3 Architecture principles (non-negotiable)

These rules go into CLAUDE.md so Claude Code follows them in every session.

  1. All business logic lives in FastAPI. Next.js only renders data and calls the API. No
     Next.js API routes or server actions with logic.

  2. Versioned REST API under /api/v1 . The OpenAPI spec is the contract; the frontend
     uses types generated from it.

  3. Bearer-token auth (JWT). No cookie-only sessions, so a native app can use the same
     API later.

  4. Notifications go through one backend service with channels ( web_push now, apns
     later).

  5. iOS Shortcuts call the same public API with an API key. No special endpoints.
  6. Supabase provides Auth and hosted PostgreSQL only. The backend connects

     through SQLAlchemy as plain Postgres. No Supabase Edge Functions, no business
     logic in database triggers, no direct table access from the frontend.
  7. Every LLM call goes through the model router. Features never import a provider SDK.
  8. Cost rule: no paid service or paid API call without the user's approval. The budget
     controller blocks calls before they happen.

    Page 4 of 49
Jr Sanzy — Product Requirements Document (V1)

 9. Approval rule: any AI-proposed change to user data becomes a decision the user
    approves. Logging is the only thing written without approval.

10. Privacy rule: content marked sensitive (email content) is never sent to a free tier that
    may use it for training.

11. No LangGraph, Docker or local models in V1. Add them only when a concrete feature
    needs them.

12. Scope rule: build only what the current phase lists. New ideas go to section 12, not
    into code.

3. Architecture, stack and repository

One backend, two interfaces (desktop browser and iPhone PWA), one database. External
callers (iOS Shortcuts, GitHub Actions) use the same API with their own credentials.

3.1 Tech stack

Use the latest stable versions at project start and pin them in lockfiles.

Layer        Choice                            Why
             Python 3.12+                      AI ecosystem, FastAPI
Backend      FastAPI + Pydantic v2
language     uv                                Typed, auto OpenAPI spec
             SQLAlchemy 2.x + Alembic
Backend      psycopg 3                         Fast, lockfile, industry
framework    httpx                             standard
                                               Portable Postgres, versioned
Package                                        schema
manager                                        Modern Postgres driver
                                               Async calls to providers and
ORM and                                        Gmail
migrations                                     Verify Supabase access
                                               tokens
DB driver                                      Encrypt OAuth tokens at rest

HTTP client

JWT verification PyJWT

Encryption   cryptography (Fernet)

                                               Page 5 of 49
Jr Sanzy — Product Requirements Document (V1)

Layer          Choice                               Why

Rate limiting  slowapi                              Protect public endpoints

Push           pywebpush                            Web Push with VAPID

Gmail          google-api-python-client, google-auth- Official client
               oauthlib

LLM SDKs       google-genai (Gemini); openai (optional Wrapped by the router only
               second provider)

Backend quality pytest, pytest-asyncio, ruff, mypy  Tests, lint, types

Frontend       Next.js (App Router) + React +       Responsive web + PWA
               TypeScript (strict)

Styling        Tailwind CSS                         Fast, consistent responsive
                                                    layout

Data fetching  TanStack Query                       Caching, refetch, loading
                                                    states

API types      openapi-typescript                   Types generated from

                                                    /openapi.json

Auth client    @supabase/supabase-js                Login, session, access token

Frontend tests Vitest + React Testing Library       Component tests

Database + Auth Supabase (Postgres + Auth)          Free tier, hosted

Hosting        Vercel (frontend), Render (backend)  Free tiers, HTTPS

Scheduler      GitHub Actions cron                  Free, wakes Render

CI             GitHub Actions                       Lint, type check, test on
                                                    every push

3.2 Request paths

     Browser or PWA: Next.js page → fetch with Authorization: Bearer <supabase
     access token> → FastAPI → service → database.
     iOS Shortcut: Shortcut → POST /api/v1/food/photo or /api/v1/wake/signal with
      X-API-Key → FastAPI.

    Page 6 of 49
Jr Sanzy — Product Requirements Document (V1)

       Scheduled job: GitHub Actions cron → POST /api/v1/jobs/<name> with X-Job-
       Secret → FastAPI.
       AI call: service → llm.router.generate() → budget check → privacy check →
       provider → llm_usage row.
       Notification: service → notification_service.send() → Web Push → iPhone or
       browser.

system architecture · 4 callers, 1 gateway

Services also read Gmail through Google's API, and the browser signs in with Supabase
Auth directly before calling the backend.

3.3 Repository structure

One monorepo. Paths below are the source of truth for where code goes.

jr-sanzy/               # Rules for Claude Code (section 11)
├── CLAUDE.md           # Setup, architecture diagram, checklist
├── README.md           # .env, .venv, node_modules, .next,
├── .gitignore
__pycache__             # This document, exported to Markdown
├── docs/               # ADRs: 0001-option-c-architecture.md, ...
│ ├── PRD.md
│ └── decisions/
├── .github/workflows/

    Page 7 of 49
Jr Sanzy — Product Requirements Document (V1)

│ ├── ci.yml                                   # Lint, type check, tests (backend +

frontend)

│ └── jobs.yml                                 # Cron: email-sync, briefing-fallback,

decisions-expire

├── backend/

│ ├── pyproject.toml

│ ├── uv.lock

│ ├── .env.example

│ ├── alembic.ini

│ ├── alembic/versions/

│ ├── app/

│ │ ├── main.py                                # App factory, CORS, routers, error

handlers

│ │ ├── core/

│ │ │ ├── config.py                            # Settings from env (pydantic-settings)

│ │ │ ├── security.py                          # JWT verify, API key verify, job secret

verify

│ │ │ ├── crypto.py                            # Fernet encrypt/decrypt for tokens

│ │ │ ├── errors.py                            # AppError + error codes + handlers

│ │ │ ├── logging.py                           # Structured logs, no PII

│ │ │ └── time.py                              # User-local time helpers (Europe/Dublin)

│ │ ├── db/

│ │ │ ├── base.py                              # Declarative base, UUID + timestamp mixins

│ │ │ └── session.py                           # Engine, session dependency

│ │ ├── models/                                # One file per table (section 5)

│ │ ├── schemas/                               # Pydantic request/response models per

module

│ │ ├── api/

│ │ │ ├── deps.py                              # get_db, get_current_user,

require_api_key(scope), require_job_secret

│ │ │ └── v1/

│││            ├── router.py                   # Includes all v1 routers

│││            ├── health.py

│││            ├── me.py

│││            ├── settings.py

│││            ├── api_keys.py

│││            ├── tasks.py

│││            ├── dashboard.py

│││            ├── food.py

│││            ├── email.py

│││            ├── integrations.py

│││            ├── wake.py

│││            ├── briefing.py

    Page 8 of 49
Jr Sanzy — Product Requirements Document (V1)

│││             ├── decisions.py

│││             ├── activity.py

│││             ├── usage.py

│││             ├── push.py

│││             └── jobs.py

│ │ ├── services/

│ │ │ ├── user_service.py

│ │ │ ├── task_service.py

│ │ │ ├── dashboard_service.py

│ │ │ ├── food_service.py

│ │ │ ├── gmail_client.py

│ │ │ ├── email_triage_service.py

│ │ │ ├── wake_service.py

│ │ │ ├── briefing_service.py

│ │ │ ├── decision_service.py                  # Create, approve, reject, expire +

executor registry

│ │ │ ├── activity_service.py

│ │ │ ├── notification_service.py # Channels: web_push (apns later)

│ │ │ └── job_service.py

│ │ └── llm/

││   ├── router.py                             # generate(), provider chains per task

││   ├── budget.py                             # Budget controller

││   ├── pricing.py                            # Per-model prices + last_verified date

││   ├── errors.py                             # Transient vs permanent error classes

││   ├── providers/

││   │ ├── base.py                             # Provider interface

││   │ ├── gemini.py

││   │ └── openai_provider.py

││   └── prompts/

││              ├── food_estimate.md

││              ├── email_triage.md

││              └── briefing.md

│ └── tests/

│   ├── conftest.py                            # Test DB, fake provider, auth override

│   ├── unit/

│   └── integration/

└── frontend/

   ├── package.json

   ├── next.config.ts

   ├── tailwind.config.ts

   ├── .env.example

   ├── public/

   │ ├── manifest.webmanifest

    Page 9 of 49
Jr Sanzy — Product Requirements Document (V1)

│ ├── sw.js                                    # Service worker: push + offline shell

│ └── icons/                                   # 180, 192, 512 px

└── src/

       ├── app/

       │ ├── layout.tsx

       │ ├── page.tsx                          # Dashboard (home)

       │ ├── login/page.tsx

       │ ├── tasks/page.tsx

       │ ├── food/page.tsx

       │ ├── inbox/page.tsx # Email triage results

       │ ├── decisions/page.tsx

       │ ├── history/page.tsx # Activity log, completed tasks, past

briefings

       │ └── settings/page.tsx

       ├── components/

       │ ├── layout/                           # Sidebar, BottomNav, Header, AuthGuard

       │ ├── dashboard/                        # BriefingCard, PriorityBoard,

PriorityColumn, TaskItem,

       ││                                      # DecisionCentre, ActivityFeed,

FoodSummary, UsageWidget

       │ └── ui/                               # Button, Card, Badge, Modal, Input,

EmptyState

       ├── lib/

       │ ├── api/client.ts                     # fetch wrapper: base URL, bearer token,

error parsing

       │ ├── api/schema.d.ts # Generated by openapi-typescript (do not

edit)

       │ ├── supabase.ts

       │ └── push.ts                           # Subscribe/unsubscribe Web Push

       └── hooks/                              # useTasks, useDashboard, useDecisions, ...

4. Functional requirements

Each requirement has an ID so tests, commits and Claude Code prompts can reference it
(e.g. FR-FOOD-3 ). "Must" means required for V1.

4.1 Auth and identity (AUTH)

     FR-AUTH-1 Login with Supabase Auth, email and password. The frontend stores the
     session with @supabase/supabase-js .

    Page 10 of 49
Jr Sanzy — Product Requirements Document (V1)

       FR-AUTH-2 Every API call from the frontend sends Authorization: Bearer
       <access_token> .
       FR-AUTH-3 get_current_user verifies the JWT signature with the public keys from
       Supabase's JWKS endpoint (SUPABASE_URL/auth/v1/.well-known/jwks.json), plus
       expiry, issuer and audience. Keys are cached for 1 hour and re-fetched once when a
       token carries an unknown key ID (kid), so signing-key rotation doesn't break login
       (legacy projects that still sign with a shared HS256 secret use
       SUPABASE_JWT_SECRET instead). Once the token is verified, the dependency
       extracts its claims, reads sub as auth_user_id , and upserts a row in users on first
       sight.
       FR-AUTH-4 Invalid or expired token → 401 UNAUTHENTICATED . The frontend then
       refreshes the session or redirects to /login .
       FR-AUTH-5 API keys for Shortcuts: created in Settings, shown once, stored as a SHA-
       256 hash with a prefix (first 8 chars) for display. Each key has scopes ( food:write ,
        wake:write ), last_used_at and can be revoked.
       FR-AUTH-6 require_api_key(scope) reads X-API-Key , hashes it, finds a non-
       revoked key with that scope, sets the user, updates last_used_at . Failure → 401 .
       FR-AUTH-7 Job endpoints require X-Job-Secret equal to JOB_SECRET (constant-
       time compare). Jobs act for all users.

 4.2 Tasks (TASK)

       FR-TASK-1 CRUD on tasks. Fields: title (1–200 chars), notes, priority ( critical , high ,
        normal , low ), status ( todo , done , archived ), due_at (optional), source
       ( manual , email , ai_suggestion ), source_ref (e.g. email item id).
       FR-TASK-2 Marking done sets completed_at ; reopening clears it. Both write an
       activity log entry.
       FR-TASK-3 Default sort: priority (critical first), then due_at ascending (nulls last),
       then created_at .
       FR-TASK-4 Overdue = status = todo and due_at before now. Overdue tasks show
       a marker and appear in the briefing.
       FR-TASK-5 Tasks created from approved decisions carry source and source_ref .
       The user can edit them like any task.

    Page 11 of 49
Jr Sanzy — Product Requirements Document (V1)

 4.3 Dashboard (DASH)

       FR-DASH-1 GET /api/v1/dashboard returns everything the home page needs in one
       call: greeting, today's briefing, tasks grouped by priority, pending decision count,
       today's food totals vs targets, the 10 latest activity entries, and AI spend today and
       this month.
       FR-DASH-2 Greeting uses the user's local time: morning 05:00–11:59, afternoon 12:00–
       16:59, evening 17:00–04:59.
       FR-DASH-3 All four priority columns are always visible. Critical gets a stronger colour,
       not more space. Each column shows up to 5 tasks plus a "+N more" link to /tasks?
       priority=… .
       FR-DASH-4 Empty states: each empty column shows a short message, not a blank
       box.
       FR-DASH-5 Mobile (< 768 px): sections stack vertically; priority columns become
       collapsible sections, Critical and High open by default.
       FR-DASH-6 The dashboard refetches on window focus and every 60 s while visible.

 4.4 Model router (LLM)

  The core engine. Every AI feature calls generate() ; nothing else talks to a provider.
       FR-LLM-1 Signature: generate(task: TaskType, prompt: PromptInput, *,

        user_id, sensitive: bool, response_schema: type[BaseModel] | None, images:

       list[bytes] | None) -> LLMResult .
       FR-LLM-2 TaskType enum: food_estimate , email_triage , briefing . Each task
       has a config: provider chain (ordered), model per provider, max_output_tokens ,
       timeout (seconds), whether vision is needed.
       FR-LLM-3 Provider interface ( providers/base.py ): name , is_free_tier ,
        supports_vision , estimate_cost(prompt, images, max_output_tokens) ->
       Decimal , async call(...) -> ProviderResponse (text, input_tokens,
       output_tokens, latency_ms).
       FR-LLM-4 For each provider in the chain, in order: skip if sensitive and
        is_free_tier ; skip if vision needed and not supported; ask the budget controller
       with the estimated cost (blocked → raise BudgetExceeded , do not try further
       providers); call with timeout.

    Page 12 of 49
Jr Sanzy — Product Requirements Document (V1)

       FR-LLM-5 Error classes: transient = timeout, HTTP 429, HTTP 5xx, connection error →
       one retry on the same provider after 2 s, then next provider. Permanent = HTTP
       400/401/403, content refused → stop and raise. All providers failed → raise
        AllProvidersFailed .
       FR-LLM-6 Structured output: when response_schema is set, parse the reply as JSON
       and validate with Pydantic. Invalid → one repair attempt (same provider, prompt
       includes the validation error). Still invalid → raise InvalidModelOutput .
       FR-LLM-7 Every attempt (success or failure) writes an llm_usage row: user, task,
       provider, model, tokens in/out, estimated cost, actual cost, latency, status, error code,
        sensitive flag. Prompt text is never stored.
       FR-LLM-8 Prompts live in app/llm/prompts/*.md with placeholders, loaded at
       startup. No prompt strings inside services.
       FR-LLM-9 Tests use a FakeProvider that returns scripted replies or errors. No real
       API calls in CI.
       FR-LLM-10 Adding a provider (e.g. Ollama later) = one new file in providers/ and a
       config change. No feature code changes.

 4.5 Budget controller (BUDGET)

       FR-BUDGET-1 User settings hold daily_limit_eur and monthly_limit_eur . Default
       both 0.00, which means only free-tier providers can run.
       FR-BUDGET-2 budget.allows(user_id, estimated_cost) returns true only if spent
       today + estimate ≤ daily limit and spent this month + estimate ≤ monthly limit. Spend
       = sum of actual_cost (fallback estimated_cost ) in llm_usage , in the user's
       timezone.
       FR-BUDGET-3 Estimate before the call: input tokens ≈ characters / 4 (+ a fixed per-
       image amount from pricing.py ), plus max_output_tokens , times the model price.
       Free-tier calls estimate €0 but still count towards the call counters shown in the UI.
       FR-BUDGET-4 Limits change only through PATCH /api/v1/settings/budget with a
       user JWT. API keys, jobs and the AI can never change them. Each change writes an
       activity entry.
       FR-BUDGET-5 When a call is blocked: return error code BUDGET_EXCEEDED , write an
       activity entry, and send at most one push notification per day saying which feature
       was blocked.

    Page 13 of 49
Jr Sanzy — Product Requirements Document (V1)

       FR-BUDGET-6 pricing.py holds per-model input/output prices and a
        last_verified date. The usage page warns when last_verified is older than 60
       days.
       FR-BUDGET-7 Backstop: set a hard spending limit in every paid provider's own billing
       console the day the account is created (documented in README).

 4.6 Food logging (FOOD)

       FR-FOOD-1 POST /api/v1/food/photo (API key scope food:write , or user JWT),
       multipart field image , optional note and eaten_at .
       FR-FOOD-2 Validate: JPEG, PNG or HEIC; max 5 MB; else 422 . Convert HEIC to JPEG
       and downscale to a max side of 1024 px before the AI call.
       FR-FOOD-3 Call generate(task=food_estimate, sensitive=False, images=[...],
       response_schema=FoodEstimate) . Schema: items[] of {name,
       estimated_quantity_g, calories_kcal, protein_g, carbs_g, fat_g, confidence 0–1}, plus
        totals and notes .
       FR-FOOD-4 Save a food_logs row with the items (JSONB) and totals. The image is
       not stored in V1.
       FR-FOOD-5 Response includes summary_text for the Shortcut to display, e.g. "About
       620 kcal, 32 g protein. Today: 1,450 / 2,200 kcal."
       FR-FOOD-6 Daily totals vs targets: targets (calories, protein) are entered by the user
       in Settings. V1 does not calculate targets from BMI.
       FR-FOOD-7 Food page: list by day, edit any number, delete an entry, add an entry
       manually without a photo.
       FR-FOOD-8 Results are labelled as estimates in the UI.
       FR-FOOD-9 iOS Shortcut "Log food": Take Photo → Resize Image (1024) → Convert
       Image (JPEG) → Get Contents of URL ( POST , form, header X-API-Key ) → Get
       Dictionary Value summary_text → Show Notification. Documented step by step in
       README.
       FR-FOOD-10 Cold start: the Shortcut first calls GET /api/v1/health and waits for
       200 before posting the photo, so a sleeping Render instance wakes first.

 4.7 Gmail job-email triage (EMAIL)

       FR-EMAIL-1 Connect Gmail from Settings with OAuth 2.0, scope gmail.readonly
       only. The Google Cloud project stays in testing mode with the user as a test user.

    Page 14 of 49
Jr Sanzy — Product Requirements Document (V1)

       FR-EMAIL-2 Store access and refresh tokens encrypted with Fernet
       ( TOKEN_ENCRYPTION_KEY ). Refresh automatically. On refresh failure: mark the
       integration needs_reconnect , show a banner and send one push notification.
       FR-EMAIL-3 Sync job ( POST /api/v1/jobs/email-sync , every 3 hours): fetch
       messages newer than the last sync that match the user's filter query (default: job
       sites and keywords set in Settings). Max 50 messages per run.
       FR-EMAIL-4 Rule pre-filter, no LLM: drop messages from blocked senders; keep only
       allowed senders or keyword matches. Dedupe by Gmail message_id (unique).
       FR-EMAIL-5 Minimal content: send only sender, subject, date and Gmail's snippet to
       the model. Never the full body in V1.
       FR-EMAIL-6 Emails that pass the pre-filter are split by sender before any AI call. Job-
       alert senders (automated listing emails such as LinkedIn or Indeed job alerts,
       matched on the exact sender address in the job_alert_senders setting) →

         generate(task=email_triage, sensitive=False,

       response_schema=EmailTriage) , so the free tier is allowed. Every other sender
       (recruiter replies, personal messages) → sensitive=True : free tiers are skipped;
       with a €0 budget the call is blocked and the email is stored as unscored and scored
       by rules only (FR-EMAIL-12). Output: category ( job_opportunity , interview ,
        deadline , other ), relevance 0–100, reasons (max 3), suggested task {title, priority,
       due_at}.
       FR-EMAIL-7 Relevance uses the career profile from Settings: target roles, skills,
       locations, seniority, keywords to avoid.
       FR-EMAIL-8 Relevance ≥ threshold (default 70, configurable) → create a decision of
       type add_task_from_email . Below threshold → stored, visible in the inbox page, no
       decision.
       FR-EMAIL-9 Approve → task created. Reject → stored as user_label = rejected .
       Approvals and rejections are kept as labelled data for a future classifier (section 12).
       FR-EMAIL-10 The system never sends, deletes, labels or modifies emails.
       FR-EMAIL-11 Email items older than 30 days have snippet cleared (retention); labels
       and scores stay.
       FR-EMAIL-12 Rule-based score for unscored items: +40 if a target role appears in the
       subject, +20 per matching skill or location (max +40), +20 if the sender is a job-alert
       sender, −100 if an avoid keyword appears; clamp to 0–100. Shown in the inbox with a
       "rules only" label. Items at or above the relevance threshold still create a decision.

    Page 15 of 49
Jr Sanzy — Product Requirements Document (V1)

 4.8 Wake detection (WAKE)

       FR-WAKE-1 POST /api/v1/wake/signal (API key scope wake:write ), body
        {signal_type, occurred_at} . Types: sleep_focus_on , sleep_focus_off ,
        alarm_stopped , manual .
       FR-WAKE-2 iOS Shortcuts personal automations send the signals: "When Sleep Focus
       turns on", "When Sleep Focus turns off", "When an alarm is stopped". Each set to run
       without asking where iOS allows it. Setup documented in README.
       FR-WAKE-3 Every signal is stored in wake_events with a decided status: sleep ,
        tentative , confirmed , ignored .
       FR-WAKE-4 Decision logic for a wake-type signal ( *_off , alarm_stopped ):

          1. Already a confirmed wake today (local date) → ignored .
          2. Local time before earliest_wake_time (setting, default 05:30) → tentative .
          3. Time since the last sleep_focus_on is under min_sleep_hours (default 4) →

              tentative .
          4. Otherwise → confirmed .
       FR-WAKE-5 A tentative wake is confirmed by a second wake-type signal at least 30
       minutes later, or by any wake-type signal after earliest_wake_time . A tentative
       wake never triggers a briefing on its own. This covers the 5 a.m. phone call case.
       FR-WAKE-6 manual signals (a "I'm up" button or Shortcut) are always confirmed .
       FR-WAKE-7 On confirmed : trigger the briefing (4.9) if none exists for today.
       FR-WAKE-8 typical_wake_time = median of the last 14 confirmed wakes, shown in
       Settings. V1 uses it for display only; later versions use it for prediction.

 4.8.1 Laptop greeting (DESK)

  When you log in to or unlock the Windows laptop, a local script asks the backend for a
  greeting and reads it aloud once per day. The backend writes the message; the laptop
  speaks it.

       FR-DESK-1 Two new wake signal types: laptop_logon and laptop_unlock . They go
       through the same rules as phone signals (FR-WAKE-4, 5), so a laptop unlock can
       confirm a genuine wake.
       FR-DESK-2 POST /api/v1/wake/signal with include_greeting: true returns,
       besides the wake status: should_speak (bool), greeting_text (e.g. "Good morning,
       Sanjay."), briefing_headline (or null) and dashboard_url .

    Page 16 of 49
Jr Sanzy — Product Requirements Document (V1)

       FR-DESK-3 should_speak is true only when all hold: no laptop greeting has been
       spoken yet today (local date), current local time is outside quiet hours, and the
        laptop_greeting_enabled setting is on. The backend records the spoken greeting in
        wake_events.greeting_spoken = true .
       FR-DESK-4 If this signal confirms the wake and no briefing exists, the briefing is
       generated within the same request with a 20 s limit. If it isn't ready in time,
        briefing_headline is null and the greeting ends with "Your briefing is on the
       dashboard."
       FR-DESK-5 Script desktop/greeter.ps1 , run with Windows PowerShell 5.1
       ( powershell.exe , which includes System.Speech ):

          1. Load the API key (scope wake:write ) from %APPDATA%\JrSanzy\key.xml , saved
             once with Export-Clixml , which encrypts it with Windows DPAPI for the current
             user only.

          2. Call the endpoint with Invoke-RestMethod , 30 s timeout, up to 4 attempts 20 s
             apart (covers Render cold starts and Wi-Fi not yet connected after unlock).

          3. If should_speak : speak greeting_text and briefing_headline with
              System.Speech.Synthesis.SpeechSynthesizer , using the voice named in
              %APPDATA%\JrSanzy\config.json (default: the first installed male English voice),
             then open dashboard_url with Start-Process .

          4. If all attempts fail: exit quietly and write one line to
              %APPDATA%\JrSanzy\greeter.log . Never show error pop-ups.

       FR-DESK-6 Script desktop/install-greeter.ps1 registers one scheduled task "Jr
       Sanzy Greeter" for the current user with two triggers: at log on ( New-
       ScheduledTaskTrigger -AtLogOn ) and on workstation unlock (CIM class
        MSFT_TaskSessionStateChangeTrigger , StateChange = 8 ). Action:

         powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -

       File <path>\greeter.ps1 . A matching uninstall-greeter.ps1 removes it.
       FR-DESK-7 Settings gets a "Laptop greeting" toggle ( laptop_greeting_enabled ,
       default on). README documents setup: create an API key, save it with the one-line
        Export-Clixml command, run the installer.
       FR-DESK-8 New repo folder desktop/ holds greeter.ps1 , install-greeter.ps1 ,
        uninstall-greeter.ps1 and config.example.json . No secrets in the folder.

    Page 17 of 49
Jr Sanzy — Product Requirements Document (V1)

 4.9 Daily briefing (BRIEF)

       FR-BRIEF-1 Triggers: confirmed wake; fallback job at a fixed local time (default 10:00)
       if no briefing exists yet; "Generate now" button.
       FR-BRIEF-2 Inputs: overdue tasks, tasks due today, all critical and high tasks, pending
       decisions, new email items since the last briefing, yesterday's food totals vs targets.
       FR-BRIEF-3 Call generate(task=briefing, sensitive=False) . Inputs passed to the
       model are task titles, counts and dates, not email content. Output: headline (one
       line) and up to 5 bullets , plus a longer full_text .
       FR-BRIEF-4 One briefing per user per local date (unique). "Generate now" replaces it
       and keeps the old version in history.
       FR-BRIEF-5 After generation: push notification with the headline; dashboard card
       shows headline and bullets; "Full briefing" expands full_text .
       FR-BRIEF-6 If the AI call fails or is blocked: build a rule-based briefing (counts and top
       3 task titles) so the user still gets one. Mark it source = fallback .

 4.10 Decision centre (DEC)

       FR-DEC-1 A decision has: type, title, rationale, payload (JSON), source
       ( email_triage , later others), status ( pending , approved , rejected , expired ),
        expires_at (default 7 days), decided_at .
       FR-DEC-2 Executor registry in decision_service.py : {decision_type:
       executor_function} . V1 type: add_task_from_email → creates a task.
       FR-DEC-3 Approve runs the executor and the status change in one database
       transaction. Approving twice is a no-op (idempotent). The user may edit the payload
       (e.g. task title, priority) before approving.
       FR-DEC-4 Reject records the decision and optional reason. Nothing else changes.
       FR-DEC-5 Expire job marks pending decisions past expires_at as expired daily.
       FR-DEC-6 Dashboard shows the pending count and the 3 newest; /decisions lists all
       with approve, edit and reject.
       FR-DEC-7 No code path may change user data based on AI output except through an
       approved decision.

    Page 18 of 49
Jr Sanzy — Product Requirements Document (V1)

 4.11 Activity log (ACT)

       FR-ACT-1 Append-only. Fields: actor ( user , system , llm_router , job:<name> ),
       action (e.g. task.completed ), entity type and id, details (JSON, no secrets, no email
       content), timestamp.
       FR-ACT-2 Written for: task create/complete/delete, decision
       create/approve/reject/expire, briefing generated, food logged, email sync run, budget
       blocked, budget changed, integration connected/disconnected, API key
       created/revoked.
       FR-ACT-3 History page: filter by actor, action and date; search by text in details.

 4.12 Notifications (NOTIF)

       FR-NOTIF-1 Web Push with VAPID keys. The frontend asks permission only after a
       user tap ("Enable notifications") and only when installed as a PWA on iOS.
       FR-NOTIF-2 POST /api/v1/push/subscribe stores the subscription; DELETE
       removes it. Subscriptions returning HTTP 404 or 410 on send are deleted.
       FR-NOTIF-3 notification_service.send(user_id, kind, title, body, url)
       picks channels from the user's subscriptions. Channel interface allows apns later.
       FR-NOTIF-4 Kinds: briefing_ready , decisions_pending (max once per 3 hours),
        budget_blocked (max once per day), integration_needs_reconnect (max once per
       day).
       FR-NOTIF-5 Quiet hours setting (default 23:00–07:00 local): non-briefing notifications
       wait until quiet hours end.

 4.13 Scheduled jobs (JOB)

       FR-JOB-1 Endpoints under /api/v1/jobs/ : email-sync , briefing-fallback ,
        decisions-expire , retention-cleanup . All require X-Job-Secret .
       FR-JOB-2 Every job is idempotent and records a job_runs row (name, started,
       finished, status, counts, error).
       FR-JOB-3 GitHub Actions jobs.yml calls them with curl (retry 3 times, 30 s apart,
       to survive Render cold starts). Every schedule entry sets timezone: "Europe/Dublin"
       (GitHub Actions has supported IANA timezones on cron schedules since March
       2026), so times are local and daylight saving is handled by GitHub. Shortest allowed
       interval is 5 minutes.

    Page 19 of 49
Jr Sanzy — Product Requirements Document (V1)

       FR-JOB-4 GitHub may delay scheduled runs and disables them on inactive
       repositories; the history page shows the last run of each job so a silent stop is visible.

 4.14 Settings (SET)

       FR-SET-1 Profile: display name, timezone (default Europe/Dublin ).
       FR-SET-2 Nutrition targets: calories, protein.
       FR-SET-3 Career profile: target roles, skills, locations, seniority, avoid keywords,
       relevance threshold.
       FR-SET-4 Email filters: allowed senders, blocked senders, job-alert senders (free tier
       allowed), keywords.
       FR-SET-5 Wake: earliest wake time, minimum sleep hours, briefing fallback time, quiet
       hours.
       FR-SET-6 Budget: daily and monthly limits (FR-BUDGET-4).
       FR-SET-7 API keys: create (shown once), list (prefix, scopes, last used), revoke.
       FR-SET-8 Integrations: Gmail status (connected, needs reconnect, disconnected),
       connect and disconnect buttons. Disconnect deletes stored tokens.
       FR-SET-9 Export my data: GET /api/v1/me/export returns one JSON file with every
       row the user owns (all user-owned tables). Button in Settings.
       FR-SET-10 Delete my data: DELETE /api/v1/me (requires typing "DELETE" in the
       confirm dialog) deletes the users row, which cascades to every user-owned table,
       and revokes all API keys and Gmail tokens. The Supabase login itself is removed from
       the Supabase dashboard; V1 does not hold the service-role key needed to do that in
       code.

 4.15 Voice commands (VOICE)

  Voice is the primary way the user talks to Jr Sanzy. V1 does speech-to-text on the device
  (free) and sends text to the backend, so no audio is uploaded or paid for.

       FR-VOICE-1 Three entry points, all ending in the same endpoint POST
       /api/v1/assistant/message with {text, channel} :

          1. Siri + Shortcut "Jr Sanzy" (main path): "Hey Siri, Jr Sanzy" → Dictate Text → Get
             Contents of URL ( X-API-Key , scope assistant:write ) → Speak Text with
              reply_text . Works from the lock screen, AirPods and CarPlay where iOS allows
             Siri.

    Page 20 of 49
Jr Sanzy — Product Requirements Document (V1)

          2. Mic button in the PWA: uses the browser's speech recognition where available; if
             it isn't supported on the device, the button falls back to the keyboard's dictation
             key. No custom audio recording in V1.

          3. Text box on the dashboard (same endpoint, channel = text ).
       FR-VOICE-2 The backend turns text into an intent with
        generate(task=voice_intent, response_schema=VoiceIntent) . TaskType gains
        voice_intent . Intents in V1: add_task , complete_task , list_today ,
        log_food_text , get_briefing , generate_briefing , unknown .
       FR-VOICE-3 Each intent maps to an existing service function (task service, food
       service, briefing service). The voice module adds no business logic of its own.
       FR-VOICE-4 Direct user commands are the user's own intent, so reversible ones
       ( add_task , complete_task , log_food_text ) run immediately, with the action
       named in the reply and an undo available for 10 minutes ( POST
       /assistant/undo/{action_id} ). This does not weaken FR-DEC-7: decisions are for
       changes the AI proposes on its own.
       FR-VOICE-5 Low confidence (< 0.6) or missing fields (e.g. no task title) → no action;
       the reply asks one short question back.
       FR-VOICE-6 reply_text is short and written to be spoken: one or two sentences, no
       lists, numbers written plainly. A longer reply_detail is shown in the PWA.
       FR-VOICE-7 Spoken output in V1: the Shortcut's Speak Text (iOS voices) and the
       browser's built-in speech synthesis in the PWA. The user can pick the deepest
       available system voice. A custom premium voice is a later, paid option and needs
       budget approval.
       FR-VOICE-8 Every message and reply is stored in assistant_messages (text,
       channel, intent, confidence, action taken, action_id, undone_at) and shown in History.
       Transcripts follow the same retention as email snippets (30 days for raw text).
       FR-VOICE-9 log_food_text ("I had two eggs and toast") uses the food estimate
       prompt without an image and saves a food_logs row with source = voice .
       FR-VOICE-10 If AI is blocked or down, a small rule-based parser handles "add task …"
       and "what's on today" so the core commands still work.

    Page 21 of 49
Jr Sanzy — Product Requirements Document (V1)

5. Data model

Seventeen tables in PostgreSQL, all created through Alembic migrations. Every table has
id UUID PRIMARY KEY DEFAULT gen_random_uuid() , created_at and updated_at
( timestamptz , UTC). Every user-owned table has user_id UUID NOT NULL REFERENCES
users(id) ON DELETE CASCADE and an index on it.

Table                                          Key columns (besides id,           Constraints and indexes
                                               timestamps, user_id)
users
user_settings                                  auth_user_id (text), email,        unique(auth_user_id); no
                                               display_name, timezone (default    user_id
api_keys                                       Europe/Dublin )
tasks
food_logs                                      calorie_target,                    unique(user_id)
                                               protein_target_g, career_profile
                                               (JSONB), email_filters
                                               (JSONB), earliest_wake_time
                                               (time), min_sleep_hours
                                               (numeric),
                                               briefing_fallback_time (time),
                                               quiet_start, quiet_end,
                                               daily_limit_eur,
                                               monthly_limit_eur (numeric
                                               10,4), relevance_threshold (int)

                                               name, key_prefix (8), key_hash     unique(key_hash)
                                               (sha256 hex), scopes (text[]),
                                               last_used_at, revoked_at

                                               title, notes, priority (enum),     index(user_id, status, priority,
                                               status (enum), due_at,             due_at)
                                               completed_at, source (enum),
                                               source_ref (UUID null)

                                               eaten_at, items (JSONB),           index(user_id, eaten_at)
                                               total_kcal, total_protein_g,
                                               total_carbs_g, total_fat_g, note,
                                               source ( photo , manual ),
                                               llm_usage_id

    Page 22 of 49
Jr Sanzy — Product Requirements Document (V1)

Table                                          Key columns (besides id,          Constraints and indexes
                                               timestamps, user_id)

integration_tokens                             provider ( gmail ),               unique(user_id, provider)
                                               access_token_enc,
                                               refresh_token_enc, expires_at,
                                               scopes, status ( connected ,
                                               needs_reconnect ,
                                               disconnected ), last_sync_at

email_items                                    gmail_message_id, thread_id,      unique(user_id,
                                               sender, subject, received_at,     gmail_message_id)
                                               snippet (null after 30 days),
                                               category, relevance (int),
                                               reasons (JSONB), triage_status
                                               ( unscored , scored , failed ),
                                               user_label ( approved ,
                                               rejected , null), decision_id

decisions                                      type, title, rationale, payload   index(user_id, status,
                                               (JSONB), source, status           created_at)
                                               (enum), expires_at, decided_at,
                                               reject_reason, result_ref (UUID)

activity_logs                                  actor, action, entity_type,       index(user_id, created_at
                                               entity_id, details (JSONB)        desc); append-only (no
                                                                                 update/delete in code)

llm_usage                                      task, provider, model,            index(user_id, created_at)
                                               input_tokens, output_tokens,
                                               estimated_cost_eur,
                                               actual_cost_eur, latency_ms,
                                               status ( ok , error , blocked ),
                                               error_code, sensitive (bool),
                                               attempt (int)

wake_events                                    signal_type, occurred_at,         index(user_id, local_date)
                                               local_date, status ( sleep ,
                                               tentative , confirmed ,
                                               ignored ), reason

    Page 23 of 49
Jr Sanzy — Product Requirements Document (V1)

Table                                          Key columns (besides id,           Constraints and indexes
                                               timestamps, user_id)               unique(user_id, local_date)
briefings                                                                         where is_current
                                               local_date, headline, bullets
push_subscriptions                             (JSONB), full_text, source ( ai ,  unique(endpoint)
job_runs                                       fallback ), trigger ( wake ,       index(job_name, started_at
budget_changes                                 fallback_job , manual ),           desc); no user_id
                                               version (int), is_current (bool),  audit of every limit change
                                               llm_usage_id

                                               endpoint, p256dh, auth,
                                               user_agent, last_success_at

                                               job_name, started_at,
                                               finished_at, status, counts
                                               (JSONB), error

                                               old_daily, new_daily,
                                               old_monthly, new_monthly

Voice adds a sixteenth table, assistant_messages : text, channel ( siri , pwa_mic ,
text ), intent, confidence, reply_text, action_type, action_id, undone_at; index(user_id,
created_at desc) (FR-VOICE-8). API key scopes also include assistant:write .

Duplicate protection adds a seventeenth table, idempotency_keys : key, endpoint,
status_code, response (JSONB); unique(user_id, key); rows older than 24 hours are
deleted by retention-cleanup (FR-IDEM-1). food_logs also gains image_sha256 with
index(user_id, image_sha256, created_at) for FR-IDEM-2.

5.1 Enums

      task_priority : critical, high, normal, low
      task_status : todo, done, archived
      task_source : manual, email, ai_suggestion
      decision_status : pending, approved, rejected, expired

5.2 Database security

The frontend has the Supabase anon key, and Supabase exposes tables in the public
schema through its REST API by default.

    Page 24 of 49
Jr Sanzy — Product Requirements Document (V1)

       Enable Row Level Security on every table with no policies, so the anon and
       authenticated roles can read and write nothing directly.
       The backend connects with the database connection string (server-side only), which
       bypasses RLS. Every query in services filters by user_id .
       The service role key and database URL never appear in frontend code or
        NEXT_PUBLIC_* variables.
       One Alembic migration enables RLS on each new table; a test checks that every table
       has RLS enabled.

 5.3 Data retention

       Email snippets: cleared after 30 days ( retention-cleanup job).
        llm_usage , activity_logs : kept 12 months, then deleted by the same job.
       Food photos: never stored in V1.
       Disconnecting Gmail deletes its tokens immediately.

 6. API specification

  All endpoints sit under /api/v1 , take and return JSON (except the photo upload), and
  are listed in FastAPI's /openapi.json . Auth column: JWT = user bearer token,
  Key(scope) = X-API-Key , Job = X-Job-Secret , None = public.

 6.1 Conventions

       Error body: {"error": {"code": "TASK_NOT_FOUND", "message": "Task not
       found", "details": {}}} .
       Codes: UNAUTHENTICATED 401, FORBIDDEN 403, NOT_FOUND 404, VALIDATION_ERROR
       422, RATE_LIMITED 429, BUDGET_EXCEEDED 402, AI_UNAVAILABLE 503, INTERNAL
       500.
       Lists: ?limit= (default 20, max 100) and ?cursor= (opaque); response {"items":
       [...], "next_cursor": "..." | null} .
       Timestamps in ISO 8601 UTC; the frontend converts to the user's timezone.
       Rate limits: Key endpoints 30/min per key; login-free endpoints 60/min per IP.
  Duplicate protection (FR-IDEM-1..3). A request can arrive twice: the PWA retries after a
  timeout, or you re-run a Shortcut because the first run looked stuck while Render was
  waking up.

    Page 25 of 49
Jr Sanzy — Product Requirements Document (V1)

     FR-IDEM-1 POST /food/photo , /wake/signal and /assistant/message accept an
     optional Idempotency-Key header. The PWA sends a new UUID per user action and
     reuses it on retries. The backend stores (user_id, key, endpoint, status code,
     response) in idempotency_keys for 24 hours; a repeat returns the stored response
     without doing the work again.
     FR-IDEM-2 Shortcuts can't reuse a key across separate runs, so the backend also
     dedupes by content: the same photo (SHA-256 of the uploaded bytes) for the same
     user within 10 minutes returns the existing food log; the same assistant text within 60
     seconds returns the previous reply. Wake signals are already safe (FR-WAKE-4 rule 1).
     FR-IDEM-3 Tests send each of these requests twice and assert exactly one row is
     created.

6.2 Endpoints

Method Path                                    Auth  Purpose                   Req
                                               None
GET     /health                                      Liveness + DB check:      —
                                               JWT
                                               JWT   {status, db,
                                               JWT
                                                     version}
                                               JWT
GET     /me                                    JWT   Current user + settings   AUTH-3
                                               JWT   summary
                                               JWT
GET     /settings                              JWT   All settings              SET
PATCH   /settings
                                               JWT   Update profile, targets,  SET-1..5
                                               JWT   career profile, filters,
                                                     wake settings

PATCH   /settings/budget                             Change limits (logged)    BUDGET-
                                                                               4

GET     /api-keys                                    List keys (prefix,        AUTH-5
                                                     scopes, last used)

POST    /api-keys                                    Create key; returns full  AUTH-5
                                                     key once

DELETE  /api-keys/{id}                               Revoke                    AUTH-5
GET     /tasks
                                                     List; filters status ,    TASK-1,3
                                                     priority , due_before ,
                                                     q

POST    /tasks                                       Create                    TASK-1
GET     /tasks/{id}
                                                     Get one                   TASK-1

    Page 26 of 49
Jr Sanzy — Product Requirements Document (V1)

Method Path                                    Auth             Purpose                  Req
                                               JWT
PATCH   /tasks/{id}                                             Update fields, complete, TASK-1,2
                                                                reopen

DELETE  /tasks/{id}                            JWT              Delete                   TASK-1
GET     /dashboard                             JWT
POST    /food/photo                            Key(food:write)  Aggregated home data DASH-1
                                               or JWT
                                               JWT              Upload photo →           FOOD-1..5
                                               JWT              estimate → log

POST    /food                                                   Manual entry             FOOD-7
GET     /food
                                                                List; ?date= or ?        FOOD-7
                                                                from=&to=

GET     /food/summary                          JWT              Daily totals vs targets; ? FOOD-6
                                                                date=

PATCH   /food/{id}                             JWT              Edit                     FOOD-7
DELETE  /food/{id}                             JWT
GET     /integrations                          JWT              Delete                   FOOD-7

                                                                Status of each           SET-8
                                                                integration

GET     /integrations/gmail/connect            JWT              Returns Google OAuth     EMAIL-1
                                                                URL (state = signed
                                                                user id + nonce)

GET     /integrations/gmail/callback           None (validates  Exchanges code, stores   EMAIL-1,2
                                               state)           encrypted tokens,
                                                                redirects to /settings

DELETE /integrations/gmail                     JWT              Disconnect, delete       SET-8
                                                                tokens

GET     /email/items                           JWT              Triage results; filters  EMAIL-8
                                                                category ,
                                                                min_relevance ,
                                                                status

POST    /email/sync                            JWT              Run sync now for this    EMAIL-3
                                                                user
                                               Key(wake:write)
POST    /wake/signal                           or JWT           Record signal, return    WAKE-1..7
                                               JWT              decided status

GET     /wake/events                                            Recent signals with      WAKE-3
                                                                statuses

    Page 27 of 49
Jr Sanzy — Product Requirements Document (V1)

Method Path                                    Auth  Purpose                    Req
                                               JWT                              BRIEF-5
GET   /briefing/today                                Current briefing for
                                               JWT   today or null              BRIEF-1,4
POST  /briefing/generate
                                               JWT   Generate or regenerate     BRIEF-4
GET   /briefing/history                        JWT   now                        DEC-6
GET   /decisions                               JWT                              DEC-3
POST  /decisions/{id}/approve                        Past briefings
                                               JWT                              DEC-4
POST  /decisions/{id}/reject                   JWT   List; ?status=pending      ACT-3
GET   /activity
                                               JWT   Body may contain           BUDGET-
GET   /usage/summary                                 edited payload             2,6

GET   /usage                                   JWT   Body {reason?}             LLM-7
GET   /push/vapid-public-key                   JWT                              NOTIF-1
                                                     List; filters actor ,
POST  /push/subscribe                          JWT   action , from , to , q     NOTIF-2
                                               JWT                              NOTIF-2
DELETE /push/subscribe                         JWT   Spend today/month,         NOTIF-3
                                               Job   calls by task and          JOB-1
POST  /push/test                                     provider, limits, pricing
                                               Job   last_verified              JOB-1
POST  /jobs/email-sync
                                                     Raw llm_usage rows         JOB-1
POST  /jobs/briefing-fallback                                                   JOB-1
                                                     Public key for             JOB-4
POST  /jobs/decisions-expire                   Job   subscribing
POST  /jobs/retention-cleanup                  Job
GET   /jobs/runs                               JWT   Save subscription

                                                     Remove subscription

                                                     Send a test notification

                                                     Sync all connected
                                                     users

                                                     Briefing for users past
                                                     fallback time without
                                                     one

                                                     Expire old decisions

                                                     Retention rules (5.3)

                                                     Last run per job

    Page 28 of 49
Jr Sanzy — Product Requirements Document (V1)

6.3 Example: food photo

  POST /api/v1/food/photo
  X-API-Key: jrs_live_xxxxxxxx...
  Content-Type: multipart/form-data

  image=<file>, note="lunch"

  {
      "id": "6f1c...",
      "eaten_at": "2026-11-16T12:41:00Z",
      "items": [
         {"name": "chicken biryani", "estimated_quantity_g": 350, "calories_kcal":

  560,
           "protein_g": 28, "carbs_g": 70, "fat_g": 18, "confidence": 0.6}

      ],
      "totals": {"calories_kcal": 560, "protein_g": 28, "carbs_g": 70, "fat_g":
  18},
      "summary_text": "About 560 kcal, 28 g protein. Today: 1,240 / 2,200 kcal."
  }

6.4 Voice endpoints

Method Path                                    Auth                  Purpose                Req
                                                                                            VOICE-
POST  /assistant/message                       Key(assistant:write)  Text from voice or     1..6
                                               or JWT                keyboard → intent →
                                                                     action → {reply_text,  VOICE-
POST  /assistant/undo/{action_id}              Key(assistant:write)  reply_detail,          4
GET   /assistant/messages                      or JWT                intent, action_id}     VOICE-
                                                                                            8
                                               JWT                   Undo an action within
                                                                     10 minutes

                                                                     Conversation history

7. Frontend, layout and PWA

One Next.js app serves desktop and iPhone. It holds no business logic: it renders API data,
collects input and calls the API.

    Page 29 of 49
Jr Sanzy — Product Requirements Document (V1)

7.1 Pages

Route       Purpose                              Main components
            Email + password login
/login      Dashboard (home)                     LoginForm
/
            All tasks, filters, quick add        Header, BriefingCard, PriorityBoard,
/tasks      Food log by day, manual entry, edit  DecisionCentre, FoodSummary,
/food                                            ActivityFeed, UsageWidget
/inbox      Email triage results
/decisions  Pending and past decisions           TaskFilters, TaskList, TaskItem,
/history                                         TaskForm
/settings   Activity log, completed tasks, past
            briefings, job runs                  DaySelector, FoodSummary,
            All of section 4.14 + usage page     FoodEntryList, FoodEntryForm

                                                 EmailItemList (relevance badge,
                                                 category, reasons)

                                                 DecisionList, DecisionCard (approve,
                                                 edit, reject)

                                                 Tabs: Activity, Completed, Briefings,
                                                 Jobs

                                                 Sections per setting group,
                                                 ApiKeyManager, IntegrationCard,
                                                 NotificationToggle, UsageTable

7.2 Layout

     Desktop (≥ 1024 px): fixed left sidebar (Dashboard, Tasks, Food, Inbox, Decisions,
     History, Settings), header with date, notification bell (pending decisions) and avatar.
     Dashboard grid: BriefingCard full width; PriorityBoard as 4 equal columns; below it a
     3-column row: DecisionCentre, FoodSummary, ActivityFeed; UsageWidget small in
     the header or footer.
     Tablet (768–1023 px): sidebar collapses to icons; priority columns 2 × 2.
     Mobile (< 768 px): no sidebar; bottom navigation with 5 items (Home, Tasks, Food,
     Decisions, More); sections stacked; priority columns as collapsible sections (Critical,
     High open). Minimum tap target 44 px. Safe-area padding for the iPhone notch and
     home bar.

                                                 Page 30 of 49
Jr Sanzy — Product Requirements Document (V1)

       Priority colours: Critical red, High orange, Normal blue, Low green; same column width
       for all.
       Light and dark themes following the system setting.
       Product name in the UI is Jr Sanzy everywhere (not "Jr Sanzi").

 7.3 Data and state

        lib/api/client.ts : one apiFetch(path, options) that adds the base URL
       ( NEXT_PUBLIC_API_URL ) and the bearer token, parses the error body, and throws a
       typed ApiError .
       Types come only from lib/api/schema.d.ts , generated with npx openapi-
       typescript $API_URL/openapi.json -o src/lib/api/schema.d.ts . Never hand-
       write API types.
       TanStack Query hooks in hooks/ ( useDashboard , useTasks , useDecisions ...).
       Mutations invalidate the related queries. Optimistic update for completing a task.
       Loading states show skeletons; errors show a retry message; BUDGET_EXCEEDED and
        AI_UNAVAILABLE show plain explanations.
       Auth: AuthGuard wraps all pages except /login ; it waits for the Supabase session
       and redirects if none.

 7.4 PWA

        public/manifest.webmanifest : name "Jr Sanzy", short_name "Jr Sanzy", start_url
       "/", display "standalone", background_color and theme_color matching the theme,
       icons 192 and 512 px (plus maskable ).
        apple-touch-icon 180 px and apple-mobile-web-app-capable meta tags in
        layout.tsx .
        public/sw.js : handles push (show notification) and notificationclick (open the
       URL in the payload); caches the app shell so the PWA opens offline with a "You're
       offline" state. No caching of API responses in V1.
       Install flow on iPhone: open the HTTPS URL in Safari → Share → Add to Home Screen →
       open from the icon → Settings → "Enable notifications". Requires iOS 16.4 or later.
       PWA install and push only work over HTTPS, so testing on the iPhone starts after
       Phase 5 (deployment) or through a temporary HTTPS tunnel (Cloudflare Tunnel or
       ngrok).

    Page 31 of 49
Jr Sanzy — Product Requirements Document (V1)

 7.5 Accessibility

       Semantic HTML, labelled inputs, visible focus states, colour is never the only signal
       (priority also shown as text), contrast at least 4.5:1.

 8. Security, privacy, cost and non-functional requirements

  Security and cost rules are acceptance criteria, not extras: a phase is not done if it breaks
  one.

 8.1 Security

       SEC-1 Secrets only in environment variables. .env is git-ignored; .env.example lists
       every variable with a placeholder. A pre-commit hook (e.g. gitleaks ) blocks
       committed secrets.
       SEC-2 HTTPS only in deployed environments. CORS allows only the Vercel domain and
        http://localhost:3000 .
       SEC-3 JWT verified on every JWT route (signature, exp , aud ). No endpoint trusts a
        user_id from the request body.
       SEC-4 API keys hashed (SHA-256), shown once, scoped, revocable. Job secret
       compared in constant time.
       SEC-5 OAuth tokens encrypted at rest with Fernet; the key is only in backend env.
       SEC-6 OAuth state parameter signed and checked on callback (prevents CSRF).
       SEC-7 RLS enabled on all tables with no policies (section 5.2).
       SEC-8 Input validation with Pydantic on every endpoint; upload type and size checked
       before processing.
       SEC-9 Rate limiting with slowapi (section 6.1).
       SEC-10 Logs never contain tokens, API keys, email snippets, prompts or images. Log
       user ids, not emails.
       SEC-11 Model output is treated as untrusted data: it is validated against a schema and
       never executed, never used as a URL to call, never used to change permissions or
       budgets.
       SEC-12 Prompt injection: email text can contain instructions. The triage prompt states
       that email content is data, and its output can only produce a decision for the user to
       approve (FR-DEC-7).
       SEC-13 Dependencies: Dependabot enabled for backend/ and frontend/ .

    Page 32 of 49
Jr Sanzy — Product Requirements Document (V1)

8.2 Privacy matrix

Which data may go to which kind of model provider.

Data                                           Free tier (may  Paid  Never sent
                                               train)          tier
Food photo                                     Allowed
Task titles, counts, dates (briefing)          Allowed         Allowed —
Email sender, subject, snippet (all senders    Not allowed
except job alerts)                                             Allowed —
Full email body                                —
                                                               Allowed —

                                                               —     Not sent in

                                                                     V1

OAuth tokens, API keys, settings               —               —     Never

Exception: automated job-alert emails from senders listed in job_alert_senders may go
to the free tier (FR-EMAIL-6). They are generic listings, not private messages.

Check each provider's current data-use terms for its paid tier before enabling it, and
record the result in docs/decisions/ .

8.3 Cost policy

     COST-1 No paid service, plan upgrade or paid API key without the user's explicit
     approval.
     COST-2 Default budget €0.00 daily and monthly: only free-tier providers run.
     COST-3 The budget controller blocks calls before they run (FR-BUDGET-2).
     COST-4 Every paid provider account gets a hard limit in its own billing console (FR-
     BUDGET-7).
     COST-5 Images are downscaled to 1024 px before any vision call; email triage sends
     snippets only; briefings use the cheapest suitable model.
     COST-6 Expected V1 running cost: €0 for hosting; AI spend only if the user raises the
     budget (e.g. for email triage).

    Page 33 of 49
Jr Sanzy — Product Requirements Document (V1)

8.4 Non-functional requirements

ID    Requirement                              Target

NFR-1 API latency, non-AI endpoints,           p95 under 500 ms
             backend awake
                                               30 s per attempt (food), 20 s (triage), 30 s
NFR-2 AI call timeout                          (briefing)

NFR-3 Cold start (Render free)                 Accepted; Shortcuts call /health first
NFR-4 Availability                             Best effort on free tiers
NFR-5 Mobile layout
NFR-6 PWA                                      Usable at 375 px width, no horizontal scroll

NFR-7 Database size                            Installable from Safari; passes Lighthouse
                                               PWA installability checks
NFR-8 Observability
                                               Under 400 MB (80% of Supabase free
NFR-9 Code quality                             tier)

NFR-  Tests                                    Structured JSON logs with request id;
10                                             job_runs and llm_usage visible in the UI

                                               ruff + mypy (strict on app/llm ,
                                               app/services ), ESLint + tsc --noEmit
                                               pass in CI

                                               Backend coverage at least 70% on
                                               services and llm; CI green before merge

9. Phased delivery plan

Thirteen phases (0–11 plus 7b), built in order. Each phase ends with its "Done when" boxes
ticked, CI green and a commit or PR. Don't start the next phase with an unticked box.

Phase 0 — Prep

  1. Free at least 30 GB of disk on the laptop.
  2. Install Git, Python 3.12+, uv, Node.js LTS, VS Code, Claude Code.
  3. Create a GitHub repo jr-sanzy (private until Phase 11).

                                               Page 34 of 49
Jr Sanzy — Product Requirements Document (V1)

    4. Create accounts: Supabase, Vercel, Render, Google AI Studio (Gemini API key). Do not
       add payment methods.

    5. Add this PRD as docs/PRD.md and the CLAUDE.md from section 11.
       Repo created with docs/PRD.md , CLAUDE.md , .gitignore
       All tools install and run from a terminal
       ADR 0001-option-c-architecture.md written

 Phase 1 — Backend skeleton

    1. backend/ with uv, FastAPI app factory in app/main.py , core/config.py (pydantic-
       settings), core/errors.py , core/logging.py .

    2. GET /api/v1/health returning {status, version} .
    3. ruff, mypy, pytest configured; first test for /health .
    4. .github/workflows/ci.yml running lint, type check and tests for the backend.

        uv run uvicorn app.main:app --reload serves /api/v1/health
        /docs shows the OpenAPI page
       CI green on push

 Phase 2 — Frontend skeleton

    1. frontend/ with Next.js (App Router, TypeScript strict, Tailwind, ESLint).
    2. Layout: Sidebar (desktop), BottomNav (mobile), Header.
    3. Dashboard with static placeholder data: BriefingCard, PriorityBoard (4 columns with

       empty states), DecisionCentre, ActivityFeed.
    4. Add frontend lint, type check and tests to CI.

        npm run dev shows the dashboard at localhost:3000
       Layout correct at 375 px, 768 px and 1280 px
       CI green

 Phase 3 — Connect frontend and backend

    1. CORS in FastAPI for localhost:3000 .
    2. lib/api/client.ts and generated schema.d.ts .
    3. Header shows backend status from /health .

       Dashboard shows "Backend: OK" from the real API

    Page 35 of 49
Jr Sanzy — Product Requirements Document (V1)

       Stopping the backend shows an error state, not a crash
        npm run gen:api script regenerates types

 Phase 4 — Database and auth

    1. Supabase project; connection string in backend/.env .
    2. SQLAlchemy base, session, Alembic; migrations for users , user_settings , tasks ,

        activity_logs , api_keys ; RLS enabled on each.
    3. Supabase Auth on the frontend ( /login , AuthGuard); get_current_user in the

       backend (FR-AUTH-1..4).
    4. Tasks CRUD API + /tasks page + real data on the PriorityBoard (FR-TASK, FR-DASH-

       1..4 without AI parts).
    5. Activity log written for task events (FR-ACT-1,2).

       Log in, create, complete and delete tasks; the dashboard updates
       Request without a token returns 401
       Test confirms RLS is enabled on every table
       Integration tests for tasks CRUD pass

 Phase 5 — Deploy

    1. Backend to Render (build with uv, start with uvicorn, env vars set, health check path
        /api/v1/health ).

    2. Frontend to Vercel ( NEXT_PUBLIC_API_URL = Render URL, Supabase public keys).
    3. Update CORS to the Vercel domain; add the Vercel URL to Supabase Auth redirect

       URLs.
    4. Run Alembic migrations against Supabase from CI or a documented manual step.

       Login and tasks work on the live Vercel URL from the laptop
       No secrets in the repo or in NEXT_PUBLIC_* variables except the Supabase anon key
       and URL

 Phase 6 — PWA and notifications

    1. Manifest, icons, Apple meta tags, sw.js (FR section 7.4).
    2. VAPID keys; push_subscriptions table; push endpoints; notification_service

       with the web push channel (FR-NOTIF-1..3).
    3. "Enable notifications" button and "Send test" in Settings.

    Page 36 of 49
Jr Sanzy — Product Requirements Document (V1)

       Installed on the iPhone from Safari, opens full screen from the icon
       Test notification arrives on the iPhone
       Same tasks visible on laptop and iPhone; a change on one shows on the other after
       refresh

 Phase 7 — Model router, budget controller, usage

    1. app/llm/ per FR-LLM-1..10: provider interface, Gemini provider, task configs, error
       classes, structured output with repair, llm_usage table.

    2. Budget controller per FR-BUDGET-1..7, budget_changes table, PATCH
       /settings/budget .

    3. FakeProvider and unit tests: fallback on 429/5xx/timeout, no fallback on 400,
       sensitive skip of free tier, budget block before call, usage rows written.

    4. Usage page in Settings and UsageWidget on the dashboard.
       Unit tests cover every branch in router.py and budget.py
       A real Gemini call from a debug script logs a usage row
       With budget €0, a call to a paid-only chain is blocked and logged as blocked
       Hard limit set in any paid provider console (or no paid provider yet)

 Phase 7b — Voice commands

  Voice comes right after the router because it is the main way the user will use the app.
    1. assistant_messages table; voice_intent task type and prompt; intent → service
       mapping; undo (FR-VOICE-2..6, 8, 10).
    2. POST /assistant/message , undo and history endpoints; assistant:write API key
       scope.
    3. Text box and mic button on the dashboard; spoken reply with browser speech
       synthesis (FR-VOICE-1, 7).
    4. Build the "Jr Sanzy" Siri Shortcut and document it in README.
    5. Unit tests per intent, low-confidence path and rule-based fallback.
       "Hey Siri, Jr Sanzy" → "Add a high priority task to email the recruiter tomorrow" → task
       appears and Siri confirms it
       "What's on today?" gets a spoken one- or two-sentence answer
       Undo removes the last added task
       With AI blocked, "add task buy milk" still works through the rule-based parser

    Page 37 of 49
Jr Sanzy — Product Requirements Document (V1)

 Phase 8 — Food logging

    1. food_logs table, food service, POST /food/photo with HEIC conversion and
       downscaling (FR-FOOD-1..5).

    2. API key creation in Settings (FR-AUTH-5,6, FR-SET-7).
    3. Food page and FoodSummary on the dashboard (FR-FOOD-6..8).
    4. Build the iOS Shortcut (FR-FOOD-9,10) and document it in README with

       screenshots.
       Photo from the iPhone Shortcut returns a summary and appears on the dashboard
       Manual entry, edit and delete work
       Revoked API key gets 401

 Phase 9 — Gmail triage and decision centre

    1. Google Cloud project, OAuth consent screen in testing mode, gmail.readonly
       scope, user added as test user.

    2. integration_tokens , email_items , decisions tables;
       connect/callback/disconnect endpoints; encrypted tokens (FR-EMAIL-1,2).

    3. Sync with pre-filter and dedupe (FR-EMAIL-3,4); triage via router with
        sensitive=True (FR-EMAIL-5..9).

    4. Decision service with executor registry; /decisions page; approve, edit, reject (FR-
       DEC-1..7).

    5. /inbox page; career profile and filter settings.
    6. jobs.yml cron for email-sync and decisions-expire ; job_runs table.

       A real job email becomes a pending decision; approving creates a task
       Rejected items are stored with user_label = rejected
       With budget €0, emails are stored as unscored unless they come from a job-alert
       sender; a test proves no other email reaches a free tier
       Expired refresh token marks the integration needs_reconnect and shows a banner

 Phase 10 — Wake detection and briefing

    1. wake_events table, /wake/signal , decision logic (FR-WAKE-1..8) with unit tests for
       each rule, including the 5 a.m. call case.

    2. briefings table, briefing service with AI and rule-based fallback (FR-BRIEF-1..6).
    3. Push on briefing ready; BriefingCard with "Full briefing" and "Generate now".

    Page 38 of 49
Jr Sanzy — Product Requirements Document (V1)

    4. Cron for briefing-fallback and retention-cleanup ; quiet hours (FR-NOTIF-5).
    5. Build the three Shortcuts automations (FR-WAKE-2) and document them.

       Turning Sleep Focus off in the morning produces one briefing and one notification
       A signal at 05:00 followed by nothing produces no briefing
       With the AI blocked, a fallback briefing still appears
  Laptop greeting (same phase, FR-DESK-1..8):
    1. Add laptop_logon and laptop_unlock signals, include_greeting response fields,
        greeting_spoken column and the laptop_greeting_enabled setting.
    2. Write desktop/greeter.ps1 , install-greeter.ps1 and uninstall-greeter.ps1 .
    3. Unit tests: speaks once per day, silent in quiet hours, silent when disabled, briefing
       timeout path.
       Morning login: laptop speaks the greeting and briefing headline, then opens the
       dashboard
       Unlocking again the same day stays silent
       With Render asleep, the greeting still arrives within about a minute
       With the internet off, nothing pops up and one line is written to the log

 Phase 11 — Hardening and portfolio

    1. Fill test gaps to the NFR-10 target; add rate limiting and the gitleaks hook if missing.
    2. README: what it is, architecture diagram, screenshots, setup steps, Shortcuts setup,

       decisions, cost and privacy rules.
    3. Record a 2-minute demo video (food photo, triage approval, morning briefing).
    4. Make the repo public after a final secrets scan; add it to the CV and LinkedIn.

       Everything in section 1.5 measured once and written in README
       A stranger can run it locally from the README alone
       Repo public, no secrets in history

 10. Testing, CI/CD, deployment and configuration

  Every push runs lint, type checks and tests in GitHub Actions; nothing merges to main on
  a red build.

    Page 39 of 49
Jr Sanzy — Product Requirements Document (V1)

10.1 Testing strategy

Level     What                                 Tools            Rules
                                                                No network;
Unit      Router, budget, wake                 pytest           FakeProvider for AI
          logic, triage pre-filter,
          decision executors,                                   Separate test database
          greeting and time helpers                             (local Postgres or a
                                                                Supabase branch); each
Integration API endpoints with a real          pytest + httpx   test in a rolled-back
                   Postgres                                     transaction
                                               AsyncClient      Mock apiFetch

Frontend  Components:                          Vitest + React   Run before closing Phases
Manual    PriorityBoard, TaskItem,             Testing Library  6, 8, 9, 10
          DecisionCard,
          BriefingCard                         Checklist in
                                               README
          iPhone install, push,
          Shortcuts, Gmail OAuth

Must-have test cases:

     Router: fallback on 429, 5xx and timeout; no fallback on 400; sensitive request skips
     free tier; budget block raises before any call; invalid JSON triggers one repair; every
     attempt writes llm_usage .
     Budget: daily and monthly limits, timezone day boundary, free-tier calls at €0.
     Wake: each rule in FR-WAKE-4 and FR-WAKE-5, including "05:00 call then back to
     sleep" and "two alarms".
     Decisions: approve creates exactly one task even if called twice; reject changes
     nothing else; expired cannot be approved.
     Security: every JWT route returns 401 without a token; another user's task returns
     404; revoked API key returns 401; RLS enabled on all tables.

10.2 CI ( .github/workflows/ci.yml )

  1. Trigger: push and pull request.
  2. Backend job: uv sync → uv run ruff check → uv run mypy app → uv run pytest

     --cov=app (Postgres service container for integration tests).

    Page 40 of 49
Jr Sanzy — Product Requirements Document (V1)

  3. Frontend job: npm ci → npm run lint → npx tsc --noEmit → npm test .
  4. Both must pass.

10.3 Scheduled jobs ( .github/workflows/jobs.yml )

Job                Cron                        Endpoint
                   (Europe/Dublin)
Email sync                                     POST /api/v1/jobs/email-sync
Briefing fallback  0 */3 * * *
                                               POST /api/v1/jobs/briefing-fallback (skips
                   5 10 * * *                  users who already have today's briefing)

Expire decisions   15 3 * * *                  POST /api/v1/jobs/decisions-expire
                   30 3 * * 0                  POST /api/v1/jobs/retention-cleanup
Retention
cleanup

Each step: curl --retry 3 --retry-delay 30 --max-time 90 -X POST -H "X-Job-
Secret: ${{ secrets.JOB_SECRET }}" $API_URL/... .

Schedule syntax used in jobs.yml :

  on:
      schedule:
         - cron: '5 10 * * *'
             timezone: 'Europe/Dublin'
      workflow_dispatch: {}

workflow_dispatch lets you run any job by hand from the Actions tab when testing.

10.4 Deployment

Part     Host                                  Build                   Start / notes
Backend
         Render (free                          pip install uv && uv    uv run uvicorn app.main:app
         web service)                          sync --frozen
                                                                       --host 0.0.0.0 --port $PORT ;
Frontend Vercel                                Default Next.js build,  health check /api/v1/health
                                               root frontend/
                                                                       Production branch main ;
                                                                       preview deploys on PRs

    Page 41 of 49
Jr Sanzy — Product Requirements Document (V1)

Part  Host                                     Build                 Start / notes
                                               Alembic upgrade head
Database Supabase                                                    Run from CI on main or
                                               —                     manually, documented in
Jobs  GitHub Actions                                                 README

                                                                     Secrets: JOB_SECRET , API_URL

Error monitoring. Sentry in both apps ( sentry-sdk[fastapi] in the backend,
@sentry/nextjs in the frontend) with send_default_pii=False , and a before_send
hook that strips request bodies, so no email text, prompts or images leave the backend.
Check the current Sentry free plan limits at sign-up. New env vars: SENTRY_DSN
(backend) and NEXT_PUBLIC_SENTRY_DSN (frontend), added to .env.example .

Backups. Don't rely on provider backups on the Supabase free plan. Once a week, run the
documented pg_dump command from README on the laptop into a folder outside the
repo, and keep the last 4 dumps. At the end of Phases 4 and 11, restore one dump into a
throwaway database to prove the backup works.

10.5 Environment variables

Variable                                       Where                 Purpose
                                               backend
APP_ENV                                        backend               local , production
DATABASE_URL
                                               backend               Supabase Postgres
SUPABASE_URL                                   backend               connection string (server
SUPABASE_JWT_SECRET                            backend               only), ending in ?
CORS_ORIGINS                                                         sslmode=require so the
                                                                     connection is always
                                                                     encrypted

                                                                     Project URL (for JWKS /
                                                                     issuer)

                                                                     Only for legacy HS256
                                                                     projects; leave empty when
                                                                     using JWKS

                                                                     Comma-separated allowed
                                                                     origins

    Page 42 of 49
Jr Sanzy — Product Requirements Document (V1)

Variable                                       Where          Purpose
                                               backend +      Protect job endpoints
JOB_SECRET                                     GitHub secret
                                               backend        Fernet key for OAuth tokens
TOKEN_ENCRYPTION_KEY                           backend        Sign OAuth state
OAUTH_STATE_SECRET                             backend        Gemini provider
GEMINI_API_KEY                                 backend        Second provider, only after
OPENAI_API_KEY                                 (optional)     budget approval
                                               backend        Gmail OAuth
GOOGLE_CLIENT_ID ,
GOOGLE_CLIENT_SECRET ,                         backend        Web Push

GOOGLE_REDIRECT_URI                            backend        Redirect after OAuth
                                               frontend       Backend base URL
VAPID_PUBLIC_KEY ,                             frontend       Supabase Auth client (public
VAPID_PRIVATE_KEY , VAPID_SUBJECT                             by design)

FRONTEND_URL
NEXT_PUBLIC_API_URL

NEXT_PUBLIC_SUPABASE_URL ,

NEXT_PUBLIC_SUPABASE_ANON_KEY

10.6 Git workflow

     Branch per phase ( phase-4-db-auth ), small commits referencing requirement IDs
     ( feat(tasks): CRUD endpoints [FR-TASK-1] ), Conventional Commits style.
     Merge to main through a PR with CI green; tag the end of each phase ( v0.4.0 ).

11. Claude Code workflow

Work one phase per session, plan first, then build, then verify against the phase's "Done
when" list. Claude Code reads CLAUDE.md automatically, so the rules live there and the
details live in docs/PRD.md .

    Page 43 of 49
Jr Sanzy — Product Requirements Document (V1)

 11.1 CLAUDE.md (copy into the repo root)

     # Jr Sanzy — rules for Claude Code

     Full spec: docs/PRD.md. Read the section for the current phase before writing
     code.

     ## Project
     Personal AI assistant. FastAPI backend (backend/), Next.js PWA frontend
     (frontend/),
     Supabase Postgres + Auth. Single user now, multi-user-ready schema.

     ## Non-negotiable rules
     1. All business logic in FastAPI. Next.js renders and calls the API only.

          No Next.js API routes or server actions with logic.
     2. All endpoints under /api/v1. Frontend types are generated from
     /openapi.json

          into frontend/src/lib/api/schema.d.ts. Never hand-write API types.
     3. Auth = Supabase JWT as Bearer token. Shortcuts use X-API-Key. Jobs use X-
     Job-Secret.
     4. Supabase = Postgres + Auth only. Access the DB via SQLAlchemy. Enable RLS
     (no policies)

          on every new table in its migration.
     5. Every LLM call goes through app/llm/router.py generate(). Never import a
     provider SDK

          outside app/llm/providers/.
     6. Budget controller checks cost BEFORE each call. Never add code that
     bypasses it.
     7. sensitive=True data (email content) must never reach a free-tier provider.
     8. AI output never changes user data directly. It creates a decision; the
     user approves.
     9. Never store secrets in code. Add every new env var to .env.example.
     10. Never log tokens, keys, prompts, email snippets or images.
     11. No LangGraph, Docker, local models or new dependencies without asking me
     first.
     12. Build only what the current phase lists. Put new ideas in docs/ideas.md.

     ## Conventions
     - Python: type hints everywhere, ruff + mypy clean, services hold logic,

        routers stay thin, Pydantic schemas in app/schemas/.
     - TypeScript: strict, no `any`, TanStack Query hooks in src/hooks/.
     - Tests: every new service function gets unit tests; every endpoint gets an

        integration test. Use FakeProvider, never real AI calls in tests.

    Page 44 of 49
Jr Sanzy — Product Requirements Document (V1)

     - Commits: Conventional Commits with requirement IDs, e.g.
        feat(food): photo endpoint [FR-FOOD-1].

     - Product name is "Jr Sanzy" everywhere.

     ## Commands
     - Backend: cd backend && uv run uvicorn app.main:app --reload
     - Backend checks: uv run ruff check && uv run mypy app && uv run pytest
     - Migrations: uv run alembic revision --autogenerate -m "..." && uv run
     alembic upgrade head
     - Frontend: cd frontend && npm run dev
     - Frontend checks: npm run lint && npx tsc --noEmit && npm test
     - API types: npm run gen:api

     ## Before saying a task is done
     Run all checks above, then list which "Done when" items in docs/PRD.md are
     met
     and which are not.

 11.2 How to run each phase

    1. Start a fresh Claude Code session for each phase, so old context doesn't pile up.
    2. Enter plan mode and ask for a plan for the phase only. Read the plan; correct anything

       that adds scope, new dependencies or skips tests.
    3. Approve and let it build in small steps, committing after each working step.
    4. Ask it to run all checks and map results to the phase's "Done when" list.
    5. Test the manual items yourself (especially anything on the iPhone).
    6. Tick the boxes in this doc, merge, tag.

 11.3 Prompt template

     We are on Phase <N> — <name> of docs/PRD.md.
     Read CLAUDE.md, docs/PRD.md section 9 Phase <N>, and the requirement sections
     it references (<e.g. 4.4, 4.5>).
     Make a plan for this phase only: files to create or change (with paths from
     section 3.3),
     migrations, endpoints, tests. Do not write code yet.
     Flag anything in the PRD that is unclear or contradictory instead of
     guessing.

  After approving the plan:

    Page 45 of 49
Jr Sanzy — Product Requirements Document (V1)

Implement the plan step by step. After each step run the checks and commit.
At the end, report each "Done when" item for Phase <N> as met or not met,
with evidence.

11.4 Things to watch for in Claude Code's output

     New packages you didn't approve, especially LangGraph, ORMs other than
     SQLAlchemy, or UI kits.
     Logic sneaking into Next.js ( app/api/ folders or server actions).
     Provider SDK imports outside app/llm/providers/ .
     Tests that call real APIs or are skipped.
     Secrets pasted into code or committed .env files.
     Migrations created without RLS.
     "Done" claims without running the checks.

The review is also how you learn the codebase well enough to explain it in interviews: ask
Claude Code to explain any file you don't fully understand before merging it.

12. Roadmap, risks, open questions and glossary

Everything from the original vision that V1 leaves out is kept here, with the condition that
unlocks it.

12.1 Future roadmap

Version Feature                                Unlocked when

V1.1  Google Calendar (read-only) in briefing V1 done; reuses Google OAuth

      and dashboard

V1.1  Email importance classifier trained on 200+ labelled email items

      approve/reject labels (scikit-learn),

      used before the LLM to cut cost

V1.1  Wake-time prediction from                60+ days of confirmed wakes

      wake_events history

V2    Native iOS app with React Native +       Clear need, e.g. HealthKit

      Expo, same API; start in Expo Go (free)

    Page 46 of 49
Jr Sanzy — Product Requirements Document (V1)

Version Feature                                                        Unlocked when

V2          HealthKit sleep data for wake detection Apple Developer Program ($99/year)

                                                                       approved

V2          Memory: preferences and facts in                           A feature that needs past context

            pgvector, retrieved into prompts

V2          Ollama local provider for simple or                        30+ GB free disk, backend run locally

            private tasks

V2          Life at a glance, goals, opportunity radar Data sources exist for each

            on the dashboard

V2          Finance tracking from bank CSV                             V1 stable

            exports (no advice)

V3          Multi-agent orchestration (LangGraph), A workflow needing multi-step state

            event bus between agents (the "group and branching

            chat")

V3          Rule-based auto-approval for routine                       3+ months of decision history

            reversible actions

V3+         Dynamic agent creation, Level 4                            Strong evaluation, audit and
                                                                       permission system in place
            autonomy

12.2 Risks

Risk                                           Likelihood Impact                  Mitigation

Scope creep (adding                            High    Project stalls             Scope rule in CLAUDE.md;
V2/V3 ideas early)                                                                ideas go to docs/ideas.md
                                               Medium  Feature breaks or
Free-tier terms change                                 costs money                Record terms with dates;
                                                                                  provider abstraction;
Render cold starts                             High    Slow or failed food        budget controller
break Shortcuts                                        logs
                                                                                  Health call first; retry in
Gmail tokens expire                            High    Triage stops               Shortcut; accept in free
weekly (testing mode)                                                             stage

                                                                                  Reconnect banner and
                                                                                  notification

    Page 47 of 49
Jr Sanzy — Product Requirements Document (V1)

Risk                                           Likelihood Impact              Mitigation
AI calorie estimates
inaccurate                                     High    Misleading diet data   Labelled as estimates;
Prompt injection via                                                          editable entries
emails                                         Medium Wrong suggestions
                                                                              Snippets only; schema-
Secrets leak to GitHub                         Low     Account abuse, cost    validated output; decisions
                                                                              need approval
Supabase project                               Medium App down
paused for inactivity                                                         gitleaks hook, .gitignore ,
Claude Code produces                           Medium  Hard to debug and      review before public
code you don't                                         explain in interviews
understand                                                                    Daily use; resume from
                                                                              dashboard

                                                                              Review every PR; ask for
                                                                              explanations; small steps

12.3 Open questions

     Decided: job-alert emails use the free tier. Still open: a paid model and monthly budget
     for all other emails? Until decided, those are rule-scored and stored as unscored .
     Default email filter: which senders and keywords count as job emails?
     Is Google's paid Gemini tier free of training use under current terms? Verify before
     enabling it for sensitive data.
     Should food photos be kept (Supabase Storage) for later review, or never stored?
     Is the repo public from Phase 11 or kept private with a demo video only?
     Voice transcripts can contain anything. Allowed on free-tier models by default (the
     user chooses what to say), or treated as sensitive? Decide before Phase 7b.
     Check whether the PWA's browser speech recognition works on your iPhone's iOS
     version; if not, the Siri Shortcut is the voice path inside V1.

12.4 Glossary

Term  Meaning
PWA
      Progressive Web App: a website installable to the
      Home Screen, with push notifications

    Page 48 of 49
Jr Sanzy — Product Requirements Document (V1)

Term          Meaning

Model router  app/llm/router.py ; picks a model provider,
              applies budget and privacy rules, handles fallback

Budget controller Checks estimated cost against daily and monthly
                             limits before every AI call

Decision      An AI-proposed change waiting for the user's
              approval

Sensitive     Data that must not go to free tiers that may use it
              for training

Free tier     A provider plan with no charge, usually with limits
              and different data-use terms

RLS           Row Level Security in Postgres; here used to block

              direct table access from the frontend

VAPID         Keys that identify the server sending Web Push
              notifications

Cold start    Delay while a sleeping free-tier server starts up

ADR           Architecture Decision Record: a short file
              explaining one decision and why

    Page 49 of 49
```
