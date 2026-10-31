"""ENARM public analytical warehouse. Version 2.0.0.

Origin faculties, receiving institutions and training units are separate facts.
No joins infer individual origin/destination. Null never means zero.
"""
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET
import csv,hashlib,json,re,zipfile,math,sys
import numpy as np
from scipy import stats
import pdfplumber
from .ingest import ROOT
from .build import slug

def clean(text):
    # The 2025 matrix duplicates the acute-I glyph with an unmapped CID 141.
    # Remove only that confirmed redundant token, never arbitrary unknown glyphs.
    text=re.sub(r'([Íí])\(cid:141\)',r'\1',str(text or ''))
    return ' '.join(text.replace('\x02','-').split())
def canonical(text):
    text=slug(text)
    return text

STATES=['AGUASCALIENTES','BAJA CALIFORNIA','BAJA CALIFORNIA SUR','CAMPECHE','CHIAPAS','CHIHUAHUA','CIUDAD DE MÉXICO','COAHUILA','COLIMA','DURANGO','ESTADO DE MÉXICO','GUANAJUATO','GUERRERO','HIDALGO','JALISCO','MICHOACÁN','MORELOS','NAYARIT','NUEVO LEÓN','OAXACA','PUEBLA','QUERÉTARO','QUINTANA ROO','SAN LUIS POTOSÍ','SINALOA','SONORA','TABASCO','TAMAULIPAS','TLAXCALA','VERACRUZ','YUCATÁN','ZACATECAS']
STATE_ALIASES={canonical(s):s for s in STATES}
STATE_ALIASES.update({'distrito-federal':'CIUDAD DE MÉXICO','mexico':'ESTADO DE MÉXICO','coahuila-de-zaragoza':'COAHUILA','michoacan-de-ocampo':'MICHOACÁN','veracruz-de-ignacio-de-la-llave':'VERACRUZ'})
def state_name(s):return STATE_ALIASES.get(canonical(s))
def number(s):
    s=clean(s).replace(',','')
    return float(s) if re.fullmatch(r'\d+(?:\.\d+)?',s) else None
def verified(source):
    path=ROOT/source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:raise ValueError('Source hash mismatch: '+source['id'])
    return path

def academic_record(source,state,name,values,registered=False,split_score=False,page=None):
    nums=[number(v) for v in values]
    registered_count=nums.pop(0) if registered else None
    if len(nums)<3:return None
    examined,selected=nums[:2];score=nums[-1]
    if examined is None or examined<=0:return None
    if selected is not None and (selected<0 or selected>examined):raise ValueError(f'Invalid selected count {source["year"]}: {name}')
    if score is not None and not 0<=score<=100:raise ValueError(f'Invalid score {name}')
    for value in [registered_count,examined,selected]:
        if value is not None and value!=int(value):raise ValueError('Fractional count')
    raw_state=state
    return {'id':slug((state or 'sin-entidad')+' '+name),'name':name,'state':state_name(state) if state else None,'state_original':raw_state,'year':source['year'],'registered':int(registered_count) if registered_count is not None else None,'examined':int(examined),'selected':int(selected) if selected is not None else None,'score':score,'score_statistic':source.get('score_statistic','mean'),'rate':100*selected/examined if selected is not None else None,'population':'mexicana','source_id':source['id'],'page':page,'original_values':values,'score_comparable_group':None,'rate_comparable_group':None,'identity_status':'exact_normalized_name_and_source_state','geographic_note':'Entidad de escuela en la fuente; no residencia del sustentante'}

