#!/usr/bin/env python3
"""Accurate words for an assembled plan: transcribe each piece from its ORIGINAL audio with context."""
import json, subprocess, sys, re
import numpy as np
from faster_whisper import WhisperModel
plan = json.load(open(sys.argv[1])); out = sys.argv[2]
fixes = [f.split("=", 1) for f in sys.argv[3:]]
m = WhisperModel("medium", device="cpu", compute_type="int8")
words = []; off = 0.0; seen = []; used = []
for p in plan["pieces"]:
    s0 = max(p["s"] - 3, 0); e0 = p["e"] + 1
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(s0), "-to", str(e0), "-i", p["a"], "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, word_timestamps=True, language="en")
    cur = []
    for sg in segs:
        for w in sg.words:
            ts = s0 + w.start; te = s0 + w.end
            # 2026-11-25 (LESSONS M15): assign a word by its START, not its midpoint. Midpoint rule dropped the
            # last word of almost every piece ("minute?", "true?", "it.") and duplicated words across
            # back-to-back pieces ("the the", "in in"). A word now belongs to exactly one piece.
            dup = any(a == p["a"] and abs(t0 - ts) < 0.15 for a, t0 in used)  # already captioned in an earlier piece
            if p["s"] - 0.12 <= ts < p["e"] and not dup:
                cur.append((p["a"], ts))
                t = w.word.strip()
                for b, g in fixes: t = re.sub(b, g, t, flags=re.I)
                if t[:1] in ".%" and words and len(t) <= 3:  # "U" ".S." -> "U.S.", "80" "%" -> "80%"
                    words[-1]["w"] += t; words[-1]["e"] = round(min(te, p["e"]) - p["s"] + off, 2); continue
                words.append({"w": t, "s": round(max(ts - p["s"], 0) + off, 2), "e": round(min(te, p["e"]) - p["s"] + off, 2)})
    # guard: a piece whose last caption word ends long before the cut usually lost a word -> hand-check it
    last = [w for w in words if off <= w["s"] < off + p["e"] - p["s"]]
    gap = (off + p["e"] - p["s"]) - (last[-1]["e"] if last else off)
    if gap > 0.35:
        print(f"CHECK piece {len(seen)}: last word ends {gap:.2f}s before the cut -> word may be missing", file=sys.stderr)
    seen.append(1); used += cur
    off += p["e"] - p["s"]
json.dump(words, open(out, "w"), indent=0)
print(" ".join(w["w"] for w in words))
