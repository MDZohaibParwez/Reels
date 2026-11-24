#!/usr/bin/env python3
"""Assemble a multi-cut source edit: list of pieces, each with audio from one source and
picture from the same or a b-roll source. Output: square/portrait intermediate for render2.

plan.json: {"size": [1080,1080], "pieces": [
  {"a": "elon.mp4", "s": 9.8, "e": 13.4, "v": "enes8.mp4", "vs": 33.0, "crop": "488:488:199:0"}, ...]}
"v"/"vs" optional (default: same as audio). "crop" optional per source (w:h:x:y before scaling).
"""
import json, subprocess, sys, os, tempfile

plan = json.load(open(sys.argv[1])); out = sys.argv[2]
# 2026-11-25 (LESSONS M14): footage memory. Every reel's audio ranges are logged in footage_used.json so a later
# run can't silently re-cut a moment that already went out. Pass the reel id as argv[3] to record it.
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "footage_used.json")
used = json.load(open(LOG)) if os.path.exists(LOG) else []
reel = sys.argv[3] if len(sys.argv) > 3 else None
for p in plan["pieces"]:
    src = os.path.basename(p["a"])
    for u in used:
        if u["src"] == src and u["reel"] != reel and min(p["e"], u["e"]) - max(p["s"], u["s"]) > 1.0:
            print(f"OVERLAP: {src} {p['s']}-{p['e']} already used in {u['reel']} ({u['s']}-{u['e']}) -> pick a new moment",
                  file=sys.stderr)
W, H = plan["size"]
tmp = tempfile.mkdtemp(); parts = []
for i, p in enumerate(plan["pieces"]):
    d = p["e"] - p["s"]
    vsrc = p.get("v", p["a"]); vs = p.get("vs", p["s"])
    crop = (f"crop={p['crop']}," if p.get("crop") else "")
    vf = f"{crop}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,format=yuv420p"
    f = os.path.join(tmp, f"p{i:02d}.mp4"); parts.append(f)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(vs), "-t", str(d), "-i", vsrc,
                    "-ss", str(p["s"]), "-t", str(d), "-i", p["a"],
                    "-map", "0:v", "-map", "1:a", "-vf", vf, "-af", "aresample=44100,aformat=channel_layouts=stereo",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k",
                    "-t", str(d), f], check=True)
lst = os.path.join(tmp, "l.txt")
open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
if reel:
    used = [u for u in used if u["reel"] != reel] + [{"reel": reel, "src": os.path.basename(p["a"]), "s": p["s"], "e": p["e"]}
                                                    for p in plan["pieces"]]
    json.dump(used, open(LOG, "w"), indent=0)
print("assembled", out)