def academic_doc(source):
    text=(ROOT/'data/staging'/f'{source["id"]}.txt').read_text(encoding='utf-8')
    source['score_statistic']='median' if 'MEDIANA' in text.upper()[:1500] else 'mean'
    # Do not include the later foreign-category table.
    text=re.split(r'M[ée]dicos\s+(?:con\s+)?categor[ií]a\s+extranjera|TOTAL DE M[ÉE]DICOS EXTRANJEROS',text,flags=re.I)[0]
    year=source['year'];rows=[];state=None;parent=None
    if year in (2010,2014,2015):
        tokens=[clean(x) for x in re.split(r'[\t\r\n]+',text) if clean(x)]
        for i,token in enumerate(tokens):
            if state_name(token):state=token;continue
            count=6 if year==2010 else 4
            if i+count<len(tokens) and all(number(t) is not None for t in tokens[i+1:i+count+1]) and number(token) is None and not token.upper().startswith('TOTAL'):
                row=academic_record(source,state,token,tokens[i+1:i+count+1],registered=True,split_score=year==2010)
                if row:rows.append(row)
        return rows
    chunks=re.split(r'\t[ \t]*\r?\n|\t{2,}' if year==2006 else r'\t[ \t]*\r?\n|\t{3,}',text)
    for chunk in chunks:
        cells=[clean(c) for c in chunk.strip('\r\n').split('\t')]
        while cells and not cells[-1]:cells.pop()
        if not cells:continue
        # State headings may occupy an otherwise empty row.
        if state_name(cells[0]):state=cells[0];parent=None
        numeric=next((i for i,v in enumerate(cells) if number(v) is not None),None)
        if numeric is None:
            meaningful=[c for c in cells if c and not state_name(c)]
            if year<2009 and meaningful and ('Universidad Nacional Aut' in meaningful[0] or 'Instituto Politécnico Nacional' in meaningful[0]):parent=meaningful[0]
            continue
        name_cells=[c for c in cells[:numeric] if c and not state_name(c)]
        if not name_cells:continue
        name=clean(' '.join(name_cells))
        if re.search(r'\bTOTAL\b|M[ÉE]DICOS EXTRANJEROS|Nota:',name,re.I):continue
        if year<2009 and parent and not re.search(r'Universidad|Instituto|Escuela Libre',name,re.I):name=parent+' · '+name
        values=cells[numeric:]
        expected=3 if year>=2017 else 4 if year>=2012 else 5 if year in (2007,2008) else 6
        # Empty selected cells must remain missing, not be shifted.
        if len(values)!=expected:continue
        row=academic_record(source,state,name,values,registered=(expected in (4,6)),split_score=expected>=5)
        if row:rows.append(row)
    return rows

def academic_docx(source):
    with zipfile.ZipFile(verified(source)) as z:root=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};rows=[]
    for row in root.findall('.//w:tr',ns):
        cells=[clean(' '.join(t.text or '' for t in c.findall('.//w:t',ns))) for c in row.findall('w:tc',ns)]
        if len(cells)==5 and number(cells[2]) is not None:
            rec=academic_record(source,cells[0],cells[1],cells[2:])
            if rec:rows.append(rec)
    return rows

def academic_pdf(source):
    if source['year']>=2024:return academic_recent_pdf(source)
    rows=[]
    with pdfplumber.open(verified(source)) as doc:
        for page_no,page in enumerate(doc.pages,1):
            words=page.extract_words();triples=[]
            nums=[w for w in words if number(w['text']) is not None and w['top']>140 and w['x0']>page.width*.5]
            for i in range(len(nums)-2):
                a,b,c=nums[i:i+3]
                if max(a['top'],b['top'],c['top'])-min(a['top'],b['top'],c['top'])<3 and a['x0']<b['x0']<c['x0'] and '.' in c['text']:triples.append((a,b,c))
            # Header state/name divider can be read from column header positions.
            divider=page.find_tables()[0].rows[0].cells[0][2]
            for i,(a,b,c) in enumerate(triples):
                top=(triples[i-1][0]['top']+a['top'])/2 if i else a['top']-12
                bottom=(a['top']+triples[i+1][0]['top'])/2 if i+1<len(triples) else a['bottom']+12
                names=[w for w in words if top<=w['top']<bottom and w['x1']<a['x0']-4]
                state=clean(' '.join(w['text'] for w in names if w['x0']<divider));name=clean(' '.join(w['text'] for w in names if w['x0']>=divider))
                if not name or 'Entidad' in name:raise ValueError(f'Invalid PDF academic row page {page_no}: state={state!r}, name={name!r}, values={[a["text"],b["text"],c["text"]]}')
                rec=academic_record(source,state,name,[a['text'],b['text'],c['text']],page=page_no)
                if rec:rows.append(rec)
    return rows

