"""
10" (mini) rack frame - parametric, 3D printable, 6U by default.

Two unique printed parts:
  * Post  x4  - one part; the four corners are mirrors, which for this solid is
                the same part rotated 180 deg (the hole grid is symmetric in Z).
  * Plate x2  - one part; the top plate is the bottom plate flipped over.

Standards (research/10-inch-rack-standard.md):
  1U = 44.45 mm; 3 holes per U at 6.35 / 22.225 / 38.10 mm above each U boundary;
  rail hole pitch 236.525 mm c/c; overall width 254 mm; clear opening 222 mm.

Change `rack_u` in Fusion's parameter dialog and the frame follows: post length
is an expression and the rail holes are a rectangular pattern of quantity rack_u.

Fusion script entry point: run(context).
"""

import math
import traceback

import adsk.core
import adsk.fusion

MM = 0.1  # mm -> Fusion internal cm

DOC_NAME = '10in Rack Frame'
TARGET_FOLDER = '10 inch rack'

# (name, expression, units, comment) -- dependency order matters
PARAM_DEFS = [
    ('rack_u',           '6',                                     '',    'Number of rack units - the main variable'),
    ('u_height',         '44.45 mm',                              'mm',  '1U, EIA-310 (1.75 in)'),
    ('rail_hole_pitch',  '236.525 mm',                            'mm',  'Rail hole centre-to-centre (10 in de-facto, 9.312 in)'),
    ('rail_edge_inset',  '8.7375 mm',                             'mm',  'Rail hole centre to outer face of post'),
    ('rack_depth',       '250 mm',                                'mm',  'Overall front-to-back depth'),
    ('post_w',           '16 mm',                                 'mm',  'Post width across the rack (0.625 in rail convention)'),
    ('post_d',           '25 mm',                                 'mm',  'Post depth front-to-back'),
    ('post_end_margin',  '10 mm',                                 'mm',  'Post material below U1 and above the top U'),
    ('plate_t',          '10 mm',                                 'mm',  'Top/bottom plate thickness'),
    ('plate_border',     '30 mm',                                 'mm',  'Plate border width around the central opening'),
    ('pocket_depth',     '6 mm',                                  'mm',  'Depth the post plugs into the plate'),
    ('cup_wall_t',       '4 mm',                                  'mm',  'Corner cup wall thickness'),
    ('cup_wall_h',       '10 mm',                                 'mm',  'Corner cup wall height above the plate'),
    ('fit_clear',        '0.15 mm',                               'mm',  'Clearance per side, post to pocket'),
    ('insert_m6_d',      '8 mm',                                  'mm',  'M6 heat-set insert hole dia - VERIFY against your inserts'),
    ('insert_m6_depth',  '10 mm',                                 'mm',  'M6 heat-set insert hole depth'),
    ('m6_clear_d',       '6.6 mm',                                'mm',  'M6 clearance hole'),
    ('m6_csk_d',         '12 mm',                                 'mm',  'M6 countersunk head diameter'),
    ('m6_csk_angle',     '90 deg',                                'deg', 'M6 countersink included angle'),
    ('edge_cham',        '1 mm',                                  'mm',  'Chamfer on the four long edges of a post'),
    ('end_cham',         '0.5 mm',                                'mm',  'Lead-in chamfer on the post ends'),
    ('first_layer_cham', '0.5 mm',                                'mm',  'First-layer (elephant-foot) chamfer on the plate bed face'),
    ('plate_corner_r',   '3 mm',                                  'mm',  'Plate outer corner radius (ABS warp relief)'),
    ('mouse_ear_r',      '8 mm',                                  'mm',  'Mouse ear radius'),
    ('mouse_ear_t',      '0.4 mm',                                'mm',  'Mouse ear thickness (2 layers at 0.2 mm)'),
    ('rail_height',      'rack_u * u_height',                     'mm',  'Total mounting height'),
    ('post_len',         'rail_height + 2 * post_end_margin',     'mm',  'Post length'),
    ('rack_width',       'rail_hole_pitch + 2 * rail_edge_inset', 'mm',  'Overall width (254 mm)'),
    ('m6_csk_depth',     '(m6_csk_d - m6_clear_d) / 2 / tan(m6_csk_angle / 2)', 'mm', 'Countersink depth'),
]

