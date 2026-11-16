"""
MOD-GRID Skeletool holder - two bands that hold a Leatherman Skeletool flat
against the plate. Built on the band architecture from the Zippo clip, as
corrected on 2026-10-24.

NO DOWNLOADABLE REFERENCE MODEL OF THE TOOL BODY EXISTS. That was searched for
properly before falling back to specs: Printables, Cults3D, free3d, GrabCAD,
Thingiverse and 3dmdb all refuse automated access, the Sketchfab API returns no
Skeletool at all, and every Skeletool file that does exist anywhere is an
ACCESSORY - hammer mods, bit drivers, blade-open assists, pocket clips - never
the tool body. So the reference body here is built from Leatherman's own
published specification rather than from somebody else's approximate mesh:

    closed length  101.60 mm  (4.00 in)
    width closed    31.50 mm  (1.24 in)
    thickness       13.20 mm  (0.52 in)

The multitool.org wiki quotes 33 x 16 mm instead. The 16 vs 13.20 gap is almost
certainly the REMOVABLE POCKET CLIP, which adds roughly 3 mm to one face. This
design assumes the clip is removed or facing UP, where it projects harmlessly
through the open middle of each band - the lips reach only ~0.65 mm in from
each side, so the centre of the band is wide open. Do NOT lay the tool
clip-side down; it would rock on the clip.

WHAT IS AND IS NOT AN ESTIMATE HERE:

  * tool_w and tool_t are the manufacturer's, so good to a few tenths - but
    they have NOT been caliper-checked, and the Skeletool is sculpted rather
    than a constant extrusion. Two numbers off the real tool would retire all
    remaining doubt: the thickness and the width AT THE TWO BAND POSITIONS.
  * tool_r, the cross-section corner radius, is a guess - and deliberately
    does not matter. Two things make the design insensitive to it, both of
    them lessons paid for on the Zippo:
      - the cavity corner is SQUARER (cav_r 0.30) than any plausible tool
        corner, so the tool cannot land on the cavity's arcs and ride proud.
        This was set to 1.50 first, equal to the guess, and run()'s sweep
        caught it: a tool with R0.2..R1.0 edges CLASHED. Squarer than the
        part, always - the cavity must not be the rounder of the two;
      - RETENTION IS A 45/45 LIP, not a round bead (changed 2026-10-25 after
        the Zippo band printed with a bead and would not seat - the bead's
        contact normal goes horizontal on the part's corner arc and the arms
        then hold the part OUT. See seat_check() and the Zippo script's header.)
      - the lip sits above the tool's top face instead of tangent to
        its corner, so it overhangs the FLAT. On the Zippo the bead WAS derived
        from the corner radius and that single estimate drove everything.
    run() sweeps tool_r 0..4 mm and shows the fit does not move.

Inherited from the corrected Zippo band and NOT re-derived here - full write-up
in research/design-for-fdm-printing.md:

  * Arms are TAPERED, thick at the root (2.80 = 7 extrusions) and thinner at
    the tip (2.00 = 5): the bending moment peaks at the root and is zero at the
    bead. A thick root also pushes the relief slot outboard, which is what
    gives the ROOT WEB its thickness.
  * THE ROOT WEB IS WHAT BREAKS, not the arm. measure_root_web() measures it on
    the real faces and classifies it by direction. The Zippo band had 0.016 mm
    there; the first prybar clip, which snapped on its first insertion, 0.162.
  * The relief slot wraps to -110 deg only. Past -90 the root web stops being
    the arm thickness and collapses, and it does NOT depend on base_t.
  * Stress limit 15 MPa (ABS ~40 MPa in-plane, 2.5x factor), evaluated AS
    PRINTED with the 0.07 mm cavity bias added to the deflection.
  * Mount is the OFFICIAL BARBED SNAP LEG, copied dimension for dimension.
  * PRINT STANDING ON AN END FACE, tool axis vertical. Each band is a prism
    along that axis, so every face is a vertical wall - no overhangs, and the
    arms flex within the layer plane. Legs sit FLUSH with the bed face.

The Skeletool is 142 g, over twice a Zippo, so retention is checked against
that rather than assumed.

Fusion script entry point: run(_context).
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1

DOC_NAME = 'MOD-GRID Skeletool Holder'
TARGET_FOLDER = 'Mod Grid'

PARAM_DEFS = [
    # ---- the tool ----
    ('tool_w',           '31.50 mm',  'mm', 'OFFICIAL LEATHERMAN SPEC, closed (1.24 in). Across the handles - the direction that lies flat on the plate. NOT yet caliper-checked on the actual tool.'),
    ('tool_t',           '13.20 mm',  'mm', 'OFFICIAL LEATHERMAN SPEC, closed overall thickness (0.52 in). This is the dimension the bands reach over. The multitool.org wiki says 16 mm, which is almost certainly WITH the removable pocket clip fitted - see the notes at the top of this file.'),
    ('tool_len',         '101.60 mm', 'mm', 'OFFICIAL LEATHERMAN SPEC, closed length (4.00 in). Only sets where the reference body ends and how far apart the bands can sit.'),
    ('tool_r',           '1.50 mm',   'mm', 'ESTIMATE of the cross-section corner radius. NOTHING IS BUILT FROM IT - it shapes the reference body and run() sweeps it. (An earlier note here claimed the bead "overhangs the flat, never the corner, which is why tool_r drops out". That was WRONG: the bead sat above the top face but only reached 0.55 mm inboard of the side face, and the top flat does not start until tool_r inboard, so every bit of the capture was still on the corner arc. The 45/45 lip that replaced it is what actually makes tool_r drop out.)'),
    ('tool_r_min',       '0.20 mm',   'mm', 'The SQUAREST corner the handle could plausibly have. Set to match cav_r\'s own assumption (R0.30 "squarer than any plausible tool edge") - at 0.50 the sweep showed a 0.20 mm edge CLASHING at seated, i.e. held proud, which is the one failure that must not happen. The cost is ~0.18 mm more free lift. The capture lip is placed so it still clears THIS at seated, which is the recoverable bias: a squarer tool can never be held proud, a rounder one only lifts further before the lip bites.'),
    # ---- cavity: squarer than the tool so it cannot jam ----
    ('cav_clear',        '1.40 mm',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Opened 0.80 -> 1.40 (0.70/side modelled, 0.63 printed). tool_w is a SPEC number, never caliper-checked, so the cavity has to absorb being wrong by half a millimetre. Was 0.50, i.e. 0.25/side modelled and 0.18/side as printed - under this project\'s own 0.5 mm floor for a fit that slides. The lip holds the tool; the walls should not touch.'),
    ('cav_hw',           '(tool_w + cav_clear) / 2', 'mm', 'Cavity half width'),
    ('cav_r',            '0.30 mm',   'mm', 'Cavity bottom corner radius. MUST BE SQUARER THAN THE TOOL, not equal to the guess: a cavity corner ROUNDER than the part lands on the part\'s corners and holds it off the floor, which is exactly what jammed three Zippo versions. run()\'s sweep caught this - at cav_r 1.50 a tool with R0.2..R1.0 edges CLASHED. 0.30 is below any plausible Skeletool edge radius. Also the arc the relief slot follows; a small value lengthens the arm, which is free stress margin.'),
    ('base_t',           '6.00 mm',   'mm', 'Base under the tool. It sets how far the slot root sits above the z=0 face (base_t + cav_r - r_out, want >= 1.5); it does NOT set the root web, which is base_t-independent because the cavity floor and the slot rise together.'),
    # ---- arms and 45/45 capture lip ----
    ('arm_root',         '2.40 mm',   'mm', 'Arm thickness AT THE ROOT = 7 extrusions at 0.4. The arm is TAPERED, thick at the base and thinner at the tip, because the bending moment is largest at the root and nearly zero at the lip. A thick root also pushes the relief slot further out, which is what gives the root web its thickness - see root_web().'),
    ('arm_tip',          '1.60 mm',   'mm', 'Arm thickness at the lip = 5 extrusions. Keep every flexure wall an integer multiple of the extrusion width and >= 4 of them: 1.2 mm is 2.86 extrusions, so the slicer lays a gap-fill bond line down the middle of the flexure.'),
    ('arm_blend',        '4.00 mm',   'mm', 'Height above the cavity corner over which arm_root blends down to arm_tip. A step here would be a stress riser; blending over several mm keeps the thick material where the moment is and still leaves most of the arm compliant.'),
    ('relief_w',         '1.20 mm',   'mm', 'Relief slot width behind the arm'),
    ('relief_a0',        '-110 deg',  'deg','Relief slot root angle about the cavity corner centre. Past -90 it tucks under the floor and buys arm length, but it also EATS THE ROOT WEB: past -90 the nearest cavity surface is the floor, not the corner arc, so the web stops being arm_root and starts shrinking fast. -135 left only 0.52 mm, which the bed chamfer then cut to 0.016. run() computes it.'),
    ('rail_t',           '3.00 mm',   'mm', 'Outer rail beyond the relief slot. With body_corner_r it sets the top land between slot and fillet: keep that > 2 * first_layer_cham.'),
    ('lip_clear',        '0.60 mm',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Gap between the lip\'s underside and the tool\'s top corner when seated, evaluated at tool_r_min. 0.10 was the Zippo\'s value and it was too tight there on a MEASURED case; tool_t here is Leatherman\'s published spec and the multitool.org wiki says 16 mm, so this one needs more. 0.60 absorbs 0.85 mm of error in tool_t before the lip can bear on the tool and hold it proud. It costs free lift and nothing else - the arms are still UNLOADED when the tool is home.'),
    ('lip_over',         '0.80 mm',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Cut 0.55 -> 0.45: the splay IS the insertion force. 23 N to press the tool in, 4.3 kg of pull-out on a 142 g tool. How far each lip reaches inboard of the tool\'s side face - and therefore the splay each arm takes. This IS the deflection, and deflection sets the bending stress, so it is budgeted against SIG_LIMIT rather than maximised. Thinning an arm to buy more reach is exactly the mistake that produced a 0.016 mm root web on the Skeletool band.'),
    ('lip_tipr',         '0.40 mm',   'mm', 'Radius on the lip tip = ONE NOZZLE WIDTH. A knife edge will not print. It also confines the only part of the stroke where the contact normal can reach horizontal - see seat_check(); a round bead lets that happen over ~0.5 mm and the Zippo band printed with one held the lighter 2 mm proud.'),
    ('lip_tip_y',        'tool_w / 2 - lip_over', 'mm', 'Innermost point of the lip'),
    ('lip_apex_y',       'lip_tip_y - 0.4142135624 * lip_tipr', 'mm', 'Virtual apex where the two 45 deg faces would meet if the tip were not rounded'),
    ('lip_proj',         'cav_hw - lip_apex_y', 'mm', 'How far the apex stands proud of the cavity wall. At 45 deg this is also the RISE of each face, so the lip is 2 * lip_proj tall.'),
    ('lip_z0',           '1.4142135624 * (tool_r_min + lip_clear) + tool_w / 2 + base_t + tool_t - 2 * tool_r_min - cav_hw', 'mm', 'Foot of the capture ramp, where the 45 deg underside leaves the cavity wall. Derived, not chosen: the underside is the line y + z = cav_hw + lip_z0, and this is the lowest it can sit while still standing lip_clear off a tool corner of radius tool_r_min.'),
    ('lip_zt',           'lip_z0 + lip_proj', 'mm', 'Height of the lip tip = where the load is applied to the arm'),
    ('land_h',           '1.00 mm',   'mm', 'Band height above the lip'),
    ('band_len',         '14.0 mm',   'mm', 'Band width along the tool = part height when printed. Grip force scales with band length and peak stress does NOT, so length is the one free way to buy retention.'),
    ('band_hw',          'cav_hw + arm_root + relief_w + rail_t', 'mm', 'Band half width - set by the ROOT thickness, which is the widest part of the arm'),
    ('band_h',           'lip_z0 + 2 * lip_proj + land_h', 'mm', 'Band overall height'),
    # ---- layout ----
    ('band_a_x',         '0 mm',      'mm', 'Band A bed face'),
    ('grid_pitch',       '8 mm',      'mm', 'MOD-GRID pitch'),
    ('tool_overhang',    '15.80 mm',  'mm', 'How much tool stands proud of Band A\'s bed face. Frozen at the value the old two-band layout produced - (band_a_x + band_b_x + band_len - tool_len) / 2 with Band B at 7 cells - so that BAND A STILL GRIPS EXACTLY THE SAME PART OF THE HANDLE as the version Rob has printed and likes. Do not "tidy" this to zero without re-checking what the band lands on.'),
    ('tool_x0',          'band_a_x - tool_overhang', 'mm', 'Tool\'s near end'),
    # ---- the POCKET that replaces Band B (2026-10-27) ----
    ('print_bias',       '0.07 mm',   'mm', 'MEASURED on this printer: a cavity comes out 0.07 per wall UNDER nominal. The pocket is modelled oversize by this so the INTERNAL DIMENSIONS PRINT AT THE NUMBERS ROB ASKED FOR, rather than 0.14 under them.'),
    ('pocket_id_w',      '27.60 mm',  'mm', 'Pocket internal WIDTH as it should measure ON THE PRINTED PART. The cut is modelled 2 * print_bias wider than this. Was 30.00, a specified round number set before the tool was measured; the end section then measured 27.00, so 30.00 left 1.50 per side. 27.60 gives 0.30 per side - a slip fit, not a press, because the tool has to SLIDE 13.8 mm into this pocket and anything tighter binds along the way.'),
    ('pocket_id_h',      '8.60 mm',   'mm', 'Pocket internal HEIGHT as it should measure ON THE PRINTED PART. Was 10.00 against a measured 8.00 end section, i.e. 1.90 of headroom. 8.60 leaves 0.50 above the tool and 0.10 under it (pocket_floor_clear), so the tool is still carried by the band and not wedged between floor and roof.'),
    ('pocket_cells',     '9',         '',   'Grid cells from Band A to the pocket mouth = 72 mm, which puts the mouth 13.8 mm short of the tool\'s far end so that much of the tool is captured.'),
    ('pocket_x0',        'band_a_x + pocket_cells * grid_pitch', 'mm', 'Pocket MOUTH = its bed face. The legs are flush with this, and it faces Band A.'),
    ('pocket_floor_clear','0.10 mm',  'mm', 'How far the pocket floor sits below the band\'s cavity floor, so the tool is carried by the band and does not rock on three points.'),
    ('pocket_z0',        'base_t - pocket_floor_clear - print_bias', 'mm', 'Pocket floor, modelled. Prints at base_t - pocket_floor_clear.'),
    ('pocket_z1',        'pocket_z0 + pocket_id_h + 2 * print_bias', 'mm', 'Pocket ceiling, modelled'),
    ('pocket_hw',        'pocket_id_w / 2 + print_bias', 'mm', 'Pocket half width, modelled'),
    ('pocket_r',         '0.30 mm',   'mm', 'Pocket corner radius. SQUARER than any plausible tool edge, same reasoning and same value as cav_r: a cavity corner ROUNDER than the part lands on the part\'s corners and holds it off, which is what jammed three Zippo versions.'),
    ('tip_gap',          '0.50 mm',   'mm', 'Air between the tool\'s end and the blind face. This is the axial stop that positions the tool.'),
    ('pocket_depth',     'tool_x0 + tool_len + tip_gap - pocket_x0', 'mm', 'Cavity depth, derived so the blind face lands tip_gap past the tool\'s end.'),
    ('pocket_end_t',     '2.50 mm',   'mm', 'Material capping the blind end. Printed standing on the mouth this is a ceiling over the cavity, and the slicer bridges its SHORT span - pocket_id_h, 10 mm - not the 30 mm one, so it is within this project\'s own bridge limit.'),
    ('pocket_roof',      '1.50 mm',   'mm', 'Material above the cavity'),
    ('pocket_len',       'pocket_depth + pocket_end_t', 'mm', 'Pocket overall length'),
    ('pocket_h',         'pocket_z1 + pocket_roof', 'mm', 'Pocket overall height'),
    ('pocket_body_hw',   'band_hw',   'mm', 'Same half width as the band so the two bodies look like a set'),
    # ---- the tool's far end, which the pocket has to accept ----
    ('tool_end_w',       '27.00 mm',  'mm', 'MEASURED 2026-10-27. Width of the tool\'s far end, the section the pocket swallows. No longer an assumption derived from the pocket ID.'),
    ('tool_end_t',       '8.00 mm',   'mm', 'MEASURED 2026-10-27. Thickness of the tool\'s far end. Its UNDERSIDE is taken as flush with the rest of the handle, the way the tool lies on the plate - which is what lets one floor plane carry both ends.'),
    ('tool_step_x',      'pocket_x0 - 2.0 mm', 'mm', 'Where the reference body steps down to the end section - just outside the pocket mouth, so the step itself is never inside the pocket.'),
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


def build_tool(root, P, log):
    """Reference model of the tool. Not printed - it is here so fitment is
    checked by interference against geometry instead of by arithmetic."""
    w = mmv(P, 'tool_w'); t = mmv(P, 'tool_t'); r = mmv(P, 'tool_r')
    L = mmv(P, 'tool_len'); bt = mmv(P, 'base_t')
    x0 = mmv(P, 'tool_x0'); xs = mmv(P, 'tool_step_x')
    ew = mmv(P, 'tool_end_w'); et = mmv(P, 'tool_end_t')

    pl = plane_at_x(root, 'tool_x0', 'Tool end')
    sk = sketch_on(root, pl, 'Tool section')
    rrect_yz(sk, x0, w / 2.0, bt, bt + t, r)
    case = _ex(root, finish(sk),
               adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
               'tool_step_x - tool_x0').bodies.item(0)
    case.name = 'Reference - Skeletool'

    # The far end steps DOWN to the section the pocket has to accept. It is an
    # assumption, not a measurement - Rob gave the pocket ID, not the tool - so
    # it is derived from that ID less pocket_fit_clear and labelled as such.
    # Its UNDERSIDE is flush with the rest of the handle, which is how the tool
    # lies on the plate and what lets one floor plane carry both ends.
    pl2 = plane_at_x(root, 'tool_step_x', 'Tool step')
    sk2 = sketch_on(root, pl2, 'Tool end section')
    rrect_yz(sk2, xs, ew / 2.0, bt, bt + et, min(r, et / 2.0 - 0.01))
    _ex(root, finish(sk2), adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'tool_x0 + tool_len - tool_step_x', parts=[case])
    log.append('Reference tool: %.2f x %.2f rounded rectangle, corner R%.2f, '
               '%.1f long, x %.1f..%.1f, stepping down to a MEASURED %.2f x %.2f '
               'at x %.1f' % (w, t, r, L, x0, x0 + L, ew, et, xs))
    return case


def build_band(root, P, log, x0, name):
    hw = mmv(P, 'band_hw'); bh = mmv(P, 'band_h'); bl = mmv(P, 'band_len')
    bt = mmv(P, 'base_t'); cr = mmv(P, 'cav_r'); chw = mmv(P, 'cav_hw')
    ar = mmv(P, 'arm_root'); atip = mmv(P, 'arm_tip'); abl = mmv(P, 'arm_blend')
    rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    lty = mmv(P, 'lip_tip_y'); lay = mmv(P, 'lip_apex_y')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt'); ltr = mmv(P, 'lip_tipr')
    xm = x0 + bl / 2.0
    key = 'band_a_x' if name.endswith('A') else 'band_b_x'

    mid = plane_at_x(root, '%s + band_len / 2' % key, '%s mid' % name)
    half = 'band_len / 2'

    sk = sketch_on(root, mid, '%s body' % name)
    rect(sk, xm, -hw, 0.0, xm, hw, bh)
    body = newbody(root, finish(sk), half, half).bodies.item(0)
    body.name = name
    fillet(root, x_corner_edges(body, [(-hw, 0.0), (hw, 0.0), (-hw, bh), (hw, bh)], bl),
           'body_corner_r')

    sk = sketch_on(root, mid, '%s cavity' % name)
    band_cavity(sk, xm, chw, bt, cr, lty, lay, lz0, lzt, ltr, bh + 2.0)
    cut(root, finish(sk), 'band_len', [body], s2='band_len')

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
    cut(root, finish(sk), 'band_len', [body], s2='band_len')
    if root.bRepBodies.count != n_before:
        log.append('%s: !! the relief cut SPLIT the body (%d -> %d bodies). The arm '
                   'is no longer attached. Everything measured below is meaningless.'
                   % (name, n_before, root.bRepBodies.count))

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
               % (name, 2 * hw, bh, bl, 2 * chw, cr, mmv(P, 'tool_r'), ar, atip,
                  ar / 0.4, atip / 0.4, ltr, lzt, mmv(P, 'lip_over'), lz0,
                  len(keep), len(short)))
    return body


def build_pocket(root, P, log):
    """A blind rectangular socket at the tool's far end, replacing Band B.

    Same idea as the prybar's Tip Nose: one end of the part is captive in a
    pocket and the other snaps into a band. That makes insertion AXIAL, not a
    swing - press the tool into Band A with its far end clear of the mouth,
    then slide it forward until it stops on the blind face. A conforming
    pocket and a swing-in assembly are mutually exclusive, and this is the
    pocket, so it is the swing that goes.

    Printed standing on the MOUTH face, so the cavity is a vertical blind hole
    and the blind end is a ceiling bridged over it. The slicer bridges the
    SHORT span of that opening - pocket_id_h, 10 mm - not the 30 mm one.
    """
    hw = mmv(P, 'pocket_body_hw'); ph = mmv(P, 'pocket_h')
    pl_ = mmv(P, 'pocket_len'); x0 = mmv(P, 'pocket_x0')
    chw = mmv(P, 'pocket_hw'); z0 = mmv(P, 'pocket_z0'); z1 = mmv(P, 'pocket_z1')
    pr = mmv(P, 'pocket_r'); dep = mmv(P, 'pocket_depth')
    cham = mmv(P, 'first_layer_cham'); bias = mmv(P, 'print_bias')
    xm = x0 + pl_ / 2.0

    mid = plane_at_x(root, 'pocket_x0 + pocket_len / 2', 'Pocket mid')
    sk = sketch_on(root, mid, 'Pocket body')
    rect(sk, xm, -hw, 0.0, xm, hw, ph)
    body = newbody(root, finish(sk), 'pocket_len / 2', 'pocket_len / 2').bodies.item(0)
    body.name = 'Tip Pocket'
    fillet(root, x_corner_edges(body, [(-hw, 0.0), (hw, 0.0), (-hw, ph), (hw, ph)],
                                pl_), 'body_corner_r')

    # Cut from the MOUTH plane with the SAME distance both ways. The far side
    # meets no material, so the result is identical whichever way the profile's
    # normal happens to point - which is the only way to make a blind cut that
    # cannot silently come out 2 mm deep.
    mouth = plane_at_x(root, 'pocket_x0', 'Pocket mouth')
    sk = sketch_on(root, mouth, 'Pocket cavity')
    rrect_yz(sk, x0, chw, z0, z1, pr)
    cut(root, finish(sk), 'pocket_depth', [body], s2='pocket_depth')

    bed = face_at_x(body, x0)
    keep = [e for e in bed.edges if e.length / MM >= 2 * cham + 0.1]
    chamfer(root, keep, 'first_layer_cham')
    add_legs(root, P, body, plane_at_x(root, 'pocket_x0', 'Pocket bed'), x0,
             'Tip Pocket')
    log.append('Tip Pocket: %.2f wide x %.2f tall x %.2f long, x %.1f..%.1f | '
               'cavity MODELLED %.2f x %.2f (z %.2f..%.2f, corner R%.2f) -> PRINTS '
               '%.2f x %.2f, which is the %.2f x %.2f ID asked for | %.2f deep, '
               'blind face x %.1f | chamfer %d edges'
               % (2 * hw, ph, pl_, x0, x0 + pl_, 2 * chw, z1 - z0, z0, z1, pr,
                  2 * chw - 2 * bias, (z1 - z0) - 2 * bias, mmv(P, 'pocket_id_w'),
                  mmv(P, 'pocket_id_h'), dep, x0 + dep, len(keep)))
    return body


def verify_pocket(body, P, log):
    x0 = mmv(P, 'pocket_x0'); dep = mmv(P, 'pocket_depth')
    z0 = mmv(P, 'pocket_z0'); z1 = mmv(P, 'pocket_z1')
    bias = mmv(P, 'print_bias'); bt = mmv(P, 'base_t')
    xm = x0 + dep / 2.0
    zc = (z0 + z1) / 2.0
    wide = 2 * probe_in(body, xm, zc)
    # walk up the centreline for the cavity height
    lo = zc
    while lo > -5.0 and body.pointContainment(p3(xm, 0.0, lo)) == 2:
        lo -= 0.005
    hi = zc
    while hi < 40.0 and body.pointContainment(p3(xm, 0.0, hi)) == 2:
        hi += 0.005
    log.append('    cavity at mid depth: %.3f wide x %.3f tall (z %.3f..%.3f) '
               '-> prints %.2f x %.2f %s'
               % (wide, hi - lo, lo, hi, wide - 2 * bias, (hi - lo) - 2 * bias,
                  'OK' if abs(wide - 2 * bias - mmv(P, 'pocket_id_w')) < 0.02
                  and abs((hi - lo) - 2 * bias - mmv(P, 'pocket_id_h')) < 0.02
                  else '** not the ID asked for **'))
    # the blind face: walk along the axis until it goes solid
    v = x0 + 0.05
    while v < x0 + 60.0 and body.pointContainment(p3(v, 0.0, zc)) == 2:
        v += 0.005
    log.append('    blind face at x %.3f (wanted %.3f), so the cavity is %.2f deep '
               'and %.2f mm of tool is captured %s'
               % (v, x0 + dep, v - x0, mmv(P, 'tool_x0') + mmv(P, 'tool_len') - x0,
                  'OK' if abs(v - (x0 + dep)) < 0.05 else '** THE CUT WENT THE '
                  'WRONG WAY - the pocket is not the depth it should be **'))
    log.append('    floor z %.3f, %.2f below the band\'s cavity floor at %.2f, so '
               'the tool is carried by the band and cannot rock on three points'
               % (lo, bt - lo, bt))
    ew = mmv(P, 'tool_end_w'); et = mmv(P, 'tool_end_t')
    pw = wide - 2 * bias; ph = (hi - lo) - 2 * bias
    log.append('    AS PRINTED against the MEASURED %.2f x %.2f end section: '
               '%.2f per side on width, %.2f of headroom (tool top z %.2f, ceiling '
               '%.2f). %s'
               % (ew, et, (pw - ew) / 2.0, ph - et - mmv(P, 'pocket_floor_clear'),
                  bt + et, hi - bias,
                  'Loose, because the ID was specified rather than fitted - '
                  'pocket_id_w/pocket_id_h are one line each if a snugger pocket '
                  'is wanted.' if (pw - ew) / 2.0 > 0.8 else 'Snug.'))
    lpy = mmv(P, 'leg_pair_y'); lxm = x0 + mmv(P, 'leg_hole_len') / 2.0
    for z, lab, want in ((-1.5, 'shank', 2 * mmv(P, 'leg_shank_hw')),
                         (mmv(P, 'barb_z'), 'barb ', 2 * mmv(P, 'barb_hw'))):
        q = lpy + mmv(P, 'leg_inner_hw') + 0.03
        while q < lpy + 9.0 and body.pointContainment(p3(lxm, q, z)) == 0:
            q += 0.005
        log.append('    leg %s span %.3f (want %.2f)' % (lab, 2 * (q - lpy), want))
    q = lxm
    yp = lpy + mmv(P, 'leg_inner_hw') + 0.3
    while q > lxm - 10.0 and body.pointContainment(p3(q, yp, mmv(P, 'barb_z'))) == 0:
        q -= 0.005
    log.append('    legs start at x=%.3f, bed is x=%.3f -> %s'
               % (q, x0, 'FLUSH' if abs(q - x0) < 0.02 else 'FLOATING'))


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
    """Temporary rounded-rectangle prism - the tool at an arbitrary corner
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


