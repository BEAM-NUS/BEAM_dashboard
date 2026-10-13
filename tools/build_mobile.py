import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src, 'rb').read().decode('utf-8')
assert s.count('\r\n') > 3000, 'expected CRLF file'
NL = '\r\n'
def crlf(t): return t.replace('\r\n','\n').replace('\n', NL)
def sub1(old, new, count=1):
    global s
    old, new = crlf(old), crlf(new)
    assert s.count(old) == count, f'expected {count} of {old[:70]!r}, got {s.count(old)}'
    s = s.replace(old, new)

# ── 1. viewport + head bootstrap ────────────────────────────────────────────
sub1('<meta name="viewport" content="width=device-width,initial-scale=1.0">', '''<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<meta name="theme-color" content="#a1bb22">
<script>
/* Mobile-lite mode: sets html.m-port (phone portrait) or html.m-land (phone landscape).
   Override for desktop testing: mobile.html?m=port  or  ?m=land */
(function(){
  var f=new URLSearchParams(location.search).get('m');
  var mq=function(q){return window.matchMedia(q).matches;};
  function apply(){
    var port,land;
    if(f==='port'){port=true;land=false;}
    else if(f==='land'){port=false;land=true;}
    else{
      land=mq('(orientation:landscape) and (max-height:500px)');
      port=!land&&mq('(orientation:portrait) and (max-width:600px)');
    }
    var de=document.documentElement;
    de.classList.toggle('m-port',port);
    de.classList.toggle('m-land',land);
    de.classList.toggle('m-lite',port||land);
    window.__mLite=port||land;
  }
  apply();
  window.addEventListener('resize',apply);
  window.addEventListener('orientationchange',apply);
})();
</script>''')
sub1('<title>BEAM Weather Station Dashboard', '<title>[MOBILE PROTOTYPE] BEAM Weather Station Dashboard')

