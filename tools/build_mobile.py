import sys
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
html.m-port .layout{grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,44%) minmax(0,1fr);}
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
html.m-land .m-mapbar{padding:4px 10px;}
html.m-land .m-mapbar button{min-height:34px;}
/* panels open over the DETAIL pane (below the strip in portrait, to the right in landscape) so the whole map stays visible while toggling */
.m-panel{display:none;position:absolute;z-index:1500;background:#fff;border-radius:12px;box-shadow:0 4px 18px rgba(0,0,0,.3);padding:8px 12px;overflow-y:auto;-webkit-overflow-scrolling:touch;}
.m-panel.open{display:block;}
html.m-port .m-panel{top:calc(100% + 6px);left:10px;right:10px;max-height:calc((100dvh - 105px)*.56 - 14px);}
html.m-land .m-panel{left:calc(100% + 8px);bottom:0;width:calc(54vw - 20px);max-height:calc(100dvh - 130px);}
html.m-land .m-panel .leaflet-control-layers-overlays{display:grid;grid-template-columns:1fr 1fr;column-gap:8px;}
html.m-land .m-panel .leaflet-control-layers label{min-height:36px;font-size:14px;}
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
html.m-land .top-bar .var-btn{flex:0 0 auto;}
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
      <button type="button" id="mLayersBtn">&#x1F5C2; Layers</button>
      <button type="button" id="mLegendBtn">&#x2139; Legend</button>
    </div>''')

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
        <li>Open <b>Layers</b> and <b>Legend</b> under the map. Green circles (G01-G25) are <b>greenery stations</b> (air temperature only)</li>
        <li>Switch between <b>Temp, Humidity, Wind</b> (with a wind rose) and <b>Solar</b> with the tabs in the top bar. The <b>Heatmap</b> button shows all four by hour and month. Compare and the tree canopy views are on the desktop version</li>
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
  if(window.__mLite){
    var h=document.querySelector('.panel-hdr');
    if(h)h.textContent='\\uD83D\\uDCCD Tap a station';
    var VL={AirTemp:'\\uD83C\\uDF21 Temp',RelHum:'\\uD83D\\uDCA7 Humidity',Wind:'\\uD83C\\uDF2C Wind',GlobalRad:'\\u2600 Solar'};
    document.querySelectorAll('.var-btn').forEach(function(b){if(VL[b.dataset.var])b.textContent=VL[b.dataset.var];});
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
