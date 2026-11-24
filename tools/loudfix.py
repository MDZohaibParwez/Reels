#!/usr/bin/env python3
"""Two-pass loudness normalise a finished reel to -14 LUFS / -1.5 dBTP (video stream copied).
python3 tools/loudfix.py in.mp4 out.mp4"""
import json, re, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
err = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err).group(0))
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-movflags", "+faststart", out], check=True)
print("ok", out)
