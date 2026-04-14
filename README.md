# Supersonic Route Demand Model

Public-data pipeline and interactive dashboard for ranking long-haul routes where Boom Overture-style service appears to make the strongest strategic business case, including both Mach 1.7 overwater flight and Boomless Cruise over land.

## What This Is

This project combines airport metadata, public traffic data, fare/yield heuristics, city-level business travel proxies, route geometry, and simplified aircraft economics to rank the top 50 route opportunities for mixed-regime supersonic service.

It is intentionally framed as a strategy model, not an airline-grade forecast. The output is designed to answer a business-development question:

> Which city pairs combine enough premium demand, enough time savings, and enough operational viability to justify serious supersonic route-planning attention?

## Current Output Snapshot

The latest pipeline run in bundled fallback mode analyzed `2,417` strategic route candidates and currently ranks these five routes highest:

1. `JFK-LHR` — score `92.89`
2. `NRT-SFO` — score `92.73`
3. `EWR-LHR` — score `92.12`
4. `LAX-NRT` — score `91.94`
5. `LAX-LHR` — score `91.47`

Additional summary metrics from the current run:

- Tier 1 routes: `50`
- Average modeled time saved: `4.09 hours`
- Average overwater share: `81.74%`
- Addressable premium passenger pool across top 50: `9.26M`
- Modeled supersonic revenue opportunity across top 50: `$4.99B`
- Pure overland routes in the current top 50: `2` (`JFK-LAX` and `JFK-SFO`)

`data/output/routes.json` is copied into `dashboard/public/routes.json` for the frontend.

## Boomless Cruise & Regulatory Context

This model incorporates Boom’s Boomless Cruise capability, announced on February 10, 2025, after XB-1’s January 28, 2025 supersonic flight validated that no audible boom reached the ground under Mach cutoff conditions. Boom’s official announcement says Boomless Cruise enables Overture to fly up to Mach 1.3 over land without an audible boom and can cut U.S. coast-to-coast times by up to 90 minutes.

On June 6, 2025, the White House issued the executive order `Leading the World in Supersonic Flight`, directing agencies to modernize the regulatory framework for civil supersonic flight. Separately, the `Supersonic Aviation Modernization Act` was introduced in the Senate on May 14, 2025 and states that FAA regulations should be revised to allow civil aircraft to operate above Mach 1 so long as no sonic boom reaches the ground in the United States.

This project therefore models three Overture speed regimes:

- Subsonic terminal/climb/descent phases
- Boomless Cruise over land
- Full Mach 1.7 supersonic cruise over water

The model assumes Boomless Cruise is operationally permitted over the United States. International overland supersonic rules remain unsettled, so international routes with large overland components should still be treated more cautiously than U.S. domestic corridors.

## Repository Layout

```text
supersonic-demand/
├── pipeline/
├── data/
├── dashboard/
├── notebooks/
├── scripts/
├── requirements.txt
└── README.md
```

## Methodology

### 1. Airport universe

- Source: OurAirports `airports.csv`
- Filter: `large_airport`
- Cleanup: drop missing IATA/lat/lon, normalize metro names for multi-airport cities such as New York and Washington

### 2. Traffic inputs

- Primary source: BTS T-100 International Segment data
- Optional source: Eurostat airport-pair data
- Bundled fallback: `data/raw/t100_sample.csv` with representative international and long-haul U.S. domestic business routes so the project runs end-to-end without the manual BTS download

Observed routes are canonicalized into undirected airport pairs, then aggregated into:

- annual passengers
- annual departures
- average seats per flight

### 3. Route generation

Candidate routes are built from a strategic subset of large airports:

- airports with observed international traffic in the bundled/public traffic files, or
- airports with `>= 15M` annual throughput in the included throughput table

Distance filter:

- minimum: `1,500 nm`
- maximum: `5,500 nm` soft cap
- routes over `4,250 nm` are flagged as range-limited for Overture

### 4. Overwater viability

- Source: Natural Earth 110m land polygons
- Method: sample the great-circle path at `20 nm` intervals
- Output: percentage of route distance that is operationally overwater

Because Natural Earth 110m is deliberately coarse for a fast-running portfolio pipeline, the model applies a conservative smoothing floor on canonical oceanic markets:

- transatlantic routes: minimum effective overwater share `0.85`
- transpacific routes: minimum effective overwater share `0.90`

This keeps major oceanic corridors from being artificially under-credited by coarse shoreline geometry.

### 5. Business Travel Index

The Business Travel Index (BTI) is a curated `0-100` city score built from public ranking families:

- metro GDP
- corporate HQ concentration
- financial center strength
- conference / event activity
- tech hub importance

The repo includes a prebuilt lookup at `data/processed/business_travel_index.csv` covering `112` cities.

### 6. Fare estimation

Because live premium-cabin fare data is generally paywalled or scraping-restricted, the model uses a defensible public-yield heuristic:

- transatlantic
- transpacific
- intra-Europe
- intra-Asia
- Middle East long-haul
- default long-haul

Business fare is estimated as:

`yield_per_km * distance_km * taper`

First class is modeled as `1.8x` business.

### 7. Time savings

The time model compares:

- Overture-style supersonic aircraft
- 787-9-style subsonic aircraft

It accounts for:

- overwater Mach 1.7 cruise
- overland Boomless Cruise
- transition overhead
- subsonic terminal phases

