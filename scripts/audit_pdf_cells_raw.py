# STANDALONE raw-source audit of the county PDF (does not read pass A/B, the county CSV or the summary JSON).
# Results: Board County Level Results exports read straight from the zip archives in repo/sources (CSV and XML; both must agree).
# Registration: vr2420 PDFs in repo/sources parsed with `pdftotext -raw` (a third extraction mode). Board grand totals: vr2420
# "Grand Total" line and the Board's statewide results JSON. Rounding: exact Fractions, decimal ROUND_HALF_UP at displayed precision.
import zipfile, io, csv, re, subprocess, json, xml.etree.ElementTree as ET
from fractions import Fraction as F
from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec=60
SRC='/workspace/oklahoma/repo/sources/'; PDF='/workspace/oklahoma/pdf/Oklahoma_77_County_Democratic_Registration_and_Vote_Change.pdf'
OUT='/workspace/oklahoma/verification/PDF_CELL_AUDIT.csv'
def gov_csv(d):
    z=zipfile.ZipFile(SRC+f'{d}_CLCSV.zip'); name=z.namelist()[0]
    res={}
    for r in csv.DictReader(io.TextIOWrapper(z.open(name),encoding='utf-8-sig')):
        if r['race_description']!='FOR GOVERNOR': continue
        c=r['county'].strip(); a=res.setdefault(c,[0,0]); v=int(r['cand_tot_votes']); a[1]+=v
        if r['cand_party'].strip()=='DEM': a[0]+=v
    return res, f'{d}_CLCSV.zip:{name}'
def gov_xml(d):
    z=zipfile.ZipFile(SRC+f'{d}_CLXML.zip'); root=ET.parse(z.open(z.namelist()[0])).getroot(); res={}
    for c in root.findall('County'):
        for r in c.findall('race'):
            if r.findtext('race_description').strip()!='FOR GOVERNOR': continue
            a=res.setdefault(c.findtext('CountyDesc').strip(),[0,0])
            for k in r.findall('candidate'):
                v=int(k.findtext('cand_tot_votes')); a[1]+=v
                if k.findtext('cand_party').strip()=='DEM': a[0]+=v
    return res
def vr(fn):
    t=subprocess.run(['pdftotext','-raw',SRC+fn,'-'],capture_output=True,text=True).stdout
    rows={}; grand=None; order=None
    for line in t.splitlines():
        if line.strip().startswith('County') and '(1)' in line:
            order=re.findall(r'\(\d\)\s*([A-Za-z]+)',line); continue
        m=re.match(r'^(\d{2}) ([A-Z][A-Z ]*?) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)$',line.strip())
        if m:
            n=[int(x.replace(',','')) for x in m.groups()[2:]]; rows[m.group(2)]=dict(zip(order,n[:4]),Total=n[4]); continue
        m=re.match(r'^Grand Total ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)$',line.strip())
        if m: n=[int(x.replace(',','')) for x in m.groups()]; grand=dict(zip(order,n[:4]),Total=n[4])
    assert len(rows)==77, (fn,len(rows))
    for r in rows.values(): assert sum(r[k] for k in ('Republican','Democrat','Libertarian','Independent'))==r['Total']
    return rows, grand
g22,src22=gov_csv('20221108'); g26,src26=gov_csv('20261103')
assert g22==gov_xml('20221108') and g26==gov_xml('20261103'), 'CSV and XML exports disagree'
v22,G22=vr('vr_2022-11-01_county.pdf'); v26,G26=vr('vr_2026-11-01_county.pdf')
assert set(g22)==set(g26)==set(v22)==set(v26) and len(g22)==77
sw22=json.load(open(SRC+'sw_results_20221108.json'))['results'][0]; sw26=json.load(open(SRC+'sw_results_20261103.json'))['results'][0]
def dem_total(sw,d):  # Board statewide Dem candidate total: the candidate whose county sums match is identified by the CSV DEM label
    return sw['totResults']['totalVotes']
SRCV={'DREG22':'vr_2022-11-01_county.pdf','DREG26':'vr_2026-11-01_county.pdf','TREG22':'vr_2022-11-01_county.pdf','TREG26':'vr_2026-11-01_county.pdf','D22':src22,'D26':src26,'T22':src22,'T26':src26}
data={}
for c in g22:
    data[c]={'DREG22':v22[c]['Democrat'],'DREG26':v26[c]['Democrat'],'TREG22':v22[c]['Total'],'TREG26':v26[c]['Total'],'D22':g22[c][0],'T22':g22[c][1],'D26':g26[c][0],'T26':g26[c][1]}
