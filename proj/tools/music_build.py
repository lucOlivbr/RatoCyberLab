# -*- coding: utf-8 -*-
"""Gera 5 trilhas chiptune (estilo jogos antigos) em assets/music/*.ogg.
Sintese propria (onda quadrada, triangulo, serra e ruido). Uso: python3 tools/music_build.py"""
import os, subprocess, wave
import numpy as np

SR = 22050
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "music")
rng = np.random.default_rng(7)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def wavef(kind, ph, duty=0.5):
    if kind == "sq":
        return np.where((ph % 1.0) < duty, 1.0, -1.0)
    if kind == "tri":
        return 4 * np.abs((ph % 1.0) - 0.5) - 1.0
    if kind == "saw":
        return 2 * (ph % 1.0) - 1.0
    return np.sin(2 * np.pi * ph)


def note(m, dur, kind="sq", vol=0.25, duty=0.5, decay=6.0, vib=0.0, slide=0.0, attack=0.004):
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    f = hz(m) * 2 ** ((slide * t / max(dur, 1e-3)) / 12.0)
    if vib:
        f = f * (1 + 0.012 * np.sin(2 * np.pi * vib * t))
    ph = np.cumsum(f) / SR
    env = np.exp(-decay * t / max(dur, 1e-3)) * np.minimum(1.0, t / attack)
    env *= np.minimum(1.0, (dur - t) / 0.01 + 0.0)
    return wavef(kind, ph, duty) * env * vol


def noise(dur, vol=0.2, decay=30.0, lo=False):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.uniform(-1, 1, n)
    if lo:
        x = np.convolve(x, np.ones(6) / 6, mode="same")
    return x * np.exp(-decay * t) * vol


def kick(vol=0.5):
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 28) + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * vol


class Track:
    def __init__(self, bpm, bars):
        self.step = 60.0 / bpm / 4.0
        self.steps = bars * 16
        self.buf = np.zeros(int((self.steps * self.step + 0.6) * SR))

    def put(self, step, sig):
        i = int(step * self.step * SR)
        e = min(len(self.buf), i + len(sig))
        self.buf[i:e] += sig[:e - i]

    def render(self):
        n = int(self.steps * self.step * SR)
        out = self.buf[:n].copy()
        tail = self.buf[n:]
        out[:len(tail)] += tail           # cauda volta ao inicio: loop sem corte
        out = np.tanh(out * 1.1)
        return (out * 0.85 * 32767).astype(np.int16)


def chord(root, kind):
    return {"m": [0, 3, 7, 12], "M": [0, 4, 7, 12], "7": [0, 4, 7, 10], "d": [0, 3, 6, 12], "5": [0, 7, 12, 19], "m7": [0, 3, 7, 10]}[kind] and [root + i for i in {"m": [0, 3, 7, 12], "M": [0, 4, 7, 12], "7": [0, 4, 7, 10], "d": [0, 3, 6, 12], "5": [0, 7, 12, 19], "m7": [0, 3, 7, 10]}[kind]]


import sys
ONLY = sys.argv[1] if len(sys.argv) > 1 else None


