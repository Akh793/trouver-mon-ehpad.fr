# -*- coding: utf-8 -*-
import json, os, math
OUT='../site/data'
os.makedirs(OUT+'/dep', exist_ok=True)

rows=json.load(open('merged.json'))
codes=json.load(open('statut_codes.json'))
fin={e['finess'].zfill(9):e for e in json.load(open('finess_ehpad.json'))}
# complément statut par code juridique FINESS (concordance ≥ 95 %, ≥ 10 observations)
best={}
for c,v in codes.items():
    tot=sum(v.values()); b=max(v,key=v.get)
    if tot>=10 and v[b]/tot>=0.95: best[c]=int(b)
filled=0
for r in rows:
    if r['statut'] is None:
        c=(fin.get(r['fin'],{}).get('pm_statut') or '')
        if c in best: r['statut'],r['statutsrc']=best[c],'code'; filled+=1
print('statut complété par code juridique :',filled,'— restants sans statut :',sum(1 for r in rows if r['statut'] is None))

def dep_of(insee, cp):
    s=insee or ''
    if s[:3] in ('971','972','973','974','975','976'): return s[:3]
    if s[:2]=='20': return '2A' if s[:3]<'202' else '2B'
    if s[:2]: return s[:2]
    return (cp or '')[:2]

# ---- colonnes du format compact (documenté dans llms.txt et data.js) ----
COLS=['fin','nom','cp','ville','lat','lon','p','pcd','pa','t12','t34','t56','maj','temp','linge','lingeU',
      'nIncl','nSus','inclTxt','susTxt','ash','ashsrc','statut','statutsrc','cap','p2020',
      'hasN','hasD','hasO','hasM','hasC','hasCI','alim','tel','adr','pm','siren','ouv','approx']
byd={}
for r in rows:
    d=dep_of(r['insee'], r['cp'])
    byd.setdefault(d,[]).append([r.get(c) for c in COLS])

bbox={}; counts={}
for d,lst in byd.items():
    lats=[x[COLS.index('lat')] for x in lst if x[COLS.index('lat')]]
    lons=[x[COLS.index('lon')] for x in lst if x[COLS.index('lon')]]
    counts[d]=len(lst)
    if lats: bbox[d]=[round(min(lats),3),round(min(lons),3),round(max(lats),3),round(max(lons),3)]
    open(OUT+'/dep/ehpad-%s.js'%d,'w',encoding='utf-8').write(
        'ME.dep(%s,%s);'%(json.dumps(d), json.dumps(lst,ensure_ascii=False,separators=(',',':'))))
print('départements :',len(byd),'— total',sum(counts.values()))

# ---- communes (centroïdes) par département ----
arm=json.load(open('arm.json'))
# les arrondissements municipaux remplacent leur commune-mère pour les codes postaux concernés
parents={'75056','69123','13055'}
cps_arm={cp for c in arm for cp in (c.get('codesPostaux') or [])}
com=[c for c in json.load(open('communes_geo.json')) if c['code'] not in parents]+arm
for c in json.load(open('communes_geo.json')):
    if c['code'] in parents:
        restants=[cp for cp in (c.get('codesPostaux') or []) if cp not in cps_arm]
        if restants: com.append({**c,'codesPostaux':restants})
cbyd={}
for c in com:
    d=c['codeDepartement']; ctr=(c.get('centre') or {}).get('coordinates')
    if not ctr: continue
    for cp in (c.get('codesPostaux') or []):
        cbyd.setdefault(d,[]).append([cp, c['nom'], round(ctr[1],4), round(ctr[0],4), c['code']])
for d,lst in cbyd.items():
    lst.sort()
    open(OUT+'/dep/communes-%s.js'%d,'w',encoding='utf-8').write(
        'ME.com(%s,%s);'%(json.dumps(d), json.dumps(lst,ensure_ascii=False,separators=(',',':'))))
