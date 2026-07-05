#!/usr/bin/env python3
"""Perimeter audit: rasterize an area's floor fills on a 1m grid, walk the
boundary, and check every 4m boundary segment for a blocking piece (wall /
window / portal / fence / blocker / gate). Segments open in ONE state only
are fine if that's a designed state-route; anything open in BOTH states is
an out-of-bounds hole.

Usage: python3 tools/audit_walls.py [area_id ...]
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCKING = {"wall_4x4", "window_lancet_4m", "portal_4m", "fence_iron_4m",
            "arcade_4m", "rubble_m", "rubble_l", "column_4m", "buttress",
            "balustrade_4m", "stair_grand_4m"}
# pieces that block travel but are passable doorways (still "not a fall")
OPEN_DOOR = {"portal_4m", "arcade_4m"}


def pieces_of(def_):
    out = []
    for spec in def_.get("pieces", []):
        out.append(spec)
    for spec in def_.get("props", []):
        out.append(spec)
    for row in def_.get("rows", []):
        fr = row.get("from", [0, 0, 0])
        d = row.get("dir", [1, 0, 0])
        step = row.get("step", 4.0)
        for i in range(int(row.get("count", 1))):
            if i in row.get("skip", []):
                continue
            sub = dict(row)
            sub["at"] = [fr[0] + d[0] * step * i, fr[1], fr[2] + d[2] * step * i]
            out.append(sub)
    return out


def audit(area_id):
    path = os.path.join(ROOT, "data", "areas", f"{area_id}.json")
    def_ = json.load(open(path))
    # floor cells (1m)
    cells = set()
    for f in def_.get("fills", []):
        mn, mx = f["min"], f["max"]
        for x in range(int(mn[0]), int(mx[0])):
            for z in range(int(mn[2]), int(mx[2])):
                cells.add((x, z))
    if not cells:
        print(f"[{area_id}] no floor fills; skipping")
        return []

    # boundary edges between floor and void, grouped into 4m segments
    # edge key: (x, z, 'N'|'S'|'E'|'W') on cell
    segs = {}   # (axis, fixed_coord, seg_start) -> set of state coverage
    edge_list = []
    for (x, z) in cells:
        for (dx, dz, side) in ((0, -1, 'N'), (0, 1, 'S'), (-1, 0, 'W'), (1, 0, 'E')):
            if (x + dx, z + dz) in cells:
                continue
            if side in ('N', 'S'):
                line_z = z if side == 'N' else z + 1
                seg = ('x', line_z, (x // 4) * 4)
            else:
                line_x = x if side == 'W' else x + 1
                seg = ('z', line_x, (z // 4) * 4)
            segs.setdefault(seg, set())
            edge_list.append(seg)

    # blocking pieces cover segments
    pieces = pieces_of(def_)
    for spec in pieces:
        kit = spec.get("kit", "")
        if kit not in BLOCKING:
            continue
        at = spec.get("at", [0, 0, 0])
        if float(at[1]) > 0.6:
            continue    # elevated decor (gargoyles etc.) doesn't seal ground level
        rot = float(spec.get("rot", 0)) % 360
        tag = spec.get("tag", "base")
        along_x = abs(math.sin(math.radians(rot))) < 0.5   # rot 0/180 -> runs along x
        if along_x:
            seg = ('x', round(at[2]), int((at[0] - 2) // 4 + 1) * 4 if False else int(round(at[0] - 2)))
            seg = ('x', round(at[2]), int(round(at[0] - 2)))
        else:
            seg = ('z', round(at[0]), int(round(at[2] - 2)))
        for cand in list(segs.keys()):
            if cand[0] != seg[0]:
                continue
            if abs(cand[1] - seg[1]) > 0.55:
                continue
            if abs(cand[2] - seg[2]) > 1.1:
                continue
            segs[cand].add(tag if kit not in OPEN_DOOR else "door")
    # blockers
    for b in def_.get("blockers", []):
        mn, mx = b["min"], b["max"]
        tag = b.get("tag", "base")
        for cand in list(segs.keys()):
            axis, fixed, start = cand
            if axis == 'x' and mn[2] - 0.6 <= fixed <= mx[2] + 0.6 and mn[0] <= start + 2 <= mx[0]:
                segs[cand].add(tag)
            if axis == 'z' and mn[0] - 0.6 <= fixed <= mx[0] + 0.6 and mn[2] <= start + 2 <= mx[2]:
                segs[cand].add(tag)

    holes = []
    for seg, cover in sorted(segs.items()):
        if "door" in cover:
            continue   # archway onto... verify it leads to floor on both sides? doors to void ARE holes
        if "base" in cover:
            continue
        if "glory" in cover and "ruin" in cover:
            continue
        state = "BOTH STATES" if not cover else \
            ("ruin only -> open in glory" if cover == {"ruin"} else "glory only -> open in ruin")
        holes.append((seg, state))
    # doors that lead into void (portal segments on outer boundary with no floor beyond)
    for seg, cover in sorted(segs.items()):
        if "door" in cover and not (cover - {"door"}):
            axis, fixed, start = seg
            # check floor on both sides of the line at segment middle
            if axis == 'x':
                a = (start + 2, fixed - 1) in cells or (start + 1, fixed - 1) in cells
                b = (start + 2, fixed) in cells or (start + 1, fixed) in cells
            else:
                a = (fixed - 1, start + 2) in cells or (fixed - 1, start + 1) in cells
                b = (fixed, start + 2) in cells or (fixed, start + 1) in cells
            if not (a and b):
                holes.append((seg, "DOORWAY TO VOID"))
    return holes


def main():
    ids = sys.argv[1:] or [f[:-5] for f in os.listdir(os.path.join(ROOT, "data", "areas"))
                           if f.endswith(".json") and f != "index.json"]
    bad = 0
    for aid in ids:
        holes = audit(aid)
        for (axis, fixed, start), state in holes:
            bad += 1
            if axis == 'x':
                where = f"z={fixed}, x {start}..{start + 4}"
            else:
                where = f"x={fixed}, z {start}..{start + 4}"
            print(f"[{aid}] HOLE  {where}   ({state})")
        if not holes:
            print(f"[{aid}] perimeter sealed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
