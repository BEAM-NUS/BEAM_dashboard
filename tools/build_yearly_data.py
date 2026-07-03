#!/usr/bin/env python3
"""
Build per-year dashboard JSONs from BEAM hourly CSV compilations.

Input : <SRC>/<period folder>/Full data compiled by WS/Hourly/WSxx(...)_*.csv
Output: GEOJSON/beam_ws_data_<year>.json       (monthly + daily means)
        GEOJSON/beam_heatmap_data_<year>.json  (hour x month, hour x day matrices)
        GEOJSON/beam_windrose_data_<year>.json (16 dir x 4 speed-bin counts)
        GEOJSON/beam_meta_years.json           (global heatmap ranges + coverage)

Conventions (reverse-engineered from the original 2025 files and verified
by exact diff against them):
  - Daytime  = hours 07..19 inclusive; night = the rest.
  - GlobalRad "all-day" value is defined as the DAYTIME mean (night ~0 would
    otherwise halve it).
  - ws_data values rounded to 2 dp; heatmap values to 1 dp.
  - Windrose: direction sector i = [i*22.5, (i+1)*22.5) deg, speed bins
    [0-1, 1-2, 2-3, >3] m/s, no calm exclusion.
  - monthly_heat matrices padded to 31 day-columns with null.
  - Missing hours are simply absent from the averages; months with no data
    are omitted (dashboard renders gaps).

Usage: python3 build_yearly_data.py <src_root> <dashboard_root>
"""
import csv, json, os, re, sys, math
from collections import defaultdict

DAY_HOURS = set(range(7, 20))          # 07:00-19:00 inclusive
VARS = {                                # JSON key -> CSV column
    'AirTemp':   'AirTemp Ave (C)',
    'RelHum':    'RelHum Ave (%)',
    'WindSpeed': 'WindSpeed Ave (m/s)',
    'GlobalRad': 'GlobalRad Ave (W/m2)',
}
SPEED_EDGES = [1.0, 2.0, 3.0]
N_DIR = 16
# QC: hourly-mean wind speeds above this are physically implausible for these
# campus stations (WS17's 2026 sensor gets stuck at 16.3 m/s for days).
# Readings above it are dropped (WindSpeed AND WindDir) before any averaging.
PLAUSIBLE_WS_MAX = 8.0

PERIODS = {  # folder -> year
    '202404 - 202412': 2024,
    '202501 - 202512': 2025,
    '202601 - 202606': 2026,
}


def fnum(s):
    try:
        v = float(s)
        return v if not math.isnan(v) else None
    except (TypeError, ValueError):
        return None


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def r(v, nd):
    return round(v, nd) if v is not None else None


def agg_record(rows, nd=2):
    """rows: list of (hour, {var: val}) -> {Var, Var_d, Var_n}"""
    out = {}
    for var in VARS:
        allv = [d[var] for _, d in rows]
        dv = [d[var] for h, d in rows if h in DAY_HOURS]
        nv = [d[var] for h, d in rows if h not in DAY_HOURS]
        a = mean(dv) if var == 'GlobalRad' else mean(allv)
        out[var] = r(a, nd)
        out[var + '_d'] = r(mean(dv), nd)
        out[var + '_n'] = r(mean(nv), nd)
    return out


def days_in_month(year, m):
    if m == 2:
        return 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
    return 29 if m == 2 else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]