Returned route-level timing outputs now include:

- overwater cruise hours
- Boomless Cruise hours
- subsonic phase hours
- a “without Boomless” comparison block time
- Boomless-specific time savings in minutes

### 8. Scoring model

Composite route score is `0-100`, built from:

- Traffic volume: `0-25`
- Premium demand: `0-20`
- Time savings: `0-25`
- Route viability: `0-15`
- Revenue potential: `0-15`

Additional guardrails:

- gravity-estimated traffic is modestly discounted vs observed traffic
- low-BTI endpoints receive heavier penalties because premium demand matters more than raw seat volume for supersonic economics
- overland routes are no longer zeroed out; viability now scales from `8` points for all-land routes to `15` for all-water routes

Routes are also classified as:

- `overwater` (`>= 80%` overwater)
- `hybrid` (`20%` to `< 80%`)
- `overland` (`< 20%`)

### 9. Unit economics

For each route, the model estimates:

- revenue per flight
- cost per flight
- profit per flight
- annual revenue / cost / profit
- breakeven load factor
- payback period

Aircraft assumptions are intentionally simplified and editable in `pipeline/ingest/aircraft_perf.py`.

## Gravity Model Fallback

When full BTS data is unavailable, the project estimates missing route traffic using a gravity model calibrated against observed routes:

`annual_pax = K * throughput_a^alpha * throughput_b^beta / distance^gamma`

Current bundled-sample calibration:

- `K = 52.846243`
- `alpha = 0.26`
- `beta = 0.41`
- `gamma = 1.54`
- `R² = 0.52`

That `R²` is intentionally reported so the limitation is explicit. The bundled sample is only meant to create a credible demo baseline; the full BTS dataset should improve calibration materially.

## Running The Project

### Pipeline

```bash
cd supersonic-demand
python3 -m pip install -r pipeline/requirements.txt
./scripts/download_data.sh
python3 scripts/build_bti.py
PYTHONPATH=. python3 -m pipeline.run_pipeline
```

Outputs land in:

- `data/output/routes.json`
- `data/output/routes.csv`
- `data/output/summary.json`

### Dashboard

```bash
cd supersonic-demand/dashboard
npm install
npm run dev
```

The dashboard expects:

- `public/routes.json`
- `public/summary.json`

Those are updated automatically by the pipeline export step.

## Data Sources

- OurAirports: <https://davidmegginson.github.io/ourairports-data/airports.csv>
- BTS TranStats T-100: <https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoession_VQ=GEE>
- Eurostat aviation tables: <https://ec.europa.eu/eurostat/databrowser/view/avia_par/default/table>
- Natural Earth land polygons: <https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson>
- Boom official Boomless Cruise announcement: <https://boomsupersonic.com/press-release/boom-supersonic-announces-boomless-cruise>
- White House executive order: <https://www.whitehouse.gov/presidential-actions/2025/06/leading-the-world-in-supersonic-flight/>
- Supersonic Aviation Modernization Act: <https://www.congress.gov/bill/119th-congress/senate-bill/1759>
- Public throughput proxies: bundled `airport_throughput.csv` synthesized from widely published airport traffic summaries
- BTI source families: Brookings metro GDP summaries, Fortune Global 500 HQ counts, GFCI, ICCA meeting rankings, and public tech-hub tiering

## Key Findings

- New York–London still behaves like a flagship Overture market: huge premium demand, large traffic, and a nearly ideal route profile.
- Boomless Cruise materially changes the model narrative by putting long U.S. domestic routes back on the board. In the bundled fallback run, `JFK-LAX` and `JFK-SFO` now rank in the top 40 instead of scoring near zero.
- The transpacific business corridor remains extremely strong because it combines high-BTI city pairs with very large absolute time savings.
- The dashboard can now filter explicitly by `overwater`, `hybrid`, and `overland` route type to isolate the new Boomless-driven opportunity set.

## Known Limitations

- Bundled fallback mode is not a substitute for full BTS coverage.
- The fallback sample now includes hand-curated U.S. domestic routes to demonstrate Boomless Cruise impact; those sample volumes are directional rather than airline-grade traffic data.
- Eurostat is supported in code but not bundled by default.
- Fare estimates are heuristic, not itinerary-level market fares.
- The overwater model uses coarse public land geometry rather than regulated airspace paths.
- Wind asymmetry is not directional; the model uses average block assumptions.
- International overland Boomless operations are still subject to jurisdiction-specific regulation and are not modeled country-by-country.
- Connecting traffic, schedule banks, alliance feed, curfew rules, and slot constraints are not modeled.
- The current frontend is implemented in source, but final visual QA depends on a local Node toolchain.

## Future Improvements

- Replace bundled traffic sample with full BTS + Eurostat extracts
- Add seasonality and directional wind adjustments
- Distinguish true premium share by market rather than using a global assumption
- Replace the curated domestic fallback sample with a stronger public proxy for U.S. domestic premium corridor traffic
- Add city-pair corporate travel intensity and alliance feed proxies
- Model fleet assignment and aircraft utilization across a network, not just route-by-route
- Add sensitivity analysis for CASM, load factor, and fare capture rate

## References

- ICAO Doc 8991, *Manual on Air Traffic Forecasting*
- IATA World Air Transport Statistics
- BTS T-100 documentation
- Natural Earth vector data