def escape_curve(part_r, reach, F_arm, mu=0.30, n=2000):
    """Force resisting the tool being rolled out past the lip, and the travel.

    2026-10-29, replacing `pull = 2 * F * 1.8`. 1.8 is the wedge factor of a
    45 deg face with friction, and it is right ONLY when the lip actually
    overhangs the part's top FLAT. When the capture lands on the part's top
    CORNER ARC instead - which is the usual case, because the flat does not
    begin until `part_r` inboard of the side face - the PART sets the escape
    ramp, and near the widest point an arc is far shallower than 45 deg.

    Two branches, chosen by where the tip lands:

      tip past the corner centre (reach >= part_r):  it rides the lip's own
        45 deg underside, ds/dh = 1, so F = 2*F_arm*(1+mu)/(1-mu). This is
        the strong case and the one the Skeletool gets, because the tool is
        nearly square - the opposite of the round holder's 7.55 mm cylinder,
        which keeps only 0.38 of the press force.

      tip on the arc:  with y_rel = part_r - reach and u the tip's height
        above the corner centre,
            s(u) = sqrt(part_r^2 - u^2) - y_rel,  ds/dh = u / sqrt(...)
            F(u) = 2*k*s*(ds/dh + mu) / (1 - mu*ds/dh)
        The denominator goes to zero at ds/dh = 1/mu (73 deg): past that the
        contact SELF-LOCKS and cannot be slid out at all, so the slope is
        capped there rather than reported as an infinite force.

    Returns (peak force N, lift at the peak, total travel, where it lands).
    """
    if reach <= 0:
        return 0.0, 0.0, 0.0, 'no lip'
    y_rel = part_r - reach
    if y_rel <= 0.0:
        return (2.0 * F_arm * (1.0 + mu) / (1.0 - mu), reach, reach,
                'on the FLAT - the lip rides its own 45 deg face')
    k = F_arm / reach
    u0 = math.sqrt(max(part_r * part_r - y_rel * y_rel, 0.0))
    slope_cap = 1.0 / mu - 1e-6
    best = (0.0, 0.0)
    for i in range(n + 1):
        u = u0 * i / n
        wv = math.sqrt(max(part_r * part_r - u * u, 1e-9))
        sv = wv - y_rel
        if sv <= 0:
            continue
        slope = min(u / wv, slope_cap)
        f = 2.0 * k * sv * (slope + mu) / (1.0 - mu * slope)
        if f > best[0]:
            best = (f, u0 - u)
    return best[0], best[1], u0, 'on the corner arc'


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


