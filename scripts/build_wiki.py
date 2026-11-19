import pandas as pd, json, shutil, os
R='/workspace/oklahoma/repo/'; W='/workspace/oklahoma/wiki/'; os.makedirs(W+'images',exist_ok=True)
o=pd.read_pickle('/tmp/ok_o.pkl'); J=json.load(open(R+'OK_results_summary.json'))
K=J['K']; F=J['fits']; S=J['statewide']['sums']; M=J['statewide']['metrics']; BS=J['statewide']['ballot_share']; B=J['ballots_statewide']; C=J['counts']; D=J['desc']
for f in os.listdir(R):
    if f.endswith('.png'): shutil.copy(R+f,W+'images/'+f)
nm=lambda c: c.title().replace('Mcc','McC').replace('Mci','McI').replace('Leflore','Le Flore')
def sg(x,d=2): return f"{x:+.{d}f}".replace('-','−')
def pc(x,d=2): return f"{x:.{d}f}%"
def n(x): return f"{int(round(x)):,}".replace('-','−')
def sn(x): v=int(round(x)); return ('+' if v>0 else '−' if v<0 else '')+f"{abs(v):,}"
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
BANNER=("> **\\*2026 figures are marked UNOFFICIAL throughout this analysis.** They are the Oklahoma State Election Board's County Level Results export for the "
"November 3, 2026 general election ([results.okelections.gov](https://results.okelections.us/OKER/?elecDate=20261103)), data last updated 11/06/2026, downloaded 11/19/2026. "
"The Board's results site labels these \"Official Results\" (county election boards certified on Nov 6, 2026); they stay marked \\* here by project rule. "
"2022 and 2024 figures are official Board results. Governor race unless a page says otherwise; denominator is total governor votes, all candidates (the Board does not publish county ballots cast). "
"Registration: Board report vr2420, \"Current Registration Statistics by County,\" as of Nov 1, 2022 and Nov 1, 2026. Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. "
"These pages measure a pattern; they make no claim about intent, fraud or cause.")
REL=lambda here: '\n---\n**Related:** '+' · '.join(x for x in ['[Home](Home)','[Bottom-Up Reverse Math](Reverse-Math)','[Locked Oklahoma Formula](Locked-Oklahoma-Formula)','[Floor and Ceiling Counties](Floor-and-Ceiling)','[Graphs](Graphs)',f'[Cedar County Audit (Nebraska)]({CEDAR})'] if here not in x)+'\n'
k22=K['k_OK_2022']; k26=K['k_OK_2026']; SF=K['state_forward']; SB=K['state_backward']
cap=J['ceiling_dG']; flo=J['floor_dG']; rt=J['resid_top5']; rb=J['resid_bottom5']
big6=o.index[:6].tolist()
def grp(ix):
    g=o.loc[ix]; s=lambda c: g[c].sum()
    S22=100*s('D22')/s('T22'); S26=100*s('D26')/s('T26'); R22=100*s('DREG22')/s('TREG22'); R26=100*s('DREG26')/s('TREG26')
    return S22,S26,R22,R26,(S26-R26)-(S22-R22),g.dG.median(),g.dG.min(),g.dG.max(),g.resid.median()
