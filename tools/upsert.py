#!/usr/bin/env python3
"""Add or update opportunities from stdin (one JSON object or a list). Matches by id.
Every entry needs fit: want | skip (skip also needs fit_reason), English text only;
team_min/team_max = required team size (null if unknown; 3+ people must be skip); prize = English text or "NA". Keeps first_seen, sets last_checked to today, never deletes. Usage: python3 tools/upsert.py < entry.json"""
import datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from build import validate, ROOT

def upsert(rows, items, today):
    by_id = {r['id']: r for r in rows}
    added, updated = [], []
    for it in items:
        old = by_id.get(it['id'])
        it = dict({'fit_reason': '', 'team_min': None, 'team_max': None, 'prize': 'NA'} if not old else {}, **it)
        it = dict(it, first_seen=old['first_seen'] if old else today, last_checked=today)
        if old:
            old.update(it); updated.append(it['id'])
        else:
            rows.append(it); by_id[it['id']] = it; added.append(it['id'])
    return validate(rows), added, updated

if __name__ == '__main__':
    items = json.load(sys.stdin)
    items = items if isinstance(items, list) else [items]
    path = ROOT / 'data/opportunities.json'
    rows, added, updated = upsert(json.loads(path.read_text(encoding='utf-8')), items, dt.date.today().isoformat())
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'added {added or "none"}; updated {updated or "none"}; total {len(rows)}')
