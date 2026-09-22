#!/usr/bin/env python3
"""
build_dashboard.py — MV Maker Signal Scan
Reads signals.json, writes a self-contained HTML dashboard.

Usage:  python3 build_dashboard.py signals.json index.html
"""
import json, sys, html, datetime

SRC = sys.argv[1] if len(sys.argv) > 1 else "signals.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "index.html"

d = json.load(open(SRC, encoding="utf-8"))

# ---------------------------------------------------------------- validators
VOCAB = set(d["episteme_vocab"].keys())
SECTORS = set(d["sectors"])
LIK = ["actual", "probable", "plausible", "possible", "preposterous"]
TLS = ["0-2", "3-6", "7-10"]

errs, ids = [], set()
for s in d["signals"]:
    if s["id"] in ids:
        errs.append(f"duplicate id: {s['id']}")
    ids.add(s["id"])
    if s["sector"] not in SECTORS:
        errs.append(f"{s['id']}: unknown sector {s['sector']!r}")
    if s["likelihood"] not in LIK:
        errs.append(f"{s['id']}: unknown likelihood {s['likelihood']!r}")
    if s["timeline"] not in TLS:
        errs.append(f"{s['id']}: unknown timeline {s['timeline']!r}")
    if s["horizon"] not in (1, 2, 3):
        errs.append(f"{s['id']}: bad horizon {s['horizon']!r}")
    ep = s.get("episteme") or []
    if not (2 <= len(ep) <= 4):
        errs.append(f"{s['id']}: episteme must hold 2-4 tags, has {len(ep)}")
    for t in ep:
        if t not in VOCAB:
            errs.append(f"{s['id']}: episteme tag not in vocabulary: {t!r}")
    for f in ("title", "summary", "so_what", "source_name", "source_url"):
        if not s.get(f):
            errs.append(f"{s['id']}: empty required field {f}")

urls = {}
for s in d["signals"]:
    urls.setdefault(s["source_url"], []).append(s["id"])
for u, who in urls.items():
    if len(who) > 1:
        errs.append(f"duplicate source_url shared by {who}")

for grp, key in (("opportunities", "evidence"), ("threats", "evidence"),
                 ("critical_uncertainties", "signals")):
    for item in d.get(grp, []):
        for sid in item.get(key, []):
            if sid not in ids:
                errs.append(f"{grp}/{item['id']}: unknown signal id {sid}")

if len(d.get("opportunities", [])) != 3:
    errs.append(f"expected 3 opportunities, found {len(d.get('opportunities', []))}")
if len(d.get("threats", [])) != 3:
    errs.append(f"expected 3 threats, found {len(d.get('threats', []))}")
if len(d.get("critical_uncertainties", [])) < 2:
    errs.append("fewer than 2 critical uncertainties")

if errs:
    print("BUILD FAILED — schema errors:")
    for e in errs:
        print("  -", e)
    sys.exit(1)

payload = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
gen = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

TPL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MV Maker Signal Scan</title>
<style>
:root{
  color-scheme:light;
  --surface-1:#fcfcfb; --page:#f9f9f7; --raise:#ffffff;
  --ink-1:#0b0b0b; --ink-2:#52514e; --ink-3:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
  --lik-1:#86b6ef; --lik-2:#3987e5; --lik-3:#256abf; --lik-4:#184f95; --lik-5:#0d366b;
  --seq-1:#cde2fb; --seq-2:#9ec5f4; --seq-3:#6da7ec; --seq-4:#3987e5; --seq-5:#256abf; --seq-6:#184f95; --seq-7:#0d366b;
  --accent:#1c5cab; --wash:rgba(28,92,171,.07);
  --opp:#0f6d43; --opp-wash:rgba(15,109,67,.08);
  --thr:#a33227; --thr-wash:rgba(163,50,39,.07);
  --cu:#6b4d0f; --cu-wash:rgba(107,77,15,.08);
}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){
  color-scheme:dark;
  --surface-1:#1a1a19; --page:#0d0d0d; --raise:#212120;
  --ink-1:#fff; --ink-2:#c3c2b7; --ink-3:#898781;
  --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
  --lik-1:#184f95; --lik-2:#256abf; --lik-3:#3987e5; --lik-4:#6da7ec; --lik-5:#9ec5f4;
  --seq-1:#0d366b; --seq-2:#104281; --seq-3:#184f95; --seq-4:#256abf; --seq-5:#3987e5; --seq-6:#6da7ec; --seq-7:#9ec5f4;
  --accent:#6da7ec; --wash:rgba(109,167,236,.13);
  --opp:#4cc98a; --opp-wash:rgba(76,201,138,.11);
  --thr:#f08a7d; --thr-wash:rgba(240,138,125,.11);
  --cu:#e0b95c; --cu-wash:rgba(224,185,92,.11);
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --surface-1:#1a1a19; --page:#0d0d0d; --raise:#212120;
  --ink-1:#fff; --ink-2:#c3c2b7; --ink-3:#898781;
  --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
  --lik-1:#184f95; --lik-2:#256abf; --lik-3:#3987e5; --lik-4:#6da7ec; --lik-5:#9ec5f4;
  --seq-1:#0d366b; --seq-2:#104281; --seq-3:#184f95; --seq-4:#256abf; --seq-5:#3987e5; --seq-6:#6da7ec; --seq-7:#9ec5f4;
  --accent:#6da7ec; --wash:rgba(109,167,236,.13);
  --opp:#4cc98a; --opp-wash:rgba(76,201,138,.11);
  --thr:#f08a7d; --thr-wash:rgba(240,138,125,.11);
  --cu:#e0b95c; --cu-wash:rgba(224,185,92,.11);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--page);color:var(--ink-1);
 font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1260px;margin:0 auto;padding:0 20px 90px}