# Hole centres within one U, measured from the bottom of that U (EIA-310)
U_HOLE_OFFSETS_MM = (6.35, 22.225, 38.10)


class Log(list):
    """Collects report lines and echoes them, so partial progress survives a failure."""

    def append(self, msg):
        print(msg)
        super(Log, self).append(msg)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def p3(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(x_mm * MM, y_mm * MM, z_mm * MM)


def coll(items):
    c = adsk.core.ObjectCollection.create()
    for it in items:
        c.add(it)
    return c


def add_params(design):
    ups = design.userParameters
    out = {}
    for name, expr, units, comment in PARAM_DEFS:
        existing = ups.itemByName(name)
        if existing:
            existing.expression = expr
            out[name] = existing
        else:
            out[name] = ups.add(name, vi(expr), units, comment)
    return out


def mm_of(params, name):
    return params[name].value / MM


def sketch_on(root, plane, name):
    sk = root.sketches.add(plane)
    sk.name = name
    sk.isComputeDeferred = True
    return sk


def finish(sk):
    sk.isComputeDeferred = False
    return [p for p in sk.profiles]


def rect(sk, x0, y0, x1, y1, z=0.0):
    # Coordinates are WORLD mm; convert so the geometry lands in the sketch plane.
    return sk.sketchCurves.sketchLines.addTwoPointRectangle(
        sk.modelToSketchSpace(p3(x0, y0, z)), sk.modelToSketchSpace(p3(x1, y1, z)))


def circle(sk, x, y, z, d_mm):
    return sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(p3(x, y, z)), d_mm * MM / 2.0)


def teardrop(sk, cx, cy, cz, d_mm, up_vec):
    """Closed teardrop loop: a 270 deg arc plus two 45 deg flanks meeting at an
    apex pointing along `up_vec` (world direction that will be 'up' when printed)."""
    c = sk.modelToSketchSpace(p3(cx, cy, cz))
    u = sk.modelToSketchSpace(p3(cx + up_vec[0], cy + up_vec[1], cz + up_vec[2]))
    ux, uy = u.x - c.x, u.y - c.y
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    r = d_mm * MM / 2.0

    def polar(deg, rad):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        return adsk.core.Point3D.create(c.x + rad * (ux * ca - uy * sa),
                                        c.y + rad * (ux * sa + uy * ca), 0)

    arc = sk.sketchCurves.sketchArcs.addByCenterStartSweep(
        adsk.core.Point3D.create(c.x, c.y, 0), polar(45, r), math.radians(270))
    lines = sk.sketchCurves.sketchLines
    l1 = lines.addByTwoPoints(arc.endSketchPoint, polar(0, r * math.sqrt(2.0)))
    lines.addByTwoPoints(l1.endSketchPoint, arc.startSketchPoint)
    return arc


def _extrude(root, profiles, op, side_one, side_two=None, participants=None, taper=None):
    feats = root.features.extrudeFeatures
    inp = feats.createInput(coll(profiles), op)
    dd = adsk.fusion.DistanceExtentDefinition.create
    if side_two is not None:
        inp.setTwoSidesExtent(dd(vi(side_one)), dd(vi(side_two)))
    elif taper is not None:
        try:
            inp.setOneSideExtent(dd(vi(side_one)),
                                 adsk.fusion.ExtentDirections.PositiveExtentDirection,
                                 vi(taper))
        except Exception:
            inp.setDistanceExtent(False, vi(side_one))
            inp.taperAngle = vi(taper)
    else:
        inp.setDistanceExtent(False, vi(side_one))
    if participants:
        inp.participantBodies = participants
    return feats.add(inp)


def new_body(root, profiles, dist):
    return _extrude(root, profiles, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, dist)


def cut(root, profiles, dist, participants, side_two=None, taper=None):
    return _extrude(root, profiles, adsk.fusion.FeatureOperations.CutFeatureOperation,
                    dist, side_two=side_two, participants=participants, taper=taper)


def join(root, profiles, dist, participants):
    return _extrude(root, profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation,
                    dist, participants=participants)