# ── 2. CSS ──────────────────────────────────────────────────────────────────
CSS = crlf('''
/* ═══════════ MOBILE LITE (prototype) ═══════════
   html.m-lite = phone; html.m-port = portrait (stacked); html.m-land = landscape (side by side) */
html.m-lite{-webkit-text-size-adjust:100%;text-size-adjust:100%;}
html.m-lite body{height:100vh;height:100dvh;}
html.m-lite button,html.m-lite select{touch-action:manipulation;}

/* header: one compact row */
html.m-lite header{padding:6px max(12px,env(safe-area-inset-right)) 6px max(12px,env(safe-area-inset-left));gap:10px;}
html.m-lite .beam-logo,html.m-lite .beam-logo svg{height:32px;}
html.m-lite .beam-logo img{height:32px!important;}
html.m-lite .hdiv,html.m-lite .beam-expand,html.m-lite .hsub{display:none;}
html.m-lite .htitle{font-size:13px;line-height:1.2;min-width:0;}
html.m-lite header button{margin-left:auto!important;white-space:nowrap;min-height:36px;}

/* control bar: one swipeable row, 16px select (stops iOS focus-zoom) */
html.m-lite .top-bar{padding:6px max(12px,env(safe-area-inset-right)) 6px max(12px,env(safe-area-inset-left));gap:8px;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;scrollbar-width:none;}
html.m-lite .top-bar::-webkit-scrollbar{display:none;}
html.m-lite .top-bar>*{flex:0 0 auto;}
html.m-lite .top-bar button,html.m-lite .top-bar select{min-height:44px;font-size:13px;padding:0 14px;}
html.m-lite .top-bar select{font-size:16px;margin-left:0;}
/* phone scope: Temp | Humidity | Wind | Solar. Hidden: labels, separators, Compare, Home, Canopy, Overall. */
html.m-lite .top-bar .sep,html.m-lite .top-bar>span,html.m-lite #compareBtn,html.m-lite .home-btn,html.m-lite .var-btn[data-var="Canopy"],html.m-lite .var-btn[data-var="Overall"]{display:none;}

/* grid children must be allowed to shrink */
html.m-lite .map-panel,html.m-lite .right-panel,html.m-lite #homeView{min-height:0;min-width:0;}
html.m-lite .panel-hdr{padding:5px 12px;}
html.m-lite .right-panel{padding:10px;padding-bottom:calc(10px + env(safe-area-inset-bottom));-webkit-overflow-scrolling:touch;overscroll-behavior:contain;}
html.m-lite #homeView img{max-height:none!important;width:100%!important;height:auto;}

/* PORTRAIT: map on top, detail below */
html.m-port .layout{grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,48%) minmax(0,1fr);}
html.m-port .map-panel{border-right:0;border-bottom:1px solid var(--border);}

/* LANDSCAPE: map left, detail right; save every vertical pixel */
html.m-land .layout{grid-template-columns:minmax(0,46%) minmax(0,1fr);padding-left:env(safe-area-inset-left);padding-right:env(safe-area-inset-right);}
html.m-land header{padding-top:3px;padding-bottom:3px;}
html.m-land .beam-logo,html.m-land .beam-logo svg,html.m-land .beam-logo img{height:26px!important;}
html.m-land .top-bar{padding-top:3px;padding-bottom:3px;}
html.m-land .top-bar button,html.m-land .top-bar select{min-height:38px;}
html.m-lite .panel-hdr{display:none;}

/* map stays clean: no zoom buttons (pinch works); Layers + Legend live in a strip UNDER the map */
html.m-lite .leaflet-control-zoom{display:none;}
.m-mapbar{display:none;}
html.m-lite .m-mapbar{display:flex;gap:8px;flex:0 0 auto;position:relative;padding:6px 10px;background:#fff;border-top:1px solid var(--border);}
.m-mapbar button{flex:1;min-height:40px;border-radius:20px;border:2px solid var(--navy);background:#fff;color:var(--navy);font-size:13px;font-weight:700;cursor:pointer;}
.m-mapbar button.on{background:var(--navy);color:#fff;}
.m-mapbar button{padding:0;display:flex;align-items:center;justify-content:center;}
.m-mapbar button svg{width:24px;height:24px;display:block;pointer-events:none;}
html.m-land .m-mapbar{padding:4px 10px;}
html.m-land .m-mapbar button{min-height:34px;}
/* panels open over the DETAIL pane (below the strip in portrait, to the right in landscape) so the whole map stays visible while toggling */
.m-panel{display:none;position:absolute;z-index:1500;background:#fff;border-radius:12px;box-shadow:0 4px 18px rgba(0,0,0,.3);padding:8px 12px;overflow-y:auto;-webkit-overflow-scrolling:touch;}
.m-panel.open{display:block;}
html.m-port .m-panel{top:calc(100% + 6px);left:10px;right:10px;max-height:calc((100dvh - 105px)*.5 - 14px);}
html.m-land .m-panel{left:calc(100% + 8px);bottom:0;width:calc(54vw - 20px);max-height:calc(100dvh - 130px);}
/* two columns, filled top to bottom: 4 on the left, 3 on the right */
html.m-lite .m-panel .leaflet-control-layers-overlays{display:grid;grid-auto-flow:column;grid-template-rows:repeat(4,auto);grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:10px;}
html.m-port .m-panel .leaflet-control-layers label{font-size:13px;}
html.m-lite .m-panel .leaflet-control-layers label>span{display:flex;align-items:center;gap:6px;white-space:nowrap;}
html.m-port .m-panel .leaflet-control-layers-selector{width:18px;height:18px;}
@media (max-width:380px){html.m-port .m-panel{padding:8px 8px;}html.m-port .m-panel .leaflet-control-layers label{font-size:12px;}html.m-lite .m-panel .leaflet-control-layers label>span{gap:4px;white-space:normal;line-height:1.15;}html.m-port .m-panel .leaflet-control-layers-overlays{column-gap:4px;}}
html.m-land .m-panel .leaflet-control-layers label{min-height:36px;font-size:14px;}
/* big-map mode (default until a station is picked): map takes most of the screen; panels open over the map, above the strip */
html.m-port.m-bigmap .layout{grid-template-rows:minmax(0,76%) minmax(0,1fr);}
html.m-land.m-bigmap .layout{grid-template-columns:minmax(0,62%) minmax(0,1fr);}
html.m-port.m-bigmap .m-panel{top:auto;bottom:calc(100% + 6px);max-height:calc((100dvh - 105px)*.55);}
html.m-land.m-bigmap .m-panel{left:8px;right:8px;width:auto;top:auto;bottom:calc(100% + 6px);max-height:calc(100dvh - 160px);}
html.m-lite .m-panel .leaflet-control-layers{border:0!important;background:none!important;box-shadow:none!important;}
/* Leaflet layers control, re-parented into its panel */
html.m-lite .m-panel .leaflet-control{float:none;clear:none;margin:0;box-shadow:none;border-radius:0;background:transparent;width:auto;}
html.m-lite .m-panel .leaflet-control-layers>div{display:none;}
html.m-lite .m-panel .leaflet-control-layers-expanded{padding:0!important;width:auto;max-height:none;}
html.m-lite .m-panel .leaflet-control-layers label{margin:0;min-height:40px;font-size:15px;align-items:center;gap:10px;}
html.m-lite .m-panel .leaflet-control-layers-selector{width:22px;height:22px;margin:0;}
/* legend, re-parented into its panel: 2 columns */
html.m-lite .m-panel .map-legend{background:transparent;box-shadow:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;font-size:13px;line-height:1.3;}
html.m-lite .m-panel .map-legend>b{grid-column:1/-1;font-size:13px!important;}
html.m-lite .m-panel .map-legend button{grid-column:1/-1;min-height:40px;font-size:13px!important;margin-top:4px!important;}

/* heatmaps on phones: one per row, colour bar under the plot */
html.m-lite #hmContainer{grid-template-columns:minmax(0,1fr)!important;}
html.m-lite .hm-card{min-width:0;}

/* month picker: grid of 3-letter buttons instead of the native dropdown */
.m-monthbtn{display:none;}
html.m-lite #monthSel{display:none;}
html.m-lite .top-bar .m-monthbtn{display:flex;align-items:center;justify-content:center;gap:8px;order:2;border:2px solid var(--navy);background:#fff;color:var(--navy);font-weight:700;font-size:15px;border-radius:22px;}
html.m-lite .m-monthbtn::after{content:"";width:7px;height:7px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg) translateY(-2px);}
html.m-lite .top-bar .m-monthbtn[aria-expanded="true"]{background:var(--navy);color:#fff;}
html.m-port .top-bar .m-monthbtn{flex:1 1 0;min-width:0;}
html.m-land .top-bar .m-monthbtn{flex:0 0 auto;min-width:110px;}
.m-pop{display:none;position:fixed;z-index:3000;background:#fff;border-radius:14px;box-shadow:0 6px 24px rgba(0,0,0,.35);padding:10px;box-sizing:border-box;}
.m-pop.open{display:block;}
.m-pop-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;}
.m-pop button{min-height:46px;border-radius:12px;border:2px solid var(--border);background:#fff;color:var(--navy);font-size:15px;font-weight:700;cursor:pointer;touch-action:manipulation;}
.m-pop button.sel{background:var(--navy);border-color:var(--navy);color:#fff;}
.m-pop button:disabled{opacity:.3;}
.m-pop .m-pop-all{grid-column:1/-1;}
/* sensor specification modal on phones: card scrolls, table scrolls sideways if needed, bigger close button */
html.m-lite #specModal>div{width:calc(100% - 20px)!important;max-height:calc(100dvh - 20px)!important;padding:12px 8px!important;box-sizing:border-box;-webkit-overflow-scrolling:touch;}
html.m-lite #specModal table{width:100%;table-layout:auto;font-size:clamp(9px,2.5vw,10.5px)!important;line-height:1.25;}
html.m-lite #specModal th,html.m-lite #specModal td{padding:4px 2px!important;}
html.m-lite #specModal>div>div:first-child button{min-width:44px;min-height:44px;font-size:22px!important;}
html.m-land .m-pop-grid{grid-template-columns:repeat(6,minmax(0,1fr));}
html.m-land .m-pop button{min-height:38px;}
/* one-line pointer to the desktop version, at the foot of the detail pane */
html.m-lite .right-panel::after{content:"More features on desktop: Compare, Tree Canopy, Wind CFD";display:block;text-align:center;font-size:12px;line-height:1.4;color:var(--muted);padding:14px 8px 6px;}
html.m-lite .hm-card canvas{max-width:100%;height:auto!important;}
html.m-lite .right-panel{scrollbar-gutter:stable;}
html.m-lite .hm-body{flex-direction:column;gap:2px;}
html.m-lite .hm-colorbar{width:100%;display:block;}
html.m-lite .hm-colorbar>div{display:none;}
html.m-lite .hm-colorbar canvas{display:block;}
/* welcome modal on phones: fits the screen, scrolls inside, button always reachable */
.w-lite{display:none;}
html.m-lite .w-full{display:none;}
html.m-lite .w-lite{display:block;}
html.m-lite #welcomeModal>div{width:calc(100% - 24px)!important;padding:16px 18px!important;max-height:calc(100dvh - 24px - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;-webkit-overflow-scrolling:touch;}
html.m-land #welcomeModal>div{padding:10px 18px!important;}
html.m-lite #welcomeModal .w-actions{position:sticky;bottom:0;background:#fff;padding:10px 0 8px;margin-top:10px!important;}
html.m-lite #welcomeModal .w-actions button{min-height:44px;padding:0 34px!important;font-size:14px!important;}

/* phone variable tabs: portrait row 1 = years + month, row 2 = four chips; landscape = one swipeable row */
html.m-lite .top-bar .m-break{display:none;}
html.m-lite .top-bar .yr-btn{order:1;}
html.m-lite .top-bar select{order:2;}
html.m-lite .top-bar .var-btn{order:4;}
html.m-port .top-bar{flex-wrap:wrap;overflow:visible;row-gap:6px;}
html.m-port .top-bar select{flex:1 1 0;min-width:0;}
html.m-port .top-bar .m-break{display:block;order:3;flex:0 0 100%;height:0;}
html.m-port .top-bar .var-btn{flex:1 1 0;min-width:0;padding:0 4px;white-space:nowrap;}
html.m-land .top-bar .var-btn{flex:0 0 auto;min-width:64px;}
html.m-lite .top-bar .var-btn svg{width:24px;height:24px;display:block;margin:0 auto;pointer-events:none;}
/* detail pane controls and wind rose */
html.m-lite .dn-btn,html.m-lite .comp-view-btn{min-height:36px;padding:0 12px;font-size:12px;}
html.m-lite .toggle-row{gap:8px;}
html.m-lite .chart-card{padding:10px;}
html.m-lite .chart-card>div[style*="display:flex"]{flex-wrap:wrap;}
html.m-lite .wr-compact{flex-direction:column;align-items:center;}
html.m-lite .wr-legend-v{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 14px;width:100%;box-sizing:border-box;font-size:12px;}
html.m-lite .wr-legend-v>div:first-child{flex:0 0 100%;text-align:center;margin-bottom:0!important;}
html.m-lite .wr-legend-v .wr-leg-item{margin-bottom:0;}
''')
i = s.index('</style>'); assert i < s.index('</head>')
s = s[:i] + CSS + s[i:]

