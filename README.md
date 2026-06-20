# BEAM Weather Station Dashboard 2025

An interactive, browser-based dashboard for exploring microclimate data from 40 weather stations across NUS Kent Ridge Campus and UTown.

**Live dashboard → [beam-nus.github.io/BEAM_dashboard](https://beam-nus.github.io/BEAM_dashboard/)**
**Version: 1.0 (June 2026)**

---

## Overview

This dashboard is part of the **BEAM (Built Environment and Microclimate) project** at the National University of Singapore. It visualises 2025 data collected from a network of ground-level, rooftop, and 3-axis rooftop weather stations distributed across campus.

No installation is required, the dashboard runs entirely in the browser and loads data from the included GEOJSON files.

---

## Features

- **4 measured variables:** Air Temperature · Relative Humidity · Wind Speed · Solar Radiation
- **Time filters:** Annual and monthly views, with All Day / Daytime / Nighttime breakdowns
- **Chart types:** Daily trend lines, monthly bar charts, hourly heatmaps, boxplots, and all-station cross-comparisons
- **Compare mode:** Select up to 3 stations side-by-side, with wind rose diagrams per station
- **Interactive campus map:** Station locations with type labels and hover tooltips (powered by Leaflet)
- **Station types:** Ground (lamp posts, columns, railings), Rooftop, and Rooftop 3-axis

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

All data is stored in the `GEOJSON/` folder:

| File | Contents |
|------|----------|
| `beam_ws_data.json` | Main station data (all variables, all stations) |
| `beam_windrose_data.json` | Wind direction and speed distributions |
| `beam_heatmap_data.json` | Hourly solar radiation data |
| `beam_meta.json` | Station metadata (type, coordinates) |

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

> **Work in progress.** Data covers 2025. Additional features and variables are planned.  
> Feedback and suggestions are welcome — please open an Issue or contact the project team.

---

## Acknowledgements

- **Dashboard development:** Marcel Ignatius (NUS BEAM Project), with AI assistance from [Anthropic Claude](https://www.anthropic.com)
- **GitHub deployment:** Joie Lim (NUS BEAM Digital Twin team)
- **Project:** CoolNUS-BEAM (Baselining - Evaluating - Action - Monitoring), National University of Singapore

---

## License

© National University of Singapore. All rights reserved.  
Data and code are shared for research and educational purposes.
