"""
MOD-GRID Zippo clip - two bands that hold a standard Zippo flat against the plate.

Zippo lies with its large face against the plate, lid up. Two identical bands
clip its cross-section, spaced along its 57.2 mm length.

THE CROSS-SECTION IS A ROUNDED RECTANGLE, NOT AN OBROUND (corrected 2026-10-24).
Every earlier version modelled the case as a stadium - flats top and bottom,
semicircular ends of R6.48 - and none of them fitted. Photographs down the long
axis show the bottom face is a rounded rectangle with roughly R3 corners and a
broad face that is flat nearly edge to edge. An interference sweep against the
old band settled it:

    case corner R6.47  ->   0.003 mm3   (fits: the stadium it was drawn for)
    case corner R6.00  ->  16.9  mm3    jams, low in the cavity
    case corner R3.00  -> 136.3  mm3    cannot seat at all

The overlap sat in the LOWER half, so the case's bottom corners landed on the
cavity's bottom arc and held the whole lighter up - exactly the reported
symptom, riding proud with the arms standing clear all round.

Two things follow, and they are the whole design:

  * The cavity is a rounded rectangle whose corner radius is deliberately
    SQUARER than the case (cav_r 1.5 against a case nearer 3). It therefore
    clears the case everywhere no matter what the real corner radius turns out
    to be, and cannot jam. Chasing the case's exact profile is what failed
    three times; this stops chasing it.
  * Retention is a 45/45 CAPTURE LIP with a rounded tip - NOT a round bead.
    See "why not a bead" below; the bead version was printed and the lighter
    stuck ~2 mm proud.

Also from the pen clip and the earlier Zippo work:

  * Mount is the OFFICIAL BARBED SNAP LEG, copied dimension for dimension.
  * Arms are CONSTANT THICKNESS; the relief slot follows the cavity's bottom
    corner at a fixed offset, then runs straight up and out of the top face.
  * The web under the slot root must stay >= 1.0 mm. Here that is what sets
    base_t: wrapping the slot under a 1.5 mm corner needs 4.5 mm of base.
  * PRINT STANDING ON AN END FACE, lighter axis vertical. Each band is a prism
    along that axis, so every face is a vertical wall - no overhangs, and the
    arms flex within the layer plane rather than across it.
  * Legs sit FLUSH WITH THE BED FACE so nothing starts partway up the print.

WHY NOT A ROUND BEAD (2026-10-25, from the test print of the bead version).
The lighter would not seat: it stuck ~2 mm proud with the arms visibly splayed,
and the band's top edge finished level with the case's top face instead of
standing 1.95 mm above it. The arms were not too weak and the cavity was not
too small. A round bead on a BIG corner radius is a shallow wedge:

  * The bead reached 0.60 mm inboard of the case's side face, i.e. to y 18.43.
    The case's top FLAT only starts at y 19.025 - case_r, about y 16.0. So the
    bead never touched the top face at all; every bit of the capture happened
    on the case's corner ARC.
  * On that arc the contact normal runs centre-to-centre, and it rotates to
    HORIZONTAL at the crest (where the two centres are level, case_r + 0.10 mm
    proud). Near horizontal the normal has no downward component left, so
    friction wins: with mu ~ 0.3 the bead holds the case OUT over the top
    0.83 mm of the stroke (0.65 at case_r 2.0, 1.25 at case_r 4.0). That is a
    self-locking wedge, and ~2 mm proud is exactly where it parks.

A straight 45 deg face cannot do that: its normal is 45 deg below horizontal
for the whole stroke, four times arctan(mu), so it always cams the case down.
The only place the normal can still go horizontal is the tip itself, so the tip
is a 0.40 mm RADIUS (one nozzle width - a knife edge will not print) rather
than a flat land, which shrinks the sticky zone from ~0.83 mm to ~0.23 mm and
puts a strong 45 deg cam immediately below it. Peak splay is unchanged at
0.60 mm, so the stress budget and the pull-out force are unchanged.

Note the earlier rule this reverses in part: "prefer a tangent BEAD to a
pointed lip" was written on the prybar, whose bar has R0.5 edges. There the
bead lands within half a millimetre of the flat and the shallow zone is 0.24 mm
wide. It does not survive a 3 mm corner radius. The rule is really about what
the bead lands on, not about beads.

cav_clear went 0.50 -> 1.00 at the same time. 0.50 total is 0.25/side modelled
and 0.18/side as printed on a 38 mm painted steel case - below this project's
own 0.5 mm floor for anything that slides. The lip does the holding; the walls
should not be touching at all.

case_r is a PHOTO ESTIMATE, but the lip no longer depends on getting it right:
it is placed to clear case_r_min (the SQUAREST plausible case) at seated, so a
rounder case only costs free lift, never a jam. run() sweeps it.

Fusion script entry point: run(_context).
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1

DOC_NAME = 'MOD-GRID Zippo Clip'
TARGET_FOLDER = 'Mod Grid'

PARAM_DEFS = [
    # ---- the lighter ----
    ('zippo_w',          '38.05 mm',  'mm', 'MEASURED across the flats'),
    ('zippo_t',          '12.96 mm',  'mm', 'MEASURED: 12.92-12.96 along its length; use the max so the thickest section still seats'),
    ('zippo_len',        '57.20 mm',  'mm', 'Case length - only sets where the reference body ends'),
    ('case_r',           '2.80 mm',   'mm', 'PHOTO ESTIMATE of the cross-section corner radius, scaled off the known 38.05 width (reads 2.8-3.0). It is NOT 6.48 - the case is a rounded rectangle, not an obround. NOTHING IS BUILT FROM THIS: it is reported and swept only. The lip is placed off case_r_min instead, so being wrong here costs free lift and never a jam.'),
    ('case_r_min',       '2.00 mm',   'mm', 'The SQUAREST corner the case could plausibly have. The capture lip is positioned so that it still clears THIS at seated, which is the recoverable bias: a squarer-than-expected case can never be held proud, while a rounder one only lifts a little further before the lip bites. Lowering it tightens the catch and risks the part not seating.'),
    # ---- cavity: squarer than the case so it cannot jam ----
    ('cav_clear',        '0.40 mm',   'mm', 'BROUGHT IN 1.00 mm ON THE PRINTED PART (2026-10-26, second pass). 1.40 fixed the seating but left the lighter rattling 1.4 mm across the band, and Rob asked for the arms 1 mm closer. 0.20/side modelled = 0.13/side as printed - BELOW this project\'s 0.5 mm floor for a sliding fit, and deliberately so, because the case is MEASURED at 38.05 and the lip, not the walls, does the holding. This is now the first knob to open if the lighter ever feels tight going down the walls. Note cav_hw does NOT move the lip: lip_zt cancels it exactly, so the splay, the insertion force and the stress are all unchanged by this - only the band gets 1 mm narrower. Was 1.40, before that 1.00 and 0.50, which is 0.25/side modelled and 0.18/side as printed - under this project\'s own 0.5 mm floor for a fit that slides, and too tight for a 38 mm painted steel case against a textured ABS wall. The lip holds the case; the walls should not touch.'),
    ('cav_hw',           '(zippo_w + cav_clear) / 2', 'mm', 'Cavity half width'),
    ('cav_r',            '1.50 mm',   'mm', 'Cavity bottom corner radius. SQUARER than the case on purpose: a cavity corner rounder than the case is what jammed every previous version. Also the arc the relief slot follows.'),
    ('base_t',           '6.00 mm',   'mm', 'Base under the lighter. It sets how far the slot root sits above the z=0 face (base_t + cav_r - r_out, want >= 1.5); it does NOT set the root web, which is base_t-independent because the cavity floor and the slot rise together.'),
    # ---- arms and capture bead ----
    ('arm_root',         '2.40 mm',   'mm', '2026-10-29: 2.80 -> 2.40 (7 -> 6 extrusions) to pay for lip_over 0.80. The splay IS the deflection, so doubling the reach doubles the stress; thinning the root takes it from 121% to 116% of the limit AND cuts the press from 50 N to 31 N, which is the number that matters on a part taken out every day. It also costs root web - the -110 wrap means the web is the FLOOR formula, not arm_root - so run() measures it on the solid and the build is only good if it still clears 1.5 mm. Arm thickness AT THE ROOT = 6 extrusions at 0.4. The arm is TAPERED, thick at the base and thinner at the tip, because the bending moment is largest at the root and nearly zero at the lip. A thick root also pushes the relief slot further out, which is what gives the root web its thickness - see root_web().'),
    ('arm_tip',          '1.60 mm',   'mm', 'Arm thickness at the lip = 4 extrusions - the floor, never below it. Keep every flexure wall an integer multiple of the extrusion width and >= 4 of them: 1.2 mm is 2.86 extrusions, so the slicer lays a gap-fill bond line down the middle of the flexure.'),
    ('arm_blend',        '4.00 mm',   'mm', 'Height above the cavity corner over which arm_root blends down to arm_tip. A step here would be a stress riser; blending over several mm keeps the thick material where the moment is and still leaves most of the arm compliant.'),
    ('relief_w',         '1.20 mm',   'mm', 'Relief slot width behind the arm'),
    ('relief_a0',        '-110 deg',  'deg','Relief slot root angle about the cavity corner centre. Past -90 it tucks under the floor and buys arm length, but it also EATS THE ROOT WEB: past -90 the nearest cavity surface is the floor, not the corner arc, so the web stops being arm_root and starts shrinking fast. -135 left only 0.52 mm, which the bed chamfer then cut to 0.016. run() computes it.'),
    ('rail_t',           '3.00 mm',   'mm', 'Outer rail beyond the relief slot. With body_corner_r it sets the top land between slot and fillet: keep that > 2 * first_layer_cham.'),
    ('lip_clear',        '0.40 mm',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Gap between the lip\'s underside and the case\'s top corner when seated, evaluated at case_r_min. Was 0.10, which the printer\'s own 0.07/wall bias cut to 0.05 - near enough to nothing that any error in zippo_t, in base_t or in the corner radius put the lip BACK ON the case and held it proud. 0.40 absorbs 0.57 mm of vertical error before anything touches, which is what makes the lighter sit flat. It costs free lift (0.6 mm at R2.0, 1.2 at R2.8) and nothing else: the arms are still UNLOADED when the case is home, so there is no creep.'),
    ('lip_over',         '0.80 mm',   'mm', '2026-10-29: 0.40 WAS NOT PRINTING. It is one extrusion width and EQUAL to lip_tipr, so the two 45 deg faces never existed and the feature was only the tip radius. Rob measured the Olight band - same defect, lip_over 0.35 - and its printed throat came back as the BORE, i.e. no lip at all; this one is the same disease one notch milder, which is exactly why he reported the Zippo as "still not as tight as I want". 0.80 is TWO extrusion widths, the floor for a feature that has to survive slicing, and it must stay above lip_tipr. Second effect, free: at 0.40 the lip was also too SHORT for its own placement formula - lip_z0 puts the underside LINE lip_clear off the corner arc, and the tangent point (y 18.44) sat inboard of where the real face ended (y 18.79), so the lip stood further off the case than lip_clear claimed and added free lift. At 0.80 the underside reaches y 18.39 and the contact lands on the face the clearance was derived on. Previous note, FIT FIRST (2026-10-26): Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Cut 0.55 -> 0.40: the splay IS the insertion force, and 0.55 took 41 N to press the lighter past both lips. 0.40 takes 29 N and still gives 5.3 kg of pull-out on a 65 g lighter. Earlier: cut 0.60 -> 0.55 on 2026-10-26 when flexure_check started biasing the ARM THICKNESS as well as the deflection: at 0.60 the as-printed stress was 102% of SIG_LIMIT. How far each lip reaches inboard of the case\'s side face - and therefore the splay each arm takes. This is the DEFLECTION, and deflection is what sets the bending stress, so it is budgeted against the stress limit rather than maximised.'),
    ('lip_tipr',         '0.40 mm',   'mm', 'Radius on the lip tip = ONE NOZZLE WIDTH. A knife edge will not print. It also sets the only part of the stroke where the contact normal can reach horizontal: a flat land of width L parks the case for L of travel, a radius parks it for 2*r*sin(arctan mu) ~ 0.23 mm and gives a 45 deg cam immediately below. That difference is the whole fix over the bead version.'),
    ('lip_tip_y',        'zippo_w / 2 - lip_over', 'mm', 'Innermost point of the lip'),
    ('lip_apex_y',       'lip_tip_y - 0.4142135624 * lip_tipr', 'mm', 'Virtual apex where the two 45 deg faces would meet if the tip were not rounded'),
    ('lip_proj',         'cav_hw - lip_apex_y', 'mm', 'How far the apex stands proud of the cavity wall. At 45 deg this is also the RISE of each face, so the lip is 2 * lip_proj tall.'),
    ('lip_z0',           '1.4142135624 * (case_r_min + lip_clear) + zippo_w / 2 + base_t + zippo_t - 2 * case_r_min - cav_hw', 'mm', 'Foot of the capture ramp, where the 45 deg underside leaves the cavity wall. Derived, not chosen: the underside is the line y + z = cav_hw + lip_z0, and this is the lowest it can sit while still standing lip_clear off a case corner of radius case_r_min centred at (zippo_w/2 - r, base_t + zippo_t - r). Lower and a square-cornered case is held proud - the exact failure of the bead version.'),
    ('lip_zt',           'lip_z0 + lip_proj', 'mm', 'Height of the lip tip = where the load is applied to the arm'),
    ('land_h',           '1.00 mm',   'mm', 'Band height above the lip'),
    ('band_len',         '14.0 mm',   'mm', 'Band width along the lighter = part height when printed. Grip force scales with band length and peak stress does NOT, so length is the one free way to buy retention. This is the GRIPPING length; Band A is stop_t longer overall because of the C stop.'),
    # ---- C-shaped retention stop on the bottom band (2026-10-27) ----
    ('stop_t',           '2.50 mm',   'mm', 'Thickness of the C stop along the lighter\'s axis. It sits at Band A\'s BED FACE, i.e. in the first 2.5 mm of the print, so it is laid straight onto the build plate - no overhang anywhere and it helps adhesion. Band A is lengthened by this much so the gripping length stays a full band_len.'),
    ('stop_w',           '3.00 mm',   'mm', 'Limb width of the C. 3.00 survives a 0.50 bed chamfer on both sides with 2 mm left.'),
    ('stop_blend',       '1.50 mm',   'mm', 'Fillet where the C\'s limbs grow out of the cavity floor, and on the inside corners of the C. This is the transition that was wrong in rev E: stop_hw was measured off cav_hw, which ignored that the floor stops being FLAT at cav_hw - cav_r. The limbs landed 0.50 mm from the bottom corner arc, so there was no room for a fillet at all and the junction came out as a cramped sliver.'),
    ('stop_gap',         '1.20 mm',   'mm', 'FLAT floor left outboard of the blend fillet, before the cavity\'s bottom corner arc starts. Together with stop_blend it is what guarantees the transition has somewhere to live. It must also clear the bed chamfer\'s own minimum edge length of 2 * first_layer_cham + 0.1 = 1.10, or that sliver of floor is SKIPPED by the chamfer and comes out as a sharp step between two chamfered edges - which is the same class of artefact this whole rework is fixing. run() reports "0 left sharp" when it is right.'),
    ('stop_h',           '8.00 mm',   'mm', 'How far the C\'s limbs rise above the cavity floor. The lighter\'s end face is 12.96 tall, so this catches the bottom 8 mm of it - far more than a 65 g lighter needs - while leaving the top open so the lighter still drops straight into the band.'),
    ('stop_edge_r',      '0.80 mm',   'mm', 'Round on the C\'s free top edges, so it does not read as a raw extruded U.'),
    ('stop_hw',          'cav_hw - cav_r - stop_blend - stop_gap', 'mm', 'C half width. Measured off the FLAT part of the floor (cav_hw - cav_r), not off the cavity wall, then set back far enough for the blend fillet plus a margin. It also puts the limbs 4.00 mm clear of the cavity walls, which keeps the stop attached to the solid BASE only - a stop reaching the walls would brace the flexing arms right at the root where the bending moment peaks.'),
    ('band_a_len',       'band_len + stop_t', 'mm', 'Band A overall - the stop plus a full gripping length'),
    ('zippo_x0',         'band_a_x + stop_t', 'mm', 'The lighter\'s bottom end, butted against the C stop.'),
    ('band_hw',          'cav_hw + arm_root + relief_w + rail_t', 'mm', 'Band half width - set by the ROOT thickness, which is the widest part of the arm'),
    ('band_h',           'lip_z0 + 2 * lip_proj + land_h', 'mm', 'Band overall height'),
    # ---- layout ----
    ('band_a_x',         '0 mm',      'mm', 'Band A bed face'),
    ('band_cells',       '5',         '',   'Grid cells between the two bands. Went 4 -> 5 when the C stop moved the lighter 5.6 mm down: at 5 cells Band B lands on the lighter at 37.5..51.5 from its bottom end, which is where it sat before, instead of creeping toward the lid.'),
    ('grid_pitch',       '8 mm',      'mm', 'MOD-GRID pitch'),
    ('band_b_x',         'band_a_x + band_cells * grid_pitch', 'mm', 'Band B bed face'),
    ('body_corner_r',    '1.50 mm',   'mm', 'Rounded outer corners'),
    ('first_layer_cham', '0.50 mm',   'mm', 'Elephant-foot chamfer on the bed face'),
    # ---- barbed snap legs, measured off MOD-GRID Olfa holder v4 ----
    ('leg_pair_y',       '12.0 mm',   'mm', 'Leg pairs at +/- this; 24 mm apart = 3 cells'),
    ('leg_clear',        '0.14 mm',   'mm', 'Shrinks the leg LENGTH and SHANK (not the barb). MEASURED: this printer runs 0.07 per wall.'),
    ('leg_hole_len',     '4.90 mm - leg_clear',     'mm', 'Leg extent along the print axis'),
    ('leg_inner_hw',     '1.45 mm',                 'mm', 'Leg inner face from pair centre -> 2.90 gap'),
    ('leg_shank_hw',     '2.39 mm - leg_clear / 2', 'mm', 'Relaxed shank half-span'),
    ('barb_hw',          '3.19 mm',                 'mm', 'Barb peak half-span - NOT reduced, it is meant to squeeze'),
    ('barb_z',           '-3.40 mm',                'mm', 'Barb peak depth below the seating face'),
    ('catch_z',          '-3.10 mm',                'mm', 'Catch face: 0.10 below the 3.00 plate'),
    ('leg_tip_z',        '-4.64 mm',                'mm', 'Leg tip'),
    ('leg_tip_hw',       '2.00 mm - leg_clear / 2', 'mm', 'Tip half-span, sets the ~45 deg lead-in'),
]


class Log(list):
    def append(self, msg):
        print(msg)
        super(Log, self).append(msg)


def vi(e):
    return adsk.core.ValueInput.createByString(e)


def p3(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


def coll(items):
    c = adsk.core.ObjectCollection.create()
    for i in items:
        c.add(i)
    return c


def add_params(design):
    ups = design.userParameters
    out = {}
    for name, expr, units, comment in PARAM_DEFS:
        e = ups.itemByName(name)
        if e:
            e.expression = expr
            out[name] = e
        else:
            out[name] = ups.add(name, vi(expr), units, comment)
    return out


def mmv(P, n):
    return P[n].value / MM


def uv(P, n):
    return P[n].value


def degv(P, n):
    return math.degrees(P[n].value)


def sketch_on(root, plane, name):
    sk = root.sketches.add(plane)
    sk.name = name
    sk.isComputeDeferred = True
    return sk


def finish(sk):
    sk.isComputeDeferred = False
    return [p for p in sk.profiles]


def rect(sk, x0, y0, z0, x1, y1, z1):
    return sk.sketchCurves.sketchLines.addTwoPointRectangle(
        sk.modelToSketchSpace(p3(x0, y0, z0)), sk.modelToSketchSpace(p3(x1, y1, z1)))


def circ(sk, x, y, z, d):
    return sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(p3(x, y, z)), d * MM / 2.0)


def poly(sk, pts):
    lines = sk.sketchCurves.sketchLines
    sp = [sk.modelToSketchSpace(p3(*p)) for p in pts]
    prev = None
    for i in range(len(sp)):
        a = sp[i]
        b = sp[(i + 1) % len(sp)]
        prev = lines.addByTwoPoints(prev.endSketchPoint if prev else a, b)
    return prev


def plane_at_x(root, expr, name):
    i = root.constructionPlanes.createInput()
    i.setByOffset(root.yZConstructionPlane, vi(expr))
    pl = root.constructionPlanes.add(i)
    pl.name = name
    return pl


def rrect_yz(sk, x, hw, z0, z1, r):
    """Rounded rectangle in the YZ plane. Explicit coordinates throughout:
    addByThreePoints may swap an arc's start and end, so a loop closed off an
    arc's SketchPoints closes across itself on the mirrored side."""
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    S = lambda q: sk.modelToSketchSpace(p3(x, q[0], q[1]))
    k = r * (1.0 - math.sqrt(0.5))
    for (cy, cz, sy, sz) in ((hw - r, z0 + r, 1, -1), (hw - r, z1 - r, 1, 1),
                             (-hw + r, z1 - r, -1, 1), (-hw + r, z0 + r, -1, -1)):
        arcs.addByThreePoints(S((cy + sy * r, cz)),
                              S((cy + sy * (r - k), cz + sz * (r - k))),
                              S((cy, cz + sz * r)))
    for a, b in (((hw - r, z0), (-hw + r, z0)), ((hw, z0 + r), (hw, z1 - r)),
                 ((hw - r, z1), (-hw + r, z1)), ((-hw, z0 + r), (-hw, z1 - r))):
        lines.addByTwoPoints(S(a), S(b))