# ── 3. strip under the map ──────────────────────────────────────────────────
sub1('    <div id="map"></div>', '''    <div id="map"></div>
    <div class="m-mapbar" id="mMapBar">
      <div class="m-panel" id="mLayersPanel"></div>
      <div class="m-panel" id="mLegendPanel"></div>
      <button type="button" id="mLayersBtn" aria-label="Layers" title="Layers"><svg viewBox="40 0 1120 1190" fill="currentColor" aria-hidden="true"><polygon points="600,27 1118,293 600,560 82,293" stroke="currentColor" stroke-width="26" stroke-linejoin="round"/><path d="M290 497L80 600L600 855L1120 600L910 497M290 805L80 907L600 1162L1120 907L910 805" fill="none" stroke="currentColor" stroke-width="50" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <button type="button" id="mLegendBtn" aria-label="Legend" title="Legend"><svg viewBox="50 180 1120 830" fill="currentColor" aria-hidden="true"><polygon points="178,218 80,392 276,392" stroke="currentColor" stroke-width="30" stroke-linejoin="round"/><rect x="68" y="476" width="226" height="226" rx="22"/><circle cx="184" cy="871" r="120"/><path d="M428 304H1130M428 589H1130M428 872H1130" fill="none" stroke="currentColor" stroke-width="44" stroke-linecap="round"/></svg></button>
      <button type="button" id="mInfoBtn" aria-label="Sensor specifications" title="Sensor specifications" onclick="showSpecModal()"><svg viewBox="0 0 1200 1200" fill="currentColor" aria-hidden="true"><circle cx="600" cy="600" r="530" fill="none" stroke="currentColor" stroke-width="70"/><circle cx="600" cy="363" r="110"/><path d="M485 530H651a32 32 0 0 1 32 32V820H714a32 32 0 0 1 32 32V914a32 32 0 0 1-32 32H485a32 32 0 0 1-32-32V852a32 32 0 0 1 32-32H517V654H485a32 32 0 0 1-32-32V562a32 32 0 0 1 32-32Z"/></svg></button>
      <button type="button" id="mSizeBtn" aria-label="Bigger map" title="Bigger map" aria-pressed="true"><svg viewBox="40 90 1100 1020" fill="none" stroke="currentColor" stroke-width="75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M112 600V225a75 75 0 0 1 75-75H1012a75 75 0 0 1 75 75V975a75 75 0 0 1-75 75H562"/><rect x="112" y="712" width="338" height="338"/><path d="M637 337H862V562M562 600L862 337"/></svg></button>
    </div>''')