def smallest_profile(profiles):
    acc = adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
    best, best_a = None, None
    for p in profiles:
        try:
            a = p.areaProperties(acc).area
        except Exception:
            continue
        if best_a is None or a < best_a:
            best, best_a = p, a
    return best


def face_at_z(body, z_mm):
    """The planar face lying in the plane Z == z_mm (there is only one per end)."""
    target = z_mm * MM
    for f in body.faces:
        g = f.geometry
        if g.objectType != adsk.core.Plane.classType():
            continue
        if abs(g.normal.z) < 0.999:
            continue
        if abs(g.origin.z - target) < 1e-3:
            return f
    return None


def loop_edges(face, outer=True, min_span_mm=None):
    out = []
    for lp in face.loops:
        if lp.isOuter != outer:
            continue
        if min_span_mm is not None:
            bb = lp.boundingBox
            span = max(bb.maxPoint.x - bb.minPoint.x, bb.maxPoint.y - bb.minPoint.y)
            if span < min_span_mm * MM:
                continue
        out.extend([e for e in lp.edges])
    return out


def vertical_corner_edges(body, corners_mm, length_mm):
    found = []
    for e in body.edges:
        g = e.geometry
        if g.objectType != adsk.core.Line3D.classType():
            continue
        d = g.startPoint.vectorTo(g.endPoint)
        if abs(abs(d.z) - d.length) > 1e-6 or abs(d.length - length_mm * MM) > 1e-3:
            continue
        x, y = g.startPoint.x, g.startPoint.y
        for cx, cy in corners_mm:
            if abs(x - cx * MM) < 1e-3 and abs(y - cy * MM) < 1e-3:
                found.append(e)
                break
    return found


def chamfer(root, edges, expr):
    if not edges:
        return None
    feats = root.features.chamferFeatures
    inp = feats.createInput2()
    inp.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll(edges), vi(expr), True)
    return feats.add(inp)


def fillet(root, edges, expr):
    if not edges:
        return None
    feats = root.features.filletFeatures
    inp = feats.createInput()
    inp.addConstantRadiusEdgeSet(coll(edges), vi(expr), True)
    return feats.add(inp)


def mirror(root, bodies, plane):
    feats = root.features.mirrorFeatures
    return feats.add(feats.createInput(coll(bodies), plane))


def offset_plane(root, base, expr, name):
    inp = root.constructionPlanes.createInput()
    inp.setByOffset(base, vi(expr))
    pl = root.constructionPlanes.add(inp)
    pl.name = name
    return pl


# --------------------------------------------------------------------------
# post
# --------------------------------------------------------------------------

