#!/usr/bin/env python3
"""Vespergard audio pack synthesizer. Everything the game plays is generated
here — bells are the kingdom's motif (DECISIONS D-011). Deterministic.

Usage: python3 tools/audio/synth.py [name ...]
Writes assets/audio/*.wav (44.1 kHz mono 16-bit).
"""
import os
import sys
import wave

import numpy as np

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "audio")
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_ad(n, attack, decay_tau, sr=SR):
    """Attack (linear) + exponential decay envelope of length n samples."""
    e = np.ones(n)
    a = max(int(attack * sr), 1)
    e[:a] = np.linspace(0, 1, a)
    d = np.arange(n - a) / sr
    e[a:] = np.exp(-d / decay_tau)
    return e


def lowpass(x, cutoff):
    """One-pole lowpass."""
    dt = 1.0 / SR
    rc = 1.0 / (2 * np.pi * cutoff)
    alpha = dt / (rc + dt)
    y = np.empty_like(x)
    acc = 0.0
    # vectorized one-pole via lfilter-style recursion
    b = alpha
    a = 1 - alpha
    y[0] = b * x[0]
    for i in range(1, len(x)):   # fallback loop only for short buffers
        y[i] = b * x[i] + a * y[i - 1]
    return y


def lowpass_fft(x, cutoff, order=2.0):
    """FFT brick-ish lowpass with soft knee (fast for long buffers)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    H = 1.0 / (1.0 + (f / max(cutoff, 1.0)) ** (2 * order))
    return np.fft.irfft(X * H, len(x))


def highpass_fft(x, cutoff, order=2.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    H = 1.0 - 1.0 / (1.0 + (f / max(cutoff, 1.0)) ** (2 * order))
    return np.fft.irfft(X * H, len(x))


def bandpass_sweep(noise, f0, f1, bw=0.5):
    """Cheap bandpass whose center sweeps f0->f1 over the buffer (chunked)."""
    n = len(noise)
    out = np.zeros(n)
    chunks = 24
    cs = n // chunks
    for i in range(chunks):
        seg = noise[i * cs:(i + 1) * cs if i < chunks - 1 else n]
        fc = f0 * (f1 / f0) ** (i / (chunks - 1))
        lo = lowpass_fft(seg, fc * (1 + bw))
        out[i * cs:i * cs + len(seg)] = lo - lowpass_fft(seg, fc * (1 - bw * 0.7))
    return out


BELL_PARTIALS = [(0.56, 1.0), (0.92, 0.72), (1.19, 0.5), (1.71, 0.42),
                 (2.00, 0.36), (2.74, 0.22), (3.00, 0.18), (3.76, 0.12), (4.07, 0.08)]


def bell(f0, dur, strike=1.0, dark=0.0):
    t = t_axis(dur)
    x = np.zeros_like(t)
    for i, (ratio, amp) in enumerate(BELL_PARTIALS):
        f = f0 * ratio * (1 + rng.normal(0, 0.0012))
        decay = dur * (0.5 / (0.6 + ratio)) * (1.6 - 0.5 * dark)
        x += amp * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / max(decay, 0.05))
    # hum reinforcement + strike noise
    x += 0.5 * np.sin(2 * np.pi * f0 * 0.5 * t) * np.exp(-t / (dur * 0.8))
    ns = rng.normal(0, 1, len(t)) * np.exp(-t / 0.02) * 0.6 * strike
    x += lowpass_fft(ns, 3000)
    return x


def choir_note(f0, dur, vib=4.6, breath=0.25):
    """Vowel-ish sustained tone: few harmonics + formant noise + vibrato."""
    t = t_axis(dur)
    vibr = 1 + 0.006 * np.sin(2 * np.pi * vib * t + rng.uniform(0, 6)) * np.minimum(t / 1.2, 1)
    x = np.zeros_like(t)
    for h, a in [(1, 1.0), (2, 0.42), (3, 0.30), (4, 0.14), (5, 0.07)]:
        x += a * np.sin(2 * np.pi * f0 * h * np.cumsum(vibr) / SR + rng.uniform(0, 6))
    br = lowpass_fft(rng.normal(0, 1, len(t)), f0 * 4) * breath
    x = x + br
    a = min(dur * 0.35, 1.6)
    e = np.minimum(t / a, 1) * np.minimum((dur - t) / a, 1) ** 1.2
    return x * np.clip(e, 0, 1)


def organ_note(f0, dur, gain=1.0):
    t = t_axis(dur)
    x = np.zeros_like(t)
    for h, a in [(1, 1.0), (2, 0.5), (3, 0.33), (4, 0.2), (6, 0.1), (8, 0.05)]:
        x += a * np.sin(2 * np.pi * f0 * h * t + 0.1 * h)
    e = np.minimum(t / 0.4, 1) * np.minimum((dur - t) / 0.8, 1)
    return x * np.clip(e, 0, 1) * gain


def wind(dur, base_cut=400, gust=0.35, seed=3):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    x = r.normal(0, 1, n)
    x = lowpass_fft(x, base_cut)
    # slow gust envelope
    gn = r.normal(0, 1, 200)
    ge = np.interp(np.linspace(0, 199, n), np.arange(200), gn)
    ge = lowpass_fft(ge, 2.0 / dur * 4) if False else ge
    ge = (ge - ge.min()) / (ge.ptp() + 1e-9)
	# smooth
    k = int(SR * 0.8)
    ge = np.convolve(ge, np.ones(k) / k, mode="same")
    return x * (0.35 + gust * ge)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def write(name, x, peak=0.9):
    os.makedirs(OUT, exist_ok=True)
    data = (norm(x, peak) * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"[audio] {name}.wav  {len(x)/SR:.1f}s")


# ------------------------------------------------------------------ pieces

def gen_bell_toll():
    write("bell_toll", bell(98, 7.0, strike=1.2), 0.85)

def gen_rest_chime():
    x = np.zeros(int(3.4 * SR))
    for i, (f, at) in enumerate([(294, 0.0), (370, 0.5), (440, 1.0)]):
        b = bell(f, 2.2, strike=0.4) * 0.7
        s = int(at * SR)
        x[s:s + len(b)] += b[:len(x) - s]
    write("rest_chime", x, 0.6)

def gen_orison_pickup():
    t = t_axis(0.5)
    x = np.zeros_like(t)
    for f, d in [(1568, 0.0), (2093, 0.06), (2637, 0.12)]:
        i = int(d * SR)
        seg = np.sin(2 * np.pi * f * t[:len(t) - i]) * env_ad(len(t) - i, 0.004, 0.09)
        x[i:] += seg * 0.5
    write("orison", x, 0.5)

def gen_levelup():
    x = np.zeros(int(2.6 * SR))
    for f, at in [(294, 0.0), (440, 0.35), (587, 0.7)]:
        b = bell(f, 1.8, strike=0.5)
        s = int(at * SR)
        x[s:s + len(b)] += b[:len(x) - s] * 0.8
    write("levelup", x, 0.62)

def gen_whooshes():
    n = int(0.34 * SR)
    x = bandpass_sweep(rng.normal(0, 1, n), 2600, 500, 0.8) * env_ad(n, 0.02, 0.1)
    write("whoosh_l", x, 0.55)
    n = int(0.5 * SR)
    x = bandpass_sweep(rng.normal(0, 1, n), 1800, 260, 0.9) * env_ad(n, 0.05, 0.16)
    write("whoosh_h", x, 0.65)
    n = int(0.3 * SR)
    x = lowpass_fft(rng.normal(0, 1, n), 900) * env_ad(n, 0.03, 0.09)
    write("roll", x, 0.4)

def gen_impacts():
    t = t_axis(0.3)
    f = 130 * np.exp(-t * 9)
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.002, 0.07)
    crack = lowpass_fft(rng.normal(0, 1, len(t)), 2400) * env_ad(len(t), 0.001, 0.025) * 0.8
    write("impact_flesh", thud * 1.2 + crack, 0.8)

    t = t_axis(0.42)
    x = np.zeros_like(t)
    for f0, a in [(760, 1.0), (1290, 0.6), (2140, 0.42), (3200, 0.2)]:
        x += a * np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.07)
    thud2 = np.sin(2 * np.pi * 90 * t) * env_ad(len(t), 0.001, 0.05)
    write("impact_blocked", x + thud2, 0.7)

    t = t_axis(0.8)
    x = np.zeros_like(t)
    for f0, a in [(1180, 1.0), (1770, 0.7), (2650, 0.5), (3980, 0.3)]:
        x += a * np.sin(2 * np.pi * f0 * t + 0.3) * np.exp(-t / 0.16)
    write("parry", x * env_ad(len(t), 0.001, 0.3), 0.7)

def gen_flask():
    t = t_axis(1.2)
    x = np.zeros_like(t)
    for i in range(3):
        s = int((0.15 + i * 0.22) * SR)
        f = 300 - i * 40
        seg_t = t_axis(0.12)
        blip = np.sin(2 * np.pi * (f - 60 * seg_t / 0.12) * seg_t) * env_ad(len(seg_t), 0.01, 0.05)
        x[s:s + len(blip)] += blip * 0.7
    sh = bell(660, 0.9, strike=0.3) * 0.25
    s = int(0.75 * SR)
    x[s:s + len(sh)] += sh[:len(x) - s]
    write("flask", x, 0.55)

def gen_death():
    t = t_axis(3.4)
    f = np.linspace(110, 82, len(t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x += 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.06) / SR)
    x *= np.exp(-t / 1.4)
    air = lowpass_fft(rng.normal(0, 1, len(t)), 500) * np.exp(-t / 2.0) * 0.4
    write("death", x + air, 0.75)

def gen_swells():
    # kindle: rising shimmer into warm bloom
    dur = 6.5
    t = t_axis(dur)
    n = len(t)
    sw = bandpass_sweep(rng.normal(0, 1, n), 300, 4200, 0.7) * (t / dur) ** 1.6
    bloom = np.zeros(n)
    for f, at in [(294, 3.4), (370, 3.9), (440, 4.3), (587, 4.7)]:
        b = choir_note(f, 2.4) * 0.5
        s = int(at * SR)
        bloom[s:min(s + len(b), n)] += b[:max(n - s, 0)]
    bl = bell(392, 2.5, 0.5) * 0.5
    s = int(4.6 * SR)
    bloom[s:min(s + len(bl), n)] += bl[:max(n - s, 0)]
    write("swell_kindle", sw * 0.7 + bloom, 0.8)

    # gutter: breath sucked out of the world, down into a toll
    t = t_axis(6.5)
    n = len(t)
    rev = bandpass_sweep(rng.normal(0, 1, n), 3800, 240, 0.8) * (t / 6.5) ** 1.3
    f = np.linspace(180, 55, n)
    moan = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / 6.5) ** 2 * 0.8
    moan += np.sin(2 * np.pi * np.cumsum(f * 1.032) / SR) * (t / 6.5) ** 2 * 0.5
    toll = bell(73.5, 2.4, 1.3, dark=0.6)
    s = int(4.4 * SR)
    out = rev * 0.75 + moan
    out[s:min(s + len(toll), n)] += toll[:max(n - s, 0)] * 1.1
    write("swell_gutter", out, 0.82)

def gen_theme_glory():
    dur = 28.0
    n = int(dur * SR)
    x = np.zeros(n)
    # organ ground: D2-A2 drone, warm
    x += organ_note(73.4, dur, 0.30)
    x += organ_note(110, dur, 0.16)
    # choir phrase (D dorian): D4 F4 E4 A3 | each 7 s crossfaded
    seq = [(293.7, 0), (349.2, 7), (329.6, 14), (220.0, 21)]
    for f, at in seq:
        c = choir_note(f, 8.4) * 0.5
        s = int(at * SR)
        x[s:min(s + len(c), n)] += c[:max(n - s, 0)]
    # high shimmer thirds, quiet
    for f, at in [(587.3, 3.5), (698.5, 10.5), (659.3, 17.5), (440.0, 24.5)]:
        c = choir_note(f, 5.5, breath=0.15) * 0.16
        s = int(at * SR)
        x[s:min(s + len(c), n)] += c[:max(n - s, 0)]
    # distant hour-bell twice
    for at, f in [(6.0, 587), (20.0, 440)]:
        b = bell(f, 3.0, 0.35) * 0.14
        s = int(at * SR)
        x[s:min(s + len(b), n)] += b[:max(n - s, 0)]
    write("theme_glory", lowpass_fft(x, 5200), 0.6)

def gen_theme_ruin():
    dur = 30.0
    n = int(dur * SR)
    t = t_axis(dur)
    x = np.zeros(n)
    # detuned low drones
    x += np.sin(2 * np.pi * 36.7 * t) * 0.5
    x += np.sin(2 * np.pi * 37.1 * t + 1.0) * 0.4
    x += np.sin(2 * np.pi * 73.4 * t + 0.5) * 0.22
    slow = 0.5 + 0.5 * np.sin(2 * np.pi * t / dur * 2 + 1.0)
    x *= 0.55 + 0.45 * slow
    # dissonant wisp: Eb over D, comes and goes
    wisp = choir_note(311.1, 9.0, vib=2.2, breath=0.5) * 0.12
    s = int(9.0 * SR)
    x[s:min(s + len(wisp), n)] += wisp[:max(n - s, 0)]
    # cold wind bed
    x += wind(dur, 300, 0.5, seed=11) * 0.30
    # funeral toll at 4 and 22 s
    for at in (4.0, 22.0):
        b = bell(65.4, 5.0, 0.9, dark=0.8) * 0.3
        s = int(at * SR)
        x[s:min(s + len(b), n)] += b[:max(n - s, 0)]
    write("theme_ruin", lowpass_fft(x, 3600), 0.62)

def gen_theme_boss():
    dur = 24.0
    n = int(dur * SR)
    t = t_axis(dur)
    x = np.zeros(n)
    # war-drum pattern every 1.5 s with pickup
    beat = t_axis(0.5)
    drum_f = 68 * np.exp(-beat * 12)
    drum = np.sin(2 * np.pi * np.cumsum(drum_f) / SR) * env_ad(len(beat), 0.002, 0.16)
    for i in range(int(dur / 1.5)):
        s = int(i * 1.5 * SR)
        x[s:s + len(drum)] += drum * (1.0 if i % 2 == 0 else 0.7)
        s2 = s + int(0.375 * SR)
        if s2 + len(drum) < n:
            x[s2:s2 + len(drum)] += drum * 0.4
    # driving low pulse + minor smear
    x += np.sin(2 * np.pi * 49 * t) * 0.28 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 3.0))
    smear = choir_note(196, 10, vib=1.8, breath=0.4) * 0.2
    x[int(6 * SR):int(6 * SR) + len(smear)] += smear[:max(n - int(6 * SR), 0)]
    # the cracked bell answers every 6 s, sour (flattened)
    for i in range(4):
        b = bell(103, 3.2, 1.1, dark=0.5) * 0.34
        s = int((3.0 + i * 6.0) * SR)
        x[s:min(s + len(b), n)] += b[:max(n - s, 0)]
    write("theme_boss", lowpass_fft(x, 4200), 0.7)

def birdsong(f0, dur=0.5, warble=28.0):
    """Tiny larksong motif: chirp with pitch warble and quick decay."""
    t = t_axis(dur)
    f = f0 * (1 + 0.09 * np.sin(2 * np.pi * warble * t)) * (1 + 0.25 * np.exp(-t * 9))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return x * env_ad(len(t), 0.02, dur * 0.3)


def crow_caw(dur=0.42):
    """Harsh descending croak: AM noise over a falling saw."""
    t = t_axis(dur)
    f = np.linspace(620, 380, len(t))
    saw = 2 * ((np.cumsum(f) / SR) % 1.0) - 1
    am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 42 * t))
    x = saw * am + lowpass_fft(rng.normal(0, 1, len(t)), 1800) * 0.5
    return lowpass_fft(x, 1500) * env_ad(len(t), 0.03, 0.16)


def gen_ambiences():
    dur = 22.0
    # glory: soft warm air, faint chimes, larks in the garth
    g = wind(dur, 600, 0.25, seed=21) * 0.5
    n = len(g)
    for at, f in [(5.0, 1174), (13.0, 880), (18.5, 1318)]:
        b = bell(f, 1.6, 0.25) * 0.05
        s = int(at * SR)
        g[s:min(s + len(b), n)] += b[:max(n - s, 0)]
    r2 = np.random.default_rng(33)
    for at in (2.2, 7.6, 11.4, 16.0, 19.8):
        for k in range(r2.integers(2, 4)):
            c = birdsong(r2.uniform(1900, 3200), r2.uniform(0.22, 0.5)) * 0.055
            s = int((at + k * 0.35 + r2.uniform(0, 0.1)) * SR)
            if s + len(c) < n:
                g[s:s + len(c)] += c
    write("amb_glory", g, 0.4)
    # ruin: hollow wind, deep resonances, drips
    r = wind(dur, 260, 0.6, seed=22) * 0.8
    for at in (6.0, 15.5):
        t2 = t_axis(1.2)
        creak_f = np.linspace(90, 60, len(t2))
        creak = np.sin(2 * np.pi * np.cumsum(creak_f) / SR) * env_ad(len(t2), 0.3, 0.3) * 0.16
        s = int(at * SR)
        r[s:s + len(creak)] += creak
    for at in (3.2, 9.7, 18.3):
        t3 = t_axis(0.09)
        drip = np.sin(2 * np.pi * 2900 * t3) * env_ad(len(t3), 0.002, 0.02) * 0.12
        s = int(at * SR)
        r[s:s + len(drip)] += drip
    r4 = np.random.default_rng(44)
    for at in (5.4, 12.8, 19.6):
        for k in range(r4.integers(1, 3)):
            c = crow_caw(r4.uniform(0.3, 0.5)) * 0.11
            s = int((at + k * 0.5) * SR)
            if s + len(c) < len(r):
                r[s:s + len(c)] += c
    write("amb_ruin", r, 0.45)

def gen_creature():
    # penitent moan: wobbling formant
    t = t_axis(1.8)
    f = 120 + 22 * np.sin(2 * np.pi * 1.4 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x += 0.5 * np.sin(2 * np.pi * np.cumsum(f * 2.02) / SR)
    x = lowpass_fft(x, 800) + lowpass_fft(rng.normal(0, 1, len(t)), 400) * 0.3
    write("penitent_moan", x * env_ad(len(t), 0.4, 0.5), 0.5)
    # ward challenge: hollow metallic breath
    t = t_axis(1.2)
    x = lowpass_fft(rng.normal(0, 1, len(t)), 900) * env_ad(len(t), 0.2, 0.4)
    x += np.sin(2 * np.pi * 220 * t) * np.exp(-t / 0.5) * 0.3
    write("ward_hail", x, 0.5)
    # bellkeeper roar: bell partials bent down + growl
    t = t_axis(2.6)
    x = np.zeros_like(t)
    for ratio, a in BELL_PARTIALS[:6]:
        f = 130 * ratio * np.exp(-t * 0.22)
        x += a * np.sin(2 * np.pi * np.cumsum(f) / SR)
    growl = lowpass_fft(rng.normal(0, 1, len(t)) * np.sin(2 * np.pi * 30 * t), 500)
    write("bellkeeper_roar", (x * 0.7 + growl * 0.6) * env_ad(len(t), 0.06, 1.0), 0.8)

def gen_misc():
    # fog gate pass: muffled whoomp + hush
    t = t_axis(1.4)
    f = 220 * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.01, 0.3)
    x += lowpass_fft(rng.normal(0, 1, len(t)), 300) * np.exp(-t / 0.8) * 0.5
    write("fog_enter", x, 0.6)
    # footsteps
    for i, name in enumerate(["step1", "step2"]):
        t = t_axis(0.16)
        f = (95 if i == 0 else 82) * np.exp(-t * 26)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.001, 0.03)
        x += lowpass_fft(np.random.default_rng(30 + i).normal(0, 1, len(t)), 1400) * env_ad(len(t), 0.001, 0.015) * 0.5
        write(name, x, 0.35)
    # ui tick
    t = t_axis(0.07)
    x = np.sin(2 * np.pi * 1100 * t) * env_ad(len(t), 0.001, 0.015)
    write("ui_tick", x, 0.3)
    # remembrance recover: warm minor->major shimmer
    t = t_axis(1.6)
    x = np.zeros_like(t)
    for f, a in [(392, 0.8), (494, 0.55), (587, 0.6)]:
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.7)
    write("remembrance", x, 0.55)
    # guard break
    t = t_axis(0.6)
    x = np.zeros_like(t)
    for f0, a in [(320, 1.0), (475, 0.5), (710, 0.4)]:
        x += a * np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.1)
    x += lowpass_fft(rng.normal(0, 1, len(t)), 900) * env_ad(len(t), 0.002, 0.08)
    write("guard_break", x, 0.7)


ALL = {
    "bell_toll": gen_bell_toll, "rest_chime": gen_rest_chime, "orison": gen_orison_pickup,
    "levelup": gen_levelup, "whooshes": gen_whooshes, "impacts": gen_impacts,
    "flask": gen_flask, "death": gen_death, "swells": gen_swells,
    "theme_glory": gen_theme_glory, "theme_ruin": gen_theme_ruin, "theme_boss": gen_theme_boss,
    "ambiences": gen_ambiences, "creature": gen_creature, "misc": gen_misc,
}

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, fn in ALL.items():
        if only and name not in only:
            continue
        fn()
    print("[audio] done")
