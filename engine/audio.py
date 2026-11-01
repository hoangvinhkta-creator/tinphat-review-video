"""Bước 4 — tạo hiệu ứng âm thanh (build/sfx.wav) theo build/events.json và nhạc nền quảng cáo (build/music.wav).
Tất cả được tổng hợp bằng code (không cần thư viện âm thanh, không vướng bản quyền).
Nhạc: vòng hợp âm I–V–vi–IV, kick/clap/hat/bass/pluck/pad, dồn trống + tiếng vút trước màn kết, hợp âm kết ngân khi hết lời.
project.json → "music": {"bpm", "key" (dịch nửa cung, 0 = Đô trưởng), "seed", "enabled"}."""
import sys, json, wave
import numpy as np
from scipy.signal import butter, sosfilt
from common import Project

SR = 48000
SFX_LEAD = 0.06   # đặt tiếng sớm 60 ms để không đè lên đầu âm tiết của lời dẫn


def main(path):
    pr = Project(path)
    ev = json.load(open(pr.b('events.json')))
    info = json.load(open(pr.b('info.json')))
    DUR = float(ev['duration']); N = int(SR * DUR)
    mcfg = pr.cfg['music']
    rng = np.random.default_rng(int(mcfg.get('seed', 7)))

    def tt(d): return np.arange(int(SR * d)) / SR
    def bp(x, lo, hi): return sosfilt(butter(2, [lo, min(hi, SR / 2 - 200)], 'bandpass', fs=SR, output='sos'), x)
    def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
    def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
    def mtof(m): return 440 * 2 ** ((m - 69) / 12)

    def place(buf, t0, sig, gain=1.0, pan=0.0):
        i = int(max(0, t0) * SR)
        if i >= N: return
        sig = sig[: N - i] * gain
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        buf[0, i:i + len(sig)] += sig * l * 1.414; buf[1, i:i + len(sig)] += sig * r * 1.414

    # ---------- âm thanh hiệu ứng ----------
    def pop(f=700, d=.12):
        t = tt(d); fr = f * (1 + 1.2 * np.exp(-t / .012))
        return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / .035) * (1 - np.exp(-t / .002))
    def whoosh(d=.5, lo=300, hi=5000, peak=.6):
        t = tt(d); n = rng.standard_normal(len(t))
        env = np.where(t < d * peak, (t / (d * peak)) ** 2, np.exp(-(t - d * peak) / (d * (1 - peak) / 3)))
        out = np.zeros_like(n); segs = 8
        for k in range(segs):
            a, b = int(len(t) * k / segs), int(len(t) * (k + 1) / segs); c = lo * (hi / lo) ** np.sin(np.pi * (k + .5) / segs)
            out[a:b] = bp(n, c * .6, c * 1.6)[a:b]
        return out * env * .6
    def ding(f=1320, d=1.0):
        t = tt(d); s = np.zeros_like(t)
        for mult, amp, dec in [(1, 1, .45), (2.0, .35, .25), (3.01, .18, .15), (4.2, .08, .08)]:
            s += amp * np.sin(2 * np.pi * f * mult * t) * np.exp(-t / dec)
        return s * (1 - np.exp(-t / .003)) * .5
    def tick():
        t = tt(.03); return hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / .004) * .5
    def thump(f=90, d=.3):
        t = tt(d); fr = f * (1 + 2 * np.exp(-t / .02))
        return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / .09) + lp(rng.standard_normal(len(t)), 1500) * np.exp(-t / .015) * .4
    def sparkle(d=.8):
        s = np.zeros(int(SR * d))
        for k in range(7):
            f = rng.uniform(2600, 4200); t0 = k * .07 + rng.uniform(0, .03); tb = tt(.25)
            b = np.sin(2 * np.pi * f * tb) * np.exp(-tb / .06) * .35; i = int(t0 * SR); s[i:i + len(b)] += b[: len(s) - i]
        return s
    def riser(d=2.0):
        t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n); segs = 16
        for k in range(segs):
            a, b = int(len(t) * k / segs), int(len(t) * (k + 1) / segs); c = 400 * 20 ** (k / segs); out[a:b] = bp(n, c * .7, c * 1.4)[a:b]
        return out * (t / d) ** 2 * .5

    sfx = np.zeros((2, N)); end_t = None
    for e in ev['sfx']:
        k, t0, gain, pan = e['kind'], e['t'] - SFX_LEAD, e.get('gain', 1.0), e.get('pan', 0.0)
        if k == 'mark_end': end_t = e['t']; continue
        sig = {'pop': lambda: pop(e.get('f', 700), e.get('d', .12)), 'whoosh': lambda: whoosh(e.get('d', .5), e.get('lo', 300), e.get('hi', 5000)),
               'ding': lambda: ding(e.get('f', 1320), e.get('d', 1.0)), 'tick': tick, 'thump': lambda: thump(e.get('f', 90), e.get('d', .3)),
               'sparkle': sparkle}.get(k)
        if sig: place(sfx, t0, sig(), gain, pan)

    # ---------- nhạc nền ----------
    mus = np.zeros((2, N))
    if mcfg.get('enabled', True):
        BPM = float(mcfg.get('bpm', 120)); KEY = int(mcfg.get('key', 0))
        BEAT = 60 / BPM; BAR = 4 * BEAT; S16 = BEAT / 4
        CH = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]; ROOT = [36, 43, 45, 41]
        CH = [[m + KEY for m in c] for c in CH]; ROOT = [m + KEY for m in ROOT]
        def kick():
            t = tt(.35); fr = 48 + 110 * np.exp(-t / .03)
            return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / .16) * (1 - np.exp(-t / .001))
        def clap():
            t = tt(.2); n = bp(rng.standard_normal(len(t)), 900, 5000); e = np.zeros_like(t)
            for o in (0, .011, .022): e += np.where(t >= o, np.exp(-(t - o) / (.008 if o < .02 else .06)), 0)
            return n * e * .5
        def hat(open_=False):
            t = tt(.18 if open_ else .05); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / (.06 if open_ else .012)) * .35
        def pluck(notes, d=.35, cutoff=2200):
            t = tt(d); s = np.zeros_like(t)
            for m in notes:
                for det in (-.006, .006):
                    f = mtof(m) * (1 + det); s += 2 * ((t * f) % 1) - 1
            return lp(s, cutoff) * np.exp(-t / .12) * (1 - np.exp(-t / .002)) / len(notes) * .6
        def bass(m, d):
            t = tt(d); f = mtof(m); s = np.sin(2 * np.pi * f * t) + .3 * lp(2 * ((t * f) % 1) - 1, 400)
            return s * np.minimum(1, np.exp(-(t - d * .7) / .03)) * (1 - np.exp(-t / .004)) * .55
        def pad(notes, d):
            t = tt(d); s = sum(np.sin(2 * np.pi * mtof(m) * t + k) for k, m in enumerate(notes)) / len(notes)
            return s * np.minimum(1, t / .4) * np.minimum(1, np.maximum(0, d - t) / .4) * .22
        M = lambda t0, s, g=1, pan=0: place(mus, t0, s, g, pan)
        voice_end = float(info.get('voice', DUR - 1.2))
        final_t = np.ceil((voice_end - .3) / BEAT) * BEAT          # hợp âm kết ngay khi gần hết lời
        roll_bar = int(end_t // BAR) - 1 if end_t else -1           # ô nhịp có dồn trống (trước màn kết)
        b = 0
        while b * BAR < final_t:
            t0 = b * BAR; ci = b % 4; intro = b < 1; bar_end = min(t0 + BAR, final_t)
            M(t0, pad(CH[ci], bar_end - t0), .9)
            for beat in range(4):
                tb = t0 + beat * BEAT
                if tb >= final_t: break
                if not intro: M(tb, kick(), .95)
                if beat in (1, 3) and not intro: M(tb, clap(), .8, .1)
                M(tb + BEAT / 2, hat(open_=(beat == 3)), .8, .25)
                if not intro: M(tb + S16 * 3, hat(), .35, -.25)
            for s16 in (0, 3, 6, 8, 10, 13):
                ts = t0 + s16 * S16
                if ts < final_t: M(ts, pluck(CH[ci] if s16 % 8 else CH[ci] + [CH[ci][0] + 12], .3, 1800 if intro else 2200), .9, -.15 if s16 % 2 else .15)
            if not intro:
                for e8 in range(8):
                    ts = t0 + e8 * BEAT / 2
                    if ts < final_t: M(ts, bass(ROOT[ci] + (12 if e8 in (3, 7) else 0), BEAT / 2 * .9), 1.0)
            if b == roll_bar:
                for k in range(8):
                    ts = t0 + BAR / 2 + k * S16
                    if ts < final_t: M(ts, clap(), .25 + .07 * k)
            b += 1
        if end_t: M(end_t - 2.0, riser(2.0), .5)
        tail = DUR - final_t
        if tail > .2:
            c = [48 + KEY, 55 + KEY, 60 + KEY, 64 + KEY, 67 + KEY]
            M(final_t, pad(c, tail), 1.2); M(final_t, pluck(c[2:] + [c[2] + 12], min(1.5, tail), 2600), 1.0); M(final_t, kick(), .9); M(final_t, bass(36 + KEY, min(1.4, tail)), 1.0)
        fade = np.ones(N); fi = int(.25 * SR); fade[:fi] = np.linspace(0, 1, fi); fo = min(int(1.2 * SR), N // 4); fade[-fo:] = np.linspace(1, 0, fo)
        mus *= fade

    def write(name, x):
        pk = np.abs(x).max()
        if pk > 0: x = x / pk * 10 ** (-1 / 20)
        with wave.open(name, 'w') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x.T * 32767).astype('<i2').tobytes())
    write(pr.b('sfx.wav'), sfx); write(pr.b('music.wav'), mus)
    print(f'✓ build/sfx.wav ({len(ev["sfx"])} hiệu ứng), build/music.wav ({"tắt" if not mcfg.get("enabled", True) else str(mcfg.get("bpm", 120)) + " BPM"})')


if __name__ == '__main__':
    main(sys.argv[1])
