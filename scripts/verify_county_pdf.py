# Independent check of the county PDF: every figure recomputed from pass B raw integer counts (exact fractions, decimal rounding)
# and compared token-by-token with `pdftotext -layout` output of the PDF.
import csv, subprocess, re, json
from fractions import Fraction as F
from decimal import Decimal, ROUND_HALF_UP
V='/workspace/oklahoma/verification/'; PDF='/workspace/oklahoma/pdf/Oklahoma_77_County_Democratic_Registration_and_Vote_Change.pdf'
B=list(csv.DictReader(open(V+'passB_counties.csv')))
def rnd(fr,d):  # exact decimal rounding of a Fraction
    q=Decimal(fr.numerator)/Decimal(fr.denominator) if False else None
    s=(Decimal(fr.numerator)*(10**(d+6))//fr.denominator)  # not used
    v=Decimal(fr.numerator)/Decimal(fr.denominator)
    return v.quantize(Decimal(1).scaleb(-d),rounding=ROUND_HALF_UP)
from decimal import getcontext; getcontext().prec=50
def pct(fr): return f"{rnd(fr,1)}%"
def spct(fr): r=rnd(fr,1); return ('+' if r>0 else ('-' if r<0 else '+'))+f"{abs(r)}%" if r!=0 else ('+0.0%' if fr>=0 else '-0.0%')
def spt(fr): r=rnd(fr,2); return ('+' if fr>=0 else '-')+f"{abs(r)}"
def si(x): return f"+{x:,}" if x>0 else (f"-{abs(x):,}" if x<0 else "0")
def name(c): return c.title().replace('Mcc','McC').replace('Mci','McI').replace('Leflore','Le Flore')
recs=[]
for r in B:
    x={k:int(r[k]) for k in ['DREG22','DREG26','TREG22','TREG26','D22','D26','T22','T26']}; x['name']=name(r['county']); recs.append(x)
tot={k:sum(r[k] for r in recs) for k in ['DREG22','DREG26','TREG22','TREG26','D22','D26','T22','T26']}; tot['name']='Statewide total'
recs.sort(key=lambda x: F(x['DREG26'],x['TREG26']),reverse=True)
def p1row(x):
    return [pct(F(100*x['DREG26'],x['TREG26'])),f"{x['DREG22']:,}",f"{x['DREG26']:,}",si(x['DREG26']-x['DREG22']),spct(F(100*(x['DREG26']-x['DREG22']),x['DREG22'])),
            f"{x['D22']:,}",f"{x['D26']:,}",si(x['D26']-x['D22']),spct(F(100*(x['D26']-x['D22']),x['D22'])),f"{x['T22']:,}",f"{x['T26']:,}",si(x['T26']-x['T22']),spct(F(100*(x['T26']-x['T22']),x['T22']))]
def p2row(x):
    a=F(100*x['D22'],x['T22']); b=F(100*x['D26'],x['T26'])
    return [pct(a),pct(b),spt(b-a),pct(F(100*x['DREG22'],x['TREG22'])),f"{x['TREG22']:,}",pct(F(100*x['DREG26'],x['TREG26'])),f"{x['TREG26']:,}"]
txt=subprocess.run(['pdftotext','-layout',PDF,'-'],capture_output=True,text=True).stdout
pages=txt.split('\f')
names=[r['name'] for r in recs]+['Statewide total']
num=r'[+-]?[\d,]+(?:\.\d+)?%?'
part1={};part2={};order1=[];order2=[]
for pi,pg in enumerate(pages):
    for line in pg.splitlines():
        m=re.match(r'^\s*([A-Z][A-Za-z ]+?)\s{2,}((?:'+num+r'\s+)*'+num+r')\s*$',line)
        if not m or m.group(1).strip() not in names: continue
        toks=m.group(2).split(); n=m.group(1).strip()
        if len(toks)==13: part1[n]=toks; order1.append(n)
        elif len(toks)==7: part2[n]=toks; order2.append(n)
mism=[]; nfig=0
for x in recs+[tot]:
    for part,exp in ((part1,p1row(x)),(part2,p2row(x))):
        got=part.get(x['name'])
        if got is None: mism.append((x['name'],'row missing')); continue
        for j,(a,b) in enumerate(zip(exp,got)):
            nfig+=1
            if a!=b: mism.append((x['name'],j,a,b))
sums_ok=all(sum(r[k] for r in recs)==tot[k] for k in tot if k!='name')
sw=json.load(open(V+'passB_statewide.json'))['sums']
board_ok=all(tot[k]==sw[k] for k in ['DREG22','DREG26','TREG22','TREG26','D22','D26','T22','T26'])
out={'county_rows_part1':len([n for n in order1 if n!='Statewide total']),'county_rows_part2':len([n for n in order2 if n!='Statewide total']),
     'statewide_rows':(order1.count('Statewide total'),order2.count('Statewide total')),'figures_compared':nfig,'mismatches':mism,
     'sort_order_matches_passB':order1==names and order2==names,'county_sums_equal_statewide_row':sums_ok,'statewide_row_equals_board_totals':board_ok,
     'pages':len([p for p in pages if p.strip()]),'unofficial_footer_on_every_page':all('2026 figures marked unofficial' in p for p in pages if p.strip()),
     'ballots_caveat_present':'OK does not publish county ballots cast' in txt,'statewide_row_part1':part1.get('Statewide total'),'statewide_row_part2':part2.get('Statewide total')}
json.dump(out,open(V+'county_pdf_check.json','w'),indent=1); print(json.dumps(out,indent=1))
