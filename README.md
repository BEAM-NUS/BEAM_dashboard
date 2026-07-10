# BEAM Weather Station Dashboard 2024–2026

An interactive, browser-based dashboard for exploring microclimate data from 40 weather stations across NUS Kent Ridge Campus and UTown.

**Live dashboard → [beam-nus.github.io/BEAM_dashboard](https://beam-nus.github.io/BEAM_dashboard/)**
**Version: 2.2 (July 2026)** — multi-year: Apr 2024 – Jun 2026 · Wind CFD map · Tree Canopy (SVI/TCM)

---

## Overview

This dashboard is part of the **CoolNUS-BEAM (Baselining - Evaluating - Action - Monitoring) project** at the National University of Singapore. It visualises 2025 data collected from a network of ground-level, rooftop, and 3-axis rooftop weather stations distributed across campus.

No installation is required, the dashboard runs entirely in the browser and loads data from the included GEOJSON files.

---

## Features

- **4 measured variables:** Air Temperature · Relative Humidity · Wind Speed · Solar Radiation
- **Year toggle (2024 / 2025 / 2026):** switch the whole dashboard between years; 2024 covers Apr–Dec, 2026 covers Jan–Jun (months without data are greyed out)
- **Year comparison:** per-station overlay chart with one line per year (monthly averages, or daily values in monthly view)
- **Time filters:** Annual and monthly views, with All Day / Daytime / Nighttime breakdowns
- **Chart types:** Daily trend lines, monthly bar charts, hourly heatmaps, boxplots, and all-station cross-comparisons
- **Compare mode:** Select up to 8 stations side-by-side, with wind rose diagrams per station
- **Interactive campus map:** Station locations with type labels and hover tooltips (powered by Leaflet)
- **Station types:** Ground (lamp posts, columns, railings), Rooftop, and Rooftop 3-axis
- **Data QC:** hourly wind readings above 8 m/s (physically implausible — faulty sensor) are removed at build time; affected station-years (e.g. WS17 wind, 2026: 72% removed) show a warning banner

- **Greenery network (Ta):** multi-year (Mar 2024 – May 2026); 12 stations in 2024 growing to 24 in 2025; follows the year toggle
- **Sensor specifications:** ℹ button in the map legend opens the full sensor spec table (models, ranges, accuracies)
- **Wind Map (CFD):** CLIMATIC MAP panel toggle — full-width pedestrian-level wind speed at 1.5 m height (12 m CFD grid), colour overlay + graduated direction arrows, per-cell hover tooltip
- **Tree Canopy (SVI/TCM):** per-station street-view panorama with Real/Segmented/Blended toggle, SVI pixel-composition donut, Sky View Factor, annual sun-path shade overlay, hour × month canopy transmittance heatmap, and shade-by-hour/month charts; network overview and Compare-mode support. Modeled from one panorama per station (Apr 2024 / Jan 2025 campaigns — capture date shown on each card); 4 stations flagged excluded for sensor/model faults

Note: the home weather radial is 2025-only and labeled as such. Greenery daytime values use the same 07–19h definition as WS data (the original 2025 greenery file used 07–18h, so its day/night means shift by ~0.1 °C).

---

## Station Coverage

| Area | Count |
|------|-------|
| Kent Ridge Campus | 34 |
| UTown | 6 |
| **Total** | **40** |

Station types: Ground · Roof · Roof-3axis

---

## Data Files

All data is stored in the `GEOJSON/` folder, per year (`<year>` = 2024, 2025, 2026):

| File | Contents |
|------|----------|
| `beam_ws_data_<year>.json` | Monthly + daily station data (all variables, all stations) |
| `beam_windrose_data_<year>.json` | Wind direction and speed distributions |
| `beam_heatmap_data_<year>.json` | Hour × month and hour × day heatmap matrices |
| `beam_greenery_data_<year>.json` | Greenery network Air Temp (monthly, daily, hour × month) |
| `beam_meta_years.json` | Global heatmap color ranges, per-year data coverage, QC flags |
| `wind_overlay.png` / `wind_grid.bin` / `wind_meta.json` | Wind CFD layer: colour overlay, packed per-cell speeds/directions, grid metadata (built with `tools/build_wind_layer.py`) |

SVI/TCM assets (panoramas, segmentation, shade-model charts and data) are **not in this repo** — they load at runtime from a public S3 bucket (`beam-dashboard-assets`, prefix `svi_tcm/2024-2025/`), with a local `TCM/` folder as offline fallback for development. The bucket needs a CORS policy allowing GET from the dashboard origins.

The default year (2025) loads at startup; other years' heatmap/windrose files are lazy-loaded on first switch. The legacy single-year files (`beam_ws_data.json`, `beam_heatmap_data.json`, `beam_windrose_data.json`, `beam_meta.json`) are no longer referenced by `index.html` and are kept only for reference.

Data files are regenerated from the hourly CSV compilations with `tools/build_yearly_data.py`:

```bash
python3 tools/build_yearly_data.py "<path to Yearly Compilation>" "<path to BEAM_dashboard>"
```

Conventions (verified against the original 2025 build): daytime = 07:00–19:00 inclusive; solar radiation "all-day" values are daytime means; windrose uses 16 direction sectors from 0° and speed bins 0–1 / 1–2 / 2–3 / >3 m/s.

---

## Tech Stack

- [Leaflet.js](https://leafletjs.com/) — interactive campus map
- [Chart.js](https://www.chartjs.org/) — data charts
- [chartjs-chart-boxplot](https://github.com/sgratzl/chartjs-chart-boxplot) — boxplot extension
- Vanilla HTML/CSS/JavaScript — no build step, no framework

---

## Usage

To run locally, clone the repo and open `index.html` with a local server (e.g. VS Code Live Server extension). Direct file:// opening will not work due to browser CORS restrictions on fetch() calls.

```bash
git clone https://github.com/BEAM-NUS/BEAM_dashboard.git
cd BEAM_dashboard
# Open with Live Server in VS Code, or any local HTTP server
```

To update the dashboard, replace `index.html` with the new version and push to `main`. GitHub Pages redeploys automatically.

---

## Status

> **Work in progress.** Data covers Apr 2024 – Jun 2026. Additional features and variables are planned.  
> Feedback and suggestions are welcome — please open an Issue or contact the project team.

---

## Acknowledgements

- **Dashboard development:** Marcel Ignatius (Co_PI CoolNUS-BEAM), with AI assistance from [Anthropic Claude](https://www.anthropic.com)
- **Wind CFD simulation:** Daniel HII Jun Chung & Takamasa HASAMA, Kajima Technical Research Institute Singapore (KaTRIS)
- **GitHub deployment:** Joie Lim (Research Assistant, Digital Twin)
- **Project:** CoolNUS-BEAM (Baselining - Evaluating - Action - Monitoring), National University of Singapore
- **CoolNUS-BEAM** is funded by the National University of Singapore through the Campus Sustainability initiative and supported by the University Campus Infrastructure (UCI) and the Office of the Deputy President – Research & Technology.
---

## License

© National University of Singapore. All rights reserved.  
Data and code are shared for research and educational purposes.
