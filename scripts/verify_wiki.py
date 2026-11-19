# Independent check: recompute headline numbers from pass B county rows (exact fractions) and confirm the strings on the staged pages;
# also confirm the published county CSV equals pass B for every numeric field.
import csv, json, re
from fractions import Fraction as F
V='/workspace/oklahoma/verification/'; W='/workspace/oklahoma/wiki/'; R='/workspace/oklahoma/repo/'
B=list(csv.DictReader(open(V+'passB_counties.csv')))
tot=lambda k: sum(int(r[k]) for r in B)
S22=F(100*tot('D22'),tot('T22')); S26=F(100*tot('D26'),tot('T26')); R22=F(100*tot('DREG22'),tot('TREG22')); R26=F(100*tot('DREG26'),tot('TREG26'))
k=S22/R22; k26=S26/R26; EL=R22-R26; dG=(S26-R26)-(S22-R22); res=dG-EL
fexp=tot('T26')*k*R26/100; fsur=tot('D26')-fexp; Rimp=S26/k
sg=lambda x: f"{float(x):+.2f}".replace('-','−')
checks={'S22':f"{float(S22):.2f}%",'S26':f"{float(S26):.2f}%",'R22':f"{float(R22):.2f}%",'R26':f"{float(R26):.2f}%",'G22':sg(S22-R22),'G26':sg(S26-R26),'dG':'ΔG '+sg(dG),
 'resid':sg(res)+' pts','k':f"{float(k):.4f}",'k26':f"{float(k26):.4f}",'fwd_exp':f"{round(fexp):,}",'fwd_sur':f"+{round(fsur):,}",'Rimp':f"{float(Rimp):.2f}%",
 'offset':f"+{round(res*tot('T26')/100):,}"}
home=open(W+'Home.md').read(); pages=''.join(open(W+p).read() for p in ['Home.md','Reverse-Math.md','Locked-Oklahoma-Formula.md','Floor-and-Ceiling.md','Graphs.md'])
res_checks={k_:{'expected':v,'found_on_Home':v in home} for k_,v in checks.items()}
# residual top/bottom from pass B
rs=sorted(B,key=lambda r: F(r['resid']) if False else float(r['resid']))
top=[r['county'] for r in rs[::-1][:5]]; bot=[r['county'] for r in rs[:5]]
# county CSV vs pass B
P={r['county'].upper().replace(' ',''):r for r in csv.DictReader(open(R+'OK_Governor_2022_2026_County_ReverseFactoring.csv'))}
mm=0; nf=0
for r in B:
    p=P[r['county'].replace(' ','')]
    for f,v in r.items():
        if f=='county' or f not in p: continue
        nf+=1
        if v in ('True','False'): mm+= v!=p[f]
        else: mm+= abs(float(v)-float(p[f]))>1e-5*max(1,abs(float(v)))
# Cedar link check
cedar='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
star_ok=all('UNOFFICIAL' in open(W+p).read() for p in ['Home.md','Reverse-Math.md','Locked-Oklahoma-Formula.md','Floor-and-Ceiling.md','Graphs.md'])
out={'headline_checks':res_checks,'all_found':all(v['found_on_Home'] for v in res_checks.values()),'passB_resid_top5':top,'passB_resid_bottom5':bot,
     'county_csv_vs_passB':{'fields':nf,'mismatches':mm},'cedar_link_on_home':cedar in home,'unofficial_banner_on_all_pages':star_ok}
json.dump(out,open(V+'wiki_number_check.json','w'),indent=1); print(json.dumps(out,indent=1))
