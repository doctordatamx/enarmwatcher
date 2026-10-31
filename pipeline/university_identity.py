"""Explicit, source-bound institution links; original rows are never rewritten."""
import json
from .ingest import ROOT

def university_profiles(records,sources):
    registry=json.loads((ROOT/'data/university_identity_links.json').read_text(encoding='utf8'))
    source_map={s['id']:s for s in sources}
    aliases={}
    groups={}
    for group in registry['groups']:
        linked=[r for r in records if r['id'] in group['alias_ids']]
        if sorted(r['year'] for r in linked)!=group['years']:
            raise ValueError('Institution link years changed; review the identity registry')
        if {r['source_id'] for r in linked}!=set(group['sources']):
            raise ValueError('Institution link sources changed; review the identity registry')
        if any(source_map.get(id,{}).get('sha256')!=sha for id,sha in group['sources'].items()):
            raise ValueError('Institution link source hash changed')
        if len({r['year'] for r in linked})!=len(linked):
            raise ValueError('Institution link duplicates an edition')
        for alias in group['alias_ids']:
            if alias in aliases:raise ValueError('Institution alias assigned twice')
            aliases[alias]=group['id']
        groups[group['id']]=group
    profiles=[]
    for id in sorted({aliases.get(r['id'],r['id']) for r in records}):
        rows=sorted([r for r in records if aliases.get(r['id'],r['id'])==id],key=lambda r:r['year'])
        group=groups.get(id)
        profiles.append({'id':id,'name':group['name'] if group else rows[-1]['name'],
            'state':group['state'] if group else rows[-1]['state'],'records':rows,
            **({'identity_link':{**group,'review_date':registry['review_date']}} if group else {})})
    return profiles

def refresh():
    for path in [ROOT/'data/normalized/platform.json',ROOT/'public/data/platform.json']:
        data=json.loads(path.read_text(encoding='utf8'))
        data['universities']=university_profiles(data['academic_records'],data['sources'])
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')

if __name__=='__main__':refresh()
