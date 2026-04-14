#!/bin/bash
set -euo pipefail

mkdir -p data/raw

curl -L -o data/raw/airports.csv \
  "https://davidmegginson.github.io/ourairports-data/airports.csv"

curl -L -o data/raw/ne_110m_land.geojson \
  "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"

echo "NOTE: BTS T-100 data must be downloaded manually."
echo "Visit: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoession_VQ=GEE"
echo "Select: T-100 International Segment (All Carriers)"
echo "Fields: ORIGIN, DEST, PASSENGERS, DEPARTURES_PERFORMED, SEATS, YEAR, QUARTER"
echo "Place the file at: data/raw/t100_international.csv"
echo "Optional Eurostat file path: data/raw/eurostat_avia_par.tsv"
echo "Download complete."

