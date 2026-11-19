# Verification (Oklahoma, staged Nov 19 2026)

- Pass A: `scripts/pass_a.py` (pandas; Board County Level Results CSV export; registration via `pdftotext -layout`).
- Pass B: `scripts/pass_b.py` (plain Python, exact `fractions.Fraction`; Board County Level Results XML export; registration via pdfplumber word positions).
- Compare: `scripts/compare_passes.py` → `compare_A_B_figure_by_figure.csv`, `compare_report.json`.

| Check | Result |
|---|---|
| County figures compared (77 × 40) | 3,080 |
| County mismatches A vs B | **0** |
| Statewide mismatches A vs B | **0** |
| County sum = Board statewide race total (2022 gov / 2024 pres / 2026 gov) | True / True / True |
| County sum = vr2420 Grand Total, Dem and total (2022 / 2024 / 2026) | True / True / True |
| Published county CSV vs pass B (3,080 fields) | 0 mismatches |
| Headline numbers on Home recomputed from pass B and found on page | True |
| Cedar Audit link on Home / UNOFFICIAL banner on all 5 pages | True / True |

Raw file hashes: `raw_sha256.txt`.
