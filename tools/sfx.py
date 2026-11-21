#!/usr/bin/env python3
"""Generate original (copyright-free) audio assets: whoosh, soft impact, cinematic pad bed."""
import numpy as np, wave, sys, os

SR = 44100


def save(path, x):
    x = np.clip(x, -1, 1)
    x = np.stack([x, x], 1) if x.ndim == 1 else x
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def lowpass(x, cutoff):
    # one-pole lowpass, cutoff may be array
    a = np.exp(-2 * np.pi * np.asarray(cutoff) / SR) * np.ones_like(x)
    y = np.zeros_like(x); p = 0.0
    for i in range(len(x)):
        p = (1 - a[i]) * x[i] + a[i] * p; y[i] = p
    return y


def whoosh(d=0.7):
    n = int(SR * d); t = np.arange(n) / SR
    noise = np.random.default_rng(1).standard_normal(n)
    sweep = 300 + 5000 * np.sin(np.pi * t / d) ** 2
    x = lowpass(noise, sweep) - lowpass(noise, sweep * 0.25)
    env = np.sin(np.pi * t / d) ** 1.5
    return 0.9 * x * env / (np.abs(x * env).max() + 1e-9)


def impact(d=1.2):
    n = int(SR * d); t = np.arange(n) / SR
    f = 55 + 70 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    click = np.random.default_rng(2).standard_normal(n) * np.exp(-t * 60) * 0.3
    tail = lowpass(np.random.default_rng(3).standard_normal(n), 600) * np.exp(-t * 3) * 0.6
    x = body + click + tail
    return 0.9 * x / np.abs(x).max()


def pad(dur=60, bpm=70):
    # slow emotional progression Am - F - C - G with soft piano-ish plucks + string pad
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    bar = 4 * 60 / bpm
    n = int(SR * dur); t = np.arange(n) / SR
    out = np.zeros(n)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    k = 0; start = 0.0
    while start < dur:
        ch = chords[k % 4]
        s0 = int(start * SR); s1 = min(n, int((start + bar + 1.5) * SR))
        tt = np.arange(s1 - s0) / SR
        env = np.minimum(tt / 1.2, 1) * np.exp(-np.maximum(tt - bar, 0) * 3)
        for m in ch + [ch[0] - 12]:
            f = hz(m)
            v = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.3)
                 + 0.15 * np.sin(2 * np.pi * f * 1.003 * tt))
            out[s0:s1] += 0.12 * v * env
        # piano-ish arpeggio notes on each beat
        for b in range(4):
            m = ch[b % 3] + 12; f = hz(m)
            p0 = int((start + b * bar / 4) * SR); p1 = min(n, p0 + int(1.5 * SR))
            if p0 >= n: break
            tp = np.arange(p1 - p0) / SR
            out[p0:p1] += 0.10 * (np.sin(2 * np.pi * f * tp) + 0.4 * np.sin(4 * np.pi * f * tp)) * np.exp(-tp * 3)
        start += bar; k += 1
    out = lowpass(out, 2500)
    fade = np.minimum(t / 2, 1) * np.minimum((dur - t) / 2, 1)
    out *= fade
    return 0.8 * out / np.abs(out).max()


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(d, exist_ok=True)
    save(f"{d}/whoosh.wav", whoosh())
    save(f"{d}/impact.wav", impact())
    save(f"{d}/pad.wav", pad(90))
    print("assets ok")