a{color:var(--accent)}

.headrow{position:relative;padding-top:26px}
.themetoggle{position:absolute;top:0;right:0;background:var(--surface-1);color:var(--ink-2);
 border:1px solid var(--border);border-radius:8px;padding:6px 11px;font:inherit;font-size:12.5px;cursor:pointer}
.themetoggle:hover{background:var(--wash);color:var(--ink-1)}
header.top{padding:34px 0 20px;border-bottom:1px solid var(--border);margin-bottom:20px}
.eyebrow{font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3);font-weight:650}
h1{font-size:clamp(26px,3.3vw,37px);line-height:1.13;margin:9px 0 8px;letter-spacing:-.016em}
.sub{color:var(--ink-2);max-width:78ch;margin:0 0 10px}
.stamp{font-size:12.5px;color:var(--ink-3)}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(142px,1fr));gap:11px;margin:20px 0 26px}
.tile{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;padding:13px 15px}
.tile .v{font-size:29px;font-weight:650;letter-spacing:-.02em;line-height:1.05}
.tile .k{font-size:11.5px;color:var(--ink-2);margin-top:3px}

h2.sec{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);
 font-weight:700;margin:30px 0 12px;padding-bottom:7px;border-bottom:1px solid var(--border)}

.otgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:920px){.otgrid{grid-template-columns:1fr}}
.stack{display:flex;flex-direction:column;gap:11px}
.ot{background:var(--surface-1);border:1px solid var(--border);border-left:3px solid var(--accent);
 border-radius:10px;padding:14px 16px}
.ot.op{border-left-color:var(--opp)} .ot.th{border-left-color:var(--thr)}
.ot .lab{font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;font-weight:750}
.ot.op .lab{color:var(--opp)} .ot.th .lab{color:var(--thr)}
.ot h3{font-size:16px;margin:5px 0 7px;line-height:1.3;letter-spacing:-.01em}
.ot p{margin:0 0 9px;font-size:13.5px;color:var(--ink-2);line-height:1.5}
.ot p.claim{color:var(--ink-1)}
.ot .meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:11.5px;color:var(--ink-3);margin-bottom:6px}
.pill{border:1px solid var(--border);border-radius:999px;padding:2px 9px;font-size:11px;color:var(--ink-2)}
.ot.op .pill.hi{background:var(--opp-wash);border-color:transparent;color:var(--opp);font-weight:650}
.ot.th .pill.hi{background:var(--thr-wash);border-color:transparent;color:var(--thr);font-weight:650}
details.more{margin-top:4px}
details.more>summary{cursor:pointer;font-size:12.5px;color:var(--accent);list-style:none;padding:3px 0}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::before{content:"▸ ";font-size:10px}
details.more[open]>summary::before{content:"▾ "}
.sub-h{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);font-weight:700;margin:10px 0 4px}
ul.tight{margin:4px 0 0;padding-left:17px}
ul.tight li{font-size:13px;color:var(--ink-2);margin-bottom:4px}
.evlinks{display:flex;flex-wrap:wrap;gap:5px;margin-top:5px}
.evlinks button{border:1px solid var(--border);background:transparent;color:var(--ink-2);border-radius:6px;
 padding:2px 7px;font:inherit;font-size:11px;cursor:pointer;text-align:left;max-width:100%;
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.evlinks button:hover{background:var(--wash);color:var(--ink-1)}

.cu{background:var(--surface-1);border:1px solid var(--border);border-left:3px solid var(--cu);
 border-radius:10px;padding:14px 16px;margin-bottom:11px}
.cu .lab{font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;font-weight:750;color:var(--cu)}
.cu h3{font-size:16.5px;margin:5px 0 7px;line-height:1.3}
.poles{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:9px 0 0}
@media(max-width:700px){.poles{grid-template-columns:1fr}}
.pole{background:var(--cu-wash);border-radius:8px;padding:9px 11px}
.pole b{display:block;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--cu);margin-bottom:3px}
.pole span{font-size:12.5px;color:var(--ink-2);line-height:1.45}

.charts{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,.85fr) minmax(0,.95fr);gap:15px;margin-bottom:24px}
@media(max-width:1000px){.charts{grid-template-columns:1fr}}
.panel{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;padding:15px 17px 17px}
.panel h3{font-size:13.5px;margin:0 0 3px}
.panel .note{font-size:11.5px;color:var(--ink-3);margin:0 0 13px}
.bars{display:flex;flex-direction:column;gap:6px}
.barrow{display:grid;grid-template-columns:148px 1fr 28px;align-items:center;gap:9px;cursor:pointer;
 border:0;background:none;padding:0;font:inherit;color:inherit;text-align:left}