def band_cavity(sk, x, hw, z0, r, lip_y, apex_y, lz0, lzt, tipr, top_z):
    """Cavity cross-section with a 45/45 CAPTURE LIP on each arm.

    Going up the wall: vertical to `lz0`, then a 45 deg face rising INBOARD
    (this is the capture face - its normal points down and inboard, 45 deg
    below horizontal, so it cams the case home instead of wedging it out),
    a `tipr` radius over the tip, then a 45 deg lead-in rising back OUTBOARD,
    then vertical again.

    The predecessor was a half circle tangent to the wall. It was replaced
    because on a case with a ~3 mm corner radius the bead never reaches the
    top face, and on the corner arc its contact normal rotates to horizontal -
    a self-locking wedge that held the printed lighter ~2 mm proud. A straight
    45 deg face holds its angle for the whole stroke; only the tip radius can
    go horizontal, and that is 0.4 mm wide.

    The tip radius is inscribed in the 90 deg corner between the two faces, so
    it never protrudes past either of them: tangent points sit tipr/sqrt(2)
    either side of the apex height, and the innermost point of the arc is
    apex_y + (sqrt(2) - 1) * tipr, which is `lip_y`.
    """
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    S = lambda q: sk.modelToSketchSpace(p3(x, q[0], q[1]))
    k = r * (1.0 - math.sqrt(0.5))
    tg = tipr / math.sqrt(2.0)          # tangent point offset from the apex
    proj = hw - apex_y                  # = rise of each 45 deg face
    for sgn in (1, -1):
        arcs.addByThreePoints(S((sgn * hw, z0 + r)),
                              S((sgn * (hw - k), z0 + k)),
                              S((sgn * (hw - r), z0)))
        arcs.addByThreePoints(S((sgn * (apex_y + tg), lzt - tg)),
                              S((sgn * lip_y, lzt)),
                              S((sgn * (apex_y + tg), lzt + tg)))
        for a, b in (((sgn * hw, z0 + r), (sgn * hw, lz0)),
                     ((sgn * hw, lz0), (sgn * (apex_y + tg), lzt - tg)),
                     ((sgn * (apex_y + tg), lzt + tg), (sgn * hw, lzt + proj)),
                     ((sgn * hw, lzt + proj), (sgn * hw, top_z))):
            lines.addByTwoPoints(S(a), S(b))
    lines.addByTwoPoints(S((-hw + r, z0)), S((hw - r, z0)))
    lines.addByTwoPoints(S((-hw, top_z)), S((hw, top_z)))