def build_post(root, P, log):
    half_w = mm_of(P, 'rack_width') / 2.0
    post_w = mm_of(P, 'post_w')
    post_d = mm_of(P, 'post_d')
    post_len = mm_of(P, 'post_len')
    margin = mm_of(P, 'post_end_margin')
    pitch = mm_of(P, 'rail_hole_pitch')
    ins_d = mm_of(P, 'insert_m6_d')

    x_out, x_in = -half_w, -half_w + post_w
    x_hole = -pitch / 2.0
    x_mid = (x_out + x_in) / 2.0
    y_mid = post_d / 2.0

    sk = sketch_on(root, root.xYConstructionPlane, 'Post section')
    rect(sk, x_out, 0.0, x_in, post_d)
    post = new_body(root, finish(sk), 'post_len').bodies.item(0)
    post.name = 'Post'
    log.append('post bar: X %.4f..%.4f, Y 0..%.1f, Z 0..%.2f mm' % (x_out, x_in, post_d, post_len))

    # Rail insert holes for U1, then a rectangular pattern of quantity rack_u.
    # Two-sided cut so the result does not depend on which way the XZ profile
    # normal points; the far side meets no material.
    sk = sketch_on(root, root.xZConstructionPlane, 'Rail holes U1')
    for off in U_HOLE_OFFSETS_MM:
        circle(sk, x_hole, 0.0, margin + off, ins_d)
    hole_cut = cut(root, finish(sk), 'insert_m6_depth', [post], side_two='insert_m6_depth')

    pats = root.features.rectangularPatternFeatures
    pinp = pats.createInput(coll([hole_cut]), root.zConstructionAxis, vi('rack_u'),
                            vi('u_height'),
                            adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    pats.add(pinp)
    log.append('rail holes: 3 per U at 6.35/22.225/38.10, patterned x rack_u @ u_height')

    # End insert holes - horizontal when printed, so teardrop with the apex
    # toward the front face (which is 'up' on the bed).
    sk = sketch_on(root, root.xYConstructionPlane, 'Post end hole bottom')
    teardrop(sk, x_mid, y_mid, 0.0, ins_d, (0.0, -1.0, 0.0))
    cut(root, finish(sk), 'insert_m6_depth', [post], side_two='insert_m6_depth')

    top_plane = offset_plane(root, root.xYConstructionPlane, 'post_len', 'Post top')
    sk = sketch_on(root, top_plane, 'Post end hole top')
    teardrop(sk, x_mid, y_mid, post_len, ins_d, (0.0, -1.0, 0.0))
    cut(root, finish(sk), 'insert_m6_depth', [post], side_two='insert_m6_depth')

    long_edges = vertical_corner_edges(
        post, [(x_out, 0.0), (x_in, 0.0), (x_out, post_d), (x_in, post_d)], post_len)
    chamfer(root, long_edges, 'edge_cham')
    log.append('post long-edge chamfer: %d edges' % len(long_edges))

    for z in (0.0, post_len):
        f = face_at_z(post, z)
        if f:
            chamfer(root, loop_edges(f, outer=True), 'end_cham')
    return post


# --------------------------------------------------------------------------
# plate
# --------------------------------------------------------------------------

def build_plate(root, P, log):
    half_w = mm_of(P, 'rack_width') / 2.0
    depth = mm_of(P, 'rack_depth')
    post_w = mm_of(P, 'post_w')
    post_d = mm_of(P, 'post_d')
    plate_t = mm_of(P, 'plate_t')
    border = mm_of(P, 'plate_border')
    clr = mm_of(P, 'fit_clear')
    cw = mm_of(P, 'cup_wall_t')
    corner_r = mm_of(P, 'plate_corner_r')
    ear_r = mm_of(P, 'mouse_ear_r')
    csk_d = mm_of(P, 'm6_csk_d')

    sk = sketch_on(root, root.xYConstructionPlane, 'Plate outline')
    rect(sk, -half_w, 0.0, half_w, depth)
    rect(sk, -half_w + border, border, half_w - border, depth - border)
    ring = smallest_profile(finish(sk))
    plate = new_body(root, [ring], '-plate_t').bodies.item(0)
    plate.name = 'Plate'

    corners = [(-half_w, 0.0), (half_w, 0.0), (-half_w, depth), (half_w, depth)]
    fillet(root, vertical_corner_edges(plate, corners, plate_t), 'plate_corner_r')

    xi = half_w - post_w  # inner face of a post, as a positive number

    # corner pockets, open to the outside faces
    sk = sketch_on(root, root.xYConstructionPlane, 'Plate pockets')
    for sx in (-1, 1):
        for sy in (0, 1):
            xa, xb = sx * (xi - clr), sx * (half_w + 2.0)
            ya = -2.0 if sy == 0 else depth + 2.0
            yb = (post_d + clr) if sy == 0 else (depth - post_d - clr)
            rect(sk, min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb))
    cut(root, finish(sk), '-pocket_depth', [plate])

    # corner cup walls: an L on the two inner sides of each pocket
    sk = sketch_on(root, root.xYConstructionPlane, 'Plate cup walls')
    for sx in (-1, 1):
        for sy in (0, 1):
            xa, xb = sx * (xi - clr), sx * (xi - clr - cw)
            y0 = 0.0 if sy == 0 else depth
            y1 = (post_d + clr + cw) if sy == 0 else (depth - post_d - clr - cw)
            rect(sk, min(xa, xb), min(y0, y1), max(xa, xb), max(y0, y1))
            xc = sx * half_w
            ya = (post_d + clr) if sy == 0 else (depth - post_d - clr)
            rect(sk, min(xb, xc), min(ya, y1), max(xb, xc), max(ya, y1))
    join(root, finish(sk), 'cup_wall_h', [plate])

    # M6 clearance holes, countersunk on the outer (bed) face
    bed_face = face_at_z(plate, -plate_t)
    sk = sketch_on(root, bed_face, 'Plate bolt holes')
    pts = []
    for sx in (-1, 1):
        for sy in (0, 1):
            x = sx * (half_w - post_w / 2.0)
            y = post_d / 2.0 if sy == 0 else depth - post_d / 2.0
            pts.append(sk.sketchPoints.add(sk.modelToSketchSpace(p3(x, y, -plate_t))))
    sk.isComputeDeferred = False
    holes = root.features.holeFeatures
    hinp = holes.createCountersinkInput(vi('m6_clear_d'), vi('m6_csk_d'), vi('m6_csk_angle'))
    hinp.setPositionBySketchPoints(coll(pts))
    hinp.setDistanceExtent(vi('plate_t'))
    hinp.participantBodies = [plate]
    try:
        holes.add(hinp)
    except Exception:
        hinp.isDefaultDirectionFlipped = not hinp.isDefaultDirectionFlipped
        holes.add(hinp)
    bed_plane = offset_plane(root, root.xYConstructionPlane, '-plate_t', 'Plate bed')
    log.append('plate: 4 countersunk M6 clearance holes, heads flush on the outer face')

    # first-layer chamfer on the bed face: outer perimeter + central opening
    bed = face_at_z(plate, -plate_t)
    bed_edges = loop_edges(bed, outer=True) + loop_edges(bed, outer=False, min_span_mm=50.0)
    chamfer(root, bed_edges, 'first_layer_cham')
    log.append('plate first-layer chamfer: %d bed edges' % len(bed_edges))

    # mouse ears, centred 2 mm outside the corner arc midpoints
    sk = sketch_on(root, bed_plane, 'Plate mouse ears')
    d = (corner_r + 2.0) / math.sqrt(2.0)
    for sx in (-1, 1):
        for sy in (0, 1):
            cx = sx * (half_w - corner_r + d)
            cy = (corner_r - d) if sy == 0 else (depth - corner_r + d)
            circle(sk, cx, cy, -plate_t, ear_r * 2.0)
    ears = []
    for prof in finish(sk):
        f = new_body(root, [prof], 'mouse_ear_t')
        for b in f.bodies:
            b.name = 'Support - Mouse Ear'
            ears.append(b)
    log.append('plate mouse ears: %d (R %.1f x %.1f mm)' % (len(ears), ear_r, mm_of(P, 'mouse_ear_t')))
    return plate, ears


