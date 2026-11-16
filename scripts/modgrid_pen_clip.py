"""
MOD-GRID pen clip - two-part top-entry snap mount for a 9.84 mm pen.

v3 of this part. History, because both earlier failures were orientation/geometry
traps worth not repeating:
  1. Printed flat with integrated pegs. Lip bending stress ran ACROSS layer lines
     (~59 MPa vs ~15-20 MPa interlayer) -> lip sheared off on first pen removal.
  2. Stood on end to fix that. Lips then loaded along layers, but the pegs turned
     sideways; the peg's un-compressible 5.13 axis became vertical, so sag and
     support scars on its underside blew the fit. Also the lip was a WEDGE,
     2.59 mm at the root but only 0.60 mm (1.5 extrusion widths) where the pen
     pushes - unprintable and far too floppy to retain anything.

This version fixes both root causes:
  * INTEGRAL BARBED SNAP LEGS, replicating how every official holder actually mounts
    (measured from MOD-GRID Olfa holder v4; see research/modgrid-edc-system.md).
    Retention is a snap, NOT friction: the relaxed 4.78 mm leg pair slides into the
    5.00 hole, the 6.38 mm barb squeezes 1.38 mm to pass, then springs out under the
    3 mm plate while the shoulder seats on top. Nothing is crushed, so it survives
    repeated remounting. No separate connector is involved.
  * CONSTANT-THICKNESS lip. The relief slot is an annular sector following the bore
    at a fixed offset, so the lip is a uniform 2.0 mm curved spring (5 perimeters)
    instead of a wedge that thins to nothing exactly where it is loaded.

PRINT ORIENTATION: stand the clip on an end face, pen axis vertical ("place on
face", the x = -clip_len/2 face, the one with the ID dimples). Lip stress then runs
along layers. With the pegs gone there is nothing sideways left, so:
NOTHING NEEDS SUPPORT and nothing floats - the body is a pure extrusion, the bore,
opening and relief slots are all vertical channels, and the legs are vertical walls
whose barbs flex within the layer plane.

Grid spec: 8.000 pitch, 5.000 square hole, 3.000 plate (research/modgrid-edc-system.md).

Fusion script entry point: run(_context).
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1

DOC_NAME = 'MOD-GRID Pen Clip 9.84'
TARGET_FOLDER = 'Mod Grid'

PARAM_DEFS = [
    ('pen_d',            '9.84 mm',                               'mm', 'Pen diameter (measured by user)'),
    ('pen_clear',        '0.2 mm',                                'mm', 'Diametral clearance in the bore'),
    ('bore_d',           'pen_d + pen_clear',                     'mm', 'Clip bore diameter'),
    ('lip_t',            '2.0 mm',                                'mm', 'CONSTANT lip thickness - 5 perimeters at 0.4 nozzle'),
    ('lip_spread',       '0.30 mm',                               'mm', 'How far the pen spreads the lips; sets snap force'),
    ('lip_gap',          'pen_d - lip_spread',                    'mm', 'Opening between the lips'),
    ('relief_w',         '1.2 mm',                                'mm', 'Relief slot width (the gap behind the lip)'),
    ('relief_a0',        '-45 deg',                               'deg','Relief slot start angle from the bore equator; lower = longer, softer lip'),
    ('bottom_wall',      '2.5 mm',                                'mm', 'Material under the bore'),
    ('land_h',           '2 mm',                                  'mm', 'Slot depth above the lips'),
    ('clip_len',         '14 mm',                                 'mm', 'Clip length along the pen axis = part height when printed'),
    ('body_hw',          '11 mm',                                 'mm', 'Body half width'),
    ('body_corner_r',    '2.0 mm',                                'mm', 'Rounded outer corners - a bare rectangle looks unfinished'),
    ('grid_pitch',       '8 mm',                                  'mm', 'MOD-GRID pitch'),
    # --- barbed snap legs, measured off MOD-GRID Olfa holder v4 ---
    ('leg_clear',        '0.14 mm',                               'mm', 'Shrinks the leg LENGTH and SHANK (not the barb). 0 = official nominal (4.90 long, 4.78 shank) which assumes the hole prints a true 5.00; FDM holes usually come out undersize, so raise this if the legs crush going in. MEASURED: the printed hole came out 0.14 under nominal, i.e. 0.07 per wall. External features run over by the same bias, so a 4.90 leg prints ~5.04; 0.14 here brings the PRINTED leg back to 4.90 in a true 5.00 hole. Zero it if the printer is dimensionally calibrated.'),
    ('leg_hole_len',     '4.90 mm - leg_clear',                   'mm', 'Leg extent along the print axis'),
    ('leg_inner_hw',     '1.45 mm',                               'mm', 'Leg inner face from pair centre -> 2.90 gap'),
    ('leg_shank_hw',     '2.39 mm - leg_clear / 2',               'mm', 'Relaxed shank half-span'),
    ('barb_hw',          '3.19 mm',                               'mm', 'Barb peak half-span. Deliberately NOT reduced by leg_clear - the barb is the retention feature and is meant to squeeze elastically; it is the shank and the length that crush.'),
    ('barb_z',           '-3.40 mm',                              'mm', 'Barb peak depth below the seating face'),
    ('catch_z',          '-3.10 mm',                              'mm', 'Catch face: 0.10 below the 3.00 plate'),
    ('leg_tip_z',        '-4.64 mm',                              'mm', 'Leg tip'),
    ('leg_tip_hw',       '2.00 mm - leg_clear / 2',               'mm', 'Tip half-span, sets the ~45 deg lead-in'),
    ('first_layer_cham', '0.5 mm',                                'mm', 'Elephant-foot chamfer on the bed face'),
    ('id_dimple_d',      '1.6 mm',                                'mm', 'Identification dimple diameter'),
    ('id_dimple_h',      '0.6 mm',                                'mm', 'Identification dimple depth'),
    ('bore_cz',          'bottom_wall + bore_d / 2',              'mm', 'Bore centre height'),
    ('lip_z',            'bore_cz + sqrt((bore_d / 2)^2 - (lip_gap / 2)^2)', 'mm', 'Lip tip height'),
    ('body_h',           'lip_z + land_h',                        'mm', 'Overall body height'),
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
    """Length parameter in mm. NOT valid for angles - .value is radians there."""
    return P[n].value / MM


def degv(P, n):
    """Angle parameter in degrees."""
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
    """Closed polygon from world-space (x, y, z) points."""
    lines = sk.sketchCurves.sketchLines
    sp = [sk.modelToSketchSpace(p3(*p)) for p in pts]
    first = None
    prev = None
    for i in range(len(sp)):
        a = sp[i]
        b = sp[(i + 1) % len(sp)]
        ln = lines.addByTwoPoints(prev.endSketchPoint if prev else a, b)
        if first is None:
            first = ln
        prev = ln
    return first


def annular_slot(sk, cy, cz, r_in, r_out, th0, th1, side):
    """Curved slot with ROUNDED ends. A straight radial end cut leaves a sharp
    V-notch - ragged in the end face and a stress riser at the lip root.

    Built as a plain annular sector PLUS a circle at each end, tangent to both
    arcs; the union is a round-ended slot. Capping with three-point arcs instead
    looked tidier but malformed on the mirrored side, splitting the sketch into
    four profiles and cutting away the whole outer rail.
    """
    def pt(r, th):
        a = math.radians(th)
        return (0.0, cy + side * r * math.cos(a), cz + r * math.sin(a))

    thm = (th0 + th1) / 2.0
    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    S = lambda q: sk.modelToSketchSpace(p3(*q))
    a_in = arcs.addByThreePoints(S(pt(r_in, th0)), S(pt(r_in, thm)), S(pt(r_in, th1)))
    a_out = arcs.addByThreePoints(S(pt(r_out, th0)), S(pt(r_out, thm)), S(pt(r_out, th1)))
    lines.addByTwoPoints(a_in.startSketchPoint, a_out.startSketchPoint)
    lines.addByTwoPoints(a_in.endSketchPoint, a_out.endSketchPoint)
    rm = (r_in + r_out) / 2.0
    for th in (th0, th1):
        c = pt(rm, th)
        circ(sk, c[0], c[1], c[2], r_out - r_in)
    return a_in


def x_corner_edges(body, corners_yz, length_mm):
    """Edges running along X (the pen axis) at the given YZ corners."""
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


def build_clip(root, P, log, y0, name, n_dimples):
    hw = mmv(P, 'body_hw'); bh = mmv(P, 'body_h'); bd = mmv(P, 'bore_d')
    R = bd / 2.0
    bcz = mmv(P, 'bore_cz'); gap = mmv(P, 'lip_gap'); lz = mmv(P, 'lip_z')
    lt = mmv(P, 'lip_t'); rw = mmv(P, 'relief_w'); ra0 = degv(P, 'relief_a0')
    cl = mmv(P, 'clip_len'); dd = mmv(P, 'id_dimple_d')
    gp = mmv(P, 'grid_pitch')
    half = 'clip_len / 2'

    # body: pure extrusion along the pen axis
    sk = sketch_on(root, root.yZConstructionPlane, '%s body' % name)
    rect(sk, 0.0, y0 - hw, 0.0, 0.0, y0 + hw, bh)
    body = newbody(root, finish(sk), half, half).bodies.item(0)
    body.name = name
    fillet(root, x_corner_edges(body, [(y0 - hw, 0.0), (y0 + hw, 0.0),
                                       (y0 - hw, bh), (y0 + hw, bh)], cl),
           'body_corner_r')

    # bore
    sk = sketch_on(root, root.yZConstructionPlane, '%s bore' % name)
    circ(sk, 0.0, y0, bcz, bd)
    cut(root, finish(sk), 'clip_len', [body], s2='clip_len')

    # opening slot, out through the top
    sk = sketch_on(root, root.yZConstructionPlane, '%s opening' % name)
    rect(sk, 0.0, y0 - gap / 2.0, lz, 0.0, y0 + gap / 2.0, bh + 1.0)
    cut(root, finish(sk), 'clip_len', [body], s2='clip_len')

    # CONSTANT-THICKNESS lip: relief slot is an annular sector that follows the
    # bore at a fixed offset, so the lip is a uniform curved spring. Running it
    # out to +70 deg puts the far end of the sector outside the body, which frees
    # the lip tip without a second cut.
    lip_tip_a = math.degrees(math.asin((lz - bcz) / R))
    sk = sketch_on(root, root.yZConstructionPlane, '%s relief' % name)
    for side in (1, -1):
        annular_slot(sk, y0, bcz, R + lt, R + lt + rw, ra0, 70.0, side)
    cut(root, finish(sk), 'clip_len', [body], s2='clip_len')

    # First-layer chamfer on the bed face. Do this BEFORE the legs are added: once
    # they reach this face the body outline is broken into segments, and chamfering
    # a chain that terminates mid-face fails with ASM_BL_CAP_COMPLEX. The legs' own
    # bed edges stay sharp, which is fine - they are 0.94 mm and could not take a
    # 0.5 mm chamfer anyway.
    bed = face_at_x(body, -cl / 2.0)
    n_cham = len([e for e in bed.edges])
    chamfer(root, [e for e in bed.edges], 'first_layer_cham')

    # Barbed snap legs, replicating the official holder mount. The profile lives in
    # the YZ plane and extrudes along the PEN AXIS, which is vertical when printed:
    # every leg face is therefore a vertical wall (no overhang, no support) and the
    # barb flexes in Y, within the layer plane.
    ihw = mmv(P, 'leg_inner_hw'); shw = mmv(P, 'leg_shank_hw')
    bhw = mmv(P, 'barb_hw'); bz = mmv(P, 'barb_z'); cz_ = mmv(P, 'catch_z')
    tz = mmv(P, 'leg_tip_z'); thw = mmv(P, 'leg_tip_hw')
    # The legs must start FLUSH WITH THE BED FACE, not centred on the clip. Centred,
    # they first appear 4.55 mm up the print with nothing beneath them - a floating
    # island the slicer can only reach with support. Flush, they rise from the bed
    # alongside the body and simply stop at 4.90, which is how the official holders
    # do it (legs 0..4.90, body 0..7.95).
    lx = -cl / 2.0
    lpin = root.constructionPlanes.createInput()
    lpin.setByOffset(root.yZConstructionPlane, vi('-clip_len / 2'))
    leg_plane = root.constructionPlanes.add(lpin)
    leg_plane.name = '%s leg base' % name
    sk = sketch_on(root, leg_plane, '%s legs' % name)
    for s in (-1, 1):                      # the two leg pairs, one per grid hole
        yc = y0 + s * gp / 2.0
        for t in (-1, 1):                  # the two legs of a pair
            poly(sk, [(lx, yc + t * ihw, 0.5),
                      (lx, yc + t * ihw, tz),
                      (lx, yc + t * thw, tz),
                      (lx, yc + t * bhw, bz),
                      (lx, yc + t * shw, cz_),
                      (lx, yc + t * shw, 0.5)])
    _ex(root, finish(sk), adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'leg_hole_len', parts=[body])

    # ID dimples on the bed face
    pin = root.constructionPlanes.createInput()
    pin.setByOffset(root.yZConstructionPlane, vi('-clip_len / 2'))
    bed_plane = root.constructionPlanes.add(pin)
    bed_plane.name = '%s bed' % name
    sk = sketch_on(root, bed_plane, '%s dimples' % name)
    for k in range(n_dimples):
        circ(sk, -cl / 2.0, y0 + hw - 2.5, bh - 2.5 - k * 3.0, dd)
    cut(root, finish(sk), 'id_dimple_h', [body])


    log.append('%s: lip %.2f mm constant, relief %.0f deg to tip at %.1f deg, %d dimple(s), '
               'first-layer chamfer on %d body edges'
               % (name, lt, ra0, lip_tip_a, n_dimples, n_cham))
    return body


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
        log.append('rebuilding into existing "%s" (was v%s)' % (DOC_NAME, existing.versionNumber))
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
    log.append('user parameters: %d' % len(P))
    log.append('bore %.3f | centre z %.3f | lips z %.3f | gap %.3f -> spread %.3f'
               % (mmv(P, 'bore_d'), mmv(P, 'bore_cz'), mmv(P, 'lip_z'),
                  mmv(P, 'lip_gap'), mmv(P, 'lip_spread')))

    a = build_clip(root, P, log, 0.0, 'Clip A', 1)
    b = build_clip(root, P, log, 30.0, 'Clip B', 2)

    # ---------------- verification ----------------
    R = mmv(P, 'bore_d') / 2.0; bcz = mmv(P, 'bore_cz'); lz = mmv(P, 'lip_z')
    lt = mmv(P, 'lip_t'); ra0 = degv(P, 'relief_a0')
    gp = mmv(P, 'grid_pitch')
    cl = mmv(P, 'clip_len'); step = 0.005
    log.append('')
    for body, y0, nm in ((a, 0.0, 'Clip A'), (b, 30.0, 'Clip B')):
        bb = body.boundingBox
        log.append('%-7s X %7.3f..%7.3f  Y %8.3f..%8.3f  Z %7.3f..%7.3f  vol %.1f mm3' % (
            nm, bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
            bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM,
            body.volume / (MM ** 3)))

        # measure lip thickness along the arc - the thing that was wrong
        worst = (1e9, 0.0)
        th = ra0
        rows = []
        while th <= math.degrees(math.asin((lz - bcz) / R)) + 1e-9:
            a_r = math.radians(th)
            yi = R * math.cos(a_r); zi = bcz + R * math.sin(a_r)
            # walk outward along the radius from the bore surface
            d = 0.03   # start just inside the wall, not on the bore surface
            while d < 6.0:
                yy = (R + d) * math.cos(a_r); zz = bcz + (R + d) * math.sin(a_r)
                if body.pointContainment(p3(0.0, y0 + yy, zz)) != 0:
                    break
                d += step
            rows.append((th, d))
            if d < worst[0]:
                worst = (d, th)
            th += (math.degrees(math.asin((lz - bcz) / R)) - ra0) / 5.0
        log.append('    lip thickness along the arc: %s'
                   % ', '.join('%.0fdeg=%.2f' % (t, v) for t, v in rows))
        log.append('    THINNEST %.2f mm at %.0f deg = %.1f perimeters at 0.4 nozzle (was 0.60 / 1.5)'
                   % (worst[0], worst[1], worst[0] / 0.4))

        L = (R + lt / 2.0) * math.radians(
            math.degrees(math.asin((lz - bcz) / R)) - ra0)
        dlt = mmv(P, 'lip_spread') / 2.0
        sig = 3 * 2000.0 * dlt * (lt / 2.0) / (L ** 2)
        log.append('    lip arc %.2f mm long, %.3f deflection -> ~%.0f MPa along layers '
                   '(limit ~40) -> margin %.1fx' % (L, dlt, sig, 40.0 / sig))

        # barbed snap legs
        # legs now sit at the BED end of the clip, not centred - probe inside them
        lxm = -cl / 2.0 + mmv(P, 'leg_hole_len') / 2.0

        def span(z):
            # start OUTSIDE the inner gap between the two legs, or the probe sits
            # in the void at the pair centre and reports zero
            yc = y0 + gp / 2.0
            v = yc + mmv(P, 'leg_inner_hw') + 0.03
            while v < yc + 8.0 and body.pointContainment(p3(lxm, v, z)) == 0:
                v += step
            return 2 * (v - yc), 0.0
        for z, lab, want in ((-1.5, 'shank', 2 * mmv(P, 'leg_shank_hw')),
                             (mmv(P, 'barb_z'), 'barb ', 2 * mmv(P, 'barb_hw')),
                             (mmv(P, 'leg_tip_z') + 0.1, 'tip  ', 2 * mmv(P, 'leg_tip_hw'))):
            w, off = span(z)
            log.append('    leg pair %s at z=%+.2f: %.3f mm span (want %.2f)'
                       % (lab, z, w, want))
        sq = 2 * mmv(P, 'barb_hw') - 5.0
        log.append('    -> barb must squeeze %.3f mm total (%.3f per side) to pass the 5.00 hole'
                   % (sq, sq / 2.0))
        log.append('    -> shank clearance in the hole: %.3f mm total'
                   % (5.0 - 2 * mmv(P, 'leg_shank_hw')))
        log.append('    -> catch face %.2f below the seating face, plate is 3.00 -> %.2f engagement'
                   % (-mmv(P, 'catch_z'), -mmv(P, 'catch_z') - 3.0))
        # leg extent along the pen axis must fit the 5.00 hole
        yprobe = y0 + gp / 2.0 + mmv(P, 'leg_inner_hw') + 0.3
        v = lxm
        while v < lxm + 10.0 and body.pointContainment(p3(v, yprobe, mmv(P, 'barb_z'))) == 0:
            v += step
        hi = v
        v = lxm
        while v > lxm - 10.0 and body.pointContainment(p3(v, yprobe, mmv(P, 'barb_z'))) == 0:
            v -= step
        log.append('    leg extent along the pen axis %.3f..%.3f = %.3f mm (want %.2f, hole 5.00)'
                   % (v, hi, hi - v, mmv(P, 'leg_hole_len')))
        bed_x = -cl / 2.0
        if abs(v - bed_x) < 0.02:
            log.append('    -> legs START AT THE BED PLANE (x=%.2f): they rise with the body, '
                       'nothing floats, no support' % bed_x)
        else:
            log.append('    !! legs begin %.2f mm up the print with nothing beneath -> '
                       'SLICER WILL DEMAND SUPPORT' % (v - bed_x))
        log.append('    leg pair pitch %.3f mm (grid is %.2f)' % (gp, gp))

    unhealthy = [design.timeline.item(i).name for i in range(design.timeline.count)
                 if design.timeline.item(i).healthState !=
                 adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    log.append('')
    log.append('bodies: %s' % [bd.name for bd in root.bRepBodies])
    log.append('timeline: %d features, %d unhealthy %s'
               % (design.timeline.count, len(unhealthy), unhealthy or ''))

    if existing is not None:
        doc.save('Integral barbed snap legs, measured from the official holders')
    else:
        doc.saveAs(DOC_NAME, folder, 'MOD-GRID pen clip, integral barbed snap legs', '')
    log.append('save issued for "%s" in "%s"' % (DOC_NAME, folder.name))
    return '\n'.join(log)
