"""Public API partitions. Separate files keep unrelated history out of each visit."""
import json,csv
from collections import defaultdict
from .ingest import ROOT
from .platform import national_aggregate

def main():
    out=ROOT/'public/data';d=json.loads((out/'platform.json').read_text(encoding='utf8'));specialties=json.loads((out/'specialties.json').read_text(encoding='utf8'))
    states=[]
    for year in d['academic_years']:
        for state in sorted({r['state'] for r in d['academic_records'] if r['year']==year and r['state']}):
            rows=[r for r in d['academic_records'] if r['year']==year and r['state']==state];states.append(dict(year=year,state=state,**national_aggregate(rows)))
    core={k:d[k] for k in ['version','audit_date','academic_years','coverage']}
    partitions={'national':{**core,'national':d['national'],'states':states},'academic':{**core,'national':d['national'],'states':states,'academic_records':d['academic_records'],'universities':d['universities'],'sources':[s for s in d['sources'] if s['kind']=='academic']},'receiving':{**core,**{k:d[k] for k in ['receiving','receiving_summary','sites','reconciliation']},'sources':[s for s in d['sources'] if s['kind'].startswith('receiving')]},'atlas':{**core,'states':states,'sites':d['sites'],'sources':d['sources']},'platform-sources':{**core,'sources':d['sources'],'issues':d['issues']}}
    for name,payload in partitions.items():(out/(name+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf8')
    items=[{'name':u['name']+' · '+(u['state'] or 'sin entidad'),'type':'Universidad de procedencia','path':'/universities/'+u['id']} for u in d['universities']]
    items.extend({'name':s['name'],'type':'Especialidad','path':'/specialty/'+s['id']} for s in specialties['specialties'])
    receiving={r['institution_id']:r['institution_name'] for r in d['receiving']};items.extend({'name':name,'type':'Institución receptora','path':'/receiving/'+id} for id,name in receiving.items())
    sites={r['site_id']:r for r in d['sites']};items.extend({'name':r['name']+' · '+r['state'],'type':'Sede receptora','path':'/hospitals/'+id} for id,r in sites.items())
    (out/'catalogue.json').write_text(json.dumps({'items':items},ensure_ascii=False,separators=(',',':')),encoding='utf8')
    with (ROOT/'docs/platform_variable_availability.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['year','academic_examined','academic_selected','academic_score_statistic','receiving_institution_specialty','receiving_state_site','clues_coordinates','individual_origin_destination'])
        for year in range(2001,2027):
            rows=[r for r in d['academic_records'] if r['year']==year];matrix=any(r['year']==year for r in d['receiving']);sites=any(r['year']==year for r in d['sites'])
            w.writerow([year,'available' if rows else 'not_incorporated','partial' if rows and any(r['selected'] is None for r in rows) else 'available' if rows else 'not_incorporated',';'.join(sorted({r['score_statistic'] for r in rows})) or 'not_incorporated','available' if matrix else 'not_incorporated','available' if sites else 'not_incorporated','not_linked','not_incorporated'])
    with (ROOT/'docs/receiving_institutions_availability.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['year','institution','specialty','level','place_type','places','source_id','status'])
        w.writerows([r['year'],r['institution_id'],r['specialty_id'],'national_institution','oferta_publicada_R1',r['places'],r['source_id'],'extracted_checked'] for r in d['receiving'])
    print('API partitioned; catalogue',len(items),'entries')

if __name__=='__main__':main()