# ---------------- Home ----------------
h=f"""# Oklahoma 2022 vs 2026 Governor Race: ΔG Method and Reverse Factoring

**Staged draft, built Nov 19 2026 (America/Chicago). Not yet published.**

{BANNER}

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit]({CEDAR}) on the [Nebraska Election Analysis wiki](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki), the origin of the ΔG method. This wiki applies the same county-by-county arithmetic to all 77 Oklahoma counties, using Oklahoma State Election Board numbers only, and runs the reverse factoring in both directions: a forward surplus (registration-implied expected Democratic vote vs. actual) and a backward solve (the registration share and constant implied by the actual result). The constant is Oklahoma's own, derived from Oklahoma statewide totals.

## Pages

Start with the Cedar County audit in Nebraska. That is where the method began. The Oklahoma pages then build up from one county (Texas County) to the six largest counties, to all 77 counties, and to the formula.

1. [Cedar County Audit]({CEDAR}) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Texas County → the six largest counties → all 77, the expected-loss residual, the forward surplus and the backward solve
3. [Locked Oklahoma Formula](Locked-Oklahoma-Formula): the equations, how the Oklahoma constant is derived, and a blank fill-in template
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the top and bottom of ΔG and of the residual, and the over-ballot check
5. [Graphs](Graphs): county slope chart, forward-fit scatter, ΔG and residual bars by population, stacked share bars, backward-solve scatter

## Statewide at a glance

| Measure | 2022 (official) | 2026\\* | Change | 2024 presidential (context, official) |
|---|---|---|---|---|
| Democratic registration (Nov 1) | {n(S['DREG22'])} | {n(S['DREG26'])} | {sn(S['DREG26']-S['DREG22'])} ({sg(100*(S['DREG26']/S['DREG22']-1),1)}%) | {n(S['DREG24'])} |
| Total registration (Nov 1) | {n(S['TREG22'])} | {n(S['TREG26'])} | {sn(S['TREG26']-S['TREG22'])} | {n(S['TREG24'])} |
| Democratic votes | {n(S['D22'])} (Hofmeister) | {n(S['D26'])}\\* (Munson) | {sn(S['D26']-S['D22'])}\\* | {n(S['D24'])} (Harris) |
| Total votes in the race, all candidates | {n(S['T22'])} (4 candidates) | {n(S['T26'])}\\* (5 candidates) | {sn(S['T26']-S['T22'])}\\* | {n(S['T24'])} |
| Total ballots cast, statewide † | {n(B['22']['rounded'])} | {n(B['26']['rounded'])}\\* | {sn(B['26']['rounded']-B['22']['rounded'])}\\* | {n(B['24']['rounded'])} |
| Democratic share of race votes (S) | {pc(M['S22'])} | {pc(M['S26'])}\\* | {sg(M['S26']-M['S22'])} pts\\* | {pc(M['S24'])} |
| Democratic share of ballots cast † | {pc(BS['S22_ballots'])} | {pc(BS['S26_ballots'])}\\* | {sg(BS['S26_ballots']-BS['S22_ballots'])} pts\\* | {pc(BS['S24_ballots'])} |
| Democratic registration share (R) | {pc(M['R22'])} | {pc(M['R26'])} | {sg(M['R26']-M['R22'])} pts | {pc(M['R24'])} |
| G = S − R (over/under-performance) | {sg(M['G22'])} | {sg(M['G26'])}\\* | ΔG {sg(M['dG'])}\\* | {sg(M['G24'])} |
| Expected loss = R2022 − R2026 | | | {sg(M['EL'])} pts | |
| **Residual = ΔG − expected loss** | | | **{sg(M['resid'])} pts\\*** | |

† The Board does not publish ballots cast by county. The statewide figure is the Board's published statewide turnout percentage ({B['22']['turnoutPerc']}% in 2022, {B['26']['turnoutPerc']}% in 2026, {B['24']['turnoutPerc']}% in 2024) × Nov 1 total registration; the 2022 result, {n(B['22']['rounded'])}, equals the Board's published 2022 total ballots cast. County pages use the race-total denominator.

## County results in brief

- **ΔG rose in all 77 counties.** County median ΔG {sg(D['dG']['median'])}\\* (mean {sg(D['dG']['mean'])}\\*), from {sg(D['dG']['min'])}\\* ({nm(D['dG']['argmin'])}) to {sg(D['dG']['max'])}\\* ({nm(D['dG']['argmax'])}). Democratic registration share fell in all 77 counties; registered Democrats fell in {C['DREG_fell']} of 77 (the exceptions, the non-loss counties, are Oklahoma and Canadian).
- **Residual (ΔG minus expected loss)** is positive in {C['resid_pos']} counties and negative in {C['resid_neg']}. County median {sg(D['resid']['median'])}\\*, range {sg(D['resid']['min'])}\\* ({nm(D['resid']['argmin'])}) to {sg(D['resid']['max'])}\\* ({nm(D['resid']['argmax'])}).
- **Top 5 residual:** {', '.join(f"{nm(c)} {sg(o.loc[c,'resid'])}\\*" for c in rt)}.
- **Bottom 5 residual:** {', '.join(f"{nm(c)} {sg(o.loc[c,'resid'])}\\*" for c in rb)}.
- **Ceiling counties** (five largest ΔG): {', '.join(f"{nm(c)} {sg(o.loc[c,'dG'])}\\*" for c in cap)}. **Floor counties** (five smallest ΔG): {', '.join(f"{nm(c)} {sg(o.loc[c,'dG'])}\\*" for c in flo)}.
- **Oklahoma constant:** k<sub>OK</sub> = S ÷ R from Oklahoma statewide 2022 totals = {pc(M['S22'],4)} ÷ {pc(M['R22'],4)} = **{k22:.4f}** Democratic vote-share points per point of Democratic registration share. In 2026\\* the same ratio is {k26:.4f}.
- **Forward surplus (statewide):** at k<sub>OK</sub> and the Nov 1, 2026 registration share, the registration-implied Democratic governor vote is {n(SF['expected_D26'])}; actual {n(SF['actual_D26'])}\\*; surplus **{sn(SF['surplus'])}\\***.
- **Backward solve (statewide):** the 2026\\* result implies a Democratic registration share of {pc(SB['R26_implied'])} at k<sub>OK</sub> (actual {pc(SB['R26_actual'])}, gap {sg(SB['gap_pts'])} pts), about {n(SB['implied_DREG26'])} registered Democrats vs. {n(SB['actual_DREG26'])} on the rolls. Backward-solved offset votes (residual × 2026 race total): {sn(SB['offset_votes_pooled'])}\\* pooled, {sn(SB['offset_votes_county_sum'])}\\* summed over counties.
- **Over-ballot check:** no county has Democratic + Republican governor votes above the governor-race total, and no county has more governor votes than registered voters, in either year. A check against county ballots cast cannot be run because the Board does not publish county ballots cast (see [Floor and Ceiling](Floor-and-Ceiling#over-ballot-check)).

## Read this before using the numbers

- **Oklahoma's registration drop is large and uneven.** Statewide Democratic registration fell {n(S['DREG22']-S['DREG26'])} ({sg(100*(S['DREG26']/S['DREG22']-1),1)}%) while total registration rose. The losses are deepest in southeastern counties with many long-time registered Democrats who already voted Republican for governor in 2022 (for example Coal, where registered Democrats fell {n(o.loc['COAL','DREG22'])} → {n(o.loc['COAL','DREG26'])}). In those counties the expected loss is large and ΔG is large mostly because R fell, not because S rose; the residual separates the two.
- **The field changed.** 2022 had four governor candidates (Stitt R, Hofmeister D, Bruno L, Yen I). 2026 had five (Mazzei R, Munson D, and three independents). The race-total denominator includes all of them.
- **Registered Democrats are not the only people who vote for Democrats.** Independents and Libertarians were {pc(100*(S['TREG26']-S['DREG26']-S['RREG26'])/S['TREG26'],1)} of Nov 1, 2026 registrants.
- **A large residual is not evidence of altered votes.** Candidate choice, crossover voting, turnout differences and list maintenance all move these numbers; the arithmetic cannot separate them.
- **2026 is marked unofficial (\\*)** everywhere on these pages.

## Verification

Every county figure was computed twice by two independently written programs: pass A (pandas; the Board's County Level Results **CSV** export; registration parsed from `pdftotext -layout`) and pass B (plain Python with exact fractions; the Board's separate County Level Results **XML** export; registration parsed from pdfplumber word positions). 77 counties × 40 fields = 3,080 figures compared: **0 mismatches**. County sums equal the Board's statewide totals in all three elections (governor 2022 {n(S['T22'])}, governor 2026 {n(S['T26'])}\\*, president 2024 {n(S['T24'])}) and the vr2420 Grand Total lines (Democrats {n(S['DREG22'])} / {n(S['DREG26'])}; total {n(S['TREG22'])} / {n(S['TREG26'])}). Reports are in the repo's `verification/` folder.

## Sources

All election and registration numbers come from the Oklahoma State Election Board. Population (sort order and size slope only) is from the U.S. Census Bureau. Retrieved Nov 19, 2026 (America/Chicago).

| Data | Status / as of | URL |
|---|---|---|
| 2022 general, County Level Results (CSV and XML export) | Official; Board data last updated 12/05/2022 | https://results.okelections.us/OKER/?elecDate=20221108 (Export menu), via https://oklahoma.gov/elections/elections-results/election-results/2022-election-results/2022-november-general-election.html |
| 2024 general, County Level Results (context) | Official; last updated 11/08/2024 | https://results.okelections.us/OKER/?elecDate=20241105 |
| 2026 general, County Level Results | **Marked UNOFFICIAL\\*** here; Board site says "Official Results"; last updated 11/06/2026 | https://results.okelections.us/OKER/?elecDate=20261103, via https://oklahoma.gov/elections/elections-results/election-results/2026-election-results/november-general-election.html |
| Statewide turnout % (statewide ballots cast) | Board results site, each election | same results pages |
| Voter registration by county and party, Nov 1, 2022 (vr2420, run 11/1/2022 3:09 AM) | Board report | https://oklahoma.gov/content/dam/ok/en/elections/voter-registration-statistics/2022-vr-statistics/vrstats-county-nov1-2022.pdf |
| Voter registration by county and party, Nov 1, 2024 (vr2420, run 11/1/2024 9:39 AM) | Board report | https://oklahoma.gov/content/dam/ok/en/elections/voter-registration-statistics/2024-vr-statistics/vrstats-county-nov1-2024.pdf |
| Voter registration by county and party, Nov 1, 2026 (vr2420, run 11/1/2026 3:05 AM) | Board report | https://oklahoma.gov/content/dam/ok/en/elections/voter-registration-statistics/2026-vr-statistics/2026-11-01-vrstats-county.pdf |
| Review of 2026 results-reporting issues, Cleveland and Comanche counties (Nov 13, 2026) | Board report | https://oklahoma.gov/content/dam/ok/en/elections/election-results/2026-election-results/20261103-reporting-issues-review.pdf |
| County population, July 1, 2025 | Census Vintage 2025 | https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv |
"""
open(W+'Home.md','w').write(h)
# ---------------- Reverse-Math ----------------
t=o.loc['TEXAS']
def row6(c):
    r=o.loc[c]; return f"| {nm(c)} | {n(r.population_2025)} | {n(r.DREG22)} → {n(r.DREG26)} | {n(r.D22)} → {n(r.D26)} | {n(r.T22)} → {n(r.T26)} | {sg(r.G22)} | {sg(r.G26)} | {sg(r.dG)} | {sg(r.EL)} | {sg(r.resid)} |"
