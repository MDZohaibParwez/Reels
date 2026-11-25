#!/usr/bin/env python3
"""2026-11-26 (LESSONS M26): show which ranges of a source are already used BEFORE you transcribe/plan a moment.
python3 tools/free.py elonvisit.mp4 [start end]  -> used ranges (+ reel), and whether start-end is free.
Source names in footage_used.json are basenames of the local files (elonvisit.mp4 = FaZe Rug full tour, touring_elon.mp4 =
Paolo Tiramani interview, inside_elon.mp4 = Enes Yilmazer factory tour, casita.mp4 = Elon Casita delivery b-roll)."""
import json, os, sys
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "footage_used.json")
src = os.path.basename(sys.argv[1]); used = sorted((u["s"], u["e"], u["reel"]) for u in json.load(open(LOG)) if u["src"] == src)
for s, e, r in used: print(f"{s:8.1f}-{e:8.1f}  {r}")
if not used: print(f"{src}: nothing used yet")
if len(sys.argv) >= 4:
    a, b = float(sys.argv[2]), float(sys.argv[3])
    hit = [r for s, e, r in used if min(b, e) - max(a, s) > 1.0]
    print("FREE" if not hit else f"OVERLAP with {sorted(set(hit))}")
