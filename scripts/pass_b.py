# PASS B: plain Python, exact Fractions. Results from the State Election Board County Level XML exports (a different export file
# than pass A's CSV); registration from pdfplumber word positions (a different PDF text extractor than pass A's pdftotext).
import xml.etree.ElementTree as ET, pdfplumber, json, csv
from fractions import Fraction as F
RAW='/workspace/oklahoma/raw/'; OUT='/workspace/oklahoma/verification/'
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def results_xml(d, race):
    root=ET.parse(f'{RAW}xml_{d}/{d}_CountyResults.xml').getroot()
    out={}
    for c in root.findall('County'):
        name=c.findtext('CountyDesc').strip()
        for r in c.findall('race'):
            if r.findtext('race_description').strip()!=race: continue
            assert name not in out
            dv=rv=t=0
            for cand in r.findall('candidate'):
                v=int(cand.findtext('cand_tot_votes')); t+=v
                p=cand.findtext('cand_party').strip()
                if p=='DEM': dv+=v
                if p=='REP': rv+=v
            out[name]=(dv,rv,t)
    return out
def vr_plumber(path):
    rows={}; grand=None
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            words=page.extract_words()
            lines={}; keys=[]
            for w in sorted(words,key=lambda w:w['top']):
                k=next((k for k in keys if abs(k-w['top'])<4.0),None)
                if k is None: k=w['top']; keys.append(k)
                lines.setdefault(k,[]).append(w)
            order=None
            for top in sorted(lines):
                ws=sorted(lines[top],key=lambda w:w['x0']); toks=[w['text'] for w in ws]
                if toks and toks[0]=='County':
                    order=[toks[i+1] for i,t in enumerate(toks) if t.startswith('(') and t.endswith(')')]
                    continue
                if toks[:2]==['Grand','Total']:
                    n=[int(t.replace(',','')) for t in toks[2:]]; grand=dict(zip(order,n[:4])); grand['Total']=n[4]; continue
                if toks and toks[0].isdigit() and len(toks[0])==2 and len(toks)>=7:
                    nums=toks[-5:]; name=' '.join(toks[1:-5])
                    n=[int(t.replace(',','')) for t in nums]
                    rec=dict(zip(order,n[:4])); rec['Total']=n[4]; rows[name]=rec
    assert len(rows)==77
    for k in grand: assert sum(r[k] for r in rows.values())==grand[k]
    for r in rows.values(): assert r['Republican']+r['Democrat']+r['Libertarian']+r['Independent']==r['Total']
    return rows, grand
import subprocess,os
# fetch 2022 / 2024 XML exports if not present (same public export, XML format)
for d in ('20221108','20241105'):
    if not os.path.exists(f'{RAW}xml_{d}'): raise SystemExit(f'missing XML export for {d}; run fetch_exports.sh')
g22=results_xml('20221108','FOR GOVERNOR'); g26=results_xml('20261103','FOR GOVERNOR'); p24=results_xml('20241105','ELECTORS FOR PRESIDENT AND VICE PRESIDENT')
v22,_=vr_plumber(RAW+'vr_2022-11-01_county.pdf'); v24,_=vr_plumber(RAW+'vr_2024-11-01_county.pdf'); v26,_=vr_plumber(RAW+'vr_2026-11-01_county.pdf')
assert set(g22)==set(g26)==set(p24)==set(v22)==set(v24)==set(v26) and len(g22)==77
def calc(x):
    m={}
    for y in ('22','24','26'):
        m['S'+y]=F(100*x['D'+y],x['T'+y]); m['R'+y]=F(100*x['DREG'+y],x['TREG'+y]); m['G'+y]=m['S'+y]-m['R'+y]
    m['dG']=m['G26']-m['G22']; m['EL']=m['R22']-m['R26']; m['resid']=m['dG']-m['EL']
    m['k22']=m['S22']/m['R22']; m['fwd_exp26']=x['T26']*m['k22']*m['R26']/100; m['fwd_surplus']=x['D26']-m['fwd_exp26']
    m['bwd_R26_implied']=m['S26']/m['k22']; m['bwd_reg_gap_pts']=m['bwd_R26_implied']-m['R26']; m['bwd_offset_votes']=m['resid']*x['T26']/100
    m['DR22_over_T22']=(x['D22']+x['Rv22'])>x['T22']; m['DR26_over_T26']=(x['D26']+x['Rv26'])>x['T26']
    m['T22_over_TREG22']=x['T22']>x['TREG22']; m['T26_over_TREG26']=x['T26']>x['TREG26']
    return m
recs=[]; tot={}
for c in sorted(g22):
    x={}
    for y,g in (('22',g22),('26',g26),('24',p24)): x['D'+y],x['Rv'+y],x['T'+y]=g[c]
    for y,v in (('22',v22),('24',v24),('26',v26)): x['DREG'+y]=v[c]['Democrat']; x['RREG'+y]=v[c]['Republican']; x['TREG'+y]=v[c]['Total']
    for k,v in x.items(): tot[k]=tot.get(k,0)+v
    m=calc(x); recs.append({'county':c,**x,**{k:(v if isinstance(v,bool) else float(v)) for k,v in m.items()}})
with open(OUT+'passB_counties.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)
sm=calc(tot)
json.dump({'sums':tot,'metrics':{k:(v if isinstance(v,bool) else float(v)) for k,v in sm.items()}},open(OUT+'passB_statewide.json','w'),indent=1)
print('pass B ok', {k:round(float(sm[k]),4) for k in ['S22','R22','G22','S26','R26','G26','dG','EL','resid']})
