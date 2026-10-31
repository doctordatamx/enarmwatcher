"""Weekly monitor. Never overwrite approved originals or silently publish candidates."""
import datetime,hashlib,json,re,sys
from urllib.parse import urljoin
from .ingest import ROOT
from .discover import fetch,Links

def main():
    directory=ROOT/'data/staging/candidates';directory.mkdir(parents=True,exist_ok=True)
    sources=json.loads((ROOT/'data/platform_sources.json').read_text(encoding='utf8'))+json.loads((ROOT/'data/sources.json').read_text(encoding='utf8'));report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changed':[],'new_links':[],'errors':[],'unchanged':0}
    if '--retry-errors' in sys.argv:
        report=json.loads((ROOT/'data/update_report.json').read_text(encoding='utf8'));failed={e['url'] for e in report['errors']};sources=[s for s in sources if s['url'] in failed];report['errors']=[];report['retried_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for src in sources:
        try:
            content=fetch(src['url']);digest=hashlib.sha256(content).hexdigest()
            if digest==src['sha256']:report['unchanged']+=1
            else:
                file=directory/(digest+'-'+src['url'].split('/')[-1]);file.write_bytes(content);report['changed'].append({'source_id':src['id'],'url':src['url'],'old_sha256':src['sha256'],'new_sha256':digest,'candidate':str(file.relative_to(ROOT)),'status':'requires_parser_and_comparability_review'})
        except Exception as e:report['errors'].append({'url':src['url'],'error':str(e)})
    known={s['url'] for s in sources};year=datetime.datetime.now(datetime.timezone.utc).year
    indexes=['https://cifrhs.salud.gob.mx/site1/enarm/reportes_academicos.html']+[f'https://cifrhs.salud.gob.mx/site1/enarm/{y}/index.html' for y in [year-1,year]]
    for url in ([] if '--retry-errors' in sys.argv else indexes):
        try:
            text=fetch(url).decode('utf8',errors='replace');links=Links();links.feed(text)
            embedded=[(url,'Reporte académico descubierto en catálogo') for url in re.findall(r'url:\s*"([^"]+\.(?:pdf|docx?))"',text)]
            for href,label in links.links+embedded:
                target=urljoin(url,href)
                if target.startswith('https://cifrhs.salud.gob.mx/') and target.lower().endswith(('.pdf','.doc','.docx')) and target not in known and not any(term in (target+' '+label).lower() for term in ['folio','cuadro','aviso_privacidad']):report['new_links'].append({'url':target,'label':label,'index':url,'status':'discovered_not_validated'})
        except Exception as e:report['errors'].append({'url':url,'error':str(e)})
    report['new_links']=list({r['url']:r for r in report['new_links']}.values())
    (ROOT/'data/update_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v if not isinstance(v,list) else len(v) for k,v in report.items()}))
    if report['errors']:raise SystemExit(1)

if __name__=='__main__':main()