st={k:sum(d[k] for d in data.values()) for k in SRCV}
# Board published grand totals
board={'DREG22':G22['Democrat'],'TREG22':G22['Total'],'DREG26':G26['Democrat'],'TREG26':G26['Total'],'T22':sw22['totResults']['totalVotes'],'T26':sw26['totResults']['totalVotes']}
# Dem statewide from the Board JSON: candidate order in JSON matches race candidate order; take the candidate whose total equals any candidate list entry with the DEM county sum
board['D22']=next(c['totalVotes'] for c in sw22['candResults'] if c['totalVotes']==st['D22']) if any(c['totalVotes']==st['D22'] for c in sw22['candResults']) else None
board['D26']=next(c['totalVotes'] for c in sw26['candResults'] if c['totalVotes']==st['D26']) if any(c['totalVotes']==st['D26'] for c in sw26['candResults']) else None
def q(fr,d): return (Decimal(fr.numerator)/Decimal(fr.denominator)).quantize(Decimal(1).scaleb(-d),rounding=ROUND_HALF_UP)
def pct(fr): return f"{q(fr,1)}%"
def spct(fr): r=q(fr,1); return ('-' if r<0 else '+')+f"{abs(r)}%"
def spt(fr): r=q(fr,2); return ('-' if r<0 else '+')+f"{abs(r)}"
def si(x): return f"+{x:,}" if x>0 else (f"-{abs(x):,}" if x<0 else "0")
def ii(x): return f"{x:,}"
C1=[('Dem Reg Share 2026 %',lambda x:pct(F(100*x['DREG26'],x['TREG26'])),'DREG26,TREG26'),('Dem Reg 2022 (Nov 1)',lambda x:ii(x['DREG22']),'DREG22'),('Dem Reg 2026 (Nov 1)',lambda x:ii(x['DREG26']),'DREG26'),
    ('Reg Change #',lambda x:si(x['DREG26']-x['DREG22']),'DREG22,DREG26'),('Reg Change %',lambda x:spct(F(100*(x['DREG26']-x['DREG22']),x['DREG22'])),'DREG22,DREG26'),
    ('Dem Gov Votes 2022',lambda x:ii(x['D22']),'D22'),('Dem Gov Votes 2026*',lambda x:ii(x['D26']),'D26'),('Vote Change #',lambda x:si(x['D26']-x['D22']),'D22,D26'),
    ('Vote Change % (on 2022 base)',lambda x:spct(F(100*(x['D26']-x['D22']),x['D22'])),'D22,D26'),('Total Gov Votes 2022',lambda x:ii(x['T22']),'T22'),('Total Gov Votes 2026*',lambda x:ii(x['T26']),'T26'),
    ('Gov Votes Change #',lambda x:si(x['T26']-x['T22']),'T22,T26'),('Gov Votes Change %',lambda x:spct(F(100*(x['T26']-x['T22']),x['T22'])),'T22,T26')]
C2=[('Dem Share of Gov Votes 2022 %',lambda x:pct(F(100*x['D22'],x['T22'])),'D22,T22'),('Dem Share of Gov Votes 2026* %',lambda x:pct(F(100*x['D26'],x['T26'])),'D26,T26'),
    ('Change (pts)',lambda x:spt(F(100*x['D26'],x['T26'])-F(100*x['D22'],x['T22'])),'D22,T22,D26,T26'),('Dem Share of Registration 2022 %',lambda x:pct(F(100*x['DREG22'],x['TREG22'])),'DREG22,TREG22'),
    ('Total Registered 2022 (Nov 1)',lambda x:ii(x['TREG22']),'TREG22'),('Dem Share of Registration 2026 %',lambda x:pct(F(100*x['DREG26'],x['TREG26'])),'DREG26,TREG26'),('Total Registered 2026 (Nov 1)',lambda x:ii(x['TREG26']),'TREG26')]
def disp(c): return c.title().replace('Mcc','McC').replace('Mci','McI').replace('Leflore','Le Flore')
order=sorted(data,key=lambda c:F(data[c]['DREG26'],data[c]['TREG26']),reverse=True)
# PDF text
txt=subprocess.run(['pdftotext','-layout',PDF,'-'],capture_output=True,text=True).stdout
num=r'[+-]?[\d,]+(?:\.\d+)?%?'
p1={};p2={};o1=[];o2=[]
for line in txt.splitlines():
    m=re.match(r'^\s*([A-Z][A-Za-z ]+?)\s{2,}((?:'+num+r'\s+)*'+num+r')\s*$',line)
    if not m: continue
    n=m.group(1).strip(); toks=m.group(2).split()
    if len(toks)==13: p1[n]=toks; o1.append(n)
    elif len(toks)==7: p2[n]=toks; o2.append(n)
