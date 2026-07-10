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


def place(buf, x, at, gain=1.0):
    """Mix x into buf starting at `at` seconds (clipped to buf)."""
    s = int(at * SR)
    if s >= len(buf) or s < 0:
        return
    seg = x[:len(buf) - s]
    buf[s:s + len(seg)] += seg * gain


def loopify(x, tail=6.0):
    """Bake a seamless whole-track loop: the last `tail` seconds are folded
    into the head with an equal-power crossfade and cut off, so the final
    sample runs straight on into the first when the stream loops."""
    n_t = int(tail * SR)
    body = x[:-n_t].copy()
    tl = x[-n_t:]
    t = np.linspace(0, 1, n_t)
    body[:n_t] = body[:n_t] * np.sqrt(t) + tl * np.sqrt(1 - t)
    return body


def fade_ends(x, head=4.5, tail=8.0, hold=1.2):
    """A piece that ENDS and BEGINS: fade in from silence over `head`, fade
    out to true silence over `tail` with a `hold` of near-silence at the very
    end. Looping such a track reads as the music finishing and, after a
    breath, starting again — no vamp seam to notice."""
    y = x.copy()
    n_h = int(head * SR)
    y[:n_h] *= np.sqrt(np.linspace(0, 1, n_h))
    n_t = int(tail * SR)
    n_hold = int(hold * SR)
    y[-(n_t + n_hold):-n_hold] *= np.sqrt(np.linspace(1, 0, n_t))
    y[-n_hold:] = 0.0
    return y


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

def _swoosh(dur, f_hi, f_lo, body_cut, peak_at=0.45, edge=0.6):
    """A blade cutting air: a bright edge band sweeping down through a broad
    low body, with an S-curve build-peak-release so it reads as a SWING, not
    a burst. Light saturation rounds it."""
    n = int(dur * SR)
    t = np.arange(n) / n
    arc = np.clip(np.sin(np.pi * np.clip((t / peak_at) * 0.5, 0, 0.5)) * (t < peak_at)
                  + np.cos(np.pi * 0.5 * np.clip((t - peak_at) / (1 - peak_at), 0, 1)) * (t >= peak_at), 0, 1) ** 1.3
    hi = bandpass_sweep(rng.normal(0, 1, n), f_hi, f_lo, 0.55) * edge
    lo = lowpass_fft(rng.normal(0, 1, n), body_cut)
    x = (hi + lo * 0.8) * arc
    return np.tanh(x * 2.2)


def gen_whooshes():
    # the raise/draw of a light and a heavy arm
    write("whoosh_l", _swoosh(0.30, 3400, 900, 1100, 0.42, 0.75), 0.55)
    write("whoosh_h", _swoosh(0.48, 2300, 380, 700, 0.5, 0.6), 0.65)
    # the CUT itself, played as the hitbox opens — short, keen, airy
    write("swing", _swoosh(0.26, 4200, 1300, 1500, 0.38, 0.9), 0.6)
    n = int(0.3 * SR)
    x = lowpass_fft(rng.normal(0, 1, n), 900) * env_ad(n, 0.03, 0.09)
    write("roll", x, 0.4)

