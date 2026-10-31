"""Reproducible descriptive composition analyses on one matrix at a time."""
import json
import numpy as np
from scipy.cluster.hierarchy import linkage,fcluster
from .ingest import ROOT
from .platform import concentration

def analyse(rows):
    names={r['institution_id']:r['institution_name'] for r in rows};specialties=sorted({r['specialty_id'] for r in rows});ids=sorted(names)
    a=np.array([[sum(r['places'] for r in rows if r['institution_id']==id and r['specialty_id']==s) for s in specialties] for id in ids],dtype=float)
    totals=a.sum(axis=1);columns=a.sum(axis=0);total=float(a.sum());shares=a/np.maximum(totals[:,None],1)
    reference=columns/total;lq=shares/np.where(reference>0,reference,1)
    entropy=-np.sum(np.where(shares>0,shares*np.log(np.maximum(shares,1e-15)),0),axis=1)
    diversity=[{'id':id,'name':names[id],'places':int(totals[i]),'specialties':int(np.sum(a[i]>0)),'shannon':float(entropy[i]),'effective_specialties':float(np.exp(entropy[i])),'within_hhi':float(np.sum(shares[i]**2)*10000)} for i,id in enumerate(ids)]
    # Hellinger profiles avoid making volume itself the similarity metric.
    z=np.sqrt(shares);labels=fcluster(linkage(z,method='ward'),3,criterion='maxclust');rng=np.random.default_rng(47);agreement=[];mask=np.triu(np.ones((len(ids),len(ids)),dtype=bool),1)
    for _ in range(100):
        indices=rng.choice(len(specialties),len(specialties),replace=True);other=fcluster(linkage(z[:,indices],method='ward'),3,criterion='maxclust');agreement.append(float(np.mean(((labels[:,None]==labels)==(other[:,None]==other))[mask])))
    # Correspondence analysis of the contingency matrix, not individual mobility.
    p=a/total;r=p.sum(axis=1);c=p.sum(axis=0);active=c>0;residual=(p[:,active]-r[:,None]*c[active])/np.sqrt(np.maximum(r[:,None]*c[active],1e-15));u,s,v=np.linalg.svd(residual,full_matrices=False);coords=u[:,:2]*s[:2]/np.sqrt(np.maximum(r[:,None],1e-15));inertia=s*s
    return {'concentration':concentration(totals),'institutions':diversity,'specialty_ids':specialties,'relative_specialization':[{'institution_id':id,'specialty_id':sp,'ratio':float(lq[i,j]),'places':int(a[i,j])} for i,id in enumerate(ids) for j,sp in enumerate(specialties) if a[i,j]>0],'clusters':{'method':'Ward sobre raíz cuadrada de participaciones; k=3; remuestreo de especialidades, 100 repeticiones, semilla 47','pairwise_agreement':float(np.mean(agreement)),'available':bool(np.mean(agreement)>=.8),'labels':dict(zip(ids,map(int,labels))),'warning':'Sensibilidad exploratoria a composición de especialidades; no implica calidad ni estabilidad longitudinal.'},'correspondence':{'method':'SVD de residuos estandarizados de tabla de contingencia','points':[{'id':id,'name':names[id],'x':float(coords[i,0]),'y':float(coords[i,1])} for i,id in enumerate(ids)],'inertia_explained':list(map(float,inertia[:2]/max(inertia.sum(),1e-15))),'warning':'Proximidad en composición de oferta; no representa movilidad de residentes.'}}

def main():
    data=json.loads((ROOT/'data/normalized/platform.json').read_text(encoding='utf8'));years=sorted({r['year'] for r in data['receiving']});out={'version':'2.0.0','years':years,'results':{str(y):analyse([r for r in data['receiving'] if r['year']==y]) for y in years}}
    (ROOT/'public/data/receiving-analysis.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf8');print('Institutional composition analytics prepared')

if __name__=='__main__':main()