# month trigger button (the native <select> stays in the DOM, hidden on phones, and still drives the dashboard)
sub1('<select class="month-select" id="monthSel">', '<button type="button" id="mMonthBtn" class="m-monthbtn" aria-haspopup="true" aria-expanded="false">Annual</button>' + NL + '  <select class="month-select" id="monthSel">')
# keep the trigger label right when the dashboard resets the month (e.g. switching to a year without that month)
sub1("if(sel.selectedOptions[0]?.disabled){ sel.value='0'; }", "if(sel.selectedOptions[0]?.disabled){ sel.value='0'; }" + NL + "  if(window.__mMonthSync) window.__mMonthSync();")

# row break so the variable chips wrap onto their own row in portrait
sub1('<option value="12">December</option>' + NL + '  </select>', '<option value="12">December</option>' + NL + '  </select>' + NL + '  <div class="m-break"></div>')

# wind rose: sharp on retina, bigger labels, fills the card; hook so it can be redrawn on rotation
sub1("""  const W=canvas.width,H=canvas.height;
  ctx.clearRect(0,0,W,H);
  const cx=W/2,cy=H/2,maxR=Math.min(W,H)/2-22;""", """  const __d=window.__mLite?Math.min(window.devicePixelRatio||1,3):1, __fs=window.__mLite?1.3:1;
  const W=canvas.width/__d,H=canvas.height/__d;
  ctx.setTransform(__d,0,0,__d,0,0);
  ctx.clearRect(0,0,W,H);
  const cx=W/2,cy=H/2,maxR=Math.min(W,H)/2-(window.__mLite?30:22);""")
