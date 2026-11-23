# 0002 -- Free-tier terms checked at sign-up

- Status: accepted
- Date checked: 2026-11-23 (PRD 2.2: free-tier terms change; recheck before relying on them)

All three providers are used on their free plans with no payment method on file (COST-1).

## Render (backend, free web service)

Source: https://render.com/docs/free

- Spins down after 15 minutes without inbound traffic; spinning back up takes about one
  minute. This is why Shortcuts call `/api/v1/health` first (FR-FOOD-10) and why scheduled
  jobs retry (FR-JOB-3).
- 750 free instance hours per workspace per calendar month, which covers one always-on
  service; the service only consumes hours while running.
- Ephemeral filesystem: nothing written locally survives a restart. Jr Sanzy stores no
  files locally.
- Outbound bandwidth and build minutes are capped; with no payment method Render suspends
  free services for the rest of the month instead of billing.
- Render's own free Postgres expires after 30 days, so it is not used. Supabase holds the data.

## Vercel (frontend, Hobby plan)

Source: https://vercel.com/docs/plans/hobby (page last updated 2026-11-12)

- Free, no billing cycle; exceeding a limit means waiting for it to reset rather than
  being charged. Relevant limits: 100 GB fast data transfer, 1,000,000 CDN requests,
  100 deployments per day, 200 projects.
- Hobby is for personal, non-commercial use, which fits this project.

## Supabase (database and auth, free plan)

Source: https://supabase.com/pricing

- Free projects are paused after 1 week of inactivity (risk R-5 in PRD 12.2).
- Limit of 2 active projects. This account already has two active: another app and Jr Sanzy.
  A third free project cannot be created without pausing one.
- 500 MB database, 50,000 monthly active users, 5 GB egress.
- No managed daily backups on the free plan (Pro has 7 days), hence the weekly `pg_dump`
  in PRD 10.4.

## Not enabled because it is paid

- Supabase leaked-password protection (Pro plan feature).
- Render paid instances, Vercel Pro, Supabase branches (about EUR 0.01 per hour while they exist).
