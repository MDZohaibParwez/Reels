#!/usr/bin/env python3
"""Premium Raj-Shamani-style reel renderer.

python3 render2.py SRC OUT START END --top "Manifested it, Said it, Achieved it!" \
    [--crop w:h:x:y] [--end-text "FINAL LINE"] [--assets assets] [--music-db -26]

- 1080x1920, footage cropped to 4:5 (1080x1350, or 1:1 with --vh 1080) over a blurred, dimmed copy of itself
  (no dead black bands). v3 (2026-11-24 audit): BIG bold hook headline (--top) visible from frame 0, inside
  the Instagram safe zone (below the Reels header); mark highlight words with [brackets] -> yellow.
  --hook-style classic restores the old thin italic bar.
- slow push-in + punch-in "cuts" on every sentence, film grain, contrast, vignette
- big bold captions in bursts (1-3 words), pop scale+fade, key words yellow/glow white
- original cinematic pad (low) + whoosh/impact on big words, loudnorm voice
- ending: last frame lingers 1.2s with final statement
"""
import argparse, json, os, subprocess, tempfile, re
import numpy as np

W, H = 1080, 1920
VW, VH = 1080, 1350
VTOP = 300
HOOK_STYLE = "big"
STOP = set(("a an the and or but to of in on at is are was were be am i you he she it we they me my your his her its "
            "our their this that for with as so just do does did not no now there there's we're i'm it's will "
            "can could would should have has had been being from by about into than then them those these what "
            "when where who how which while if all very really gonna going").split())
YELLOW = "&H0000D7FF&"; WHITE = "&H00FFFFFF&"


def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def transcribe(src, start, end):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-to", str(end), "-i", src,
                          "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, word_timestamps=True)
    return [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]


def is_key(w):
    w = w["w"] if isinstance(w, dict) else w
    c = re.sub(r"[^\w']", "", w.lower())
    return bool(re.search(r"\d", c)) or (len(c) >= 5 and c not in STOP)


