#!/usr/bin/env python3
"""Painterly detail textures for the gothic shader's triplanar overlay.

Grayscale 512x512, value-centered near 0.5 so they modulate family albedo
without shifting hue (overlay math in gothic.gdshader). Deterministic.

Technique: octave value noise -> directional 'brush' smearing -> partial
posterize -> per-material structure (ashlar grid, planks, shingles, weave,
slabs) painted on top with per-cell tone jitter and edge strokes.
"""
import os
import struct
import zlib

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "textures")
N = 512
rng = np.random.default_rng(11)


def write_png(name, img):
    """img: float array HxW in [0,1] -> 8-bit grayscale PNG."""
    data = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    raw = b"".join(b"\x00" + data[y].tobytes() for y in range(data.shape[0]))
    def chunk(tag, payload):
        c = tag + payload
        return struct.pack(">I", len(payload)) + c + struct.pack(">I", zlib.crc32(c))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", data.shape[1], data.shape[0], 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".png"), "wb") as f:
        f.write(png)
    print(f"[tex] {name}.png")


def blur_wrap(img, passes=1):
    for _ in range(passes):
        img = (img + np.roll(img, 1, 0) + np.roll(img, -1, 0)
               + np.roll(img, 1, 1) + np.roll(img, -1, 1)) / 5.0
    return img


