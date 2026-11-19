import csv, json
V='/workspace/oklahoma/verification/'; RAW='/workspace/oklahoma/raw/'
A={r['county']:r for r in csv.DictReader(open(V+'passA_counties.csv'))}
B={r['county']:r for r in csv.DictReader(open(V+'passB_counties.csv'))}
assert set(A)==set(B) and len(A)==77
fields=[f for f in B[next(iter(B))] if f!='county']
rows=[]; mism=0
for c in sorted(A):
    for f in fields:
        a,b=A[c][f],B[c][f]
        if a in ('True','False') or b in ('True','False'): ok=(a==b); d=''
        else:
            fa,fb=float(a),float(b); d=abs(fa-fb); ok=d<=1e-9*max(1,abs(fb))
        mism+= not ok; rows.append([c,f,a,b,d,'MATCH' if ok else 'MISMATCH'])
with open(V+'compare_A_B_figure_by_figure.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['county','field','passA','passB','abs_diff','status']); w.writerows(rows)
sa=json.load(open(V+'passA_statewide.json')); sb=json.load(open(V+'passB_statewide.json'))
smis=[k for k in sb['sums'] if sa['sums'][k]!=sb['sums'][k]]+[k for k in sb['metrics'] if not isinstance(sb['metrics'][k],bool) and abs(sa['metrics'][k]-sb['metrics'][k])>1e-9]
# county sums vs the Board's own statewide totals (SW results JSON) and vr2420 Grand Total lines
off={}
for d,y in (('20221108','22'),('20241105','24'),('20261103','26')):
    sw=json.load(open(f'{RAW}sw_results_{d}.json'))['results'][0]
    off[y]={'sw_race_total':sw['totResults']['totalVotes'],'county_sum_T':sb['sums']['T'+y],'match':sw['totResults']['totalVotes']==sb['sums']['T'+y]}
vg=sa['vr_grand']
for y,k in (('22','2022'),('24','2024'),('26','2026')):
    off[y].update({'vr_grand_dem':vg[k]['Democrat'],'county_sum_DREG':sb['sums']['DREG'+y],'vr_grand_total':vg[k]['Total'],'county_sum_TREG':sb['sums']['TREG'+y]})
    off[y]['vr_match']=vg[k]['Democrat']==sb['sums']['DREG'+y] and vg[k]['Total']==sb['sums']['TREG'+y]
rep={'counties':77,'fields_per_county':len(fields),'figures_compared':len(rows),'county_mismatches':mism,'statewide_mismatches':smis,'vs_official_statewide':off}
json.dump(rep,open(V+'compare_report.json','w'),indent=1); print(json.dumps(rep,indent=1))