def bursts_of(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        end_punct = w["w"].endswith((".", "?", "!", ","))
        if len(cur) == 3 or end_punct or (len(cur) == 2 and is_key(w)):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def sentences_of(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"].endswith((".", "?", "!")):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def hook_text(top, maxlen=17):
    """Wrap headline to <=2 lines (~maxlen chars each) and turn [word] into yellow."""
    plain = re.sub(r"[\[\]]", "", top)
    words, lines, cur = top.split(), [], ""
    for w in words:
        n = len(re.sub(r"[\[\]]", "", (cur + " " + w).strip()))
        if cur and n > maxlen and len(lines) < 1:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    out = "\\N".join(lines)
    out = re.sub(r"\[([^\]]+)\]", lambda m: "{\\c" + YELLOW + "}" + m.group(1) + "{\\c&H00FFFFFF&}", out)
    return out, len(plain)


def build_ass(words, top, dur, end_text, path):
    cap_y = VTOP + VH - (260 if VH >= 1350 else 190)
    L = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Hook,Montserrat ExtraBold,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,1,0,0,0,100,100,0,0,1,6,5,5,40,40,0,1",
         "Style: Top,Montserrat,44,&H00F2F2F2,&H00FFFFFF,&H00000000,&H00000000,0,1,0,0,100,100,0.5,0,1,0,0,8,40,40,0,1",
         # 2026-11-26 audit (M25): captions had Outline 0 + a WHITE glow -> white text vanished on bright footage
         # (fold_race 1s "BOXABL RIGHT" on a white wall, house_per_minute 0s "DUDE" on pale ground). Now: thick black
         # outline + dark soft halo behind every caption, readable on any background.
         "Style: Cap,Montserrat ExtraBold,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,3,5,50,50,0,1",
         "Style: Glow,Montserrat ExtraBold,92,&H00000000,&H00000000,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,14,0,5,50,50,0,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    if HOOK_STYLE == "classic":  # old thin elegant top bar (pre-v3)
        L.append(f"Dialogue: 0,{ts(0)},{ts(dur)},Top,,0,0,0,,{{\\pos(540,215)\\fad(300,0)}}{top.replace('[', '').replace(']', '')}")
        L.append(f"Dialogue: 0,{ts(0)},{ts(dur)},Top,,0,0,0,,{{\\an7\\pos(240,282)\\alpha&HA0&\\p1}}m 0 0 l 600 0 600 2 0 2{{\\p0}}")
    else:  # v3: big hook headline, readable on frame 0, centred in the band above the video
        txt, n = hook_text(top)
        fs = 104 if n <= 30 else 90
        y = VTOP - 165
        L.append(f"Dialogue: 3,{ts(0)},{ts(dur)},Hook,,0,0,0,,{{\\pos(540,{y})\\fs{fs}\\fscx94\\fscy94\\t(0,120,\\fscx100\\fscy100)}}{txt}")
    sfx = []
    last_sfx = -9
    bursts = bursts_of(words)
    for i, b in enumerate(bursts):
        st = b[0]["s"]
        en = bursts[i + 1][0]["s"] if i + 1 < len(bursts) else min(dur, b[-1]["e"] + 0.4)
        en = min(en, b[-1]["e"] + 0.6)
        if en - st < 0.2: en = st + 0.2
        keys = [w for w in b if is_key(w)]
        key = max(keys, key=lambda w: len(w["w"])) if keys else None
        txt = []
        for w in b:
            t = re.sub(r"[.,!?]+$", "", w["w"]).upper()
            if w is key:
                col = YELLOW if i % 3 != 2 else WHITE
                txt.append("{\\c" + col + "}" + t + "{\\c&H00FFFFFF&}")
            else:
                txt.append(t)
        text = " ".join(txt)
        plain = re.sub(r"\{[^}]*\}", "", text)
        if len(plain) > 18:  # break long bursts onto two lines
            parts = text.split(" "); h = len(parts) // 2
            text = " ".join(parts[:h]) + "\\N" + " ".join(parts[h:])
        pop = "\\fscx72\\fscy72\\t(0,140,\\fscx104\\fscy104)\\t(140,220,\\fscx100\\fscy100)\\fad(90,60)"
        gtext = re.sub(r"\{\\c[^}]*\}", "", text)  # halo = one dark colour, no yellow blob
        L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Glow,,0,0,0,,{{\\pos(540,{cap_y})\\blur12\\alpha&H70&{pop}}}{gtext}")
        L.append(f"Dialogue: 1,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\pos(540,{cap_y}){pop}}}{text}")
        if key and st - last_sfx > 3.0:
            sfx.append((st, "whoosh" if len(sfx) % 2 == 0 else "impact")); last_sfx = st
    if end_text:
        L.append(f"Dialogue: 2,{ts(dur - 0.05)},{ts(dur + 1.4)},Cap,,0,0,0,,{{\\pos(540,{cap_y})\\c{YELLOW}\\fscx80\\fscy80\\t(0,250,\\fscx100\\fscy100)\\fad(200,0)}}{end_text.upper()}")
        sfx.append((dur - 0.05, "impact"))
    open(path, "w").write("\n".join(L) + "\n")
    return sfx


def zoom_expr(words, dur, fps=30):
    """Piecewise zoom: each sentence alternates base zoom (punch-in cut) + slow push."""
    sents = sentences_of(words)
    expr = "1.0+0.00025*on"
    for k, s in enumerate(reversed(sents)):
        idx = len(sents) - 1 - k
        base = [1.00, 1.10, 1.04, 1.13][idx % 4]
        f0 = int(s[0]["s"] * fps)
        expr = f"if(gte(on,{f0}),{base}+0.00025*(on-{f0}),{expr})"
    return expr


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src"); p.add_argument("out"); p.add_argument("start", type=float); p.add_argument("end", type=float)
    p.add_argument("--top", default="Manifested it, Said it, Achieved it!")
    p.add_argument("--crop", help="w:h:x:y crop of source before framing")
    p.add_argument("--end-text", default="")
    p.add_argument("--assets", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))
    p.add_argument("--music-db", type=float, default=-24)
    p.add_argument("--words")
    p.add_argument("--vh", type=int, default=1350)
    p.add_argument("--hook-style", default="big", choices=["big", "classic"])
    p.add_argument("--fix", action="append", default=[], help="wrong=Right word fix, e.g. boxable=BOXABL")
    a = p.parse_args()
    global VH, VTOP, HOOK_STYLE
    HOOK_STYLE = a.hook_style
    VH = a.vh
    if HOOK_STYLE == "classic":
        VTOP = 300 if VH >= 1350 else 330
    else:  # leave room for a 2-line hook below the IG Reels header (~0-220px)
        VTOP = 470 if VH >= 1350 else 500
    dur = a.end - a.start
    words = json.load(open(a.words)) if a.words else transcribe(a.src, a.start, a.end)
    fixes = [f.split("=", 1) for f in a.fix]
    for w in words:
        for bad, good in fixes:
            w["w"] = re.sub(bad, good, w["w"], flags=re.I)
    json.dump(words, open(a.out + ".words.json", "w"))
    tmp = tempfile.mkdtemp(); ass = os.path.join(tmp, "c.ass")
    sfx = build_ass(words, a.top, dur, a.end_text, ass)
    linger = 1.4 if a.end_text else 0.6
    total = dur + linger
    pre = f"crop={a.crop}," if a.crop else ""
    z = zoom_expr(words, dur)
    bg = (f"[0:v]{pre}split[vm][vb];[vb]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,"
          f"boxblur=28:2,eq=brightness=-0.36:saturation=0.7,tpad=stop_mode=clone:stop_duration={linger}[bg];")
    if HOOK_STYLE == "classic":
        bg = f"[0:v]{pre}null[vm];color=black:s={W}x{H}:d={total}:r=30[bg];"
    vf = bg + (f"[vm]scale={VW*2}:{VH*2}:force_original_aspect_ratio=increase,crop={VW*2}:{VH*2},setsar=1,fps=30,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={VW}x{VH}:fps=30,"
          f"eq=contrast=1.10:saturation=1.06:gamma=0.97,vignette=PI/5,noise=alls=7:allf=t,"
          f"tpad=stop_mode=clone:stop_duration={linger}[v0];"
          f"[bg][v0]overlay=0:{VTOP}:shortest=1,ass={ass},format=yuv420p[v]")
    inputs = ["-ss", str(a.start), "-to", str(a.end), "-i", a.src,
              "-i", f"{a.assets}/pad.wav", "-i", f"{a.assets}/whoosh.wav", "-i", f"{a.assets}/impact.wav"]
    af = [f"[0:a]loudnorm=I=-14:TP=-1.5,apad=pad_dur={linger}[voice]",
          f"[1:a]atrim=0:{total},volume={a.music_db}dB,afade=t=in:d=1,afade=t=out:st={total-1.5}:d=1.5[mus]"]
    mix = ["[voice]", "[mus]"]
    nw = sum(1 for _, k in sfx if k == "whoosh"); ni = len(sfx) - nw
    if nw: af.append(f"[2:a]asplit={nw}" + "".join(f"[w{i}]" for i in range(nw)) if nw > 1 else "[2:a]anull[w0]")
    if ni: af.append(f"[3:a]asplit={ni}" + "".join(f"[i{i}]" for i in range(ni)) if ni > 1 else "[3:a]anull[i0]")
    wi = ii = 0
    for j, (t, k) in enumerate(sfx):
        ms = int(max(t - (0.35 if k == "whoosh" else 0.0), 0) * 1000)
        src = f"[w{wi}]" if k == "whoosh" else f"[i{ii}]"
        vol = -14 if k == "whoosh" else -12
        af.append(f"{src}volume={vol}dB,adelay={ms}|{ms}[s{j}]"); mix.append(f"[s{j}]")
        if k == "whoosh": wi += 1
        else: ii += 1
    af.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[a]")
    # 2026-11-25: v3 (full blurred bg + grain) hits the 10M cap -> 26-29 MB at ~22s, >30 MB past ~24s (precheck FAIL).
    # Budget the video bitrate from the length so any 15-35s reel lands <= ~27 MB.
    vkbps = int(min(10000, max(4000, 27e6 * 8 / total / 1000 - 250)))
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", vf + ";" + ";".join(af),
           "-map", "[v]", "-map", "[a]", "-t", str(total), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-maxrate", f"{vkbps}k", "-bufsize", f"{2*vkbps}k",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print("ok", a.out, f"{total:.1f}s", f"sfx={len(sfx)}")


if __name__ == "__main__":
    main()