def relief_slot(sk, x, side, cy, cz, r_in, r_out, th0, z_top, y_tip, z_blend):
    """Arc around the cavity's bottom corner, then up and out through the top.

    The slot's OUTER edge is vertical, so the rail keeps a constant thickness.
    The INNER edge steps inboard from `r_in` (the root offset) to `y_tip` over
    the blend height, which is what tapers the arm: thick at the root where the
    bending moment is, thinner at the lip where it is nearly zero. The slot
    simply gets wider further up, which costs nothing.
    """
    def Pt(rr, th):
        a = math.radians(th)
        return (side * (cy + rr * math.cos(a)), cz + rr * math.sin(a))

    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    S = lambda q: sk.modelToSketchSpace(p3(x, q[0], q[1]))
    thm = th0 / 2.0
    arcs.addByThreePoints(S(Pt(r_in, th0)), S(Pt(r_in, thm)), S(Pt(r_in, 0.0)))
    arcs.addByThreePoints(S(Pt(r_out, th0)), S(Pt(r_out, thm)), S(Pt(r_out, 0.0)))
    i0 = Pt(r_in, 0.0); o0 = Pt(r_out, 0.0)
    yt = side * y_tip
    for a, b in ((i0, (yt, z_blend)), ((yt, z_blend), (yt, z_top)),
                 ((yt, z_top), (o0[0], z_top)),
                 ((o0[0], z_top), o0), (Pt(r_out, th0), Pt(r_in, th0))):
        lines.addByTwoPoints(S(a), S(b))
    c = Pt((r_in + r_out) / 2.0, th0)
    circ(sk, x, c[0], c[1], r_out - r_in)