# --------------------------------------------------------------------------

def run(_context: str):
    app = adsk.core.Application.get()
    log = Log()

    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    try:
        design.fusionUnitsManager.distanceDisplayUnits = \
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    except Exception:
        pass
    root = design.rootComponent

    P = add_params(design)
    log.append('user parameters: %d' % len(P))

    post = build_post(root, P, log)

    mid_depth = offset_plane(root, root.xZConstructionPlane, 'rack_depth / 2', 'Mid depth')
    mid_height = offset_plane(root, root.xYConstructionPlane, 'post_len / 2', 'Mid height')

    mirror(root, [post], root.yZConstructionPlane)
    fronts = [b for b in root.bRepBodies]
    mirror(root, fronts, mid_depth)

    plate, ears = build_plate(root, P, log)
    mirror(root, [plate] + ears, mid_height)

    # name bodies by size
    post_len = mm_of(P, 'post_len')
    posts, plates, supports = [], [], []
    for b in root.bRepBodies:
        bb = b.boundingBox
        h = (bb.maxPoint.z - bb.minPoint.z) / MM
        if h < 1.0:
            supports.append(b)
        elif abs(h - post_len) < 0.5:
            posts.append(b)
        else:
            plates.append(b)
    posts.sort(key=lambda b: (round(b.boundingBox.minPoint.y, 4), b.boundingBox.minPoint.x))
    for name, b in zip(['Post FL', 'Post FR', 'Post RL', 'Post RR'], posts):
        b.name = name
    plates.sort(key=lambda b: b.boundingBox.minPoint.z)
    for name, b in zip(['Plate Bottom', 'Plate Top'], plates):
        b.name = name
    supports.sort(key=lambda b: (b.boundingBox.minPoint.z, b.boundingBox.minPoint.y,
                                 b.boundingBox.minPoint.x))
    for i, b in enumerate(supports, 1):
        b.name = 'Support - Mouse Ear %d' % i

    # ---------------- verification ----------------
    half_w = mm_of(P, 'rack_width') / 2.0
    pitch = mm_of(P, 'rail_hole_pitch')
    rack_u = int(round(P['rack_u'].value))
    log.append('')
    log.append('bodies: %d posts, %d plates, %d mouse ears' %
               (len(posts), len(plates), len(supports)))
    for b in posts + plates:
        bb = b.boundingBox
        log.append('  %-13s X %9.3f..%9.3f  Y %8.3f..%8.3f  Z %8.3f..%8.3f' % (
            b.name, bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
            bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM))

    bad = []
    for b in posts:
        sign = -1.0 if b.boundingBox.minPoint.x < 0 else 1.0
        front = b.boundingBox.minPoint.y / MM < 1.0
        y_probe = 3.0 if front else mm_of(P, 'rack_depth') - 3.0
        for u in range(rack_u):
            for off in U_HOLE_OFFSETS_MM:
                z = mm_of(P, 'post_end_margin') + u * mm_of(P, 'u_height') + off
                if b.pointContainment(p3(sign * pitch / 2.0, y_probe, z)) != 2:
                    bad.append((b.name, u + 1, off))
    log.append('rail-hole probe: %d holes checked, %d missing' %
               (len(posts) * rack_u * 3, len(bad)))
    if bad:
        log.append('  MISSING: %s' % bad[:8])

    unhealthy = []
    for i in range(design.timeline.count):
        it = design.timeline.item(i)
        if it.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            unhealthy.append((it.name, it.errorOrWarningMessage))
    log.append('timeline: %d features, %d unhealthy' % (design.timeline.count, len(unhealthy)))
    for n, m in unhealthy:
        log.append('  !! %s: %s' % (n, m))

    xs, ys, zs = [], [], []
    for b in posts + plates:
        bb = b.boundingBox
        xs += [bb.minPoint.x, bb.maxPoint.x]
        ys += [bb.minPoint.y, bb.maxPoint.y]
        zs += [bb.minPoint.z, bb.maxPoint.z]
    log.append('overall W x D x H = %.2f x %.2f x %.2f mm' % (
        (max(xs) - min(xs)) / MM, (max(ys) - min(ys)) / MM, (max(zs) - min(zs)) / MM))
    log.append('rail pitch %.3f mm | clear between posts %.2f mm | %dU rail = %.2f mm' % (
        pitch, 2 * (half_w - mm_of(P, 'post_w')), rack_u, mm_of(P, 'rail_height')))

    tbm = adsk.fusion.TemporaryBRepManager.get()
    hits = 0
    for pb in posts:
        for pl in plates:
            a = tbm.copy(pb)
            if tbm.booleanOperation(a, tbm.copy(pl),
                                    adsk.fusion.BooleanTypes.IntersectionBooleanType):
                if a.volume > 1e-6:
                    hits += 1
    log.append('post/plate interference: %d (expect 0)' % hits)

    # ---------------- save ----------------
    rootf = app.data.activeProject.rootFolder
    folder = None
    for f in rootf.dataFolders:
        if f.name.strip().lower() == TARGET_FOLDER.lower():
            folder = f
            break
    if folder is None:
        log.append('WARNING: folder "%s" not found; saving to project root' % TARGET_FOLDER)
        folder = rootf
    for df in folder.dataFiles:
        if df.name == DOC_NAME:
            log.append('replacing existing "%s" (v%s) in %s' % (df.name, df.versionNumber, folder.name))
            df.deleteMe()
            break
    doc.saveAs(DOC_NAME, folder, 'Parametric 10 inch rack frame', '')
    log.append('saved "%s" in "%s"' % (DOC_NAME, folder.name))

    return '\n'.join(log)
