"""Strict public event research schema and shared HTML presentation."""
import datetime as dt
import html
import re
from urllib.parse import urlsplit
from translate import FOREIGN

DETAIL_FIELDS=set('purpose theme activities cycle checked_at coverage company limitations sources requirements winners'.split())
REQUIRED_FIELDS=set('id label category required stage details source_url'.split())
CONSTRAINT_TYPES={'language':str,'format':str,'min_seconds':int,'max_seconds':int,'max_age_days':int,'max_bytes':int,'max_words':int,'max_pages':int,'must_be_new':bool,'min_company_age_months':int,'max_company_age_months':int,'company_age_reference':str}


def public_url(value):
    u=urlsplit(value)
    if u.scheme not in {'https','http'} or not u.netloc or u.username or u.password:
        raise ValueError('Invalid public source URL')


def ensure_english(value,key=''):
    if isinstance(value,str) and key not in {'url','source_url'} and not value.startswith(('https://','http://')) and FOREIGN.search(value):raise ValueError('Translate event research into English before publication')
    if isinstance(value,list):
        for v in value:ensure_english(v,key)
    if isinstance(value,dict):
        for k,v in value.items():ensure_english(v,k)


def text(value):
    if not isinstance(value,str) or not value.strip():raise ValueError('Expected nonempty text')


def validate_details(details,rows):
    if not isinstance(details,dict):raise ValueError('Event details must be an object keyed by id')
    fits={r['id']:r['fit'] for r in rows}
    out={}
    for event,detail in details.items():
        if event not in fits:raise ValueError('Unknown event '+event)
        if fits[event]=='skip':continue
        if not isinstance(detail,dict) or set(detail)!=DETAIL_FIELDS:raise ValueError('Unexpected or missing public detail fields')
        for key in ('purpose','theme','activities','cycle','checked_at'):text(detail[key])
        dt.date.fromisoformat(detail['checked_at'])
        if detail['coverage'] not in {'partial','verified'}:raise ValueError('Invalid research coverage')
        company=detail['company']
        if not isinstance(company,dict) or set(company)!=set('required jurisdiction entity_types min_age_months max_age_months age_reference formation_stage notes source_url'.split()):raise ValueError('Company formation and age fields are required')
        if company['required'] is not None and type(company['required']) is not bool:raise ValueError('Invalid company requirement')
        for k in ('jurisdiction','entity_types','age_reference','formation_stage','notes'):text(company[k])
        for k in ('min_age_months','max_age_months'):
            if company[k] is not None and (type(company[k]) is not int or company[k]<0):raise ValueError('Invalid company age')
        public_url(company['source_url'])
        if not isinstance(detail['limitations'],list):raise ValueError('Invalid limitations')
        for value in detail['limitations']:text(value)
        if not isinstance(detail['sources'],list) or not detail['sources']:raise ValueError('Official sources required')
        for source in detail['sources']:
            if set(source)!={'url','title'}:raise ValueError('Invalid public source fields')
            text(source['title']);public_url(source['url'])
        if not isinstance(detail['requirements'],list):raise ValueError('Invalid requirements')
        ids=set()
        for req in detail['requirements']:
            if not REQUIRED_FIELDS<=set(req) or set(req)-REQUIRED_FIELDS-{'match_key','constraints'}:raise ValueError('Invalid requirement fields')
            for key in ('id','label'):text(req[key])
            if not isinstance(req['details'],str):raise ValueError('Invalid requirement details')
            if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',req['id']) or req['id'] in ids:raise ValueError('Unsafe or duplicate requirement id')
            ids.add(req['id'])
            if req['category'] not in {'eligibility','material','field','step'} or req['stage'] not in {'application','participation','award'} or (req['required'] is not None and type(req['required']) is not bool):raise ValueError('Invalid requirement category, stage or required flag')
            public_url(req['source_url'])
            if 'match_key' in req and not re.fullmatch(r'(founder|company|project|event)\.[a-z0-9_]+',req['match_key']):raise ValueError('Invalid shared match key')
            constraints=req.get('constraints',{})
            if not isinstance(constraints,dict):raise ValueError('Invalid constraints')
            for k,v in constraints.items():
                if k not in CONSTRAINT_TYPES or type(v) is not CONSTRAINT_TYPES[k] or (type(v) is int and v<0):raise ValueError('Invalid constraint '+k)
        if not isinstance(detail['winners'],list):raise ValueError('Invalid previous winners')
        for winner in detail['winners']:
            if set(winner)-{'year','name','description','source_url','kind'} or not {'year','name','description','source_url'}<=set(winner) or type(winner['year']) is not int:raise ValueError('Invalid previous winner fields')
            text(winner['name']);text(winner['description']);public_url(winner['source_url'])
            if winner.get('kind','winner') not in {'winner','recipient','alumnus','participant'}:raise ValueError('Invalid past-example kind')
        ensure_english(detail)
        out[event]=detail
    return out


