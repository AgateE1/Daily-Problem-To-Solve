# Daily Data Analytics Problem Picker

A daily practice tracker that automatically picks one Pandas or SQL problem from
LeetCode or DataLemur each morning, across difficulty levels, and logs what
I've completed — all surfaced in Notion.

## What it does

Every day a scheduled job selects one *not-yet-completed* problem at random from
a pool of ~110 curated questions and flags it as today's problem in a Notion
database. I open Notion, solve the problem at the linked source, and tick it off.
The next run clears the old flag and picks a fresh one, so there's always exactly
one problem waiting and nothing repeats until the pool is exhausted.

## How it works

```
GitHub Actions (cron, daily)
        │
        ▼
  Python script (requests)
        │   - queries Notion for problems where Completed = false
        │   - picks one at random
        │   - clears the previous "Today" flag, sets the new one
        ▼
   Notion API  ──►  Notion database (the daily view + my progress)
```

- **Notion database** — one row per problem, with typed properties:
  `Problem` (title), `Category` (SQL / Pandas), `Difficulty` (Easy / Medium / Hard),
  `Skills`, `Resource` (LeetCode / DataLemur), `Link` (direct URL to the problem),
  and two checkboxes: `Today` (set by the script) and `Completed` (set by me).
- **Notion integration** — a scoped internal integration with read + update access
  to the database, authenticated by a token.
- **Python script** — uses `requests` to query the database (with pagination and a
  `Completed = false` filter), choose a random problem, and patch the `Today`
  checkbox. Token and database ID come from environment variables.
- **GitHub Actions** — a cron-triggered workflow runs the script daily in the cloud,
  with the token and database ID stored as encrypted repository secrets. A manual
  "Run workflow" trigger is also enabled for on-demand picks.

## The problem pool

- **LeetCode** — the SQL 50 study plan (50 problems) and the Introduction to Pandas
  study plan (15 problems).
- **DataLemur** — 40+ free SQL interview questions spanning easy aggregations to
  hard window-function problems.

Each row links directly to that exact problem's interactive editor.

## Setup overview

1. Create a Notion database and import the problem set (CSV).
2. Create a Notion internal integration, give it read + update access to the
   database, and copy its token.
3. Add the script and a `.github/workflows/daily.yml` workflow to this repo.
4. Store two repository secrets: `NOTION_TOKEN` and `DATABASE_ID`.
5. Trigger the workflow once to confirm it picks a problem and updates Notion.

```yaml
# .github/workflows/daily.yml (schedule excerpt)
on:
  schedule:
    - cron: "0 5 * * *"   # 05:00 UTC daily
  workflow_dispatch:        # manual run button
```

## Daily use

1. Open the **Today** view in Notion (filtered to `Today` is checked).
2. Click the **Link** to open the problem and solve it.
3. Tick **Completed** when done — it leaves the pool and won't be picked again.

## Skills demonstrated

- **API integration** — Notion REST API: token auth, filtered + paginated queries,
  writing updates back via property patches.
- **Workflow automation (CI/CD)** — scheduled GitHub Actions pipeline running a
  Python job in the cloud, configured entirely through code.
- **Python scripting** — `requests`-based API client with pagination, randomized
  selection, and environment-variable configuration.
- **Data management in Notion** — relational-style database design with typed
  properties, CSV import, and filtered views for state tracking.
- **Secrets management** — credentials kept out of source code via environment
  variables and encrypted GitHub secrets, with token rotation.

## Notes

A personal learning project — a working end-to-end tool rather than a
production system. Built to make daily SQL and Pandas practice automatic and
self-tracking
