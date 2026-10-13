"""Phone-sized WebP copies of the canopy-tab images (used by mobile.html only).

Output (gitignored, uploaded to S3 next to the originals):
  TCM/m/<WSxx>/{real,segmented,blended,sunpath_rgb,sunpath_tcm}.webp
  GREENERY_TCM/m/<GSxx>/{segmented,sunpath_rgb,sunpath_tcm}.webp

Notes: WS "real" photos come from the export (dashboard_export/svi), never from the local TCM/svi copies.
Greenery real/blended photos are not produced for the phone (the phone shows Segmented, RGB and TCM sun paths).

Run:  python3 tools/make_phone_images.py "<path to Tree Shade Mapper>"
"""
import sys, os, json
from PIL import Image

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tsm = sys.argv[1]
EXP = os.path.join(tsm, 'dashboard_export')
GEXP = os.path.join(tsm, 'greenery_export')
PHOTO_W, SUN_W, Q = 1400, 1800, 80

def save(src, dst, width):
    if not os.path.exists(src):
        return False
    im = Image.open(src).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, 'WEBP', quality=Q, method=6)
    return True

stats = {}
def tally(k, ok):
    stats.setdefault(k, [0, 0]); stats[k][0 if ok else 1] += 1

svi = json.load(open(os.path.join(repo, 'TCM', 'svi_manifest.json')))
for sid in sorted(k for k in svi if not k.startswith('_')):
    out = os.path.join(repo, 'TCM', 'm', sid)
    tally('WS real', save(f'{EXP}/svi/{sid}.jpg', f'{out}/real.webp', PHOTO_W))
    tally('WS segmented', save(f'{EXP}/segmentation/{sid}/{sid}_segmented.png', f'{out}/segmented.webp', PHOTO_W))
    tally('WS blended', save(f'{EXP}/segmentation/{sid}/{sid}_blended.png', f'{out}/blended.webp', PHOTO_W))
    ch = os.path.join(repo, 'TCM', 'tcm_charts', sid)
    if os.path.isdir(ch):
        tally('WS sunpath rgb', save(f'{ch}/sunpath_v4_rgb.png', f'{out}/sunpath_rgb.webp', SUN_W))
        tally('WS sunpath tcm', save(f'{ch}/sunpath_v4_tcm.png', f'{out}/sunpath_tcm.webp', SUN_W))

gm = json.load(open(os.path.join(repo, 'GREENERY_TCM', 'manifest.json')))
for sid in sorted(k for k in gm if k.startswith('GS')):
    out = os.path.join(repo, 'GREENERY_TCM', 'm', sid)
    tally('GS segmented', save(f'{GEXP}/segmentation/{sid}/segmented.png', f'{out}/segmented.webp', PHOTO_W))
    tally('GS sunpath tcm', save(f'{repo}/GREENERY_TCM/tcm_charts/{sid}/sunpath_v4_tcm.png', f'{out}/sunpath_tcm.webp', SUN_W))
    tally('GS sunpath rgb', save(f'{repo}/GREENERY_TCM/tcm_charts/{sid}/sunpath_v4_rgb.png', f'{out}/sunpath_rgb.webp', SUN_W))

for k, (ok, miss) in stats.items():
    print(f'{k:16s} made {ok:3d}  missing {miss}')
tot = 0
for base in ('TCM/m', 'GREENERY_TCM/m'):
    for r, _, fs in os.walk(os.path.join(repo, base)):
        tot += sum(os.path.getsize(os.path.join(r, f)) for f in fs)
print('total MB', round(tot / 1e6, 1))