def academic_recent_pdf(source):
    """2024–25: anchor on the score, retain blank selected cells explicitly.

    Use printed table column and row rectangles, not the presence of three
    numbers. The latter would silently drop the 2024 naval-school observation.
    """
    rows=[]
    with pdfplumber.open(verified(source)) as doc:
        for page_no,page in enumerate(doc.pages,1):
            words=page.extract_words();table=page.find_tables()[0];header=[c for c in table.rows[0].cells if c]
            divider=header[0][2]
            scores=[w for w in words if re.fullmatch(r'\d+\.\d+',w['text']) and w['top']>140 and w['x0']>page.width*.8]
            numeric=[w for w in words if number(w['text']) is not None and w['top']>140 and w['x0']>page.width*.5]
            sample=next(sorted([w for w in numeric if abs(w['top']-c['top'])<3],key=lambda w:w['x0']) for c in scores if len([w for w in numeric if abs(w['top']-c['top'])<3])==3)
            def column(w):
                x=(w['x0']+w['x1'])/2
                return max([b for b in header if b[0]<x<b[2]],key=lambda b:b[2]-b[0])
            count_col,selected_col=column(sample[0]),column(sample[1]);school_x=(divider+count_col[0])/2
            for c in scores:
                cy=(c['top']+c['bottom'])/2
                rectangles=[b for b in table.cells if b[0]<school_x<b[2] and b[1]<cy<b[3] and b[3]-b[1]<100]
                if not rectangles:raise ValueError(f'Missing school row bounds {source["year"]} page {page_no}')
                box=max(rectangles,key=lambda b:b[3]-b[1]);top,bottom=box[1],box[3]
                row_words=[w for w in words if top<= (w['top']+w['bottom'])/2 <bottom]
                def cell_value(col):
                    values=[w['text'] for w in row_words if col[0]<=(w['x0']+w['x1'])/2<col[2] and number(w['text']) is not None]
                    if len(values)>1:raise ValueError('Multiple counts in one academic cell')
                    return values[0] if values else ''
                state=clean(' '.join(w['text'] for w in row_words if w['x0']<divider))
                original_name=clean(' '.join(w['text'] for w in row_words if divider<=w['x0']<count_col[0]))
                name=original_name.replace('C AMPUS','CAMPUS')
                if not name:raise ValueError('Missing academic school name')
                rec=academic_record(source,state,name,[cell_value(count_col),cell_value(selected_col),c['text']],page=page_no)
                if rec:rec['name_original']=original_name;rows.append(rec)
            page.close()
    expected={2024:153,2025:159}
    if len(rows)!=expected[source['year']]:raise ValueError(f'Academic row count {source["year"]}: expected {expected[source["year"]]}, got {len(rows)}')
    return rows

MAJOR={'secretaria-de-salud':'ssa','secretaria-de-salud-ssa':'ssa','instituto-mexicano-del-seguro-social':'imss','instituto-mexicano-del-seguro-social-imss':'imss','instituto-de-seguridad-y-servicios-sociales-de-los-trabajadores-del-estado':'issste','instituto-de-seguridad-y-servicios-sociales-de-los-trabajadores-del-estado-issste':'issste','petroleos-mexicanos':'pemex','petroleos-mexicanos-pemex':'pemex'}
def institution_id(name):return MAJOR.get(slug(name),slug(name))