MU_SEAT = 0.30      # ABS on dry steel. arctan -> 16.7 deg.


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
    """Will the tool seat, and can the lip hold it OUT instead?

    This check exists because the previous (round bead) version failed in a way
    nothing was looking for. It seated in the model, cleared on interference,
    and was 8 percent under the stress limit - and the printed lighter still
    stuck about 2 mm proud with the arms splayed.

    The missing physics is friction. Where the capture surface touches the
    case, the contact normal is perpendicular to that surface. Its DOWNWARD
    component is what pulls the tool home; friction, up to mu * N, resists.
    So the contact face must stay steeper than arctan(mu) from horizontal or
    the joint is a self-locking wedge and the arms' own spring force parks the
    case part way in.

    A round bead fails this near its crest by construction: the normal runs
    centre to centre, so it rotates through horizontal as the tool rises past
    it. On a Zippo band's ~3 mm corner radius that shallow region is ~0.8 mm of the
    stroke. A straight 45 deg face holds 45 deg throughout; only the 0.4 mm tip
    radius can go shallow, which is ~0.23 mm of stroke.

    Everything here is as PRINTED, and it is swept across the whole plausible
    corner radius because that number has never been measured.
    """
    w = mmv(P, 'tool_w'); t = mmv(P, 'tool_t'); bt = mmv(P, 'base_t')
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

    log.append('SEATING against the tool corner, AS PRINTED (cavity %.2f/wall '
               'under). The contact face must stay steeper than '
               'arctan(mu=%.2f) = %.1f deg, or the arms hold the tool OUT.'
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
        log.append('   tool R%.2f: seated clearance %5.2f %s | free lift %.2f | '
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


def verify_band(app, body, P, log, x0):
    bt = mmv(P, 'base_t'); cr = mmv(P, 'cav_r'); chw = mmv(P, 'cav_hw')
    ar = mmv(P, 'arm_root'); atip = mmv(P, 'arm_tip'); abl = mmv(P, 'arm_blend')
    rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt'); bl = mmv(P, 'band_len')
    w = mmv(P, 'tool_w')
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
               'when seated) | narrowest across the lip tips %.3f -> the tool must '
               'splay the arms %.3f total' % (cav, w, cav - w, gap, w - gap))

    F, sig = flexure_check(log, bl, ar, atip, abl, cr, ra0, ccz, lzt,
                           mmv(P, 'lip_over'))
    push = 2 * F
    # NOT 2*F*1.8 - that assumes the lip overhangs the tool's top FLAT. Whether
    # it does depends on tool_r, which has never been measured, so report BOTH
    # ends of the plausible range. See escape_curve().
    reach = mmv(P, 'lip_over') + PRINT_BIAS
    log.append('      -> %.0f N (%.1f kg) to PRESS the tool in %s. Arms are '
               'UNLOADED when seated, so no creep.'
               % (push, push / 9.81,
                  'OK' if push <= 35.0 else '** over a comfortable two-finger press **'))
    for rr in (mmv(P, 'tool_r_min'), mmv(P, 'tool_r'), 2.0 * mmv(P, 'tool_r')):
        pk, at_lift, travel, where = escape_curve(rr, reach, F)
        log.append('      ESCAPE at tool_r %.2f: %.0f N (%.1f kg) = %.0fx the '
                   'tool\'s %.0f g, %.2f mm of travel, peak after %.2f mm - %s'
                   % (rr, pk, pk / 9.81, pk / (142.0 * 9.81 / 1000.0), 142.0,
                      travel, at_lift, where))
    log.append('      tool_r is a GUESS, and it is what decides which of those you '
               'get: the flat begins tool_r inboard of the side face, so a square '
               'tool puts the lip on its own 45 deg cam and a round one puts it on '
               'a shallow arc. One caliper reading on an edge settles it.')

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

    cr_tool = mmv(P, 'tool_r'); w = mmv(P, 'tool_w'); t = mmv(P, 'tool_t')
    chw = mmv(P, 'cav_hw'); bt = mmv(P, 'base_t')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt')
    top = bt + t
    log.append('user parameters: %d' % len(P))
    log.append('tool %.2f wide x %.2f thick x %.1f long (OFFICIAL LEATHERMAN SPEC, '
               'NOT caliper-checked) | corner R%.2f is a guess and nothing is built '
               'from it' % (w, t, mmv(P, 'tool_len'), cr_tool))
    log.append('cavity %.2f wide, corner R%.2f (SQUARER than the tool, so it cannot '
               'jam) | capture lip 45/45, tip r%.2f reaching %.2f inboard of the '
               'tool face, ramp foot z %.2f, tip z %.2f, tool top face z %.2f'
               % (2 * chw, mmv(P, 'cav_r'), mmv(P, 'lip_tipr'), mmv(P, 'lip_over'),
                  lz0, lzt, top))
    log.append('lip placed off tool_r_min R%.2f (the SQUAREST plausible handle) with '
               '%.2f clearance, so a rounder tool costs free lift and never a jam'
               % (mmv(P, 'tool_r_min'), mmv(P, 'lip_clear')))
    log.append('')
    seat_check(log, P)
    log.append('')

    case = build_tool(root, P, log)
    xa = mmv(P, 'band_a_x')
    a = build_band(root, P, log, xa, 'Band A')
    b = build_pocket(root, P, log)
    log.append('LAYOUT: Band A (snap) x %.1f..%.1f, Tip Pocket x %.1f..%.1f, '
               '%d cells apart at %.0f mm pitch. The tool runs x %.1f..%.1f, so '
               'Band A grips it %.1f..%.1f from its near end and the pocket '
               'swallows the last %.1f mm.'
               % (xa, xa + mmv(P, 'band_len'), mmv(P, 'pocket_x0'),
                  mmv(P, 'pocket_x0') + mmv(P, 'pocket_len'),
                  int(uv(P, 'pocket_cells')), mmv(P, 'grid_pitch'),
                  mmv(P, 'tool_x0'), mmv(P, 'tool_x0') + mmv(P, 'tool_len'),
                  mmv(P, 'tool_overhang'),
                  mmv(P, 'tool_overhang') + mmv(P, 'band_len'),
                  mmv(P, 'tool_x0') + mmv(P, 'tool_len') - mmv(P, 'pocket_x0')))

    log.append('')
    for body, nm in ((a, 'Band A'), (b, 'Tip Pocket')):
        bb = body.boundingBox
        log.append('%-11s X %7.3f..%7.3f  Y %8.3f..%8.3f  Z %7.3f..%7.3f  vol %.1f mm3'
                   % (nm, bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
                      bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM,
                      body.volume / (MM ** 3)))
        if nm == 'Band A':
            verify_band(app, body, P, log, xa)
        else:
            verify_pocket(body, P, log)

    tbm = adsk.fusion.TemporaryBRepManager.get()
    log.append('')
    log.append('FITMENT (interference against the reference tool)')
    for body, nm in ((a, 'Band A'), (b, 'Tip Pocket')):
        v = clash(tbm, case, body)
        log.append('  seated vs %s: %.3f mm3 %s'
                   % (nm, v, 'CLEAR' if v < 0.01 else '** CLASH **'))
    # Insertion is AXIAL, like the prybar: press the tool into Band A with its
    # far end clear of the mouth, then slide forward until it stops. Check the
    # tool is clear of the pocket at every stage of that slide.
    log.append('  slide in (tool drawn back along its axis, then pushed home):')
    for back in (2.0, 6.0, 14.0, 18.0):
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(-back * MM, 0.0, 0.0)
        v1 = clash(tbm, case, b, m); v2 = clash(tbm, case, a, m)
        log.append('      back %4.1f mm   vs pocket %.3f   vs band %.3f   %s'
                   % (back, v1, v2, 'clear' if max(v1, v2) < 0.01 else '** FOULS **'))
    free_x = mmv(P, 'tool_x0') + mmv(P, 'tool_len') - mmv(P, 'pocket_x0')
    log.append('      -> the tool must be drawn back %.1f mm to clear the mouth '
               'before it can be pressed into the band' % free_x)
    free = lzt + (chw - mmv(P, 'lip_apex_y')) - bt
    for h in (free / 2.0, free):
        v = clash(tbm, case, a, shift_matrix(h))
        log.append('  lifted %.2f mm vs Band A: %.3f mm3  %s'
                   % (h, v, 'clear of the lip' if v < 0.01
                      else 'arms splayed here by design'))

    # How much does the assumed corner radius actually matter? Sketch geometry
    # is frozen numbers, so re-expressing tool_r does NOT move the modelled
    # case - build a temporary case at each radius instead. (Doing it the
    # parametric-looking way gave an identical answer for every radius, which
    # is how the mistake showed up.)
    log.append('')
    log.append('SENSITIVITY to the corner radius GUESS. The cavity is R%.2f and the '
               'lip is placed off tool_r_min, so seating must stay CLEAR throughout:'
               % mmv(P, 'cav_r'))
    tl = mmv(P, 'tool_len')
    tx0 = mmv(P, 'tool_x0')
    for r in (0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
        tc = temp_case(tbm, w, t, r, bt, tx0, tx0 + tl)
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
        log.append('   tool R%.2f -> seated %7.3f mm3 %s, lifts %.2f mm before the '
                   'lip bites' % (r, v, 'CLEAR' if v < 0.01 else 'CLASH ', play))

    unhealthy = [design.timeline.item(i).name for i in range(design.timeline.count)
                 if design.timeline.item(i).healthState !=
                 adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    log.append('')
    log.append('timeline: %d features, %d unhealthy %s'
               % (design.timeline.count, len(unhealthy), unhealthy or ''))
    log.append('NOTE "Reference - Skeletool" is a reference body, NOT printed. '
               'Export only "Band A" and "Tip Pocket".')
    log.append('ASSEMBLY (axial, like the prybar - a conforming pocket and a '
               'swing-in are mutually exclusive): press the tool down into Band A '
               'with its far end clear of the pocket mouth, then slide it forward '
               'until it stops on the blind face.')

    if existing is not None:
        doc.save('Rebuilt from modgrid_zippo_clip.py - rounded-rectangle cavity')
    else:
        doc.saveAs(DOC_NAME, folder, 'MOD-GRID Skeletool clip, two bands', '')
    log.append('save issued for "%s" in "%s"' % (DOC_NAME, folder.name))
    return '\n'.join(log)
