"""Discover official links, snapshot source files, and preserve original bytes.

No selection folios or personal applicant lists are downloaded.
"""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin,urlparse
from pathlib import Path
import re,json,hashlib,datetime,time
from .ingest import ROOT

# Official academic PDFs discovered outside the historical catalogue's active
# script entries. Keep exact published filenames, including ENARx in 2024.
RECENT_ACADEMIC = {
    2024: 'https://cifrhs.salud.gob.mx/site1/enarm/2024/docs/2024-ENARx_Reporte-Academico.pdf',
    2025: 'https://cifrhs.salud.gob.mx/site1/enarm/2025/docs/2025-ENARM_Reporte-Academico.pdf',
}

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.href=None;self.label=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.href=dict(attrs).get('href');self.label=[]
    def handle_data(self,text):
        if self.href:self.label.append(text)
    def handle_endtag(self,tag):
        if tag=='a' and self.href:self.links.append((self.href,' '.join(self.label).strip()));self.href=None

def fetch(url):
    # Only official public sources; no insecure TLS fallback.
    if urlparse(url).hostname!='cifrhs.salud.gob.mx':raise ValueError('Unapproved source hostname')
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'ENARMWatcher/0.2 public-source-audit'}),timeout=45) as r:return r.read()
        except HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==2:raise
        except (URLError,ConnectionError,TimeoutError,OSError):
            if attempt==2:raise
        time.sleep(1+attempt)

def main():
    directory=ROOT/'data/raw/platform';directory.mkdir(parents=True,exist_ok=True)
    manifest_path=ROOT/'data/platform_sources.json'
    existing={s['url']:s for s in json.loads(manifest_path.read_text(encoding='utf-8'))} if manifest_path.exists() else {}
    found=[(year,'academic',url,'Reporte académico') for year,url in RECENT_ACADEMIC.items()];discovery=[];errors=[]
    academic_url='https://cifrhs.salud.gob.mx/site1/enarm/reportes_academicos.html'
    html=fetch(academic_url).decode('utf-8',errors='replace')
    (directory/'academic-index.html').write_text(html,encoding='utf-8')
    # Official index embeds its academic file catalogue in a script.
    for year,url in re.findall(r'anio:\s*"(\d{4})"[^\n]+?url:\s*"([^"]+\.(?:pdf|docx?))"',html):found.append((int(year),'academic',url,'Reporte académico'))
    for year in range(2022,2026):
        url=f'https://cifrhs.salud.gob.mx/site1/enarm/{year}/index.html'
        try:
            text=fetch(url).decode('utf-8',errors='replace');(directory/f'{year}-index.html').write_text(text,encoding='utf-8')
            parser=Links();parser.feed(text)
            for href,label in parser.links:
                target=urljoin(url,href)
                if urlparse(target).hostname!='cifrhs.salud.gob.mx' or not target.lower().endswith('.pdf'):continue
                discovery.append({'year':year,'url':target,'label':label,'index':url})
                # Pick only first-round main matrix and original institution files.
                name=target.split('/')[-1].lower()
                if year==2023 and name=='2023-enarm-plaza-especialidad-mex.pdf':found.append((year,'receiving_matrix',target,label))
                if year==2024 and name=='2024-enarm-plazas-mex.pdf':found.append((year,'receiving_matrix',target,label))
                if year==2025 and name=='plazas_sicco_plazas-mex-directa.pdf':found.append((year,'receiving_matrix',target,label))
                if year==2025 and re.fullmatch(r'Plazas_sicco_plazas-mex-directa-(salud|imss|issste|pemex|total)\.pdf',target.split('/')[-1],re.I):found.append((year,'receiving_sites',target,label))
                if year in (2022,2023) and ('plazas' in name or 'plaza' in name) and ('mex' in name) and ('directa' in name or 'plazas_mex' in name):found.append((year,'receiving_candidate',target,label))
        except Exception as e:errors.append({'url':url,'error':str(e)})
    for year,kind,url,label in dict.fromkeys(found):
        if url in existing:continue
        try:
            content=fetch(url);filename=f'{year}-{kind}-{url.split("/")[-1]}';path=directory/filename;path.write_bytes(content)
            source={'id':f'{kind}-{year}-'+hashlib.sha256(url.encode()).hexdigest()[:8],'kind':kind,'year':year,'edition':year-1976,'url':url,'title':label,'issuer':'CIFRHS / Secretaría de Salud','file':str(path.relative_to(ROOT)).replace('\\','/'),'downloaded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(content).hexdigest(),'parser_version':'2.0.0','status':'downloaded','population':'mexicana','stage':'published-academic' if kind=='academic' else 'oferta publicada R1, snapshot de documento; no asignación ni ocupación','cutoff':None}
            existing[url]=source;print(year,kind,len(content),flush=True)
            manifest_path.write_text(json.dumps(list(existing.values()),ensure_ascii=False,indent=2),encoding='utf-8')
            time.sleep(.2)
        except Exception as e:errors.append({'url':url,'error':str(e)})
    (ROOT/'data/discovery.json').write_text(json.dumps({'links':discovery,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Sources',len(existing),'errors',len(errors))

if __name__=='__main__':main()