sub1("ctx.font='8px Segoe UI';ctx.textAlign='center';", "ctx.font=`${8*__fs}px Segoe UI`;ctx.textAlign='center';")
sub1("ctx.font=`${isC?'bold ':''} ${isC?10:8}px Segoe UI`;", "ctx.font=`${isC?'bold ':''} ${(isC?10:8)*__fs}px Segoe UI`;")
sub1("""  requestAnimationFrame(()=>{
    const cardW=document.getElementById('wrCompact').offsetWidth;
    const sz=Math.min(Math.max(cardW-140,192),312);
    const canvas=document.getElementById('wr_canvas');
    canvas.width=sz; canvas.height=sz;
    const wrData=getWrData();
    if(wrData)drawWindRose('wr_canvas',wrData);
  });""", """  const __drawWr=()=>{
    const box=document.getElementById('wrCompact'), canvas=document.getElementById('wr_canvas');
    if(!box||!canvas) return;
    const cardW=box.offsetWidth;
    if(window.__mLite){
      const rp=document.getElementById('rightPanel'), cap=document.documentElement.classList.contains('m-land')?Math.max(200,rp.clientHeight-40):320;
      const sz=Math.max(180,Math.min(cardW-8,cap)), d=Math.min(window.devicePixelRatio||1,3);
      canvas.style.width=sz+'px'; canvas.style.height=sz+'px';
      canvas.width=Math.round(sz*d); canvas.height=Math.round(sz*d);
    } else {
      const sz=Math.min(Math.max(cardW-140,192),312);
      canvas.width=sz; canvas.height=sz;
    }
    const wrData=getWrData();
    if(wrData)drawWindRose('wr_canvas',wrData);
  };
  window.__wrRedraw=window.__mLite?__drawWr:null;
  requestAnimationFrame(__drawWr);""")

# ── 3c. welcome modal: phone-specific quick start (the desktop list mentions Compare / other variables) ──
sub1('<ul style="margin:0 0 10px;padding-left:20px">', '<ul class="w-full" style="margin:0 0 10px;padding-left:20px">')
sub1("""measuring air temperature near vegetation</li>
      </ul>""", """measuring air temperature near vegetation</li>
      </ul>
      <ul class="w-lite" style="margin:0 0 10px;padding-left:20px">
        <li><b>Tap any station</b> on the map to see its charts through the year</li>
        <li>Use the <b>year buttons</b> (2024 / 2025 / 2026) and the month menu to change the period. 2024 starts in April, 2026 runs to June</li>
        <li>Use the <b>layers</b> (stacked sheets) and <b>legend</b> (list) icons under the map; the <b>i</b> icon shows the sensor specifications. Green circles (G01-G25) are <b>greenery stations</b> (air temperature only)</li>
        <li>Switch variable with the icon tabs in the top bar: <b>thermometer</b> (temperature), <b>drop</b> (humidity), <b>wind</b> (with a wind rose) and <b>sun</b> (solar). The <b>Heatmap</b> button shows all four by hour and month. The corner icon under the map makes the map bigger or smaller. Compare and the tree canopy views are on the desktop version</li>
      </ul>""")
sub1('<div style="text-align:center;margin-top:16px">' + NL + '      <button type="button" onclick="closeWelcomeModal()"', '<div class="w-actions" style="text-align:center;margin-top:16px">' + NL + '      <button type="button" onclick="closeWelcomeModal()"')

