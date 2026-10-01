# Public software funding directory

This repository is a generated public projection of the private consolidated Grants workspace. Do not edit its data as a separate source. The Grant cron job discovers and rechecks programs, updates the private records, and refreshes this site, Obsidian views and the private Grants notebook. The upsert entry point delegates to that workspace.

Canonical records: `/opt/data/vaults/vaults/Grants and Accelerators/data/opportunities.json`. Refresh entry point: `/opt/data/profiles/grant/scripts/grant-publish.sh`; pass `--force` to refresh every output without forcing Git history. No private decisions or application files are exported here.

To verify the generated public build, run:

    python3 tools/build.py
    python3 -m unittest discover -s tools -v
    python3 tools/build.py --check

Python standard library only. `tools/template.html` owns the directory shell; `assets/site.css` and `assets/directory.js` own the light design and filters. The builder also generates one stable detail page per program under `programs/`. Program links open those pages in a new tab. The build escapes content, validates the exact schema, marks past dates closed, and orders the directory by deadline (unknown last). The default Available view shows potential fits recorded as open, upcoming or rolling; All programs, Closed and Excluded views preserve access to every record. Search and region/type/team filters retain deadline order and are saved in the URL. For reproducible checks use `--as-of YYYY-MM-DD`. A same-day intraday cutoff must be checked by the scanner; the date-only schema cannot encode time zones.

## Editorial rules

Public facts only. Software opportunities in TW, TH, HK and relevant regional competitions. Exclude defense, military, hardware, loans, personal purchases, training-only and residency-only offers. Broad programs appear only for their civilian software scope. No personal biographies, budgets, application plans or IDs. Never commit raw private research or chat output. Never delete existing JSON entries: close old rounds and create distinct IDs for new ones.

All required fields: id, name, type, country, organizer, url, deadline, status, summary, first_seen, last_checked, source_url. Dates are ISO dates; deadline may be null. `last_checked` means the record was reviewed, not necessarily that its official page was successfully reverified; summaries explicitly identify legacy research. `closed` with null deadline is a conservative inactive/watchlist classification, not proof a program ended. Do not infer annual dates. `upcoming` requires a published future program/intake; no opening date is invented.

## Initial migration and scan — 2026-09-18

Seeds were manually selected from the original table and prior public-program research. Loans, registration tasks, computer purchases, training and programs outside the geographic scope were not imported. Excluded legacy rows include Youth Loan, loan-interest subsidy, entrepreneurship training, company registration, Mac purchase, Singapore Tourism Accelerator, UNDP Ocean Challenge, Schmidt Marine and Canadian Ocean Startup Challenge. Hardware/space and purely financial investment/residency rows from research were also excluded.

New official discoveries: AppWorks #33, VentureSpark cohort 2, Cyberport CCMF October 2026 and February 2027 intakes. Checked both Global AI Builders Cup pages: Bangkok has no published round and is recruiting a host; January 2027 applications are upcoming. Its headline prize is a conditional investment, not a cash grant. Official True and Chunghwa pages were also checked. Earlier research supplies some historical seed deadlines; those are labelled, not silently presented as newly verified. Global Fast Track's current page confirms the competition but the September 25 deadline remains from prior research.

The original page mixed public facts with personal banking, registration budgets, and cash-flow strategy. Its full original was backed up outside this public repository before editing. At the initial migration, original styles and main headings remained in the template; personal plan text and financial estimates were replaced with neutral public guidance. This deliberately prioritizes the public-only requirement over verbatim preservation of sensitive non-table text. Original content may still exist in earlier Git history; history was not rewritten.

Monthly operation: search official pages, append/update records, build/test, review public-only diff, commit/push and verify remote HEAD. Refresh the private consolidated Grants notebook through the shared publisher; failed authentication must not prevent the public scan. Report new entries and confirmed deadlines within 60 days. No contacting programs or submitting applications.


## Event research and private preparation

`data/event_details.json` is the validated public projection of research for potential-fit events only. It includes purpose/theme, expected work, company formation and exact company-age rules, sourced eligibility/materials/form fields/steps, research gaps and past examples. Company formation and age are separate columns in the directory. Unknown requirements remain explicitly unverified. Closed rounds are historical; no successor is assumed.

The private grants workspace owns enrichment and shared readiness. `grant_sync.py details` saves research, and `prepare` saves shared facts/materials or a signed per-event check. The common cron publisher regenerates every output, including the expanded private CSV and NotebookLM. No readiness, personal evidence, identifiers or private attachments are exported to this public repository.

The directory links to https://grants.srv1989548.hstgr.cloud/ for open preparation checklists without sign-in or passwords. A shared update recomputes matching events; exact duration/language/format/freshness/new-work and company-age constraints remain separate checks. Private checks never submit applications.


Matt approved open viewing and editing of the hosted event checklists on2026-10-01. No account, password or sign-in is required. Source storage and synchronization remain in the same grants workspace.
