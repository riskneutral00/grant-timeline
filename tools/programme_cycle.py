"""Keep programme families visible; forecasts never become verified deadlines."""
import calendar
import copy
import datetime as dt
import re


def next_anniversary(value,today):
    if not value:return None
    previous=dt.date.fromisoformat(value)
    year=previous.year+1
    candidate=dt.date(year,previous.month,min(previous.day,calendar.monthrange(year,previous.month)[1]))
    while candidate<today:
        year+=1;candidate=dt.date(year,previous.month,min(previous.day,calendar.monthrange(year,previous.month)[1]))
    return candidate.isoformat()


def catalogue_name(row,year):
    name=re.sub(r'\s*\(planning\)$','',row['name'],flags=re.I)
    name=re.sub(r'\s+#\d+\b|\s+Batch\s+\d+\b','',name,flags=re.I)
    if re.search(r'\b20\d{2}\b',name):name=re.sub(r'\b20\d{2}\b',str(year),name)
    else:name+=' '+str(year)
    return name+' (planning)'


def planning_stub(row):
    url=row.get('source_url',row.get('url','https://example.invalid/'))
    return {'purpose':row['summary'],'theme':'Not yet verified.','activities':'Not yet verified.','cycle':'Previous known programme; next call not announced.','checked_at':row.get('last_checked',dt.date.today().isoformat()),'coverage':'partial','company':{'required':None,'jurisdiction':'Not yet verified.','entity_types':'Not yet verified.','min_age_months':None,'max_age_months':None,'age_reference':'Not yet verified.','formation_stage':'Not yet verified.','notes':'Company rules need official-source verification.','source_url':url},'limitations':['Next intake and requirements have not been announced or verified.'],'sources':[{'url':url,'title':'Last known official programme source'}],'requirements':[],'winners':[]}


def roll_programmes(rows,details,today,planning_year=None):
    rows=copy.deepcopy(rows);details=copy.deepcopy(details)
    if isinstance(today,str):today=dt.date.fromisoformat(today)
    target=planning_year or today.year+1
    for row in rows:
        if row['fit']!='want':continue
        detail=details.get(row['id'])
        expired=row['deadline'] is not None and row['deadline']<today.isoformat()
        if row['status'] in {'open','upcoming','rolling'} and not expired:
            if detail:detail.pop('planning',None)
            continue
        if row['status'] not in {'closed','planning'} and not expired:continue
        if detail is None:detail=details.setdefault(row['id'],planning_stub(row))
        planning=detail.get('planning')
        if planning and planning['year']>=today.year:
            row['status']='planning';row['deadline']=None
            continue
        last_date=planning['last_round_deadline'] if planning else row['deadline']
        last_name=planning['last_round_name'] if planning else row['name']
        estimate=next_anniversary(last_date,today)
        named=re.findall(r'\b(20\d{2})\b',last_name)
        previous_cycle=int(named[-1]) if named else dt.date.fromisoformat(last_date).year if last_date else None
        if planning and planning.get('estimated_deadline') and estimate:
            inferred=dt.date.fromisoformat(estimate).year + planning['year'] - dt.date.fromisoformat(planning['estimated_deadline']).year
        else:inferred=previous_cycle+dt.date.fromisoformat(estimate).year-dt.date.fromisoformat(last_date).year if estimate and previous_cycle else target
        year=planning_year or max(today.year,inferred)
        detail['planning']={'year':year,'estimated_deadline':estimate,'last_round_deadline':last_date,'last_round_name':last_name,'basis':'Planning estimate from the previous round. A new call, recurrence and deadline are not officially confirmed.'}
        row['status']='planning';row['deadline']=None;row['name']=catalogue_name(dict(row,name=last_name),year)
        previous_summary=row['summary'].split('Previous-round reference: ',1)[-1]
        summary=re.sub(r'\bclosed\b','ended',previous_summary,flags=re.I)
        row['summary']=f'Planning for {year}; next intake and deadline are unconfirmed. Previous-round reference: '+summary
    return rows,details


def effective_date(row,detail=None):
    return row['deadline'] or (detail or {}).get('planning',{}).get('estimated_deadline')
