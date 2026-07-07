"""Black Gate kit: the kingdom's outer gatehouse under the drowned sun.

Portcullis, the great black doors, winch capstans, battlement crenels and
the Tollkeeper's maul. Z up; exporter maps Z->Y.
"""
import math
import bmesh

import vglib as V


def portcullis_4m():
    """Iron portcullis filling a 4 m arch: crossed bars, spiked foot. Rises
    when the capstans are turned (FlagGate open_dir=up). Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    for x in [-1.8 + i * 0.45 for i in range(9)]:                 # verticals
        V.add_box(bm, (x - 0.05, -0.05, 0.0), (x + 0.05, 0.05, 3.6))
        # spiked foot
        tip = bmesh.new()
        a = tip.verts.new((x - 0.07, -0.07, 0.0)); b = tip.verts.new((x + 0.07, -0.07, 0.0))
        c = tip.verts.new((x + 0.07, 0.07, 0.0)); d = tip.verts.new((x - 0.07, 0.07, 0.0))
        p = tip.verts.new((x, 0.0, -0.28))
        for e0, e1 in ((a, b), (b, c), (c, d), (d, a)):
            tip.faces.new((e0, e1, p))
        objs.append(V.bm_to_object(tip, "spike", ("M_iron",)))
    for z in (0.5, 1.3, 2.1, 2.9, 3.5):                            # crossbars
        V.add_box(bm, (-2.0, -0.06, z - 0.06), (2.0, 0.06, z + 0.06))
    objs.append(V.bm_to_object(bm, "grate", ("M_iron",)))
    return objs, {"size": [4, 0.3, 3.9], "origin": "bottom-center"}


def gate_black():
    """The Black Gate itself: two towering iron-black leaves under a common
    lintel, studded and barred, standing a hand's breadth ajar — the veil
    hangs in that breach. 8 m wide, 6 m tall. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    for s, x0, x1 in ((-1, -3.9, -0.12), (1, 0.12, 3.9)):
        V.add_box(bm, (x0, -0.14, 0.0), (x1, 0.14, 5.6))
        # iron bands
        for z in (0.9, 2.4, 3.9):
            V.add_box(bm, (x0 - 0.03, -0.2, z - 0.14), (x1 + 0.03, 0.2, z + 0.14))
        # studs
        for zi in range(4):
            for xi in range(4):
                sx = x0 + 0.5 + xi * (abs(x1 - x0) - 1.0) / 3.0
                V.add_box(bm, (sx - 0.05, -0.24, 0.5 + zi * 1.3), (sx + 0.05, -0.14, 0.6 + zi * 1.3))
    objs.append(V.bm_to_object(bm, "gate_leaves", ("M_iron",)))
    lin = bmesh.new()
    V.add_box(lin, (-4.3, -0.3, 5.6), (4.3, 0.3, 6.4))
    objs.append(V.bm_to_object(lin, "gate_lintel", ("M_stone_dark",)))
    return objs, {"size": [8.6, 0.6, 6.4], "origin": "bottom-center"}


def capstan_base():
    """Winch drum housing: stepped stone base + iron drum wound with chain.
    The bar cross (capstan_bars) rotates above it. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.8, -0.8, 0.0), (0.8, 0.8, 0.18))
    objs.append(V.bm_to_object(bm, "cap_plinth", ("M_stone_dark",)))
    drum = V.loft_rings("cap_drum", [(0.42, 0.18, 10, 0), (0.42, 0.85, 10, 0),
                                     (0.5, 0.9, 10, 0), (0.5, 1.0, 10, 0)], "M_iron")
    objs.append(drum)
    # chain winding: two dark rings around the drum
    for z in (0.4, 0.62):
        ring = V.loft_rings("cap_chain", [(0.46, z, 10, 0), (0.46, z + 0.09, 10, 0)], "M_iron",
                            cap_bottom=False, cap_top=False)
        objs.append(ring)
    return objs, {"size": [1.6, 1.6, 1.0], "origin": "bottom-center"}


def capstan_bars():
    """The rotating bar cross of the capstan (the part you push). Named so a
    puzzle can spin it. Origin at the drum axle (sits atop capstan_base)."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.15, -0.07, 0.0), (1.15, 0.07, 0.14))
    V.add_box(bm, (-0.07, -1.15, 0.0), (0.07, 1.15, 0.14))
    for (x, y) in ((1.15, 0), (-1.15, 0), (0, 1.15), (0, -1.15)):   # worn grip knobs
        V.add_box(bm, (x - 0.11, y - 0.11, -0.03), (x + 0.11, y + 0.11, 0.17))
    objs.append(V.bm_to_object(bm, "cap_bars", ("M_wood",)))
    hub = V.loft_rings("cap_hub", [(0.16, -0.05, 8, 0), (0.14, 0.3, 8, 0)], "M_iron")
    objs.append(hub)
    return objs, {"size": [2.4, 2.4, 0.35], "origin": "axle"}


def battlement_4m():
    """Crenellated parapet strip for wall-tops: low wall + merlons. 4 m run,
    origin bottom-center like the balustrade (seat ON the floor, INSIDE it)."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2.0, -0.22, 0.0), (2.0, 0.22, 0.85))
    for i in range(3):
        x0 = -1.8 + i * 1.4
        V.add_box(bm, (x0, -0.24, 0.85), (x0 + 0.75, 0.24, 1.5))
    objs.append(V.bm_to_object(bm, "battlement", ("M_stone",)))
    return objs, {"size": [4, 0.5, 1.5], "origin": "bottom-center"}


def toll_maul():
    """The Tollkeeper's maul: a long dark haft into a massive square iron
    head, gilt-banded — the hammer that rang the toll. Origin at grip."""
    objs = [V.loft_rings("maul_haft", [(0.035, -1.0, 8, 0), (0.04, 1.15, 8, 0)], "M_wood")]
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.34, 1.05), (0.34, 0.34, 1.75))
    objs.append(V.bm_to_object(bm, "maul_head", ("M_iron",)))
    gm = bmesh.new()
    for z in (1.12, 1.66):
        V.add_box(gm, (-0.36, -0.36, z - 0.045), (0.36, 0.36, z + 0.045))
    objs.append(V.bm_to_object(gm, "maul_bands", ("M_gold",)))
    return objs, {"size": [0.72, 0.72, 2.9], "origin": "grip"}


BUILDERS = {
    "portcullis_4m": portcullis_4m,
    "gate_black": gate_black,
    "capstan_base": capstan_base,
    "capstan_bars": capstan_bars,
    "battlement_4m": battlement_4m,
    "toll_maul": toll_maul,
}
