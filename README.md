# JobPilot — AI Job Search & Resume Automation Platform

An AI-powered job assistant that discovers new Power BI / Power Platform /
Microsoft Fabric / Data & BI Analyst postings, tailors your resume and
cover letter to each one, scores the match, and either submits the
application automatically or prepares everything and hands you a
"Manual Action Required" screen so finishing it takes under a minute.

## Compliance-first design

Several major job boards' Terms of Service explicitly prohibit automated
scraping and bot-driven applications. Rather than build something that
gets your accounts banned, this project splits job sources into two tiers:

| Tier | Platforms | Behavior |
|---|---|---|
| **Full automation** | Greenhouse, Lever, Ashby, SmartRecruiters, Workday, Microsoft Careers, Google Careers, company career pages | Polled via each platform's own public/official API on a schedule. Auto-apply is attempted on Greenhouse/Lever/Ashby/SmartRecruiters, whose hosted forms are simple enough to fill safely; every other platform lands in Manual Action Required with everything pre-filled. |
| **Manual-assist only** | LinkedIn, Indeed, Dice, ZipRecruiter, Wellfound | Never scraped, never auto-submitted. You paste a posting you found yourself via "Add Job"; it gets the same AI summary/match-score/resume/cover-letter treatment and always ends in Manual Action Required with a direct link back to the posting. |

Even on auto-apply-capable platforms, the automation only clicks the final
Submit button if you've explicitly opted in via
**Profile → Auto-Submit Applications**. By default it fills the form and
waits for your one-click confirmation — reducing manual work to seconds,
not eliminating your final review.

## Architecture

```
apps/
  api/    FastAPI backend — REST API, SQLAlchemy models, Celery tasks, AI services
  web/    Next.js 14 frontend — dashboard, job list/detail, profile & settings
```

**Backend** (`apps/api`)
- `app/models/` — SQLAlchemy models: `UserProfile`, `Job` (shared, deduped
  postings), `UserJob` (per-user match score / status / documents),
  `MasterResume`, `TailoredResume`, `CoverLetter`, `Notification`
- `app/services/job_sources/` — one connector per platform's public API
  (see `docs/JOB_SOURCES.md` for how to configure each)
- `app/services/ai/` — provider-agnostic AI layer (OpenAI / Anthropic /
  Gemini) for job summarization, match scoring, resume tailoring, cover
  letter generation, and interview prep — all with an explicit
  never-fabricate-experience constraint in every prompt
- `app/services/automation/` — Playwright-based auto-apply for ATS
  platforms with structured, fillable forms
- `app/services/notifications/` — email, WhatsApp (Twilio), and Web Push
- `app/tasks/` — Celery Beat runs `scan_all_sources` every
  `JOB_SCAN_INTERVAL_MINUTES` (default 30); each new job fans out into a
  per-user AI pipeline (summarize → score → tailor resume → cover letter →
  auto-apply or manual-action-required → notify)
- `app/api/v1/routers/` — REST endpoints, authenticated via Clerk JWT

**Frontend** (`apps/web`)
- Next.js App Router + TypeScript + Tailwind, Clerk auth, light/dark theme
- `/dashboard` — stat tiles (found today, matches, applied, manual action
  required, submitted, interviews, rejections, saved, favorites) + recent
  job list
- `/jobs` — full searchable/sortable/filterable job list, "Add Job" for
  manual-assist platforms
- `/jobs/[id]` — job detail: AI summary, match breakdown, missing skills,
  tailored resume/cover letter downloads, manual-action steps + one-click
  "Resume Application"
- `/profile` — master resume upload, work history, skills, salary
  expectations, visa/work authorization, notification preferences,
  auto-submit toggle

## Tech stack

Next.js · React · TypeScript · Tailwind · FastAPI · PostgreSQL · Clerk ·
OpenAI/Anthropic/Gemini · Playwright · Celery + Redis · S3/Cloudinary ·
Docker · Vercel (web) · Railway (api)

## Getting started

1. **Copy environment config**
   ```bash
   cp .env.example .env
   # fill in: database creds, Clerk keys, an AI provider key, storage creds
   ```

2. **Start everything**
   ```bash
   docker compose up --build
   ```
   This starts Postgres, Redis, the FastAPI API (`:8000`), a Celery
   worker, Celery Beat (the 30-minute job scanner), and the Next.js
   frontend (`:3000`).

3. **Run migrations**
   ```bash
   docker compose exec api alembic upgrade head
   ```

4. **Configure job sources** — see `docs/JOB_SOURCES.md`. Without any
   tokens configured, connectors simply return zero results; the app
   still works end-to-end via the "Add Job" manual-paste flow.

5. **Set up Clerk** — create an application at clerk.com, add its
   publishable/secret keys and JWKS URL to `.env`.

6. Visit `http://localhost:3000`, sign up, go to **Profile** and upload a
   master resume — tailoring/scoring only runs for users with one on file.

## What's production-depth vs. MVP-depth

This scaffold stands up every layer described in the spec end-to-end and
is safe to run, but a few things are intentionally left thin for a first
iteration rather than over-built speculatively:
- Company-career-page polling (`CompanyPageConnector`) needs a per-user
  list of URLs wired into a settings screen — the connector itself is
  complete.
- ATS auto-apply field-mapping is best-effort (common label patterns); any
  field it can't confidently map always degrades to Manual Action Required
  rather than guessing.
- Predefined-answer autofill for custom application questions
  (`UserProfile.predefined_answers`) is stored and passed through but not
  yet matched against arbitrary question text — today those always route
  to manual action.
- STEM-OPT-friendly detection (`Job.is_stem_opt_friendly`) is a schema
  field without a populated heuristic yet.

## Roadmap (architecture already supports these)

Chrome extension (reuses the same `/jobs/manual` ingestion endpoint) ·
mobile app (same REST API) · AI interview coach (`app/services/ai/interview_prep.py`
already generates questions/answers) · referral finder · recruiter CRM ·
salary insights · networking tracker · daily application analytics
(`UserJob`/`Notification` tables already capture the event stream these
would aggregate).
