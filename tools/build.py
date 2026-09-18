#!/usr/bin/env python3
"""Validate public opportunity records and render the static page (stdlib only)."""
import argparse
import datetime as dt
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = set('id name type country organizer url deadline status summary first_seen last_checked source_url'.split())


def validate(rows):
    if not isinstance(rows, list):
        raise ValueError('Data must be a list')
    seen = set()
    for row in rows:
        if set(row) != FIELDS:
            raise ValueError('Missing or unexpected fields')
        for key in FIELDS - {'deadline'}:
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError(f'Invalid {key}')
        if row['id'] in seen:
            raise ValueError('Duplicate id: ' + row['id'])
        seen.add(row['id'])
        if row['type'] not in {'grant', 'accelerator', 'hackathon', 'competition'}:
            raise ValueError('Invalid type')
        if row['country'] not in {'TW', 'TH', 'HK', 'regional'}:
            raise ValueError('Invalid country')
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


def render(rows, template):
    if template.count('{{TABLE}}') != 1:
        raise ValueError('Template must have exactly one table marker')
    esc = html.escape
    lines = ['<table><thead><tr><th>Deadline</th><th>Status</th><th>Program</th><th>Country / Type</th><th>Organizer / Summary</th></tr></thead><tbody>']
    for r in sorted(rows, key=sort_key):
        lines.append(f'<tr data-id="{esc(r["id"], quote=True)}"><td>{esc(r["deadline"] or "Not announced")}</td><td>{esc(r["status"])}</td><td><a href="{esc(r["url"], quote=True)}">{esc(r["name"])}</a></td><td>{esc(r["country"])} / {esc(r["type"])}</td><td>{esc(r["organizer"])}<br>{esc(r["summary"])}<br><a href="{esc(r["source_url"], quote=True)}">Source</a> · Last checked {esc(r["last_checked"])}</td></tr>')
    lines.append('</tbody></table>')
    return template.replace('{{TABLE}}', '\n'.join(lines))


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
    page = render(rows, (ROOT / 'tools/template.html').read_text(encoding='utf-8'))
    if args.check:
        if old != data or (ROOT / 'index.html').read_text(encoding='utf-8') != page:
            raise SystemExit('Generated files are stale; run tools/build.py')
    else:
        if old != data:
            path.write_text(data, encoding='utf-8')
        (ROOT / 'index.html').write_text(page, encoding='utf-8')
    print(f'Validated {len(rows)} entries; ' + ('generated files match' if args.check else 'built index.html'))


if __name__ == '__main__':
    main()
