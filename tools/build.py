#!/usr/bin/env python3
"""Validate public opportunity records and render the static page (stdlib only)."""
import argparse
import datetime as dt
import html
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, quote
from event_details import validate_details, render_research, company_age_summary

from translate import FIELDS as SHOWN, FOREIGN, english, gemini, load_cache, save_cache

ROOT = Path(__file__).resolve().parents[1]
FIELDS = set('id name type country organizer url deadline status summary first_seen last_checked source_url fit fit_reason team_min team_max prize'.split())



def validate(rows):
    if not isinstance(rows, list):
        raise ValueError('Data must be a list')
    seen = set()
    for row in rows:
        if set(row) != FIELDS:
            raise ValueError('Missing or unexpected fields')
        for key in FIELDS - {'deadline', 'fit_reason', 'team_min', 'team_max'}:
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError(f'Invalid {key}')
        if row['id'] in seen:
            raise ValueError('Duplicate id: ' + row['id'])
        seen.add(row['id'])
        if row['type'] not in {'grant', 'accelerator', 'hackathon', 'competition'}:
            raise ValueError('Invalid type')
        if row['country'] not in {'TW', 'TH', 'HK', 'regional'}:
            raise ValueError('Invalid country')
        if row['fit'] not in {'want', 'skip'}:
            raise ValueError('Invalid fit (want or skip)')
        if not isinstance(row['fit_reason'], str) or (row['fit'] == 'skip' and not row['fit_reason'].strip()):
            raise ValueError('A skipped entry needs fit_reason')
        lo, hi = row['team_min'], row['team_max']
        for v in (lo, hi):
            if v is not None and (type(v) is not int or v < 1):
                raise ValueError('team_min/team_max must be a whole number or null')
        if lo is not None and hi is not None and lo > hi:
            raise ValueError('team_min is larger than team_max')
        if lo is not None and lo >= 3 and row['fit'] == 'want':
            raise ValueError('Needs 3+ people, so it must be skip: ' + row['id'])
        if row['status'] not in {'open', 'upcoming', 'rolling', 'closed'}:
            raise ValueError('Invalid status')
        for key in ('deadline', 'first_seen', 'last_checked'):
            value = row[key]
            if value is None and key == 'deadline':
                continue
            if not isinstance(value, str) or dt.date.fromisoformat(value).isoformat() != value:
                raise ValueError('Invalid ISO date')
        for key in ('url', 'source_url'):
            url = urlsplit(row[key])
            if url.scheme not in ('https', 'http') or not url.netloc:
                raise ValueError('Invalid public URL')
    return rows


def normalized(rows, today):
    return [dict(r, status='closed') if r['deadline'] and r['deadline'] < today else dict(r) for r in rows]


def sort_key(row):
    return ({'open': 0, 'upcoming': 0, 'rolling': 1, 'closed': 2}[row['status']], row['deadline'] or '9999-12-31', row['name'], row['id'])


def team(r):
    lo, hi = r['team_min'], r['team_max']
    if lo is None and hi is None:
        return 'NA'
    if lo == hi == 1:
        return 'Solo OK'
    if hi is None:
        return f'{lo}+'
    return f'{lo or 1}–{hi}' if lo != hi else str(lo)


COUNTRIES = {'TW': 'Taiwan', 'TH': 'Thailand', 'HK': 'Hong Kong', 'regional': 'Regional'}


def program_path(row):
    # Safe filenames even if a future import contains punctuation or path separators.
    return 'programs/' + hashlib.sha256(row['id'].encode()).hexdigest()[:20] + '.html'


def date_label(value):
    return dt.date.fromisoformat(value).strftime('%d %b %Y').lstrip('0') if value else 'Not announced'


def group_key(row):
    if row['deadline']:
        return row['deadline'][:7]
    return 'rolling' if row['status'] == 'rolling' else 'unknown'