rows=[]; mism=0
def srcs(keys,state=False): return '; '.join(sorted(set(SRCV[k] for k in keys.split(','))))
for label,x,keys_state in [(disp(c),data[c],False) for c in order]+[('Statewide total',st,True)]:
    for part,cols,tab in ((p1,C1,'Table 1'),(p2,C2,'Table 2')):
        got=part.get(label)
        for j,(col,f,keys) in enumerate(cols):
            exp=f(x); pv=got[j] if got and j<len(got) else 'MISSING'
            ok=pv==exp; mism+=not ok
            rows.append([tab,label,col,pv,exp,srcs(keys),'MATCH' if ok else 'MISMATCH'])
# statewide row vs Board published grand totals
for k in ['DREG22','DREG26','TREG22','TREG26','D22','D26','T22','T26']:
    ok=board[k] is not None and board[k]==st[k]; mism+=not ok
    rows.append(['Board grand total','Statewide total',k,f"{st[k]:,}",f"{board[k]:,}" if board[k] is not None else 'NOT FOUND',
                 ('vr2420 Grand Total line, '+SRCV[k]) if k.startswith(('DREG','TREG')) else ('sw_results_'+('20221108' if k.endswith('22') else '20261103')+'.json'),'MATCH' if ok else 'MISMATCH'])
order_ok=(o1==[disp(c) for c in order]+['Statewide total']) and (o2==[disp(c) for c in order]+['Statewide total'])
mism+=not order_ok
with open(OUT,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['table','county','column','pdf_value','recomputed_from_raw','source_file','match']); w.writerows(rows)
cells=sum(1 for r in rows if r[0]!='Board grand total')
print(json.dumps({'pdf_cells_checked':cells,'board_total_checks':len(rows)-cells,'rows_checked':len(rows),'mismatches':mism,'sort_order_ok':order_ok,'county_rows':(len(o1)-1,len(o2)-1),'csv_xml_agree':True},indent=1))
# ---- text figures outside the table cells (legend, sort note, ballots footnote) ----
extra=[]
rose=[disp(c) for c in order if data[c]['DREG26']>data[c]['DREG22']]; fell=[c for c in data if data[c]['D26']<data[c]['D22']]
flat=' '.join(txt.split())
for desc,exp,src in [('legend: Dem registration rose',f"Democratic registration rose ({', '.join(rose)})",'vr_2022/2026 PDFs'),
                     ('legend: Dem gov votes fell count',f"Democratic governor votes fell ({len(fell)} counties)",src22+'; '+src26),
                     ('sort note: share leader',f"{disp(order[0])} leads by share",'vr_2026-11-01_county.pdf'),
                     ('sort note: raw Dem reg leader',f"{disp(max(data,key=lambda c:data[c]['DREG26']))} County leads by raw Democratic registration",'vr_2026-11-01_county.pdf')]:
    extra.append(['Text','—',desc,exp if exp in flat else 'NOT FOUND',exp,src,'MATCH' if exp in flat else 'MISMATCH'])
for y,d,k in (('2022','20221108','TREG22'),('2026','20261103','TREG26')):
    tp=F(str(json.load(open(SRC+f'sw_results_{d}.json'))['turnoutPerc'])); b=int(q(tp*st[k]/100,0))
    s=f"{b:,}"+(' (2022)' if y=='2022' else '* (2026)'); ok=s in flat
    extra.append(['Text','Statewide',f'footnote: statewide ballots {y} (turnout % × Nov 1 registration)',s if ok else 'NOT FOUND',s,f'sw_results_{d}.json; vr PDF Grand Total','MATCH' if ok else 'MISMATCH'])
pub22='1,155,911'; extra.append(['Text','Statewide','2022 ballots = Board published 1,155,911',f"{int(q(F(str(json.load(open(SRC+'sw_results_20221108.json'))['turnoutPerc']))*st['TREG22']/100,0)):,}",pub22,'Board published 2022 total ballots cast','MATCH' if f"{int(q(F(str(json.load(open(SRC+'sw_results_20221108.json'))['turnoutPerc']))*st['TREG22']/100,0)):,}"==pub22 else 'MISMATCH'])
m2=sum(r[-1]!='MATCH' for r in extra)
with open(OUT,'a',newline='') as f: csv.writer(f).writerows(extra)
import hashlib
print(json.dumps({'text_checks':len(extra),'text_mismatches':m2,'TOTAL_rows':len(rows)+len(extra),'TOTAL_mismatches':mism+m2,'pdf_sha256':hashlib.sha256(open(PDF,'rb').read()).hexdigest()},indent=1))
