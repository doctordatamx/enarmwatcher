"""Download pinned official documents. Raw bytes and hashes are preserved."""
from pathlib import Path
import urllib.request, hashlib, json, datetime

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    2022: 'https://cifrhs.salud.gob.mx/site1/enarm/_2022/docs/E46_puntajes_max_min_2022.pdf',
    2023: 'https://cifrhs.salud.gob.mx/site1/enarm/2023/docs/E47_puntajes_max_min_2023.pdf',
    2024: 'https://cifrhs.salud.gob.mx/site1/enarm/2024/docs/2024-ENARM-puntajes.pdf',
    2025: 'https://cifrhs.salud.gob.mx/site1/enarm/2025/docs/2025-ENARM-puntajes.pdf',
}

def main():
    folder = ROOT / 'data/raw'
    folder.mkdir(parents=True, exist_ok=True)
    inventory = []
    for year, url in SOURCES.items():
        path = folder / f'{year}-puntajes.pdf'
        if not path.exists():
            req = urllib.request.Request(url, headers={'User-Agent':'ENARMWatcher/0.1 source-audit'})
            with urllib.request.urlopen(req, timeout=90) as response:
                content = response.read()
            if not content.startswith(b'%PDF'): raise ValueError(f'Not PDF: {url}')
            path.write_bytes(content)
        content = path.read_bytes()
        inventory.append({'id':f'cifrhs-{year}-puntajes','year':year,'edition':year-1976,'issuer':'CIFRHS / Secretaría de Salud','url':url,'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(content).hexdigest(),'downloaded_at':datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),'parser_version':'1.0.0','status':'downloaded','document_type':'Puntajes máximos y mínimos de seleccionados','stage':'Documento de seleccionados publicado; ronda no especificada en tabla','cutoff':None})
    (ROOT/'data/sources.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(inventory)} official PDFs archived')

if __name__ == '__main__': main()