def root_web(cav_r, relief_w, arm_root, th0_deg):
    """Thickness of the arm's ANCHORAGE: the material between the relief slot's
    root cap and the cavity.

    Up to -90 deg the slot runs at a constant offset from the cavity corner
    arc, so the web IS arm_root. Past -90 the cap tucks under the floor and the
    nearest cavity surface becomes the FLOOR PLANE, so the web starts shrinking
    and keeps shrinking - and it is independent of base_t, because the floor
    and the slot rise together. At -135 with a 1.6 arm it is 0.52 mm; the bed
    chamfer then takes it to 0.016 and the arm is hanging off a razor. That,
    not bending stress down the arm, is what broke the first prybar clip.
    """
    if th0_deg >= -90.0:
        return arm_root
    r_mid = cav_r + arm_root + relief_w / 2.0
    return -cav_r - r_mid * math.sin(math.radians(th0_deg)) - relief_w / 2.0


def bed_edges_no_relief(bed, ccy, ccz, r_in, r_out, y_vals, min_len,
                        lip_y_max, lip_lo):
    """Bed-face edges minus the relief slot and the capture lip.

    Chamfering 0.5 off both sides of a 1.2 mm slot collapses it, and a 0.5
    chamfer either side of a 0.4 mm lip tip runs through itself. Elephant foot
    inside a relief slot or on a lip at one end of a 14 mm part is harmless.
    """
    def ends(e):
        try:
            return [(v.geometry.y / MM, v.geometry.z / MM)
                    for v in (e.startVertex, e.endVertex)]
        except Exception:
            return []

    keep, short = [], []
    for e in bed.edges:
        pts = ends(e)
        if pts and all(any(abs(abs(y) - yv) < 0.02 for yv in y_vals)
                       for y, _ in pts):
            continue
        if pts and all(z < ccz + 0.02
                       and r_in - 0.02 <= math.hypot(abs(y) - ccy, z - ccz) <= r_out + 0.02
                       for y, z in pts):
            continue
        if pts and all(abs(y) <= lip_y_max + 0.01 and z >= lip_lo - 0.01
                       for y, z in pts):
            continue
        if e.length / MM < min_len - 0.01:
            short.append(e.length / MM)
            continue
        keep.append(e)
    return keep, short


def _ex(root, profs, op, s1, s2=None, parts=None):
    f = root.features.extrudeFeatures
    i = f.createInput(coll(profs), op)
    dd = adsk.fusion.DistanceExtentDefinition.create
    if s2 is not None:
        i.setTwoSidesExtent(dd(vi(s1)), dd(vi(s2)))
    else:
        i.setDistanceExtent(False, vi(s1))
    if parts:
        i.participantBodies = parts
    return f.add(i)


def newbody(root, profs, s1, s2=None):
    return _ex(root, profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, s1, s2)


def cut(root, profs, s1, parts, s2=None):
    return _ex(root, profs, adsk.fusion.FeatureOperations.CutFeatureOperation, s1, s2, parts)


def face_at_x(body, x):
    t = x * MM
    for f in body.faces:
        g = f.geometry
        if g.objectType != adsk.core.Plane.classType():
            continue
        if abs(abs(g.normal.x) - 1.0) < 1e-3 and abs(g.origin.x - t) < 1e-3:
            return f
    return None


def x_corner_edges(body, corners_yz, length_mm):
    found = []
    for e in body.edges:
        g = e.geometry
        if g.objectType != adsk.core.Line3D.classType():
            continue
        d = g.startPoint.vectorTo(g.endPoint)
        if abs(abs(d.x) - d.length) > 1e-6 or abs(d.length - length_mm * MM) > 1e-3:
            continue
        for cy, cz in corners_yz:
            if (abs(g.startPoint.y - cy * MM) < 1e-3
                    and abs(g.startPoint.z - cz * MM) < 1e-3):
                found.append(e)
                break
    return found


def fillet(root, edges, expr):
    if not edges:
        return None
    f = root.features.filletFeatures
    i = f.createInput()
    i.addConstantRadiusEdgeSet(coll(edges), vi(expr), True)
    return f.add(i)


def chamfer(root, edges, expr):
    if not edges:
        return None
    f = root.features.chamferFeatures
    i = f.createInput2()
    i.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll(edges), vi(expr), True)
    return f.add(i)


def add_legs(root, P, body, bed_plane, bed_x, name):
    ihw = mmv(P, 'leg_inner_hw'); shw = mmv(P, 'leg_shank_hw')
    bhw = mmv(P, 'barb_hw'); bz = mmv(P, 'barb_z'); cz_ = mmv(P, 'catch_z')
    tz = mmv(P, 'leg_tip_z'); thw = mmv(P, 'leg_tip_hw'); lpy = mmv(P, 'leg_pair_y')
    sk = sketch_on(root, bed_plane, '%s legs' % name)
    for sg in (-1, 1):
        yc = sg * lpy
        for t in (-1, 1):
            poly(sk, [(bed_x, yc + t * ihw, 0.5), (bed_x, yc + t * ihw, tz),
                      (bed_x, yc + t * thw, tz), (bed_x, yc + t * bhw, bz),
                      (bed_x, yc + t * shw, cz_), (bed_x, yc + t * shw, 0.5)])
    return _ex(root, finish(sk), adsk.fusion.FeatureOperations.JoinFeatureOperation,
               'leg_hole_len', parts=[body])


def build_case(root, P, log):
    """Reference model of the lighter. Not printed - it is here so fitment is
    checked by interference against geometry instead of by arithmetic."""
    w = mmv(P, 'zippo_w'); t = mmv(P, 'zippo_t'); r = mmv(P, 'case_r')
    L = mmv(P, 'zippo_len'); bt = mmv(P, 'base_t')
    x0 = mmv(P, 'zippo_x0')
    pl = plane_at_x(root, 'zippo_x0', 'Case end')
    sk = sketch_on(root, pl, 'Case section')
    rrect_yz(sk, x0, w / 2.0, bt, bt + t, r)
    case = _ex(root, finish(sk),
               adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
               'zippo_len').bodies.item(0)
    case.name = 'Reference - Zippo'
    log.append('Reference case: %.2f x %.2f rounded rectangle, corner R%.2f '
               '(PHOTO ESTIMATE), %.1f long, x %.1f..%.1f - its bottom end BUTTS '
               'AGAINST the C stop' % (w, t, r, L, x0, x0 + L))
    return case


def add_stop(root, P, body, x0, name):
    """C-shaped retention stop at the bottom band's bed face.

    With the plate mounted vertically the lighter can slide DOWN its own axis
    and out of the two bands, which grip its cross-section but do nothing
    axially. This blocks that: a U sitting on the cavity floor at Band A's bed
    face, which the lighter's bottom end face butts against.

    Three things make it a C rather than a solid end wall:
      * It is OPEN AT THE TOP, so the lighter still drops straight down into
        the band. (It could be closed and still allow that - the stop sits at
        a different station along x from the lighter - but open costs nothing
        and leaves a window.)
      * Its limbs stop `stop_gap` short of the cavity wall, so it attaches to
        the solid BASE and never to the flexing arms. A stop that reached the
        walls would brace the arms over its own length, right at the root
        where the bending moment peaks.
      * The window lets a finger through the bed face to push the lighter out.

    It is the first 2.5 mm of the print, laid straight on the build plate, so
    there is no overhang and nothing to support.
    """
    shw = mmv(P, 'stop_hw'); sw = mmv(P, 'stop_w')
    sh = mmv(P, 'stop_h'); bt = mmv(P, 'base_t')
    st = mmv(P, 'stop_t'); blend = mmv(P, 'stop_blend')
    sk = sketch_on(root, plane_at_x(root, 'band_a_x', '%s stop' % name),
                   '%s stop' % name)
    poly(sk, [(x0, -shw, bt), (x0, shw, bt), (x0, shw, bt + sh),
              (x0, shw - sw, bt + sh), (x0, shw - sw, bt + sw),
              (x0, -shw + sw, bt + sw), (x0, -shw + sw, bt + sh),
              (x0, -shw, bt + sh)])
    _ex(root, finish(sk), adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'stop_t', parts=[body])

    # THE TRANSITION. Every edge below runs along X for exactly stop_t, which is
    # how they are picked out - nothing else on the band is that length. The
    # CONCAVE ones are where the stop grows out of the body and are what the
    # blend is for; the convex tops just get a small round so the C does not
    # read as a raw extruded U.
    fillet(root, x_corner_edges(body, [(-shw, bt), (shw, bt),
                                       (-(shw - sw), bt + sw), (shw - sw, bt + sw)],
                                st), 'stop_blend')
    fillet(root, x_corner_edges(body, [(-shw, bt + sh), (shw, bt + sh),
                                       (-(shw - sw), bt + sh), (shw - sw, bt + sh)],
                                st), 'stop_edge_r')
    return 2 * shw, sw, sh