gb=grp(big6); go=grp(o.index[6:]); ga=grp(o.index)
def grow(name,cnt,g): return f"| {name} | {cnt} | {pc(g[0])} → {pc(g[1])} | {pc(g[2])} → {pc(g[3])} | {sg(g[1]-g[0])} | {sg(g[3]-g[2])} | {sg(g[4])} | {sg(g[5])} ({sg(g[6])} to {sg(g[7])}) | {sg(g[8])} |"
def rrow(c):
    r=o.loc[c]; dag=' †' if r.nonloss else ''
    return f"| {nm(c)}{dag} | {n(r.population_2025)} | {pc(r.R22)} → {pc(r.R26)} | {sg(r.EL)} | {sg(r.dG)} | {sg(r.resid)} | {n(r.T26)} | {sn(r.bwd_offset_votes)} | {n(r.fwd_exp26)} | {sn(r.fwd_surplus)} | {pc(r.bwd_R26_implied)} |"
RH="| County | Population | Dem reg share 2022 → 2026 | Expected loss (pts) | ΔG\\* | Residual\\* (pts) | Gov votes 2026\\* | Backward-solved offset votes\\* | Forward expected Dem votes 2026 | Forward surplus\\* | Backward-solved R2026\\* |\n|---|---|---|---|---|---|---|---|---|---|---|"
fr=F['2022']; f6=F['2026']; rc=F['regconst']; sz=F['size']
rm=f"""# Bottom-Up Reverse Math

{BANNER}

The same arithmetic at three levels, from one county up to the whole state, then the reverse factoring in both directions with Oklahoma's own constant. The method comes from the [Cedar County Audit]({CEDAR}) in Nebraska. Denominator: total governor votes, all candidates, both years.

## Step 1: Texas County (largest residual)

| Step | Value |
|---|---|
| Democratic share of governor votes (S) | {pc(t.S22)} (2022: {n(t.D22)} of {n(t.T22)}) → {pc(t.S26)}\\* (2026: {n(t.D26)} of {n(t.T26)}\\*): **{sg(t.S26-t.S22)} points\\*** |
| Democratic registration share (R) | {pc(t.R22)} ({n(t.DREG22)} of {n(t.TREG22)}) → {pc(t.R26)} ({n(t.DREG26)} of {n(t.TREG26)}): **{sg(t.R26-t.R22)} points** |
| G 2022 = S − R | {sg(t.G22)} |
| G 2026\\* | {sg(t.G26)}\\* |
| ΔG = G 2026 − G 2022 | **{sg(t.dG)}\\*** |
| Expected loss = R 2022 − R 2026 | {sg(t.EL)} |
| Residual = ΔG − expected loss | {sg(t.dG)} − {t.EL:.2f} = **{sg(t.resid)}\\*** (= change in S) |
| Backward-solved offset votes = residual × 2026 gov votes ÷ 100 | {sg(t.resid)} × {n(t.T26)} ÷ 100 = **{sn(t.bwd_offset_votes)}\\*** |
| Forward: county constant k = S2022 ÷ R2022 | {t.S22:.4f} ÷ {t.R22:.4f} = {t.k22:.4f} |
| Forward: registration-implied expected Dem votes 2026 = gov votes 2026 × k × R2026 ÷ 100 | {n(t.T26)} × {t.k22:.4f} × {t.R26:.4f} ÷ 100 = {n(t.fwd_exp26)} |
| Forward surplus = actual − expected | {n(t.D26)} − {n(t.fwd_exp26)} = **{sn(t.fwd_surplus)}\\*** |
| Backward: registration share implied by the 2026 result = S2026 ÷ k | {t.S26:.4f} ÷ {t.k22:.4f} = **{pc(t.bwd_R26_implied)}\\*** vs actual {pc(t.R26)} (gap {sg(t.bwd_reg_gap_pts)} pts) |

## Step 2: the six largest counties

Largest to smallest population.

| County | Population | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* | Total gov votes 2022 → 2026\\* | G 2022 | G 2026\\* | ΔG\\* | Expected loss | Residual\\* |
|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(row6(c) for c in big6) + f"""

