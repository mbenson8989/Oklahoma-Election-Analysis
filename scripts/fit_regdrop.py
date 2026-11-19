# Oklahoma fitted equation: dG = constant + multiplier x (Dem registration-share drop, R2022 - R2026), OLS across 77 counties.
# Path 1: numpy lstsq on pass A floats. Path 2: exact Fractions from pass B raw integer counts, closed-form normal equations.
import numpy as np, pandas as pd, csv, json, math
from fractions import Fraction as F
V='/workspace/oklahoma/verification/'
a=pd.read_csv(V+'passA_counties.csv',index_col=0)
x=a.EL.values; y=a.dG.values; X=np.column_stack([np.ones_like(x),x])
beta,_,_,_=np.linalg.lstsq(X,y,rcond=None); res=y-X@beta; n=len(y); s2=res@res/(n-2)
cov=s2*np.linalg.inv(X.T@X); p1={'n':n,'b':beta[0],'m':beta[1],'se_b':math.sqrt(cov[0,0]),'se_m':math.sqrt(cov[1,1]),'r2':1-res@res/((y-y.mean())@(y-y.mean()))}
rows=list(csv.DictReader(open(V+'passB_counties.csv')))
xs=[];ys=[]
for r in rows:
    i={k:int(r[k]) for k in ['D22','T22','D26','T26','DREG22','TREG22','DREG26','TREG26']}
    S22=F(100*i['D22'],i['T22']);S26=F(100*i['D26'],i['T26']);R22=F(100*i['DREG22'],i['TREG22']);R26=F(100*i['DREG26'],i['TREG26'])
    xs.append(R22-R26); ys.append((S26-R26)-(S22-R22))
N=len(xs); mx=sum(xs)/N; my=sum(ys)/N
Sxx=sum((v-mx)**2 for v in xs); Sxy=sum((u-mx)*(v-my) for u,v in zip(xs,ys)); Syy=sum((v-my)**2 for v in ys)
m=Sxy/Sxx; b=my-m*mx; SSE=Syy-m*Sxy; s2=SSE/(N-2)
p2={'n':N,'b':float(b),'m':float(m),'se_b':math.sqrt(float(s2*(F(1,N)+mx*mx/Sxx))),'se_m':math.sqrt(float(s2/Sxx)),'r2':float(1-SSE/Syy)}
diff={k:abs(p1[k]-p2[k]) for k in p1}
ok=all(d<1e-9 for d in diff.values())
# worked example: Tulsa
t=a.loc['TULSA']; pred=p2['b']+p2['m']*t.EL
out={'path1_numpy':p1,'path2_exact':p2,'abs_diff':diff,'match':ok,'tulsa':{'R22':t.R22,'R26':t.R26,'EL':t.EL,'dG':t.dG,'pred':pred,'diff':t.dG-pred}}
json.dump(out,open(V+'fit_regdrop_check.json','w'),indent=1,default=float); print(json.dumps(out,indent=1,default=float))
