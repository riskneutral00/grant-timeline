#!/usr/bin/env python3
"""Output-stage translation. opportunities.json keeps text as found (any language); everything
shown to Matt (site, NotebookLM, Discord) goes through english(). Translations are cached in
data/translations.json keyed by the exact source text, so each text is translated once, and a
changed source is translated again while old entries stay. Stdlib only."""
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'data/translations.json'
FIELDS = ('name', 'organizer', 'summary', 'prize', 'fit_reason')
FOREIGN = re.compile(r'[฀-๿　-鿿가-힯＀-￯]')  # Thai, CJK, Korean, full-width


def english(rows, cache, translate):
    """Rows with FIELDS in English. Fills cache via translate(list[str]) -> list[str]; None = cache only."""
    missing = sorted({r[k] for r in rows for k in FIELDS if FOREIGN.search(r[k]) and r[k] not in cache})
    if missing:
        if translate is None:
            raise ValueError(f'{len(missing)} texts have no English translation yet; run tools/build.py')
        out = translate(missing)
        if len(out) != len(missing) or any(not isinstance(t, str) or FOREIGN.search(t) for t in out):
            raise ValueError('Translation came back incomplete or not in English')
        cache.update(zip(missing, out))
    return [dict(r, **{k: cache.get(r[k], r[k]) for k in FIELDS}) for r in rows]


def load_cache():
    return json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}


def save_cache(cache):
    CACHE.write_text(json.dumps(dict(sorted(cache.items())), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _gemini_key():
    if os.environ.get('GEMINI_API_KEY'):
        return os.environ['GEMINI_API_KEY']
    # Server: read it from Bitwarden Secrets Manager through creds (never printed).
    env = dict(os.environ, CREDS_MAP='/opt/data/credmap/credentials.json', BWS_BIN='/opt/data/tools/bin/bws')
    for line in Path('/opt/data/.env').read_text().splitlines():
        if line.startswith('BWS_ACCESS_TOKEN='):
            env['BWS_ACCESS_TOKEN'] = line.split('=', 1)[1].strip().strip('"')
    return subprocess.run(['/opt/data/tools/bin/creds', 'gemini.api_key'], env=env, capture_output=True, text=True, check=True).stdout.strip()


def gemini(texts, model='gemini-3-flash-preview'):
    prompt = ('Translate each string in this JSON list into plain English. Keep numbers, dates, money and URLs exact. '
              'For names of programs and organizations use the official English name if one exists. '
              'Return only a JSON list of the same length and order.\n' + json.dumps(texts, ensure_ascii=False))
    body = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0}}
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                                 data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': _gemini_key()})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(json.load(r)['candidates'][0]['content']['parts'][0]['text'])
