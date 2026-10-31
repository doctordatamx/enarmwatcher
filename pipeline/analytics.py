"""Version 1.0.0. Pure functions; no ENARM results are generated here.

Analytical eligibility is separate from extraction validity. A comparable block
requires a documented review, never an inference from a similar numeric range.
"""
import math
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster

def eligible(rows, minimum=6, field='minimum'):
    if len(rows) < minimum: return False, f'Se requieren al menos {minimum} ediciones; hay {len(rows)}.'
    if any(r.get(field) is None for r in rows): return False, 'Existen datos faltantes.'
    if any(not isinstance(r[field],(int,float)) or not math.isfinite(r[field]) for r in rows):return False, 'Existen valores no finitos o no numéricos.'
    if field=='pressure' and any(not r.get('demand_comparable') for r in rows):return False, 'La compatibilidad de aspirantes y plazas no está validada.'
    blocks = {r.get('comparable_group') for r in rows}
    if None in blocks or len(blocks) != 1: return False, 'Comparabilidad histórica pendiente o periodos incompatibles.'
    if len({(r['population'],r['stage']) for r in rows}) != 1: return False, 'Población o etapa incompatible.'
    years = sorted(r['year'] for r in rows)
    if years != list(range(years[0],years[-1]+1)): return False, 'La serie contiene huecos temporales.'
    return True, None

def pressure(row):
    a, p = row.get('applicants'), row.get('places')
    if not row.get('demand_comparable') or a is None or p is None or p <= 0 or a<0 or not math.isfinite(a) or not math.isfinite(p): return None
    return a / p

def volatility(rows):
    rows=sorted(rows,key=lambda r:r['year']);ok,reason=eligible(rows)
    if not ok:return {'available':False,'reason':reason}
    values=np.array([r['minimum'] for r in rows]); changes=np.diff(values)
    return {'available':True,'sd':float(values.std(ddof=1)),'iqr':float(np.quantile(values,.75)-np.quantile(values,.25)),'range':float(np.ptp(values)),'yearly_changes':[{'year':r['year'],'absolute':float(d),'relative_percent':float(100*d/prev) if prev!=0 else None} for r,d,prev in zip(rows[1:],changes,values[:-1])],'warning':'Variabilidad de mínimos temporales; no es dispersión individual de sustentantes.'}

def robust_trend(rows, field='minimum'):
    rows=sorted(rows,key=lambda r:r['year'])
    ok, reason = eligible(rows, field=field)
    if not ok: return {'available':False,'reason':reason}
    x = np.array([r['year'] for r in rows]); y = np.array([r[field] for r in rows])
    fit = stats.theilslopes(y,x,alpha=.95)
    changes = [rows[i][field]-rows[i-1][field] for i in range(1,len(rows))]
    return {'available':True,'method':'Theil–Sen','slope':float(fit.slope),'intercept':float(fit.intercept),'fitted':[{'year':int(year),'value':float(fit.intercept+fit.slope*year)} for year in x],'slope_ci':[float(fit.low_slope),float(fit.high_slope)],'sd':float(np.std(y,ddof=1)),'changes':changes,'n':len(rows)}

def segmented(rows, field='minimum'):
    rows=sorted(rows,key=lambda r:r['year'])
    ok, reason = eligible(rows, minimum=10, field=field)
    if not ok: return {'available':False,'reason':reason}
    x = np.array([r['year'] for r in rows],dtype=float); x -= x[0]
    y = np.array([r[field] for r in rows]); n=len(y)
    base=np.column_stack([np.ones(n),x]); b=np.linalg.lstsq(base,y,rcond=None)[0]
    base_bic=n*math.log(max(float(np.sum((y-base@b)**2))/n,1e-12))+2*math.log(n)
    candidates=[]
    for k in range(3,n-3):
        design=np.column_stack([base,np.maximum(x-x[k],0)])
        coef=np.linalg.lstsq(design,y,rcond=None)[0]
        bic=n*math.log(max(float(np.sum((y-design@coef)**2))/n,1e-12))+4*math.log(n)
        candidates.append((bic,k,coef))
    bic,k,coef=min(candidates,key=lambda a:a[0])
    return {'available':True,'method':'Regresión continua con bisagra; búsqueda exploratoria BIC','candidate_year':rows[k]['year'],'bic_gain':base_bic-bic,'supported':bool(base_bic-bic>6),'slopes':[float(coef[1]),float(coef[1]+coef[2])],'fitted':[{'year':r['year'],'value':float(value)} for r,value in zip(rows,np.column_stack([base,np.maximum(x-x[k],0)])@coef)],'warning':'Punto exploratorio, sin interpretación causal; sensibilidad a longitud mínima de segmentos.'}

