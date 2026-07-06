#!/usr/bin/env python3
"""Systematic anomaly audit for every area's JSON: catches props floating off
the floor, duplicate/overlapping props, placements off any floor, and interior
holes in the walkable floor. Complements audit_walls.py (perimeter sealing).

Run: python3 tools/audit_areas.py [area_id]
Exit non-zero if any anomaly is found."""
import json, glob, math, os, sys

# props that are meant to sit ABOVE the floor (wall/ceiling/window mounted), so
# a high Y is expected and must not be flagged as "floating".
MOUNTED = {
    "banner", "banner_torn", "sconce_torch", "censer_hanging", "cobweb",
    "gargoyle", "glass_lancet", "glass_lancet_broken", "candle_cluster",
    "candle_cluster_dead", "hanging_chain", "hanging_chain_bare", "rose_window",
    "buttress", "gargoyle", "chime_stone", "banner", "vault_bay_4x4",
    "city_panorama", "cathedral_mass", "spire_tower_a", "spire_tower_b",
    "spire_tower_c", "buttress_arc", "bell_great",
}
# kits that are architecture (not decor); they define floors/walls, skip float check
ARCH = {"floor_4x4", "wall_4x4", "ossuary_wall_4m", "arcade_4m", "portal_4m",
        "window_lancet_4m", "column_4m", "stair_grand_4m", "fence_iron_4m",
        "column_broken", "door_leaf", "fog_gate_frame", "cornice_4m",
        "balustrade_4m", "buttress"}   # railings/buttresses ride at height on purpose


def v3(a):
    return (float(a[0]), float(a[1]), float(a[2]))


def expand_row(r):
    out = []
    frm = v3(r["from"]); d = v3(r.get("dir", [1, 0, 0]))
    step = float(r.get("step", 4.0)); n = int(r.get("count", 1))
    skip = set(int(x) for x in r.get("skip", []))
    for i in range(n):
        if i in skip:
            continue
        out.append({"kit": r["kit"], "at": [frm[0] + d[0] * step * i,
                    frm[1] + d[1] * step * i, frm[2] + d[2] * step * i],
                    "tag": r.get("tag", "base")})
    return out


def floors_at(fills, x, z):
    """All floor heights whose tile covers (x,z) — an area can be multi-level."""
    ys = []
    for f in fills:
        mn, mx = v3(f["min"]), v3(f["max"])
        if mn[0] - 0.05 <= x <= mx[0] + 0.05 and mn[2] - 0.05 <= z <= mx[2] + 0.05:
            ys.append(mx[1])
    return ys


def audit(area_id):
    d = json.load(open(f"data/areas/{area_id}.json"))
    fills = d.get("fills", [])
    issues = []

    # gather all placed decor props (pieces + props + rows of decor)
    placed = []
    for key in ("pieces", "props"):
        for p in d.get(key, []):
            if "at" in p:
                placed.append(p)
    for r in d.get("rows", []):
        placed += expand_row(r)

    # 1) props floating off the floor (grounded decor only)
    for p in placed:
        kit = p.get("kit", "")
        if kit in MOUNTED or kit in ARCH:
            continue
        at = v3(p["at"])
        ys = floors_at(fills, at[0], at[2])
        if not ys:
            issues.append(f"OFF-FLOOR  {kit} at {p['at']} (over no floor)")
        elif not any(abs(at[1] - y) <= 0.6 for y in ys):
            # nearest floor the prop could rest on
            near = min(ys, key=lambda y: abs(at[1] - y))
            if near < at[1]:
                issues.append(f"FLOATING   {kit} at {p['at']} (nearest floor y={near:.1f}, {at[1]-near:.1f} m up)")
            else:
                issues.append(f"SUNK       {kit} at {p['at']} (nearest floor y={near:.1f}, {near-at[1]:.1f} m below)")

    # 2) duplicate/overlapping props of the same kit+tag at ~same spot
    seen = {}
    for p in placed:
        kit = p.get("kit", "")
        if kit in ARCH:
            continue
        at = v3(p["at"]); tag = p.get("tag", "base")
        key = (kit, tag, round(at[0]), round(at[1]), round(at[2]))
        if key in seen:
            issues.append(f"DUPLICATE  {kit} ({tag}) near {p['at']}")
        seen[key] = True

    # 3) interior holes: floor cells missing where surrounded by floor
    if fills:
        cells = set()
        for f in fills:
            mn, mx = v3(f["min"]), v3(f["max"])
            x = mn[0]
            while x < mx[0] - 0.01:
                z = mn[2]
                while z < mx[2] - 0.01:
                    cells.add((round(x + 2), round(z + 2)))
                    z += 4
                x += 4
        for (cx, cz) in list(cells):
            if (cx, cz) in cells:
                continue
        # a hole = empty cell with floor on all 4 sides
        xs = [c[0] for c in cells]; zs = [c[1] for c in cells]
        for cx in range(min(xs), max(xs) + 1, 4):
            for cz in range(min(zs), max(zs) + 1, 4):
                if (cx, cz) not in cells:
                    nb = sum((cx + dx, cz + dz) in cells for dx, dz in [(4, 0), (-4, 0), (0, 4), (0, -4)])
                    if nb >= 4:
                        issues.append(f"FLOOR-HOLE interior gap at cell ~({cx},{cz})")

    return issues


def main():
    ids = [sys.argv[1]] if len(sys.argv) > 1 else \
        [os.path.basename(p)[:-5] for p in sorted(glob.glob("data/areas/*.json"))
         if os.path.basename(p) != "index.json"]
    total = 0
    for aid in ids:
        iss = audit(aid)
        if iss:
            print(f"[{aid}] {len(iss)} anomalies:")
            for s in iss:
                print("   " + s)
            total += len(iss)
        else:
            print(f"[{aid}] clean")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