# ── 3d. heatmaps on phones: hour labels 1-24, wider plot, horizontal colour bar, sharp canvases ──
sub1("function drawHeatmapNew(canvasId, data2d, cmap, yLabels, hmRange, cbId, unit, cbTicks, startHour=0, endHour=23, aspect=0.8){",
     "function drawHeatmapNew(canvasId, data2d, cmap, yLabels, hmRange, cbId, unit, cbTicks, startHour=0, endHour=23, aspect=(window.__mLite?0.6:0.8)){")
sub1("  const ctx=canvas.getContext('2d');\n  // Clip to requested hour range",
     "  const ctx=canvas.getContext('2d');\n  canvas._hmArgs=[canvasId,data2d,cmap,yLabels,hmRange,cbId,unit,cbTicks,startHour,endHour,aspect];\n  // Clip to requested hour range")
sub1("  const PL=38, PB=36, PT=6, PR=6;", "  const PL=(window.__mLite?30:38), PB=36, PT=6, PR=6;")
sub1("  canvas.width=W; canvas.height=H;\n  ctx.clearRect(0,0,W,H);",
     "  if(window.__mLite){ const dpr=Math.min(window.devicePixelRatio||1,3); canvas.width=Math.round(W*dpr); canvas.height=Math.round(H*dpr); canvas.style.width=W+'px'; canvas.style.height=H+'px'; ctx.setTransform(dpr,0,0,dpr,0,0); }\n  else{ canvas.width=W; canvas.height=H; }\n  ctx.clearRect(0,0,W,H);")
sub1("  const xStep=(plotW/nCols)>=44?1:2;",
     "  const xStep=window.__mLite?((plotW/nCols)>=11?1:2):((plotW/nCols)>=44?1:2);\n  if(window.__mLite) ctx.font='10px sans-serif';")
sub1("    ctx.fillText(`${String(hr).padStart(2,'0')}:00`, PL+c*cellW+cellW/2, PT+plotH+14);",
     "    ctx.fillText(window.__mLite?String(hr):`${String(hr).padStart(2,'0')}:00`, PL+c*cellW+cellW/2, PT+plotH+14);")
sub1("  const cb=document.getElementById(cbId);\n  if(cb){",
     "  const cb=document.getElementById(cbId);\n  if(cb && window.__mLite){ __hmColorbarH(cb,cmap,cbTicks,mn,mx,PL,plotW,W); }\n  else if(cb){")
sub1("  ctx.fillText('Hour of Day', PL+plotW/2, PT+plotH+28);",
     "  ctx.fillText(window.__mLite ? 'Hour of day (0 to 23)' : 'Hour of Day', PL+plotW/2, PT+plotH+28);")

# ── 3b. CARTO basemap API key (required for raster tiles since 25 Sep 2026) ──
# Public client-side key, restricted by nothing. Skipped automatically once index.html carries a key itself.
CARTO_KEY = 'cb1_4hpq_1_0a4e81905447dea960020e42'
if 'basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?key=' not in s:
    sub1("L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{",
         "L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?key=" + CARTO_KEY + "',{")
    sub1("attribution:'\u00a9 OpenStreetMap \u00a9 CARTO'",
         "attribution:'&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors, &copy; <a href=\"https://carto.com/attribution/\">CARTO</a>'")

# ── 4. layers: on phones only the hotspot zones start on; the rest load when first ticked ──
sub1('''  Promise.all(layerDefs.map(def =>
    fetch(def.file).then(r => r.json()).then(data => ({ def, data }))
  )).then(results => {
    results.forEach(({def, data}, i) => {
      const layer = L.geoJSON(data, {
        style: def.style,
        onEachFeature: def.onEachFeature
      }).addTo(mapInstance);  // all on by default
      geojsonLayers[def.name] = layer;
      overlayControl[def.name] = layer;
    });''', '''  Promise.all(layerDefs.map(def => {
    // phone: only Hotspot Zones loads at startup; the other layers fetch when first ticked
    if(window.__mLite && !def.file.includes('Hotspots')) return Promise.resolve({ def, data: null });
    return fetch(def.file).then(r => r.json()).then(data => ({ def, data }));
  })).then(results => {
    results.forEach(({def, data}, i) => {
      const layer = L.geoJSON(data, {
        style: def.style,
        onEachFeature: def.onEachFeature
      });
      if(data){ layer.addTo(mapInstance); }  // desktop: all on by default
      else{
        let started = false;
        layer.on('add', () => {
          if(started) return; started = true;
          fetch(def.file).then(r => r.json()).then(d => layer.addData(d))
            .catch(e => { started = false; console.warn('Layer load failed', def.name, e); });
        });
      }
      geojsonLayers[def.name] = layer;
      overlayControl[def.name] = layer;
    });''')