def forecast(rows, field='minimum'):
    ok, reason = eligible(rows, minimum=14, field=field)
    if not ok: return {'available':False,'reason':reason}
    rows=sorted(rows,key=lambda r:r['year']); y=np.array([r[field] for r in rows]); x=np.array([r['year'] for r in rows])
    errors={'naive':[],'theil_sen':[]}; backtests=[]
    # Rolling origins, no future observation enters a fitted training window.
    for t in range(6,len(rows)):
        naive=y[t-1]; fit=stats.theilslopes(y[:t],x[:t]); pred=fit.intercept+fit.slope*x[t]
        errors['naive'].append(float(y[t]-naive)); errors['theil_sen'].append(float(y[t]-pred))
        backtests.append({'year':int(x[t]),'actual':float(y[t]),'naive':float(naive),'theil_sen':float(pred)})
    metrics={k:{'mae':float(np.mean(np.abs(v))),'rmse':float(np.sqrt(np.mean(np.square(v))))} for k,v in errors.items()}
    winner=min(metrics,key=lambda k:metrics[k]['mae'])
    residuals=errors[winner]; q=float(np.quantile(np.abs(residuals),.9,method='higher'))
    fit=stats.theilslopes(y,x); point=float(y[-1] if winner=='naive' else fit.intercept+fit.slope*(x[-1]+1))
    if not math.isfinite(point) or point<0 or (field=='minimum' and point>100):return {'available':False,'reason':'La predicción excede el dominio válido.','metrics':metrics,'backtests':backtests}
    # Prequential interval evaluation: width uses only earlier validation errors.
    cover=[abs(residuals[i])<=float(np.quantile(np.abs(residuals[:i]),.9,method='higher')) for i in range(4,len(residuals))]
    coverage=float(np.mean(cover)) if cover else None
    if coverage is None or coverage<.75: return {'available':False,'reason':'Cobertura retrospectiva insuficiente para publicar proyección.','metrics':metrics,'backtests':backtests}
    return {'available':True,'model':winner,'metrics':metrics,'backtests':backtests,'year':int(x[-1]+1),'point':point,'interval90':[max(0,point-q),min(100,point+q)] if field=='minimum' else [max(0,point-q),point+q],'coverage':coverage,'warning':'Intervalo predictivo empírico exploratorio; no garantiza cobertura futura.'}

def convergence(series):
    if len(series)<5: return {'available':False,'reason':'Se requieren al menos cinco especialidades en panel balanceado.'}
    common=set.intersection(*(set(r['year'] for r in rows) for rows in series.values()))
    if len(common)<6:return {'available':False,'reason':f'El panel de {len(series)} especialidades tiene {len(common)} ediciones comunes; se requieren al menos 6. Revisar composición y cobertura antes del análisis.'}
    panel={key:sorted([r for r in rows if r['year'] in common],key=lambda r:r['year']) for key,rows in series.items()}
    for rows in panel.values():
        ok,reason=eligible(rows)
        if not ok:return {'available':False,'reason':reason}
    if len({r['comparable_group'] for rows in panel.values() for r in rows})!=1:return {'available':False,'reason':'Bloques no comparables entre especialidades.'}
    arr=np.array([[r['minimum'] for r in rows] for rows in panel.values()]); years=sorted(common)
    sigma=np.std(arr,axis=0,ddof=1); initial=arr[:,0]; change=(arr[:,-1]-initial)/(years[-1]-years[0])
    beta=stats.linregress(initial,change) if np.std(initial)>0 else None
    return {'available':True,'years':years,'balanced_specialties':list(panel),'sigma':sigma.tolist(),'gap_p90_p10':(np.quantile(arr,.9,axis=0)-np.quantile(arr,.1,axis=0)).tolist(),'beta':float(beta.slope) if beta else None,'warning':'Panel balanceado; asociación descriptiva, sin causalidad.'}

def longitudinal_clusters(series):
    conv=convergence(series)
    if not conv['available']:return conv
    years=conv['years']; names=list(series)
    arr=np.array([[next(r['minimum'] for r in series[s] if r['year']==y) for y in years] for s in names])
    # Per-year standardization across specialties preserves relative level and path.
    scale=arr.std(axis=0); z=(arr-arr.mean(axis=0))/np.where(scale>0,scale,1)
    k=min(3,len(names)-1); labels=fcluster(linkage(z,method='ward'),k,criterion='maxclust')
    rng=np.random.default_rng(47); stability=[]
    for _ in range(100):
        sample=z[:,rng.choice(len(years),len(years),replace=True)]
        other=fcluster(linkage(sample,method='ward'),k,criterion='maxclust')
        # Pairwise agreement is invariant to arbitrary cluster numbering.
        mask=np.triu(np.ones((len(names),len(names)),dtype=bool),1)
        stability.append(float(np.mean(((labels[:,None]==labels)==(other[:,None]==other))[mask])))
    agreement=float(np.mean(stability))
    return {'available':agreement>=.8,'reason':None if agreement>=.8 else 'Partición inestable en remuestreo de años.','groups':dict(zip(names,map(int,labels))),'pairwise_stability':agreement,'method':'Ward, z por año, 100 remuestreos de años; semilla 47','warning':'Perfiles exploratorios, sin etiquetas de calidad. La estabilidad depende del esquema de remuestreo.'}

def rank_stability(series):
    panel=convergence(series)
    if not panel['available']:return panel
    years=panel['years'];names=list(series)
    values=np.array([[next(r['minimum'] for r in series[s] if r['year']==y) for y in years] for s in names])
    ranks=np.column_stack([stats.rankdata(-values[:,i],method='average') for i in range(len(years))])
    correlations=[]
    for i in range(1,len(years)):
        rho=stats.spearmanr(ranks[:,i-1],ranks[:,i]).statistic if np.std(ranks[:,i-1])>0 and np.std(ranks[:,i])>0 else None
        correlations.append({'year':years[i],'spearman':float(rho) if rho is not None else None})
    return {'available':True,'years':years,'panel':names,'ranks':dict(zip(names,ranks.tolist())),'rank_sd':dict(zip(names,map(float,ranks.std(axis=1,ddof=1)))),'yearly_correlations':correlations,'warning':'Panel balanceado; empates con rango medio. Posición por umbral, no calidad.'}
