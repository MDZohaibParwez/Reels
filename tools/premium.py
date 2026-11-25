#!/usr/bin/env python3
"""premium.py — "premium podcast" reel renderer (style learned 2026-11-25 from Zohaib's references:
the Jensen Huang premium edit + the Mark Sut before/after reel).

    python3 tools/premium.py aroll.mp4 words.json scenes.json out.mp4

aroll.mp4  = full-bleed 1080x1920 speech edit (assemble.py with "size": [1080,1920]; per-piece "crop" w:h:x:y picked
             from frames so the speaker's face sits upper-middle; crop OFF any burned-in source subtitles)
words.json = plan_words.py output ([{"w","s","e"}], times in the aroll timeline)
scenes.json:
{
  "hook": "FaZe Rug [won] this house",      # RULE 1 hook, big from frame 0, [keyword] in serif italic accent
  "hook_end": 2.6,                          # seconds the hook stays
  "name": ["FaZe Rug", "YouTuber"],          # optional lower-third during the hook
  "accent": "auto" | "#3D7BFF",              # auto = picked from the footage (style fundamental #2)
  "special": ["house", "free"],              # words forced to be the big serif word in their caption
  "cards": [{"t0": 6.1, "t1": 8.0, "style": "paper"|"ink"|"pip", "text": "optional *special* override"},
            {"t0": 6.4, "t1": 7.9, "style": "pip", "src": "broll.mp4", "ss": 13, "speed": 6}],  # wide b-roll inset
  "punch": [[3.0, 4.6, 1.12]],               # punch-in zooms (t0, t1, zoom)
  "end_text": "House or $50K cash?",         # question shown the last ~2.2 s (loop/CTA)
  "music_db": -27
}
Style fundamentals (from the references): 2 fonts only (thin sans Inter Light + special serif Lora Bold Italic),
one accent colour from the footage (+ dark version, cream, near-black), textures (paper / halftone / film grain),
A-roll for talking & resting, full-screen cards for value lines, pip card (text top + video inset), SFX on every card.
"""
import argparse, json, os, re, subprocess, tempfile, colorsys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
IN = "/usr/share/fonts/opentype/inter/"
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
STOP = set("""a an the and or but so to of in on at for with from by is are was were be been am i you he she it we they me
him her us them my your his its our their this that these those there here what which who how why when where just like
really very do does did done have has had not no yes yeah oh okay ok um uh gonna wanna can could would should will
all any some more most much many if then than as about into out up down over also too get got go going one""".split())


def font(kind, size):
    if kind == "serif":
        f = ImageFont.truetype(LORA, size); f.set_variation_by_name("Bold Italic"); return f
    return ImageFont.truetype(IN + {"thin": "Inter-Light.otf", "med": "Inter-Medium.otf", "semi": "Inter-SemiBold.otf",
                                    "bold": "Inter-Bold.otf", "xbold": "Inter-ExtraBold.otf"}[kind], size)


def clean(w):
    return re.sub(r"[^\w$%'-]", "", w).lower()


def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def auto_accent(src, dur):
    """Style fundamental #2: pick the colour that stands out in the A-roll, make a bright + dark version."""
    hues = np.zeros(36)
    for t in np.linspace(0.5, max(dur - 0.5, 0.6), 10):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=72:128",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) < 72 * 128 * 3: continue
        hsv = cv2.cvtColor(np.frombuffer(raw, np.uint8).reshape(128, 72, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3).astype(float)
        m = (hsv[:, 1] > 80) & (hsv[:, 2] > 70)
        np.add.at(hues, (hsv[m, 0] / 5).astype(int) % 36, hsv[m, 1] / 255)
    if hues.sum() < 5: return (61, 123, 255)
    h = (np.argmax(np.convolve(np.r_[hues[-1], hues, hues[0]], [1, 2, 1], "valid")) * 10 + 5) / 360
    # 2026-11-25 test: accent = footage colour made text vanish on it (orange word on orange vest). Use the
    # complementary hue of the dominant colour -> the special word always pops off the A-roll.
    h = (h + 0.5) % 1.0
    if 0.08 < h < 0.17: h = 0.10  # muddy yellows/browns read badly as text -> warm orange
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.70, 1.0))


