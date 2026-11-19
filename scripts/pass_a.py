# PASS A: pandas. Results from the State Election Board County Level CSV exports; registration from `pdftotext -layout` text of the vr2420 PDFs.
import pandas as pd, numpy as np, re, subprocess, json, sys
RAW='/workspace/oklahoma/raw/'; OUT='/workspace/oklahoma/verification/'
def results(d, race):
    df=pd.read_csv(f'{RAW}res_{d}/{d}_CountyResults.csv', usecols=range(16), dtype=str)
    df=df[df.race_description==race].copy(); df['v']=df.cand_tot_votes.astype(int)
    assert not df.duplicated().any()
    p=df.pivot_table(index='county',columns='cand_party',values='v',aggfunc='sum',fill_value=0)
    out=pd.DataFrame({'D':p['DEM'],'Rv':p['REP'],'T':p.sum(axis=1)})
    return out
def vr(path):
    txt=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout
    order=None; rows={}; grand=None
    for line in txt.splitlines():
        if line.strip().startswith('County') and '(1)' in line:
            order=[re.sub(r'\(\d\)\s*','',x).strip() for x in re.findall(r'\(\d\)\s*[A-Za-z]+',line)]
            continue
        m=re.match(r'^\s*(\d{2})\s+([A-Z][A-Z ]+?)\s{2,}([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$',line)
        if m:
            nums=[int(x.replace(',','')) for x in m.groups()[2:]]
            rec=dict(zip(order,nums[:4])); rec['Total']=nums[4]; rows[m.group(2).strip()]=rec; continue
        m=re.match(r'^\s*Grand Total\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$',line)
        if m:
            nums=[int(x.replace(',','')) for x in m.groups()]; grand=dict(zip(order,nums[:4])); grand['Total']=nums[4]
    df=pd.DataFrame(rows).T
    assert len(df)==77, len(df)
    assert (df[['Republican','Democrat','Libertarian','Independent']].sum(axis=1)==df.Total).all()
    for k in grand: assert df[k].sum()==grand[k], k
    return df, grand
g22=results('20221108','FOR GOVERNOR'); g26=results('20261103','FOR GOVERNOR'); p24=results('20241105','ELECTORS FOR PRESIDENT AND VICE PRESIDENT')
v22,G22=vr(RAW+'vr_2022-11-01_county.pdf'); v24,G24=vr(RAW+'vr_2024-11-01_county.pdf'); v26,G26=vr(RAW+'vr_2026-11-01_county.pdf')
o=pd.DataFrame(index=sorted(g22.index))
for y,g in (('22',g22),('26',g26),('24',p24)):
    o['D'+y]=g.D; o['Rv'+y]=g.Rv; o['T'+y]=g['T']
for y,v in (('22',v22),('24',v24),('26',v26)):
    o['DREG'+y]=v.Democrat.astype(int); o['RREG'+y]=v.Republican.astype(int); o['TREG'+y]=v.Total.astype(int)
assert o.notna().all().all() and len(o)==77
def metrics(x):
    m={}
    for y in ('22','24','26'):
        m['S'+y]=100*x['D'+y]/x['T'+y]; m['R'+y]=100*x['DREG'+y]/x['TREG'+y]; m['G'+y]=m['S'+y]-m['R'+y]
    m['dG']=m['G26']-m['G22']; m['EL']=m['R22']-m['R26']; m['resid']=m['dG']-m['EL']
    m['k22']=m['S22']/m['R22']; m['fwd_exp26']=x['T26']*m['k22']*m['R26']/100; m['fwd_surplus']=x['D26']-m['fwd_exp26']
    m['bwd_R26_implied']=m['S26']/m['k22']; m['bwd_reg_gap_pts']=m['bwd_R26_implied']-m['R26']; m['bwd_offset_votes']=m['resid']*x['T26']/100
    m['DR22_over_T22']=(x['D22']+x['Rv22'])>x['T22']; m['DR26_over_T26']=(x['D26']+x['Rv26'])>x['T26']
    m['T22_over_TREG22']=x['T22']>x['TREG22']; m['T26_over_TREG26']=x['T26']>x['TREG26']
    return m
for k,v in metrics(o).items(): o[k]=v
o.index.name='county'; o.to_csv(OUT+'passA_counties.csv')
st=pd.Series({c:int(o[c].sum()) for c in ['D22','Rv22','T22','D24','Rv24','T24','D26','Rv26','T26','DREG22','RREG22','TREG22','DREG24','RREG24','TREG24','DREG26','RREG26','TREG26']})
sm={k:float(v) for k,v in metrics(st).items()}
json.dump({'sums':{k:int(v) for k,v in st.items()},'metrics':sm,'vr_grand':{'2022':G22,'2024':G24,'2026':G26}},open(OUT+'passA_statewide.json','w'),indent=1,default=float)
print('pass A ok', {k:round(sm[k],4) for k in ['S22','R22','G22','S26','R26','G26','dG','EL','resid']})
