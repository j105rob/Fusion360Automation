"""
MOD-GRID prybar holder - a tip socket and an end clip for "The Mighty Bar".

The bar lies FLAT against the plate, large face down, and is fitted in two
moves: thread the tapered tip through the SOCKET, then press the square end
down into the CLIP.

WHY THE CLIP HAS NO LIP OVER THE BAR'S TOP FACE
-----------------------------------------------
A lipped C-clip and a tip socket are kinematically incompatible. With the tip
captured, the square end can only descend by the whole bar ROTATING about the
socket. To get under a lip at the bar's top face the square end must drop a
full bar_t, which over this lever needs a tilt the socket cannot give without
becoming sloppy. So the clip is a PINCH: parallel arms, throat narrower than
the bar by arm_spread, gripping the bar's lower grip_h on its flat sides. The
bar's width presented to the arms is the same at any tilt, so the descent is
continuous and the socket only has to allow the swing itself. Grip is friction
from ~13 N of squeeze: about 400 g of hold on a ~35 g bar.

WHY THE SOCKET IS SHORT AND HAS HEADROOM
----------------------------------------
Socket length and headroom set the available tilt (atan(sleeve_hr/slv_len)).
A long socket swallows the tapered tip but kills the tilt. This one is short,
sits on FULL-SECTION bar just before the taper starts, and leaves the tip
protruding - which also makes it insensitive to the taper geometry. run()
prints the tilt budget: available vs required.

Everything else follows the pen clip and Zippo clip
(research/modgrid-edc-system.md, research/design-for-fdm-printing.md):

  * Mount is the OFFICIAL BARBED SNAP LEG, copied dimension for dimension.
  * Arms are CONSTANT THICKNESS - the relief slot follows the cavity's bottom
    corner arc at a fixed offset, then runs straight up. A straight slot beside
    a curved cavity makes a wedge that thins exactly where it is loaded.
  * Slot root is ROUNDED (sector + a capping circle) - no V-notch stress riser.
  * PRINT STANDING ON AN END FACE, bar axis vertical. Both bodies are prisms
    along that axis, so every face is a vertical wall: no overhangs, no
    support, and the arms flex WITHIN the layer plane, never across it.
  * Legs sit FLUSH WITH THE BED FACE so nothing starts partway up the print.
  * Both bed faces are the -X end, so both parts print the same way up.

BAR DIMENSIONS ARE MEASURED (2026-10-24): 6.0 mm square, 72.0 long, with a
SINGLE-SIDED wedge starting 55 mm from the square end and running to a 0.5 mm
point. The opposite face is flat the whole length, and that is the face that
goes against the plate.

Fusion script entry point: run(_context).
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1

DIAG = False

DOC_NAME = 'MOD-GRID Prybar Holder'
TARGET_FOLDER = 'Mod Grid'

PARAM_DEFS = [
    # ---- the bar itself: PHOTO ESTIMATES, replace with caliper readings ----
    ('bar_w',            '6.0 mm',    'mm', 'MEASURED. Bar width, the dimension ACROSS the plate. The clip pinches this.'),
    ('bar_t',            '6.0 mm',    'mm', 'MEASURED. Bar thickness, standing off the plate. The bar is 6 mm SQUARE.'),
    ('bar_len',          '72.0 mm',   'mm', 'MEASURED, exactly 72. Sets where the nose sits and how much slack there is before the point bottoms out.'),
    ('hole_x',           '2.0 mm',    'mm', 'MEASURED. Near edge of the lanyard slot, from the square end.'),
    ('hole_len',         '6.5 mm',    'mm', 'MEASURED. Slot length along the bar -> it runs x 2.0..8.5.'),
    ('hole_inset',       '1.5 mm',    'mm', 'MEASURED. Slot edge to the top and bottom faces, so the slot is bar_t - 2*hole_inset = 3.0 tall.'),
    ('hole_r',           '0.5 mm',    'mm', 'MEASURED. Slot corner radius - part of the 0.5 fillet carried over the whole bar.'),
    ('bar_edge_r',       '0.5 mm',    'mm', 'MEASURED. R0.5 on the whole bar. On the cross-section this leaves the side faces flat only between z 4.5 and 9.5, and the TOP FACE only 5.0 wide - which is why the capture lip has to reach 0.8 mm in to get a worthwhile bite.'),
    ('wedge_x',          '55.0 mm',   'mm', 'MEASURED. Where the wedge begins, from the square end. The bar is a constant 6 mm square up to here - there is NO width taper (what looked like one in the photos was the wedge face seen foreshortened).'),
    ('wedge_len',        'bar_len - wedge_x', 'mm', 'Wedge length'),
    ('tip_t',            '0.5 mm',    'mm', 'MEASURED. Thickness at the very point. The wedge is on ONE FACE ONLY, so the opposite face stays flat the whole length - that flat face goes against the plate.'),
    # ---- fit ----
    ('fit_adj',          '0.00 mm',   'mm', 'ONE KNOB for every surface the bar touches: the clip cavity, the nose width, the nose floor and the nose roof all carry it, per side. It exists because this part has now failed to fit twice for the same reason - a clearance that was corrected in one pocket and not the other - and chasing four numbers is what caused that. Raise it if the PRINTER runs tighter than the assumed 0.07/wall; if instead the BAR is bigger than bar_w/bar_t, fix those and leave this at zero, because they also move the bead, the reference body and the nose section.'),
    ('cav_clear',        '2.00 mm + 2 * fit_adj',   'mm', 'OPENED A FURTHER 1.00 ON THE PRINTED PART (2026-10-26, second pass): Rob asked for the arms 1 mm further out. Clearance on the cavity WIDTH (total, so 1.00/side modelled = 0.93/side printed). An 8.00 cavity takes a bar up to 7.4 mm wide, which is well past anything "The Mighty Bar" could plausibly be - the point is to stop the cavity ever being the thing in the way, since the bar has still never been across a caliper. It costs lateral rattle and nothing else: the bead is still only lip_over past the bar\'s face, so the splay, the push force and the stress are all unchanged (bead_r simply grows with cav_hw and the bead sits a touch higher). Earlier: opened 0.60 -> 1.00 because the cavity is one of the three things that could have stopped the bar and it is the cheapest to rule out. Was 0.30, which the printer\'s 0.14 cavity bias turned into 0.08/side and the bar would not seat. Same omission as the nose - apply the bias to EVERY cavity, not just the obvious one. A SLIP fit now, not an interference - the lip does the holding, so the arms sit unstressed when the bar is in. That matters in ABS: a permanently splayed arm creeps and goes slack over months, a lip does not.'),
    ('lip_over',         '0.08 mm',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Cut 0.15 -> 0.08. At 0.15 the two arms took 56 N to press the bar past the beads - that is the t^3 term after the 2026-10-26 thickness bias, and a very plausible reading of "there is no way this will fit". 0.08 takes 35 N and still holds 6.4 kg on a 35 g bar. How far each bead reaches inboard of the bar\'s side face - and therefore how far each arm must splay. Was 0.70 and the arms broke on the first insertion. DEFLECTION is what breaks a flexure, not thickness: a thicker arm moved less gives the SAME grip force at less than half the stress. The working pen clip runs 0.15/arm; 0.25 here still gives ~1.6 kg of pull-out on a 35 g bar.'),
    ('cav_hw',           '(bar_w + cav_clear) / 2',  'mm', 'Cavity half width'),
    ('lip_tip_y',        'bar_w / 2 - lip_over',     'mm', 'Innermost point of the bead'),
    ('bead_r',           'cav_hw - lip_tip_y',       'mm', 'Bead radius. Equal to the reach by construction, which makes the bead a HALF CIRCLE tangent to the cavity wall at both ends - no tooth, no tip, no corner anywhere on the arm. A pointed lip between two 45 deg ramps leaves a 0.4 mm feature on a 1.2 mm arm and snaps off; this is a local thickening instead.'),
    ('bead_clear',       '0.05 mm',   'mm', 'Clearance between the bead and the bar\'s top corner radius when seated'),
    ('bead_z',           '10.74 mm',  'mm', 'Bead centre height - DERIVED by run() as the lowest the bead can sit without fouling the bar\'s R0.5 top corner. Raising the bead also lengthens the arm, which is why the margin improved when the tooth went.'),
    # ---- clip ----
    ('base_t',           '5.5 mm',    'mm', 'Base under the bar. It sets how far the slot root sits above the bed (base_t + cav_r - r_out, want >= 1.2). It does NOT set the ROOT WEB - the cavity floor and the slot rise together with it, so that web is base_t-independent. See root_web().'),
    ('land_h',           '0.8 mm',    'mm', 'Arm height above the bead'),
    ('cav_r',            '0.5 mm',    'mm', 'Cavity bottom corner radius - also the arc the relief slot follows. Deliberately SMALL: it puts the corner centre further outboard, which is what lets the relief slot wrap to -140 deg without the two slots meeting on the centreline. On a 6 mm bar that wrap is the only source of flexure length.'),
    ('arm_root',         '2.4 mm',    'mm', 'Arm thickness AT THE ROOT = 6 extrusions at 0.4. The arm is TAPERED - thick at the base, thinner at the tip - because the bending moment is largest at the root and zero at the bead. A thick root also pushes the relief slot outboard, which is what gives the ROOT WEB its thickness. The 1.2 mm version that broke on first insertion was anchored on a 0.162 mm ligament; that, not bending, is what failed.'),
    ('arm_tip',          '1.6 mm',    'mm', 'Arm thickness at the bead = 4 extrusions. Never below 4: 1.2 mm is 2.86 extrusions and the slicer lays a gap-fill bond line down the middle of the flexure.'),
    ('arm_blend',        '1.5 mm',    'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Cut 3.0 -> 1.5 so more of this very short arm (only 5.5 mm of straight run on a 6 mm bar) sits at arm_tip and flexes. Height above the cavity corner over which arm_root blends down to arm_tip. A step would be a stress riser; blending keeps the thick material where the moment is and leaves the rest compliant.'),
    ('relief_w',         '1.2 mm',    'mm', 'Relief slot width behind the arm'),
    ('relief_a0',        '-115 deg',  'deg','Relief slot root angle about the cavity corner centre, from +Y. Past -90 the slot tucks UNDER the floor, which is what buys the arm its length. Limit is the two slots converging on the centreline - a thicker arm pushes the slot further in, so the wrap had to come back from -130 to -115; run() measures the column.'),
    ('rail_t',           '3.0 mm',    'mm', 'Outer rail beyond the relief slot. With body_corner_r it sets the top land between the slot and the corner fillet: keep that land > 2 * first_layer_cham or the bed chamfer eats it and the solver runs away.'),
    
    ('clip_len',         '12.0 mm',   'mm', 'Clip length along the bar = part height when printed. Grip force scales with it and peak stress does not, so it is the one free way to buy retention.'),
    ('clip_h',           'bead_z + bead_r + land_h', 'mm', 'Clip overall height'),
    ('body_hw',          'cav_hw + arm_root + relief_w + rail_t', 'mm', 'Half width, shared by both bodies so they look like a set. Set by the ROOT thickness, the widest part of the arm.'),
    # ---- socket ----
    ('nose_len',         '15.8 mm',   'mm', 'Nose cap length - DERIVED by run() so the blind face lands tip_gap past the point.'),
    ('nose_wclear',      '2.20 mm + 2 * fit_adj',   'mm', 'OPENED A FURTHER 1.00 ON THE PRINTED PART (2026-10-26, second pass), with cav_clear and for the same reason. Width clearance in the nose (total). This pocket is the worse of the two to get wrong: the bar slides 13 mm along it, so any binding stops the assembly dead, and unlike the clip there is no flexure to give. Earlier: opened 0.80 -> 1.20. Was 0.30 and the bar would not go in. Cavities print ~0.14 UNDER nominal on this printer (0.07/wall), so 0.30 modelled was 0.16 real, and the bar\'s R0.5 edges and burrs ate the rest. This is a sliding fit along a wedge, so any interference binds at once.'),
    ('nose_floor_clear', '0.35 mm + fit_adj',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Cavity floor below the seated height, opened 0.20 -> 0.35. Was 0.05, which the print bias turned into interference. the bar\'s underside is FLAT for its whole length (the wedge is on one face only), so the nose floor and the clip floor are the same plane and the bar is supported at both ends.'),
    ('nose_top_clear',   '0.80 mm + fit_adj',   'mm', 'FIT FIRST (2026-10-26). Rob reported the prybar would not go in at all and the Zippo still popped out instead of sitting flat, and said to stop optimising retention and make the parts fit. Clearance over the wedge face, opened 0.50 -> 0.80. Was 0.20, i.e. 0.06 after the printer\'s 0.07/wall bias - effectively zero, which is why it was too tight. The cavity ceiling runs at the SAME slope as the wedge, so this clearance is constant along the pocket - the bar slides in parallel and stops on the blind face rather than jamming.'),
    ('tip_gap',          '0.30 mm',   'mm', 'Air between the point and the blind face. Small, because this is the axial stop that positions the bar.'),
    ('nose_sec_w',       '6.00 mm',   'mm', 'Bar WIDTH at the nose mouth - DERIVED by run(). Constant 6.0, since the bar does not taper in width.'),
    ('nose_sec_t',       '4.71 mm',   'mm', 'Bar THICKNESS at the nose mouth - DERIVED by run() from wedge_x/tip_t. This is the largest section that ever passes the mouth, so it sizes the cavity.'),
    ('sock_end_t',       '2.5 mm',    'mm', 'Closed end capping the point. Printed standing on the mouth this is a ceiling bridged over the cavity - a short span, fine.'),
    ('nose_roof',        '1.5 mm',    'mm', 'Material above the cavity'),
    ('nose_h',           'base_t + nose_sec_t + nose_top_clear + nose_roof', 'mm', 'Nose overall height'),
    # ---- layout along the bar ----
    ('clip_x0',          '11.0 mm',   'mm', 'Clip bed face. MUST clear the lanyard slot (which ends at hole_x + hole_len = 8.5): the clip pinches the bar\'s SIDE faces, and the slot goes straight through them, so a clip sitting over it would grip an opening for half its length and bear on the slot edges. run() checks this. The square end plus the slot then stand proud of the clip, which is also the finger grab.'),
    ('nose_cells',       '7',         '',   'Whole grid cells between the two bodies\' leg rows. Set by run() to push the nose as far toward the point as the bar allows; both parts must land on the same 8 mm grid.'),
    ('grid_pitch',       '8 mm',      'mm', 'MOD-GRID pitch'),
    ('nose_x0',          'clip_x0 + nose_cells * grid_pitch', 'mm', 'Nose bed face = its mouth, facing the clip'),
    ('nose_x1',          'nose_x0 + nose_len',                'mm', 'Nose blind end - past the point, so the wedge is captive'),
    ('body_corner_r',    '1.5 mm',    'mm', 'Rounded outer corners - see rail_t'),
    ('first_layer_cham', '0.5 mm',    'mm', 'Elephant-foot chamfer on the bed face'),
    # ---- barbed snap legs, measured off MOD-GRID Olfa holder v4 ----
    ('leg_pair_y',       '4.0 mm',    'mm', 'Leg pairs at +/- this; 8 mm apart = 1 cell'),
    ('leg_clear',        '0.14 mm',   'mm', 'Shrinks the leg LENGTH and SHANK (not the barb). MEASURED: this printer runs 0.07 per wall, so a hole comes out 0.14 under and an external feature 0.14 over. Zero it if the printer is calibrated.'),
    ('leg_hole_len',     '4.90 mm - leg_clear',       'mm', 'Leg extent along the print axis'),
    ('leg_inner_hw',     '1.45 mm',                   'mm', 'Leg inner face from pair centre -> 2.90 gap'),
    ('leg_shank_hw',     '2.39 mm - leg_clear / 2',   'mm', 'Relaxed shank half-span'),
    ('barb_hw',          '3.19 mm',                   'mm', 'Barb peak half-span. NOT reduced by leg_clear - the barb is meant to squeeze elastically.'),
    ('barb_z',           '-3.40 mm',                  'mm', 'Barb peak depth below the seating face'),
    ('catch_z',          '-3.10 mm',                  'mm', 'Catch face: 0.10 below the 3.00 plate'),
    ('leg_tip_z',        '-4.64 mm',                  'mm', 'Leg tip'),
    ('leg_tip_hw',       '2.00 mm - leg_clear / 2',   'mm', 'Tip half-span, sets the ~45 deg lead-in'),
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


def degv(P, n):
    return math.degrees(P[n].value)


def uv(P, n):
    return P[n].value


def sketch_on(root, plane, name):
    sk = root.sketches.add(plane)
    sk.name = name
    sk.isComputeDeferred = True
    return sk


def finish(sk):
    sk.isComputeDeferred = False
    return [p for p in sk.profiles]


def plane_at_x(root, expr, name):
    i = root.constructionPlanes.createInput()
    i.setByOffset(root.yZConstructionPlane, vi(expr))
    pl = root.constructionPlanes.add(i)
    pl.name = name
    return pl


def rect(sk, x, y0, z0, y1, z1):
    return sk.sketchCurves.sketchLines.addTwoPointRectangle(
        sk.modelToSketchSpace(p3(x, y0, z0)), sk.modelToSketchSpace(p3(x, y1, z1)))


def circ(sk, x, y, z, d):
    return sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(p3(x, y, z)), d * MM / 2.0)


def poly(sk, pts):
    lines = sk.sketchCurves.sketchLines
    sp = [sk.modelToSketchSpace(p3(*p)) for p in pts]
    prev = None
    for i in range(len(sp)):
        prev = lines.addByTwoPoints(prev.endSketchPoint if prev else sp[i],
                                    sp[(i + 1) % len(sp)])
    return prev


def cav_profile(sk, x, hw, z0, z1, r):
    """Cavity cross-section: flat floor, rounded bottom corners, open square top.

    Every connecting line is drawn from EXPLICIT COORDINATES. addByThreePoints
    is free to swap an arc's start and end to keep its sweep direction, so on a
    mirrored side a_r.endSketchPoint is not the end you drew - the loop then
    closes across itself. Coincident explicit points get merged by the solver,
    which is what we actually want.
    """
    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    S = lambda q: sk.modelToSketchSpace(p3(*q))
    k = r * (1.0 - math.sqrt(0.5))
    arcs.addByThreePoints(S((x, hw, z0 + r)), S((x, hw - k, z0 + k)),
                          S((x, hw - r, z0)))
    arcs.addByThreePoints(S((x, -hw + r, z0)), S((x, -hw + k, z0 + k)),
                          S((x, -hw, z0 + r)))
    for a, b in (((hw - r, z0), (-hw + r, z0)),
                 ((-hw, z0 + r), (-hw, z1)),
                 ((-hw, z1), (hw, z1)),
                 ((hw, z1), (hw, z0 + r))):
        lines.addByTwoPoints(S((x, a[0], a[1])), S((x, b[0], b[1])))


def rrect_xz(sk, x0, z0, x1, z1, r):
    """Rounded rectangle in the XZ plane. Explicit coordinates throughout."""
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    S = lambda q: sk.modelToSketchSpace(p3(q[0], 0.0, q[1]))
    if r < 0.02:
        for a, b in (((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)),
                     ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))):
            lines.addByTwoPoints(S(a), S(b))
        return
    k = r * (1.0 - math.sqrt(0.5))
    for (cx, cz, sx, sz) in ((x0 + r, z0 + r, -1, -1), (x1 - r, z0 + r, 1, -1),
                             (x1 - r, z1 - r, 1, 1), (x0 + r, z1 - r, -1, 1)):
        arcs.addByThreePoints(S((cx + sx * r, cz)), S((cx + sx * (r - k), cz + sz * (r - k))),
                              S((cx, cz + sz * r)))
    for a, b in (((x0 + r, z0), (x1 - r, z0)), ((x1, z0 + r), (x1, z1 - r)),
                 ((x1 - r, z1), (x0 + r, z1)), ((x0, z1 - r), (x0, z0 + r))):
        lines.addByTwoPoints(S(a), S(b))


def clip_cavity(sk, x, hw, z0, r, bead_y, bead_z, bead_r, top_z):
    """Clip cavity cross-section with a ROUNDED-EDGE capture bead.

    Each arm carries a half-circle bulge of radius bead_r centred ON the
    cavity wall, so it is tangent to the wall above and below: the arm's inner
    face is one continuous curve from the floor to the top, with no tooth, no
    tip and no corner to concentrate stress or break off. The bar's own R0.5
    top edge rolls over it, which is also why no lead-in ramp is needed (and
    a ramp would feather the arm tip anyway - the Zippo lesson).

    Retention is the splay needed to roll past the bead, not a ledge depth.
    """
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    S = lambda q: sk.modelToSketchSpace(p3(x, q[0], q[1]))
    k = r * (1.0 - math.sqrt(0.5))
    for sgn in (1, -1):
        arcs.addByThreePoints(S((sgn * hw, z0 + r)),
                              S((sgn * (hw - k), z0 + k)),
                              S((sgn * (hw - r), z0)))
        arcs.addByThreePoints(S((sgn * hw, bead_z - bead_r)),
                              S((sgn * bead_y, bead_z)),
                              S((sgn * hw, bead_z + bead_r)))
        for a, b in (((sgn * hw, z0 + r), (sgn * hw, bead_z - bead_r)),
                     ((sgn * hw, bead_z + bead_r), (sgn * hw, top_z))):
            lines.addByTwoPoints(S(a), S(b))
    lines.addByTwoPoints(S((-hw + r, z0)), S((hw - r, z0)))
    lines.addByTwoPoints(S((-hw, top_z)), S((hw, top_z)))


def relief_slot(sk, x, side, cy, cz, r_in, r_out, th0, z_top, y_tip, z_blend):
    """Arc around the seat's bottom corner, then up and out through the top.

    The OUTER edge stays vertical so the rail keeps a constant thickness; the
    INNER edge steps inboard from r_in to y_tip over the blend height, which is
    what tapers the arm - thick at the root where the bending moment is, thinner
    at the bead where it is nearly zero. The slot just gets wider further up.
    """
    def P(r, th):
        a = math.radians(th)
        return (x, side * (cy + r * math.cos(a)), cz + r * math.sin(a))

    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    S = lambda q: sk.modelToSketchSpace(p3(*q))
    thm = th0 / 2.0
    arcs.addByThreePoints(S(P(r_in, th0)), S(P(r_in, thm)), S(P(r_in, 0.0)))
    arcs.addByThreePoints(S(P(r_out, th0)), S(P(r_out, thm)), S(P(r_out, 0.0)))
    # explicit coordinates only - see cav_profile for why
    i0 = P(r_in, 0.0); o0 = P(r_out, 0.0)
    ib = (x, side * y_tip, z_blend)
    it = (x, side * y_tip, z_top); ot = (x, o0[1], z_top)
    for a, b in ((i0, ib), (ib, it), (it, ot), (ot, o0),
                 (P(r_out, th0), P(r_in, th0))):
        lines.addByTwoPoints(S(a), S(b))
    c = P((r_in + r_out) / 2.0, th0)
    circ(sk, c[0], c[1], c[2], r_out - r_in)


def root_web(cav_r, relief_w, arm_root, th0_deg):
    """Thickness of the arm's ANCHORAGE - the material between the relief
    slot's root cap and the cavity.

    Up to -90 deg the slot runs at a constant offset from the cavity corner, so
    the web IS arm_root. Past -90 the cap tucks under the floor and the nearest
    cavity surface becomes the FLOOR PLANE, so the web shrinks fast - and it is
    independent of base_t, because floor and slot rise together. The v1 clip
    wrapped to -130 with a 1.2 arm: 0.66 mm of web, which the 0.5 mm bed
    chamfer cut to 0.162. It tore out there on the first insertion.
    """
    if th0_deg >= -90.0:
        return arm_root
    r_mid = cav_r + arm_root + relief_w / 2.0
    return -cav_r - r_mid * math.sin(math.radians(th0_deg)) - relief_w / 2.0


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


def bed_edges_no_relief(bed, ccy, ccz, r_in, r_out, y_vals, min_len,
                        lip_y_max=None, lip_z=None):
    """Bed-face edges minus the relief slot's own boundary.

    A 0.5 mm elephant-foot chamfer taken off BOTH sides of a 1.2 mm slot - and
    all the way round its rounded root cap - collapses the slot to nothing and
    Fusion rejects it as non-manifold. The slot is internal relief, so elephant
    foot there is harmless; chamfer only the faces the bar and the eye touch.
    """
    def ends(e):
        try:
            return [(v.geometry.y / MM, v.geometry.z / MM)
                    for v in (e.startVertex, e.endVertex)]
        except Exception:
            return []

    keep = []
    short = []
    for e in bed.edges:
        pts = ends(e)
        if pts and all(any(abs(abs(y) - yv) < 0.02 for yv in y_vals)
                       for y, _ in pts):
            continue
        if pts and all(z < ccz + 0.02
                       and r_in - 0.02 <= math.hypot(abs(y) - ccy, z - ccz) <= r_out + 0.02
                       for y, z in pts):
            continue
        # The lip's two 45 deg ramps meet at a 0.4 mm flat tip. Chamfering both
        # ramps runs the two chamfers straight through that tip and the solver
        # gives up (ASM_BL_UNFIN_SHEET). Elephant foot on a lip tip at one end
        # of a 10 mm part is harmless, so leave the whole lip alone.
        if (lip_z is not None and pts
                and all(abs(y) <= lip_y_max + 0.01 and z >= lip_z - 0.01
                        for y, z in pts)):
            continue
        if e.length / MM < min_len - 0.01:
            short.append(e.length / MM)
            continue
        keep.append(e)
    return keep, short


def add_legs(root, P, body, bed_plane, bed_x, name):
    """Barbed snap legs, flush with the bed face, extruded along +X."""
    ihw = mmv(P, 'leg_inner_hw'); shw = mmv(P, 'leg_shank_hw')
    bhw = mmv(P, 'barb_hw'); bz = mmv(P, 'barb_z'); cz_ = mmv(P, 'catch_z')
    tz = mmv(P, 'leg_tip_z'); thw = mmv(P, 'leg_tip_hw')
    lpy = mmv(P, 'leg_pair_y')
    sk = sketch_on(root, bed_plane, '%s legs' % name)
    for s in (-1, 1):
        yc = s * lpy
        for t in (-1, 1):
            poly(sk, [(bed_x, yc + t * ihw, 0.5),
                      (bed_x, yc + t * ihw, tz),
                      (bed_x, yc + t * thw, tz),
                      (bed_x, yc + t * bhw, bz),
                      (bed_x, yc + t * shw, cz_),
                      (bed_x, yc + t * shw, 0.5)])
    return _ex(root, finish(sk), adsk.fusion.FeatureOperations.JoinFeatureOperation,
               'leg_hole_len', parts=[body])


def bbx(body, log, tag):
    if not DIAG:
        return
    bb = body.boundingBox
    log.append('      [%-14s] Y %8.3f..%8.3f  Z %7.3f..%7.3f  vol %8.1f  bodies-ok'
               % (tag, bb.minPoint.y / MM, bb.maxPoint.y / MM,
                  bb.minPoint.z / MM, bb.maxPoint.z / MM, body.volume / (MM ** 3)))


def build_clip(root, P, log):
    hw = mmv(P, 'body_hw'); ch = mmv(P, 'clip_h'); cl = mmv(P, 'clip_len')
    x0 = mmv(P, 'clip_x0'); xm = x0 + cl / 2.0
    bt = mmv(P, 'base_t'); cr = mmv(P, 'cav_r'); chw = mmv(P, 'cav_hw')
    ar = mmv(P, 'arm_root'); atip = mmv(P, 'arm_tip'); abl = mmv(P, 'arm_blend')
    rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    lty = mmv(P, 'lip_tip_y'); bz = mmv(P, 'bead_z'); br = mmv(P, 'bead_r')

    mid = plane_at_x(root, 'clip_x0 + clip_len / 2', 'Clip mid')
    half = 'clip_len / 2'

    sk = sketch_on(root, mid, 'Clip body')
    rect(sk, xm, -hw, 0.0, hw, ch)
    body = newbody(root, finish(sk), half, half).bodies.item(0)
    body.name = 'End Clip'
    fillet(root, x_corner_edges(body, [(-hw, 0.0), (hw, 0.0), (-hw, ch), (hw, ch)], cl),
           'body_corner_r')

    # cavity + capture lip in one profile
    sk = sketch_on(root, mid, 'Clip cavity')
    clip_cavity(sk, xm, chw, bt, cr, lty, bz, br, ch + 2.0)
    cut(root, finish(sk), 'clip_len', [body], s2='clip_len')

    # THE ROOT WEB IS WHAT BREAKS. Check it before the cut: a cut that splits
    # or starves a body still reports 0 unhealthy, and a starved root looks
    # perfect in a render.
    cham = mmv(P, 'first_layer_cham')
    web = root_web(cr, rw, ar, ra0)
    slot_bed = (bt + cr) - (cr + ar + rw)
    log.append('End Clip: ROOT WEB %.2f mm raw, %.2f after the %.2f bed chamfer %s'
               % (web, web - cham, cham,
                  'OK' if web - cham >= 1.5 else '** TOO THIN - the arm is hanging '
                  'off a ligament and will tear out (this is what broke v1). Make '
                  'relief_a0 less negative or arm_root thicker **'))
    log.append('End Clip: slot root sits %.2f mm above the bed face %s'
               % (slot_bed, 'OK' if slot_bed >= 1.2 else '** raise base_t **'))

    # relief slots: wrap under the cavity corner, then straight out the top
    n_before = root.bRepBodies.count
    sk = sketch_on(root, mid, 'Clip relief')
    for side in (1, -1):
        relief_slot(sk, xm, side, chw - cr, bt + cr, cr + ar, cr + ar + rw,
                    ra0, ch + 2.0, chw + atip, bt + cr + abl)
    cut(root, finish(sk), 'clip_len', [body], s2='clip_len')
    if root.bRepBodies.count != n_before:
        log.append('End Clip: !! the relief cut SPLIT the body (%d -> %d). Nothing '
                   'measured below means anything.'
                   % (n_before, root.bRepBodies.count))

    bed = face_at_x(body, x0)
    keep, short = bed_edges_no_relief(bed, chw - cr, bt + cr, cr + ar, cr + ar + rw,
                                      (chw + ar, chw + atip, chw + ar + rw),
                                      2 * cham + 0.1,
                                      lip_y_max=chw, lip_z=bz - br)
    log.append('End Clip: bed face has %d edges, chamfering %d (relief slot skipped)'
               % (len([e for e in bed.edges]), len(keep)))
    if short:
        log.append('    note: %d bed edge(s) shorter than two chamfers, left sharp: %s'
                   % (len(short), ', '.join('%.3f' % v for v in sorted(short))))
    if DIAG:
        for e in sorted(bed.edges, key=lambda q: q.length):
            pt = e.pointOnEdge
            log.append('      %-7s len %6.3f at y=%7.3f z=%7.3f  %s'
                       % (e.geometry.objectType.split('::')[-1], e.length / MM,
                          pt.y / MM, pt.z / MM, 'CHAMFER' if e in keep else 'skip'))
    else:
        chamfer(root, keep, 'first_layer_cham')

    add_legs(root, P, body, plane_at_x(root, 'clip_x0', 'Clip bed'), x0, 'Clip')
    log.append('End Clip: %.2f wide x %.2f tall x %.2f | cavity %.2f wide | arm '
               '%.2f at the root -> %.2f at the tip (%.0f -> %.0f extrusions) | '
               'ROUNDED CAPTURE BEAD r%.2f centred (%.2f, %.2f), innermost point '
               'y %.2f -> reaches %.2f inboard of the bar\'s side face'
               % (2 * hw, ch, cl, 2 * chw, ar, atip, ar / 0.4, atip / 0.4,
                  br, chw, bz, lty, mmv(P, 'bar_w') / 2 - lty))
    return body


def build_bar(root, P, log):
    """Reference model of the bar itself. Not a printed part - it is here so
    fitment is checked against geometry instead of arithmetic: run() rotates a
    copy of it to the insertion angle and asks Fusion whether it collides.

    The taper is the soft part of the estimate. Photo 1 (looking down on the
    wide face) shows the WIDTH narrowing over roughly the last 28 mm; photo 4
    (on edge) shows the thickness breaking only near the point. So it is
    modelled as a long width taper plus a short chisel bevel on the top face.
    """
    bw = mmv(P, 'bar_w'); btk = mmv(P, 'bar_t'); bl = mmv(P, 'bar_len')
    base = mmv(P, 'base_t'); wx = mmv(P, 'wedge_x'); tt = mmv(P, 'tip_t')

    mid = plane_at_x(root, 'bar_len / 2', 'Bar mid')
    sk = sketch_on(root, mid, 'Bar blank')
    rect(sk, bl / 2.0, -bw / 2.0, base, bw / 2.0, base + btk)
    bar = newbody(root, finish(sk), 'bar_len / 2', 'bar_len / 2').bodies.item(0)
    bar.name = 'Reference - Mighty Bar'

    # Single-sided wedge, cut from the TOP face only. The underside therefore
    # stays flat for the whole 72 mm, which is the face that goes on the plate.
    # The wedge line must run from the bar's TOP FACE at wedge_x to the point.
    # Lifting its start clear of the face to close the profile also tilts it:
    # starting 1 mm high moved the wedge to x 57.6 at 0.38/mm instead of x 55
    # at 0.32/mm, so the real bar came out up to 0.57 thicker than the analytic
    # section the nose pocket was cut from. Close the profile ABOVE the line
    # instead, with the line itself untouched.
    sk = sketch_on(root, root.xZConstructionPlane, 'Bar wedge')
    poly(sk, [(wx, 0.0, base + btk),
              (bl, 0.0, base + tt),
              (bl + 2.0, 0.0, base + tt),
              (bl + 2.0, 0.0, base + btk + 1.0),
              (wx, 0.0, base + btk + 1.0)])
    cut(root, finish(sk), 'bar_w', [bar], s2='bar_w')

    # Lanyard slot, straight through the side faces
    hx = mmv(P, 'hole_x'); hln = mmv(P, 'hole_len')
    hin = mmv(P, 'hole_inset'); hr = mmv(P, 'hole_r')
    sk = sketch_on(root, root.xZConstructionPlane, 'Bar lanyard slot')
    rrect_xz(sk, hx, base + hin, hx + hln, base + btk - hin, hr)
    cut(root, finish(sk), 'bar_w', [bar], s2='bar_w')

    # R0.5 on the long edges. Not the ends or the wedge tip: the tip is only
    # 0.5 thick, so a 0.5 radius on both its faces has no material to sit in.
    ber = mmv(P, 'bar_edge_r')
    def along_x(e):
        g = e.geometry
        if g.objectType != adsk.core.Line3D.classType():
            return False
        v = g.startPoint.vectorTo(g.endPoint)
        return abs(abs(v.x) - v.length) < 1e-6
    longs = [e for e in bar.edges if along_x(e) and e.length / MM > 20.0]
    fillet(root, longs, 'bar_edge_r')
    log.append('Reference bar: R%.2f on %d long edges' % (ber, len(longs)))

    log.append('Reference bar: %.2f x %.2f square x %.1f long, single-sided wedge '
               'from x %.1f down to %.2f at the point; lanyard slot x %.1f..%.1f, '
               'z %.1f..%.1f (%.1f x %.1f, r%.2f); flat face DOWN  (MEASURED)'
               % (bw, btk, bl, wx, tt, hx, hx + hln, base + hin, base + btk - hin,
                  hln, btk - 2 * hin, hr))
    return bar


def build_nose(root, P, log):
    """Closed cap over the point that CONFORMS to the wedge.

    The cavity is cut as a side-view profile swept through the width, so its
    ceiling runs at the wedge's own slope and sits nose_top_clear above it the
    whole way. The floor is the same plane the clip seats the bar on. Nothing
    floats.

    The consequence is that the bar can no longer be SWUNG in here - a flat
    floor at the seated height leaves the point nowhere to dip. It goes in
    axially instead: press the square end into the clip first, then slide the
    bar forward until the point stops on the blind face. Because the pocket
    and the wedge share a slope, the two faces stay parallel and it slides
    freely rather than wedging.

    Printed standing on the mouth, the sloping ceiling is 18 deg off vertical,
    well inside self-supporting, and the blind face is a 6 mm bridge.
    """
    hw = mmv(P, 'body_hw'); nh = mmv(P, 'nose_h'); nl = mmv(P, 'nose_len')
    x0 = mmv(P, 'nose_x0'); x1 = mmv(P, 'nose_x1')
    xm = (x0 + x1) / 2.0
    bt = mmv(P, 'base_t'); bl = mmv(P, 'bar_len')
    fc = mmv(P, 'nose_floor_clear'); tc = mmv(P, 'nose_top_clear')
    end_t = mmv(P, 'sock_end_t')
    chw = (mmv(P, 'bar_w') + mmv(P, 'nose_wclear')) / 2.0
    blind = x1 - end_t
    z_floor = bt - fc

    mid = plane_at_x(root, '(nose_x0 + nose_x1) / 2', 'Nose mid')
    sk = sketch_on(root, mid, 'Nose body')
    rect(sk, xm, -hw, 0.0, hw, nh)
    body = newbody(root, finish(sk), 'nose_len / 2', 'nose_len / 2').bodies.item(0)
    body.name = 'Tip Nose'
    fillet(root, x_corner_edges(body, [(-hw, 0.0), (hw, 0.0), (-hw, nh), (hw, nh)], nl),
           'body_corner_r')

    # Side-view profile following the wedge, swept through the width. Take the
    # ceiling height AT the profile's own start station: anchoring it to the
    # value at the mouth instead gave the line a 0.30/mm slope against the
    # wedge's 0.32/mm, and the clearance drifted from -0.08 to +0.19 along the
    # pocket - a seated clash at one end and a gap at the other.
    x_start = x0 - 1.0
    z_mouth = bt + bar_section(P, x_start)[1] + tc
    z_point = bt + mmv(P, 'tip_t') + tc
    sk = sketch_on(root, root.xZConstructionPlane, 'Nose cavity')
    poly(sk, [(x_start, 0.0, z_floor),
              (blind, 0.0, z_floor),
              (blind, 0.0, z_point),
              (bl, 0.0, z_point),
              (x_start, 0.0, z_mouth)])
    _ex(root, finish(sk), adsk.fusion.FeatureOperations.CutFeatureOperation,
        '(bar_w + nose_wclear) / 2', s2='(bar_w + nose_wclear) / 2', parts=[body])

    bed = face_at_x(body, x0)
    n_cham = len([e for e in bed.edges])
    chamfer(root, [e for e in bed.edges], 'first_layer_cham')

    add_legs(root, P, body, plane_at_x(root, 'nose_x0', 'Nose bed'), x0, 'Nose')
    log.append('Tip Nose: %.2f wide x %.2f tall x %.2f long | cavity %.2f wide, floor '
               'z %.2f, ceiling FOLLOWS THE WEDGE from z %.2f at x %.1f to z %.2f '
               'at the point (%.2f clearance throughout) | blind face x %.1f, point '
               'stops %.2f short | bed chamfer on %d edges'
               % (2 * hw, nh, nl, 2 * chw, z_floor, z_mouth, x_start, z_point,
                  tc, blind, blind - bl, n_cham))
    return body


def probe_out(body, x, y_from, z, limit=10.0, step=0.005):
    """March +Y from y_from while still inside the solid; returns the wall thickness."""
    v = 0.0
    while v < limit and body.pointContainment(p3(x, y_from + v, z)) == 0:
        v += step
    return v


def probe_in(body, x, z, limit=20.0, step=0.005):
    """March +Y from the centreline while OUTSIDE the solid; returns the half gap."""
    v = 0.0
    while v < limit and body.pointContainment(p3(x, v, z)) == 2:
        v += step
    return v


# The v1 arm snapped on its first insertion and this file used to blame
# bending stress, concluding that ABS only delivers 17.5 MPa here and that the
# arms therefore had to get THINNER to stay under it. Both halves were wrong.
# Measuring the real solid showed the arm was anchored on a 0.162 mm ligament:
# the relief slot wrapped to -130 deg, leaving 0.66 mm between its root cap and
# the cavity floor, and the 0.5 mm bed chamfer took nearly all of the rest. It
# TORE OUT AT THE ROOT; it did not yield in bending. See root_web().
#
# So the limit below comes from the material, not from that failure. These arms
# flex WITHIN the layer plane (both bodies print standing on an end face) and
# are >= 4 perimeters with no gap-fill bond line down the middle, so the
# across-layer knockdown does not apply: ABS in-plane yield ~40 MPa, 2.5x
# design factor. The working pen clip computes ~9 MPa by this method.
SIG_LIMIT = 15.0
PRINT_BIAS = 0.07   # cavities print ~0.07/wall under, so the bead reaches
                    # FURTHER inboard than modelled and the arm flexes more


def arm_profile(cav_r, arm_root, arm_tip, arm_blend, th0_deg, ccz, bead_z, n=300):
    """Sample the arm's neutral axis from the slot root up to the bead:
    the wrap at constant arm_root, then the straight run blending to arm_tip."""
    th0 = math.radians(th0_deg)
    segs = []
    r_arm = cav_r + arm_root / 2.0
    for i in range(n):
        th = th0 + (0.0 - th0) * (i + 0.5) / n
        segs.append((ccz + r_arm * math.sin(th), arm_root, r_arm * (-th0) / n))
    h = bead_z - ccz
    for i in range(n):
        d = h * (i + 0.5) / n
        t = arm_tip if d >= arm_blend else \
            arm_root + (arm_tip - arm_root) * (d / arm_blend)
        segs.append((ccz + d, t, h / n))
    return segs


def flexure_check(log, bl, arm_root, arm_tip, arm_blend, cav_r, th0_deg,
                  ccz, bead_z, delta, E=2000.0):
    """Stiffness and peak bending stress for one TAPERED curved arm, unit load.

    A horizontal force at the bead puts a moment F*(bead_z - z) on every
    section, so the moment follows VERTICAL distance below the bead, not
    distance along the arm. On a tapered arm the peak is wherever
    (bead_z - z) / t^2 is largest, which is not automatically the root.
    """
    segs = arm_profile(cav_r, arm_root, arm_tip, arm_blend, th0_deg, ccz, bead_z)

    def solve(d, dt=0.0):
        C = sum((bead_z - z) ** 2 / (E * bl * (t + dt) ** 3 / 12.0) * ds
                for z, t, ds in segs)
        F = d / C
        peak, where = 0.0, None
        for z, t, ds in segs:
            sig = 6.0 * F * (bead_z - z) / (bl * (t + dt) ** 2)
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
               'extrusions) -> %.2f tip (%.0f), clip %.1f long'
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


def measure_root_web(app, body, relief_w, log, label, below_z=1e9):
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
    # below_z keeps this on the SLOT ROOT CAPS. Any cylinder of about the right
    # radius used to qualify, and on 2026-10-26 lip_over 0.08 made bead_r 0.58
    # against a relief_w/2 of 0.60 - so the capture bead was measured as if it
    # were a slot cap and reported a 0.300 mm "anchorage" that does not exist.
    # The caps are the only ones under the cavity floor.
    caps = [f for f in body.faces
            if f.geometry.objectType == adsk.core.Cylinder.classType()
            and abs(f.geometry.radius / MM - relief_w / 2.0) < 0.05
            and f.geometry.origin.z / MM < below_z]
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


def verify_clip(app, body, P, log):
    bt = mmv(P, 'base_t'); cr = mmv(P, 'cav_r'); chw = mmv(P, 'cav_hw')
    ar = mmv(P, 'arm_root'); atip = mmv(P, 'arm_tip'); abl = mmv(P, 'arm_blend')
    rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    lty = mmv(P, 'lip_tip_y'); bz = mmv(P, 'bead_z'); br = mmv(P, 'bead_r')
    ch = mmv(P, 'clip_h'); cl = mmv(P, 'clip_len')
    xm = mmv(P, 'clip_x0') + cl / 2.0
    bw = mmv(P, 'bar_w'); ber = mmv(P, 'bar_edge_r')
    ccy = chw - cr; ccz = bt + cr
    worst = (1e9, 'nowhere')

    rows = []
    for i in range(6):
        th = -90.0 + i * 90.0 / 5.0
        a = math.radians(th); d = 0.03
        while d < 8.0:
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
        zz = ccz + i * (bz - br - 0.05 - ccz) / 4.0
        y_wall = probe_in(body, xm, zz)
        d = probe_out(body, xm, y_wall + 0.005, zz)
        rows.append((zz, d))
        if d < worst[0]:
            worst = (d, 'cavity wall at z=%.2f' % zz)
    log.append('    arm up the wall: %s (tapering %.2f -> %.2f by design)'
               % (', '.join('z%.2f=%.2f' % r for r in rows), ar, atip))
    log.append('    THINNEST ANYWHERE %.2f mm = %.1f perimeters at 0.4 nozzle (%s) %s'
               % (worst[0], worst[0] / 0.4, worst[1],
                  'OK' if worst[0] >= atip - 0.05 else '** thinner than arm_tip - '
                  'something is eating the arm **'))

    # The anchorage, measured on the real faces rather than inferred.
    cham = mmv(P, 'first_layer_cham')
    web_calc = root_web(cr, rw, ar, ra0)
    log.append('    root web %.3f mm by geometry, %.3f after the %.2f bed chamfer'
               % (web_calc, web_calc - cham, cham))
    measure_root_web(app, body, rw, log, 'root web', below_z=bt)

    # column left between the two slots where they wrap under the cavity
    # Stop short of the cavity floor: a point sampled exactly ON a face returns
    # "on surface" (1), not "inside" (0), so the walk bails at once and reports
    # a false 0.000. Cost a round trip the first time it bit here.
    col = 1e9
    zz = 0.5
    while zz < bt - 0.1:
        if body.pointContainment(p3(xm, 0.0, zz)) == 0:
            v = 0.0
            while v < chw and body.pointContainment(p3(xm, v, zz)) == 0:
                v += 0.005
            col = min(col, 2 * v)
        zz += 0.05
    log.append('    column between the two relief slots %.3f mm (want >= 1.00)' % col)

    cav = 2 * probe_in(body, xm, bt + 2.0)
    gap = 2 * probe_in(body, xm, bz)
    log.append('    cavity %.3f (bar %.2f, %.3f clearance - slip fit, arms relax when '
               'seated) | narrowest point across the beads %.3f -> the bar must splay '
               'the arms %.3f total to pass' % (cav, bw, cav - bw, gap, bw - gap))
    # the bead is tangent to the wall at both ends, so the arm's inner face has
    # no corner on it anywhere - check there is no flat or cusp at the crown
    crown = 2 * probe_in(body, xm, bz + br * 0.5)
    log.append('    bead profile: y %.3f at the crown, %.3f half a radius above -> '
               'rises %.3f, a continuous curve with no tip to snap off'
               % (gap / 2, crown / 2, (crown - gap) / 2))

    F, sig = flexure_check(log, cl, ar, atip, abl, cr, ra0, ccz, bz,
                           mmv(P, 'lip_over'))
    pull = 2 * F * 1.8
    log.append('      -> roughly %.0f N (%.1f kg) to roll the bar back out over the '
               'bead. Arms are UNLOADED when seated, so no creep.'
               % (pull, pull / 9.81))
    return sig


def bar_section(P, x):
    """Bar width and thickness at station x, from the taper parameters."""
    bw = mmv(P, 'bar_w'); btk = mmv(P, 'bar_t'); bl = mmv(P, 'bar_len')
    wx = mmv(P, 'wedge_x'); tt = mmv(P, 'tip_t')
    if x <= wx or bl <= wx:
        return bw, btk
    return bw, max(btk + (tt - btk) * (x - wx) / (bl - wx), tt)


def clash(tbm, a_src, b_src, matrix=None):
    """Volume of overlap between two bodies, in mm3. 0.0 means clear."""
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


def tilt_matrix(deg, px, pz):
    """Rotate about +Y through (px, 0, pz). Positive raises the square end."""
    m = adsk.core.Matrix3D.create()
    m.setToRotation(math.radians(deg), adsk.core.Vector3D.create(0.0, 1.0, 0.0),
                    p3(px, 0.0, pz))
    return m


def verify_nose(body, P, log):
    bt = mmv(P, 'base_t'); x0 = mmv(P, 'nose_x0')
    blind = mmv(P, 'nose_x1') - mmv(P, 'sock_end_t')
    rows = []
    for f in (0.05, 0.35, 0.65, 0.95):
        xx = x0 + f * (blind - x0)
        w = 2 * probe_in(body, xx, bt + 0.2)
        z = bt - mmv(P, 'nose_floor_clear') + 0.01
        while z < 30.0 and body.pointContainment(p3(xx, 0.0, z)) == 2:
            z += 0.005
        bw_, bt_ = bar_section(P, xx)
        rows.append((xx, w - bw_, z - (bt + bt_)))
    log.append('    conformity along the pocket (clearance on width / over the wedge):')
    for xx, dw, dz in rows:
        log.append('      x %5.1f   width +%.3f   ceiling +%.3f' % (xx, dw, dz))


def shift_matrix(dx, dz):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(dx * MM, 0.0, dz * MM)
    return m


def verify_fit(tbm, bar, clip, nose, P, log):
    """Fitment against real geometry rather than trigonometry.

    The conforming nose rules out swinging the bar in, so the motion is now
    axial: press the square end into the clip, then slide forward until the
    point stops on the blind face.
    """
    bt = mmv(P, 'base_t'); ber = mmv(P, 'bar_edge_r')
    br = mmv(P, 'bead_r'); bz = mmv(P, 'bead_z'); chw = mmv(P, 'cav_hw')
    # To be clear of the beads the bar's UNDERSIDE has to be above the top of
    # the bead, not merely its top corner above the bead's crown: below that
    # corner the bar is at full width and fouls the bead head on.
    lift = (bz + br) - bt

    log.append('')
    log.append('FITMENT (interference against the reference bar, not arithmetic)')
    v_nose = clash(tbm, bar, nose)
    v_clip = clash(tbm, bar, clip)
    log.append('  seated: bar vs nose %.3f mm3 %s | bar vs clip %.3f mm3 %s'
               % (v_nose, 'CLEAR' if v_nose < 0.01 else '** CLASH **',
                  v_clip, 'CLEAR' if v_clip < 0.01 else '** CLASH **'))

    rows = [(d, clash(tbm, bar, nose, shift_matrix(-d, 0.0)),
             clash(tbm, bar, clip, shift_matrix(-d, 0.0)))
            for d in (2.0, 6.0, 12.0)]
    log.append('  slide in (bar drawn back along the bar axis, then pushed home):')
    for d, vn, vc in rows:
        log.append('      back %4.1f mm   vs nose %.3f   vs clip %.3f   %s'
                   % (d, vn, vc, 'clear' if max(vn, vc) < 0.01 else '** CLASH **'))

    log.append('  press into the clip (done with the point clear of the nose, then '
               'slide forward): the bar sits clear of the beads %.2f mm above '
               'seated' % lift)
    for h in (lift, lift + 1.5):
        v = clash(tbm, bar, clip, shift_matrix(0.0, h))
        log.append('      lifted %.2f mm   vs clip %.3f   %s'
                   % (h, v, 'clear' if v < 0.01 else '** still fouling **'))
    mid = clash(tbm, bar, clip, shift_matrix(0.0, lift / 2.0))
    log.append('      lifted %.2f mm   vs clip %.3f   <- mid press, the arms are '
               'splayed here by design' % (lift / 2.0, mid))
    return lift


def verify_legs(body, P, log, bed_x):
    bl = mmv(P, 'leg_hole_len'); lpy = mmv(P, 'leg_pair_y')
    lxm = bed_x + bl / 2.0
    for z, lab, want in ((-1.5, 'shank', 2 * mmv(P, 'leg_shank_hw')),
                         (mmv(P, 'barb_z'), 'barb ', 2 * mmv(P, 'barb_hw'))):
        v = lpy + mmv(P, 'leg_inner_hw') + 0.03
        while v < lpy + 8.0 and body.pointContainment(p3(lxm, v, z)) == 0:
            v += 0.005
        log.append('    leg %s span %.3f (want %.2f)' % (lab, 2 * (v - lpy), want))
    yp = lpy + mmv(P, 'leg_inner_hw') + 0.3
    v = lxm
    while v > lxm - 10.0 and body.pointContainment(p3(v, yp, mmv(P, 'barb_z'))) == 0:
        v -= 0.005
    log.append('    legs start at x=%.3f, bed face is x=%.3f -> %s'
               % (v, bed_x, 'FLUSH, nothing floats' if abs(v - bed_x) < 0.02
                  else 'FLOATING - they would need support'))


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
        log.append('WARNING: folder "%s" not found; using project root' % TARGET_FOLDER)
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
        log.append('rebuilding into existing "%s" (was v%s)'
                   % (DOC_NAME, existing.versionNumber))
    else:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        log.append('creating new document "%s"' % DOC_NAME)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    try:
        design.fusionUnitsManager.distanceDisplayUnits = \
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    except Exception:
        pass
    root = design.rootComponent

    P = add_params(design)

    # Push the nose as far toward the point as the grid allows. Far out = a long
    # lever to the clip = a small swing angle, which is what makes this fit.
    gp = mmv(P, 'grid_pitch')
    bl = mmv(P, 'bar_len'); x0c = mmv(P, 'clip_x0')
    # Push the nose as far out as the grid allows while leaving a pocket at least
    # min_pocket long, then derive its length from where the point must stop.
    min_pocket = 12.0
    cells = max(2, int(math.floor((bl + mmv(P, 'tip_gap') + mmv(P, 'sock_end_t')
                                   - x0c - min_pocket) / gp)))
    P['nose_cells'].expression = str(cells)
    # Nose length follows from where the point must stop, not the other way round
    P['nose_len'].expression = '%.3f mm' % (bl + mmv(P, 'tip_gap')
                                            + mmv(P, 'sock_end_t') - mmv(P, 'nose_x0'))
    x0n = mmv(P, 'nose_x0')
    sw, st = bar_section(P, x0n)
    P['nose_sec_w'].expression = '%.3f mm' % sw
    P['nose_sec_t'].expression = '%.3f mm' % st
    # Bead sits as low as it can without fouling the bar's top corner radius.
    # Lower is better: it keeps the clip short, but higher lengthens the arm.
    ber = mmv(P, 'bar_edge_r')
    dy = mmv(P, 'cav_hw') - (mmv(P, 'bar_w') / 2 - ber)
    reach = mmv(P, 'bead_r') + ber + mmv(P, 'bead_clear')
    P['bead_z'].expression = '%.3f mm' % (
        mmv(P, 'base_t') + mmv(P, 'bar_t') - ber
        + math.sqrt(max(reach ** 2 - dy ** 2, 0.0)))
    log.append('user parameters: %d' % len(P))

    bw = mmv(P, 'bar_w'); btk = mmv(P, 'bar_t'); wx = mmv(P, 'wedge_x')
    cl = mmv(P, 'clip_len'); nl = mmv(P, 'nose_len'); x1n = mmv(P, 'nose_x1')
    log.append('bar %.2f x %.2f square x %.1f long, single-sided wedge from x %.1f '
               '(%.1f long) to %.2f at the point  (MEASURED)'
               % (bw, btk, bl, wx, bl - wx, mmv(P, 'tip_t')))
    log.append('layout along the bar: square end at 0 | clip %.1f..%.1f | bar free '
               '%.1f..%.1f | nose %.1f..%.1f | point at %.1f, blind end at %.1f '
               '(%.1f mm of slack)'
               % (x0c, x0c + cl, x0c + cl, x0n, x0n, x1n, bl,
                  x1n - mmv(P, 'sock_end_t'), x1n - mmv(P, 'sock_end_t') - bl))
    log.append('leg rows %.1f mm apart = %d cells at %.0f mm pitch'
               % (x0n - x0c, cells, gp))

    # The clip pinches the bar's SIDE faces and the lanyard slot goes straight
    # through them, so any overlap means gripping an opening and bearing on its
    # edges. Check it in x, and check the slot is in the pinched band in z.
    hx = mmv(P, 'hole_x'); hx1 = hx + mmv(P, 'hole_len')
    ov = min(x0c + cl, hx1) - max(x0c, hx)
    log.append('lanyard slot x %.1f..%.1f vs clip x %.1f..%.1f -> %s'
               % (hx, hx1, x0c, x0c + cl,
                  'CLEAR by %.1f mm, full %.1f mm of pinch lands on solid bar'
                  % (x0c - hx1, cl) if ov <= 0 else
                  '** OVERLAP %.1f mm: the clip would grip across the slot for '
                  '%.0f%% of its length. Raise clip_x0 above %.1f. **'
                  % (ov, 100.0 * ov / cl, hx1)))
    if x1n - mmv(P, 'sock_end_t') - bl < 0:
        log.append('!! the point bottoms out before the square end reaches the clip. '
                   'bar_len is the number to get right here - lengthen nose_len or '
                   'drop a grid cell.')

    bar = build_bar(root, P, log)
    clip = build_clip(root, P, log)
    nose = build_nose(root, P, log)

    log.append('')
    for body, bed_x, nm in ((clip, x0c, 'End Clip'), (nose, x0n, 'Tip Nose')):
        bb = body.boundingBox
        log.append('%-11s X %7.3f..%7.3f  Y %7.3f..%7.3f  Z %7.3f..%7.3f  vol %.1f mm3'
                   % (nm, bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
                      bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM,
                      body.volume / (MM ** 3)))
        if nm == 'End Clip':
            verify_clip(app, body, P, log)
        else:
            verify_nose(body, P, log)
        verify_legs(body, P, log, bed_x)

    verify_fit(adsk.fusion.TemporaryBRepManager.get(), bar, clip, nose, P, log)

    unhealthy = [design.timeline.item(i).name for i in range(design.timeline.count)
                 if design.timeline.item(i).healthState !=
                 adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    log.append('')
    log.append('timeline: %d features, %d unhealthy %s'
               % (design.timeline.count, len(unhealthy), unhealthy or ''))
    log.append('NOTE "Reference - Mighty Bar" is a reference body, NOT a printed part. '
               'Export only "End Clip" and "Tip Nose".')

    if existing is not None:
        doc.save('Rebuilt from modgrid_prybar_holder.py')
    else:
        doc.saveAs(DOC_NAME, folder,
                   'MOD-GRID prybar holder: captive tip nose + end clip', '')
    log.append('save issued for "%s" in "%s"' % (DOC_NAME, folder.name))
    return '\n'.join(log)