def build_band(root, P, log, x0, name, lkey):
    hw = mmv(P, 'band_hw'); bh = mmv(P, 'band_h'); bl = mmv(P, lkey)
    bt = mmv(P, 'base_t'); cr = mmv(P, 'cav_r'); chw = mmv(P, 'cav_hw')
    ar = mmv(P, 'arm_root'); atip = mmv(P, 'arm_tip'); abl = mmv(P, 'arm_blend')
    rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    lty = mmv(P, 'lip_tip_y'); lay = mmv(P, 'lip_apex_y')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt'); ltr = mmv(P, 'lip_tipr')
    xm = x0 + bl / 2.0
    key = 'band_a_x' if name.endswith('A') else 'band_b_x'

    mid = plane_at_x(root, '%s + %s / 2' % (key, lkey), '%s mid' % name)
    half = '%s / 2' % lkey

    sk = sketch_on(root, mid, '%s body' % name)
    rect(sk, xm, -hw, 0.0, xm, hw, bh)
    body = newbody(root, finish(sk), half, half).bodies.item(0)
    body.name = name
    fillet(root, x_corner_edges(body, [(-hw, 0.0), (hw, 0.0), (-hw, bh), (hw, bh)], bl),
           'body_corner_r')

    sk = sketch_on(root, mid, '%s cavity' % name)
    band_cavity(sk, xm, chw, bt, cr, lty, lay, lz0, lzt, ltr, bh + 2.0)
    cut(root, finish(sk), lkey, [body], s2=lkey)

    # THE ROOT WEB IS THE THING THAT BREAKS. Check it before cutting: a cut
    # that splits a body still reports 0 unhealthy, and a web thinned to a
    # sliver looks perfect in the timeline and in a render.
    cham = mmv(P, 'first_layer_cham')
    web = root_web(cr, rw, ar, ra0)
    slot_bed = (bt + cr) - (cr + ar + rw)
    log.append('%s: ROOT WEB %.2f mm raw, %.2f after the %.2f bed chamfer %s'
               % (name, web, web - cham, cham,
                  'OK' if web - cham >= 1.5 else '** TOO THIN - the arm is hanging '
                  'off a ligament and will tear out. Make relief_a0 less negative '
                  'or arm_root thicker **'))
    log.append('%s: slot root sits %.2f mm above the z=0 face %s'
               % (name, slot_bed,
                  'OK' if slot_bed >= 1.2 else '** TOO THIN - raise base_t **'))
    n_before = root.bRepBodies.count
    sk = sketch_on(root, mid, '%s relief' % name)
    for side in (1, -1):
        relief_slot(sk, xm, side, chw - cr, bt + cr, cr + ar, cr + ar + rw,
                    ra0, bh + 2.0, chw + atip, bt + cr + abl)
    cut(root, finish(sk), lkey, [body], s2=lkey)
    if root.bRepBodies.count != n_before:
        log.append('%s: !! the relief cut SPLIT the body (%d -> %d bodies). The arm '
                   'is no longer attached. Everything measured below is meaningless.'
                   % (name, n_before, root.bRepBodies.count))

    if name.endswith('A'):
        sw_, sl_, sh_ = add_stop(root, P, body, x0, name)
        log.append('%s: C RETENTION STOP %.2f wide x %.2f tall, %.2f limbs, %.2f '
                   'thick, blended into the cavity floor with R%.2f and standing '
                   '%.2f clear of the cavity walls so it never braces the arms. '
                   '%.2f of FLAT floor is left outboard of the blend before the '
                   'R%.2f bottom corner arc starts.'
                   % (name, sw_, sh_, sl_, mmv(P, 'stop_t'), mmv(P, 'stop_blend'),
                      chw - mmv(P, 'stop_hw'), mmv(P, 'stop_gap'), cr))
    bed = face_at_x(body, x0)
    keep, short = bed_edges_no_relief(bed, chw - cr, bt + cr, cr + ar, cr + ar + rw,
                                      (chw + ar, chw + atip, chw + ar + rw),
                                      2 * cham + 0.1, chw, lz0)
    chamfer(root, keep, 'first_layer_cham')
    add_legs(root, P, body, plane_at_x(root, key, '%s bed' % name), x0, name)
    log.append('%s: %.2f wide x %.2f tall x %.2f | cavity %.2f wide, corner R%.2f '
               '(case R%.2f, so the cavity is SQUARER and cannot jam) | arm %.2f at '
               'the root -> %.2f at the tip (%.0f -> %.0f extrusions) | lip 45/45, '
               'tip r%.2f at z %.2f reaching %.2f inboard, ramp foot z %.2f | '
               'chamfer %d edges, %d left sharp'
               % (name, 2 * hw, bh, bl, 2 * chw, cr, mmv(P, 'case_r'), ar, atip,
                  ar / 0.4, atip / 0.4, ltr, lzt, mmv(P, 'lip_over'), lz0,
                  len(keep), len(short)))
    return body


def probe_in(body, x, z, limit=40.0, step=0.005):
    v = 0.0
    while v < limit and body.pointContainment(p3(x, v, z)) == 2:
        v += step
    return v


def probe_out(body, x, y_from, z, limit=12.0, step=0.005):
    v = 0.0
    while v < limit and body.pointContainment(p3(x, y_from + v, z)) == 0:
        v += step
    return v


def clash(tbm, a_src, b_src, matrix=None):
    a = tbm.copy(a_src)
    if matrix is not None:
        tbm.transform(a, matrix)
    b = tbm.copy(b_src)
    try:
        if not tbm.booleanOperation(a, b,
                                    adsk.fusion.BooleanTypes.IntersectionBooleanType):
            return 0.0
        return a.volume / (MM ** 3)
    except Exception:
        return 0.0


def temp_case(tbm, w, t, r, z_floor, x0, x1):
    """Temporary rounded-rectangle prism - the lighter at an arbitrary corner
    radius, for sweeping the fit without rebuilding the timeline."""
    r = max(0.0, min(r, t / 2.0 - 0.01))
    cz = z_floor + t / 2.0
    ex = adsk.core.Vector3D.create(1, 0, 0)
    ey = adsk.core.Vector3D.create(0, 1, 0)
    L = x1 - x0
    c = p3((x0 + x1) / 2.0, 0.0, cz)
    parts = []
    if w - 2 * r > 0.01:
        parts.append(tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
            c, ex, ey, L * MM, (w - 2 * r) * MM, t * MM)))
    if t - 2 * r > 0.01:
        parts.append(tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
            c, ex, ey, L * MM, w * MM, (t - 2 * r) * MM)))
    if r > 0.01:
        for sy in (-1, 1):
            for sz in (-1, 1):
                parts.append(tbm.createCylinderOrCone(
                    p3(x0, sy * (w / 2.0 - r), cz + sz * (t / 2.0 - r)), r * MM,
                    p3(x1, sy * (w / 2.0 - r), cz + sz * (t / 2.0 - r)), r * MM))
    body = parts[0]
    for q in parts[1:]:
        tbm.booleanOperation(body, q, adsk.fusion.BooleanTypes.UnionBooleanType)
    return body


def shift_matrix(dz):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(0.0, 0.0, dz * MM)
    return m


# The first prybar clip arm snapped on its first insertion and this file used
# to blame bending stress for it, concluding that ABS only delivers 17.5 MPa
# here and that the arms therefore had to get THINNER to stay under that.
# Both halves of that were wrong. Measuring the real solid showed the arm was
# anchored on a 0.162 mm ligament: the relief slot had wrapped to -130 deg,
# which left 0.66 mm between its root cap and the cavity floor, and the 0.5 mm
# bed chamfer took almost all of what was left. It tore out at the root; it did
# not yield in bending. See root_web().
#
# So the limit below comes from the material, not from that failure. These arms
# flex WITHIN the layer plane (the bands print standing on an end face) and are
# >= 4 perimeters with no gap-fill bond line down the middle, so the
# across-layer knockdown does not apply: ABS in-plane yield ~40 MPa, 2.5x design
# factor. The working pen clip computes ~9 MPa by this method.
SIG_LIMIT = 15.0
PRINT_BIAS = 0.07   # cavities print ~0.07/wall under, so the lip reaches
                    # FURTHER inboard than modelled and the arm flexes more


