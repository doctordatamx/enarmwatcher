from pathlib import Path
import csv, hashlib, json, re, unicodedata
import pdfplumber
from .analytics import robust_trend, segmented, forecast, pressure, convergence, longitudinal_clusters, volatility, rank_stability
from .ingest import ROOT

def slug(name):
    return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip('-')

def parse(source):
    path=ROOT/source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:raise ValueError('SHA-256 mismatch')
    year=source['year']; records=[]
    with pdfplumber.open(path) as doc:
        for page_index,page in enumerate(doc.pages):
            # 2022–24 have two independent population tables side by side.
            region=page if year>=2025 else page.crop((0,0,page.width/2,page.height))
            if year>=2025 and page_index>0: continue
            words=region.extract_words()
            numbers=[w for w in words if re.fullmatch(r'\d+(?:\.\d+)?',w['text']) and float(w['text'])<=100]
            # Identify rows by adjacent numeric cells, then collect name words
            # using their vertical band. Handles wrapped multi-line cells.
            pairs=[]
            for i in range(len(numbers)-1):
                a,b=numbers[i:i+2]
                if abs(a['top']-b['top'])<3 and b['x0']>a['x1']:
                    if a['x0']>region.width*.40:pairs.append((a,b))
            for idx,(a,b) in enumerate(pairs):
                top=(pairs[idx-1][0]['top']+a['top'])/2 if idx else a['top']-8
                bottom=(a['top']+pairs[idx+1][0]['top'])/2 if idx<len(pairs)-1 else a['bottom']+8
                namewords=[w for w in words if top<=w['top']<bottom and w['x1']<a['x0']-2]
                name=' '.join(w['text'] for w in namewords).strip()
                if 'Página' in name or 'Página' in ' '.join(w['text'] for w in words if abs(w['top']-a['top'])<3):continue
                if not name or 'ESPECIALIDAD' in name:raise ValueError(f'Bad name {year}: {name}')
                v1,v2=float(a['text']),float(b['text'])
                low,high=(v2,v1) if year<=2023 else (v1,v2)
                if not 0<=low<=high<=100:raise ValueError(f'Bad range: {name}')
                records.append({'specialty_id':slug(name),'official_name':name,'year':year,'minimum':low,'maximum':high,'original_values':[a['text'],b['text']],'population':'mexicana','stage':source['stage'],'source_id':source['id'],'page':page_index+1,'applicants':None,'places':None,'selected':None,'mean':None,'demand_comparable':False,'comparable_group':None,'validation':'extracted_checked','comparability':'pending_review'})
    expected={2022:27,2023:26,2024:27,2025:27}
    if len(records)!=expected[year]:raise ValueError(f'{year}: expected {expected[year]}, got {len(records)}')
    if len({r['specialty_id'] for r in records})!=len(records):raise ValueError('Duplicate specialty')
    return records

def main():
    sources=json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
    records=[]
    for source in sources:
        records.extend(parse(source));source['status']='extracted_checked'
    names={r['specialty_id']:r['official_name'] for r in records}
    series={key:sorted([r for r in records if r['specialty_id']==key],key=lambda r:r['year']) for key in names}
    specialties=[]
    for key,name in sorted(names.items(),key=lambda a:a[1]):
        rows=series[key]
        demand_rows=[dict(r,pressure=pressure(r)) for r in rows]
        specialties.append({'id':key,'name':name.capitalize(),'official_name':name,'records':rows,'analytics':{'trend':robust_trend(rows),'volatility':volatility(rows),'segmented':segmented(rows),'forecast':forecast(rows),'demand_forecast':forecast(demand_rows,field='pressure'),'pressure':None}})
    out=ROOT/'public/data';out.mkdir(parents=True,exist_ok=True)
    payload={'version':'1.0.0','audit_date':'2026-10-31','population':'Categoría mexicana','years':sorted({r['year'] for r in records}),'sources':sources,'specialties':specialties,'convergence':convergence(series),'clusters':longitudinal_clusters(series),'coverage_note':'Cobertura inicial 2022–2025. Archivo histórico 2001–2021 sin extracción en esta entrega; 2026 sin resultados definitivos incorporados. Comparabilidad entre ediciones pendiente de revisión documental.'}
    payload['rank_stability']=rank_stability(series)
    (out/'specialties.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    normalized=ROOT/'data/normalized';normalized.mkdir(exist_ok=True)
    (normalized/'specialties.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    docs=ROOT/'docs';docs.mkdir(exist_ok=True)
    with (docs/'source_inventory.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(sources[0]));writer.writeheader();writer.writerows(sources)
    with (docs/'specialty_availability.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f);writer.writerow(['specialty','year','minimum','maximum','applicants','places','comparability'])
        for key in names:
            for year in payload['years']:
                row=next((r for r in series[key] if r['year']==year),None)
                writer.writerow([key,year,'available' if row else 'not_in_extracted_table','available' if row else 'not_in_extracted_table','not_extracted','not_extracted','pending_review'])
    print(f'{len(records)} checked observations; {len(specialties)} specialty profiles. Analytics eligibility gates applied.')

if __name__=='__main__': main()