def directory(rows, details=None):
    details = details or {}
    esc = html.escape
    groups = {}
    for row in sorted(rows, key=lambda r: (r['deadline'] or '9999', r['status'] != 'rolling', r['name'], r['id'])):
        groups.setdefault(group_key(row), []).append(row)
    parts = []
    for group, items in groups.items():
        label = {'rolling': 'Rolling applications', 'unknown': 'Deadline not announced'}.get(group)
        if label is None:
            label = dt.date.fromisoformat(group + '-01').strftime('%B %Y')
        parts.append(f'<section class="deadline-group"><h2>{label}<span class="group-count"></span></h2><div class="program-list">')
        for r in items:
            status = r['status'].capitalize()
            deadline = r['deadline'] or ''
            if deadline:
                date = dt.date.fromisoformat(deadline)
                when = f'<time datetime="{deadline}"><strong>{date.day:02d}</strong><span>{date.strftime("%b %Y")}</span></time>'
            else:
                when = '<strong class="undated">Anytime</strong><span>No fixed deadline</span>' if r['status'] == 'rolling' else '<strong class="undated">TBA</strong><span>No published date</span>'
            team_text = team(r) if team(r) != 'NA' else 'Not specified'
            prize = r['prize'] if r['prize'] != 'NA' else 'Not announced'
            research = details.get(r['id']) if r['fit'] == 'want' else None
            description = research['purpose'] if research else r['summary']
            theme = f'<p class="event-theme">Theme: {esc(research["theme"])}</p>' if research else ''
            company = research['company'] if research else None
            formation = ('Required' if company['required'] is True else '' if company['required'] is False else 'Not verified') if company else 'Not researched'
            company_cells = f'<div class="company-formation"><span class="mobile-label">Company formation: </span><strong>{formation}</strong><p>{esc(company["jurisdiction"]) if company else ""}</p></div><div class="company-age"><span class="mobile-label">Company age: </span><p title="{esc(company["notes"],quote=True) if company else ""}">{esc(company_age_summary(company)) if company else ""}</p></div>'
            if not company:company_cells = ''
            elif company['required'] is False:company_cells='<div class="company-formation"></div><div class="company-age"></div>'
            search = (' '.join(research[k] for k in ('purpose', 'theme', 'activities')) + ' ' if research else '') + ' '.join(str(r[k]) for k in ('name', 'organizer', 'summary', 'prize', 'fit_reason')) + ' ' + COUNTRIES[r['country']]
            why = f'<p class="exclusion">{esc(r["fit_reason"])}</p>' if r['fit'] == 'skip' else ''
            solo = r['team_min'] is not None and r['team_min'] <= 1
            parts.append(f'''<article class="program-row" data-id="{esc(r['id'], quote=True)}" data-status="{r['status']}" data-fit="{r['fit']}" data-country="{r['country']}" data-type="{r['type']}" data-solo="{str(solo).lower()}" data-deadline="{deadline}" data-search="{esc(search, quote=True)}">
<div class="deadline">{when}<span class="status status-{r['status']}">{status}</span></div>
<div class="program-info"><div class="program-meta">{COUNTRIES[r['country']]}<span>·</span>{r['type'].capitalize()}</div><h3><a class="program-link" href="{program_path(r)}" target="_blank" rel="noopener noreferrer">{esc(r['name'])}<span class="new-tab" aria-hidden="true">↗</span><span class="sr-only"> (opens in a new tab)</span></a></h3><p class="summary">{esc(description)}</p>{theme}{why}</div>
<div class="program-facts"><p class="funding">{esc(prize)}</p><p class="team"><span class="mobile-label">Team: </span>{esc(team_text)}</p></div>{company_cells}</article>''')
        parts.append('</div></section>')
    return '\n'.join(parts)


def ensure_english(rows):
    bad = [r['id'] for r in rows for k in SHOWN if FOREIGN.search(r[k])]
    if bad:
        raise ValueError('Not in English, refusing to publish: ' + ', '.join(sorted(set(bad))))


def render(rows, template, details=None):
    if template.count('{{TABLE}}') != 1:
        raise ValueError('Template must have exactly one table marker')
    ensure_english(rows)
    checked = max((r['last_checked'] for r in rows), default=None)
    return template.replace('{{TABLE}}', directory(rows, details)).replace('{{CHECKED}}', date_label(checked))