def escape_curve(Rc, y_rel, F_arm, mu=0.30, n=2000):
    """Force resisting the case being rolled out past the lip, and the travel.

    2026-10-29. This replaces `pull = 2 * F * 1.8`, where 1.8 is the wedge
    factor of a 45 deg face with friction. The lip's FACE is 45 deg, but the
    lip does not ride on its own face - the capture lands on the case's top
    CORNER ARC (the tip is `lip_over` inboard of the side face, and the flat
    does not begin until `case_r` inboard, which is several times further).
    So the CASE sets the escape ramp, and near the widest point a corner arc
    is a shallow ramp, not a 45 deg one.

    With the lip tip `y_rel` out from the corner centre and the corner radius
    `Rc`, `u` being the tip's height above the corner centre:

        splay  s(u) = sqrt(Rc^2 - u^2) - y_rel
        ramp   ds/dh = u / sqrt(Rc^2 - u^2)
        travel u0 = sqrt(Rc^2 - y_rel^2)
        F(u)  = 2*k*s*(ds/dh + mu) / (1 - mu*ds/dh),   k = F_arm / (Rc - y_rel)

    The old model was ~3.6x optimistic here and 4.8x on the round holder's
    cylinder, where the part radius is bigger and the ramp therefore shallower
    still. The Zippo keeps about 0.6 of its press force as pull-out because a
    2.8 mm corner is a much steeper escape than a 7.55 mm one.
    """
    smax = Rc - y_rel
    if smax <= 0:
        return 0.0, 0.0, 0.0
    k = F_arm / smax
    u0 = math.sqrt(max(Rc * Rc - y_rel * y_rel, 0.0))
    best = (0.0, 0.0)
    for i in range(n + 1):
        u = u0 * i / n
        wv = math.sqrt(max(Rc * Rc - u * u, 1e-9))
        sv = wv - y_rel
        if sv <= 0:
            continue
        slope = u / wv
        f = 2.0 * k * sv * (slope + mu) / max(1.0 - mu * slope, 1e-6)
        if f > best[0]:
            best = (f, u0 - u)
    return best[0], best[1], u0


def arm_profile(cav_r, arm_root, arm_tip, arm_blend, th0_deg, ccz, load_z, n=300):
    """Sample the arm's neutral axis from the slot root up to the lip tip.

    Returns (z, thickness, ds) per station: the wrap at constant arm_root, then
    the straight run blending down to arm_tip over arm_blend.
    """
    th0 = math.radians(th0_deg)
    segs = []
    r_arm = cav_r + arm_root / 2.0
    for i in range(n):
        th = th0 + (0.0 - th0) * (i + 0.5) / n
        segs.append((ccz + r_arm * math.sin(th), arm_root, r_arm * (-th0) / n))
    h = load_z - ccz
    for i in range(n):
        d = h * (i + 0.5) / n
        t = arm_tip if d >= arm_blend else \
            arm_root + (arm_tip - arm_root) * (d / arm_blend)
        segs.append((ccz + d, t, h / n))
    return segs


def flexure_check(log, bl, arm_root, arm_tip, arm_blend, cav_r, th0_deg,
                  ccz, load_z, delta, E=2000.0):
    """Stiffness and peak bending stress for one TAPERED curved arm, unit load.

    A horizontal force at the lip puts a moment F*(load_z - z) on every
    section, so the moment follows VERTICAL distance below the lip - not
    distance along the arm. Peak stress is wherever (load_z - z) / t^2 is
    largest, which on a tapered arm is not automatically the root.
    """
    segs = arm_profile(cav_r, arm_root, arm_tip, arm_blend, th0_deg, ccz, load_z)

    def solve(d, dt=0.0):
        C = sum((load_z - z) ** 2 / (E * bl * (t + dt) ** 3 / 12.0) * ds
                for z, t, ds in segs)
        F = d / C
        peak, where = 0.0, None
        for z, t, ds in segs:
            sig = 6.0 * F * (load_z - z) / (bl * (t + dt) ** 2)
            if sig > peak:
                peak, where = sig, (z, t + dt)
        return F, peak, where

    F, sig, where = solve(delta)
    # AS PRINTED the arm is also THICKER, and that was missing until 2026-10-26.
    # The arm sits between the cavity and the relief slot - BOTH are voids, both
    # print ~PRINT_BIAS/wall undersize, so the material between them grows by
    # 2 * PRINT_BIAS. Stiffness goes as t^3 and stress as t (sigma = 3*E*delta*t
    # / (2*L^2) for an imposed deflection), so ignoring it under-reports the
    # insertion force by ~20% and the stress by ~5%. It is why a part that
    # computes comfortably can still feel too tight to press together by hand.
    Fp, sigp, wp = solve(delta + PRINT_BIAS, 2.0 * PRINT_BIAS)
    log.append('    FLEXURE (tapered curved beam, unit load): %.2f mm root (%.0f '
               'extrusions) -> %.2f tip (%.0f), band %.1f long'
               % (arm_root, arm_root / 0.4, arm_tip, arm_tip / 0.4, bl))
    log.append('      %.2f mm/arm -> %.1f N, peak %.1f MPa at z %.2f where the arm '
               'is %.2f thick' % (delta, F, sig, where[0], where[1]))
    log.append('      as printed (+%.2f deflection AND +%.2f on the arm, which sits '
               'between two voids -> %.2f mm/arm on a %.2f mm section): %.1f N, %.1f '
               'MPa = %.0f%% of the %.0f MPa limit %s'
               % (PRINT_BIAS, 2.0 * PRINT_BIAS, delta + PRINT_BIAS, wp[1], Fp, sigp,
                  100.0 * sigp / SIG_LIMIT, SIG_LIMIT,
                  'OK' if sigp <= SIG_LIMIT else '** OVER - cut lip_over **'))
    return Fp, sigp


MU_SEAT = 0.30      # ABS on a dry painted-steel case. arctan -> 16.7 deg.


def lip_profile_fn(chw, cav_r, bt, lz0, lzt, lip_y, apex_y, tipr):
    """One arm's inner face as y = f(z): floor arc, wall, 45 deg up-and-inboard,
    tip radius, 45 deg up-and-outboard, wall.

    It is single valued in z, which is what makes seat_check() below a
    one-dimensional problem rather than a solid-modelling one.
    """
    proj = chw - apex_y
    cy = apex_y + tipr * math.sqrt(2.0)     # centre of the tip radius
    tg = tipr / math.sqrt(2.0)              # tangent points, either side of lzt

    def f(z):
        if z < bt + cav_r:
            return (chw - cav_r) + math.sqrt(
                max(cav_r ** 2 - (bt + cav_r - z) ** 2, 0.0))
        if z <= lz0 or z >= lzt + proj:
            return chw
        if abs(z - lzt) <= tg:
            return cy - math.sqrt(max(tipr ** 2 - (z - lzt) ** 2, 0.0))
        return chw - (proj - abs(z - lzt))
    return f