def receiving_matrix(source,specialty_names):
    names=sorted(specialty_names,key=lambda n:n)
    # Authoritative column order verified in each matrix's rotated header.
    names=[n for n in names if n!='MEDICINA LEGAL' and (source['year']>=2024 or n!='MEDICINA PALIATIVA')]
    rows=[];published_total=None;columns_total=None
    with pdfplumber.open(verified(source)) as doc:
        for page_no,page in enumerate(doc.pages,1):
            words=page.extract_words();by_y=[]
            for w in sorted([w for w in words if re.fullmatch(r'\d+',w['text']) and w.get('upright',True)],key=lambda w:w['top']):
                if by_y and abs(by_y[-1][0]['top']-w['top'])<3:by_y[-1].append(w)
                else:by_y.append([w])
            anchors=[sorted(ws,key=lambda w:w['x0']) for ws in by_y if len(ws)>=len(names)+1]
            for i,ws in enumerate(anchors):
                if len(ws)!=len(names)+1:raise ValueError(f'Matrix numeric columns {source["year"]}: {len(ws)}')
                a=ws[0];prev=anchors[i-1][0]['top'] if i else None;nxt=anchors[i+1][0]['top'] if i+1<len(anchors) else None
                top=(prev+a['top'])/2 if prev is not None else a['top']-18
                bottom=(a['top']+nxt)/2 if nxt is not None else a['bottom']+20
                name=clean(' '.join(w['text'] for w in words if top<=w['top']<bottom and w['x1']<a['x0']-1 and w.get('upright',True)))
                vals=list(map(lambda w:int(w['text']),ws))
                if sum(vals[:-1])!=vals[-1]:raise ValueError(f'Matrix row total mismatch {source["year"]}: {name}')
                if slug(name)=='total':published_total=vals[-1];columns_total=vals[:-1];continue
                if not name:raise ValueError('Missing institution name')
                for specialty,count in zip(names,vals[:-1]):rows.append({'institution_id':institution_id(name),'institution_name':name,'specialty_id':slug(specialty),'specialty':specialty,'year':source['year'],'places':count,'population':'mexicana','place_type':'oferta_publicada_R1','stage':'snapshot_matriz_publicada','source_id':source['id'],'page':page_no,'state':None,'site_id':None,'cutoff':None})
    if published_total is None:raise ValueError('Missing published national total')
    if sum(r['places'] for r in rows)!=published_total:raise ValueError(f'Matrix grand total mismatch {source["year"]}: extracted {sum(r["places"] for r in rows)} vs published {published_total}; {len(rows)//len(names)} institutions')
    for specialty,value in zip(names,columns_total):
        if sum(r['places'] for r in rows if r['specialty']==specialty)!=value:raise ValueError('Matrix column total mismatch')
    source['published_total']=published_total
    return rows

def concentration(values):
    v=np.asarray(values,dtype=float);total=float(v.sum())
    if total<=0:return {'total':0,'hhi':None,'gini':None,'top3':None,'top5':None,'lorenz':[]}
    v=np.sort(v);n=len(v);shares=v/total
    return {'total':int(total),'hhi':float(np.sum(shares**2)*10000),'gini':float((2*np.sum(np.arange(1,n+1)*v)/(n*total))-(n+1)/n),'top3':float(np.sum(shares[-3:])*100),'top5':float(np.sum(shares[-5:])*100),'lorenz':[[0,0]]+[[float((i+1)/n),float(s)] for i,s in enumerate(np.cumsum(shares))]}