def process_station(path, year):
    """Parse one CSV; return per-structure aggregates."""
    by_day = defaultdict(list)                     # 'YYYY-MM-DD' -> [(hour, vals)]
    by_month = defaultdict(list)                   # month int -> [(hour, vals)]
    hm_month = defaultdict(lambda: defaultdict(dict))   # m -> var -> (hour, day) -> [vals]
    cells = defaultdict(lambda: defaultdict(list)) # var -> (hour, month) -> vals ; -> annual heat
    mcells = defaultdict(lambda: defaultdict(list))# var -> (month, hour, day) -> vals
    wr = {k: defaultdict(lambda: [[0] * 4 for _ in range(N_DIR)])
          for k in ('a', 'd', 'n')}                # month(0=annual handled later) counts
    n_rows = 0
    n_ws_dropped = 0
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            dt = row['Datetime']
            if not dt or int(dt[:4]) != year:
                continue
            m, day, hour = int(dt[5:7]), int(dt[8:10]), int(dt[11:13])
            vals = {var: fnum(row[col]) for var, col in VARS.items()}
            n_rows += 1
            dr = fnum(row['WindDir Ave (degrees)'])
            if vals['WindSpeed'] is not None and vals['WindSpeed'] > PLAUSIBLE_WS_MAX:
                vals['WindSpeed'] = None   # faulty reading — drop speed and direction
                dr = None
                n_ws_dropped += 1
            key_rows = (hour, vals)
            by_day[dt[:10]].append(key_rows)
            by_month[m].append(key_rows)
            for var, v in vals.items():
                if v is not None:
                    cells[var][(hour, m)].append(v)
                    mcells[var][(m, hour, day)].append(v)
            sp = vals['WindSpeed']
            if sp is not None and dr is not None:
                di = int((dr % 360) // 22.5) % N_DIR
                si = sum(1 for e in SPEED_EDGES if sp >= e)
                dn = 'd' if hour in DAY_HOURS else 'n'
                wr['a'][m][di][si] += 1
                wr[dn][m][di][si] += 1
    return by_day, by_month, cells, mcells, wr, n_rows, n_ws_dropped


def build_year(src_hourly, year, stations_meta):
    ws_monthly, ws_daily = {}, {}
    annual_heat, monthly_heat = {}, {}
    wr_out = {f'wr_annual{s}': {} for s in ('', '_d', '_n')}
    wr_out.update({f'wr_monthly{s}': {} for s in ('', '_d', '_n')})
    coverage = {}
    qc = {}
    files = sorted(f for f in os.listdir(src_hourly) if f.endswith('.csv') and f.startswith('WS'))
    for fn in files:
        sid = 'WS' + re.match(r'WS(\d+)', fn).group(1)
        by_day, by_month, cells, mcells, wr, n_rows, n_ws_dropped = process_station(
            os.path.join(src_hourly, fn), year)
        if not n_rows:
            continue
        ws_monthly[sid] = {str(m): agg_record(rows) for m, rows in sorted(by_month.items())}
        ws_daily[sid] = {d: agg_record(rows) for d, rows in sorted(by_day.items())}
        # annual heatmap: 24 x 12, a/d/n (d/n = same values masked to their hours)
        ah = {}
        for var in VARS:
            grid = [[r(mean(cells[var].get((h, m), [])), 1) for m in range(1, 13)]
                    for h in range(24)]
            ah[var] = {
                'a': grid,
                'd': [[grid[h][m] if h in DAY_HOURS else None for m in range(12)] for h in range(24)],
                'n': [[None if h in DAY_HOURS else grid[h][m] for m in range(12)] for h in range(24)],
            }
        annual_heat[sid] = ah
        # monthly heatmap: month -> var -> 24 x 31 (padded with null)
        mh = {}
        for m in sorted(by_month):
            mh[str(m)] = {}
            for var in VARS:
                nd_ = days_in_month(year, m)
                grid = [[r(mean(mcells[var].get((m, h, d), [])), 1)
                         for d in range(1, nd_ + 1)] + [None] * (31 - nd_)
                        for h in range(24)]
                mh[str(m)][var] = grid
        monthly_heat[sid] = mh
        # windrose
        for dn, suf in (('a', ''), ('d', '_d'), ('n', '_n')):
            ann = [[0] * 4 for _ in range(N_DIR)]
            for m, mat in wr[dn].items():
                for i in range(N_DIR):
                    for j in range(4):
                        ann[i][j] += mat[i][j]
            wr_out[f'wr_annual{suf}'][sid] = ann
            wr_out[f'wr_monthly{suf}'][sid] = {str(m): wr[dn][m] for m in sorted(wr[dn])}
        exp = sum(days_in_month(year, m) for m in by_month) * 24
        coverage[sid] = {'months': sorted(by_month), 'hours': n_rows,
                         'completeness': round(n_rows / exp, 3) if exp else 0}
        if n_rows and n_ws_dropped / n_rows > 0.01:
            qc[sid] = {'WindSpeed': round(n_ws_dropped / n_rows, 3)}
    ws = {'stations': stations_meta, 'monthly': ws_monthly, 'daily': ws_daily}
    hm = {'annual_heat': annual_heat, 'monthly_heat': monthly_heat}
    return ws, hm, wr_out, coverage, qc


GREENERY_CSV = os.path.join('SOURCE DATA', 'GREENERY LOCATIONS',
                            'greenery_NUSws_hourly_202403_202605_revised.csv')

def build_greenery(dash, geo, years):
    """Per-year greenery JSONs from the wide multi-year CSV.
    Columns 'WSn_<name>' map to station Gnn (G13 absent). Dates are M/D/YYYY.
    Daytime unified to 07-19h inclusive (the original 2025 greenery file used
    7-18h; WS data and all dashboard labels use 7-19h)."""
    stations = json.load(open(os.path.join(geo, 'beam_greenery_data.json')))['stations']
    rows = list(csv.reader(open(os.path.join(dash, GREENERY_CSV))))
    colmap = {}
    for i, h in enumerate(rows[0]):
        mm = re.match(r'WS(\d+)_', h or '')
        if mm:
            gid = f'G{int(mm.group(1)):02d}'
            if gid in stations:
                colmap[i] = gid
    # per-year accumulators: year -> gid -> ...
    acc = {y: defaultdict(lambda: {'day': defaultdict(list), 'cell': defaultdict(list)}) for y in years}
    for r in rows[1:]:
        if not r[0]:
            continue
        try:
            dpart, tpart = r[0].split(' ')
            mth, day, yr = map(int, dpart.split('/'))
            hour = int(tpart.split(':')[0])
        except ValueError:
            continue
        if yr not in acc:
            continue
        for ci, gid in colmap.items():
            v = fnum(r[ci]) if ci < len(r) else None
            if v is None:
                continue
            a = acc[yr][gid]
            a['day'][f'{yr}-{mth:02d}-{day:02d}'].append((hour, v))
            a['cell'][(hour, mth)].append(v)
    heat_all = []
    out_by_year = {}
    for y in years:
        monthly, daily, heat = {}, {}, {}
        for gid, a in sorted(acc[y].items()):
            by_month = defaultdict(list)
            dd = {}
            for date, hv in sorted(a['day'].items()):
                m = int(date[5:7])
                by_month[m].extend(hv)
                dd[date] = grec(hv)
            daily[gid] = dd
            monthly[gid] = {str(m): grec(hv) for m, hv in sorted(by_month.items())}
            grid = [[r(mean(a['cell'].get((h, m), [])), 1) for m in range(1, 13)]
                    for h in range(24)]
            heat[gid] = grid
            heat_all.extend(v for row in grid for v in row if v is not None)
        out_by_year[y] = {'stations': stations, 'monthly': monthly, 'daily': daily, 'heat': heat}
    rng = {'min': round(min(heat_all), 1), 'max': round(max(heat_all), 1)}
    for y, obj in out_by_year.items():
        obj['heat_range'] = rng
        p = os.path.join(geo, f'beam_greenery_data_{y}.json')
        json.dump(obj, open(p, 'w'), separators=(',', ':'))
        print(f'  {os.path.basename(p)}: {os.path.getsize(p)/1e6:.2f} MB, '
              f'{len(obj["monthly"])} stations')
    print('  greenery heat_range:', rng)

def grec(hv):
    allv = [v for _, v in hv]
    dv = [v for h, v in hv if h in DAY_HOURS]
    nv = [v for h, v in hv if h not in DAY_HOURS]
    return {'AirTemp': r(mean(allv), 2), 'AirTemp_d': r(mean(dv), 2), 'AirTemp_n': r(mean(nv), 2)}

def main():
    src_root, dash = sys.argv[1], sys.argv[2]
    geo = os.path.join(dash, 'GEOJSON')
    stations_meta = json.load(open(os.path.join(geo, 'beam_ws_data.json')))['stations']
    meta = {'years': [], 'coverage': {}, 'hm_ranges': {}, 'qc_flags': {}}
    allvals = {v: [] for v in VARS}
    for folder, year in PERIODS.items():
        src = os.path.join(src_root, folder, 'Full data compiled by WS', 'Hourly')
        print(f'== {year} ({folder})')
        ws, hm, wr, cov, qc = build_year(src, year, stations_meta)
        if qc:
            meta['qc_flags'][str(year)] = qc
            print(f'  ! wind readings >{PLAUSIBLE_WS_MAX} m/s removed: {qc}')
        for sid, ah in hm['annual_heat'].items():
            for var in VARS:
                allvals[var].extend(v for row in ah[var]['a'] for v in row if v is not None)
        for name, obj in (('ws_data', ws), ('heatmap_data', hm), ('windrose_data', wr)):
            p = os.path.join(geo, f'beam_{name}_{year}.json')
            json.dump(obj, open(p, 'w'), separators=(',', ':'))
            print(f'  {os.path.basename(p)}: {os.path.getsize(p)/1e6:.2f} MB')
        meta['years'].append(year)
        meta['coverage'][year] = cov
        low = [s for s, c in cov.items() if c['completeness'] < 0.9]
        if low:
            print(f'  ! completeness <90%: {low}')
    # Color ranges: raw min/max, but WindSpeed screened at 8 m/s so a faulty
    # sensor (e.g. WS17 wind, 2026, stuck at 16.3 m/s) doesn't flatten every
    # heatmap. Faulty station-years are listed in meta['qc_flags'].
    PLAUSIBLE_WS_MAX = 8.0
    meta['hm_ranges'] = {}
    for v, vals in allvals.items():
        if v == 'WindSpeed':
            vals = [x for x in vals if x <= PLAUSIBLE_WS_MAX]
        meta['hm_ranges'][v] = {'min': round(min(vals), 1), 'max': round(max(vals), 1)}
    json.dump(meta, open(os.path.join(geo, 'beam_meta_years.json'), 'w'), separators=(',', ':'))
    print('meta:', meta['hm_ranges'])
    print('== greenery')
    build_greenery(dash, geo, list(PERIODS.values()))


if __name__ == '__main__':
    main()
