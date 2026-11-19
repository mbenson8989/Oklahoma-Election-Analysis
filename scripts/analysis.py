# Builds the county CSV, Oklahoma-only constants and summary JSON from the verified pass outputs (pass A values; pass B already matched).
import pandas as pd, numpy as np, json
from scipy import stats
V='/workspace/oklahoma/verification/'; RAW='/workspace/oklahoma/raw/'; R='/workspace/oklahoma/repo/'
o=pd.read_csv(V+'passA_counties.csv',index_col=0)
pop=pd.read_csv(RAW+'ok_pop_2025.csv',index_col=0).population_2025; pop.index=pop.index.str.replace(' ','')
o['population_2025']=[int(pop[c.replace(' ','')]) for c in o.index]
o=o.sort_values('population_2025',ascending=False)
o['nonloss']=o.DREG26>=o.DREG22
o['gap_votes_NE']=o.D26-o.D22*o.DREG26/o.DREG22
sw={y:json.load(open(f'{RAW}sw_results_{d}.json')) for y,d in (('22','20221108'),('24','20241105'),('26','20261103'))}
st=json.load(open(V+'passA_statewide.json')); S=st['sums']; M=st['metrics']
# statewide ballots cast: county ballots are NOT published; the Board's results site publishes a statewide turnout % = ballots / Nov 1 registration
ball={}
for y in ('22','24','26'):
    raw=sw[y]['turnoutPerc']/100*S['TREG'+y]; ball[y]={'turnoutPerc':sw[y]['turnoutPerc'],'derived':raw,'rounded':int(round(raw))}
K={}
K['k_OK_2022']=M['S22']/M['R22']; K['k_OK_2026']=M['S26']/M['R26']; K['k_OK_2024pres']=M['S24']/M['R24']
fwd_exp_state=S['T26']*K['k_OK_2022']*M['R26']/100
K['state_forward']={'expected_D26':fwd_exp_state,'actual_D26':S['D26'],'surplus':S['D26']-fwd_exp_state}
R26_impl=M['S26']/K['k_OK_2022']
K['state_backward']={'R26_implied':R26_impl,'R26_actual':M['R26'],'gap_pts':R26_impl-M['R26'],'implied_DREG26':R26_impl/100*S['TREG26'],'actual_DREG26':S['DREG26'],
  'implied_minus_actual_DREG26':R26_impl/100*S['TREG26']-S['DREG26'],'offset_votes_pooled':M['resid']*S['T26']/100,'offset_votes_county_sum':float(o.bwd_offset_votes.sum()),
  'fwd_surplus_county_sum':float(o.fwd_surplus.sum())}
def ols(x,y):
    r=stats.linregress(x,y); res=y-(r.slope*x+r.intercept); n=len(x)
    t=stats.t.ppf(0.975,n-2)
    return {'n':n,'m':r.slope,'m_se':r.stderr,'m_ci':[r.slope-t*r.stderr,r.slope+t*r.stderr],'b':r.intercept,'b_se':r.intercept_stderr,'b_ci':[r.intercept-t*r.intercept_stderr,r.intercept+t*r.intercept_stderr],
            'r2':r.rvalue**2,'p_m':r.pvalue,'resid_sd':float(np.std(res,ddof=2)),'within_2':int((abs(res)<=2).sum()),'within_5':int((abs(res)<=5).sum())}
fits={'2022':ols(o.R22.values/100,o.G22.values),'2026':ols(o.R26.values/100,o.G26.values),'2024pres':ols(o.R24.values/100,o.G24.values)}
fits['regconst']=ols(o.EL.values,o.dG.values)  # dG = b + m*EL (SD registration constant)
fits['size']=ols(np.log10(o.population_2025.values),o.dG.values)
fits['size_resid']=ols(np.log10(o.population_2025.values),o.resid.values)
top5=o.dG.sort_values(ascending=False).index[:5].tolist(); floor=o.dG.sort_values().index[:5].tolist()
rtop=o.resid.sort_values(ascending=False).index[:5].tolist(); rbot=o.resid.sort_values().index[:5].tolist()
summ={'K':K,'fits':fits,'ballots_statewide':ball,'ceiling_dG':top5,'floor_dG':floor,'resid_top5':rtop,'resid_bottom5':rbot,
 'counts':{'dG_pos':int((o.dG>0).sum()),'resid_pos':int((o.resid>0).sum()),'resid_neg':int((o.resid<0).sum()),'S_rose':int((o.S26>o.S22).sum()),'DREG_fell':int((o.DREG26<o.DREG22).sum()),
           'Rshare_fell':int((o.R26<o.R22).sum()),'nonloss':o.index[o.nonloss].tolist(),'overballot_DR_gt_T':int((o.DR22_over_T22|o.DR26_over_T26).sum()),'T_gt_TREG':int((o.T22_over_TREG22|o.T26_over_TREG26).sum())},
 'desc':{k:{'median':float(o[k].median()),'mean':float(o[k].mean()),'sd':float(o[k].std()),'min':float(o[k].min()),'argmin':o[k].idxmin(),'max':float(o[k].max()),'argmax':o[k].idxmax()} for k in ['dG','resid','EL','fwd_surplus','bwd_offset_votes','bwd_reg_gap_pts','G22','G26','G24']},
 'statewide':{'sums':S,'metrics':M,'ballot_share':{'S22_ballots':100*S['D22']/ball['22']['rounded'],'S26_ballots':100*S['D26']/ball['26']['rounded'],'S24_ballots':100*S['D24']/ball['24']['rounded']}},
 'sw_dem_cand':{y:sw[y]['results'][0]['candResults'] for y in sw}}
json.dump(summ,open(R+'OK_results_summary.json','w'),indent=1,default=lambda x: x.item() if hasattr(x,'item') else str(x))
cols=['population_2025','D22','Rv22','T22','DREG22','RREG22','TREG22','S22','R22','G22','D26','Rv26','T26','DREG26','RREG26','TREG26','S26','R26','G26','dG','EL','resid','k22','fwd_exp26','fwd_surplus','bwd_R26_implied','bwd_reg_gap_pts','bwd_offset_votes','gap_votes_NE','nonloss','D24','Rv24','T24','DREG24','RREG24','TREG24','S24','R24','G24','DR22_over_T22','DR26_over_T26','T22_over_TREG22','T26_over_TREG26']
out=o[cols].copy(); out.insert(0,'county',[c.title().replace('Mcc','McC').replace('Mci','McI').replace('Leflore','Le Flore') for c in o.index])
out.to_csv(R+'OK_Governor_2022_2026_County_ReverseFactoring.csv',index=False,float_format='%.6f')
o.to_pickle('/tmp/ok_o.pkl')
print(json.dumps({k:summ[k] for k in ['K','ballots_statewide','ceiling_dG','floor_dG','resid_top5','resid_bottom5','counts']},indent=1,default=str))
for k in ['2022','2026','2024pres','regconst','size','size_resid']: print(k,{a:round(b,4) if isinstance(b,float) else b for a,b in fits[k].items() if a in ('m','b','r2','p_m','resid_sd','n')})
print(summ['statewide']['ballot_share'])