Oklahoma and Canadian are the state's only two non-loss counties (registered Democrats rose); their registration share still slipped because total registration grew faster.

## Step 3: all 77 counties

| Group | Counties | Dem vote share | Dem registration share | Vote-share change\\* | Reg-share change | Pooled ΔG\\* | County median ΔG\\* (range) | County median residual\\* |
|---|---|---|---|---|---|---|---|---|
{grow('Six largest counties',6,gb)}
{grow('Other counties',71,go)}
{grow('All Oklahoma counties',77,ga)}

- ΔG rose in all 77 counties. County-level SD of ΔG: {D['dG']['sd']:.2f} points.
- **Size slope:** ΔG = {sz['b']:.2f} {sg(sz['m'])} × log10(population) (R² = {sz['r2']:.3f}, p = {sz['p_m']:.2g}). County size explains little of the spread in Oklahoma.

## Expected-Loss Residual and Backward-Solved Offset Votes (NE/IA/SD/KS method)

The formulas, exactly as the sister wikis define them (Nebraska `regdrop`/`resid`/`unexpl_votes`; Iowa `reg_share_loss`/`residual`/`residual_votes`; South Dakota "residual = ΔG − registration-share drop"; Kansas expected-loss layer):

- **Expected loss** (points) = Dem registration share 2022 − Dem registration share 2026
- **Residual** (points) = ΔG − expected loss = Dem share of governor votes 2026 − Dem share of governor votes 2022
- **Backward-solved offset votes** = residual ÷ 100 × 2026 total governor votes = 2026 Dem votes − (2022 Dem share × 2026 total governor votes)

Statewide (pooled): expected loss {sg(M['EL'])} pts (R {pc(M['R22'])} → {pc(M['R26'])}), ΔG {sg(M['dG'])}\\*, residual **{sg(M['resid'])}\\***. Offset votes {sg(M['resid'])} × {n(S['T26'])} ÷ 100 = **{sn(SB['offset_votes_pooled'])}\\*** pooled; county sum {sn(SB['offset_votes_county_sum'])}\\*. County residual: median {sg(D['resid']['median'])}\\*, mean {sg(D['resid']['mean'])}\\*, SD {D['resid']['sd']:.2f}; positive in {C['resid_pos']}, negative in {C['resid_neg']}.

**Registration constant** (South Dakota's check, fitted on Oklahoma's 77 counties): ΔG = {rc['b']:.2f} {sg(rc['m'])} × expected loss (slope SE {rc['m_se']:.2f}, R² {rc['r2']:.3f}). In Oklahoma about a third of a point of ΔG comes with each point of registration-share decline, well short of the one-for-one a pure registration effect would give.

## Forward surplus (registration-implied expected Democratic vote vs actual)

