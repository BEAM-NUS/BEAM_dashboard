#!/usr/bin/env python3
"""
Build wind GIS layer assets for the BEAM dashboard.

Inputs (SOURCE DATA/WIND_RAW/):
  windraster/   Esri binary grid, float32 wind speed (m/s) at 1.5 m, EPSG:4326
  winddata3.shp CFD point grid (112,574 pts) with Umag (m/s) + Dir2D
                (meteorological "wind from" direction, deg clockwise from N)

Outputs (GEOJSON/):
  wind_overlay.png  colored classified overlay (transparent NoData)
  wind_grid.bin     Uint16 LE: [speed mm/s ...] then [dir tenths-deg ...],
                    65535 = NoData, row-major from NW corner
  wind_meta.json    bounds, grid size, encoding, snapshot info

CFD snapshot: 2 July 2024, 2 PM. Wind speed at 1.5 m height (pedestrian level).
"""
import json, struct, sys
import numpy as np
import rasterio, shapefile
from rasterio.transform import rowcol
from PIL import Image

SRC = "SOURCE DATA/WIND_RAW"
OUT = "GEOJSON"

# ── raster ────────────────────────────────────────────────────────────────
src = rasterio.open(f"{SRC}/windraster")
nx, ny = src.width, src.height
rast = src.read(1, masked=True)
b = src.bounds
print(f"raster {nx}x{ny}  bounds {b}")

# ── grid the points ───────────────────────────────────────────────────────
r = shapefile.Reader(f"{SRC}/winddata3")
fields = [f[0] for f in r.fields[1:]]
iU, iD = fields.index("Umag"), fields.index("Dir2D")

speed = np.full((ny, nx), np.nan, np.float32)
dirn  = np.full((ny, nx), np.nan, np.float32)
coll = out = 0
for sr in r.iterShapeRecords():
    x, y = sr.shape.points[0]
    row, col = rowcol(src.transform, x, y)
    if not (0 <= row < ny and 0 <= col < nx):
        out += 1; continue
    if not np.isnan(speed[row, col]): coll += 1
    speed[row, col] = sr.record[iU]
    dirn[row, col]  = sr.record[iD] % 360.0
n_pts = len(r)
n_fill = int(np.isfinite(speed).sum())
print(f"points {n_pts}  gridded {n_fill}  collisions {coll}  outside {out}")

# consistency: point Umag vs raster value on shared cells
both = np.isfinite(speed) & ~rast.mask
diff = np.abs(speed[both] - rast.data[both])
print(f"cells with both point+raster: {both.sum()}  |Umag-raster| max {diff.max():.4f}  mean {diff.mean():.4f}")

# ── colored PNG (match ArcGIS legend: 6 classes, blue→red, >0.5 red) ─────
BOUNDS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
COLORS = ["#4575b4", "#91bfdb", "#e0f3f8", "#fee090", "#fc8d59", "#d73027"]
def hex2rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
rgba = np.zeros((ny, nx, 4), np.uint8)
valid = np.isfinite(speed)
cls = np.digitize(speed, BOUNDS[1:] + [np.inf])  # 0..5
for k, c in enumerate(COLORS):
    m = valid & (cls == k)
    rgba[m, :3] = hex2rgb(c)
rgba[valid, 3] = 255
Image.fromarray(rgba).save(f"{OUT}/wind_overlay.png", optimize=True)

# ── binary lookup grid ────────────────────────────────────────────────────
NOD = 65535
sp = np.where(valid, np.clip(np.round(speed * 1000), 0, 65534), NOD).astype("<u2")
dr = np.where(valid, np.clip(np.round(dirn * 10) % 3600, 0, 3599), NOD).astype("<u2")
with open(f"{OUT}/wind_grid.bin", "wb") as f:
    f.write(sp.tobytes()); f.write(dr.tobytes())

# ── meta ──────────────────────────────────────────────────────────────────
meta = {
    "west": b.left, "south": b.bottom, "east": b.right, "north": b.top,
    "nx": nx, "ny": ny,
    "encoding": {"order": "speed_then_dir", "type": "uint16le",
                 "speed_scale": 0.001, "dir_scale": 0.1, "nodata": 65535,
                 "dir_convention": "meteorological_from_north_cw"},
    "classes": {"bounds_ms": BOUNDS, "colors": COLORS},
    "snapshot": "2 July 2024, 2 PM", "height": "1.5 m",
    "source": "CFD simulation, 12 m grid", "units": "m/s"
}
json.dump(meta, open(f"{OUT}/wind_meta.json", "w"), indent=1)
print("wrote wind_overlay.png, wind_grid.bin, wind_meta.json")
