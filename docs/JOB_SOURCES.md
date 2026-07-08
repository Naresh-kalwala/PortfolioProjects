# Configuring job source connectors

Each connector polls a platform's own public API — no scraping, no login,
no credentials required for the platform itself.

## Greenhouse (`GREENHOUSE_BOARD_TOKENS`)

Every company on Greenhouse exposes `https://boards-api.greenhouse.io/v1/boards/<token>/jobs`.
The token is the slug in a company's public job board URL, e.g. for
`https://job-boards.greenhouse.io/stripe` the token is `stripe`.

Set a comma-separated list: `GREENHOUSE_BOARD_TOKENS=stripe,figma,notion`

## Lever (`LEVER_COMPANY_SLUGS`)

Same idea: `https://jobs.lever.co/<slug>` → `api.lever.co/v0/postings/<slug>`.

`LEVER_COMPANY_SLUGS=netflix,palantir`

## Ashby (`ASHBY_JOB_BOARD_NAMES`)

`https://jobs.ashbyhq.com/<board-name>` → the public job-board API at
`api.ashbyhq.com/posting-api/job-board/<board-name>`.

## SmartRecruiters (`SMARTRECRUITERS_COMPANY_IDS`)

Find a company's numeric/slug ID from its public careers page URL
(`careers.smartrecruiters.com/<CompanyID>`).

## Workday (`WORKDAY_TENANTS`)

Format: comma-separated `host|tenant|site` triples, e.g.

```
WORKDAY_TENANTS=example.wd1.myworkdayjobs.com|example|Example_Careers
```

Find these three values by opening a company's Workday careers site and
inspecting the network request its own search box makes to `/wday/cxs/...`.

## Microsoft & Google Careers

No configuration needed — both connectors query the same public search API
their own careers sites use in the browser.

## Company career pages (generic)

`CompanyPageConnector` reads schema.org `JobPosting` JSON-LD — the same
structured data Google for Jobs indexes. Pass it a list of specific career
page URLs to poll (wire this up per-user in a future settings screen; the
connector class already accepts `career_page_urls`).

## LinkedIn, Indeed, Dice, ZipRecruiter, Wellfound

**Intentionally not scraped.** Each platform's Terms of Service prohibits
automated scraping and bot-driven applications for individual accounts.
Instead, the dashboard's "Add Job" action lets you paste a posting you
found yourself — see `app/services/job_sources/manual_paste.py`. It still
gets the full AI pipeline (summary, match score, tailored resume, cover
letter); it just always lands in "Manual Action Required" since we never
submit on your behalf on these platforms.

If you later obtain an approved partner/publisher feed for one of these
platforms, drop a new connector into `app/services/job_sources/` following
the same `JobSourceConnector` interface as `greenhouse.py` and register it
in `ACTIVE_CONNECTORS` — no other code changes needed.
