import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
R='/workspace/oklahoma/repo/'
o=pd.read_pickle('/tmp/ok_o.pkl'); J=json.load(open(R+'OK_results_summary.json')); F=J['fits']; K=J['K']
nm=lambda c: c.title().replace('Mcc','McC').replace('Mci','McI').replace('Leflore','Le Flore')
cap=J['ceiling_dG']; flo=J['floor_dG']; rt=J['resid_top5']; rb=J['resid_bottom5']
NOTE='*2026 marked UNOFFICIAL here (OK State Election Board county export, data last updated 11/06/2026). Governor race; denominator = all governor votes.'
def stack(items,gap):
    items=sorted(items,key=lambda t:t[1]); ys=[t[1] for t in items]
    for k in range(1,len(ys)): ys[k]=max(ys[k],ys[k-1]+gap)
    return [(t[0],y) for t,y in zip(items,ys)]
# 1 slope chart
fig,ax=plt.subplots(figsize=(10,12))
for c,r in o.iterrows():
    if c in cap or c in flo: continue
    ax.plot([0,1],[r.G22,r.G26],color='#bbbbbb',lw=0.8,alpha=0.8,zorder=1)
for c in flo: r=o.loc[c]; ax.plot([0,1],[r.G22,r.G26],color='#1f5fbf',lw=2.2,zorder=2,marker='o',ms=4)
for c in cap: r=o.loc[c]; ax.plot([0,1],[r.G22,r.G26],color='#e8590c',lw=3,zorder=3,marker='o')
for c,y in stack([(c,o.loc[c,'G26']) for c in cap],1.0): ax.text(1.03,y,f"{nm(c)} {o.loc[c,'dG']:+.2f} pts",va='center',color='#b02a00',fontweight='bold',fontsize=10)
for c,y in stack([(c,o.loc[c,'G22']) for c in flo],1.0): ax.text(-0.03,y,f"{nm(c)} {o.loc[c,'dG']:+.2f} pts",va='center',ha='right',color='#1f4e9a',fontweight='bold',fontsize=9)
ax.set_xticks([0,1]); ax.set_xticklabels(['2022 (official)','2026*'],fontsize=12); ax.set_xlim(-0.5,1.5)
ax.set_ylabel('G = Dem share of governor votes − Dem registration share (points)')
ax.set_title(f'Oklahoma G 2022 to G 2026* — County Slope Chart\nGovernor race; 77 counties. Orange: 5 ceiling counties (largest ΔG). Blue: 5 floor counties (smallest ΔG).\nG rose in {J["counts"]["dG_pos"]} of 77 counties. Labels show ΔG = G2026* − G2022.',fontsize=11)
ax.grid(axis='y',alpha=0.3); fig.text(0.01,0.005,NOTE,fontsize=6.5)
plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(R+'OK_Slope_G2022_to_G2026_County_Slope_Chart.png',dpi=150); plt.close()
# 2 forward fit S vs D (Kansas style) with statewide constant
fig,axs=plt.subplots(1,2,figsize=(14,6.5),sharey=True)
for ax,y,lab in ((axs[0],'22','2022 (official)'),(axs[1],'26','2026*')):
    f=F['20'+y]; x=o['R'+y]; s=o['G'+y]
    ax.scatter(x,s,s=18,color='#888',zorder=2)
    ax.scatter(o.loc[cap,'R'+y],o.loc[cap,'G'+y],s=40,color='#e8590c',zorder=3,label='ceiling (top-5 ΔG)')
    ax.scatter(o.loc[flo,'R'+y],o.loc[flo,'G'+y],s=30,color='#1f5fbf',zorder=3,label='floor (bottom-5 ΔG)')
    xx=np.linspace(x.min(),x.max(),50); ax.plot(xx,f['m']*xx/100+f['b'],color='black',lw=1.6,label=f"fit: G = {f['m']:.2f}·(R/100) + {f['b']:.2f}")
    ax.fill_between(xx,f['m']*xx/100+f['b']-f['resid_sd'],f['m']*xx/100+f['b']+f['resid_sd'],color='#999',alpha=0.15,label=f"±1 residual SD ({f['resid_sd']:.2f} pts)")
    kk=K['k_OK_2022']; ax.plot(xx,(kk-1)*xx,color='#2a9d8f',lw=1.4,ls='--',label=f"statewide constant k_OK,2022 = {kk:.4f}: G = (k−1)·R")
    for c in cap: ax.annotate(nm(c),(o.loc[c,'R'+y],o.loc[c,'G'+y]),xytext=(4,3),textcoords='offset points',fontsize=8,color='#b02a00')
    ax.set_title(f"{lab}: R² = {f['r2']:.3f}, n = 77",fontsize=11); ax.set_xlabel('R = Democratic registration share (%)'); ax.grid(alpha=0.3); ax.legend(fontsize=7.5,loc='upper right')
