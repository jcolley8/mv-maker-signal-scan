#!/usr/bin/env python3
"""
assemble.py — MV Maker Signal Scan
Merges the base corpus with every delta file in a folder, writes the updated corpus.

Usage:  python3 assemble.py <delta_dir> <base_signals.json> [out.json]

Delta file shape (only `date` is required; every other key is optional):
{
  "date": "YYYY-MM-DD",
  "new_signals": [ {...full signal objects...} ],
  "sightings": { "<existing id>": <new count> },
  "opportunities": [ ...all three, only when revised... ],
  "threats": [ ...all three, only when revised... ],
  "critical_uncertainties": [ ...all of them, only when revised... ],
  "archived": [ "<id to retire>" ]
}
"""
import json, sys, os, glob

delta_dir = sys.argv[1] if len(sys.argv) > 1 else "drive"
base_path = sys.argv[2] if len(sys.argv) > 2 else "signals.json"
out_path  = sys.argv[3] if len(sys.argv) > 3 else base_path

base = json.load(open(base_path, encoding="utf-8"))
by_id = {s["id"]: s for s in base["signals"]}
order = [s["id"] for s in base["signals"]]

deltas = sorted(glob.glob(os.path.join(delta_dir, "delta-*.json")))
applied, added, bumped, archived_n = [], 0, 0, 0

for path in deltas:
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"  !! skipping unreadable delta {os.path.basename(path)}: {e}")
        continue
    date = d.get("date")
    if not date:
        print(f"  !! skipping {os.path.basename(path)}: no date")
        continue

    for s in d.get("new_signals", []):
        sid = s.get("id")
        if not sid:
            continue
        if sid in by_id:                      # already known — treat as a sighting
            by_id[sid]["sightings"] = by_id[sid].get("sightings", 1) + 1
            by_id[sid]["last_seen"] = date
            bumped += 1
            continue
        s.setdefault("first_seen", date)
        s.setdefault("last_seen", date)
        s.setdefault("sightings", 1)
        by_id[sid] = s
        order.append(sid)
        added += 1

    for sid, n in (d.get("sightings") or {}).items():
        if sid in by_id:
            by_id[sid]["sightings"] = max(by_id[sid].get("sightings", 1), int(n))
            by_id[sid]["last_seen"] = date
            bumped += 1

    for key in ("opportunities", "threats", "critical_uncertainties"):
        if d.get(key):
            base[key] = d[key]

    for sid in d.get("archived", []):
        if sid in by_id:
            by_id.pop(sid)
            archived_n += 1

    base["last_updated"] = date
    base["scan_count"] = base.get("scan_count", 0) + 1
    applied.append(os.path.basename(path))

order = [i for i in order if i in by_id]
seen, clean = set(), []
for i in order:
    if i in seen:
        continue
    seen.add(i)
    clean.append(by_id[i])
base["signals"] = clean

json.dump(base, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"assembled {len(applied)} delta(s): {', '.join(applied) if applied else 'none'}")
print(f"  +{added} new · {bumped} sighting bumps · -{archived_n} archived · {len(clean)} total")
print(f"  last_updated={base['last_updated']} scan_count={base['scan_count']} -> {out_path}")
