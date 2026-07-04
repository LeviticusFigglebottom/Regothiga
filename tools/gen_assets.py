#!/usr/bin/env python3
"""Regenerate the whole gothic kit: tools/blender/* -> assets/kit/*.glb
plus assets/kit/manifest.json. Deterministic (fixed seeds).

Usage: python3 tools/gen_assets.py [piece ...]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "blender"))

import bpy  # noqa: E402
import vglib as V  # noqa: E402
import kit_arch  # noqa: E402
import kit_props  # noqa: E402
import kit_chars  # noqa: E402
import kit_backdrop  # noqa: E402

OUT = os.path.join(ROOT, "assets", "kit")

# per-piece vertex-mask overrides (ceilings don't grow floor moss, etc.)
PAINT_OVERRIDES = {
    "vault_bay_4x4": {"moss_below": -99.0},
    "roof_shed_4m": {"moss_below": -99.0},
    "cornice_4m": {"moss_below": -99.0},
}


def main():
    only = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    manifest_path = os.path.join(OUT, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path) and only:
        with open(manifest_path) as f:
            manifest = json.load(f)

    builders = {}
    builders.update(kit_arch.BUILDERS)
    builders.update(kit_props.BUILDERS)
    builders.update(kit_chars.BUILDERS)
    builders.update(kit_backdrop.BUILDERS)

    for name, fn in builders.items():
        if only and name not in only:
            continue
        V.reset_scene()
        objs, entry = fn()
        path = os.path.join(OUT, f"{name}.glb")
        V.export_glb(objs, path, seed=hash(name) % 10000, **PAINT_OVERRIDES.get(name, {}))
        entry["file"] = f"assets/kit/{name}.glb"
        tris = sum(len(o.data.polygons) for o in objs if o.type == 'MESH')
        entry["polys"] = tris
        manifest[name] = entry
        print(f"[kit] {name:24s} {tris:6d} polys -> {path}")

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print(f"[kit] manifest: {len(manifest)} pieces")


if __name__ == "__main__":
    main()
