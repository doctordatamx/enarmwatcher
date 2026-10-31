"""Build data-driven trend coverage and model eligibility after every data update."""
import json
from collections import defaultdict
from .ingest import ROOT
from .analytics import robust_trend,segmented,forecast

RULES={'trend':6,'segmented':10,'forecast':14}

def model_checks(rows,minimum):
    years=[r['year'] for r in rows];missing=[r['year'] for r in rows if r['value'] is None]
    consecutive=bool(years) and sorted(years)==list(range(min(years),max(years)+1))
    comparable=bool(rows) and None not in {r['comparable_group'] for r in rows} and len({r['comparable_group'] for r in rows})==1
    return [{'id':'length','passed':len(rows)>=minimum,'detail':f'{len(rows)} ediciones incorporadas; mínimo operativo {minimum}.'},
            {'id':'complete','passed':not missing,'detail':('Datos presentes en todas las ediciones.' if not missing else 'Valores faltantes: '+', '.join(map(str,missing))+'.')},
            {'id':'consecutive','passed':consecutive,'detail':'Ediciones consecutivas, sin duplicados.' if consecutive else 'La serie tiene huecos o años duplicados.'},
            {'id':'comparability','passed':comparable,'detail':'Bloque comparable documentado.' if comparable else 'Comparabilidad de escala, población, composición y etapa pendiente de revisión.'}]

def series(rows,unit,bounded=False):
    rows=sorted(rows,key=lambda r:r['year'])
    model_rows=[dict(r,minimum=r['value']) for r in rows]
    results={'trend':robust_trend(model_rows,field='value'),'segmented':segmented(model_rows,field='value'),'forecast':forecast(model_rows,field='minimum' if bounded else 'value')}
    return {'unit':unit,'bounded':bounded,'records':rows,'coverage':{'years':[r['year'] for r in rows],'editions':len(rows),'observed':sum(r['value'] is not None for r in rows),'missing_years':[r['year'] for r in rows if r['value'] is None]},'models':{key:{**result,'checks':model_checks(rows,RULES[key])} for key,result in results.items()}}

def observation(year,value,source_ids,group=None,population='mexicana',stage='academic-published',note=None):
    return {'year':year,'value':value,'source_ids':source_ids,'comparable_group':group,'population':population,'stage':stage,'note':note}

def build(data,specialties):
    out=ROOT/'public/data';sources=data['sources']+specialties['sources'];source_map={s['id']:s for s in sources}
    def write(name,payload):
        ids={id for entity in payload['entities'] for s in entity['series'].values() for r in s['records'] for id in r['source_ids']}
        payload['sources']=[{'id':id,'year':source_map[id]['year'],'url':source_map[id]['url'],'sha256':source_map[id]['sha256']} for id in sorted(ids)]
        payload['version']='2.1.0';payload['audit_date']=data['audit_date']
        (out/f'trends-{name}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf8')
    metrics={'examined':('Sustentantes','participaciones',False),'selected':('Seleccionados','participaciones',False),'rate':('Tasa de selección','%',True),'score':('Puntaje publicado','puntos',True)}
    national={}
    for field,(label,unit,bounded) in metrics.items():
        rows=[]
        for r in data['national']:
            ids=[s['id'] for s in sources if s.get('kind')=='academic' and s['year']==r['year']]
            note=None
            if field in ('selected','rate') and not r['selected_complete']:note=f"Seleccionados incompletos: {r.get('selected_missing_rows','')} fila(s) sin dato. Subtotal informado: {r.get('selected_observed_subtotal','no disponible')}. No se imputa el total o la tasa."
            if field=='score' and r['score'] is None:note='Media agregada no disponible; no se promedian medianas.'
            rows.append(observation(r['year'],r[field],ids,note=note))
        national[field]={'label':label,**series(rows,unit,bounded)}
    write('national',{'entities':[{'id':'national','name':'Agregado de filas académicas · categoría mexicana','series':national}]})
    universities=[]
    for u in data['universities']:
        values={}
        for field,(label,unit,bounded) in metrics.items():
            rows=[observation(r['year'],r[field],[r['source_id']],r['score_comparable_group'] if field=='score' else r.get('rate_comparable_group'),note=('Mediana publicada; no equiparada a medias históricas.' if field=='score' and r['score_statistic']=='median' else 'Seleccionados sin dato en la fuente.' if field in ('selected','rate') and r['selected'] is None else None)) for r in u['records']]
            values[field]={'label':label,**series(rows,unit,bounded)}
        universities.append({'id':u['id'],'name':u['name']+' · '+(u['state'] or 'sin entidad'),'series':values})
    write('universities',{'entities':universities})
    special=[]
    for s in specialties['specialties']:
        values={field:{'label':label,**series([observation(r['year'],r[field],[r['source_id']],r['comparable_group'],stage=r['stage']) for r in s['records']],'puntos',True)} for field,label in [('minimum','Puntaje mínimo'),('maximum','Puntaje máximo')]}
        special.append({'id':s['id'],'name':s['name'],'series':values})
    write('specialties',{'entities':special})
    groups=defaultdict(list)
    for r in data['receiving']:groups[r['institution_id']].append(r)
    receiving=[]
    for id,records in sorted(groups.items()):
        years=sorted({r['year'] for r in records})
        rows=[observation(y,sum(r['places'] for r in records if r['year']==y),sorted({r['source_id'] for r in records if r['year']==y}),stage='snapshot_matriz_publicada',note='Snapshot de oferta R1; no asignación ni ocupación. Identidad y etapa requieren revisión longitudinal.') for y in years]
        receiving.append({'id':id,'name':max(records,key=lambda r:r['year'])['institution_name'],'series':{'places':{'label':'Plazas publicadas R1',**series(rows,'plazas')}}})
    write('receiving',{'entities':receiving})
    def coverage(records,field='year'):
        years=sorted({r[field] for r in records});return {'years':years,'first_year':min(years),'last_year':max(years),'editions':len(years),'records':len(records)}
    index={'version':'2.1.0','audit_date':data['audit_date'],'datasets':{'national':{'label':'Panorama académico',**coverage(data['national'])},'universities':{'label':'Universidades',**coverage(data['academic_records'])},'specialties':{'label':'Especialidades',**coverage([r for s in specialties['specialties'] for r in s['records']])},'receiving':{'label':'Oferta institucional',**coverage(data['receiving'])}},'rules':RULES,'warning':'Incorporar nuevas ediciones actualiza observaciones y elegibilidad; no acredita comparabilidad ni habilita automáticamente pronósticos.'}
    (out/'trends-index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    print('Trend datasets and eligibility rebuilt through',max(data['academic_years']))

if __name__=='__main__':
    build(json.loads((ROOT/'data/normalized/platform.json').read_text(encoding='utf8')),json.loads((ROOT/'public/data/specialties.json').read_text(encoding='utf8')))
