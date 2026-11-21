#!/usr/bin/env python3
"""Assemble a multi-cut source edit: list of pieces, each with audio from one source and
picture from the same or a b-roll source. Output: square/portrait intermediate for render2.

plan.json: {"size": [1080,1080], "pieces": [
  {"a": "elon.mp4", "s": 9.8, "e": 13.4, "v": "enes8.mp4", "vs": 33.0, "crop": "488:488:199:0"}, ...]}
"v"/"vs" optional (default: same as audio). "crop" optional per source (w:h:x:y before scaling).
"""
import json, subprocess, sys, os, tempfile

plan = json.load(open(sys.argv[1])); out = sys.argv[2]
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
print("assembled", out)