def gen_impacts():
    t = t_axis(0.3)
    f = 130 * np.exp(-t * 9)
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.002, 0.07)
    crack = lowpass_fft(rng.normal(0, 1, len(t)), 2400) * env_ad(len(t), 0.001, 0.025) * 0.8
    write("impact_flesh", thud * 1.2 + crack, 0.8)

    # the SLASH: a cut that lands — fast bright shear over a short wet body,
    # keener and shorter than the swing's air-cut
    n = int(0.2 * SR)
    shear = bandpass_sweep(rng.normal(0, 1, n), 5600, 2100, 0.5) * env_ad(n, 0.001, 0.05)
    wet = lowpass_fft(rng.normal(0, 1, n), 620) * env_ad(n, 0.002, 0.055) * 0.9
    tf = 150 * np.exp(-np.arange(n) / SR * 11)
    body = np.sin(2 * np.pi * np.cumsum(tf) / SR) * env_ad(n, 0.001, 0.05) * 0.7
    write("slash", np.tanh((shear * 1.25 + wet + body) * 2.0), 0.78)

    t = t_axis(0.42)
    x = np.zeros_like(t)
    for f0, a in [(760, 1.0), (1290, 0.6), (2140, 0.42), (3200, 0.2)]:
        x += a * np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.07)
    thud2 = np.sin(2 * np.pi * 90 * t) * env_ad(len(t), 0.001, 0.05)
    write("impact_blocked", x + thud2, 0.7)

    # shield ding: a strike click into an inharmonic steel ring — bright,
    # quick, unmistakably metal-on-metal
    t = t_axis(0.5)
    x = np.zeros_like(t)
    for ratio, a, tau in [(1.0, 1.0, 0.16), (2.32, 0.62, 0.11), (3.01, 0.45, 0.085),
                          (4.27, 0.3, 0.06), (6.13, 0.18, 0.045)]:
        f = 1480.0 * ratio
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    click = highpass_fft(rng.normal(0, 1, len(t)), 2400) * env_ad(len(t), 0.001, 0.012) * 1.2
    write("shield_ding", x + click, 0.66)

    # parry: a hard crack, then a rising shimmer that hangs — the reward bell
    t = t_axis(1.1)
    x = np.zeros_like(t)
    for f0, a, tau in [(1180, 1.0, 0.22), (1770, 0.72, 0.2), (2650, 0.55, 0.17),
                       (3980, 0.36, 0.14), (5340, 0.2, 0.11)]:
        f = f0 * (1.0 + 0.02 * np.minimum(t / 0.25, 1.0))    # partials lift a hair
        x += a * np.sin(2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    crack = highpass_fft(rng.normal(0, 1, len(t)), 1800) * env_ad(len(t), 0.001, 0.02) * 1.6
    sparkle = bandpass_sweep(rng.normal(0, 1, len(t)), 5200, 8200, 0.5) * np.exp(-t / 0.28) * 0.3
    write("parry", x + crack + sparkle, 0.74)

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

## ------------------------------------------------------------------ themes
## The three underscores are COMPLETE pieces now, not vamps: each runs
## through named sections (statement, development, recession) and then the
## whole track loops seamlessly via loopify() — the last bars are composed
## to hand back to the first. D dorian is the kingdom's mode; the ruin
## flattens it, the boss hammers it.

# a small chord book (frequencies) used by both day-themes
_CH = {
    "Dm":  (146.8, 220.0, 293.7, 349.2),          # D3 A3 D4 F4
    "F":   (174.6, 261.6, 349.2, 440.0),          # F3 C4 F4 A4
    "C":   (130.8, 196.0, 329.6, 392.0),          # C3 G3 E4 G4
    "G":   (196.0, 246.9, 293.7, 392.0),          # G3 B3 D4 G4
    "Am":  (220.0, 261.6, 329.6, 440.0),          # A3 C4 E4 A4
    "Bb":  (233.1, 293.7, 349.2, 466.2),          # Bb3 D4 F4 Bb4
}


def _chorale(x, at, chords, phrase=9.0, gain=0.42, breath=0.22, top_gain=0.5):
    """Lay a chord progression as overlapping choir phrases from `at`."""
    for k, name in enumerate(chords):
        fs = _CH[name]
        for i, f in enumerate(fs):
            g = gain * (0.9 if i == 0 else (0.66 if i < 3 else top_gain))
            place(x, choir_note(f, phrase * 1.25, breath=breath) * g, at + k * phrase)


def gen_theme_glory():
    """The Kept Hours — four sections, ~2:15, loops whole.
    A matins: the organ ground wakes, lone voices. B the choir walks above:
    full chorale. C gilded: an organ chorale melody over the choir, larks far
    off. D vespers: the voices recede to the pedal and the hour is struck —
    which is where matins begins again."""
    dur, tail = 136.0, 6.0
    n = int((dur + tail) * SR)
    x = np.zeros(n)
    # the ground: warm organ pedal (D2+A2) breathing the whole way through,
    # and soft air so silence is never digital-black
    t = t_axis(dur + tail)
    breathe = 0.8 + 0.2 * np.sin(2 * np.pi * t / 27.0)
    x += organ_note(73.4, dur + tail, 0.26) * breathe
    x += organ_note(110.0, dur + tail, 0.13) * breathe
    x += wind(dur + tail, 700, 0.22, seed=21) * 0.10

    # A — matins (0..34): lone voices find the mode; the hour-bell far off
    place(x, bell(587.3, 4.0, 0.3) * 0.10, 5.0)
    place(x, choir_note(293.7, 11.0, breath=0.3) * 0.34, 10.0)
    place(x, choir_note(440.0, 9.0, breath=0.28) * 0.22, 19.0)
    place(x, choir_note(349.2, 10.0, breath=0.3) * 0.30, 26.0)

    # B — the choir walks above (34..70): the day's full chorale
    _chorale(x, 34.0, ["Dm", "F", "C", "Am"], phrase=9.0)
    place(x, choir_note(587.3, 7.0, breath=0.14) * 0.13, 41.0)   # descant thirds
    place(x, choir_note(523.3, 7.0, breath=0.14) * 0.12, 59.0)
    place(x, bell(440.0, 3.0, 0.3) * 0.10, 68.0)

    # C — gilded (70..106): organ chorale melody over Dm-G-Bb-Dm, larks far
    _chorale(x, 70.0, ["Dm", "G", "Bb", "Dm"], phrase=9.0, gain=0.34)
    melody = [(293.7, 0.0), (349.2, 2.2), (392.0, 4.4), (440.0, 6.6),
              (523.3, 9.0), (440.0, 11.2), (392.0, 13.4), (349.2, 15.6),
              (329.6, 18.0), (392.0, 20.2), (349.2, 22.4), (329.6, 24.6),
              (293.7, 27.0)]
    for f, at in melody:
        place(x, organ_note(f, 2.6, 0.20), 70.5 + at)
    r2 = np.random.default_rng(52)
    for at in (78.0, 93.0):
        for k in range(2):
            place(x, birdsong(r2.uniform(2100, 2900), 0.35) * 0.030, at + k * 0.5)
    place(x, bell(587.3, 3.5, 0.3) * 0.11, 96.0)

    # D — vespers recede (106..136+): thin to the pedal; the hour strikes,
    # and the whole piece settles and ENDS on the same D it woke on
    place(x, choir_note(220.0, 12.0, breath=0.32) * 0.26, 106.0)
    place(x, choir_note(293.7, 14.0, breath=0.3) * 0.30, 116.0)
    place(x, bell(293.7, 5.0, 0.5) * 0.16, 114.0)
    place(x, bell(587.3, 4.0, 0.3) * 0.09, 124.0)
    place(x, bell(146.8, 6.0, 0.55) * 0.14, 130.0)   # the low D lays it to rest
    write("theme_glory", fade_ends(lowpass_fft(x, 5200), 4.5, 9.0), 0.62)


def gen_theme_ruin():
    """The Unkept Hours — four sections, ~2:15, loops whole.
    A the hollow: beating sub-drones and cold wind. B the sour wisps: Eb
    leaning on the D that is no longer sung. C the procession: low organ
    clusters walking under creaks. D emptying: one last toll, then only the
    drones — which is the hollow again."""
    dur, tail = 136.0, 6.0
    n = int((dur + tail) * SR)
    t = t_axis(dur + tail)
    x = np.zeros(n)
    # beating sub pair + weak octave, breathing very slowly; cold wind bed
    sub = (np.sin(2 * np.pi * 36.7 * t) * 0.48
           + np.sin(2 * np.pi * 37.1 * t + 1.0) * 0.38
           + np.sin(2 * np.pi * 73.4 * t + 0.5) * 0.20)
    x += sub * (0.62 + 0.38 * np.sin(2 * np.pi * t / 31.0 + 1.2))
    x += wind(dur + tail, 280, 0.55, seed=11) * 0.34

    # A — the hollow (0..34): one far, dark toll
    place(x, bell(65.4, 6.0, 0.8, dark=0.8) * 0.24, 18.0)

    # B — sour wisps (34..70): Eb (and its shadow) over the absent D
    place(x, choir_note(311.1, 11.0, vib=2.2, breath=0.5) * 0.13, 36.0)
    place(x, choir_note(466.2, 9.0, vib=2.0, breath=0.55) * 0.08, 48.0)
    place(x, choir_note(311.1, 12.0, vib=2.4, breath=0.5) * 0.12, 58.0)
    for at in (40.0, 62.0):
        place(x, bell(65.4, 5.0, 0.9, dark=0.8) * 0.28, at)

    # C — the procession (70..106): low organ clusters lean D->Eb and back,
    # timbers complain, a crow far off
    place(x, organ_note(73.4, 15.0, 0.13), 70.0)
    place(x, organ_note(77.8, 15.0, 0.11), 78.0)
    place(x, organ_note(73.4, 15.0, 0.12), 90.0)
    for at in (74.0, 93.0):
        t2 = t_axis(1.4)
        creak_f = np.linspace(90, 58, len(t2))
        creak = np.sin(2 * np.pi * np.cumsum(creak_f) / SR) * env_ad(len(t2), 0.35, 0.35) * 0.15
        place(x, creak, at)
    place(x, crow_caw(0.45) * 0.07, 84.0)
    place(x, bell(49.0, 6.0, 0.8, dark=0.9) * 0.2, 100.0)

    # D — emptying (106..136+): the last toll and its faint answer, then the
    # drones sink back into the silence they rose from
    place(x, choir_note(311.1, 10.0, vib=2.0, breath=0.6) * 0.09, 108.0)
    place(x, bell(65.4, 6.0, 1.0, dark=0.8) * 0.30, 114.0)
    place(x, bell(98.0, 4.0, 0.5, dark=0.7) * 0.12, 126.0)
    write("theme_ruin", fade_ends(lowpass_fft(x, 3400), 5.0, 10.0), 0.62)


def gen_theme_boss():
    """The Thirteenth Hour — two escalations over a war-drum grid, ~1:32,
    loops whole. A: drums, low D pulse, the cracked bell answering, choir
    cluster stabs. B: the ostinato joins, drums double, a high lament rides
    over — then two bars of drums alone hand the loop back to A."""
    bar = 3.64                       # four beats at ~132 BPM
    bars = 26
    dur, tail = bar * bars, 3.64
    n = int((dur + tail) * SR)
    t = t_axis(dur + tail)
    x = np.zeros(n)

    beat = t_axis(0.5)
    drum_f = 66 * np.exp(-beat * 12)
    drum = np.sin(2 * np.pi * np.cumsum(drum_f) / SR) * env_ad(len(beat), 0.002, 0.16)
    tick = lowpass_fft(np.random.default_rng(61).normal(0, 1, int(0.12 * SR)), 1800) * env_ad(int(0.12 * SR), 0.001, 0.03)

    half = bars // 2
    for b in range(bars + 1):        # +1 bar runs into the fold
        s = b * bar
        heavy = b >= half
        place(x, drum, s, 1.0)
        place(x, drum, s + 0.455, 0.38)
        place(x, drum, s + 1.818, 0.8)
        place(x, drum, s + 2.727, 0.62 if not heavy else 0.85)
        if heavy:                    # doubled ghosts drive the second half
            place(x, tick, s + 0.909, 0.5)
            place(x, tick, s + 2.273, 0.5)
            place(x, tick, s + 3.18, 0.55)
    # low D pulse with a slow snarl
    x += np.sin(2 * np.pi * 49.0 * t) * 0.24 * (0.62 + 0.38 * np.sin(2 * np.pi * t / 5.6))

    # the cracked bell answers on the bar, sour and flattened
    for b in range(0, bars - 2, 4):
        f = 103.0 if (b // 4) % 2 == 0 else 97.0
        place(x, bell(f, 3.4, 1.1, dark=0.5) * 0.30, b * bar + 1.818)
    # choir cluster stabs (D + Eb + A) every 8 bars
    for b in range(0, bars - 2, 8):
        for f, g in [(293.7, 0.16), (311.1, 0.12), (220.0, 0.12)]:
            place(x, choir_note(f, 3.2, vib=3.0, breath=0.4) * g, b * bar + 0.2)

    # B half: organ ostinato (D-F-E-C#) + high lament, stopping short of the
    # final two bars so the loop lands on drums alone, straight back into A
    ost = [(146.8, 0.0), (174.6, 0.909), (164.8, 1.818), (138.6, 2.727)]
    for b in range(half, bars - 2):
        for f, off in ost:
            place(x, organ_note(f, 0.8, 0.16), b * bar + off)
    for f, at in [(587.3, half * bar + 2.0), (523.3, half * bar + 16.0), (440.0, half * bar + 30.0)]:
        place(x, choir_note(f, 9.0, vib=3.4, breath=0.3) * 0.11, at)
    # the last two bars strip back to drums so the loop lands clean on A
    write("theme_boss", loopify(lowpass_fft(x, 4400), tail), 0.7)

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
    """Long ambience beds (~42 s heard length), looped whole like the themes
    so their event patterns don't telegraph a short cycle."""
    dur, tail = 42.0, 4.0
    # glory: soft warm air, faint chimes, larks about the garth
    g = wind(dur + tail, 600, 0.25, seed=21) * 0.5
    for at, f in [(5.0, 1174), (15.5, 880), (24.0, 1318), (33.5, 987)]:
        place(g, bell(f, 1.6, 0.25) * 0.05, at)
    r2 = np.random.default_rng(33)
    for at in (2.2, 7.6, 12.4, 18.0, 22.8, 28.3, 34.0, 38.6):
        for k in range(r2.integers(2, 4)):
            place(g, birdsong(r2.uniform(1900, 3200), r2.uniform(0.22, 0.5)) * 0.055,
                  at + k * 0.35 + r2.uniform(0, 0.1))
    write("amb_glory", loopify(g, tail), 0.4)
    # ruin: hollow wind, timber groans, drips, carrion birds
    r = wind(dur + tail, 260, 0.6, seed=22) * 0.8
    for at in (6.0, 17.5, 29.0, 38.5):
        t2 = t_axis(1.2)
        creak_f = np.linspace(90, 60, len(t2))
        place(r, np.sin(2 * np.pi * np.cumsum(creak_f) / SR) * env_ad(len(t2), 0.3, 0.3) * 0.16, at)
    for at in (3.2, 9.7, 15.1, 21.4, 27.8, 33.2, 40.1):
        t3 = t_axis(0.09)
        place(r, np.sin(2 * np.pi * 2900 * t3) * env_ad(len(t3), 0.002, 0.02) * 0.12, at)
    r4 = np.random.default_rng(44)
    for at in (5.4, 13.8, 25.6, 35.2):
        for k in range(r4.integers(1, 3)):
            place(r, crow_caw(r4.uniform(0.3, 0.5)) * 0.11, at + k * 0.5)
    write("amb_ruin", loopify(r, tail), 0.45)

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




def gen_lark_trill():
    """A freed lark's rising trill — the Daily Offices puzzle's reward note."""
    r = np.random.default_rng(11)
    t, parts = 0.0, []
    for i in range(4):
        c = birdsong(2100 + i * 260 + r.uniform(-80, 80), r.uniform(0.16, 0.28))
        parts.append((t, c))
        t += r.uniform(0.06, 0.11)
    n = int((t + 0.7) * SR)
    x = np.zeros(n)
    for (st, c) in parts:
        i0 = int(st * SR)
        x[i0:i0 + len(c)] += c
    write("lark_trill", x, 0.5)


ALL = {
    "bell_toll": gen_bell_toll, "rest_chime": gen_rest_chime, "orison": gen_orison_pickup,
    "levelup": gen_levelup, "whooshes": gen_whooshes, "impacts": gen_impacts,
    "flask": gen_flask, "death": gen_death, "swells": gen_swells,
    "theme_glory": gen_theme_glory, "theme_ruin": gen_theme_ruin, "theme_boss": gen_theme_boss,
    "ambiences": gen_ambiences, "lark_trill": gen_lark_trill, "creature": gen_creature, "misc": gen_misc,
}

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, fn in ALL.items():
        if only and name not in only:
            continue
        fn()
    print("[audio] done")