def seat_check(log, P):
    """Will the case seat, and can the lip hold it OUT instead?

    This check exists because the previous (round bead) version failed in a way
    nothing was looking for. It seated in the model, cleared on interference,
    and was 8 percent under the stress limit - and the printed lighter still
    stuck about 2 mm proud with the arms splayed.

    The missing physics is friction. Where the capture surface touches the
    case, the contact normal is perpendicular to that surface. Its DOWNWARD
    component is what pulls the case home; friction, up to mu * N, resists.
    So the contact face must stay steeper than arctan(mu) from horizontal or
    the joint is a self-locking wedge and the arms' own spring force parks the
    case part way in.

    A round bead fails this near its crest by construction: the normal runs
    centre to centre, so it rotates through horizontal as the case rises past
    it. On a Zippo's ~3 mm corner radius that shallow region is ~0.8 mm of the
    stroke. A straight 45 deg face holds 45 deg throughout; only the 0.4 mm tip
    radius can go shallow, which is ~0.23 mm of stroke.

    Everything here is as PRINTED, and it is swept across the whole plausible
    corner radius because that number has never been measured.
    """
    w = mmv(P, 'zippo_w'); t = mmv(P, 'zippo_t'); bt = mmv(P, 'base_t')
    chw = mmv(P, 'cav_hw') - PRINT_BIAS
    cav_r = mmv(P, 'cav_r')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt'); tipr = mmv(P, 'lip_tipr')
    lip_y = mmv(P, 'lip_tip_y') - PRINT_BIAS
    apex_y = mmv(P, 'lip_apex_y') - PRINT_BIAS
    f = lip_profile_fn(chw, cav_r, bt, lz0, lzt, lip_y, apex_y, tipr)
    top = bt + t
    lock_deg = math.degrees(math.atan(MU_SEAT))

    def ycase(z, h, R):
        a = z - (top + h - R); b = (bt + h + R) - z
        if a > 0:
            return (w / 2.0 - R) + math.sqrt(max(R * R - a * a, 0.0))
        if b > 0:
            return (w / 2.0 - R) + math.sqrt(max(R * R - b * b, 0.0))
        return w / 2.0

    def splay(h, R, n=400):
        best, bz = -9e9, 0.0
        for i in range(n + 1):
            z = bt + h + t * i / n
            v = ycase(z, h, R) - f(z)
            if v > best:
                best, bz = v, z
        return best, bz

    def face_deg(z):
        e = 0.004
        dy = (f(z + e) - f(z - e)) / (2 * e)
        return 90.0 if abs(dy) < 1e-9 else math.degrees(math.atan(1.0 / abs(dy)))

    log.append('SEATING against the case corner, AS PRINTED (cavity %.2f/wall '
               'under). The contact face must stay steeper than '
               'arctan(mu=%.2f) = %.1f deg, or the arms hold the case OUT.'
               % (PRINT_BIAS, MU_SEAT, lock_deg))
    worst, bad = 0.0, False
    for R in (2.0, 2.5, 3.0, 3.5, 4.0):
        s0, _ = splay(0.0, R)
        rows, h = [], 0.0
        while h <= 6.0:
            rows.append((h,) + splay(h, R))
            h += 0.02
        smax = max(r[1] for r in rows)
        on = next((r[0] for r in rows if r[1] > 0.0), 0.0)
        stick = [r[0] for r in rows if r[1] > 0.02 and face_deg(r[2]) < lock_deg]
        zone = (max(stick) - min(stick) + 0.02) if stick else 0.0
        worst = max(worst, zone)
        bad = bad or s0 > 0.0 or zone > 0.30
        log.append('   case R%.2f: seated clearance %5.2f %s | free lift %.2f | '
                   'peak splay %.2f | sticky zone %.2f mm %s'
                   % (R, -s0, 'OK' if -s0 >= 0.0 else '** HELD PROUD **',
                      on, smax, zone,
                      'tip radius only' if zone <= 0.30 else '** SELF-LOCKING **'))
    log.append('   worst sticky zone %.2f mm. The round bead this replaces was '
               '0.83 mm at R2.8 and 1.25 at R4.0, and the printed part stuck in '
               'it. %s' % (worst, 'OK' if not bad else '** NOT FIXED **'))
    return worst


def measure_root_web(app, body, relief_w, log, label):
    """Narrowest gaps between a relief slot's root cap and any other face.

    This is the check that was missing when the v1 arm broke. The old probe
    walked DOWN from the slot to the bed and reported a healthy number, which
    was true and irrelevant: the anchorage is ABOVE the cap, between it and the
    cavity floor, and the bed chamfer cuts straight into it.

    Direction matters, so classify it rather than report one number:
      ABOVE    the cap -> the arm's anchorage into the base. This is the one
               that broke. Want >= 1.5 mm.
      BELOW    the cap -> material down to the bed face. Want >= 1.2 mm.
      BESIDE   the cap -> usually the opposite slot, i.e. the column between
               them. Loaded in tension, not bending. Want >= 1.2 mm.
    """
    mgr = app.measureManager
    caps = [f for f in body.faces
            if f.geometry.objectType == adsk.core.Cylinder.classType()
            and abs(f.geometry.radius / MM - relief_w / 2.0) < 0.05]
    if not caps:
        log.append('    %s: no slot root cap found to measure' % label)
        return 1e9
    found = []
    for cap in caps:
        cz = cap.geometry.origin.z / MM
        for f in body.faces:
            if f == cap:
                continue
            try:
                r = mgr.measureMinimumDistance(cap, f)
            except Exception:
                continue
            d = r.value / MM
            if d < 1e-4:
                continue          # a face the cap actually joins
            p1, p2 = r.positionOne, r.positionTwo
            dz = (p2.z - p1.z) / MM
            dy = abs(p2.y - p1.y) / MM
            if abs(dz) <= dy:
                kind, want = 'BESIDE', 1.2
            elif dz > 0:
                kind, want = 'ABOVE ', 1.5
            else:
                kind, want = 'BELOW ', 1.2
            found.append((d, kind, want,
                          'y %.2f z %.2f x %.2f' % (p2.y / MM, p2.z / MM, p2.x / MM)))
    found.sort(key=lambda t: t[0])
    best = {}
    for d, kind, want, where in found:
        if kind not in best:
            best[kind] = (d, want, where)
    bad = False
    for kind in ('ABOVE ', 'BELOW ', 'BESIDE'):
        if kind not in best:
            continue
        d, want, where = best[kind]
        ok = d >= want
        bad = bad or not ok
        log.append('    %s %s cap: %.3f mm (want >= %.1f) at %s %s'
                   % (label, kind, d, want, where,
                      'OK' if ok else '** THE ARM HANGS OFF THIS **'))
    return min(d for d, _, _, _ in found) if found else 1e9


def verify_band(app, body, P, log, x0, lkey):
    bt = mmv(P, 'base_t'); cr = mmv(P, 'cav_r'); chw = mmv(P, 'cav_hw')
    ar = mmv(P, 'arm_root'); atip = mmv(P, 'arm_tip'); abl = mmv(P, 'arm_blend')
    rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt'); bl = mmv(P, lkey)
    # The FLEXURE uses the gripping length, not the overall one: Band A is
    # stop_t longer but the lighter only bears on band_len of it, and force
    # scales with the loaded width (stress does not scale with width at all).
    glen = mmv(P, 'band_len')
    w = mmv(P, 'zippo_w')
    xm = x0 + bl / 2.0
    ccy = chw - cr; ccz = bt + cr
    worst = (1e9, '')

    rows = []
    for i in range(5):
        th = -90.0 + i * 90.0 / 4.0
        a = math.radians(th); d = 0.03
        while d < 9.0:
            yy = ccy + (cr + d) * math.cos(a); zz = ccz + (cr + d) * math.sin(a)
            if body.pointContainment(p3(xm, yy, zz)) != 0:
                break
            d += 0.005
        rows.append((th, d))
        if d < worst[0]:
            worst = (d, '%.0f deg on the corner arc' % th)
    log.append('    arm on the corner arc: %s'
               % ', '.join('%.0fdeg=%.2f' % r for r in rows))

    rows = []
    for i in range(5):
        zz = ccz + i * (lz0 - 0.05 - ccz) / 4.0
        yw = probe_in(body, xm, zz)
        d = probe_out(body, xm, yw + 0.005, zz)
        rows.append((zz, d))
        if d < worst[0]:
            worst = (d, 'cavity wall at z=%.2f' % zz)
    log.append('    arm up the wall: %s (tapering %.2f -> %.2f by design)'
               % (', '.join('z%.2f=%.2f' % r for r in rows), ar, atip))
    log.append('    THINNEST ANYWHERE %.2f mm = %.1f perimeters (%s) %s'
               % (worst[0], worst[0] / 0.4, worst[1],
                  'OK' if worst[0] >= atip - 0.05 else '** thinner than arm_tip - '
                  'something is eating the arm **'))

    # The anchorage, measured on the real faces rather than inferred.
    web_calc = root_web(cr, rw, ar, ra0)
    cham = mmv(P, 'first_layer_cham')
    log.append('    root web %.3f mm by geometry, %.3f after the %.2f bed chamfer'
               % (web_calc, web_calc - cham, cham))
    measure_root_web(app, body, rw, log, 'root web')

    cav = 2 * probe_in(body, xm, bt + 3.0)
    gap = 2 * probe_in(body, xm, lzt)
    log.append('    cavity %.3f (case %.2f, %.3f clearance - slip fit, arms relax '
               'when seated) | narrowest across the lip tips %.3f -> the case must '
               'splay the arms %.3f total' % (cav, w, cav - w, gap, w - gap))

    F, sig = flexure_check(log, glen, ar, atip, abl, cr, ra0, ccz, lzt,
                           mmv(P, 'lip_over'))
    push = 2 * F
    # The capture lands on the case's top CORNER ARC, never on the flat, so the
    # CASE sets the escape ramp - not the lip's 45 deg face. See escape_curve().
    rnom = mmv(P, 'case_r')
    y_rel = (w / 2.0 - mmv(P, 'lip_over') - PRINT_BIAS) - (w / 2.0 - rnom)
    pull, at_lift, travel = escape_curve(rnom, y_rel, F)
    log.append('      -> %.0f N (%.1f kg) to PRESS the case in %s, %.0f N (%.1f kg) '
               'to roll it out = %.0fx the lighter\'s %.0f g. Arms are UNLOADED when '
               'seated, so no creep.'
               % (push, push / 9.81,
                  'OK' if push <= 35.0 else '** a firm two-handed press **',
                  pull, pull / 9.81, pull / (65.0 * 9.81 / 1000.0), 65.0))
    log.append('      ESCAPE RAMP over the R%.2f corner: %.2f mm of travel from '
               'seated to free, peaking at %.0f N after %.2f mm. Pull-out is %.2f x '
               'the press force - a corner this size is a far steeper escape than '
               'the round holder\'s 7.55 mm cylinder, which keeps only 0.38.'
               % (rnom, travel, pull, at_lift, pull / max(push, 1e-6)))

    lpy = mmv(P, 'leg_pair_y'); lxm = x0 + mmv(P, 'leg_hole_len') / 2.0
    for z, lab, want in ((-1.5, 'shank', 2 * mmv(P, 'leg_shank_hw')),
                         (mmv(P, 'barb_z'), 'barb ', 2 * mmv(P, 'barb_hw'))):
        v = lpy + mmv(P, 'leg_inner_hw') + 0.03
        while v < lpy + 9.0 and body.pointContainment(p3(lxm, v, z)) == 0:
            v += 0.005
        log.append('    leg %s span %.3f (want %.2f)' % (lab, 2 * (v - lpy), want))
    yp = lpy + mmv(P, 'leg_inner_hw') + 0.3
    v = lxm
    while v > lxm - 10.0 and body.pointContainment(p3(v, yp, mmv(P, 'barb_z'))) == 0:
        v -= 0.005
    log.append('    legs start at x=%.3f, bed is x=%.3f -> %s'
               % (v, x0, 'FLUSH' if abs(v - x0) < 0.02 else 'FLOATING'))


