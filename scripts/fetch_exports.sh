#!/bin/bash
# Downloads the County Level Results exports (CSV and XML) the same way the public results page's Export menu does.
cd /workspace/oklahoma/raw
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"; B=https://results.okelections.gov/OKERS/
# OKER_APP_KEY: the anonymous app key the public results page (results.okelections.us/OKER) sends when you use its Export menu.
# It is not stored here. To obtain it, open the results page in a browser and read it from the page's own JavaScript
# (main.*.bundle.js, the connKey value), or simply download the County Level Results CSV/XML from the page's Export menu by hand
# and place the files in raw/ as YYYYMMDD_CLCSV.zip / YYYYMMDD_CLXML.zip.
: "${OKER_APP_KEY:?set OKER_APP_KEY (see comment above) or download the exports manually}"
TOK=$(curl -s -A "$UA" -X PUT -H "Content-Type: application/json" -d "{\"Username\":\"appuser\",\"Password\":\"${OKER_APP_KEY}\"}" ${B}enrapi/login/)
T=$(python3 -c "import sys,json;print(json.loads(sys.argv[1])[1:])" "$TOK")
for d in 20221108 20241105 20261103; do for k in CLCSV CLXML; do
  curl -s -A "$UA" -H "Authorization: Bearer $T" -o ${d}_${k}.zip "${B}enrapi/GetExtract/$k/$d"; done
  mkdir -p res_$d xml_$d; unzip -o -q ${d}_CLCSV.zip -d res_$d; unzip -o -q ${d}_CLXML.zip -d xml_$d
  curl -s -A "$UA" -H "Authorization: Bearer $T" -o sw_results_$d.json "${B}enrapi/GetResults/$d/SW/xx"
  curl -s -A "$UA" -H "Authorization: Bearer $T" -o sw_elec_$d.json "${B}enrapi/getelec/$d/SW/xx"
done
sha256sum *_CLCSV.zip *_CLXML.zip vr_*.pdf > /workspace/oklahoma/verification/raw_sha256.txt
