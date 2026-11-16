"""
MOD-GRID baseplate - parametric, 3D printable. 12 x 4 cells (99 x 35 mm) by default.

Spec measured from the official MOD-GRID files; see research/modgrid-edc-system.md.
  grid pitch 8.000 mm | hole 5.000 mm square, straight through | plate 3.000 mm thick
  border 3.000 mm | plate size = pitch * n + border = 8n + 3

Change `grid_x` / `grid_y` in Fusion's parameter dialog and the plate follows: the outline
is driven by expressions and the holes are a two-direction rectangular pattern whose
quantities are grid_x and grid_y.

Printed flat, hole axes are vertical: no overhangs, no bridges, nothing to design out.
The one FDM risk is elephant foot closing the 5 mm holes, so every bed-face edge -
including all 48 hole mouths - gets a first-layer chamfer.

Fusion script entry point: run(_context).
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1  # mm -> Fusion internal cm

TARGET_FOLDER = 'Mod Grid'

PARAM_DEFS = [
    ('grid_x',           '12',                              '',   'Cells along X - the main variable'),
    ('grid_y',           '8',                               '',   'Cells along Y - the main variable'),
    ('grid_pitch',       '8 mm',                            'mm', 'MOD-GRID pitch (measured from the official 4x12)'),
    ('hole_size',        '5 mm',                            'mm', 'Square hole across flats (measured: 5.000)'),
    ('hole_clear',       '0.07 mm',                         'mm', 'Per-side hole adjustment. MEASURED: this printer puts out a 4.86 hole from a 5.00 model, i.e. 0.07 per wall undersize, so +0.07 per side makes the PRINTED hole a true 5.00 - which also makes official accessories fit properly. Re-measure and reset if the printer or material changes.'),
    ('plate_t',          '3 mm',                            'mm', 'Plate thickness (measured: 3.000)'),
    ('border',           '3 mm',                            'mm', 'Edge to first hole; equals the wall between holes'),
    ('corner_r',         '3 mm',                            'mm', 'Outer corner radius'),
    ('first_layer_cham', '0.3 mm',                          'mm', 'Elephant-foot chamfer on every bed-face edge. Kept SMALL because it opens the hole on the underside, which is exactly where the barb catches: at 0.5 the barb had only 0.19 mm of catch left, at 0.3 it has 0.39.'),
    ('hole_lead_in',     '0.4 mm',                          'mm', 'Lead-in chamfer on the TOP of each hole so a peg starts square instead of jamming on a sharp lip. The official plate has none; this eases ENTRY but does not widen the parallel section, so it is NOT a fix for holes printing undersize - use hole_clear for that.'),
    ('hole_w',           'hole_size + 2 * hole_clear',      'mm', 'Actual modelled hole width'),
    ('plate_x',          'grid_pitch * grid_x + border',    'mm', 'Plate length (8n + 3)'),
    ('plate_y',          'grid_pitch * grid_y + border',    'mm', 'Plate width (8n + 3)'),
]


class Log(list):
    def append(self, msg):
        print(msg)
        super(Log, self).append(msg)


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def p3(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


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


def mm_of(P, name):
    return P[name].value / MM


def sketch_on(root, plane, name):
    sk = root.sketches.add(plane)
    sk.name = name
    sk.isComputeDeferred = True
    return sk


def finish(sk):
    sk.isComputeDeferred = False
    return [p for p in sk.profiles]


def rect(sk, x0, y0, x1, y1, z=0.0):
    # WORLD mm in, converted into the sketch plane
    return sk.sketchCurves.sketchLines.addTwoPointRectangle(
        sk.modelToSketchSpace(p3(x0, y0, z)), sk.modelToSketchSpace(p3(x1, y1, z)))


def circle(sk, x, y, z, d_mm):
    return sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(p3(x, y, z)), d_mm * MM / 2.0)


def _grid_default(name):
    return int([d for d in PARAM_DEFS if d[0] == name][0][1])


# Each grid size gets its own document, so building a bigger plate does not
# overwrite a smaller one you still use.
DOC_NAME = 'MOD-GRID Baseplate %dx%d' % (_grid_default('grid_x'), _grid_default('grid_y'))


def _dim(sk, p1, p2, expr, horizontal, tx, ty):
    """Driving distance dimension so the sketch follows the user parameters."""
    orient = (adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation if horizontal
              else adsk.fusion.DimensionOrientations.VerticalDimensionOrientation)
    d = sk.sketchDimensions.addDistanceDimension(
        p1, p2, orient, sk.modelToSketchSpace(p3(tx, ty, 0.0)), True)
    d.parameter.expression = expr
    return d


def _extrude(root, profiles, op, side_one, side_two=None, participants=None):
    feats = root.features.extrudeFeatures
    inp = feats.createInput(coll(profiles), op)
    dd = adsk.fusion.DistanceExtentDefinition.create
    if side_two is not None:
        inp.setTwoSidesExtent(dd(vi(side_one)), dd(vi(side_two)))
    else:
        inp.setDistanceExtent(False, vi(side_one))
    if participants:
        inp.participantBodies = participants
    return feats.add(inp)


def new_body(root, profiles, dist):
    return _extrude(root, profiles, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, dist)


def cut(root, profiles, dist, participants, side_two=None):
    return _extrude(root, profiles, adsk.fusion.FeatureOperations.CutFeatureOperation,
                    dist, side_two=side_two, participants=participants)


def face_at_z(body, z_mm):
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


def loop_edges(face, outer=True):
    out = []
    for lp in face.loops:
        if lp.isOuter == outer:
            out.extend([e for e in lp.edges])
    return out


def edges_in_box(body, z_mm, x0, y0, x1, y1, pad=0.2):
    """Edges lying in the plane Z == z_mm whose midpoint falls inside the box."""
    out = []
    zt = z_mm * MM
    for e in body.edges:
        bb = e.boundingBox
        if abs(bb.minPoint.z - zt) > 1e-3 or abs(bb.maxPoint.z - zt) > 1e-3:
            continue
        mx = (bb.minPoint.x + bb.maxPoint.x) / 2.0 / MM
        my = (bb.minPoint.y + bb.maxPoint.y) / 2.0 / MM
        if x0 - pad <= mx <= x1 + pad and y0 - pad <= my <= y1 + pad:
            out.append(e)
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


def run(_context: str):
    app = adsk.core.Application.get()
    log = Log()

    # Resolve the target folder and document up front. Never delete-then-save under
    # the same name: the data-side delete is asynchronous and can land *after* the
    # save, taking the new file with it. Rebuild into the existing document instead,
    # which also keeps version history. NOTE: this wipes any manual edits.
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
        log.append('rebuilding into existing "%s" (was v%s); timeline cleared'
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
    log.append('user parameters: %d' % len(P))

    px = mm_of(P, 'plate_x')
    py = mm_of(P, 'plate_y')
    pt = mm_of(P, 'plate_t')
    border = mm_of(P, 'border')
    hw = mm_of(P, 'hole_w')
    corner_r = mm_of(P, 'corner_r')
    gx = int(round(P['grid_x'].value))
    gy = int(round(P['grid_y'].value))

    # 1. plate
    sk = sketch_on(root, root.xYConstructionPlane, 'Plate outline')
    lines = rect(sk, 0.0, 0.0, px, py)
    ll = lines.item(0).startSketchPoint
    lr = lines.item(0).endSketchPoint
    ur = lines.item(1).endSketchPoint
    sk.geometricConstraints.addCoincident(ll, sk.originPoint)
    _dim(sk, ll, lr, 'plate_x', True, px / 2.0, -8.0)
    _dim(sk, lr, ur, 'plate_y', False, px + 8.0, py / 2.0)
    plate = new_body(root, finish(sk), 'plate_t').bodies.item(0)
    plate.name = 'Baseplate'
    log.append('plate %.3f x %.3f x %.3f mm' % (px, py, pt))

    corners = [(0.0, 0.0), (px, 0.0), (0.0, py), (px, py)]
    fillet(root, vertical_corner_edges(plate, corners, pt), 'corner_r')

    # 2. one hole, then a two-direction pattern of grid_x by grid_y
    sk = sketch_on(root, root.xYConstructionPlane, 'Hole cell')
    lines = rect(sk, border, border, border + hw, border + hw)
    ll = lines.item(0).startSketchPoint
    lr = lines.item(0).endSketchPoint
    ur = lines.item(1).endSketchPoint
    _dim(sk, sk.originPoint, ll, 'border', True, border / 2.0, -6.0)
    _dim(sk, sk.originPoint, ll, 'border', False, -6.0, border / 2.0)
    _dim(sk, ll, lr, 'hole_w', True, border + hw / 2.0, border - 4.0)
    _dim(sk, lr, ur, 'hole_w', False, border + hw + 4.0, border + hw / 2.0)
    hole_cut = cut(root, finish(sk), 'plate_t', [plate], side_two='plate_t')

    # 3. Chamfer this ONE hole's bed-face edges, then pattern the cut and the
    #    chamfer together. Chamfering after the pattern stores ~200 edge
    #    references and breaks as soon as grid_x/grid_y shrinks; chamfering the
    #    bed FACE instead only catches its outer loop and leaves every hole
    #    mouth sharp, which is exactly what elephant foot would close up.
    hole_edges = edges_in_box(plate, 0.0, border, border, border + hw, border + hw)
    hole_cham = chamfer(root, hole_edges, 'first_layer_cham')
    log.append('hole mouth chamfer: %d edges on one cell (bed face)' % len(hole_edges))

    # Lead-in on the TOP of the hole, so a peg starts square rather than jamming
    # on a sharp lip. Patterned along with the cut, same as the bed chamfer.
    top_edges = edges_in_box(plate, mm_of(P, 'plate_t'), border, border,
                             border + hw, border + hw)
    top_cham = chamfer(root, top_edges, 'hole_lead_in')
    log.append('hole lead-in chamfer: %d edges on one cell (top face)' % len(top_edges))

    pats = root.features.rectangularPatternFeatures
    targets = ([hole_cut] + ([hole_cham] if hole_cham else [])
               + ([top_cham] if top_cham else []))
    pinp = pats.createInput(coll(targets), root.xConstructionAxis, vi('grid_x'),
                            vi('grid_pitch'),
                            adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    pinp.setDirectionTwo(root.yConstructionAxis, vi('grid_y'), vi('grid_pitch'))
    pats.add(pinp)
    log.append('holes: %.3f mm square at %.3f pitch, cut+chamfer patterned grid_x x grid_y'
               % (hw, mm_of(P, 'grid_pitch')))

    # outer perimeter: 8 edges that always exist, so this reference is stable
    bed = face_at_z(plate, 0.0)
    outer = loop_edges(bed, outer=True)
    chamfer(root, outer, 'first_layer_cham')
    log.append('first-layer chamfer on %d outer perimeter edges' % len(outer))

    # 4. NO mouse ears. The plate's footprint corners are already filleted
    #    (corner_r), and a rounded corner has no stress concentration to lift, so
    #    ears there are redundant. Keep them for SHARP-cornered ABS parts only.
    #    See the warping section of research/design-for-fdm-printing.md.
    ears = []

    # ---------------- verification ----------------
    bb = plate.boundingBox
    log.append('')
    log.append('plate bbox  X %.4f..%.4f  Y %.4f..%.4f  Z %.4f..%.4f' % (
        bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
        bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM))

    pitch = mm_of(P, 'grid_pitch')
    missing, solid_bad = [], []
    for i in range(gx):
        for j in range(gy):
            cx = border + hw / 2.0 + i * pitch
            cy = border + hw / 2.0 + j * pitch
            if plate.pointContainment(p3(cx, cy, pt / 2.0)) != 2:
                missing.append((i, j))
            # the wall midway between two holes must be solid
            if i < gx - 1:
                if plate.pointContainment(p3(cx + pitch / 2.0, cy, pt / 2.0)) != 0:
                    solid_bad.append(('wall x', i, j))
    log.append('hole probe: %d/%d open, %d wall points solid-checked, %d bad'
               % (gx * gy - len(missing), gx * gy, (gx - 1) * gy, len(solid_bad)))
    if missing:
        log.append('  MISSING: %s' % missing[:8])
    if solid_bad:
        log.append('  WALL FAIL: %s' % solid_bad[:8])

    def opening(z):
        x = border
        while x > border - 2.0 and plate.pointContainment(
                p3(x - 0.01, border + hw / 2.0, z)) == 2:
            x -= 0.01
        return hw + 2 * (border - x)
    cham = mm_of(P, 'first_layer_cham')
    zp = 0.02
    # probing zp above the bed walks partway up the 45 deg chamfer, so the
    # opening there is hw + 2*(cham - zp), not the full hw + 2*cham
    want_bed = hw + 2 * (cham - zp)
    bed_open, top_open = opening(zp), opening(pt - zp)
    top_lead = mm_of(P, 'hole_lead_in')
    log.append('hole opening: bed %.3f mm (want %.3f at z=%.2f)  top %.3f mm (want %.3f)'
               % (bed_open, want_bed, zp, top_open, hw))
    parallel = pt - cham - top_lead
    log.append('hole profile: %.2f lead-in | %.2f PARALLEL (this is what grips) | %.2f bed chamfer'
               % (top_lead, parallel, cham))
    if parallel < 1.5:
        log.append('  !! parallel section under 1.5 mm - chamfers are eating the grip')
    if abs(bed_open - want_bed) > 0.05:
        log.append('  !! BED CHAMFER MISSING - elephant foot will close these holes')

    extra = [b.name for b in root.bRepBodies if b.name != plate.name]
    log.append('bodies: 1 plate, %d support bodies (expect 0 - corners are rounded)'
               % len(extra))
    if extra:
        log.append('  !! unexpected extra bodies: %s' % extra)

    unhealthy = []
    for i in range(design.timeline.count):
        it = design.timeline.item(i)
        if it.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            unhealthy.append((it.name, it.errorOrWarningMessage))
    log.append('timeline: %d features, %d unhealthy' % (design.timeline.count, len(unhealthy)))
    for n, m in unhealthy:
        log.append('  !! %s: %s' % (n, m))

    log.append('rule check: pitch*n + border = %.3f x %.3f (stock 4x12 is 99.000 x 35.000)'
               % (px, py))
    log.append('plate volume %.1f mm3' % (plate.volume / (MM ** 3)))

    # ---------------- save ----------------
    if existing is not None:
        doc.save('Rebuilt from modgrid_baseplate.py')
    else:
        doc.saveAs(DOC_NAME, folder, 'Parametric MOD-GRID baseplate', '')
    adsk.doEvents()
    landed = None
    for df in folder.dataFiles:
        if df.name == DOC_NAME:
            landed = df
            break
    if landed is None:
        log.append('save initiated; not in the Data Panel yet (cloud publish is '
                   'asynchronous - re-check in a minute)')
    else:
        log.append('saved "%s" v%s in "%s"' % (landed.name, landed.versionNumber, folder.name))

    return '\n'.join(log)
