#!/usr/bin/env python3
"""Pre-post gate for a rendered reel (creator-audit-master, section 7).

python3 tools/precheck.py clips/<file>.mp4 [--caption "..."] [--queue queue.json]

Checks what a script can measure; prints PASS/FAIL per check and exits 1 if any FAIL.
Things it cannot judge (is the hook interesting? is frame 0 the best visual?) still need eyes on frames.
"""
import argparse, json, os, re, subprocess, sys


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


QWORDS = ("how", "what", "why", "who", "when", "where", "which", "is", "are", "do", "does", "can", "should")
LABEL = [r"^[A-Z][\w.']+( [A-Z][\w.']+)* on ",          # "Rick Caruso on BOXABL homes"
         r"\bis (more|not just|the future)\b", r"^this is\b", r"\bexplained\b", r"^the (story|truth) of\b"]


def hook_checks(hook):
    """RULE 1: <= 8 words, one [keyword], curiosity/stakes line - not a question or a topic label."""
    plain = re.sub(r"[\[\]]", "", hook).strip()
    words = plain.split()
    first = words[0].lower().strip("\"'") if words else ""
    yield "hook <= 8 words", 1 <= len(words) <= 8, f"{len(words)}: {plain!r}"
    yield "hook has one [keyword]", len(re.findall(r"\[[^\]]+\]", hook)) == 1, hook
    yield "hook is not a question/topic opener (How/What/Why...)", first not in QWORDS and "?" not in plain, plain
    bad = [x for x in LABEL if re.search(x, plain, flags=re.I if not x.startswith("^[A-Z]") else 0)]
    yield "hook is not a topic label", not bad, (bad[0] if bad else "")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file"); p.add_argument("--caption"); p.add_argument("--queue", default="queue.json")
    p.add_argument("--hook", help="the --top hook text given to render2.py (default: queue.json entry's 'hook')")
    a = p.parse_args()
    try:
        reels = json.load(open(a.queue))["reels"]
    except Exception:
        reels = []
    me = os.path.basename(a.file)
    own = next((r for r in reels if os.path.basename(r.get("file", "")) == me), None)
    others = [r for r in reels if r is not own]
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
    check("frame 0 not black", y0 is not None and y0 > 22, f"YAVG {y0}")

    if a.caption is not None:
        c = a.caption
        first = c.strip().split("\n")[0]
        tags = re.findall(r"#\w+", c)
        check("caption first line <= 125 chars (shows before 'more')", len(first) <= 125, f"{len(first)}")
        check("3-5 hashtags", 3 <= len(tags) <= 5, f"{len(tags)}")
        check("no spam tags", not any(t.lower() in ("#viral", "#fyp", "#foryou", "#trending", "#explore") for t in tags))
        if "boxabl" in c.lower():
            check("BOXABL: tags @boxabl", "@boxabl" in c.lower())
        body = "\n".join(l for l in c.split("\n") if not re.match(r"^\s*([@#]\S+\s*)+$", l))
        q = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", body) if s.strip().endswith("?")]
        check("ends with a question (comment trigger)", bool(q))
        prev = [r.get("caption", "") for r in others][-6:]
        last_q = q[-1].strip().lower() if q else ""
        reused = sum(1 for pc in prev if last_q and last_q in pc.lower())
        # 2026-11-25: was "<= 1" and counted the reel itself -> a question used once before still passed.
        check("question not reused in last 6 captions", reused == 0, f"used {reused}x before")

    # Hook gate (RULE 1). 2026-11-25: LESSONS said precheck checks hooks (M3) but it did not -> now it does.
    hook = a.hook if a.hook is not None else (own or {}).get("hook")
    if hook is None:
        check("hook given (--hook or queue 'hook')", False, "missing")
    else:
        for name, ok, info in hook_checks(hook):
            check(name, ok, info)

    print("RESULT:", "PASS" if all(res) else "FAIL")
    sys.exit(0 if all(res) else 1)


if __name__ == "__main__":
    main()