def vnoise(freq, seed, octaves=3, gain=0.55):
    r = np.random.default_rng(seed)
    out = np.zeros((N, N))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        f = freq * (2 ** o)
        small = r.random((f, f))
        big = np.kron(small, np.ones((N // f + 1, N // f + 1)))[:N, :N]
        big = blur_wrap(big, 3)
        out += big * amp
        total += amp
        amp *= gain
    out /= total
    out -= out.min()
    out /= max(out.ptp(), 1e-9)
    return out


def brush(img, angle_deg, length=7, passes=2):
    """Directional smear — the 'painted' feel."""
    a = np.deg2rad(angle_deg)
    dx, dy = np.cos(a), np.sin(a)
    for _ in range(passes):
        acc = img.copy()
        for i in range(1, length):
            acc += np.roll(np.roll(img, int(round(dy * i)), 0), int(round(dx * i)), 1)
        img = acc / length
    return img

def posterize(img, steps=6, mix=0.4):
    q = np.round(img * steps) / steps
    return img * (1 - mix) + q * mix


def norm05(img, spread=0.5):
    img = img - img.mean()
    s = img.std() + 1e-9
    return np.clip(0.5 + img / s * 0.5 * spread * 0.35, 0, 1)


def cell_grid(rows, cols, jitter_seed, stagger=True):
    """Per-cell id map + mortar mask + painted bevel strokes."""
    r = np.random.default_rng(jitter_seed)
    y = np.linspace(0, rows, N, endpoint=False)
    ids = np.zeros((N, N))
    mortar = np.zeros((N, N))
    bevel = np.zeros((N, N))
    row_i = np.floor(y).astype(int)
    for i in range(rows):
        band = row_i == i
        off = 0.5 if (stagger and i % 2) else 0.0
        x = np.linspace(0, cols, N, endpoint=False) + off
        col_i = np.floor(x).astype(int) % (cols + 1)
        fx = x - np.floor(x)
        fy = (y - np.floor(y))[band]
        ids[band] = (i * 31 + col_i[None, :] * 7 + r.integers(0, 5)) % 97
        m = np.zeros((band.sum(), N))
        m += (fx[None, :] < 0.035) | (fx[None, :] > 0.965)
        m += (fy[:, None] < 0.06) | (fy[:, None] > 0.94)
        mortar[band] = np.clip(m, 0, 1)
        # painted highlight along the top edge of each block
        b = np.clip(1.0 - np.abs(fy[:, None] - 0.10) / 0.07, 0, 1) * (fx[None, :] > 0.05) * (fx[None, :] < 0.95)
        bevel[band] = b
    return ids, blur_wrap(mortar, 1), blur_wrap(bevel, 1)


def tone_from_ids(ids, seed, spread=0.16):
    r = np.random.default_rng(seed)
    lut = 0.5 + (r.random(128) - 0.5) * spread * 2
    return lut[(ids.astype(int)) % 128]


def make_stone():
    base = vnoise(8, 21, 4)
    base = brush(base, 15, 6) * 0.5 + brush(vnoise(16, 22, 3), -30, 5) * 0.5
    ids, mortar, bevel = cell_grid(4, 2, 31)          # 2m tile: 0.5m rows, 1m blocks
    tone = tone_from_ids(ids, 32, 0.13)
    img = norm05(base, 0.8) * 0.55 + tone * 0.45
    img = posterize(img, 7, 0.35)
    img = img * (1 - 0.42 * mortar) + 0.06 * bevel
    write_png("T_stone", img)

def make_trim():
    base = brush(vnoise(12, 41, 4), 5, 5)
    img = norm05(base, 0.6) * 0.8 + 0.1
    veins = (vnoise(6, 42, 2) > 0.62) * 0.08
    img = posterize(img - veins, 8, 0.3)
    write_png("T_trim", img)

def make_floor():
    base = brush(vnoise(10, 51, 4), 40, 6)
    ids, mortar, bevel = cell_grid(2, 2, 52, stagger=False)   # 1m slabs
    tone = tone_from_ids(ids, 53, 0.1)
    wear = blur_wrap((vnoise(4, 54, 2) > 0.6).astype(float), 4) * 0.12
    img = norm05(base, 0.7) * 0.5 + tone * 0.5 - wear
    img = posterize(img, 6, 0.4)
    img = img * (1 - 0.38 * mortar) + 0.045 * bevel
    write_png("T_floor", img)

def make_wood():
    g = vnoise(6, 61, 3)
    grain = np.tile(np.linspace(0, 1, N // 8, endpoint=False), 8)[None, :]
    img = 0.5 + 0.5 * np.sin((grain * 4 + g * 2.2) * np.pi * 2) * 0.14
    img = brush(img + (vnoise(24, 62, 2) - 0.5) * 0.15, 90, 8)
    planks = ((np.arange(N)[None, :] % (N // 4)) < 4).astype(float)
    img = norm05(img, 0.8) * (1 - 0.3 * blur_wrap(planks, 1))
    write_png("T_wood", img)

def make_roof():
    # staggered shingle rows: 8 rows per 2m tile
    y = np.linspace(0, 8, N, endpoint=False)
    fy = y - np.floor(y)
    row = np.floor(y).astype(int)
    x = np.linspace(0, 8, N, endpoint=False)
    img = np.full((N, N), 0.5)
    r = np.random.default_rng(71)
    for i in range(8):
        band = row == i
        off = 0.5 if i % 2 else 0.0
        fx = (x + off) - np.floor(x + off)
        tone = tone_from_ids(np.floor(x + off)[None, :] + i * 13, 72 + i, 0.12)
        img[band] = tone[0]
        edge = np.clip((fy[band][:, None] - 0.78) / 0.22, 0, 1) ** 1.5
        img[band] -= edge * 0.34
        gap = ((fx < 0.04) | (fx > 0.96)).astype(float)[None, :]
        img[band] -= gap * 0.2
    img += (vnoise(12, 73, 3) - 0.5) * 0.12
    write_png("T_roof", posterize(np.clip(img, 0, 1), 7, 0.3))

def make_cloth():
    weave = (np.indices((N, N)).sum(0) % 4 < 2).astype(float) * 0.05
    u = np.linspace(0, 6, N, endpoint=False)
    diam = (np.abs(((u[None, :] + u[:, None]) % 1) - 0.5) + np.abs(((u[None, :] - u[:, None]) % 1) - 0.5))
    damask = (diam < 0.42).astype(float) * 0.07
    folds = brush(vnoise(5, 81, 3), 90, 9)
    img = norm05(folds, 0.7) + weave - damask
    write_png("T_cloth", np.clip(img, 0, 1))

def make_iron():
    img = brush(vnoise(20, 91, 3), 0, 10)
    pits = (vnoise(32, 92, 2) > 0.72) * 0.18
    img = norm05(img, 0.55) - pits
    write_png("T_iron", np.clip(img, 0, 1))

def make_wax():
    blobs = blur_wrap(vnoise(6, 101, 3), 6)
    drips = brush(vnoise(18, 102, 2), 90, 12)
    img = norm05(blobs * 0.7 + drips * 0.3, 0.5)
    write_png("T_wax", img)

def make_mosaic():
    # tesserae: 24 cells/2m tile, per-cube tone jitter, sunk grout, a few
    # missing cubes; concentric band pattern for medallion charm
    cells = 24
    u = np.linspace(0, cells, N, endpoint=False)
    fx = u[None, :] - np.floor(u[None, :])
    fy = u[:, None] - np.floor(u[:, None])
    ids = (np.floor(u)[None, :] * 53 + np.floor(u)[:, None] * 17)
    tone = tone_from_ids(ids, 111, 0.2)
    r = np.random.default_rng(112)
    missing = (r.random((cells, cells)) < 0.04)
    miss = np.kron(missing, np.ones((N // cells + 1, N // cells + 1)))[:N, :N]
    grout = ((fx < 0.12) | (fx > 0.88) | (fy < 0.12) | (fy > 0.88)).astype(float)
    cx = (np.linspace(-1, 1, N)[None, :] ** 2 + np.linspace(-1, 1, N)[:, None] ** 2) ** 0.5
    band = 0.5 + 0.5 * np.sin(cx * np.pi * 6)
    img = tone * 0.62 + band * 0.16 + 0.11
    img = img * (1 - 0.5 * blur_wrap(grout, 1)) * (1 - 0.35 * miss)
    img += (vnoise(10, 113, 2) - 0.5) * 0.08
    write_png("T_mosaic", posterize(np.clip(img, 0, 1), 8, 0.3))

def make_bronze():
    # cast bronze: vertical pour streaks, patina mottle, bright rubbed spots
    streaks = brush(vnoise(14, 121, 3), 90, 14)
    patina = blur_wrap((vnoise(7, 122, 3) > 0.58).astype(float), 3)
    rubbed = blur_wrap((vnoise(5, 123, 2) > 0.72).astype(float), 4)
    img = norm05(streaks, 0.5) - patina * 0.16 + rubbed * 0.18
    img += (vnoise(28, 124, 2) - 0.5) * 0.07
    write_png("T_bronze", posterize(np.clip(img, 0, 1), 7, 0.25))


def make_bone():
    # ossuary stacking: rounded knuckle cells + dark socket pits + dust
    cells = 14
    u = np.linspace(0, cells, N, endpoint=False)
    fx = u[None, :] - np.floor(u[None, :])
    fy = u[:, None] - np.floor(u[:, None])
    dome = np.clip(1.0 - ((fx - 0.5) ** 2 + (fy - 0.5) ** 2) * 5.0, 0, 1) ** 0.7
    ids = (np.floor(u)[None, :] * 31 + np.floor(u)[:, None] * 7)
    tone = tone_from_ids(ids, 131, 0.14)
    r = np.random.default_rng(132)
    sockets = (r.random((cells, cells)) < 0.16)
    soc = np.kron(sockets, np.ones((N // cells + 1, N // cells + 1)))[:N, :N]
    soc = soc * (dome > 0.55)
    img = 0.34 + dome * 0.34 + tone * 0.22
    img -= soc * 0.34
    img += (vnoise(9, 133, 3) - 0.5) * 0.1
    write_png("T_bone", posterize(np.clip(img, 0, 1), 7, 0.3))


def make_marble():
    # palace ashlar: near-still ivory ground, thin meandering veins, a faint
    # polish sheen band — reads rich and smooth against T_stone's rough blocks
    # true marble veining: sine bands warped by smooth turbulence (integer
    # band counts keep the tile seamless). Ridge-of-blocky-noise traces the
    # noise cells' edges and reads as nested squares — never that.
    yy, xx = np.mgrid[0:N, 0:N] / N
    warp1 = blur_wrap(vnoise(4, 142, 3, gain=0.55), 10)
    warp2 = blur_wrap(vnoise(6, 143, 3, gain=0.55), 10)
    band1 = np.sin((xx * 3 + yy * 1) * 2 * np.pi + warp1 * 7.5)
    band2 = np.sin((xx * 1 - yy * 2) * 2 * np.pi + warp2 * 9.5)
    veins = (np.clip(1.0 - np.abs(band1) * 5.0, 0, 1) * 0.65
             + np.clip(1.0 - np.abs(band2) * 7.0, 0, 1) * 0.45)
    veins = blur_wrap(veins, 1)
    ground = brush(blur_wrap(vnoise(16, 141, 3, gain=0.5), 2), 30, 12, passes=2)
    sheen = brush(vnoise(5, 145, 2), 25, 14)
    img = norm05(ground, 0.14) + (norm05(sheen, 0.2) - 0.5) * 0.07 - veins * 0.15
    write_png("T_marble", np.clip(img, 0, 1))


def make_marble_floor():
    # broad polished slabs, hairline joints, long reflection streaks
    base = brush(blur_wrap(vnoise(14, 151, 3, gain=0.5), 2), 78, 10, passes=3)
    streaks = brush(vnoise(7, 152, 3), 78, 14)
    ids, mortar, bevel = cell_grid(2, 2, 153, stagger=False)      # 2 m slabs
    tone = tone_from_ids(ids, 154, 0.06)
    yy, xx = np.mgrid[0:N, 0:N] / N
    warp = blur_wrap(vnoise(5, 155, 3, gain=0.55), 10)
    band = np.sin((xx * 2 + yy * 2) * 2 * np.pi + warp * 8.0)
    veins = blur_wrap(np.clip(1.0 - np.abs(band) * 6.0, 0, 1), 1)
    img = norm05(base, 0.2) * 0.5 + tone * 0.5 + (norm05(streaks, 0.25) - 0.5) * 0.09
    img -= veins * 0.10
    img = img * (1 - 0.30 * mortar) + 0.03 * bevel
    write_png("T_marble_floor", np.clip(img, 0, 1))


if __name__ == "__main__":
    make_stone(); make_trim(); make_floor(); make_wood()
    make_roof(); make_cloth(); make_iron(); make_wax()
    make_mosaic(); make_bronze(); make_bone()
    make_marble(); make_marble_floor()
    print("[tex] done")