# phone: drop the '(Ta)' suffix so the label fits a half-width column (display text only)
sub1("} Greenery Stations (Ta)`] = greeneryLayer;", "} Greenery Stations`] = greeneryLayer;")

# phone: the Specifications button moves out of the legend into its own icon button under the map
_n = len(re.findall(r'<button type="button" onclick="showSpecModal\(\)"[^\n]*?Specifications</button>', s))
assert _n == 1, _n
s = re.sub(r'<button type="button" onclick="showSpecModal\(\)"[^\n]*?Specifications</button>', '', s)

# layers control -> panel under the map; hide the wind (CFD) control for now
sub1('const climCtl=L.control.layers(', "if(window.__mLite){ const lp=document.getElementById('mLayersPanel'); if(lp) lp.appendChild(layersCtl.getContainer()); }" + NL + '    const climCtl=L.control.layers(')
sub1('climCtl.getContainer().insertAdjacentHTML(', "if(window.__mLite) climCtl.getContainer().style.display='none';" + NL + '    climCtl.getContainer().insertAdjacentHTML(')
# legend -> panel under the map
sub1('leg.addTo(mapInstance);', "leg.addTo(mapInstance);" + NL + "  if(window.__mLite){ const gp=document.getElementById('mLegendPanel'); if(gp) gp.appendChild(leg.getContainer()); }")