def run(_context: str):
    app = adsk.core.Application.get()
    log = Log()

    rootf = app.data.activeProject.rootFolder
    folder = None
    for f in rootf.dataFolders:
        if f.name.strip().lower() == TARGET_FOLDER.lower():
            folder = f
            break
    if folder is None:
        folder = rootf
    existing = None
    for df in folder.dataFiles:
        if df.name == DOC_NAME:
            existing = df
            break
    if existing is not None:
        doc = app.documents.open(existing)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.timeline.markerPosition = 0
        design.timeline.deleteAllAfterMarker()
        log.append('rebuilding "%s" (was v%s)' % (DOC_NAME, existing.versionNumber))
    else:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        log.append('creating "%s"' % DOC_NAME)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    try:
        design.fusionUnitsManager.distanceDisplayUnits = \
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    except Exception:
        pass
    root = design.rootComponent
    P = add_params(design)

    # lip_over (the reach, and therefore the arm's deflection) is an INPUT
    # budgeted against the stress limit, not "the largest feature that fits".
    # Maximising it is what forced the arms thin in an earlier version.
    cr_case = mmv(P, 'case_r'); w = mmv(P, 'zippo_w'); t = mmv(P, 'zippo_t')
    chw = mmv(P, 'cav_hw'); bt = mmv(P, 'base_t')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt')
    log.append('user parameters: %d' % len(P))
    log.append('case %.2f x %.2f, corner R%.2f (PHOTO ESTIMATE, nothing is built '
               'from it) | cavity %.2f wide, corner R%.2f | capture lip 45/45, tip '
               'r%.2f reaching %.2f inboard of the case face, ramp foot z %.2f, tip '
               'z %.2f, case top face z %.2f'
               % (w, t, cr_case, 2 * chw, mmv(P, 'cav_r'), mmv(P, 'lip_tipr'),
                  mmv(P, 'lip_over'), lz0, lzt, bt + t))
    log.append('lip placed off case_r_min R%.2f (the SQUAREST plausible case) with '
               '%.2f clearance, so a rounder case costs free lift and never a jam'
               % (mmv(P, 'case_r_min'), mmv(P, 'lip_clear')))
    log.append('')
    seat_check(log, P)
    log.append('')

    case = build_case(root, P, log)
    xa = mmv(P, 'band_a_x'); xb = mmv(P, 'band_b_x')
    a = build_band(root, P, log, xa, 'Band A', 'band_a_len')
    b = build_band(root, P, log, xb, 'Band B', 'band_len')
    zx0 = mmv(P, 'zippo_x0'); zl = mmv(P, 'zippo_len')
    log.append('LAYOUT: Band A (with the stop) x %.1f..%.1f, Band B x %.1f..%.1f, '
               '%d cells apart. The lighter runs x %.1f..%.1f, so Band A grips it '
               '0.0..%.1f from its bottom end and Band B %.1f..%.1f, leaving %.1f '
               'of lid proud.'
               % (xa, xa + mmv(P, 'band_a_len'), xb, xb + mmv(P, 'band_len'),
                  int(uv(P, 'band_cells')), zx0, zx0 + zl,
                  mmv(P, 'band_len'), xb - zx0, xb + mmv(P, 'band_len') - zx0,
                  zx0 + zl - (xb + mmv(P, 'band_len'))))

    log.append('')
    for body, x0, nm, lk in ((a, xa, 'Band A', 'band_a_len'),
                             (b, xb, 'Band B', 'band_len')):
        bb = body.boundingBox
        log.append('%-7s X %7.3f..%7.3f  Y %8.3f..%8.3f  Z %7.3f..%7.3f  vol %.1f mm3'
                   % (nm, bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
                      bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM,
                      body.volume / (MM ** 3)))
        verify_band(app, body, P, log, x0, lk)

    tbm = adsk.fusion.TemporaryBRepManager.get()
    log.append('')
    log.append('FITMENT (interference against the reference case)')
    for body, nm in ((a, 'Band A'), (b, 'Band B')):
        v = clash(tbm, case, body)
        log.append('  seated vs %s: %.3f mm3 %s'
                   % (nm, v, 'CLEAR' if v < 0.01 else '** CLASH **'))
    free = lzt + (chw - mmv(P, 'lip_apex_y')) - bt
    for h in (free / 2.0, free):
        v = clash(tbm, case, a, shift_matrix(h))
        log.append('  lifted %.2f mm vs Band A: %.3f mm3  %s'
                   % (h, v, 'clear of the lip' if v < 0.01
                      else 'arms splayed here by design'))

    # How much does the assumed corner radius actually matter? Sketch geometry
    # is frozen numbers, so re-expressing case_r does NOT move the modelled
    # case - build a temporary case at each radius instead. (Doing it the
    # parametric-looking way gave an identical answer for every radius, which
    # is how the mistake showed up.)
    log.append('')
    log.append('SENSITIVITY to the corner radius estimate (cavity is R%.2f, so it '
               'clears any of these):' % mmv(P, 'cav_r'))
    for r in (2.0, 2.5, 3.0, 3.5, 4.0, 6.47):
        tc = temp_case(tbm, w, t, r, bt, zx0, zx0 + zl)
        v = clash(tbm, tc, a)
        play = 0.0
        if v < 0.01:
            lo, hi = 0.0, 4.0
            for _ in range(14):
                md = (lo + hi) / 2.0
                if clash(tbm, tc, a, shift_matrix(md)) < 0.01:
                    lo = md
                else:
                    hi = md
            play = lo
        log.append('   case R%.2f -> seated %7.3f mm3 %s, lifts %.2f mm before the '
                   'lip bites' % (r, v, 'CLEAR' if v < 0.01 else 'CLASH ', play))

    unhealthy = [design.timeline.item(i).name for i in range(design.timeline.count)
                 if design.timeline.item(i).healthState !=
                 adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    log.append('')
    log.append('timeline: %d features, %d unhealthy %s'
               % (design.timeline.count, len(unhealthy), unhealthy or ''))
    log.append('NOTE "Reference - Zippo" is a reference body, NOT printed. '
               'Export only Band A and Band B. THEY ARE NO LONGER IDENTICAL - '
               'Band A carries the C stop and is %.1f long, Band B is %.1f.'
               % (mmv(P, 'band_a_len'), mmv(P, 'band_len')))
    log.append('ORIENTATION: Band A is the BOTTOM of the holder. Its stop is what '
               'stops the lighter sliding out when the plate is vertical, so fit '
               'that band at the low end.')

    if existing is not None:
        doc.save('Rebuilt from modgrid_zippo_clip.py - 45/45 capture lip, '
                 'wider cavity (the round bead self-locked on the case corner)')
    else:
        doc.saveAs(DOC_NAME, folder, 'MOD-GRID Zippo clip, two bands', '')
    log.append('save issued for "%s" in "%s"' % (DOC_NAME, folder.name))
    return '\n'.join(log)
