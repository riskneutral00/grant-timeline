# Public software funding directory

Edit `data/opportunities.json`, then run:

    python3 tools/build.py
    python3 -m unittest discover -s tools -v
    python3 tools/build.py --check

Python standard library only. `tools/template.html` owns non-table content. The build escapes content, validates the exact schema, marks past dates closed, and sorts open/upcoming together by deadline (unknown last), followed by rolling and closed. For reproducible checks use `--as-of YYYY-MM-DD`. A same-day intraday cutoff must be checked by the scanner; the date-only schema cannot encode time zones.

## Editorial rules

Public facts only. Software opportunities in TW, TH, HK and relevant regional competitions. Exclude defense, military, hardware, loans, personal purchases, training-only and residency-only offers. Broad programs appear only for their civilian software scope. No personal biographies, budgets, application plans or IDs. Never commit raw private research or chat output. Never delete existing JSON entries: close old rounds and create distinct IDs for new ones.

All required fields: id, name, type, country, organizer, url, deadline, status, summary, first_seen, last_checked, source_url. Dates are ISO dates; deadline may be null. `last_checked` means the record was reviewed, not necessarily that its official page was successfully reverified; summaries explicitly identify legacy research. `closed` with null deadline is a conservative inactive/watchlist classification, not proof a program ended. Do not infer annual dates. `upcoming` requires a published future program/intake; no opening date is invented.

## Initial migration and scan — 2026-09-18

Seeds were manually selected from the original table and prior public-program research. Loans, registration tasks, computer purchases, training and programs outside the geographic scope were not imported. Excluded legacy rows include Youth Loan, loan-interest subsidy, entrepreneurship training, company registration, Mac purchase, Singapore Tourism Accelerator, UNDP Ocean Challenge, Schmidt Marine and Canadian Ocean Startup Challenge. Hardware/space and purely financial investment/residency rows from research were also excluded.

New official discoveries: AppWorks #33, VentureSpark cohort 2, Cyberport CCMF October 2026 and February 2027 intakes. Checked both Global AI Builders Cup pages: Bangkok has no published round and is recruiting a host; January 2027 applications are upcoming. Its headline prize is a conditional investment, not a cash grant. Official True and Chunghwa pages were also checked. Earlier research supplies some historical seed deadlines; those are labelled, not silently presented as newly verified. Global Fast Track's current page confirms the competition but the September 25 deadline remains from prior research.

The original page mixed public facts with personal banking, registration budgets, and cash-flow strategy. Its full original was backed up outside this public repository before editing. Original styles and main headings remain in the template; personal plan text and financial estimates were replaced with neutral public guidance. This deliberately prioritizes the public-only requirement over verbatim preservation of sensitive non-table text. Original content may still exist in earlier Git history; history was not rewritten.

Monthly operation: search official pages, append/update records, build/test, review public-only diff, commit/push and verify remote HEAD. Refresh only the exact-title NotebookLM text source `Grant opportunities (auto)`; failed authentication must not prevent the public scan. Report new entries and confirmed deadlines within 60 days. No contacting programs or submitting applications.