def receiving_sites(source):
    kind=Path(source['file']).stem.split('-')[-1]
    columns={'salud':[14,107.7,146.5,331.7,643,811.2,923.5],'imss':[14,136.3,183,340.85,467.6,578.4,696.2,804.4,923.5],'issste':[14,95.76,133.9,351.77,570.1,710.7,923.5],'pemex':[14,101.78,150.7,394.86,593.93,745.4,923.5],'total':[14,101.78,142.22,291.86,406.13,732.31,794.98,923.5]}[kind]
    rows=[]
    with pdfplumber.open(verified(source)) as doc:
        for page_no,page in enumerate(doc.pages,1):
            words=page.extract_words();boundaries=[]
            raw=sorted(set(e['top'] for e in page.edges if e['orientation']=='h' and e['x0']<16 and columns[1]-1<e['x1']<columns[1]+2))
            for y in raw:
                if boundaries and y-boundaries[-1]<2:boundaries[-1]=(boundaries[-1]+y)/2
                else:boundaries.append(y)
            for top,bottom in zip(boundaries,boundaries[1:]):
                if top<139:continue
                cells=[clean(' '.join(w['text'] for w in words if top<w['top']<bottom-1 and left<=(w['x0']+w['x1'])/2<right)) for left,right in zip(columns,columns[1:])]
                code=cells[0].replace(' ','')
                if not code.startswith('CODUNI'):continue
                if not re.fullmatch(r'CODUNI2025_\d{5}',code):raise ValueError(f'Invalid code {code}, {source["id"]}, page {page_no}')
                if number(cells[1]) is None:raise ValueError('Missing site count '+code)
                if kind=='imss':
                    _,count,specialty,site,state,subsite,substate,aval=cells;institution='INSTITUTO MEXICANO DEL SEGURO SOCIAL'
                elif kind=='total':
                    _,count,specialty,institution,site,state,aval=cells;subsite=None;substate=None
                else:
                    _,count,specialty,site,state,aval=cells;subsite=None;substate=None
                    institution={'salud':'SECRETARÍA DE SALUD','issste':'INSTITUTO DE SEGURIDAD Y SERVICIOS SOCIALES DE LOS TRABAJADORES DEL ESTADO','pemex':'PETRÓLEOS MEXICANOS'}[kind]
                if not state_name(state):raise ValueError(f'Unknown state {state!r} for {code}')
                if not specialty or not site:raise ValueError('Missing site identity '+code)
                rows.append({'code':code,'site_id':slug(institution+' '+site+' '+state),'name':site,'institution_id':institution_id(institution),'institution_name':institution,'specialty_id':slug(specialty),'specialty':specialty,'state':state_name(state),'state_original':state,'subsite':subsite,'substate':state_name(substate) if substate else None,'academic_endorsement':aval,'places':int(number(count)),'year':2025,'population':'mexicana','place_type':'oferta_publicada_R1','stage':'snapshot_listado_sedes_publicado','cutoff':None,'clues':None,'latitude':None,'longitude':None,'source_id':source['id'],'page':page_no})
            page.close()
    if len({r['code'] for r in rows})!=len(rows):raise ValueError('Duplicate site-offer code within source')
    return rows

def binomial_interval(selected,examined):
    if selected is None or not examined:return None
    p=selected/examined;z=1.95996398454;den=1+z*z/examined;mid=(p+z*z/(2*examined))/den;half=z*math.sqrt(p*(1-p)/examined+z*z/(4*examined**2))/den
    return [max(0,100*(mid-half)),min(100,100*(mid+half))]

def national_aggregate(rows):
    n=sum(r['examined'] for r in rows);complete=all(r['selected'] is not None for r in rows);sel=sum(r['selected'] for r in rows) if complete else None
    mean_rows=[r for r in rows if r['score'] is not None and r['score_statistic']=='mean']
    return {'examined':n,'selected':sel,'selected_observed_subtotal':sum(r['selected'] for r in rows if r['selected'] is not None),'selected_missing_rows':sum(r['selected'] is None for r in rows),'rate':100*sel/n if sel is not None and n else None,'score':sum(r['examined']*r['score'] for r in mean_rows)/sum(r['examined'] for r in mean_rows) if len(mean_rows)==len(rows) and mean_rows else None,'institutions':len(rows),'selected_complete':complete,'aggregation':'Suma de filas extraídas, categoría mexicana; no equivale a personas únicas entre ediciones.'}