- **Oklahoma constant** k<sub>OK</sub> = statewide S2022 ÷ statewide R2022 = {pc(M['S22'],4)} ÷ {pc(M['R22'],4)} = **{k22:.4f}** (derivation on [Locked Oklahoma Formula](Locked-Oklahoma-Formula#the-oklahoma-constant)).
- **Statewide:** expected Dem votes 2026 = {n(S['T26'])} × {k22:.4f} × {M['R26']:.4f}% = {n(SF['expected_D26'])}. Actual {n(SF['actual_D26'])}\\*. **Forward surplus {sn(SF['surplus'])}\\*.**
- **County level:** each county uses its own 2022 ratio k = S2022 ÷ R2022 (the same formula as k<sub>OK</sub>, applied to the county), so the county's 2022 starting point carries forward. Sum of county forward surpluses: {sn(SB['fwd_surplus_county_sum'])}\\*. County range {sn(D['fwd_surplus']['min'])} ({nm(D['fwd_surplus']['argmin'])}) to {sn(D['fwd_surplus']['max'])} ({nm(D['fwd_surplus']['argmax'])}).

## Backward solve (registration share and constant implied by actual results)

- **Statewide:** registration share implied by the 2026\\* result at k<sub>OK</sub> = {M['S26']:.4f} ÷ {k22:.4f} = **{pc(SB['R26_implied'])}** vs actual {pc(SB['R26_actual'])}: gap **{sg(SB['gap_pts'])} pts**, i.e. about {n(SB['implied_DREG26'])} registered Democrats implied vs {n(SB['actual_DREG26'])} on the Nov 1, 2026 rolls ({sn(SB['implied_minus_actual_DREG26'])}).
- **Constant implied by the 2026 result:** k2026 = S2026 ÷ R2026 = {M['S26']:.4f} ÷ {M['R26']:.4f} = **{k26:.4f}** (vs {k22:.4f} in 2022; 2024 presidential {K['k_OK_2024pres']:.4f}).
- **County level:** backward-solved R2026 = S2026 ÷ county k; median gap {sg(D['bwd_reg_gap_pts']['median'])} pts, range {sg(D['bwd_reg_gap_pts']['min'])} ({nm(D['bwd_reg_gap_pts']['argmin'])}) to {sg(D['bwd_reg_gap_pts']['max'])} ({nm(D['bwd_reg_gap_pts']['argmax'])}).

## Oklahoma-only fitted constants (Kansas-style forward fit)

Least squares across the 77 counties, Oklahoma data only: **G = m × (R/100) + b**.

| Fit | n | m (multiplier) | b (offset, pts) | R² | Residual SD (pts) | Counties within ±2 / ±5 pts |
|---|---|---|---|---|---|---|
| 2022 (official) | 77 | {fr['m']:.2f} (95% CI {fr['m_ci'][0]:.2f} to {fr['m_ci'][1]:.2f}) | {fr['b']:.2f} ({fr['b_ci'][0]:.2f} to {fr['b_ci'][1]:.2f}) | {fr['r2']:.3f} | {fr['resid_sd']:.2f} | {fr['within_2']} / {fr['within_5']} |
| 2026\\* | 77 | {f6['m']:.2f} ({f6['m_ci'][0]:.2f} to {f6['m_ci'][1]:.2f}) | {f6['b']:.2f} ({f6['b_ci'][0]:.2f} to {f6['b_ci'][1]:.2f}) | {f6['r2']:.3f} | {f6['resid_sd']:.2f} | {f6['within_2']} / {f6['within_5']} |

In 2022, counties with more registered Democrats had a lower G (the multiplier is negative: high-registration southeastern counties voted well below their Democratic registration). In 2026\\* that slope nearly disappears (R² {f6['r2']:.3f}), because registration share fell most where it had been highest.

## Top and bottom counties by residual

Five highest residuals:

{RH}
""" + '\n'.join(rrow(c) for c in rt) + f"""

Five lowest residuals:

{RH}
""" + '\n'.join(rrow(c) for c in rb) + f"""

![Residual after the expected loss, by population](images/OK_Expected_Loss_Residual_Bars_by_Population.png)

*Residual (ΔG minus expected loss) for all 77 counties, largest to smallest population. Orange: top 5. Blue: bottom 5. Hatched: non-loss counties.*

> **Hypothesis label.** Turning the residual or the forward surplus into "offset votes" and calling them injected, switched or offset votes is a hypothesis the arithmetic cannot test. The same numbers reflect candidate choice, crossover voting by Republicans and Independents, turnout changes, registration-list maintenance and any other cause. Candidate votes are not turnout, and registered Democrats are not the only people who vote for Democrats.

## All 77 counties

Largest to smallest population. † = non-loss county (registered Democrats did not fall).

| County | Population | Dem gov votes 2022 | Gov votes 2022 | Dem reg 2022 | Total reg 2022 | G 2022 | Dem gov votes 2026\\* | Gov votes 2026\\* | Dem reg 2026 | Total reg 2026 | G 2026\\* | ΔG\\* | Expected loss | Residual\\* | Offset votes\\* | Forward surplus\\* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(f"| {nm(c)}{' †' if r.nonloss else ''} | {n(r.population_2025)} | {n(r.D22)} | {n(r.T22)} | {n(r.DREG22)} | {n(r.TREG22)} | {sg(r.G22)} | {n(r.D26)} | {n(r.T26)} | {n(r.DREG26)} | {n(r.TREG26)} | {sg(r.G26)} | {sg(r.dG)} | {sg(r.EL)} | {sg(r.resid)} | {sn(r.bwd_offset_votes)} | {sn(r.fwd_surplus)} |" for c,r in o.iterrows()) + '\n' + REL('Reverse-Math')
open(W+'Reverse-Math.md','w').write(rm)
# ---------------- Locked formula ----------------
FR=json.load(open('/workspace/oklahoma/verification/fit_regdrop_check.json')); P=FR['path2_exact']; TU=FR['tulsa']
FITSEC=f"""## Oklahoma fitted equation

```
Oklahoma equation:  ΔG = {sg(P['b'])} + {P['m']:.2f} × (Dem registration-share drop, points)
Four decimals:      ΔG = {sg(P['b'],4)} + {P['m']:.4f} × (Dem registration-share drop, points)
```

| Item | Rounded | 4 decimals |
|---|---|---|
| Constant (intercept) | {sg(P['b'])}\\* | {sg(P['b'],4)}\\* |
| Constant standard error | {P['se_b']:.2f} | {P['se_b']:.4f} |
| Multiplier (slope) | {P['m']:.2f}\\* | {P['m']:.4f}\\* |
| Slope standard error | {P['se_m']:.2f} | {P['se_m']:.4f} |
| R² | {P['r2']:.2f}\\* | {P['r2']:.4f}\\* |

Fitted by least squares across all 77 counties (n = 77): 2022 to 2026\\* governor race, governor-votes denominator, Nov 1 vr2420 registration (all registered voters). Registration-share drop = R 2022 − R 2026, in points. Computed twice (numpy least squares on pass A; exact-fraction normal equations on pass B raw counts); the two match to within 1e-14.

**What it means:** across Oklahoma's counties, each 1-point drop in Democratic registration share goes with about {P['m']:.2f} points of ΔG\\*, starting from about {sg(P['b'])}\\* when the share does not fall. The fit explains about {round(100*P['r2'])}% of the county-to-county differences in ΔG\\*. This line describes the county pattern; it does not prove anything. The locked formula below uses a fixed 1:1 subtraction (residual = ΔG − registration-share drop); the fitted line is shown for comparison.

**Worked example: Tulsa.** R fell from {TU['R22']:.2f} to {TU['R26']:.2f}, a drop of {TU['EL']:.4f} points. Predicted ΔG = {sg(P['b'],4)} + {P['m']:.4f} × {TU['EL']:.4f} = {sg(TU['pred'])}\\*. Actual ΔG = {sg(TU['dG'])}\\*. Difference from the fitted line (actual − predicted) = {sg(TU['diff'])}\\*. This difference is not the line-11 residual in the template below, which is ΔG minus the registration-share drop.

"""
lf=f"""# Locked Oklahoma Formula

{BANNER}

{FITSEC}## The equation

- **S** (Democratic vote share) = Democratic governor votes ÷ total votes in the governor race (all candidates) × 100
- **R** (Democratic registration share) = Democratic registered voters ÷ total registered voters (vr2420 Total column, Nov 1 report) × 100
- **G** = S − R (Democratic over/under-performance against registration)
- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (R2026 − R2022)
- **Expected loss** = R2022 − R2026 (the vote-share loss expected from the registration-share decline alone)
- **Residual** = ΔG − expected loss = S2026 − S2022 (the observed change in vote share left after the expected loss)
- **Backward-solved offset votes** = residual ÷ 100 × 2026 governor votes
- **Forward (registration-implied) expected Dem votes 2026** = 2026 governor votes × k × R2026 ÷ 100; **forward surplus** = actual Dem votes 2026 − expected
- **Backward-solved registration share** = S2026 ÷ k; **backward-solved constant** k2026 = S2026 ÷ R2026
- **Gap in votes** (Nebraska comparison line) = D2026 − D2022 × (RegDem2026 ÷ RegDem2022)

**Why race votes, not ballots.** The method's first choice is total ballots cast. The Oklahoma State Election Board's county results exports (CSV and XML) and its results site report votes by race and candidate only; they do not report ballots cast by county. So county ballots cast are **missing** for every county in 2022 and 2026, and the denominator is total governor votes in both years (the Kansas wiki made the same change). Statewide, the Board publishes a turnout percentage; turnout % × Nov 1 registration gives {n(B['22']['rounded'])} ballots in 2022 (equal to the Board's published total) and {n(B['26']['rounded'])}\\* in 2026. On that statewide basis the Democratic share of ballots was {pc(BS['S22_ballots'])} and {pc(BS['S26_ballots'])}\\* (vs {pc(M['S22'])} and {pc(M['S26'])}\\* of governor votes).

## The Oklahoma constant

Oklahoma-only, from Oklahoma statewide totals; no other state's constant is used.

| Line | Item | 2022 (official) | 2026\\* |
|---|---|---|---|
| a | Democratic governor votes, statewide (Board statewide total = sum of 77 counties) | {n(S['D22'])} | {n(S['D26'])}\\* |
| b | Total governor votes, statewide | {n(S['T22'])} | {n(S['T26'])}\\* |
| c | S = a ÷ b × 100 | {M['S22']:.4f} | {M['S26']:.4f}\\* |
| d | Registered Democrats, vr2420 Grand Total (Nov 1) | {n(S['DREG22'])} | {n(S['DREG26'])} |
| e | Total registered, vr2420 Grand Total (Nov 1) | {n(S['TREG22'])} | {n(S['TREG26'])} |
| f | R = d ÷ e × 100 | {M['R22']:.4f} | {M['R26']:.4f} |
| g | **k = c ÷ f** | **{k22:.4f}** (k<sub>OK</sub>, the locked constant) | {k26:.4f}\\* (backward-solved) |

k<sub>OK</sub> = {k22:.4f} is the locked Oklahoma constant: in the 2022 baseline, each point of statewide Democratic registration share went with {k22:.4f} points of Democratic governor vote share. The forward step applies it to the 2026 registration share; the backward step divides the 2026 vote share by it. County rows use the same formula on the county's own 2022 numbers (county k = county S2022 ÷ county R2022), because Oklahoma's counties start far apart (county k ranges from {o.k22.min():.4f} in {nm(o.k22.idxmin())} to {o.k22.max():.4f} in {nm(o.k22.idxmax())}).

## Blank template

| Line | Item | 2022 | 2026\\* |
|---|---|---|---|
| 1 | Democratic governor votes | ______ | ______ |
| 2 | Total votes in the governor race (all candidates) | ______ | ______ |
| 3 | S = line 1 ÷ line 2 × 100 | ______ | ______ |
| 4 | Democratic registered voters (Nov 1 vr2420) | ______ | ______ |
| 5 | Total registered voters (Nov 1 vr2420) | ______ | ______ |
| 6 | R = line 4 ÷ line 5 × 100 | ______ | ______ |
| 7 | G = line 3 − line 6 | ______ | ______ |
| 8 | ΔG = G 2026 − G 2022 | | ______ |
| 9 | Expected loss = R 2022 − R 2026 | | ______ |
| 10 | Did Democratic registration fall? (line 4: 2026 < 2022) | | Yes / No |
| 11 | Residual = line 8 − line 9 | | ______ |
| 12 | Backward-solved offset votes = line 11 × line 2 (2026) ÷ 100 | | ______ |
| 13 | County constant k = line 3 (2022) ÷ line 6 (2022) | ______ | |
| 14 | Forward expected Dem votes = line 2 (2026) × line 13 × line 6 (2026) ÷ 100 | | ______ |
| 15 | Forward surplus = line 1 (2026) − line 14 | | ______ |
| 16 | Backward-solved R 2026 = line 3 (2026) ÷ line 13 | | ______ |
| 17 | Over-ballot flag: line 1 + Republican votes > ballots cast? (ballots not published by county in Oklahoma; check against line 2 and line 5) | ______ | ______ |

**Non-loss counties** (registered Democrats did not fall: Oklahoma and Canadian) get the residual shown for completeness, marked †, and statewide figures are given with them included.

## Rules for using this formula

1. **If a county lost Democratic registration, run the residual step** (lines 9 to 12). Non-loss counties are marked † and reported raw.
2. **The starting point is different in every state. Don't assume another state's numbers carry over.** Oklahoma's constant k<sub>OK</sub> = {k22:.4f} comes from Oklahoma's own statewide totals; its county median ΔG is {sg(D['dG']['median'])}\\*.
3. **Always pull out the ceiling and floor counties**, and the top and bottom residual counties ([Floor and Ceiling Counties](Floor-and-Ceiling)).
4. **Mark every 2026 number with \\*.**

## Worked example: Texas County

| Line | Item | 2022 | 2026\\* |
|---|---|---|---|
| 1 | Democratic governor votes | {n(t.D22)} | {n(t.D26)}\\* |
| 2 | Governor race total | {n(t.T22)} | {n(t.T26)}\\* |
| 3 | S | {t.S22:.2f} | {t.S26:.2f}\\* |
| 4 | Democratic registered | {n(t.DREG22)} | {n(t.DREG26)} |
| 5 | Total registered | {n(t.TREG22)} | {n(t.TREG26)} |
| 6 | R | {t.R22:.2f} | {t.R26:.2f} |
| 7 | G | {sg(t.G22)} | {sg(t.G26)}\\* |
| 8 | ΔG | | {sg(t.dG)}\\* |
| 9 | Expected loss | | {sg(t.EL)} |
| 10 | Registration fell? | | Yes |
| 11 | Residual | | {sg(t.resid)}\\* |
| 12 | Offset votes | | {sn(t.bwd_offset_votes)}\\* |
| 13 | k | {t.k22:.4f} | |
| 14 | Forward expected Dem votes | | {n(t.fwd_exp26)} |
| 15 | Forward surplus | | {sn(t.fwd_surplus)}\\* |
| 16 | Backward-solved R 2026 | | {t.bwd_R26_implied:.2f}\\* |
| 17 | Over-ballot flag | No | No |
""" + REL('Locked-Oklahoma-Formula')
open(W+'Locked-Oklahoma-Formula.md','w').write(lf)
# ---------------- Floor and ceiling ----------------
def fcrow(c):
    r=o.loc[c]; return f"| {nm(c)} | {n(r.population_2025)} | {sg(r.G22)} | {sg(r.G26)} | {sg(r.dG)} | {sg(r.EL)} | {sg(r.resid)} | {pc(r.R26,1)} | {n(r.DREG22)} → {n(r.DREG26)} | {n(r.D22)} → {n(r.D26)} |"
fc=f"""# Floor and Ceiling Counties

{BANNER}

## How to read floor and ceiling counties

The ceiling counties are the ones with the highest ΔG; the floor counties are the ones with the lowest ΔG.

- **The floor** is the single county with the lowest ΔG in the state. In Oklahoma that's {nm(flo[0])}, at {sg(o.loc[flo[0],'dG'])}\\*.
- **The ceiling** is the single county with the highest ΔG in the state. In Oklahoma that's {nm(cap[0])}, at {sg(o.loc[cap[0],'dG'])}\\*.

Every state has its own floor and ceiling. Oklahoma's ΔG is positive in all 77 counties, so even the floor county rose.

## Terminology

- **Ceiling counties**: the five largest ΔG: {', '.join(f"{nm(c)} {sg(o.loc[c,'dG'])}\\*" for c in cap)}.
- **Floor counties**: the five smallest ΔG: {', '.join(f"{nm(c)} {sg(o.loc[c,'dG'])}\\*" for c in flo)}.
- **Over-performing / under-performing counties**: the five highest and lowest residuals (ΔG minus expected loss), below.
- **Non-loss counties** (registered Democrats did not fall): Oklahoma ({n(o.loc['OKLAHOMA','DREG22'])} → {n(o.loc['OKLAHOMA','DREG26'])}; Dem governor votes {n(o.loc['OKLAHOMA','D22'])} → {n(o.loc['OKLAHOMA','D26'])}\\*) and Canadian ({n(o.loc['CANADIAN','DREG22'])} → {n(o.loc['CANADIAN','DREG26'])}; votes {n(o.loc['CANADIAN','D22'])} → {n(o.loc['CANADIAN','D26'])}\\*).
- **Registration fell and votes fell too:** {', '.join(nm(c) for c in o.index[(o.DREG26<o.DREG22)&(o.D26<o.D22)])}.

## Ceiling and floor detail

**Ceiling:** {sum(o.loc[c,'G22']<0 for c in cap)} of the five ceiling counties ({', '.join(nm(c) for c in cap if o.loc[c,'G22']<0)}) began 2022 with a negative G. In {', '.join(nm(c) for c in cap if o.loc[c,'EL']>o.loc[c,'resid'])}, most of the ΔG is expected loss (registration-share decline of {', '.join(f"{o.loc[c,'EL']:.2f}" for c in cap if o.loc[c,'EL']>o.loc[c,'resid'])} points respectively). Texas County is the exception: expected loss {o.loc['TEXAS','EL']:.2f} points and the state's largest residual, {sg(o.loc['TEXAS','resid'])}\\*.

**Floor:** in {', '.join(nm(c) for c in flo if o.loc[c,'resid']<0)} the Democratic share of governor votes fell (negative residual), which held ΔG down; in {', '.join(nm(c) for c in flo if o.loc[c,'resid']>=0)} vote share rose but the registration-share decline was small ({', '.join(f"{o.loc[c,'EL']:.2f}" for c in flo if o.loc[c,'resid']>=0)} points).

| County | Population | G 2022 | G 2026\\* | ΔG\\* | Expected loss | Residual\\* | Dem reg share 2026 | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* |
|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(fcrow(c) for c in cap+flo) + f"""

## Top 5 over- and under-performing counties by residual

| Rank | Over-performing | Residual\\* | Under-performing | Residual\\* |
|---|---|---|---|---|
""" + '\n'.join(f"| {i+1} | {nm(a)} | {sg(o.loc[a,'resid'])} | {nm(b)} | {sg(o.loc[b,'resid'])} |" for i,(a,b) in enumerate(zip(rt,rb))) + f"""

The under-performing counties are all in southern and eastern Oklahoma (Coal, Adair, Pushmataha, McCurtain, Johnston): Democratic share of governor votes fell there even though ΔG rose, because registration share fell even faster. The over-performing counties are Oklahoma County and its western neighbor Canadian (the state's two non-loss counties) and three western counties (Texas, Roger Mills, Kingfisher).

| County | Population | G 2022 | G 2026\\* | ΔG\\* | Expected loss | Residual\\* | Dem reg share 2026 | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* |
|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(fcrow(c) for c in rt+rb) + f"""

## Over-ballot check

The check asks whether Democratic + Republican votes exceed total ballots cast in any county.

- **County ballots cast are missing.** The Board's county results exports and results site do not publish county ballots cast for 2022 or 2026, so the ballots-cast test cannot be run at county level. No values were estimated.
- **Proxy checks run instead (both passes):** Democratic + Republican governor votes ≤ governor-race total in all 77 counties in both years (0 flags), and governor-race total ≤ Nov 1 registered voters in all 77 counties in both years (0 flags).
- **Statewide:** Democratic + Republican governor votes were {n(S['D22']+S['Rv22'])} in 2022 vs {n(B['22']['rounded'])} ballots cast, and {n(S['D26']+S['Rv26'])}\\* in 2026 vs {n(B['26']['rounded'])}\\* ballots (from the Board's statewide turnout %). No statewide over-ballot.

**Over-ballot counties: none found** on the checks that the published data allow.

## 2026 reporting note

The Board reviewed delayed election-night reporting in Cleveland and Comanche counties (security-protocol hold in Cleveland; tabulation-computer hard drive failure in Comanche, results hand-entered from voting-device tapes). The Board reports neither issue affected the vote count; both counties certified on Nov 6, 2026 ([review, Nov 13, 2026](https://oklahoma.gov/content/dam/ok/en/elections/election-results/2026-election-results/20261103-reporting-issues-review.pdf)). Cleveland residual {sg(o.loc['CLEVELAND','resid'])}\\*, Comanche {sg(o.loc['COMANCHE','resid'])}\\*.

![All 77 counties, ΔG in population order](images/OK_DeltaG_Bars_by_Population.png)

*All 77 counties, ΔG\\* in population order. Orange: ceiling (5 largest ΔG). Blue: floor (5 smallest ΔG). Hatched: non-loss counties.*
""" + REL('Floor-and-Ceiling')
open(W+'Floor-and-Ceiling.md','w').write(fc)
# ---------------- Graphs ----------------
gr=f"""# Graphs

> **\\*2026 figures are marked UNOFFICIAL** (Oklahoma State Election Board county export, last updated 11/06/2026). Governor race unless noted; denominator is total governor votes. Registration is the Nov 1 vr2420 report. These charts measure a pattern; they make no claim about intent, fraud or cause.

## 1. County slope chart

![County slope chart, G 2022 to G 2026](images/OK_Slope_G2022_to_G2026_County_Slope_Chart.png)

*Each line is one county, G 2022 to G 2026\\*. G rose in all 77 counties; ceiling counties (orange) rose most steeply; in four of the five most of the rise is registration-share loss.*

## 2. Forward surplus fit: G against R

![Forward surplus fit, G = m(R/100) + b, 2022 and 2026](images/OK_Forward_Surplus_Fit_G_vs_R.png)

*Least squares across 77 counties, Oklahoma data only. 2022: G = {fr['m']:.2f}·(R/100) + {fr['b']:.2f} (R² {fr['r2']:.3f}); 2026\\*: G = {f6['m']:.2f}·(R/100) + {f6['b']:.2f} (R² {f6['r2']:.3f}). Dashed: the statewide constant k<sub>OK</sub> = {k22:.4f}.*

## 3. ΔG by population

![Delta-G for all 77 counties in population order](images/OK_DeltaG_Bars_by_Population.png)

*All 77 counties, largest to smallest population. Floor: {nm(flo[0])} ({sg(o.loc[flo[0],'dG'])}\\*). Ceiling: {nm(cap[0])} ({sg(o.loc[cap[0],'dG'])}\\*).*

## 4. Residual after expected loss, by population

![Residual by population](images/OK_Expected_Loss_Residual_Bars_by_Population.png)

*Residual = ΔG − expected loss = change in Democratic share of governor votes. Top 5: {', '.join(nm(c) for c in rt)}. Bottom 5: {', '.join(nm(c) for c in rb)}.*

## 5. Stacked share bars with registration loss

![Democratic vote share with 2026 change stacked, registration-share loss below](images/OK_Stacked_Share_Reg_Loss_by_Population.png)

*Democratic share of governor votes (blue) with the 2022→2026\\* gain (orange) or fall (gray) stacked; Democratic registration-share loss (red) below the line. Population order.*

## 6. Backward solve

![Backward-solved registration share vs actual](images/OK_Backward_Solve_Implied_vs_Actual_Reg_Share.png)

*Registration share implied by each county's 2026\\* result at its own 2022 constant, against the actual Nov 1, 2026 share. Statewide: implied {pc(SB['R26_implied'])} vs actual {pc(SB['R26_actual'])} at k<sub>OK</sub> = {k22:.4f}.*
""" + REL('Graphs')
open(W+'Graphs.md','w').write(gr)
open(W+'_Sidebar.md','w').write(f"""**Oklahoma Election Analysis**

1. [[Home]]
2. [Cedar County Audit (Nebraska)]({CEDAR})
3. [[Bottom-Up Reverse Math|Reverse-Math]]
4. [[Locked Oklahoma Formula|Locked-Oklahoma-Formula]]
5. [[Floor and Ceiling Counties|Floor-and-Ceiling]]
6. [[Graphs]]

*2026 figures marked unofficial (\\*).*
""")
print('wiki built')
