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
    hangs in that breach. Framed by heavy stone jamb piers, recessed coffer
    panels, and tarnished gilt-bronze rivet bosses & ring-knockers so the
    monumental doors read clearly against the dark stone. 8 m wide, 6 m tall.
    Origin bottom-center."""
    objs = []
    bm_iron = bmesh.new()
    bm_panel = bmesh.new()
    bm_gild = bmesh.new()

    # The breach between the leaves is a real 1.5 m opening (-0.75..0.75).
    # Each leaf spans 3.10 m of width (x = -3.85..-0.75 and 0.75..3.85) and 5.6 m height.
    for s, x0, x1 in ((-1, -3.85, -0.75), (1, 0.75, 3.85)):
        # Core iron door slab
        V.add_box(bm_iron, (x0, -0.12, 0.0), (x1, 0.12, 5.6))
        # Raised outer stile, inner breach stile, and central vertical muntin
        xm = 0.5 * (x0 + x1)
        for sx0, sx1 in ((x0, x0 + 0.24), (xm - 0.11, xm + 0.11), (x1 - 0.24, x1)):
            V.add_box(bm_iron, (sx0, -0.17, 0.0), (sx1, 0.17, 5.6))
        # Heavy horizontal iron cross-bars (bottom rail, 3 intermediate bands, top rail)
        rail_zs = (0.14, 1.35, 2.75, 4.15, 5.42)
        for z in rail_zs:
            V.add_box(bm_iron, (x0 - 0.02, -0.20, z - 0.13), (x1 + 0.02, 0.20, z + 0.13))
        # Recessed bronze-plate coffer fields between stiles and rails (both faces)
        bay_xs = ((x0 + 0.26, xm - 0.13), (xm + 0.13, x1 - 0.26))
        bay_zs = ((0.29, 1.20), (1.50, 2.60), (2.90, 4.00), (4.30, 5.27))
        for bx0, bx1 in bay_xs:
            for bz0, bz1 in bay_zs:
                V.add_box(bm_panel, (bx0, -0.145, bz0), (bx1, 0.145, bz1))
                # Moulded gilt inner fillet rim around each coffer panel so light catches the grid
                t = 0.028
                V.add_box(bm_gild, (bx0, -0.16, bz0), (bx1, 0.16, bz0 + t))
                V.add_box(bm_gild, (bx0, -0.16, bz1 - t), (bx1, 0.16, bz1))
                V.add_box(bm_gild, (bx0, -0.16, bz0), (bx0 + t, 0.16, bz1))
                V.add_box(bm_gild, (bx1 - t, -0.16, bz0), (bx1, 0.16, bz1))
        # Tarnished gilt-bronze pyramid rivet studs along every cross-bar (both faces)
        for z in rail_zs:
            for xi in range(5):
                sx = x0 + 0.20 + xi * (abs(x1 - x0) - 0.40) / 4.0
                V.add_box(bm_gild, (sx - 0.048, -0.235, z - 0.048), (sx + 0.048, 0.235, z + 0.048))
        # Wrought ring-knocker & rosette escutcheon mounted on the inner stile at z = 2.05
        kx = x1 - 0.16 if s < 0 else x0 + 0.16
        V.add_box(bm_gild, (kx - 0.09, -0.22, 1.98), (kx + 0.09, 0.22, 2.16))
        # Hollow square/octagonal knocker ring hanging below the escutcheon (both faces)
        for sy0, sy1 in ((-0.24, -0.18), (0.18, 0.24)):
            V.add_box(bm_gild, (kx - 0.11, sy0, 1.66), (kx + 0.11, sy1, 1.71))
            V.add_box(bm_gild, (kx - 0.11, sy0, 1.95), (kx + 0.11, sy1, 2.00))
            V.add_box(bm_gild, (kx - 0.11, sy0, 1.66), (kx - 0.06, sy1, 2.00))
            V.add_box(bm_gild, (kx + 0.06, sy0, 1.66), (kx + 0.11, sy1, 2.00))
        # Angled reveal on the breach edge (the leaf stands pushed inward)
        ex = -0.75 if s < 0 else 0.75
        V.add_box(bm_iron, (ex - 0.09, 0.12, 0.0), (ex + 0.09, 0.50, 5.6))

    objs.append(V.bm_to_object(bm_iron, "gate_leaves", ("M_iron",)))
    objs.append(V.bm_to_object(bm_panel, "gate_panels", ("M_bronze",)))

    # Monumental stone jamb piers framing the outer edges under the lintel
    bm_stone = bmesh.new()
    bm_trim = bmesh.new()
    for s in (-1, 1):
        px0, px1 = (s * 4.30, s * 3.82) if s < 0 else (s * 3.82, s * 4.30)
        V.add_box(bm_stone, (px0, -0.28, 0.0), (px1, 0.28, 5.6))
        # Stepped plinth base & impost capital on each jamb pier
        V.add_box(bm_trim, (px0 - 0.04, -0.30, 0.0), (px1 + 0.04, 0.30, 0.45))
        V.add_box(bm_trim, (px0 - 0.04, -0.30, 5.25), (px1 + 0.04, 0.30, 5.60))
        for z_quoin in (1.2, 2.5, 3.8):
            V.add_box(bm_trim, (px0 - 0.02, -0.29, z_quoin), (px1 + 0.02, 0.29, z_quoin + 0.32))
    # Heavy stone lintel beam + moulded cornice + keystone block
    V.add_box(bm_stone, (-4.30, -0.30, 5.60), (4.30, 0.30, 6.40))
    V.add_box(bm_trim, (-4.34, -0.32, 5.56), (4.34, 0.32, 5.74))
    V.add_box(bm_trim, (-4.36, -0.34, 6.22), (4.36, 0.34, 6.40))
    V.add_box(bm_trim, (-0.52, -0.33, 5.54), (0.52, 0.33, 6.42))
    # Carved eclipsed-sun ring on the lintel keystone (hollow gilt corona around dark stone disc)
    V.add_box(bm_stone, (-0.20, -0.35, 5.80), (0.20, 0.35, 6.16))
    for sy0, sy1 in ((-0.36, -0.32), (0.32, 0.36)):
        V.add_box(bm_gild, (-0.26, sy0, 5.74), (0.26, sy1, 5.80))
        V.add_box(bm_gild, (-0.26, sy0, 6.16), (0.26, sy1, 6.22))
        V.add_box(bm_gild, (-0.26, sy0, 5.74), (-0.20, sy1, 6.22))
        V.add_box(bm_gild, (0.20, sy0, 5.74), (0.26, sy1, 6.22))

    objs.append(V.bm_to_object(bm_stone, "gate_lintel", ("M_stone_dark",)))
    objs.append(V.bm_to_object(bm_trim, "gate_trim", ("M_stone_trim",)))
    objs.append(V.bm_to_object(bm_gild, "gate_gild", ("M_gild",)))
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
    # the chain-LEAD: a taut run leaving the drum toward the gate it pulls
    # (local -Y = Godot +Z). The puzzle reads by laying the gilded bar of
    # capstan_bars along this lead — a fixed pointer the player can see.
    lead = bmesh.new()
    V.add_box(lead, (-0.06, -1.5, 0.30), (0.06, -0.42, 0.40))
    objs.append(V.bm_to_object(lead, "cap_lead", ("M_iron",)))
    guide = bmesh.new()
    V.add_box(guide, (-0.16, -1.5, 0.0), (0.16, -1.16, 0.5))
    objs.append(V.bm_to_object(guide, "cap_guide", ("M_stone_dark",)))
    return objs, {"size": [1.6, 3.0, 1.0], "origin": "bottom-center"}


def capstan_bars():
    """The rotating bar cross of the capstan (the part you push). Named so a
    puzzle can spin it. Origin at the drum axle (sits atop capstan_base)."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.15, -0.07, 0.0), (1.15, 0.07, 0.14))
    V.add_box(bm, (-0.07, -1.15, 0.0), (0.07, 1.15, 0.14))
    for (x, y) in ((1.15, 0), (-1.15, 0), (0, 1.15)):               # worn grip knobs
        V.add_box(bm, (x - 0.11, y - 0.11, -0.03), (x + 0.11, y + 0.11, 0.17))
    objs.append(V.bm_to_object(bm, "cap_bars", ("M_wood",)))
    # ONE bar is the chain-bar: gilt-capped and ridged (local -Y = Godot +Z at
    # rot 0). The cross is otherwise 90-degree symmetric, so without this the
    # capstan's bearing is unreadable — lay the gilded bar on the base's
    # chain-lead and the wheel is set.
    gild = bmesh.new()
    V.add_box(gild, (-0.13, -1.34, -0.05), (0.13, -1.02, 0.19))
    V.add_box(gild, (-0.05, -1.02, 0.14), (0.05, -0.2, 0.21))
    objs.append(V.bm_to_object(gild, "cap_goldbar", ("M_gold",)))
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
    """The Tollkeeper's maul: a long dark haft into a massive iron bell-hammer
    head with flared striking faces, socket langets, and gilt bronze straps. Origin at grip."""
    objs = [V.loft_rings("maul_haft", [
        (0.038, -1.02, 10, 0), (0.030, -0.92, 10, 0),
        (0.034, 0.85, 10, 0), (0.042, 1.15, 10, 0),
        (0.028, 1.80, 10, 0), (0.006, 1.92, 10, 0),
    ], "M_wood")]
    bm = bmesh.new()
    # Reinforced iron haft socket + langets + top pommel collar
    V.add_box(bm, (-0.055, -0.055, 0.88), (0.055, 0.055, 1.16))
    V.add_box(bm, (-0.050, -0.050, 1.64), (0.050, 0.050, 1.78))
    # Waisted central block + flared striking heads along +-Y
    V.add_box(bm, (-0.18, -0.24, 1.16), (0.18, 0.24, 1.64))
    for sy in (-1, 1):
        V.add_box(bm, (-0.22, sy * 0.22, 1.12), (0.22, sy * 0.34, 1.68))
        V.add_box(bm, (-0.19, sy * 0.33, 1.15), (0.19, sy * 0.37, 1.65))
    objs.append(V.bm_to_object(bm, "maul_head", ("M_iron",)))
    gm = bmesh.new()
    # Gilt bronze bands wrapping both striking necks and waist cross-straps
    for sy in (-1, 1):
        V.add_box(gm, (-0.235, sy * 0.21, 1.105), (0.235, sy * 0.255, 1.695))
    for z in (1.20, 1.60):
        V.add_box(gm, (-0.195, -0.245, z - 0.032), (0.195, 0.245, z + 0.032))
    V.add_box(gm, (-0.065, -0.065, 0.86), (0.065, 0.065, 0.92))
    V.add_box(gm, (-0.062, -0.062, 1.74), (0.062, 0.062, 1.80))
    objs.append(V.bm_to_object(gm, "maul_bands", ("M_gold",)))
    return objs, {"size": [0.48, 0.74, 2.9], "origin": "grip"}


BUILDERS = {
    "portcullis_4m": portcullis_4m,
    "gate_black": gate_black,
    "capstan_base": capstan_base,
    "capstan_bars": capstan_bars,
    "battlement_4m": battlement_4m,
    "toll_maul": toll_maul,
}