# bbox communes (pour savoir quels départements charger dans un rayon)
cbbox={}
for d,lst in cbyd.items():
    la=[x[2] for x in lst]; lo=[x[3] for x in lst]
    cbbox[d]=[round(min(la),3),round(min(lo),3),round(max(la),3),round(max(lo),3)]
print('communes+arrondissements :',sum(len(v) for v in cbyd.values()),'couples CP/commune')

# ---- table départementale : ASH (DREES 2018) + indicateurs DREES ----
ash=json.load(open('ash_dept.json'))
drees={}
for r in json.load(open('drees.json')):
    d=str(r.get('code_dep') or '').strip()
    if not d: continue
    ind=r['id_indicateur']; an=str(r['annee'])
    cur=drees.setdefault(d,{}).get(ind)
    if cur and cur[0]>=an: continue
    try: v=float(r['value'])
    except: continue
    drees[d][ind]=(an, v)
# codes de l'enquête ASH : la Corse est une collectivité unique (20R),
# le Rhône est partagé entre le département (69D) et la Métropole de Lyon (69M)
ASH_CODE={'2A':'20R','2B':'20R','69':'69D'}
def bloc_ash(code):
    a=ash.get(code,{})
    return {'nom':a.get('dep'),'recours':a.get('recours_succession'),
            'obliges':[a.get('obliges_enfants'),a.get('obliges_gendres'),a.get('obliges_petits'),a.get('obliges_autres')],
            'gir56':a.get('gir56'),
            'ded':[a.get('ded_tutelle'),a.get('ded_mutuelle'),a.get('ded_assurance'),a.get('ded_fiscal')]}
DEP={}
for d in set(list(counts)):
    a=ash.get(ASH_CODE.get(d,d),{}); dr=drees.get(d,{})
    DEP[d]={**bloc_ash(ASH_CODE.get(d,d)),
            'ashM':(bloc_ash('69M') if d=='69' else None),
            'ash_places':dr.get('pa_part_benef_ash_places_heberg'),
            'tx_equip':dr.get('pa_tx_equip_heberg_1000_75p'),
            'apa_etab':dr.get('pa_part_benef_apa_etab_75p'),
            'n':counts.get(d,0),
            'bbox':bbox.get(d)}
lyonm=[c['code'] for c in json.load(open('lyonm.json'))]
open(OUT+'/departements.js','w',encoding='utf-8').write(
  'window.ME_DEP=%s;\nwindow.ME_BBOX=%s;\nwindow.ME_LYONM=%s;'%(json.dumps(DEP,ensure_ascii=False,separators=(',',':')),
                                           json.dumps(cbbox,separators=(',',':')),
                                           json.dumps(lyonm,separators=(',',':'))))
print('table départementale :',len(DEP),'départements ; recours succession connu pour',
      sum(1 for v in DEP.values() if v['recours']))
# stats de distribution des prix (percentiles par département) pour le positionnement
import statistics
PCT={}
for d,lst in byd.items():
    ps=sorted([x[COLS.index('p')] for x in lst if x[COLS.index('p')]])
    if len(ps)>=5:
        PCT[d]=[round(statistics.quantiles(ps,n=4)[0],2),round(statistics.median(ps),2),round(statistics.quantiles(ps,n=4)[2],2),len(ps)]
allp=sorted([r['p'] for r in rows if r['p']])
PCT['FR']=[round(statistics.quantiles(allp,n=4)[0],2),round(statistics.median(allp),2),round(statistics.quantiles(allp,n=4)[2],2),len(allp)]
open(OUT+'/prix-reference.js','w',encoding='utf-8').write('window.ME_PCT=%s;'%json.dumps(PCT,separators=(',',':')))
print('prix médian France (chambre seule, €/jour) :',PCT['FR'][1],'sur',PCT['FR'][3],'établissements')
json.dump(COLS,open('cols.json','w'))
