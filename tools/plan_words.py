#!/usr/bin/env python3
"""Accurate words for an assembled plan: transcribe each piece from its ORIGINAL audio with context."""
import json, subprocess, sys, re
import numpy as np
from faster_whisper import WhisperModel
plan = json.load(open(sys.argv[1])); out = sys.argv[2]
fixes = [f.split("=", 1) for f in sys.argv[3:]]
m = WhisperModel("medium", device="cpu", compute_type="int8")
words = []; off = 0.0
for p in plan["pieces"]:
    s0 = max(p["s"] - 3, 0); e0 = p["e"] + 1
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(s0), "-to", str(e0), "-i", p["a"], "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, word_timestamps=True, language="en")
    for sg in segs:
        for w in sg.words:
            ts = s0 + w.start; te = s0 + w.end
            mid = (ts + te) / 2
            if p["s"] - 0.05 <= mid < p["e"]:
                t = w.word.strip()
                for b, g in fixes: t = re.sub(b, g, t, flags=re.I)
                words.append({"w": t, "s": round(max(ts - p["s"], 0) + off, 2), "e": round(min(te, p["e"]) - p["s"] + off, 2)})
    off += p["e"] - p["s"]
json.dump(words, open(out, "w"), indent=0)
print(" ".join(w["w"] for w in words))