def render_detail(row, research=None):
    ensure_english([row])
    esc = html.escape
    team_text = team(row) if team(row) != 'NA' else 'Not specified'
    prize = row['prize'] if row['prize'] != 'NA' else 'Not announced'
    research = research if row['fit'] == 'want' else None
    researched = render_research(research)
    readiness_link = f'<p><a class="button" href="https://grants.srv1989548.hstgr.cloud/event?id={quote(row["id"], safe="")}" target="_blank" rel="noopener noreferrer">My preparation checklist ↗</a></p>' if research else ''
    company_glance = ''
    if research:
        company = research['company']
        formed = 'Required' if company['required'] is True else '' if company['required'] is False else 'Needs verification'
        age = company_age_summary(company)
        company_glance = f'<div><dt>Company formation</dt><dd>{formed}<br>{esc(company["jurisdiction"])}</dd></div><div><dt>Company age</dt><dd>{esc(age)}</dd></div>'
        if company['required'] is False:company_glance=''
    fit = esc(row['fit_reason']) if row['fit'] == 'skip' else 'Potential fit. Check the official requirements before preparing an application.'
    status_note = {
        'closed': 'This round is closed or has no verified active intake. Keep it for reference; a future round is not yet confirmed.',
        'rolling': 'No fixed closing date is recorded. Check that applications are still being accepted.',
        'upcoming': 'A future intake is recorded. Check the official page for opening dates and application instructions.',
        'open': 'An open intake is recorded. Check the official page for the exact cutoff time and current requirements.'
    }[row['status']]
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(row['name'])} | Grant directory</title><meta name="description" content="{esc(row['summary'], quote=True)}"><link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../assets/site.css"></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="shell header-inner"><a class="brand" href="../index.html"><span class="brand-mark" aria-hidden="true">g.</span>Grant directory</a><span class="header-note">Program details</span></div></header>
<main id="main" class="shell detail-page"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">All programs</a><span aria-hidden="true">/</span><span>{COUNTRIES[row['country']]}</span></nav>
<div class="detail-heading"><p class="eyebrow">{COUNTRIES[row['country']]} · {row['type'].capitalize()}</p><h1>{esc(row['name'])}</h1><p class="organizer">{esc(row['organizer'])}</p></div>
<div class="detail-layout"><div class="detail-copy"><section><h2>What to know</h2><p class="full-summary">{esc(row['summary'])}</p></section><section><h2>Eligibility</h2><p>{fit}</p><p class="muted">Team size refers to the recorded application requirement. It can mean people or companies; the program description gives the context.</p></section><section><h2>Application window</h2><p>{status_note}</p></section>{researched}{readiness_link}<section class="sources"><h2>Go to the source</h2><a class="button primary" href="{esc(row['url'], quote=True)}" target="_blank" rel="noopener noreferrer">Official program <span aria-hidden="true">↗</span><span class="sr-only"> (opens in a new tab)</span></a><a class="source-link" href="{esc(row['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Research source ↗<span class="sr-only"> (opens in a new tab)</span></a><p class="muted">Record reviewed {date_label(row['last_checked'])}. A review date does not guarantee that every official detail was reconfirmed. Any limits on verification appear in the description.</p></section></div>
<aside class="fact-sheet" aria-label="Program key facts"><h2>At a glance</h2><dl><div><dt>Deadline</dt><dd>{date_label(row['deadline'])}</dd></div><div><dt>Status</dt><dd><span class="status status-{row['status']}">{row['status'].capitalize()}</span></dd></div><div><dt>Funding / benefit</dt><dd>{esc(prize)}</dd></div><div><dt>Team size</dt><dd>{esc(team_text)}</dd></div>{company_glance}<div><dt>Review</dt><dd>{'Excluded' if row['fit'] == 'skip' else 'Potential fit'}</dd></div><div><dt>First listed</dt><dd>{date_label(row['first_seen'])}</dd></div></dl></aside></div>
</main><footer class="shell site-footer">Generated from public program records. Updated by the Grant cron pipeline. Do not edit this page by hand.</footer></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--as-of', default=dt.date.today().isoformat())
    parser.add_argument('--check', action='store_true', help='Fail if generated files are stale; do not write')
    args = parser.parse_args()
    dt.date.fromisoformat(args.as_of)
    path = ROOT / 'data/opportunities.json'
    old = path.read_text(encoding='utf-8')
    rows = normalized(validate(json.loads(old)), args.as_of)
    data = json.dumps(rows, ensure_ascii=False, indent=2) + '\n'
    cache = load_cache()
    before = dict(cache)
    shown = english(rows, cache, None if args.check else gemini)
    if cache != before:
        save_cache(cache)
    research_path = ROOT / 'data/event_details.json'
    research = validate_details(json.loads(research_path.read_text()) if research_path.exists() else {}, rows)
    page = render(shown, (ROOT / 'tools/template.html').read_text(encoding='utf-8'), research)
    details = {program_path(r): render_detail(r, research.get(r['id'])) for r in shown}
    if args.check:
        if any(not (ROOT / name).exists() or (ROOT / name).read_text(encoding='utf-8') != content for name, content in details.items()):
            raise SystemExit('Generated program pages are stale; run tools/build.py')
        if old != data or (ROOT / 'index.html').read_text(encoding='utf-8') != page:
            raise SystemExit('Generated files are stale; run tools/build.py')
    else:
        if old != data:
            path.write_text(data, encoding='utf-8')
        (ROOT / 'programs').mkdir(exist_ok=True)
        for name, content in details.items():
            (ROOT / name).write_text(content, encoding='utf-8')
        (ROOT / 'index.html').write_text(page, encoding='utf-8')
    print(f'Validated {len(rows)} entries; ' + ('generated files match' if args.check else 'built index.html'))


if __name__ == '__main__':
    main()