axs[0].set_ylabel('G = Dem vote share − Dem registration share (points)')
fig.suptitle('Oklahoma forward surplus fit, least squares across 77 counties (Oklahoma data only)',fontsize=12)
fig.text(0.01,0.005,NOTE,fontsize=7); plt.tight_layout(rect=(0,0.03,1,0.96)); plt.savefig(R+'OK_Forward_Surplus_Fit_G_vs_R.png',dpi=140); plt.close()
# 3 dG bars by population
def bars(col,fname,title,ylab,hi,lo,hl,ll):
    fig,ax=plt.subplots(figsize=(20,8)); xs=np.arange(len(o))
    cols=['#e8590c' if c in hi else '#1f5fbf' if c in lo else '#9a9a9a' for c in o.index]
    ax.bar(xs,o[col],color=cols,hatch=None)
    for i,c in enumerate(o.index):
        if o.loc[c,'nonloss']: ax.bar([i],[o.loc[c,col]],color='none',edgecolor='k',hatch='//',lw=0)
    ax.axhline(0,color='k',lw=0.6); ax.axhline(o[col].median(),ls='--',color='gray',lw=1,label=f"County median {o[col].median():+.2f} (mean {o[col].mean():+.2f})")
    for c in list(hi)+list(lo):
        i=list(o.index).index(c); v=o.loc[c,col]; ax.text(i,v+(0.3 if v>=0 else -0.8),f"{v:+.2f}",ha='center',fontsize=8,color='#b02a00' if c in hi else '#1f4e9a',fontweight='bold')
    ax.bar([0],[0],color='#e8590c',label=hl); ax.bar([0],[0],color='#1f5fbf',label=ll); ax.bar([0],[0],color='none',hatch='//',edgecolor='k',label='non-loss county (registered Democrats did not fall)')
    ax.set_xticks(xs); ax.set_xticklabels([f"{nm(c)} {p:,}" for c,p in zip(o.index,o.population_2025)],rotation=90,fontsize=7.5); ax.set_xlim(-1,len(o))
    ax.set_ylabel(ylab); ax.grid(axis='y',alpha=0.25); ax.legend(fontsize=9,loc='upper right')
    ax.set_title(title,fontsize=13,fontweight='bold'); fig.text(0.01,0.005,NOTE,fontsize=8); plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(R+fname,dpi=140); plt.close()
bars('dG','OK_DeltaG_Bars_by_Population.png','Oklahoma governor ΔG by county, largest to smallest population (2025 Census estimate)','ΔG = G2026* − G2022 (points)',cap,flo,'Ceiling: 5 largest ΔG','Floor: 5 smallest ΔG')
bars('resid','OK_Expected_Loss_Residual_Bars_by_Population.png','Oklahoma residual = ΔG − expected loss (= change in Dem share of governor votes), largest to smallest population','Residual* (points)',rt,rb,'Top 5 residual','Bottom 5 residual')
# 4 stacked share with registration loss (Nebraska style)
fig,ax=plt.subplots(figsize=(20,9)); xs=np.arange(len(o))
base=np.minimum(o.S22,o.S26); gain=(o.S26-o.S22).clip(lower=0); loss=(o.S22-o.S26).clip(lower=0)
ax.bar(xs,base,color='#4a78c2',label='Dem share of governor votes, lower of 2022 / 2026*')
ax.bar(xs,gain,bottom=base,color='#f28e2b',label='2022→2026* vote-share gain')
ax.bar(xs,loss,bottom=base,color='#c9c9c9',label='2022→2026* vote-share fall')
ax.bar(xs,-o.EL,color='#d62728',label='Dem registration-share loss, R2022 − R2026 (drawn below zero)')
ax.axhline(0,color='k',lw=0.7)
ax.set_xticks(xs); ax.set_xticklabels([f"{nm(c)} {p:,}" for c,p in zip(o.index,o.population_2025)],rotation=90,fontsize=7.5); ax.set_xlim(-1,len(o))
ax.set_ylabel('points'); ax.grid(axis='y',alpha=0.25); ax.legend(fontsize=9,loc='upper right')
ax.set_title('Oklahoma governor: Dem vote share with 2026* change stacked, registration-share loss below the line, by population',fontsize=13,fontweight='bold')
fig.text(0.01,0.005,NOTE,fontsize=8); plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(R+'OK_Stacked_Share_Reg_Loss_by_Population.png',dpi=140); plt.close()
# 5 backward solve: implied vs actual registration share
fig,ax=plt.subplots(figsize=(9,8))
ax.scatter(o.R26,o.bwd_R26_implied,s=np.clip(o.population_2025/4000,10,250),color='#888',alpha=0.7,edgecolor='k',lw=0.3)
for c in set(rt+rb+['OKLAHOMA','TULSA','CLEVELAND']): ax.annotate(nm(c),(o.loc[c,'R26'],o.loc[c,'bwd_R26_implied']),xytext=(4,3),textcoords='offset points',fontsize=8)
lim=[0,max(o.bwd_R26_implied.max(),o.R26.max())+3]; ax.plot(lim,lim,color='k',lw=1,label='implied = actual')
st=K['state_backward']; ax.scatter([st['R26_actual']],[st['R26_implied']],marker='*',s=300,color='#e8590c',zorder=5,label=f"Statewide: actual {st['R26_actual']:.2f}% vs implied {st['R26_implied']:.2f}%")
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_xlabel('Actual Dem registration share, Nov 1 2026 (%)'); ax.set_ylabel('Backward-solved registration share implied by 2026* result = S2026 ÷ k2022 (%)')
ax.set_title('Oklahoma backward solve: registration share implied by the 2026* governor result\n(each county at its own 2022 conversion constant k = S2022 ÷ R2022; dot size ~ population)',fontsize=11)
ax.grid(alpha=0.3); ax.legend(fontsize=9,loc='upper left'); fig.text(0.01,0.005,NOTE,fontsize=6); plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(R+'OK_Backward_Solve_Implied_vs_Actual_Reg_Share.png',dpi=140); plt.close()
print('charts ok')