# ── 5. end-of-body helpers ──────────────────────────────────────────────────
TAIL = crlf('''<script>
/* mobile-lite helpers */
(function(){
  var el=document.getElementById('map');
  if(window.ResizeObserver&&el){
    new ResizeObserver(function(){
      if(typeof mapInstance!=='undefined'&&mapInstance)mapInstance.invalidateSize();
    }).observe(el);
  }
  window.__hmColorbarH=function(cb,cmap,cbTicks,mn,mx,PL,plotW,W){
    var dpr=Math.min(window.devicePixelRatio||1,3),H=34,top=2,barH=10;
    cb.width=Math.round(W*dpr);cb.height=Math.round(H*dpr);cb.style.width=W+'px';cb.style.height=H+'px';
    var c=cb.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,W,H);
    var g=c.createLinearGradient(PL,0,PL+plotW,0);
    cmap.forEach(function(col,i){g.addColorStop(i/(cmap.length-1),col);});
    c.fillStyle=g;c.fillRect(PL,top,plotW,barH);
    c.strokeStyle='#d1d5db';c.lineWidth=.5;c.strokeRect(PL,top,plotW,barH);
    var ticks=(cbTicks&&cbTicks.length)?cbTicks:[mn,mn+(mx-mn)*.25,mn+(mx-mn)*.5,mn+(mx-mn)*.75,mx];
    c.font='10px sans-serif';c.fillStyle='#374151';c.strokeStyle='#9ca3af';c.lineWidth=1;
    ticks.forEach(function(v,i){
      var tt=Math.max(0,Math.min(1,(v-mn)/(mx-mn))),x=PL+tt*plotW;
      c.beginPath();c.moveTo(x,top+barH);c.lineTo(x,top+barH+4);c.stroke();
      c.textAlign=i===0?'left':(i===ticks.length-1?'right':'center');
      c.fillText(Number.isInteger(v)?String(v):v.toFixed(1),x,top+barH+15);
    });
  };
  (function(){
    var rp=document.getElementById('rightPanel'),lastW=0,tm=null;
    function redraw(){
      document.querySelectorAll('canvas').forEach(function(c){
        if(c._hmArgs&&c.isConnected){try{drawHeatmapNew.apply(null,c._hmArgs);}catch(e){console.warn('heatmap redraw failed',e);}}
      });
      if(window.__wrRedraw&&document.getElementById('wr_canvas')){try{window.__wrRedraw();}catch(e){console.warn('wind rose redraw failed',e);}}
    }
    if(window.ResizeObserver&&rp){
      new ResizeObserver(function(){
        var w=Math.round(rp.clientWidth);
        if(!w||w===lastW)return;
        lastW=w;clearTimeout(tm);tm=setTimeout(redraw,120);
      }).observe(rp);
    }
  })();
  var lb=document.getElementById('mLayersBtn'),gb=document.getElementById('mLegendBtn');
  var lp=document.getElementById('mLayersPanel'),gp=document.getElementById('mLegendPanel');
  var cur=null;
  function show(w){
    cur=w;
    lb.classList.toggle('on',w==='layers'); lp.classList.toggle('open',w==='layers');
    gb.classList.toggle('on',w==='legend'); gp.classList.toggle('open',w==='legend');
  }
  lb.addEventListener('click',function(){show(cur==='layers'?null:'layers');});
  gb.addEventListener('click',function(){show(cur==='legend'?null:'legend');});
  el.addEventListener('click',function(){if(cur)show(null);},true);   // tap the map to close
  /* big map until a station is picked; the Bigger/Smaller button toggles it */
  var de=document.documentElement,sb=document.getElementById('mSizeBtn');
  function setBig(on){de.classList.toggle('m-bigmap',on);sb.classList.toggle('on',on);sb.setAttribute('aria-pressed',on?'true':'false');}
  if(window.__mLite){
    setBig(true);
    sb.addEventListener('click',function(){show(null);setBig(!de.classList.contains('m-bigmap'));});
    /* month picker popover */
    (function(){
      var sel=document.getElementById('monthSel'),btn=document.getElementById('mMonthBtn');
      if(!sel||!btn)return;
      var MS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var pop=document.createElement('div');pop.className='m-pop';pop.id='mMonthPop';
      var h='<div class="m-pop-grid"><button type="button" class="m-pop-all" data-m="0">Annual view</button>';
      MS.forEach(function(n,i){h+='<button type="button" data-m="'+(i+1)+'">'+n+'</button>';});
      pop.innerHTML=h+'</div>';document.body.appendChild(pop);
      function label(){var v=+sel.value;btn.textContent=v?MS[v-1]:'Annual';}
      function mark(){pop.querySelectorAll('button').forEach(function(b){var m=+b.dataset.m,o=sel.options[m];b.classList.toggle('sel',m===+sel.value);b.disabled=!!(o&&o.disabled);});}
      function close(){pop.classList.remove('open');btn.setAttribute('aria-expanded','false');}
      function open(){
        show(null);label();mark();
        var r=document.querySelector('.top-bar').getBoundingClientRect();
        pop.style.top=(r.bottom+6)+'px';
        if(de.classList.contains('m-land')){pop.style.left='10px';pop.style.right='auto';pop.style.width=Math.min(600,innerWidth-20)+'px';}
        else{pop.style.left='10px';pop.style.right='10px';pop.style.width='auto';}
        pop.classList.add('open');btn.setAttribute('aria-expanded','true');
      }
      btn.addEventListener('click',function(){pop.classList.contains('open')?close():open();});
      pop.addEventListener('click',function(e){
        var b=e.target.closest('button');if(!b||b.disabled)return;
        sel.value=b.dataset.m;sel.dispatchEvent(new Event('change',{bubbles:true}));label();close();
      });
      document.addEventListener('click',function(e){if(pop.classList.contains('open')&&!pop.contains(e.target)&&!btn.contains(e.target))close();},true);
      window.addEventListener('resize',close);
      window.__mMonthSync=label;label();
    })();
    var rp2=document.getElementById('rightPanel');
    if(window.MutationObserver&&rp2){
      new MutationObserver(function(){
        if(!de.classList.contains('m-bigmap')||!rp2.querySelector('#mainContent,.sel-bar'))return;
        setBig(false);
        setTimeout(function(){try{
          var id=(typeof activeGreenery!=='undefined'&&activeGreenery)||activeStation;
          var m=(typeof grMarkers!=='undefined'&&grMarkers[id])||markers[id];
          if(m)mapInstance.panTo(m.getLatLng(),{animate:true});
        }catch(e){}},350);
      }).observe(rp2,{childList:true});
    }
  }
  if(window.__mLite){
    var h=document.querySelector('.panel-hdr');
    if(h)h.textContent='\\uD83D\\uDCCD Tap a station';
    var IC='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">';
    var VI={
      AirTemp:['Temperature',IC+'<path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0z"/></svg>'],
      RelHum:['Humidity',IC+'<path d="M12 3s-6.5 7-6.5 11.5a6.5 6.5 0 0 0 13 0C18.5 10 12 3 12 3z"/></svg>'],
      Wind:['Wind',IC+'<path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/></svg>'],
      GlobalRad:['Solar radiation',IC+'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>']
    };
    document.querySelectorAll('.var-btn').forEach(function(b){var v=VI[b.dataset.var];if(v){b.innerHTML=v[1];b.setAttribute('aria-label',v[0]);b.title=v[0];}});
    var ns=document.querySelector('.no-sel div:last-child');
    if(ns)ns.textContent='Tap any marker to explore weather data.';
  }
})();
</script>
</body>''')
j = s.rindex('</body>')
s = s[:j] + TAIL + s[j+len('</body>'):]

open(dst, 'wb').write(s.encode('utf-8'))
print('wrote', dst, len(s), 'chars')
