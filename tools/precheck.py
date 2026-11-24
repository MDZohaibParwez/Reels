#!/usr/bin/env python3
"""Pre-post gate for a rendered reel (creator-audit-master, section 7).

python3 tools/precheck.py clips/<file>.mp4 [--caption "..."] [--queue queue.json]

Checks what a script can measure; prints PASS/FAIL per check and exits 1 if any FAIL.
Things it cannot judge (is the hook interesting? is frame 0 the best visual?) still need eyes on frames.
"""
import argparse, json, re, subprocess, sys


def probe(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration,size",
                          "-of", "json", f], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def lufs(f):
    err = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    return float(m[-1]) if m else None


def luma(f, t):
    err = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(t), "-i", f, "-frames:v", "1", "-vf", "signalstats,metadata=print",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"YAVG=([\d.]+)", err)
    return float(m.group(1)) if m else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file"); p.add_argument("--caption"); p.add_argument("--queue", default="queue.json")
    a = p.parse_args()
    res = []
    def check(name, ok, info=""):
        res.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  ({info})" if info else ""))

    d = probe(a.file)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    dur = float(d["format"]["duration"]); size = int(d["format"]["size"]) / 1e6
    check("1080x1920", (v["width"], v["height"]) == (1080, 1920), f'{v["width"]}x{v["height"]}')
    check("30fps", v["r_frame_rate"] in ("30/1", "30000/1001"), v["r_frame_rate"])
    check("length 15-35s", 15 <= dur <= 35, f"{dur:.1f}s")
    check("size < 30 MB", size < 30, f"{size:.1f} MB")
    has_a = any(s["codec_type"] == "audio" for s in d["streams"])
    check("has audio", has_a)
    if has_a:
        L = lufs(a.file)
        check("loudness -16..-12 LUFS", L is not None and -16 <= L <= -12, f"{L} LUFS")
    y0 = luma(a.file, 0.0)
    check("frame 0 not dark/black", y0 is not None and y0 > 35, f"YAVG {y0}")

    if a.caption is not None:
        c = a.caption
        first = c.strip().split("\n")[0]
        tags = re.findall(r"#\w+", c)
        check("caption first line <= 125 chars (shows before 'more')", len(first) <= 125, f"{len(first)}")
        check("3-5 hashtags", 3 <= len(tags) <= 5, f"{len(tags)}")
        check("no spam tags", not any(t.lower() in ("#viral", "#fyp", "#foryou", "#trending", "#explore") for t in tags))
        if "boxabl" in c.lower():
            check("BOXABL: tags @boxabl", "@boxabl" in c.lower())
        q = [s for s in re.split(r"(?<=[.!?])\s+", c.split("\n\n")[0]) if s.endswith("?")]
        check("ends with a question (comment trigger)", bool(q))
        try:
            prev = [r.get("caption", "") for r in json.load(open(a.queue))["reels"]][-6:]
            last_q = q[-1].strip().lower() if q else ""
            reused = sum(1 for pc in prev if last_q and last_q in pc.lower())
            check("question not reused in last 6 captions", reused <= 1, f"used {reused}x")
        except Exception as e:
            print("SKIP queue check:", e)

    print("RESULT:", "PASS" if all(res) else "FAIL")
    sys.exit(0 if all(res) else 1)


if __name__ == "__main__":
    main()