def main(academic_only=False):
    sources=json.loads((ROOT/'data/platform_sources.json').read_text(encoding='utf-8'));specialties=json.loads((ROOT/'public/data/specialties.json').read_text(encoding='utf-8'))
    academics=[];receiving=[];sites=[];issues=[]
    previous=None
    if academic_only:
        previous=json.loads((ROOT/'data/normalized/platform.json').read_text(encoding='utf8'))
        receiving=previous['receiving'];sites=previous['sites']
    for source in sources:
        if academic_only and source['kind']!='academic':
            old=next((s for s in previous['sources'] if s['id']==source['id']),None)
            if not old or old['sha256']!=source['sha256']:raise ValueError('Non-academic source changed; run full build')
            verified(source)
            for key in ['rows','status','published_total']:
                if key in old:source[key]=old[key]
            continue
        if source['kind']=='academic':
            verified(source)
            try:
                suffix=Path(source['file']).suffix
                rows=academic_pdf(source) if suffix=='.pdf' else academic_docx(source) if suffix=='.docx' else academic_doc(source)
                if len(rows)<40:raise ValueError(f'Too few extracted academic rows: {len(rows)}')
                keys=[r['id'] for r in rows]
                if len(keys)!=len(set(keys)):raise ValueError('Duplicate academic institution within edition')
                source['status']='extracted_checked';source['rows']=len(rows);academics.extend(rows);print('academic',source['year'],len(rows),flush=True)
            except Exception as e:source['status']='quarantined';issues.append({'source_id':source['id'],'error':str(e)});print('QUARANTINE',source['year'],str(e),flush=True)
        elif source['kind']=='receiving_matrix':
            rows=receiving_matrix(source,[s['official_name'] for s in specialties['specialties']]);receiving.extend(rows);source['rows']=len(rows);source['status']='extracted_checked';print('matrix',source['year'],source['published_total'],flush=True)
        elif source['kind']=='receiving_sites':
            rows=receiving_sites(source);sites.extend(rows);source['rows']=len(rows);source['status']='extracted_checked';print('sites',source['file'].split('-')[-1],len(rows),sum(r['places'] for r in rows),flush=True)
    for r in academics:r['rate_interval95']=binomial_interval(r['selected'],r['examined'])
    years=sorted({r['year'] for r in academics});national=[dict(year=y,**national_aggregate([r for r in academics if r['year']==y])) for y in years]
    from .university_identity import university_profiles
    institutions=university_profiles(academics,sources)
    receiving_summary=[dict(year=y,**concentration([sum(r['places'] for r in receiving if r['year']==y and r['institution_id']==id) for id in {r['institution_id'] for r in receiving if r['year']==y}])) for y in sorted({r['year'] for r in receiving})]
    if len({r['code'] for r in sites})!=len(sites):raise ValueError('Duplicate code across receiving sources')
    reconciliation=[]
    for id in ['ssa','imss','issste','pemex']:
        matrix_total=sum(r['places'] for r in receiving if r['year']==2025 and r['institution_id']==id)
        site_total=sum(r['places'] for r in sites if r['institution_id']==id)
        reconciliation.append({'institution_id':id,'matrix_total':matrix_total,'site_total':site_total,'difference':site_total-matrix_total})
        if site_total!=matrix_total:raise ValueError(f'Site reconciliation failed {id}: {site_total} vs {matrix_total}')
    payload={'version':'2.0.0','audit_date':'2026-10-31','academic_years':years,'national':national,'universities':institutions,'academic_records':academics,'receiving':receiving,'receiving_summary':receiving_summary,'sites':sites,'reconciliation':reconciliation,'sources':sources,'issues':issues,'coverage':{'academic':'Filas de categoría mexicana; denominaciones conservadas y sin unión difusa. Puntajes no equiparados entre ediciones.','receiving':'Matrices institucionales R1. Snapshots de oferta publicada; no asignación ni ocupación. No sumar rondas.','geography':'Entidad de escuela o sede según documento, sin inferir domicilio del sustentante.','forecast':'Comparabilidad longitudinal pendiente; sin predicciones publicadas.'}}
    output=ROOT/'public/data/platform.json';output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (ROOT/'data/normalized/platform.json').write_text(output.read_text(encoding='utf-8'),encoding='utf-8')
    (ROOT/'data/platform_validation.json').write_text(json.dumps({'issues':issues,'sources':sources},ensure_ascii=False,indent=2),encoding='utf-8')
    docs=ROOT/'docs'
    with (docs/'platform_source_inventory.csv').open('w',encoding='utf-8',newline='') as f:
        fields=sorted(set().union(*(s.keys() for s in sources)));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(sources)
    with (docs/'receiving_institutions_availability.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['year','institution','specialty','level','place_type','places','source_id','status'])
        w.writerows([r['year'],r['institution_id'],r['specialty_id'],'national_institution','oferta_publicada_R1',r['places'],r['source_id'],'extracted_checked'] for r in receiving)
    print(len(academics),'academic records;',len(institutions),'university identities;',len(receiving),'matrix cells;',len(issues),'quarantined sources')

if __name__=='__main__':main('--academic-only' in sys.argv)