def darker(c, k=0.28):
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in c]); return tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h, min(1, s * 1.05), v * k))


# ---------------------------------------------------------------- text layout (positions fixed up front, words revealed)
def layout_tokens(tokens, maxw, gap=0.28, lead=1.18, align="center"):
    """tokens: [(text, font, fill, extra)] -> list of (x, baseline_y, text, font, fill, idx), total height. Baseline-aligned lines."""
    lines, cur, cw = [], [], 0
    for i, (t, f, c, ex) in enumerate(tokens):
        w = f.getlength(t); sp = f.size * gap
        if cur and (cw + sp + w > maxw or ex.get("br")):
            lines.append(cur); cur, cw = [], 0
        cw += (sp if cur else 0) + w; cur.append((i, t, f, c, w, sp))
    if cur: lines.append(cur)
    out, y = [], 0
    for ln in lines:
        asc = max(f.getmetrics()[0] for _, _, f, _, _, _ in ln); y += asc * (1 if not out else lead)
        lw = sum(w for *_, w, _ in ln) + sum(sp for *_, sp in ln[1:])
        x = (maxw - lw) / 2 if align == "center" else 0
        for k, (i, t, f, c, w, sp) in enumerate(ln):
            if k: x += sp
            out.append((x, y, t, f, c, i)); x += w
    return out, y