.barrow .lbl{font-size:11.5px;color:var(--ink-2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bartrack{display:block;height:11px;background:var(--grid);border-radius:3px;overflow:hidden}
.barfill{display:block;height:100%;background:var(--seq-4);border-radius:0 4px 4px 0;transition:width .25s}
.barrow .num{font-size:11.5px;color:var(--ink-2);font-variant-numeric:tabular-nums;text-align:right}
.barrow:hover .lbl,.barrow:hover .num{color:var(--ink-1)}
.barrow[aria-pressed="true"] .lbl{color:var(--ink-1);font-weight:650}
.barrow[aria-pressed="true"] .barfill{background:var(--seq-6)}
table.matrix{border-collapse:separate;border-spacing:2px;width:100%}
table.matrix th{font-size:11px;font-weight:650;color:var(--ink-3);text-align:left;padding:0 2px 4px}
table.matrix th.rowh{font-weight:500;color:var(--ink-2);padding-right:7px;white-space:nowrap;font-size:11.5px}
table.matrix td{padding:0}
.cell{width:100%;min-width:40px;height:32px;border:0;border-radius:4px;cursor:pointer;font:inherit;
 font-size:12px;font-variant-numeric:tabular-nums;font-weight:650;display:flex;align-items:center;justify-content:center}
.legend{display:flex;flex-wrap:wrap;gap:12px;margin-top:11px;font-size:11.5px;color:var(--ink-2);align-items:center}
.legend i{width:11px;height:11px;border-radius:2px;display:inline-block}

.filters{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;padding:13px 15px;
 margin-bottom:16px;position:sticky;top:0;z-index:30}
.frow{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:8px}
.frow:last-child{margin-bottom:0}
.flabel{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);font-weight:700;width:82px;flex:0 0 82px}
.chip{border:1px solid var(--border);background:transparent;color:var(--ink-2);border-radius:999px;
 padding:3.5px 10px;font:inherit;font-size:12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.chip:hover{background:var(--wash);color:var(--ink-1)}
.chip[aria-pressed="true"]{background:var(--wash);border-color:var(--accent);color:var(--ink-1);font-weight:650}
.chip .sw{width:9px;height:9px;border-radius:2px;flex:0 0 9px}
.chip .ct{color:var(--ink-3);font-variant-numeric:tabular-nums;font-size:11px}
input.search{flex:1;min-width:210px;background:var(--page);border:1px solid var(--border);border-radius:8px;
 padding:7px 11px;font:inherit;font-size:13.5px;color:var(--ink-1)}
input.search::placeholder{color:var(--ink-3)}
.ghost{border:1px solid var(--border);background:transparent;color:var(--ink-2);border-radius:8px;
 padding:6px 11px;font:inherit;font-size:12.5px;cursor:pointer}
.ghost:hover{background:var(--wash);color:var(--ink-1)}
.ghost[aria-pressed="true"]{background:var(--wash);color:var(--ink-1);border-color:var(--accent)}
.resultbar{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin:0 0 13px;flex-wrap:wrap}
.resultbar .n{font-size:13px;color:var(--ink-2)}
.resultbar .n b{color:var(--ink-1)}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(358px,1fr));gap:13px}
.card{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;padding:15px 16px;
 display:flex;flex-direction:column;gap:8px;scroll-margin-top:190px}
.card.flash{outline:2px solid var(--accent);outline-offset:2px}
.card .meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:11px;color:var(--ink-3)}
.lbadge{display:inline-flex;align-items:center;gap:5px;color:var(--ink-2);font-weight:650;font-size:11px}
.lbadge .sw{width:10px;height:10px;border-radius:2px}
.dot{color:var(--axis)}
.newtag{background:var(--accent);color:#fff;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:700;letter-spacing:.04em}
.card h3{font-size:15.5px;margin:0;line-height:1.32;letter-spacing:-.008em}
.card p{margin:0;font-size:13.5px;color:var(--ink-2);line-height:1.5}
.card .so{border-left:2px solid var(--accent);padding-left:11px;color:var(--ink-1);font-size:13.5px}
.epis{display:flex;flex-wrap:wrap;gap:4px}
.epis span{border:1px solid var(--border);border-radius:5px;padding:1px 6px;font-size:10.5px;color:var(--ink-2)}
.epis span b{color:var(--accent);font-weight:800;margin-right:3px}
.card .src{font-size:11.5px;color:var(--ink-3);margin-top:auto;padding-top:3px}
.tableview{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;overflow-x:auto}
table.data{border-collapse:collapse;width:100%;font-size:12.5px}
table.data th{text-align:left;font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);
 padding:10px 11px;border-bottom:1px solid var(--border);white-space:nowrap;position:sticky;top:0;background:var(--surface-1)}
table.data td{padding:9px 11px;border-bottom:1px solid var(--grid);color:var(--ink-2);vertical-align:top}
table.data td.tt{color:var(--ink-1);min-width:240px}
.hidden{display:none!important}
.empty{padding:42px 20px;text-align:center;color:var(--ink-2);background:var(--surface-1);
 border:1px solid var(--border);border-radius:12px}
#tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .12s;z-index:200;background:var(--raise);
 color:var(--ink-1);border:1px solid var(--border);border-radius:8px;padding:7px 10px;font-size:12.5px;
 box-shadow:0 6px 20px rgba(0,0,0,.18);max-width:260px}
footer.foot{margin-top:32px;padding-top:17px;border-top:1px solid var(--border);font-size:12.5px;color:var(--ink-3)}
footer.foot p{margin:0 0 7px;max-width:92ch}
footer.foot b{color:var(--ink-2)}
@media print{.filters,.themetoggle,.charts{display:none}.cards{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <div class="headrow">
    <button class="themetoggle" id="tbtn" type="button">Dark mode</button>
    <header class="top">
      <div class="eyebrow" id="eyebrow">Horizon scan</div>
      <h1 id="dtitle">MV Maker Signal Scan</h1>
      <p class="sub" id="dsub"></p>
      <div class="stamp" id="stamp"></div>
    </header>
  </div>

  <div class="tiles" id="tiles"></div>

  <h2 class="sec">Opportunities &amp; threats to the Mount Vernon maker program</h2>
  <div class="otgrid">
    <div class="stack" id="opps"></div>
    <div class="stack" id="threats"></div>
  </div>

  <h2 class="sec">Critical uncertainties</h2>
  <div id="cus"></div>

  <h2 class="sec">The signal field</h2>
  <div class="charts">
    <div class="panel"><h3>Signals by sector</h3><p class="note">Click a bar to filter.</p><div class="bars" id="secbars"></div></div>
    <div class="panel"><h3>EPISTEME(S) coverage</h3><p class="note">Signals carry 2–4 tags, so totals exceed the corpus.</p><div class="bars" id="epibars"></div></div>
    <div class="panel"><h3>Three Horizons &#215; timeline</h3><p class="note">Counts per cell. Click to filter.</p><div id="matrix"></div><div class="legend" id="mlegend"></div></div>
  </div>

  <div class="filters">
    <div class="frow">
      <span class="flabel">Search</span>
      <input class="search" id="q" type="search" placeholder="Search titles, findings, sources&#8230;" autocomplete="off">
      <button class="ghost" id="newonly" type="button" aria-pressed="false">New this scan</button>
      <button class="ghost" id="reset" type="button">Reset</button>
      <button class="ghost" id="viewbtn" type="button" aria-pressed="false">Table view</button>
    </div>
    <div class="frow"><span class="flabel">Sector</span><span id="secchips"></span></div>
    <div class="frow"><span class="flabel">EPISTEME(S)</span><span id="epichips"></span></div>
    <div class="frow"><span class="flabel">Likelihood</span><span id="likchips"></span></div>
    <div class="frow"><span class="flabel">Horizon</span><span id="hzchips"></span><span class="flabel" style="margin-left:14px">Timeline</span><span id="tlchips"></span></div>
  </div>

  <div class="resultbar"><div class="n" id="count"></div><div class="n" id="sortnote">Strongest signals first</div></div>
  <div id="cards" class="cards"></div>
  <div id="tableview" class="tableview hidden"></div>
  <div id="empty" class="empty hidden">No signals match those filters.</div>

  <footer class="foot" id="foot"></footer>
</div>
<div id="tip" role="status" aria-live="polite"></div>

<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
(function(){
var D = JSON.parse(document.getElementById('payload').textContent);
var S = D.signals || [], EPI = D.episteme_vocab || {}, SECT = D.sectors || [];
var OPS = D.opportunities || [], THR = D.threats || [], CUS = D.critical_uncertainties || [];
var LIK = ['actual','probable','plausible','possible','preposterous'];
var LIKV = {actual:'--lik-5',probable:'--lik-4',plausible:'--lik-3',possible:'--lik-2',preposterous:'--lik-1'};
var TLS = ['0-2','3-6','7-10'], TLL = {'0-2':'0–2 yrs','3-6':'3–6 yrs','7-10':'7–10 yrs'};
var HZL = {1:'H1 · Status quo',2:'H2 · Disruptive',3:'H3 · Transformative'};
var SEQ = ['--seq-1','--seq-2','--seq-3','--seq-4','--seq-5','--seq-6','--seq-7'];
var esc = function(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
var el = function(i){return document.getElementById(i);};
var cssv = function(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();};
function inkOn(hex){var h=(hex||'').replace('#','');if(h.length<6)return 'var(--ink-1)';
  var c=[0,2,4].map(function(i){return parseInt(h.substr(i,2),16)/255;}).map(function(v){
    return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);});
  var L=0.2126*c[0]+0.7152*c[1]+0.0722*c[2];
  return ((L+0.05)/0.05)>=(1.05/(L+0.05))?'#0b0b0b':'#ffffff';}
var byId={}; S.forEach(function(s){byId[s.id]=s;});
var isNew=function(s){return s.first_seen===D.last_updated;};

/* ---------- header ---------- */
el('dtitle').textContent = D.dashboard || 'Signal Scan';
el('dsub').textContent = (D.subject||'') + ' — a standing, cumulative horizon scan for ' + (D.owner||'');
el('eyebrow').textContent = 'Horizon scan · scan #' + (D.scan_count||1);
el('stamp').textContent = 'Last refreshed ' + (D.last_updated||'') + ' · ' + S.length +
  ' signals under watch · ' + (D.cadence||'') + ' · memory: ' + (D.memory_model||'cumulative');

/* ---------- tiles ---------- */
var tiles=[[S.length,'Under watch'],[S.filter(isNew).length,'New this scan'],
  [OPS.length,'Opportunities'],[THR.length,'Threats'],[CUS.length,'Critical uncertainties'],
  [S.filter(function(s){return s.horizon===3;}).length,'Horizon 3'],
  [S.filter(function(s){return s.likelihood==='actual';}).length,'Already actual'],
  [S.filter(function(s){return s.timeline==='0-2';}).length,'Landing in 0–2 yrs']];
el('tiles').innerHTML = tiles.map(function(t){
  return '<div class="tile"><div class="v">'+t[0]+'</div><div class="k">'+esc(t[1])+'</div></div>';}).join('');

/* ---------- evidence chips ---------- */
function evBlock(ids){
  if(!ids||!ids.length) return '';
  return '<div class="sub-h">Evidence in the corpus</div><div class="evlinks">'+ids.map(function(id){
    var s=byId[id]; if(!s) return '';
    return '<button type="button" data-goto="'+esc(id)+'">'+esc(s.title)+'</button>';}).join('')+'</div>';
}

/* ---------- opportunities & threats ---------- */
function otCard(x,kind,n){
  var cls = kind==='op'?'op':'th';
  var lab = kind==='op'?('Opportunity '+n):('Threat '+n);
  var grade = kind==='op' ? (x.confidence||'') : (x.severity||'');
  var gradeLabel = kind==='op' ? ('confidence: '+grade) : ('severity: '+grade);
  var extra = kind==='op'
    ? (x.what_it_would_take?'<div class="sub-h">What it would take</div><p>'+esc(x.what_it_would_take)+'</p>':'')
      + (x.cost_shape?'<div class="sub-h">Cost shape</div><p>'+esc(x.cost_shape)+'</p>':'')
    : (x.mechanism?'<div class="sub-h">Mechanism</div><p>'+esc(x.mechanism)+'</p>':'')
      + (x.early_warning&&x.early_warning.length?'<div class="sub-h">Early warning</div><ul class="tight">'+
         x.early_warning.map(function(w){return '<li>'+esc(w)+'</li>';}).join('')+'</ul>':'');
  return '<article class="ot '+cls+'" id="'+esc(x.id)+'">'+
    '<div class="lab">'+esc(lab)+'</div>'+
    '<h3>'+esc(x.title)+'</h3>'+
    '<div class="meta"><span class="pill hi">'+esc(gradeLabel)+'</span>'+
      '<span class="pill">first identified '+esc(x.first_identified||'—')+'</span>'+
      '<span class="pill">last revised '+esc(x.last_revised||'—')+'</span></div>'+
    '<p class="claim">'+esc(x.claim)+'</p>'+
    '<details class="more"><summary>Why now, and what it rests on</summary>'+
      '<div class="sub-h">Why now</div><p>'+esc(x.why_now)+'</p>'+ extra +
      (x.status_note?'<div class="sub-h">Status</div><p>'+esc(x.status_note)+'</p>':'')+
      evBlock(x.evidence)+
    '</details></article>';
}
el('opps').innerHTML = OPS.map(function(x,i){return otCard(x,'op',i+1);}).join('');
el('threats').innerHTML = THR.map(function(x,i){return otCard(x,'th',i+1);}).join('');

/* ---------- critical uncertainties ---------- */
el('cus').innerHTML = CUS.map(function(c,i){
  return '<section class="cu" id="'+esc(c.id)+'">'+
    '<div class="lab">Critical uncertainty '+(i+1)+'</div>'+
    '<h3>'+esc(c.title)+'</h3>'+
    '<p style="margin:0 0 4px;font-size:13.5px;color:var(--ink-2)">'+esc(c.question)+'</p>'+
    '<details class="more"><summary>Why it matters, poles and watch indicators</summary>'+
      '<div class="sub-h">Why it matters</div><p style="font-size:13.5px;color:var(--ink-2);margin:0">'+esc(c.why_it_matters)+'</p>'+
      '<div class="poles"><div class="pole"><b>Pole A</b><span>'+esc(c.pole_a)+'</span></div>'+
      '<div class="pole"><b>Pole B</b><span>'+esc(c.pole_b)+'</span></div></div>'+
      (c.watch&&c.watch.length?'<div class="sub-h">What to watch</div><ul class="tight">'+
        c.watch.map(function(w){return '<li>'+esc(w)+'</li>';}).join('')+'</ul>':'')+
      (c.status_note?'<div class="sub-h">Status</div><p style="font-size:13px;color:var(--ink-2);margin:0">'+esc(c.status_note)+'</p>':'')+
      evBlock(c.signals)+
    '</details></section>';}).join('');

/* ---------- state & filters ---------- */
var st={sec:new Set(),epi:new Set(),lik:new Set(),hz:new Set(),tl:new Set(),q:'',newonly:false,table:false};
function match(s){
  if(st.sec.size&&!st.sec.has(s.sector))return false;
  if(st.lik.size&&!st.lik.has(s.likelihood))return false;
  if(st.hz.size&&!st.hz.has(s.horizon))return false;
  if(st.tl.size&&!st.tl.has(s.timeline))return false;
  if(st.newonly&&!isNew(s))return false;
  if(st.epi.size){var ok=false;(s.episteme||[]).forEach(function(t){if(st.epi.has(t))ok=true;});if(!ok)return false;}
  if(st.q){var hay=(s.title+' '+s.summary+' '+s.so_what+' '+s.source_name+' '+s.sector+' '+(s.episteme||[]).join(' ')).toLowerCase();
    if(!st.q.split(/\s+/).every(function(t){return hay.indexOf(t)>-1;}))return false;}
  return true;
}
var LRANK={actual:5,probable:4,plausible:3,possible:2,preposterous:1};
function filtered(){return S.filter(match).slice().sort(function(a,b){
  return (isNew(b)?1:0)-(isNew(a)?1:0) || (LRANK[b.likelihood]||0)-(LRANK[a.likelihood]||0) || a.title.localeCompare(b.title);});}
function toggle(set,v){set.has(v)?set.delete(v):set.add(v);}

function renderChips(){
  el('secchips').innerHTML = SECT.map(function(k){
    return '<button class="chip" type="button" data-k="'+esc(k)+'" aria-pressed="'+st.sec.has(k)+'">'+esc(k)+
     ' <span class="ct">'+S.filter(function(s){return s.sector===k;}).length+'</span></button>';}).join(' ');
  el('epichips').innerHTML = Object.keys(EPI).map(function(k){
    return '<button class="chip" type="button" data-k="'+esc(k)+'" aria-pressed="'+st.epi.has(k)+'">'+
     '<b style="color:var(--accent)">'+esc(EPI[k][0])+'</b> '+esc(EPI[k][1])+
     ' <span class="ct">'+S.filter(function(s){return (s.episteme||[]).indexOf(k)>-1;}).length+'</span></button>';}).join(' ');
  el('likchips').innerHTML = LIK.map(function(k){
    return '<button class="chip" type="button" data-k="'+k+'" aria-pressed="'+st.lik.has(k)+'">'+
     '<span class="sw" style="background:var('+LIKV[k]+')"></span>'+k+
     ' <span class="ct">'+S.filter(function(s){return s.likelihood===k;}).length+'</span></button>';}).join(' ');
  el('hzchips').innerHTML = [1,2,3].map(function(h){
    return '<button class="chip" type="button" data-k="'+h+'" aria-pressed="'+st.hz.has(h)+'">'+esc(HZL[h])+
     ' <span class="ct">'+S.filter(function(s){return s.horizon===h;}).length+'</span></button>';}).join(' ');
  el('tlchips').innerHTML = TLS.map(function(t){
    return '<button class="chip" type="button" data-k="'+t+'" aria-pressed="'+st.tl.has(t)+'">'+esc(TLL[t])+
     ' <span class="ct">'+S.filter(function(s){return s.timeline===t;}).length+'</span></button>';}).join(' ');
  el('secchips').querySelectorAll('.chip').forEach(function(c){c.onclick=function(){toggle(st.sec,c.dataset.k);render();};});
  el('epichips').querySelectorAll('.chip').forEach(function(c){c.onclick=function(){toggle(st.epi,c.dataset.k);render();};});
  el('likchips').querySelectorAll('.chip').forEach(function(c){c.onclick=function(){toggle(st.lik,c.dataset.k);render();};});
  el('hzchips').querySelectorAll('.chip').forEach(function(c){c.onclick=function(){toggle(st.hz,+c.dataset.k);render();};});
  el('tlchips').querySelectorAll('.chip').forEach(function(c){c.onclick=function(){toggle(st.tl,c.dataset.k);render();};});
}

var tip=el('tip');
function showTip(e,h){tip.innerHTML=h;tip.style.opacity=1;var r=tip.getBoundingClientRect();
  var x=e.clientX+14,y=e.clientY+14;
  if(x+r.width>innerWidth-8)x=e.clientX-r.width-12;
  if(y+r.height>innerHeight-8)y=e.clientY-r.height-12;
  tip.style.left=x+'px';tip.style.top=y+'px';}
function hideTip(){tip.style.opacity=0;}

function barPanel(node,rows,onClick,pressed){
  var max=Math.max.apply(null,[1].concat(rows.map(function(r){return r.n;})));
  node.innerHTML = rows.map(function(r){
    return '<button class="barrow" type="button" data-k="'+esc(r.k)+'" aria-pressed="'+(pressed(r.k))+'">'+
      '<span class="lbl">'+esc(r.label)+'</span>'+
      '<span class="bartrack"><span class="barfill" style="width:'+(r.n/max*100).toFixed(1)+'%"></span></span>'+
      '<span class="num">'+r.n+'</span></button>';}).join('');
  node.querySelectorAll('.barrow').forEach(function(b){
    b.onclick=function(){onClick(b.dataset.k);render();};
    b.onmousemove=function(e){showTip(e,'<b>'+b.querySelector('.num').textContent+'</b> signals<br><span style="color:var(--ink-3)">click to filter</span>');};
    b.onmouseleave=hideTip;});
}
function renderBars(){
  var rows=SECT.map(function(k){return {k:k,label:k,n:S.filter(function(s){return s.sector===k&&(!st.lik.size||st.lik.has(s.likelihood));}).length};});
  rows.sort(function(a,b){return b.n-a.n;});
  barPanel(el('secbars'),rows,function(k){toggle(st.sec,k);},function(k){return st.sec.has(k);});
  var erows=Object.keys(EPI).map(function(k){return {k:k,label:EPI[k][1],n:S.filter(function(s){return (s.episteme||[]).indexOf(k)>-1;}).length};});
  erows.sort(function(a,b){return b.n-a.n;});
  barPanel(el('epibars'),erows,function(k){toggle(st.epi,k);},function(k){return st.epi.has(k);});
}
function renderMatrix(){
  var grid=[1,2,3].map(function(h){return TLS.map(function(t){
    return S.filter(function(s){return s.horizon===h&&s.timeline===t&&(!st.sec.size||st.sec.has(s.sector));}).length;});});
  var max=Math.max.apply(null,[1].concat(grid.reduce(function(a,b){return a.concat(b);},[])));
  var h='<table class="matrix"><thead><tr><th></th>'+TLS.map(function(t){return '<th>'+esc(TLL[t])+'</th>';}).join('')+'</tr></thead><tbody>';
  [3,2,1].forEach(function(hz){
    h+='<tr><th class="rowh">'+esc(HZL[hz])+'</th>';
    TLS.forEach(function(t,j){
      var n=grid[hz-1][j];
      var step=n===0?0:Math.min(6,Math.max(1,Math.round(n/max*6)));
      var bg=n===0?'var(--grid)':'var('+SEQ[step]+')';
      var fg=n===0?'var(--ink-3)':inkOn(cssv(SEQ[step]));
      h+='<td><button class="cell" type="button" data-h="'+hz+'" data-t="'+t+'" style="background:'+bg+';color:'+fg+'">'+(n||'')+'</button></td>';});
    h+='</tr>';});
  h+='</tbody></table>';
  el('matrix').innerHTML=h;
  el('matrix').querySelectorAll('.cell').forEach(function(c){
    c.onclick=function(){var hz=+c.dataset.h,t=c.dataset.t;
      var already=st.hz.size===1&&st.hz.has(hz)&&st.tl.size===1&&st.tl.has(t);
      st.hz.clear();st.tl.clear();
      if(!already){st.hz.add(hz);st.tl.add(t);} render();};
    c.onmousemove=function(e){showTip(e,'<b>'+(c.textContent||'0')+'</b> signals<br>'+esc(HZL[+c.dataset.h])+' · '+esc(TLL[c.dataset.t]));};
    c.onmouseleave=hideTip;});
  el('mlegend').innerHTML='<span style="color:var(--ink-3)">Fewer</span>'+
    [1,3,5,6].map(function(i){return '<span><i style="background:var('+SEQ[i]+')"></i></span>';}).join('')+
    '<span style="color:var(--ink-3)">More</span>';
}

function episBlock(s){
  return '<div class="epis">'+(s.episteme||[]).map(function(t){
    var v=EPI[t]||['?',t];
    return '<span><b>'+esc(v[0])+'</b>'+esc(v[1])+'</span>';}).join('')+'</div>';
}
function renderResults(){
  var list=filtered();
  el('count').innerHTML='<b>'+list.length+'</b> of '+S.length+' signals shown';
  el('empty').classList.toggle('hidden',list.length>0);
  if(st.table){
    el('cards').classList.add('hidden'); el('tableview').classList.remove('hidden');
    el('tableview').innerHTML='<table class="data"><thead><tr><th>Signal</th><th>Sector</th><th>EPISTEME(S)</th>'+
      '<th>Likelihood</th><th>Horizon</th><th>Timeline</th><th>Source</th><th>So what</th></tr></thead><tbody>'+
      list.map(function(s){return '<tr><td class="tt">'+esc(s.title)+(isNew(s)?' <span class="newtag">NEW</span>':'')+'</td>'+
        '<td>'+esc(s.sector)+'</td><td>'+(s.episteme||[]).map(function(t){return esc((EPI[t]||['?'])[0]);}).join(' · ')+'</td>'+
        '<td>'+esc(s.likelihood)+'</td><td>'+esc(HZL[s.horizon])+'</td><td>'+esc(TLL[s.timeline])+'</td>'+
        '<td><a href="'+esc(s.source_url)+'" target="_blank" rel="noopener">'+esc(s.source_name)+'</a></td>'+
        '<td>'+esc(s.so_what)+'</td></tr>';}).join('')+'</tbody></table>';
    return;
  }
  el('tableview').classList.add('hidden'); el('cards').classList.remove('hidden');
  el('cards').innerHTML=list.map(function(s){
    return '<article class="card" id="card-'+esc(s.id)+'">'+
      '<div class="meta">'+(isNew(s)?'<span class="newtag">NEW</span>':'')+
        '<span class="lbadge"><span class="sw" style="background:var('+LIKV[s.likelihood]+')"></span>'+esc(s.likelihood)+'</span>'+
        '<span class="dot">&bull;</span><span>'+esc(s.sector)+'</span>'+
        '<span class="dot">&bull;</span><span>'+esc(HZL[s.horizon])+'</span>'+
        '<span class="dot">&bull;</span><span>'+esc(TLL[s.timeline])+'</span></div>'+
      '<h3>'+esc(s.title)+'</h3>'+ episBlock(s)+
      '<p>'+esc(s.summary)+'</p>'+
      '<div class="so"><b>So what:</b> '+esc(s.so_what)+'</div>'+
      '<div class="src">'+esc(s.source_name)+(s.source_date_label?' · '+esc(s.source_date_label):'')+
        ' · '+esc(s.source_type||'source')+' · <a href="'+esc(s.source_url)+'" target="_blank" rel="noopener">source &#8599;</a></div>'+
    '</article>';}).join('');
}
function render(){renderChips();renderBars();renderMatrix();renderResults();}

/* jump from an evidence chip to its card */
document.addEventListener('click',function(e){
  var b=e.target.closest?e.target.closest('[data-goto]'):null;
  if(!b)return;
  var id=b.getAttribute('data-goto');
  st.sec.clear();st.epi.clear();st.lik.clear();st.hz.clear();st.tl.clear();st.newonly=false;st.q='';
  el('q').value='';el('newonly').setAttribute('aria-pressed','false');
  if(st.table){st.table=false;el('viewbtn').setAttribute('aria-pressed','false');el('viewbtn').textContent='Table view';}
  render();
  var card=el('card-'+id);
  if(card){card.scrollIntoView({behavior:'smooth',block:'center'});
    card.classList.add('flash');setTimeout(function(){card.classList.remove('flash');},2200);}
});

var t=null;
el('q').oninput=function(e){clearTimeout(t);t=setTimeout(function(){st.q=e.target.value.trim().toLowerCase();renderResults();},130);};
el('reset').onclick=function(){st.sec.clear();st.epi.clear();st.lik.clear();st.hz.clear();st.tl.clear();
  st.q='';st.newonly=false;el('q').value='';el('newonly').setAttribute('aria-pressed','false');render();};
el('newonly').onclick=function(){st.newonly=!st.newonly;el('newonly').setAttribute('aria-pressed',st.newonly);renderResults();};
el('viewbtn').onclick=function(){st.table=!st.table;el('viewbtn').setAttribute('aria-pressed',st.table);
  el('viewbtn').textContent=st.table?'Card view':'Table view';renderResults();};

var v=D.verification||{};
el('foot').innerHTML=
 '<p><b>EPISTEME(S).</b> Every signal carries 2–4 domain tags: '+
 Object.keys(EPI).map(function(k){return '<b>'+esc(EPI[k][0])+'</b> '+esc(EPI[k][1]);}).join(' · ')+
 '. <i>Interaction with Environment</i> is applied literally — climate, energy, emissions, water, land, food, biodiversity, pollution, biosecurity, physical climate risk, resource scarcity, materials circularity and the environmental footprint of technology — and never metaphorically.</p>'+
 '<p><b>Three Horizons.</b> H1 is the current system continuing, being measured or defended. H2 is the contested transition. H3 is the emerging system that would dominate if it wins. <b>Timeline</b> is years until a head of school must act, not years until something is invented.</p>'+
 '<p><b>Likelihood</b> tracks the claim the "so what" makes, not the authority of the source. <i>Actual</i> is reserved for claims needing no projection.</p>'+
 '<p><b>Opportunities and threats</b> are held stable between scans and revised only when new signals genuinely move them; each carries the date it was first identified and last revised. <b>Critical uncertainties</b> are the questions whose answers would change the strategy, not the questions that are merely interesting.</p>'+
 (v.note?'<p><b>Verification.</b> '+esc(v.note)+'</p>':'')+
 '<p>Sources marked <i>advertisement</i> are vendor marketing and should not be used as evidence in a board memo.</p>';

var tb=el('tbtn');
function applyTheme(mode){
  if(mode)document.documentElement.setAttribute('data-theme',mode);
  else document.documentElement.removeAttribute('data-theme');
  var dark=document.documentElement.getAttribute('data-theme')==='dark'||
    (!document.documentElement.hasAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
  tb.textContent=dark?'Light mode':'Dark mode';
  renderMatrix();
}
tb.onclick=function(){
  var dark=document.documentElement.getAttribute('data-theme')==='dark'||
    (!document.documentElement.hasAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
  applyTheme(dark?'light':'dark');};
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){
  applyTheme(document.documentElement.getAttribute('data-theme')||null);});

render(); applyTheme(null);
})();
</script>
</body>
</html>
"""

open(OUT, "w", encoding="utf-8").write(TPL.replace("__PAYLOAD__", payload))
n = d["signals"]
print(f"OK  {OUT}  signals={len(n)}  opportunities={len(d['opportunities'])} "
      f"threats={len(d['threats'])} uncertainties={len(d['critical_uncertainties'])}")
from collections import Counter
print("    likelihood:", dict(Counter(s["likelihood"] for s in n)))
print("    horizon:   ", dict(Counter(s["horizon"] for s in n)))
print("    timeline:  ", dict(Counter(s["timeline"] for s in n)))
print("    episteme:  ", dict(Counter(t for s in n for t in s["episteme"])))
print("    generated: ", gen)