def company_age_summary(company):
    if company['required'] is False:return 'Not applicable to the individual path.'
    notes=company['notes']
    if company['max_age_months'] is not None:
        months=company['max_age_months']
        bound=f'Under {months // 12} years' if months % 12 == 0 and ('exclusive' in notes.lower() or 'less than' in notes.lower()) else f'{months}-month upper bound'
        return bound+'; measured at '+company['age_reference']+'.'
    for sentence in re.split(r'(?<=[.!?])\s+',notes):
        if re.search(r'company.age|\d{4}-\d{2}-\d{2}|formation (cutoff|window)',sentence,re.I):return sentence
    return 'No exact company-age limit verified. See the formation rules.'


def render_research(detail):
    if not detail:return ''
    esc=html.escape
    company=detail['company']
    requirement='Required' if company['required'] is True else 'Not required for the individual path' if company['required'] is False else 'Not yet verified'
    parts=[f'<section class="company-rules"><h2>Company formation and age</h2><dl><div><dt>Company required</dt><dd>{requirement}</dd></div><div><dt>Jurisdiction</dt><dd>{esc(company["jurisdiction"])}</dd></div><div><dt>Entity types</dt><dd>{esc(company["entity_types"])}</dd></div><div><dt>When you must be incorporated</dt><dd>{esc(company["formation_stage"])}</dd></div><div><dt>When company age is measured</dt><dd>{esc(company["age_reference"])}</dd></div></dl><p>{esc(company["notes"])}</p><a href="{esc(company["source_url"],quote=True)}" target="_blank" rel="noopener noreferrer">Company eligibility source ↗</a></section>']
    for key,title in [('purpose','What this event is for'),('theme','Theme and focus'),('activities','What you would do')]:
        parts.append(f'<section><h2>{title}</h2><p>{esc(detail[key])}</p></section>')
    parts.append(f'<section class="research-status"><h2>Research coverage</h2><p>{esc(detail["cycle"])} · Checked {esc(detail["checked_at"])} · {detail["coverage"].capitalize()}</p>')
    if detail['limitations']:parts.append('<ul>'+''.join('<li>'+esc(v)+'</li>' for v in detail['limitations'])+'</ul>')
    parts.append('</section>')
    for category,title in [('eligibility','Eligibility requirements'),('material','Materials to prepare'),('field','Application fields'),('step','Application steps')]:
        tag='ol' if category=='step' else 'ul'
        items=[r for r in detail['requirements'] if r['category']==category]
        parts.append(f'<section><h2>{title}</h2>')
        if not items:parts.append('<p class="muted">Not yet verified. Check the official application instructions.</p>')
        else:
            parts.append(f'<{tag} class="requirements">')
            for req in items:
                flag='Required' if req['required'] is True else 'Optional' if req['required'] is False else 'Required status unverified'
                stage={'application':'To apply','participation':'During participation','award':'After award'}[req['stage']]
                parts.append(f'<li><strong>{esc(req["label"])}</strong><span class="requirement-meta">{flag} · {stage}</span><p>{esc(req["details"])}</p><a href="{esc(req["source_url"],quote=True)}" target="_blank" rel="noopener noreferrer">Requirement source ↗</a></li>')
            parts.append(f'</{tag}>')
        parts.append('</section>')
    parts.append('<section><h2>Previous winners and other past examples</h2>')
    if not detail['winners']:parts.append('<p class="muted">No verified past-winner or recipient details captured. This does not mean there were no previous winners.</p>')
    else:
        for w in detail['winners']:
            parts.append(f'<article class="winner"><h3>{w["year"]} · {esc(w["name"])}</h3><p class="requirement-meta">{esc(w.get("kind","winner").capitalize())}</p><p>{esc(w["description"])}</p><a href="{esc(w["source_url"],quote=True)}" target="_blank" rel="noopener noreferrer">Example source ↗</a></article>')
    parts.append('</section><section><h2>Research sources</h2><ul>')
    for source in detail['sources']:parts.append(f'<li><a href="{esc(source["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{esc(source["title"])} ↗</a></li>')
    parts.append('</ul></section>')
    return ''.join(parts)
