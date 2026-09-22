# MV Maker Signal Scan

A standing, cumulative horizon scan of the future of Maker programming in K–12 — Preschool
through High School — maintained for Jared Colley, Chief Innovation Officer, The Mount Vernon
School & MV Ventures.

**Live dashboard:** https://jcolley8.github.io/mv-maker-signal-scan/

Sister project to [mv-futures-signal-scan](https://github.com/jcolley8/mv-futures-signal-scan);
same architecture, same delta-and-assemble pattern, different subject.

---

## What it holds

| | |
|---|---|
| **Signals** | Every entry carries a summary, a "so what", a verified source link, a sector, a likelihood, a Three Horizons position, a timeline, and 2–4 EPISTEME(S) tags. |
| **Opportunities** | Exactly three, for the Mount Vernon maker program. Held stable between scans; revised only when new signals genuinely move them. |
| **Threats** | Exactly three, same rule. Each carries a mechanism and early-warning indicators. |
| **Critical uncertainties** | At least two. Questions whose answers would change the strategy, each with two poles and watch indicators. |

### EPISTEME(S)

| Tag | Meaning |
|---|---|
| `E-Educational` | Teaching, learning, curriculum, assessment, credentialing, schooling |
| `P-Political` | Legislation, regulation, policy, public funding, standards bodies, litigation |
| `I-Environmental` | Interaction with Environment — climate, ecology, energy, emissions, water, land, food, biodiversity, pollution, biosecurity, physical climate risk, resource scarcity, materials circularity, the environmental footprint of technology. Applied literally, never metaphorically. |
| `S-Social` | Behaviour, culture, identity, community, equity, wellbeing, demographics |
| `T-Technological` | Tools, machines, software, hardware, platforms, technical capability |
| `EC-Economic` | Markets, prices, costs, funding, labour, business models, enrollment economics |
| `ME-Moral/Ethical` | Fairness, authenticity, integrity, consent, safety, professional duty, provenance |
| `SC-Scientific` | Research and method, empirical evidence, studies, measurement, state of knowledge |

### Calibration

- **Horizon** — H1 the current system continuing, being measured or defended · H2 the contested transition · H3 the emerging system that would dominate if it wins.
- **Timeline** — years until a head of school must act. `0-2` a rule in force, a product at a payable price, or a present condition already biting · `3-6` proposed rules, consultations, single-jurisdiction rulings · `7-10` basic science, patents, early research.
- **Likelihood** — tracks the claim the "so what" makes, not the authority of the source. `actual` only where the claim needs no projection.

---

## How an update works

1. A scheduled task runs every 48 hours, scans across all eight sectors, and writes a **delta file**.
2. The delta is uploaded to the shared Google Drive folder as `delta-YYYY-MM-DD.json`.
3. The GitHub Action pulls new deltas, runs `assemble.py`, rebuilds `index.html`, commits, and deploys to Pages.

Delta shape — only `date` is required:

```json
{
  "date": "2026-09-24",
  "new_signals": [ { "...full signal objects..." } ],
  "sightings": { "existing-signal-id": 2 },
  "opportunities": [ "...all three, only if revised..." ],
  "threats": [ "...all three, only if revised..." ],
  "critical_uncertainties": [ "...all, only if revised..." ],
  "archived": [ "id-to-retire" ]
}
```

## Local use

```bash
python3 assemble.py drive signals.json signals.json   # merge any deltas
python3 build_dashboard.py signals.json index.html    # rebuild the page
```

`build_dashboard.py` refuses to build on a schema error: unknown ids, duplicate ids,
duplicate source URLs, bad episteme vocabulary, fewer than 2 or more than 4 episteme tags,
an unknown sector, likelihood, timeline or horizon, a missing required field, or anything
other than exactly three opportunities and three threats.

## Setup checklist

- [ ] Create the repo as `jcolley8/mv-maker-signal-scan`, push these files to `main`
- [ ] Settings → Pages → Source: **GitHub Actions**
- [x] Drive delta folder created: `1Ftfs8_hNF7iMAxg49iIpg2y5XDZ4KbpR`
      (https://drive.google.com/drive/folders/1Ftfs8_hNF7iMAxg49iIpg2y5XDZ4KbpR) — set it to *Anyone with the link — Viewer* so the Action can read it
- [ ] Repo → Settings → Secrets and variables → Actions:
      - variable `GDRIVE_FOLDER_ID` = `1Ftfs8_hNF7iMAxg49iIpg2y5XDZ4KbpR`
      - secret `GDRIVE_API_KEY` = a Google API key with the Drive API enabled
- [x] The scheduled task already writes to that folder

If the Drive variables are unset the Action simply assembles whatever is already in `drive/`.
