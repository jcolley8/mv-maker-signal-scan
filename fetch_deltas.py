#!/usr/bin/env python3
"""Download any delta-*.json files listed in a Drive API response that we do not already have."""
import json, os, sys, urllib.request

listing = sys.argv[1] if len(sys.argv) > 1 else "/tmp/list.json"
dest_dir = sys.argv[2] if len(sys.argv) > 2 else "drive"
key = os.environ.get("KEY", "")

os.makedirs(dest_dir, exist_ok=True)
files = json.load(open(listing)).get("files", [])
got = 0
for f in files:
    name = f.get("name", "")
    if not (name.startswith("delta-") and name.endswith(".json")):
        continue
    dest = os.path.join(dest_dir, name)
    if os.path.exists(dest):
        continue
    url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={key}"
    with urllib.request.urlopen(url) as r, open(dest, "wb") as out:
        out.write(r.read())
    print("fetched", name, os.path.getsize(dest), "bytes")
    got += 1
print(f"{got} new delta(s); {len(files)} file(s) in folder")