def build(name, bpm, prog, arp, arp_kind, arp_duty, bass, bass_kind, drums, lead_a, lead_b, lead_kind, lead_vol, extra=None, bars=16):
    if ONLY and name != ONLY:
        return
    T = Track(bpm, bars)
    st = T.step
    for bar in range(bars):
        root, kind = prog[bar % len(prog)]
        ch = chord(root, kind)
        base = bar * 16
        # arpejo
        for k, idx in enumerate(arp):
            if idx is None:
                continue
            m = ch[idx % 4] + 12 * (idx // 4) + 12
            T.put(base + k, note(m, st * 1.6, arp_kind, 0.11, arp_duty, 7.0))
        # baixo
        for k, (off, ln) in bass.items():
            T.put(base + k, note(root - 12 + off, st * ln, bass_kind, 0.30, 0.5, 2.5))
        # bateria
        for k, d in drums.items():
            if d == "k":
                T.put(base + k, kick(0.45))
            elif d == "s":
                T.put(base + k, noise(0.12, 0.26, 24))
            elif d == "h":
                T.put(base + k, noise(0.04, 0.12, 60))
        # melodia (a partir da barra 4: A, B alternando)
        if bar >= 4:
            phrase = lead_a if ((bar - 4) // 4) % 2 == 0 else lead_b
            if bar % 4 == 0 or True:
                pass
            seq = phrase[bar % 4]
            pos = 0
            for m, ln, fx in seq:
                if m is not None:
                    T.put(base + pos, note(m, st * ln * 0.95, lead_kind, lead_vol, 0.25 if lead_kind == "sq" else 0.5,
                                           3.0, vib=5.0 if fx == "v" else 0.0, slide=-12.0 if fx == "z" else 0.0))
                pos += ln
        if extra:
            extra(T, bar, base, ch)
    sig = T.render()
    os.makedirs(OUT, exist_ok=True)
    wp = os.path.join(OUT, name + ".wav")
    with wave.open(wp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(sig.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wp, "-c:a", "libvorbis", "-q:a", "3", os.path.join(OUT, name + ".ogg")], check=True)
    os.remove(wp)
    print(name, round(len(sig) / SR, 1), "s")


def mk(seqs):
    """seqs: lista de 4 barras, cada uma lista de (midi|None, passos, fx)"""
    return [[(m, l, (f[0] if f else "")) for (m, l, *f) in bar] for bar in seqs]


A = 57  # A3
# 1) LABORATORIO (salas 0, 1, 2 e menu): calma, misteriosa
lab_a = mk([[(76, 6), (74, 2), (72, 8)], [(69, 4), (72, 4), (77, 8)], [(76, 6), (72, 2), (79, 8)], [(74, 6), (71, 2), (67, 8)]])
lab_b = mk([[(72, 4), (76, 4), (81, 8)], [(77, 6), (76, 2), (72, 8)], [(79, 4), (76, 4), (72, 4), (76, 4)], [(74, 8), (71, 4), (67, 4)]])
build("lab", 96, [(57, "m"), (53, "M"), (48, "M"), (55, "M")],
      [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 1, 2, 1], "sq", 0.25,
      {0: (0, 6), 8: (0, 4), 12: (7, 4)}, "tri", {0: "k", 8: "k", 4: "h", 12: "h", 10: "h", 2: "h"},
      lab_a, lab_b, "sq", 0.17, bars=16)

# 2) ENERGIA (sala 3): eletrica, rapida, com "zaps"
en_a = mk([[(88, 2, "z"), (None, 2), (86, 2, "z"), (None, 2), (83, 4, "v"), (None, 4)],
           [(84, 2, "z"), (None, 2), (88, 2, "z"), (None, 2), (91, 4, "v"), (None, 4)],
           [(86, 2, "z"), (None, 2), (90, 2, "z"), (None, 2), (93, 4, "v"), (None, 4)],
           [(83, 2, "z"), (None, 2), (86, 2, "z"), (None, 2), (95, 8, "v")]])
en_b = mk([[(88, 1), (88, 1), (None, 2), (91, 1), (91, 1), (None, 2), (95, 2, "z"), (None, 6)],
           [(84, 1), (84, 1), (None, 2), (88, 1), (88, 1), (None, 2), (91, 2, "z"), (None, 6)],
           [(86, 1), (86, 1), (None, 2), (90, 1), (90, 1), (None, 2), (93, 2, "z"), (None, 6)],
           [(95, 2, "z"), (93, 2, "z"), (90, 2, "z"), (86, 2, "z"), (83, 8)]])


def zaps(T, bar, base, ch):
    for k in (3, 7, 11, 15):
        if (bar + k) % 3 == 0:
            T.put(base + k, noise(0.09, 0.22, 25) * np.sign(np.sin(np.arange(int(0.09 * SR)) * 0.9 + 1)))


build("energia", 150, [(52, "m"), (48, "M"), (50, "M"), (47, "7")],
      [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 1, 2, 3], "sq", 0.125,
      {0: (0, 2), 2: (0, 2), 4: (0, 2), 6: (0, 2), 8: (0, 2), 10: (0, 2), 12: (7, 2), 14: (0, 2)}, "saw",
      {0: "k", 4: "s", 8: "k", 12: "s", 2: "h", 6: "h", 10: "h", 14: "h"},
      en_a, en_b, "sq", 0.14, extra=zaps, bars=16)

# 3) MUTACAO / QUIMICA (salas 4, 5, 8): lenta, estranha, bolhas
mu_a = mk([[(74, 8, "v"), (73, 8, "v")], [(75, 8, "v"), (74, 8, "v")], [(74, 6, "v"), (77, 2), (76, 8, "v")], [(69, 16, "v")]])
mu_b = mk([[(81, 8, "v"), (80, 8, "v")], [(79, 8, "v"), (77, 8, "v")], [(76, 6, "v"), (74, 2), (73, 8, "v")], [(69, 8, "v"), (None, 8)]])


def bubbles(T, bar, base, ch):
    for k in range(16):
        if rng.random() < 0.22:
            T.put(base + k, note(int(rng.integers(79, 94)), 0.12, "sin", 0.13, 0.5, 6.0, slide=8.0))


build("mutacao", 78, [(50, "m"), (51, "M"), (50, "m"), (45, "7")],
      [0, 2, 1, 3, 0, 2, 1, 3, 0, 2, 1, 3, 2, 1, 3, 1], "tri", 0.5,
      {0: (0, 8), 8: (1 if False else 0, 6), 12: (-5, 4)}, "tri", {0: "k", 8: "k", 6: "h", 14: "h"},
      mu_a, mu_b, "tri", 0.22, extra=bubbles, bars=16)

# 4) SEGURANCA / ROBOTICA (salas 6, 7 e 9): furtiva, sirene e robos (versao 2)
se_a = mk([[(81, 4, "v"), (76, 4, "v"), (81, 4, "v"), (76, 4, "v")],
           [(79, 4, "v"), (74, 4, "v"), (79, 4, "v"), (74, 4, "v")],
           [(77, 4, "v"), (72, 4, "v"), (77, 4, "v"), (72, 4, "v")],
           [(78, 4, "v"), (73, 4, "v"), (81, 8, "z")]])
se_b = mk([[(74, 2), (77, 2), (81, 2), (77, 2), (86, 4), (None, 4)],
           [(74, 2), (77, 2), (79, 2), (77, 2), (82, 4), (None, 4)],
           [(72, 2), (75, 2), (79, 2), (75, 2), (84, 4), (None, 4)],
           [(73, 2), (76, 2), (81, 2), (76, 2), (85, 8, "v")]])
build("seguranca", 112, [(50, "m"), (46, "M"), (43, "m"), (45, "7")],
      [0, 2, 3, 2, 0, 2, 3, 2, 1, 3, 2, 3, 1, 3, 2, 1], "saw", 0.5,
      {0: (0, 1), 2: (12, 1), 3: (0, 1), 6: (7, 1), 8: (0, 1), 10: (12, 1), 11: (0, 1), 14: (7, 1)}, "sq",
      {0: "k", 6: "k", 8: "k", 4: "s", 12: "s", 0: "k", 2: "h", 3: "h", 7: "h", 10: "h", 11: "h", 14: "h", 15: "h"},
      se_a, se_b, "sq", 0.15, bars=16)

# 5) CHEFE (sala 10): epica e urgente
ch_a = mk([[(81, 4), (84, 4), (88, 4), (84, 4)], [(81, 4), (84, 4), (89, 8)], [(83, 4), (86, 4), (91, 4), (86, 4)], [(80, 4), (83, 4), (88, 8)]])
ch_b = mk([[(93, 2), (91, 2), (88, 2), (91, 2), (93, 8)], [(93, 2), (91, 2), (89, 2), (91, 2), (89, 8)],
           [(95, 2), (93, 2), (91, 2), (93, 2), (91, 8)], [(92, 2), (88, 2), (83, 2), (88, 2), (92, 8)]])
def pesado(T, bar, base, ch):
    r = ch[0] - 12
    st = T.step
    # power chords (fundamental + quinta + oitava) em serra, tocados em colcheias
    for k in (0, 2, 3, 4, 6, 8, 10, 11, 12, 14):
        for off in (0, 7, 12):
            T.put(base + k, note(r + off, st * 1.7, "saw", 0.085, 0.5, 5.0))
    # bumbo duplo e prato no inicio de cada 4 compassos
    for k in (1, 5, 9, 13):
        T.put(base + k, kick(0.38))
    if bar % 4 == 0:
        T.put(base, noise(0.9, 0.22, 4.0))


build("chefe", 168, [(45, "m"), (41, "M"), (43, "M"), (40, "7")],
      [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 3, 4, 3], "sq", 0.25,
      {0: (0, 2), 2: (0, 2), 3: (0, 1), 4: (12, 2), 6: (0, 2), 8: (0, 2), 10: (0, 2), 11: (0, 1), 12: (12, 2), 14: (7, 2)}, "saw",
      {0: "k", 2: "h", 4: "s", 6: "h", 8: "k", 10: "k", 12: "s", 14: "h", 15: "h"},
      ch_a, ch_b, "sq", 0.16, extra=pesado, bars=16)
