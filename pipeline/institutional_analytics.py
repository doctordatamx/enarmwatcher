"""Cross-sectional university analytics. No causal or individual claims."""
import math
import numpy as np
from scipy import stats,optimize,special
from .platform import concentration

def partial_pooling(rows):
    valid=[r for r in rows if r['selected'] is not None and r['examined']>0]
    if len(valid)<10:return {'available':False,'reason':'Se requieren al menos diez instituciones con conteos compatibles.'}
    n=np.array([r['examined'] for r in valid]);k=np.array([r['selected'] for r in valid])
    def loss(par):
        a,b=np.exp(par);return -float(np.sum(special.betaln(k+a,n-k+b)-special.betaln(a,b)))
    fit=optimize.minimize(loss,np.log([2.,5.]),bounds=[(-8,12),(-8,12)],method='L-BFGS-B')
    if not fit.success:return {'available':False,'reason':'No convergió la estimación de hiperparámetros.'}
    a,b=np.exp(fit.x)
    return {'available':True,'method':'Beta-binomial empírico Bayes; máxima verosimilitud marginal','alpha':float(a),'beta':float(b),'institutions':[{'id':r['id'],'raw':100*r['selected']/r['examined'],'pooled':float(100*(r['selected']+a)/(r['examined']+a+b)),'interval95':list(map(float,100*stats.beta.ppf([.025,.975],r['selected']+a,r['examined']-r['selected']+b)))} for r in valid],'warning':'Modelo de intercambio entre instituciones; intervalos posteriores condicionados a hiperparámetros estimados. No incorpora toda su incertidumbre ni estima calidad causal.'}

def cross_section(rows):
    valid=[r for r in rows if r['selected'] is not None and r['rate'] is not None and r['examined']>0]
    if len(valid)<3:return {'available':False,'reason':'Menos de tres observaciones completas.'}
    x=np.array([r['examined'] for r in valid]);y=np.array([r['rate'] for r in valid]);ranks=stats.rankdata(-y,method='average')
    rho=float(stats.spearmanr(x,y).statistic) if np.std(y)>0 and np.std(x)>0 else None
    pearson=float(stats.pearsonr(x,y).statistic) if np.std(y)>0 and np.std(x)>0 else None
    frontier=[r['id'] for r in valid if not any(o['examined']>=r['examined'] and o['rate']>=r['rate'] and (o['examined']>r['examined'] or o['rate']>r['rate']) for o in valid)]
    weighted_mean=float(np.average(y,weights=x));groups={r['state'] for r in valid if r['state']};geo=[r for r in valid if r['state']]
    if geo:
        weights=np.array([r['examined'] for r in geo]);rates=np.array([r['rate'] for r in geo]);overall=float(np.average(rates,weights=weights));total=float(np.average((rates-overall)**2,weights=weights));between=0.;within=0.;den=weights.sum()
        for state in groups:
            group=[r for r in geo if r['state']==state];ns=np.array([r['examined'] for r in group]);ys=np.array([r['rate'] for r in group]);mean=float(np.average(ys,weights=ns));between+=float(ns.sum()/den*(mean-overall)**2);within+=float(np.sum(ns*(ys-mean)**2)/den)
        decomposition={'total':total,'between':between,'within':within,'unit':'puntos porcentuales al cuadrado; ponderación por sustentantes','n':len(geo)}
    else:decomposition=None
    return {'available':True,'n':len(valid),'spearman':rho,'pearson':pearson,'weighted_rate':weighted_mean,'rankings':[{'id':r['id'],'rank':float(rank),'percentile':float(100*(len(valid)-rank)/(len(valid)-1))} for r,rank in zip(valid,ranks)],'pareto_ids':frontier,'concentration_examined':concentration(x),'concentration_selected':concentration([r['selected'] for r in valid]),'variance_decomposition':decomposition,'pooling':partial_pooling(valid),'warning':'Asociación ecológica dentro de una edición. El denominador compartido puede inducir asociación volumen–tasa; no estima probabilidad individual ni valor agregado causal.'}

def main():
    import json
    from .ingest import ROOT
    data=json.loads((ROOT/'public/data/platform.json').read_text(encoding='utf8'))
    out={'version':'2.0.0','years':data['academic_years'],'results':{str(y):cross_section([r for r in data['academic_records'] if r['year']==y]) for y in data['academic_years']}}
    (ROOT/'public/data/research.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf8')
    from .analytics import robust_trend,volatility,segmented,forecast,convergence,rank_stability,longitudinal_clusters
    series={u['id']:[dict(r,minimum=r['rate'],population='mexicana',stage='academic-published',comparable_group=r['rate_comparable_group']) for r in u['records']] for u in data['universities']}
    longitudinal={'version':'2.0.0','field':'rate','unit':'porcentaje','special_note':'El campo minimum es un adaptador interno del motor genérico; aquí representa tasa institucional, no umbral. No se aplica equiparación implícita.','institutions':{id:{'trend':robust_trend(rows),'volatility':volatility(rows),'segmented':segmented(rows),'forecast':forecast(rows)} for id,rows in series.items()},'convergence':convergence(series),'rank_stability':rank_stability(series),'clusters':longitudinal_clusters(series)}
    (ROOT/'public/data/academic-longitudinal.json').write_text(json.dumps(longitudinal,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf8')
    print('Cross-sectional research prepared for',len(out['years']),'editions')

if __name__=='__main__':main()