def draw_tokens(img, placed, ox, oy, visible, shadow=True, ages=None, box=None, stroke=0):
    """Draw revealed tokens. ages[i] = frames since the word appeared -> 3-frame rise + fade."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for x, y, t, f, c, i in placed:
        if i not in visible: continue
        a = ages.get(i, 99) if ages else 99
        k = min(1.0, (a + 1) / 4); dy = int((1 - k) * 22); al = int(255 * k)
        X, Y = ox + x, oy + y + dy
        if box and i in box:
            l, tp, r, b = d.textbbox((X, Y), t, font=f, anchor="ls")
            d.rounded_rectangle((l - 14, tp - 6, r + 14, b + 12), 10, fill=box[i] + (al,))
        if shadow: ds.text((X, Y + 4), t, font=f, fill=(0, 0, 0, int(al * 0.85)), anchor="ls", stroke_width=stroke + 4)
        d.text((X, Y), t, font=f, fill=c + (al,), anchor="ls", stroke_width=stroke, stroke_fill=(10, 10, 14, al))
    if shadow:
        sh = sh.filter(ImageFilter.GaussianBlur(9)); img.alpha_composite(sh)
    img.alpha_composite(lay)


# ---------------------------------------------------------------- captions (A-roll)
def chunk_words(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w); nxt = words[i + 1] if i + 1 < len(words) else None
        txt = " ".join(x["w"] for x in cur)
        if (len(cur) >= 3 or len(txt) >= 15 or re.search(r"[.,!?;:]$", w["w"]) or nxt is None or nxt["s"] - w["e"] > 0.35):
            out.append(cur); cur = []
    for k, c in enumerate(out):
        c_end = out[k + 1][0]["s"] if k + 1 < len(out) else c[-1]["e"] + 0.6
        for w in c: w["_end"] = min(c_end, c[-1]["e"] + 0.8)
    return out


def pick_special(chunk, forced):
    for f in forced:  # forced words in the order given in scenes.json (brand name first wins)
        for j, w in enumerate(chunk):
            if clean(w["w"]) == f: return j
    cands = [(len(clean(w["w"])), j) for j, w in enumerate(chunk) if clean(w["w"]) not in STOP and len(clean(w["w"])) >= 4]
    if any(re.search(r"\d", w["w"]) for w in chunk):  # numbers are always the special word
        return next(j for j, w in enumerate(chunk) if re.search(r"\d", w["w"]))
    return max(cands)[1] if cands else None


def caption_layout(chunk, sp, accent):
    toks = []
    for j, w in enumerate(chunk):
        if j == sp: toks.append((w["w"].strip(",."), font("serif", 128), accent, {"br": j > 0}))
        elif sp is None: toks.append((w["w"], font("xbold", 76), (255, 255, 255), {}))
        else: toks.append((w["w"], font("semi", 62), (255, 255, 255), {}))
    return layout_tokens(toks, 960)


# ---------------------------------------------------------------- backgrounds / textures
def grain_frames(n=6, amp=5.0):
    rng = np.random.default_rng(7)
    return [np.clip(rng.normal(0, amp, (H, W, 1)), -14, 14).astype(np.int16) for _ in range(n)]


def halftone(size, color, corner="br", maxr=9, step=26):
    w, h = size; im = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(0, h, step):
        for x in range(0, w, step):
            fx = x / w if "r" in corner else 1 - x / w; fy = y / h if "b" in corner else 1 - y / h
            r = maxr * max(0.0, (fx + fy - 0.9)) ** 1.4
            if r > 0.8: d.ellipse((x - r, y - r, x + r, y + r), fill=color)
    return im


def paper_bg(accent):
    rng = np.random.default_rng(3)
    base = np.ones((H, W, 3)) * np.array([238, 233, 219])
    low = cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 3)
    low = cv2.resize(low, (W, H))[..., None] * 7
    fib = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8)[..., None] * 4
    im = Image.fromarray(np.clip(base + low + fib, 0, 255).astype(np.uint8)).convert("RGBA")
    im.alpha_composite(halftone((W, H), (20, 20, 20, 26), "br"))
    ImageDraw.Draw(im).rectangle((W - 200, 150, W - 110, 160), fill=(222, 38, 38, 255))  # small red tab (Mark Sut reference)
    return im


def ink_bg(accent):
    dark = darker(accent, 0.22)
    g = np.linspace(0, 1, H)[:, None, None]
    base = np.array(dark) * (1 - g) + np.array([8, 9, 14]) * g
    im = Image.fromarray(np.broadcast_to(base, (H, W, 3)).astype(np.uint8)).convert("RGBA")
    im.alpha_composite(halftone((W, H), accent + (40,), "bl", maxr=7, step=22))
    return im


def orb(accent, r, pulse):
    s = int(r * 2.6); im = np.zeros((s, s, 4), np.float32); yy, xx = np.mgrid[0:s, 0:s]
    d = np.hypot(xx - s / 2, yy - s / 2) / (r * (1 + 0.04 * pulse))
    a = np.clip(1.25 - d, 0, 1) ** 2.2
    core = np.clip(1 - d * 2.4, 0, 1)
    rgb = np.array(accent, np.float32) * (1 - core[..., None]) + 255 * core[..., None]
    im[..., :3] = rgb; im[..., 3] = a * 255
    return Image.fromarray(im.astype(np.uint8), "RGBA")


def gradient_top(h=900, a=0.72):
    al = (np.linspace(a, 0, h) ** 1.3 * 255).astype(np.uint8)
    arr = np.zeros((h, W, 4), np.uint8); arr[..., 3] = al[:, None]
    return Image.fromarray(arr, "RGBA")


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("aroll"); ap.add_argument("words"); ap.add_argument("scenes"); ap.add_argument("out")
    ap.add_argument("--assets", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))
    ap.add_argument("--preview", help="comma list of seconds -> write PNG frames only (fast look before a full render;\n                    pip b-roll frames are not exact in preview)")
    a = ap.parse_args()
    S = json.load(open(a.scenes)); words = json.load(open(a.words))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.aroll],
                               capture_output=True, text=True).stdout)
    acc = hexrgb(S["accent"]) if S.get("accent", "auto") != "auto" else auto_accent(a.aroll, dur)
    print("accent", "#%02X%02X%02X" % acc)
    forced = [clean(x) for x in S.get("special", [])]
    cards = sorted(S.get("cards", []), key=lambda c: c["t0"])
    hook_end = S.get("hook_end", 2.6); end_text = S.get("end_text", ""); end_t = dur - 2.2

    # captions: words inside cards are shown by the card, not as captions
    in_card = lambda t: any(c["t0"] - 0.05 <= t < c["t1"] for c in cards)
    cap_words = [w for w in words if not in_card(w["s"])]
    chunks = chunk_words(cap_words)
    caps = []
    for c in chunks:
        sp = pick_special(c, forced)
        placed, hgt = caption_layout(c, sp, acc)
        caps.append((c, placed, hgt))

    # hook layout
    htoks = []
    for t in re.findall(r"\[[^\]]+\]|[^\s\[\]]+", S["hook"]):
        if t.startswith("["): htoks.append((t[1:-1], font("serif", 156), acc, {}))
        else: htoks.append((t, font("xbold", 92), (255, 255, 255), {}))
    hook_placed, hook_h = layout_tokens(htoks, 940)
    etoks = [(t, font("xbold", 74), (255, 255, 255), {}) for t in end_text.split()]
    end_placed, end_h = layout_tokens(etoks, 920) if end_text else ([], 0)

    # cards
    bgs = {"paper": paper_bg(acc), "ink": ink_bg(acc), "pip": paper_bg(acc)}
    for c in cards:
        st = c.get("style", "paper")
        if c.get("text"):
            raw = c["text"].split(); n = len(raw); span = (c["t1"] - c["t0"]) * 0.6
            cw = [{"w": x.strip("*"), "s": c["t0"] + span * i / max(n, 1), "sp": x.startswith("*")} for i, x in enumerate(raw)]
        else:
            cw = [dict(w) for w in words if c["t0"] - 0.05 <= w["s"] < c["t1"]]
            sp = pick_special(cw, forced) if cw else None
            for j, w in enumerate(cw): w["sp"] = j == sp
        # Mark Sut / Jensen cards: ONE short phrase at a time (2-3 words), big, special word in serif.
        for w in cw: w.setdefault("e", w["s"] + 0.25)
        ink = (255, 255, 255) if st == "ink" else (18, 18, 18)
        size = {"paper": 118, "pip": 98, "ink": 104}[st]
        groups = []
        for ch in chunk_words([dict(w) for w in cw]):
            spj = next((j for j, w in enumerate(ch) if w.get("sp")), None)
            if spj is None: spj = pick_special(ch, forced)
            toks = []
            for j, w in enumerate(ch):
                if j == spj:
                    toks.append((w["w"].strip(",."), font("serif", int(size * 1.55)) if st != "ink" else font("bold", size),
                                 darker(acc, 0.55) if st != "ink" else (255, 255, 255), {"br": j > 0 and st != "ink"}))
                else:
                    toks.append((w["w"], font("bold" if st != "ink" else "thin", size), ink, {}))
            placed, hgt = layout_tokens(toks, 880, gap=0.26, lead=1.05, align="left" if st != "ink" else "center")
            box = {spj: acc} if st == "ink" and spj is not None else None
            groups.append((ch, placed, hgt, box))
        c["_groups"] = groups

    punches = S.get("punch", [])
    grains = grain_frames()
    yy, xx = np.mgrid[0:H, 0:W]
    vign = (1 - 0.38 * np.clip((np.hypot((xx - W / 2) / (W * 0.75), (yy - H * 0.42) / (H * 0.62))) - 0.35, 0, 1) ** 1.6)[..., None]
    lut = np.clip((np.arange(256) / 255 - 0.5) * 1.1 + 0.5 + 0.01, 0, 1) * 255
    topgrad = gradient_top()
    mask_pip = rounded_mask(900, 1000, 40); mask_wide = rounded_mask(940, 530, 34)
    name = S.get("name")

    tmp = tempfile.mkdtemp(); vid = os.path.join(tmp, "v.mp4")
    total = dur
    vkbps = max(3000, min(10000, int(27 * 8000 / total) - 250))
    times = [float(x) for x in a.preview.split(",")] if a.preview else None
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.aroll, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = None if times else subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-maxrate", f"{vkbps}k", "-bufsize", f"{2 * vkbps}k",
         "-g", "30", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    nfr = int(round(dur * FPS)); fi = 0; prev_card_end = -9
    while fi < nfr:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        t = fi / FPS
        if times and not any(abs(t - x) < 0.5 / FPS for x in times): fi += 1; continue
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        # ---- A-roll grade + punch / re-entry zoom
        z = 1.0
        for p0, p1, zz in punches:
            if p0 <= t < p1: z = zz
        since = t - prev_card_end
        if 0 <= since < 0.22: z *= 1 + 0.07 * (1 - since / 0.22) ** 2
        if z != 1.0:
            M = cv2.getRotationMatrix2D((W / 2, H * 0.4), 0, z); fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR)
        base = lut[fr].astype(np.float32) * vign
        img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
        # ---- card?
        card = next((c for c in cards if c["t0"] <= t < c["t1"]), None)
        if card:
            st = card.get("style", "paper"); k = min(1.0, (t - card["t0"]) / 0.13)
            cv = bgs[st].copy()
            if st == "ink":
                o = orb(acc, 170, np.sin(t * 3)); cv.alpha_composite(o, (W // 2 - o.width // 2, 1180 - o.height // 2))
            if st == "pip" and card.get("src"):
                # wide b-roll inset (e.g. the whole home / the lot) from its own source, 16:9 at full width
                if card.get("_dec") is None:
                    card["_dec"] = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(card["ss"]), "-i", card["src"], "-vf",
                                                     f"setpts=PTS/{card.get('speed', 1)},fps={FPS},scale=940:530:force_original_aspect_ratio=increase,crop=940:530",
                                                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
                pb = card["_dec"].stdout.read(940 * 530 * 3)
                if len(pb) == 940 * 530 * 3: card["_last"] = Image.fromarray(np.frombuffer(pb, np.uint8).reshape(530, 940, 3))
                shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(shadow).rounded_rectangle((76, 996, 1016, 1526), 34, fill=(0, 0, 0, 95))
                cv.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
                if card.get("_last") is not None: cv.paste(card["_last"], (70, 980), mask_wide)
            elif st == "pip":
                src = Image.fromarray(fr[260:1460, :, :]).resize((900, 1000)).convert("RGBA")
                shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(shadow).rounded_rectangle((96, 846, 996, 1846), 40, fill=(0, 0, 0, 90))
                cv.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
                cv.paste(src, (90, 820), mask_pip)
            g = [x for x in card["_groups"] if x[0][0]["s"] - 0.04 <= t] or card["_groups"][:1]
            ch, placed, hgt, box = g[-1]
            if st == "pip" and card.get("src"): oy = 900 - hgt - 30
            elif st == "pip": oy = 520 - hgt / 2
            else: oy = 900 - hgt / 2
            vis = {j for j, w in enumerate(ch) if w["s"] <= t + 0.04}
            ages = {j: int((t - w["s"]) * FPS) for j, w in enumerate(ch)}
            draw_tokens(cv, placed, 100, oy, vis, shadow=st == "ink", ages=ages, box=box)
            if k < 1:
                sc = 1.05 - 0.05 * k
                cs = cv.resize((int(W * sc), int(H * sc))).crop((int((W * sc - W) / 2), int((H * sc - H) / 2),
                                                                  int((W * sc - W) / 2) + W, int((H * sc - H) / 2) + H))
                img = Image.blend(img, cs, k)
            else:
                img = cv
            if t + 1 / FPS >= card["t1"]: prev_card_end = card["t1"]
        else:
            # ---- captions
            for c, placed, hgt in caps:
                if c[0]["s"] - 0.02 <= t < c[-1]["_end"]:
                    vis = {j for j, w in enumerate(c) if w["s"] <= t + 0.04}
                    ages = {j: int((t - w["s"]) * FPS) for j, w in enumerate(c)}
                    draw_tokens(img, placed, 60, 1330 - hgt, vis, ages=ages, stroke=3)
                    break
        # ---- hook (frame 0, fully visible on frame 0)
        if t < hook_end + 0.2:
            al = 1.0 if t < hook_end else 1 - (t - hook_end) / 0.2
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ov.alpha_composite(topgrad)
            draw_tokens(ov, hook_placed, 70, 300, set(range(len(htoks))), ages=None, stroke=4)
            if name and 0.3 < t:
                d = ImageDraw.Draw(ov); y0 = 1500
                d.rectangle((70, y0, 77, y0 + 74), fill=acc + (255,))
                d.text((96, y0 + 34), name[0], font=font("bold", 46), fill=(255, 255, 255, 255), anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0))
                if len(name) > 1: d.text((96, y0 + 74), name[1], font=font("med", 34), fill=(225, 225, 225, 255), anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0))
            if al < 1: ov.putalpha(ov.getchannel("A").point(lambda v: int(v * al)))
            img.alpha_composite(ov)
        # ---- end question
        if end_placed and t >= end_t and not card:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ov.alpha_composite(topgrad)
            ages = {i: int((t - end_t) * FPS) for i in range(len(etoks))}
            draw_tokens(ov, end_placed, 80, 360, set(range(len(etoks))), ages=ages, stroke=3)
            ImageDraw.Draw(ov).text((W / 2, 380 + end_h + 70), "@mictalkclips", font=font("bold", 40),
                                    fill=acc + (255,), anchor="ms")
            img.alpha_composite(ov)
        out = np.asarray(img.convert("RGB")).astype(np.int16) + grains[fi % len(grains)]
        out = np.clip(out, 0, 255).astype(np.uint8)
        if times:
            Image.fromarray(out).save(f"{a.out}_{t:05.2f}.png")
        else:
            enc.stdin.write(out.tobytes())
        fi += 1
    dec.stdout.close(); dec.wait()
    if times: print("preview frames written"); return
    enc.stdin.close(); enc.wait()

    # ---- audio: voice + low original pad + whoosh on every card / hook exit (all generated, copyright-free)
    for f in ("whoosh.wav", "pad.wav", "impact.wav"):
        if not os.path.exists(os.path.join(a.assets, f)):
            subprocess.run(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx.py"), a.assets], check=True)
            break
    hits = [max(c["t0"] - 0.18, 0) for c in cards] + [hook_end - 0.1]
    inputs = ["-i", a.aroll, "-stream_loop", "-1", "-i", os.path.join(a.assets, "pad.wav")]
    for k in hits: inputs += ["-i", os.path.join(a.assets, "whoosh.wav")]
    mixed = os.path.join(tmp, "mix.mp4")
    # (explicit index map: 0 = rendered video, 1 = aroll audio, 2 = pad, 3.. = whooshes)
    fl = [f"[1:a]aformat=channel_layouts=stereo,aresample=44100[v]",
          f"[2:a]atrim=0:{dur},volume={S.get('music_db', -27)}dB,afade=t=out:st={max(dur - 1.2, 0)}:d=1.2[m]"]
    mix = "[v][m]"
    for k, h0 in enumerate(hits):
        fl.append(f"[{k + 3}:a]volume=-9dB,adelay={int(h0 * 1000)}|{int(h0 * 1000)}[w{k}]"); mix += f"[w{k}]"
    fl.append(f"{mix}amix=inputs={len(hits) + 2}:normalize=0:duration=first[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid] + inputs + ["-filter_complex", ";".join(fl), "-map", "0:v",
                    "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur}", mixed], check=True)
    subprocess.run(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "loudfix.py"), mixed, a.out], check=True)
    print("rendered", a.out)


if __name__ == "__main__":
    main()
