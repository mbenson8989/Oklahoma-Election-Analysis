#!/bin/bash
set -e; cd /workspace/oklahoma/scripts
# ./fetch_exports.sh   # needs OKER_APP_KEY; raw exports are already saved in sources/ and raw/
python3 pass_a.py; python3 pass_b.py; python3 compare_passes.py
python3 analysis.py >/dev/null; python3 charts.py; python3 build_wiki.py; python3 verify_wiki.py >/dev/null
echo done
