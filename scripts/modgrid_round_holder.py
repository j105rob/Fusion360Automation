"""
MOD-GRID round-part holder - two bands that hold a CYLINDER flat against the plate.

Built for two parts from one script, selected by the module-level PART:

    'pill'    a 17.0 mm x 40 mm pill bottle
    'olight'  an Olight i Mini 2 flashlight, 15.1 mm x 55 mm

This is the Zippo/Skeletool band architecture with ONE change: the cavity's
bottom is a SEMICIRCLE instead of a rounded rectangle. Everything else - the
45/45 capture lip with a rounded tip, the concentric relief slot, the tapered
arm, the measured root web, the barbed snap legs, the first-layer chamfer - is
the same code, because it is the same problem.

WHY A CYLINDER IS THE EASY CASE. Every failure on the Zippo came from not
knowing the case's corner radius: the lip has to be placed off that radius, it
was never measured, and three versions jammed or sat proud because of it. On a
cylinder the "corner radius" IS the part radius, exactly and by definition. Put
the numbers through the lip-placement formula and the radius cancels:

    the lip underside is the line  y + z = K,  K = sqrt(2)*(R + clear) + w/2
                                                   + part_top - 2R
    for a cylinder  w = D,  R = D/2,  part_top = base_t + D, so
    K = sqrt(2)*(D/2 + clear) + D/2 + base_t
    and the distance from the part's axis to that line, minus D/2, is EXACTLY
    `clear` - for any D.

So there is no estimate to be wrong about and no sensitivity sweep to run. What
IS uncertain is the diameter itself, and that is what run() sweeps instead: a
part `dia_err` bigger than nominal eats about 0.85 * dia_err of lip_clear, so
lip_clear is sized from how well the diameter is known.

BUT THE LIP IS NOT THAT LINE, AND THAT COST THE OLIGHT TWO PRINTS (2026-10-28).
The formula above is exact for an INFINITE 45 deg plane. The real lip is only
`lip_proj` tall - 0.72 mm here - and it sits well below the point where that
line touches the cylinder, which is the part's 45 deg point at
z = part_z + 0.707 * D/2. The part therefore never reaches the face the
clearance was derived on: its closest approach is to the lip's TIP RADIUS, and
on the Olight that stood 0.67 mm off a part the parameter said was 0.30 away.

Free lift goes as the square root of that gap, so being 2.2x out on clearance
was 2.8x out on lift: the cap could rise 1.52 mm before the lip bit, on a band
only 12 mm tall. That is what "still too loose" was, twice, while the bore was
already as tight as the proven Zippo band.

`lip_z0` is now solved from the tip radius instead, which is a closed form just
as exact and measures the thing the part actually touches:

    lip_zt = part_z + sqrt( (D/2 + clear + tipr)^2 - lip_cy^2 )

(valid because the arc's closest normal, ~23 deg here, lies inside the +/-45 deg
the tip radius spans). `cav_hw` still cancels out of lip_zt and out of the
seated clearance, so a wider cradle is still free.

THE CRADLE IS ROUNDER THAN THE PART, which is the opposite of the rule for a
rounded rectangle and for the same reason. A square-ish cavity corner clears a
rounded part everywhere; a cradle arc LARGER than the cylinder touches it at one
point at the bottom and cannot jam, while a cradle smaller than the cylinder
would catch it on two points up the sides and hold it proud. For a round part,
bigger is the safe direction.

THE RELIEF SLOT IS CONCENTRIC WITH THE BORE, so the arm is a constant-thickness
curved spring (the pen clip's lesson: a straight slot beside a round bore makes
the arm a wedge that thins to 1.5 extrusions right where the part pushes). The
wrap is limited to -80 deg rather than the -110 the flat-walled bands use,
because here the slot wraps around the BORE CENTRE rather than a corner that is
offset to one side - at -90 the two slots would meet on the centreline and cut
the band in half. run() measures the column between them.

INSERTION FORCE IS BUDGETED, NOT LEFT TO FALL OUT (2026-10-26). These arms wrap
a long way but they are short in the straight run, so they are stiff: at
lip_over 0.60 the pill holder would have wanted 57 N to press the bottle in and
run at 133% of the stress limit. lip_over is therefore set from the push force
first and checked against the stress limit second. Both parts land near 25 N,
which is a firm two-finger press, with 100-200x the part's weight in pull-out.

PRINT STANDING ON AN END FACE, part axis vertical. Each band is a prism along
that axis, so every face is a vertical wall - no overhangs - and the arms flex
WITHIN the layer plane. Legs sit flush with the bed face so nothing starts
partway up the print. Both need a plate wider than the stock 4x12.

Fusion script entry point: run(_context).
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1

TARGET_FOLDER = 'Mod Grid'

# Which holder this run builds. The bootstrap sets it before calling run().
PART = 'pill'

PROFILES = {
    'pill': dict(
        # 2026-10-27: 17.00 was wrong. The printed 17x40 holder would not grip the
        # bottle, and the bottle DID clip into and hold in the 15.10 Olight band -
        # which brackets it, because that band's printed bore is 15.96 and its
        # printed throat is 14.26, so the bottle has to be between them. This
        # profile is therefore set to the Olight band's section EXACTLY (part_d
        # 15.10, lip_clear 0.50, lip_over 0.35), because that cross-section is
        # physically confirmed to hold this bottle - it is not another estimate.
        # Only the length and the band spacing differ, 40 mm and 3 cells.
        # Doc name no longer carries the size: it changed once and will change
        # again if the bottle is ever put across a caliper, and a size in the name
        # orphans a document every time.
        cav_clear='1.00 mm',
        grip_d='part_d',
        doc='MOD-GRID Pill Bottle Holder',
        label='pill bottle',
        part_d='15.10 mm',
        part_len='40.0 mm',
        d_note='NOT measured directly - inferred from the test fit: the bottle '
               'clips into and is held by the 15.10 band, whose printed bore is '
               '15.96 and printed throat 14.26, so 14.26 < d <= 15.96.',
        # 0.81, not 0.50, and the SECTION IS UNCHANGED. lip_z0's derivation was
        # corrected on 2026-10-28 to measure lip_clear from the tip radius rather
        # than from the 45 deg line, and 0.8069 is what this band was really
        # standing off the bottle all along. Holding that number keeps the lip
        # within 0.005 mm of where it is on the printed part that DOES grip this
        # bottle - which is the only evidence this profile has, so it does not get
        # moved on the strength of a formula fix.
        lip_clear='0.81 mm',
        lip_over='0.35 mm',
        band_cells='3',
        band_a_len='14.0 mm',
        band_b_len='14.0 mm',
        kinds=('snap', 'snap'),
        weight_g=30.0,
        blurb='MOD-GRID pill bottle holder, two bands',
    ),
    'olight': dict(
        # 2026-10-27, REBUILT AROUND HOW THE LIGHT ACTUALLY WORKS. The i Mini 2
        # is two pieces held together by a magnet: a CAP carrying the keyring
        # and the USB plug, and the light BODY, which pulls off the cap and
        # switches on as it separates. Rob wants the base left mounted and the
        # light pulled out of it.
        #
        # That also explains why the first version would not clip in. The light
        # measures 15.10 and the band's printed throat is 14.26, so the snap is
        # correctly sized - but pressing the ASSEMBLED light into a band takes
        # 26 N and the magnet holding the two halves together is nowhere near
        # that, so it comes apart in your hand instead of going in. The mount
        # was not too big; it was asking for more force than the light can pass
        # through its own magnetic joint.
        #
        # So: Band A SNAPS onto the cap (pressed in on its own, no magnet in the
        # load path), and Band B is a PLAIN OPEN CRADLE under the body with no
        # capture lip at all, whose walls stop BELOW the body's equator. The
        # body therefore lifts straight up out of it with almost no force,
        # peeling off the magnet as it goes, and the cap stays snapped down.
        #
        # Why not a collar on the cap's shoulder, which is the obvious answer to
        # an axial pull: when the light is assembled the BODY is sitting on that
        # shoulder, so there is nothing there to grab. Making the removal motion
        # RADIAL instead removes the axial load from the problem entirely.
        # 2026-10-28 rev E. 0.40 left the printed bore 15.36 on a 15.10 cap -
        # 0.13/side of slop, and Rob wants these TIGHT (the prybar, the pen and
        # the pill holder are all "super tight" and all of them grip by a real
        # interference). 0.00 models the bore at 15.10, which PRINTS 14.96:
        # 0.07/side of pinch, so the arms close on the cap and there is no
        # rattle anywhere in the bore.
        cav_clear='0.14 mm',
        cradle_clear='0.40 mm',
        doc='MOD-GRID Olight iMini 2 Holder',
        label='Olight i Mini 2',
        # 2026-10-28, MEASURED by Rob, and this is the number three
        # revisions were missing: THE LIGHT IS NOT ONE DIAMETER. The
        # keyring end (the cap) is 15.10; the body is 13.25. part_d is
        # therefore the BODY and grip_d is the CAP, and the 0.93 mm
        # radial step between them is a ready-made axial stop.
        part_d='13.25 mm',
        grip_d='15.10 mm',
        # MEASURED by Rob 2026-10-28: 18.1 mm from the keyring end to the
        # step. Was an assumed 15.0. Band A's 12 mm now lands entirely on the cap.
        cap_len='18.1 mm',
        part_len='55.0 mm',
        d_note='BODY 13.25 and CAP 15.10, both MEASURED by Rob 2026-10-28. '
               'The earlier \'15.10\' was the cap only; assuming the body matched '
               'it left the cradle band floating 0.93 mm clear of the body, so '
               'that band touched nothing at all for three revisions.',
        # 2026-10-28, STILL TOO LOOSE after cav_clear 1.00 -> 0.40 and lip_clear
        # 0.50 -> 0.30. The bore was never the problem: at 0.13/side printed it
        # is as tight as the proven Zippo band. The play was VERTICAL - the cap
        # could rise 1.52 mm before the lip bit - and the cause was lip_z0's
        # derivation, not its value (see the lip_z0 note). With the lip placed
        # off the tip radius, 0.25 is a real 0.25: free lift 1.52 -> 0.54.
        # 0.25 is also the balanced value - run()'s sweep shows the lip and the
        # cradle both run out at the same +0.26 of diameter error, so neither
        # one is wasted on the other. Below it the lip binds first, which is the
        # failure that must not happen.
        lip_clear='0.25 mm',
        # 2026-10-28 rev E, AND THIS IS WHY IT NEVER HELD. 0.35 is SMALLER
        # THAN ONE EXTRUSION WIDTH, and smaller than lip_tipr (0.40) - so the
        # two 45 deg faces never existed and the whole lip was a 0.35 x 0.72
        # bump the slicer deleted. Rob measured the printed band's opening at
        # 15.34 against a bore of 15.36: the throat WAS the bore, through all
        # five prints. 0.80 is two extrusion widths, which is the floor for a
        # feature that has to survive slicing.
        lip_over='0.80 mm',
        # 2026-11-16 rev F. BOTH ENDS NOW CLAMP. Rob carries the plate in a
        # trouser pocket and the body was not held: Band B was an OPEN CRADLE
        # with no capture lip and walls stopping below the body's equator, so it
        # had, by design, ZERO radial retention. Jostling peeled the body off
        # the magnet and swung it out of the channel - and because the light
        # switches on as it separates, that also meant it could come on in his
        # pocket.
        #
        # Band B is therefore a real snap band now, bored for the BODY (13.25)
        # through its own grip_d_b - NOT for the cap, which is the rev D defect.
        # The step stop survives untouched: Band B's bore is cut for the body,
        # so the 15.10 cap still cannot enter it and the light's own shoulder
        # still lands on that bed face.
        #
        # What this gives up is the rev B/C removal motion. The body used to
        # lift straight out with nothing but the magnet to beat; now it has to
        # come out past a lip. That is the trade Rob asked for, and Band B's
        # arms are deliberately the SOFT ones - see arm_root_b - because the
        # body comes out every time the light is used while the cap is pressed
        # in once.
        grip_b_d='part_d',
        cav_clear_b='0.14 mm',
        # 1.60 FLAT, 4 extrusions, where Band A is 2.40 -> 1.60 tapered. Not a
        # taper, because on this band the problem is the opposite one: the body
        # is the smaller diameter, so the arm wrapping it is SHORTER than Band
        # A's, and stress goes as 1/L^2 while the reach cannot come down (0.80
        # is the printability floor). The only levers left are thickness and
        # wrap, so both go to their limits. 1.60 is also exactly the root web
        # floor, which run() checks - do not go below it.
        arm_root_b='1.60 mm',
        arm_tip_b='1.60 mm',
        # -80, the same as Band A, and the first attempt at -86 was WRONG in
        # the interesting direction. A smaller bore puts the two slot roots
        # CLOSER to the centreline for the same angle, not further - the column
        # is 2*r_mid*cos(theta) - relief_w and r_mid shrinks with the bore - so
        # Band B can wrap LESS deeply than Band A, not more. At -86 the two
        # slots passed 0.041 mm apart and the measured root web read
        # 0.74/0.82/0.04 against floors of 1.5/1.2/1.2: the arm was hanging off
        # a razor, which is the one failure that has actually broken parts here.
        # The arithmetic limit at this bore is -82.2; -80 keeps the margin the
        # proven bands run.
        relief_a0_b='-80 deg',
        lip_over_b='0.80 mm',
        lip_clear_b='0.25 mm',
        band_cells='2',
        band_a_len='12.0 mm',
        # 14.0, down from the cradle's 24.0. Force scales with the band's
        # length and the body end is now the daily-use interface, so the extra
        # 10 mm would have cost ~70% more press force to hold a 19.5 g light
        # that already has 30x its weight of retention. The grip IS the support,
        # so the length the cradle needed to stop the body drooping is no longer
        # doing a job.
        band_b_len='14.0 mm',
        kinds=('snap', 'snap'),
        weight_g=19.5,
        blurb='MOD-GRID Olight i Mini 2 holder: snap band on the magnetic cap, '
              'second snap band on the body so both ends are clamped',
    ),
}


def param_defs(pr):
    return [
        # ---- the part ----
        ('part_d',           pr['part_d'],   'mm', 'Cylinder diameter. ' + pr['d_note']),
        ('part_len',         pr['part_len'], 'mm', 'Cylinder length - sets where the reference body ends and how far apart the bands can sit.'),
        ('cap_len',          pr.get('cap_len', 'part_len'), 'mm', 'Length of the GRIP section (the cap) along the axis, measured from the part\'s end to the step. Only a stepped part has one; for a plain cylinder it is the whole length. **It does not shape the holder at all** - the bands are where the grid puts them - it only decides how much of Band A lands on the cap, which run() checks and reports. It is the one number on this light still not measured, so it is set to the SHORT end of the 15-20 estimate: too short only under-reports the grip, while too long would over-report it.'),
        # ---- cradle ----
        ('base_t',           '6.00 mm',   'mm', 'Base under the part. It sets how far the slot root sits above the z=0 face; run() checks it.'),
        ('cav_clear',        pr['cav_clear'], 'mm', 'Clearance on the cradle DIAMETER (total). On a ROUND part this is close to free, which is not true of the flat-walled bands: a cylinder nests at the bottom of a larger cylindrical cradle and self-centres there, so extra clearance buys tolerance without buying rattle. It is also provably free at the lip - cav_hw cancels out of lip_zt and out of K, so the splay, the push force, the stress and the seated lip clearance are all identical at any value; only the band gets wider. Set from how well the diameter is known. 1.00 (0.86 as printed) where it is not, which tolerates the diameter being 0.86 over nominal - the number that runs out first. **The Olight runs 0.40 instead** (0.26 printed, 0.13 per side): its 15.10 is measured, it came back a little loose, and Rob asked for the band 1 mm tighter. 0.40 is as far as that can go - the FULL 1 mm would make the bore 15.10 modelled and **14.96 as printed, 0.14 UNDER the cap, so it would not seat at all.** 0.13 per side is the same printed tightness the Zippo band runs at and that one is proven.'),
        ('grip_d',           pr['grip_d'], 'mm', 'The diameter the SNAP band grips. On a one-piece part it is just part_d. On the Olight it is the CAP, 15.10, while part_d is the BODY, 13.25 - **and getting that wrong is what made three revisions feel identical.** Every lip number derives from this one, not from part_d.'),
        ('cav_r',            'grip_d / 2 + cav_clear / 2', 'mm', 'Cradle radius of the SNAP band. LARGER than the part on purpose. For a rounded rectangle the rule is the other way round - a cavity corner rounder than the part lands on its corners and holds it off the floor - but a cradle arc larger than a cylinder touches at ONE point at the bottom and cannot jam. Also the arc the relief slot follows.'),
        ('cav_hw',           'cav_r',     'mm', 'Half width of the straight walls above the cradle. Equal to cav_r, because the walls are tangent to the bore at its equator.'),
        ('bore_z',           'base_t + cav_r', 'mm', 'Height of the cradle centre'),
        ('part_z',           'base_t + grip_d / 2', 'mm', 'Height of the part axis when seated. Set by the SNAP band, because that is the one that positions the part; any cradle band has to be sunk to match it. It sits cav_clear/2 BELOW bore_z, because a smaller cylinder in a larger cradle rests at the bottom.'),
        # ---- arms ----
        ('arm_root',         '2.40 mm',   'mm', 'Arm thickness AT THE ROOT = 6 extrusions at 0.4. Tapered, because the bending moment is largest at the root and nearly zero at the lip.'),
        ('arm_tip',          '1.60 mm',   'mm', 'Arm thickness at the lip = 4 extrusions. Never below 4: 1.2 mm is 2.86 extrusions and the slicer lays a gap-fill bond line down the middle of the flexure.'),
        ('arm_blend',        '4.00 mm',   'mm', 'Height above the bore centre over which arm_root blends down to arm_tip.'),
        ('relief_w',         '1.20 mm',   'mm', 'Relief slot width behind the arm'),
        ('relief_a0',        '-80 deg',   'deg','Relief slot root angle about the BORE CENTRE. The flat-walled bands run -110, but their slot wraps a corner that is offset far to one side. Here it wraps the axis, so at -90 the two slots meet on the centreline and cut the band in two. -80 leaves a column run() measures.'),
        ('rail_t',           '3.00 mm',   'mm', 'Outer rail beyond the relief slot'),
        # ---- capture lip ----
        ('lip_clear',        pr['lip_clear'], 'mm', 'Gap between the lip\'s underside and the part when seated. For a cylinder this comes out EXACTLY lip_clear whatever the diameter, so what it really buys is tolerance to the diameter being wrong: a part dia_err bigger than nominal eats 0.854 * dia_err of it. Sized from how well the diameter is known.'),
        ('lip_over',         pr['lip_over'], 'mm', 'How far each lip reaches inboard of the part\'s widest point - and therefore the splay each arm takes. This IS the deflection, so it sets both the push force and the bending stress. Budgeted against ~25 N of push first and the 15 MPa limit second.'),
        ('lip_tipr',         '0.40 mm',   'mm', 'Radius on the lip tip = ONE NOZZLE WIDTH. A knife edge will not print, and a flat land would park the part for its full width; a radius parks it for ~0.23 mm and presents a 45 deg cam immediately below.'),
        ('lip_tip_y',        'grip_d / 2 - lip_over', 'mm', 'Innermost point of the lip'),
        ('lip_apex_y',       'lip_tip_y - 0.4142135624 * lip_tipr', 'mm', 'Virtual apex where the two 45 deg faces would meet if the tip were not rounded'),
        ('lip_cy',           'lip_apex_y + 1.4142135624 * lip_tipr', 'mm', 'Centre of the lip\'s tip radius. This is the point the seated part is actually closest to, so it - not the 45 deg face - is what lip_clear has to be measured from.'),
        ('lip_proj',         'cav_hw - lip_apex_y', 'mm', 'How far the apex stands proud of the wall. At 45 deg this is also the RISE of each face.'),
        ('lip_z0',           'part_z + sqrt(((grip_d / 2 + lip_clear + lip_tipr) / 1 mm) ^ 2 - (lip_cy / 1 mm) ^ 2) * 1 mm - lip_proj', 'mm', 'Foot of the capture ramp, placed so the TIP RADIUS stands lip_clear off the seated part. '
         '**2026-10-28: this replaces a formula that placed the 45 deg underside LINE lip_clear off the part, and that was the whole of the Olight\'s remaining looseness.** '
         'The line y + z = cav_hw + lip_z0 touches a cylinder at its 45 deg point, z = part_z + 0.707*d/2, but the lip is only lip_proj tall (0.72 mm here) and sits well BELOW that - so the part never reaches the face the clearance was derived on, and the real closest approach is at the tip radius, which stood 0.67 mm off a part the parameter said was 0.30 away. '
         'Free lift goes as the SQUARE ROOT of that error, so 2.2x the clearance was 2.8x the lift: 1.52 mm of vertical play on a 12 mm band. '
         'Now solved directly: put the tip-radius centre lip_cy at distance grip_d/2 + lip_clear + lip_tipr from the seated axis and lip_clear means what it says.'),
        ('lip_zt',           'lip_z0 + lip_proj', 'mm', 'Height of the lip tip = where the load is applied to the arm'),
        ('land_h',           '1.00 mm',   'mm', 'Band height above the lip'),
        # ---- band ----
        ('band_a_len',       pr['band_a_len'], 'mm', 'Band A width along the part = its height when printed. Grip scales with it and peak stress does not. On the Olight it is cut to 12 so the whole band lands on the 15-20 mm cap and never straddles the step onto the body.'),
        ('band_b_len',       pr['band_b_len'], 'mm', 'Band B width along the part'),
        ('band_len',         'band_a_len', 'mm', 'Kept for the reference body\'s placement'),
        # ---- the open cradle band (no capture lip), used under the Olight body ----
        ('cradle_clear',     pr.get('cradle_clear', pr['cav_clear']), 'mm', 'Clearance on the CRADLE band\'s channel. Separate from cav_clear since 2026-10-28: the snap band\'s bore was closed onto the cap to kill the slop, and that dragged the cradle channel down with it to 0.00 - which PRINTS 0.14 under the body, so the body could not nest and sat 0.39 mm high on the channel mouth, tilting the light between the two bands. A cradle has no arms and must never grip.'),
        ('cradle_r',         'part_d / 2 + cradle_clear / 2', 'mm', 'Cradle radius of a CRADLE band, off part_d rather than grip_d.'),
        ('cradle_z',         'part_z + cradle_r - part_d / 2', 'mm', 'Cradle centre, sunk so the part sits on the SAME AXIS as it does in the snap band. Get this wrong and the two bands hold the part at different heights and it rocks.'),
        ('cradle_drop',      '1.00 mm',   'mm', 'How far the cradle band\'s top face stops BELOW its own centre. It must exceed cav_clear/2, or the walls rise past the part\'s widest point and the part is trapped in a rigid band with no arms to let it out. run() checks it. It also avoids ending the wall on a tangent knife edge.'),
        ('cradle_h',         'cradle_z - cradle_drop', 'mm', 'Cradle band overall height'),
        # ---- BAND B's OWN SECTION (2026-11-16) ----
        # Band B used to be an open cradle, so it needed no lip numbers at all.
        # Now that it SNAPS onto the body it needs a full set, and it cannot
        # share Band A's: Band A grips the CAP (grip_d 15.10) and Band B grips
        # the BODY (13.25). Boring Band B for grip_d is exactly the rev D defect
        # - a band sized for a diameter the part does not have at that station.
        # Everything below defaults to Band A's value, so a one-piece part
        # (the pill bottle) builds bit-identically to before.
        ('grip_d_b',         pr.get('grip_b_d', 'grip_d'), 'mm', 'The diameter BAND B grips. On a one-piece part it is just grip_d. On the Olight it is the BODY, 13.25, against Band A\'s 15.10 cap.'),
        ('cav_clear_b',      pr.get('cav_clear_b', 'cav_clear'), 'mm', 'Clearance on Band B\'s bore diameter (total). Separate from cav_clear because the two bands sit on different sections of the part, each measured to its own confidence.'),
        ('cav_r_b',          'grip_d_b / 2 + cav_clear_b / 2', 'mm', 'Band B bore radius.'),
        ('cav_hw_b',         'cav_r_b', 'mm', 'Band B wall half width.'),
        ('bore_z_b',         'part_z + cav_r_b - grip_d_b / 2', 'mm', 'Band B bore centre, solved so the part sits on the SAME AXIS as it does in Band A. The part rests at the bottom of a larger bore, so a band gripping a SMALLER section needs its bore centre higher - exactly the correction cradle_z makes. Get it wrong and the light rocks between the two bands. run() asserts it.'),
        ('arm_root_b',       pr.get('arm_root_b', 'arm_root'), 'mm', 'Band B arm thickness at the root. Its own parameter because Band B is the DAILY-USE flexure - the body comes out every time the light is used, while the cap is pressed in once - so its force budget is a different problem from Band A\'s.'),
        ('arm_tip_b',        pr.get('arm_tip_b', 'arm_tip'), 'mm', 'Band B arm thickness at the lip. Never below 1.60 = 4 extrusions.'),
        ('arm_blend_b',      pr.get('arm_blend_b', 'arm_blend'), 'mm', 'Band B taper blend height.'),
        ('relief_a0_b',      pr.get('relief_a0_b', 'relief_a0'), 'deg', 'Band B slot wrap. It can go deeper than Band A\'s because its bore is smaller, so the two slot roots are further from meeting on the centreline - and arm LENGTH is the only lever that cuts stress without cutting the reach. run() measures the column.'),
        ('lip_clear_b',      pr.get('lip_clear_b', 'lip_clear'), 'mm', 'Band B seated lip clearance.'),
        ('lip_over_b',       pr.get('lip_over_b', 'lip_over'), 'mm', 'Band B lip reach. Same floor as everywhere: > lip_tipr and >= 2 extrusion widths, or the feature does not print.'),
        ('lip_tip_y_b',      'grip_d_b / 2 - lip_over_b', 'mm', 'Band B innermost point of the lip'),
        ('lip_apex_y_b',     'lip_tip_y_b - 0.4142135624 * lip_tipr', 'mm', 'Band B virtual apex'),
        ('lip_cy_b',         'lip_apex_y_b + 1.4142135624 * lip_tipr', 'mm', 'Band B tip-radius centre - the point the seated part is actually closest to'),
        ('lip_proj_b',       'cav_hw_b - lip_apex_y_b', 'mm', 'Band B lip projection = the rise of each 45 deg face'),
        ('lip_z0_b',         'part_z + sqrt(((grip_d_b / 2 + lip_clear_b + lip_tipr) / 1 mm) ^ 2 - (lip_cy_b / 1 mm) ^ 2) * 1 mm - lip_proj_b', 'mm', 'Band B ramp foot, solved off the TIP RADIUS exactly as lip_z0 is - see that parameter for why the 45 deg line is the wrong thing to measure from.'),
        ('lip_zt_b',         'lip_z0_b + lip_proj_b', 'mm', 'Band B lip tip height = where the load is applied'),
        ('band_hw_b',        'cav_hw_b + arm_root_b + relief_w + rail_t', 'mm', 'Band B half width. It no longer matches Band A\'s, because the two bores differ.'),
        ('band_h_b',         'lip_z0_b + 2 * lip_proj_b + land_h', 'mm', 'Band B overall height'),
        ('band_hw',          'cav_hw + arm_root + relief_w + rail_t', 'mm', 'Band half width'),
        ('band_h',           'lip_z0 + 2 * lip_proj + land_h', 'mm', 'Band overall height'),
        ('band_a_x',         '0 mm',      'mm', 'Band A bed face'),
        ('band_cells',       pr['band_cells'], '', 'Grid cells between the two bands. Set so both bands land on the part with a margin at each end.'),
        ('grid_pitch',       '8 mm',      'mm', 'MOD-GRID pitch'),
        ('band_b_x',         'band_a_x + band_cells * grid_pitch', 'mm', 'Band B bed face'),
        ('body_corner_r',    '1.50 mm',   'mm', 'Rounded outer corners'),
        ('first_layer_cham', '0.50 mm',   'mm', 'Elephant-foot chamfer on the bed face'),
        # ---- barbed snap legs, measured off MOD-GRID Olfa holder v4 ----
        ('leg_pair_y',       '8.0 mm',    'mm', 'Leg pairs at +/- this; 16 mm apart = 2 cells. Not 12 like the Zippo: these bands are only ~30 mm wide and the shank would run within 0.1 mm of the outer face.'),
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


def add_params(design, pr):
    ups = design.userParameters
    out = {}
    for name, expr, units, comment in param_defs(pr):
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


def bore_cavity(sk, x, r, cz, lip_y, apex_y, lz0, lzt, tipr, top_z):
    """Cradle cross-section: a SEMICIRCLE of radius r centred at (0, cz),
    tangent vertical walls above it, and a 45/45 CAPTURE LIP on each.

    Going up a wall: vertical to `lz0`, a 45 deg face rising INBOARD (the
    capture face - its normal points down and inboard, so it cams the part
    home instead of wedging it out), a `tipr` radius over the tip, a 45 deg
    lead-in rising back OUTBOARD, then vertical to the top.

    Every point is given in explicit coordinates. addByThreePoints may swap an
    arc's start and end to keep its sweep direction, so a loop closed off an
    arc's SketchPoints closes across itself on the mirrored side.
    """
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    S = lambda q: sk.modelToSketchSpace(p3(x, q[0], q[1]))
    tg = tipr / math.sqrt(2.0)          # tangent points either side of the tip
    proj = r - apex_y                   # = rise of each 45 deg face
    h = r / math.sqrt(2.0)
    # the cradle, as two quarter arcs meeting at the bottom
    for sgn in (1, -1):
        arcs.addByThreePoints(S((sgn * r, cz)), S((sgn * h, cz - h)), S((0.0, cz - r)))
        arcs.addByThreePoints(S((sgn * (apex_y + tg), lzt - tg)),
                              S((sgn * lip_y, lzt)),
                              S((sgn * (apex_y + tg), lzt + tg)))
        for a, b in (((sgn * r, cz), (sgn * r, lz0)),
                     ((sgn * r, lz0), (sgn * (apex_y + tg), lzt - tg)),
                     ((sgn * (apex_y + tg), lzt + tg), (sgn * r, lzt + proj)),
                     ((sgn * r, lzt + proj), (sgn * r, top_z))):
            lines.addByTwoPoints(S(a), S(b))
    lines.addByTwoPoints(S((-r, top_z)), S((r, top_z)))


def relief_slot(sk, x, side, cy, cz, r_in, r_out, th0, z_top, y_tip, z_blend):
    """Arc concentric with the bore, then up and out through the top face.

    The slot's OUTER edge is vertical above the equator, so the rail keeps a
    constant thickness. The INNER edge steps inboard from `r_in` to `y_tip`
    over the blend height, which is what tapers the arm: thick at the root
    where the bending moment is, thinner at the lip where it is nearly zero.
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


def bed_edges_no_relief(bed, ccy, ccz, r_in, r_out, y_vals, min_len,
                        lip_y_max, lip_lo, bore_r=None):
    """Bed-face edges minus the relief slot and the capture lip.

    Chamfering 0.5 off both sides of a 1.2 mm slot collapses it, and a 0.5
    chamfer either side of a 0.4 mm lip tip runs through itself.

    `bore_r` additionally leaves the WHOLE CAVITY MOUTH sharp - bore arc and
    both walls - for a band whose bed face is the part's axial stop. It has to
    be the whole mouth and not just the arc, for two reasons. The walls are
    TANGENT to the bore at its equator by design, so Fusion's chamfer runs
    straight on into the arc from a selected wall edge whatever the selection
    says; and dropping tangent chaining instead leaves the chain ending on that
    tangent point, which fails outright with ASM_BL_END_TOO_CMPLX. Two reasons, and both of them have already
    bitten this design: the stop is the annulus between this bore and the
    larger section butting against it, and 0.50 of chamfer eats most of a
    0.86 mm engagement (rev D left the cradle's channel sharp for exactly
    this); and that same 0.50 is cut out of the arm's ANCHORAGE, which took
    the measured root web ABOVE the slot cap from 1.60 to 1.10 against a
    1.5 floor. Elephant foot there only ADDS material to the stop, and the
    part drops in radially, so a tight mouth costs nothing.
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
        if bore_r and pts and all(abs(y) <= bore_r + 0.02 and z <= lip_lo + 0.02
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


def chamfer(root, edges, expr, tangent=True):
    """`tangent` is Fusion's isTangentChain. It is True by default and that is
    usually what you want, but it means **the edge selection is not the whole
    story**: the chamfer runs on into any edge tangent to one you picked. Here
    the cavity's walls are tangent to the bore at its equator BY DESIGN, so a
    chamfer on a wall edge propagates right round the bore arc and excluding
    that arc from the selection achieves nothing. Pass False where the
    selection has to be authoritative."""
    if not edges:
        return None
    f = root.features.chamferFeatures
    i = f.createInput2()
    i.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll(edges), vi(expr),
                                                     tangent)
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


def build_part(root, P, pr, log):
    """Reference cylinder. NOT printed - it is here so fitment is checked by
    interference against geometry instead of by arithmetic."""
    d = mmv(P, 'part_d'); L = mmv(P, 'part_len'); pz = mmv(P, 'part_z')
    gd = mmv(P, 'grip_d'); cl = mmv(P, 'cap_len')
    xa = mmv(P, 'band_a_x'); xs = mmv(P, 'band_b_x')

    if pr.get('cap_len'):
        # A STEPPED part, and the step is the whole point. The light is located
        # ALONG ITS AXIS by its own shoulder butting against Band B's bed face,
        # so the reference is built outwards from that face - cap backwards,
        # body forwards - instead of centred between the bands the way a plain
        # cylinder is.
        sk = sketch_on(root, plane_at_x(root, 'band_b_x - cap_len', 'Cap end'),
                       'Cap section')
        circ(sk, xs - cl, 0.0, pz, gd)
        part = _ex(root, finish(sk),
                   adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                   'cap_len').bodies.item(0)
        sk = sketch_on(root, plane_at_x(root, 'band_b_x', 'Step'), 'Body section')
        circ(sk, xs, 0.0, pz, d)
        _ex(root, finish(sk), adsk.fusion.FeatureOperations.JoinFeatureOperation,
            'part_len - cap_len', parts=[part])
        part.name = 'Reference - %s' % pr['label']
        grip = max(0.0, min(xa + mmv(P, 'band_a_len'), xs) - max(xa, xs - cl))
        log.append('Reference part: STEPPED - cap %.2f dia x %.1f long at '
                   'x %.1f..%.1f, body %.2f dia x %.1f long at x %.1f..%.1f, both '
                   'on axis z %.2f. The %.2f mm radial step at x %.1f is the axial '
                   'stop.' % (gd, cl, xs - cl, xs, d, L - cl, xs, xs + L - cl, pz,
                              (gd - d) / 2.0, xs))
        log.append('  Band A grips %.2f of its %.2f mm on the cap %s'
                   % (grip, mmv(P, 'band_a_len'),
                      'OK' if grip >= mmv(P, 'band_a_len') - 1.01 else
                      '** cap_len is short - the rest of Band A grips the BODY, '
                      'which is smaller, so that length does nothing. Measure the '
                      'cap and reset cap_len. **'))
        return part

    xb = xs + mmv(P, 'band_b_len')
    x0 = (xa + xb) / 2.0 - L / 2.0
    pl = plane_at_x(root, '(band_a_x + band_b_x + band_b_len - part_len) / 2',
                    'Part end')
    sk = sketch_on(root, pl, 'Part section')
    circ(sk, x0, 0.0, pz, d)
    part = _ex(root, finish(sk),
               adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
               'part_len').bodies.item(0)
    part.name = 'Reference - %s' % pr['label']
    log.append('Reference part: %.2f dia x %.1f long cylinder, axis at z %.2f, '
               'x %.1f..%.1f  (%s)' % (d, L, pz, x0, x0 + L, pr['d_note'].split('.')[0]))
    return part


def build_band(root, P, log, x0, name, lkey, sfx='', stop_face=False):
    """One snap band. `sfx` selects which section it grips: '' is Band A's set
    (grip_d), '_b' is Band B's (grip_d_b). On a stepped part those are different
    diameters and sharing one set is the rev D defect."""
    pn = lambda nm: nm + sfx
    hw = mmv(P, pn('band_hw')); bh = mmv(P, pn('band_h')); bl = mmv(P, lkey)
    cr = mmv(P, pn('cav_r')); cz = mmv(P, pn('bore_z'))
    ar = mmv(P, pn('arm_root')); atip = mmv(P, pn('arm_tip'))
    abl = mmv(P, pn('arm_blend'))
    rw = mmv(P, 'relief_w'); ra0 = degv(P, pn('relief_a0'))
    lty = mmv(P, pn('lip_tip_y')); lay = mmv(P, pn('lip_apex_y'))
    lz0 = mmv(P, pn('lip_z0')); lzt = mmv(P, pn('lip_zt')); ltr = mmv(P, 'lip_tipr')
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

    sk = sketch_on(root, mid, '%s cradle' % name)
    bore_cavity(sk, xm, cr, cz, lty, lay, lz0, lzt, ltr, bh + 2.0)
    cut(root, finish(sk), lkey, [body], s2=lkey)

    # The anchorage, checked BEFORE the cut: a cut that splits a body still
    # reports 0 unhealthy, and a starved web looks perfect in a render.
    # With a slot concentric to the bore the web simply IS arm_root, but the
    # two slots converge under the bore, so the COLUMN between them is the
    # number that matters here and it is the one that runs out first.
    cham = mmv(P, 'first_layer_cham')
    r_mid = cr + ar + rw / 2.0
    slot_bed = cz - r_mid * math.sin(math.radians(-ra0)) - rw / 2.0
    # 2026-11-16: this used to be the distance between the two root CAP CENTRES
    # and was therefore relief_w too big - it printed "column 1.24 mm OK" on a
    # band whose real column measured 0.050. Same class of fault as picking a
    # face by radius alone: a check that does not measure the thing it names.
    col = 2.0 * r_mid * math.cos(math.radians(-ra0)) - rw
    log.append('%s: ROOT WEB %.2f mm (= arm_root; the slot is concentric with the '
               'bore, so the arm is a constant-thickness spring) %s'
               % (name, ar, 'OK' if ar >= 1.5 else '** TOO THIN **'))
    log.append('%s: slot root sits %.2f mm above the z=0 face, %.2f after the %.2f '
               'bed chamfer %s | column between the two slots %.2f mm %s'
               % (name, slot_bed, slot_bed - cham, cham,
                  'OK' if slot_bed - cham >= 1.2 else '** TOO THIN - raise base_t **',
                  col, 'OK' if col >= 1.2 else '** the slots have nearly met - '
                  'make relief_a0 less negative **'))
    n_before = root.bRepBodies.count
    sk = sketch_on(root, mid, '%s relief' % name)
    for side in (1, -1):
        relief_slot(sk, xm, side, 0.0, cz, cr + ar, cr + ar + rw,
                    ra0, bh + 2.0, cr + atip, cz + abl)
    cut(root, finish(sk), lkey, [body], s2=lkey)
    if root.bRepBodies.count != n_before:
        log.append('%s: !! the relief cut SPLIT the body (%d -> %d bodies). The arm '
                   'is no longer attached. Everything below is meaningless.'
                   % (name, n_before, root.bRepBodies.count))

    bed = face_at_x(body, x0)
    keep, short = bed_edges_no_relief(bed, 0.0, cz, cr + ar, cr + ar + rw,
                                      (cr + ar, cr + atip, cr + ar + rw),
                                      2 * cham + 0.1, cr, lz0,
                                      bore_r=cr if stop_face else None)
    if stop_face:
        log.append('%s: bore mouth left UNCHAMFERED on purpose - this bed face is '
                   'the axial stop, so %.2f of chamfer would come off both the '
                   'engagement the shoulder lands on and the arm\'s anchorage '
                   'above the slot root. The WALLS come out of the selection '
                   'too, not just the arc: they are tangent to the bore, so the '
                   'chamfer runs on into it from a wall edge regardless.'
                   % (name, cham))
    chamfer(root, keep, 'first_layer_cham')
    add_legs(root, P, body, plane_at_x(root, key, '%s bed' % name), x0, name)
    log.append('%s: %.2f wide x %.2f tall x %.2f | cradle R%.2f centred z %.2f '
               '(part R%.2f, so the cradle is ROUNDER and touches at one point) | '
               'arm %.2f root -> %.2f tip (%.0f -> %.0f extrusions), slot wrap '
               '%.0f deg | lip 45/45, tip r%.2f at z %.2f reaching %.2f inboard, '
               'ramp foot z %.2f | chamfer %d edges, %d left sharp'
               % (name, 2 * hw, bh, bl, cr, cz, mmv(P, pn('grip_d')) / 2.0, ar,
                  atip, ar / 0.4, atip / 0.4, ra0, ltr, lzt,
                  mmv(P, pn('lip_over')), lz0, len(keep), len(short)))
    return body


def cradle_cavity(sk, x, r, cz, top_z):
    """Open channel for a CRADLE band: an arc of radius r centred (0, cz),
    closed across the top at `top_z`.

    `top_z` is deliberately BELOW cz, so the walls stop short of the part's
    widest point and the part lifts straight out. A cradle band has no relief
    slots and therefore no arms - if its walls rose past the equator the part
    would be trapped in rigid material with nothing to flex.
    """
    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    S = lambda q: sk.modelToSketchSpace(p3(x, q[0], q[1]))
    drop = cz - top_z
    yt = math.sqrt(max(r * r - drop * drop, 0.0))
    th_s = math.atan2(-drop, yt)
    for sgn in (1, -1):
        th_m = (th_s + math.radians(-90.0)) / 2.0
        arcs.addByThreePoints(S((sgn * yt, top_z)),
                              S((sgn * r * math.cos(th_m), cz + r * math.sin(th_m))),
                              S((0.0, cz - r)))
    lines.addByTwoPoints(S((-yt, top_z)), S((yt, top_z)))


def build_cradle(root, P, log, x0, name, lkey):
    """A band with NO capture lip: it only supports the part and locates it
    sideways. Used under the Olight's BODY so the light lifts straight up off
    its magnetic cap, which is the whole point of the design - see the note on
    the olight profile."""
    hw = mmv(P, 'band_hw'); bh = mmv(P, 'cradle_h'); bl = mmv(P, lkey)
    cr = mmv(P, 'cradle_r'); cz = mmv(P, 'cradle_z')
    pz = mmv(P, 'part_z'); drop = mmv(P, 'cradle_drop')
    cham = mmv(P, 'first_layer_cham')
    key = 'band_a_x' if name.endswith('A') else 'band_b_x'

    mid = plane_at_x(root, '%s + %s / 2' % (key, lkey), '%s mid' % name)
    half = '%s / 2' % lkey
    sk = sketch_on(root, mid, '%s body' % name)
    rect(sk, x0 + bl / 2.0, -hw, 0.0, x0 + bl / 2.0, hw, bh)
    body = newbody(root, finish(sk), half, half).bodies.item(0)
    body.name = name
    fillet(root, x_corner_edges(body, [(-hw, 0.0), (hw, 0.0), (-hw, bh), (hw, bh)], bl),
           'body_corner_r')

    sk = sketch_on(root, mid, '%s cradle' % name)
    cradle_cavity(sk, x0 + bl / 2.0, cr, cz, bh)
    cut(root, finish(sk), lkey, [body], s2=lkey)

    # The bed face of a cradle band is not just a bed face: on the Olight it is
    # the AXIAL STOP that the cap's shoulder butts against, and the engagement
    # is only ~0.8 mm. A 0.50 chamfer round the channel mouth would eat most of
    # it - the same trap as chamfering a hole a snap barb catches under. So the
    # channel arc is left sharp and only the outer edges are chamfered; a
    # little elephant foot at the mouth adds material to the stop rather than
    # removing it, and the part drops in radially so a tight mouth costs
    # nothing.
    def on_channel(e):
        ev = e.evaluator
        ok, t0, t1 = ev.getParameterExtents()
        ok, pt = ev.getPointAtParameter((t0 + t1) / 2.0)
        return abs(math.hypot(pt.y / MM, pt.z / MM - cz) - cr) < 0.05

    bed = face_at_x(body, x0)
    keep = [e for e in bed.edges
            if e.length / MM >= 2 * cham + 0.1 and not on_channel(e)]
    chamfer(root, keep, 'first_layer_cham')
    # ONE leg row, however long the band is, and it must be the row at the bed
    # face. A second row further along would be a grid-pitch multiple away and
    # would land in real holes - but the band prints standing on this face, so
    # a second row 16 mm along begins 16 mm UP the print with nothing beneath
    # it: an island in mid-air, which is the exact failure the pen clip had.
    # One pair is enough here anyway - the band lies flat on the plate, the
    # part lifts straight out so nothing pries it, and the only real load is
    # the part's weight in shear on the legs.
    add_legs(root, P, body, plane_at_x(root, key, '%s bed' % name), x0, name)
    free = pz - bh
    log.append('%s: OPEN CRADLE, no capture lip. %.2f wide x %.2f tall x %.2f | '
               'channel R%.2f centred z %.2f, top face z %.2f = %.2f below the '
               'part axis, so the part lifts STRAIGHT OUT %s | chamfer %d edges'
               % (name, 2 * hw, bh, bl, cr, cz, bh, free,
                  'OK' if free > 0.05 else '** the walls rise past the part\'s '
                  'widest point and it is TRAPPED - raise cradle_drop **',
                  len(keep)))
    log.append('%s: cradle centre sits %.2f above the part axis, which is '
               'cradle_r - part_d/2 - exactly what puts the part on the SAME AXIS '
               'as the snap band holds it %s'
               % (name, cz - pz, 'OK' if abs((cz - pz) - (cr - mmv(P, 'part_d') / 2.0))
                  < 0.01 else '** the two bands disagree and the part will rock **'))
    return body


def verify_cradle(body, P, log, x0, lkey):
    cr = mmv(P, 'cradle_r'); cz = mmv(P, 'cradle_z'); pz = mmv(P, 'part_z')
    d = mmv(P, 'part_d'); bh = mmv(P, 'cradle_h')
    xm = x0 + mmv(P, lkey) / 2.0
    # Probe INSIDE the channel. The part's widest point is above this band's top
    # face by design, so a probe at the part axis finds no material at all and
    # walks to its limit - which is what it did the first time this ran.
    rows = []
    for frac in (0.15, 0.45, 0.75, 0.98):
        z = bh - (bh - (cz - cr)) * (1.0 - frac)
        wall = probe_in(body, xm, z)
        dz = pz - z
        ypart = math.sqrt(max((d / 2.0) ** 2 - dz * dz, 0.0)) if abs(dz) < d / 2.0 else 0.0
        rows.append((z, wall, wall - ypart))
    log.append('    channel vs the part, per side: %s'
               % ', '.join('z%.2f wall %.2f gap %+.2f' % r for r in rows))
    worst = min(r[2] for r in rows)
    log.append('    tightest %+.3f mm per side %s. There is NO capture lip on this '
               'band by design - the part is held down by its own magnet and the '
               'band only stops it rolling.'
               % (worst, 'OK' if worst > 0.05 else '** the cradle is gripping **'))
    log.append('    the part\'s widest point sits %.2f mm ABOVE the cradle\'s top '
               'face %s' % (pz - bh, 'OK - it lifts straight out' if pz - bh > 0.05
                            else '** TRAPPED **'))

    # THE AXIAL STOP. A band grips radially and its arms are unloaded when
    # seated, so there is essentially nothing holding a smooth cylinder against
    # sliding along its own axis - which is exactly what Rob reported, three
    # revisions running, while every radial number was being tightened. On a
    # STEPPED part the fix needs no new geometry at all: bore this band for the
    # BODY, put its bed face at the step, and the part's own shoulder lands on
    # it. The engagement below is what carries the part's weight.
    gd = mmv(P, 'grip_d')
    if gd > d + 0.01:
        o = cz - pz
        eng, hi = 1e9, 0.0
        for i in range(361):
            a = math.radians(-180.0 + i * 0.5)
            t = o * math.sin(a) + math.sqrt(max(o * o * math.sin(a) ** 2
                                                - o * o + cr * cr, 0.0))
            if pz + t * math.sin(a) > bh:
                continue
            eng = min(eng, gd / 2.0 - t)
            hi = max(hi, gd / 2.0 - t)
        log.append('    AXIAL STOP: the %.2f cap cannot enter a %.2f channel, so '
                   'its shoulder lands on this band\'s bed face with %.2f-%.2f mm '
                   'of radial engagement %s'
                   % (gd, 2 * cr, eng, hi,
                      'OK - that is the part\'s whole weight, carried on a face '
                      'rather than on friction' if eng > 0.15 else
                      '** barely engaged - the part will still slide **'))
        log.append('    -> mount this band at the LOW end: the part hangs with '
                   'its shoulder resting on it.')
    lpy = mmv(P, 'leg_pair_y'); lxm = x0 + mmv(P, 'leg_hole_len') / 2.0
    for z, lab, want in ((-1.5, 'shank', 2 * mmv(P, 'leg_shank_hw')),
                         (mmv(P, 'barb_z'), 'barb ', 2 * mmv(P, 'barb_hw'))):
        v = lpy + mmv(P, 'leg_inner_hw') + 0.03
        while v < lpy + 9.0 and body.pointContainment(p3(lxm, v, z)) == 0:
            v += 0.005
        log.append('    leg %s span %.3f (want %.2f)' % (lab, 2 * (v - lpy), want))
    v = lxm
    yp = lpy + mmv(P, 'leg_inner_hw') + 0.3
    while v > lxm - 10.0 and body.pointContainment(p3(v, yp, mmv(P, 'barb_z'))) == 0:
        v -= 0.005
    log.append('    legs start at x=%.3f, bed is x=%.3f -> %s'
               % (v, x0, 'FLUSH' if abs(v - x0) < 0.02 else 'FLOATING'))


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


def temp_cyl(tbm, d, pz, x0, x1):
    return tbm.createCylinderOrCone(p3(x0, 0.0, pz), d * MM / 2.0,
                                    p3(x1, 0.0, pz), d * MM / 2.0)


def shift_matrix(dz):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(0.0, 0.0, dz * MM)
    return m


SIG_LIMIT = 15.0
PRINT_BIAS = 0.07   # cavities print ~0.07/wall under, so the lip reaches
                    # FURTHER inboard than modelled and the arm flexes more
MU_SEAT = 0.30      # ABS on dry plastic/anodised aluminium. arctan -> 16.7 deg.
PUSH_BUDGET = 35.0  # N, total over both arms. More than this is not a press,
                    # it is a struggle - see the 2026-10-26 note in CLAUDE.md.


def arm_profile(cav_r, arm_root, arm_tip, arm_blend, th0_deg, ccz, load_z, n=300):
    """Sample the arm's neutral axis from the slot root up to the lip: the
    wrap around the bore at constant arm_root, then the straight run above the
    equator blending to arm_tip."""
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
    """Stiffness and peak bending stress for one tapered curved arm.

    A horizontal force at the lip puts a moment F*(load_z - z) on every
    section, so the moment follows VERTICAL distance below the lip, not
    distance along the arm. On a tapered arm the peak is wherever
    (load_z - z) / t^2 is largest, which is not automatically the root.
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
    # AS PRINTED the arm is also THICKER. It sits between the cradle and the
    # relief slot - both voids, both printing inward - so it grows by
    # 2 * PRINT_BIAS. Stiffness goes as t^3 and stress as t, so ignoring it
    # under-reports the push force by ~20%.
    Fp, sigp, wp = solve(delta + PRINT_BIAS, 2.0 * PRINT_BIAS)
    log.append('    FLEXURE (tapered curved beam): %.2f mm root (%.0f extrusions) '
               '-> %.2f tip (%.0f), band %.1f long'
               % (arm_root, arm_root / 0.4, arm_tip, arm_tip / 0.4, bl))
    log.append('      %.2f mm/arm -> %.1f N, peak %.1f MPa at z %.2f where the arm '
               'is %.2f thick' % (delta, F, sig, where[0], where[1]))
    log.append('      as printed (+%.2f deflection AND +%.2f on the arm, which sits '
               'between two voids -> %.2f mm/arm on a %.2f mm section): %.1f N/arm, '
               '%.1f MPa = %.0f%% of the %.0f MPa limit %s'
               % (PRINT_BIAS, 2.0 * PRINT_BIAS, delta + PRINT_BIAS, wp[1], Fp, sigp,
                  100.0 * sigp / SIG_LIMIT, SIG_LIMIT,
                  'OK' if sigp <= SIG_LIMIT else '** OVER - cut lip_over **'))
    return Fp, sigp


def lip_profile_fn(chw, cav_r, bt, lz0, lzt, lip_y, apex_y, tipr):
    """One arm's inner face as y = f(z): cradle arc, wall, 45 deg up-and-inboard,
    tip radius, 45 deg up-and-outboard, wall. Single valued in z, which is what
    makes seat_check() a one-dimensional problem."""
    proj = chw - apex_y
    cy = apex_y + tipr * math.sqrt(2.0)     # centre of the tip radius
    tg = tipr / math.sqrt(2.0)

    def f(z):
        if z < bt + cav_r:
            return math.sqrt(max(cav_r ** 2 - (bt + cav_r - z) ** 2, 0.0))
        if z <= lz0 or z >= lzt + proj:
            return chw
        if abs(z - lzt) <= tg:
            return cy - math.sqrt(max(tipr ** 2 - (z - lzt) ** 2, 0.0))
        return chw - (proj - abs(z - lzt))
    return f


def seat_check(log, P, sfx='', label='Band A'):
    """Will the part seat, and can the lip hold it OUT instead?

    Only the DOWNWARD component of the contact normal pulls the part home, and
    friction resists with up to mu*N, so the contact face must stay steeper
    than arctan(mu) from horizontal for the whole stroke. A round bead cannot
    manage that - its normal rotates through horizontal at the crest, which is
    what held a printed Zippo 2 mm proud. A straight 45 deg face holds 45 deg
    throughout; only the 0.4 mm tip radius can go shallow.

    Swept over the DIAMETER, not over a corner radius: on a cylinder the
    corner radius is the part radius and it cancels out of the lip placement
    exactly, so the only thing left to be wrong about is the diameter.
    """
    pn = lambda nm: nm + sfx
    d = mmv(P, pn('grip_d'))
    chw = mmv(P, pn('cav_hw')) - PRINT_BIAS
    cav_r = mmv(P, pn('cav_r'))
    # not base_t: on a band gripping a smaller section the bore centre is
    # raised so the part keeps the same axis, so the floor of the bore is
    # bore_z - cav_r and NOT the band's base thickness.
    bt = mmv(P, pn('bore_z')) - cav_r
    lz0 = mmv(P, pn('lip_z0')); lzt = mmv(P, pn('lip_zt')); tipr = mmv(P, 'lip_tipr')
    lip_y = mmv(P, pn('lip_tip_y')) - PRINT_BIAS
    apex_y = mmv(P, pn('lip_apex_y')) - PRINT_BIAS
    f = lip_profile_fn(chw, cav_r, bt, lz0, lzt, lip_y, apex_y, tipr)
    lock_deg = math.degrees(math.atan(MU_SEAT))

    def splay(h, dd, n=400, lip_only=False):
        """Worst (part surface - arm face) over the part's height, at lift h.

        `lip_only` restricts it to the capture lip. That distinction matters:
        at rest the part SITS ON the cradle, so the gap down there is zero by
        definition and a whole-part minimum just reports the contact it is
        supposed to have. What tells you whether the part seats FLAT is the
        clearance under the lip, and nothing else.
        """
        R = dd / 2.0
        # a cylinder dd across rests in the cradle, so its axis is cav_r - R
        # below the cradle centre
        az = bt + cav_r - (cav_r - R) + h
        best, bz = -9e9, 0.0
        for i in range(n + 1):
            z = az - R + 2.0 * R * i / n
            if lip_only and z < lz0:
                continue
            y = math.sqrt(max(R * R - (z - az) ** 2, 0.0))
            v = y - f(z)
            if v > best:
                best, bz = v, z
        return best, bz

    def face_deg(z):
        e = 0.004
        dy = (f(z + e) - f(z - e)) / (2 * e)
        return 90.0 if abs(dy) < 1e-9 else math.degrees(math.atan(1.0 / abs(dy)))

    log.append('SEATING of %s on the %.2f section, AS PRINTED (cavity %.2f/wall '
               'under). The contact face must stay steeper than arctan(mu=%.2f) = '
               '%.1f deg or the arms hold the part OUT. Swept over the DIAMETER, '
               'since that is the only uncertain number on a cylinder.'
               % (label, d, PRINT_BIAS, MU_SEAT, lock_deg))
    worst, bad = 0.0, False
    for err in (-0.40, -0.20, 0.0, 0.20, 0.40, 0.60):
        dd = d + err
        s0, _ = splay(0.0, dd, lip_only=True)
        cradle = (mmv(P, pn('cav_clear')) - 2.0 * PRINT_BIAS) - err
        rows, h = [], 0.0
        while h <= 8.0:
            rows.append((h,) + splay(h, dd))
            h += 0.02
        smax = max(r[1] for r in rows)
        on = next((r[0] for r in rows if r[1] > 0.0), 0.0)
        stick = [r[0] for r in rows if r[1] > 0.02 and face_deg(r[2]) < lock_deg]
        zone = (max(stick) - min(stick) + 0.02) if stick else 0.0
        worst = max(worst, zone)
        proud = s0 > 0.0
        tight = cradle < 0.0
        bad = bad or proud or tight or zone > 0.30
        log.append('   dia %5.2f (%+.2f): under the LIP %5.2f %s | in the CRADLE '
                   '%5.2f %s | free lift %.2f | peak splay %.2f | sticky zone '
                   '%.2f mm %s'
                   % (dd, err, -s0, 'OK' if not proud else '** HELD PROUD **',
                      cradle, 'OK' if not tight else '** WILL NOT GO IN **',
                      on, smax, zone,
                      'tip radius only' if zone <= 0.30 else '** SELF-LOCKING **'))
    log.append('   worst sticky zone %.2f mm %s' % (worst, 'OK' if not bad else
               '** something in this range does not seat **'))

    # Does lip_clear MEAN anything? It is supposed to be the gap between the
    # lip and the seated part, and for two prints it was not: the derivation
    # measured it off a 45 deg face the part never reached, so the parameter
    # read 0.30 while the real gap was 0.67 and the band was loose. The number
    # below is measured off the profile, so the two can never silently diverge
    # again. (It comes out ~PRINT_BIAS under lip_clear because this sweep is
    # as-printed and the modelled derivation is not.)
    # Measured RADIALLY from the seated axis, which is the direction lip_clear
    # is defined in. The sweep's "under the LIP" column above is a horizontal
    # gap, and on a steep contact the two differ by 1/cos(angle) - enough to
    # hide exactly the error this guard exists to catch.
    fm = lip_profile_fn(mmv(P, pn('cav_hw')), cav_r, bt, lz0, lzt,
                        mmv(P, pn('lip_tip_y')), mmv(P, pn('lip_apex_y')), tipr)
    az = bt + d / 2.0
    rad, z = 9e9, lz0
    while z <= lzt + (mmv(P, pn('cav_hw')) - mmv(P, pn('lip_apex_y'))):
        rad = min(rad, math.hypot(fm(z), z - az) - d / 2.0)
        z += 0.002
    want = mmv(P, pn('lip_clear'))
    log.append('   lip_clear says %.2f and the modelled profile stands %.2f off '
               'the seated part, measured radially %s'
               % (want, rad, 'OK' if abs(rad - want) < 0.03 else
                  '** lip_clear is not the gap it claims - check lip_z0 **'))
    return worst


def escape_curve(R, y_tip, F_arm, mu=MU_SEAT, n=2000):
    """Force resisting a CYLINDER being pulled out past a lip, and the travel.

    2026-10-28. The band reported "not retained at all" with a model that said
    5.4 kg. The model was `pull = 2 * F * 1.8`, where 1.8 is the wedge factor of
    a 45 deg face with friction - correct for the Zippo and the Skeletool, whose
    lip rides over a FLAT or a 2.8 mm corner, and badly wrong here.

    On a cylinder the escape ramp is not the lip's face at all. The lip tip
    radius is 0.40 and the part radius is 7.55, so the contact is governed by
    the PART, and a cylinder near its equator is a nearly vertical wall - which
    is a nearly HORIZONTAL ramp for this purpose. The slope runs from about
    18 deg at first touch DOWN to 0 at release, so the whole stroke sits at or
    under arctan(mu): the part is held by friction, not by the spring, and the
    resistance dies away exactly when the part is closest to escaping.

    Geometry. Lip tip at radius y_tip, part radius R, axis `u` below the tip:

        splay  s(u) = sqrt(R^2 - u^2) - y_tip        (u from u0 down to 0)
        ramp   ds/dh = u / sqrt(R^2 - u^2)
        travel u0 = sqrt(R^2 - y_tip^2)              seated-to-free lift

    and with a linear arm, k = F_arm / (R - y_tip),

        F(u) = 2*k*s*(ds/dh + mu) / (1 - mu*ds/dh)

    Returns (peak force N, lift at the peak, total travel). The useful identity
    that falls out: on a smooth cylinder the peak is about 0.38 * 2 * F_arm
    whatever lip_over is, so PULL-OUT IS ABOUT 0.38 x THE PRESS FORCE and no
    clearance anywhere changes it. A light press and a firm hold are mutually
    exclusive on a plain cylinder; only arm stiffness moves both together.
    """
    smax = R - y_tip
    if smax <= 0:
        return 0.0, 0.0, 0.0
    k = F_arm / smax
    u0 = math.sqrt(max(R * R - y_tip * y_tip, 0.0))
    best = (0.0, 0.0)
    for i in range(n + 1):
        u = u0 * i / n
        w = math.sqrt(max(R * R - u * u, 1e-9))
        s = w - y_tip
        if s <= 0:
            continue
        slope = u / w
        f = 2.0 * k * s * (slope + mu) / max(1.0 - mu * slope, 1e-6)
        if f > best[0]:
            best = (f, u0 - u)
    return best[0], best[1], u0


def measure_root_web(app, body, relief_w, log, label, below_z=1e9):
    """Narrowest gaps between a relief slot's root cap and any other face.

    Direction matters, so classify rather than report one number:
      ABOVE  the cap -> the arm's anchorage. Want >= 1.5 mm.
      BELOW  the cap -> material down to the bed face. Want >= 1.2 mm.
      BESIDE the cap -> the column between the two slots. Want >= 1.2 mm.

    below_z keeps this on the SLOT ROOT CAPS: any cylinder of about the right
    radius used to qualify, and a capture bead that happened to share it was
    once measured as a slot cap and reported an anchorage that did not exist.
    """
    mgr = app.measureManager
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
                continue
            p = r.positionTwo
            dz = p.z / MM - cz
            kind = 'ABOVE ' if dz > 0.15 else ('BELOW ' if dz < -0.15 else 'BESIDE')
            found.append((d, kind, p, cap))
    best = {}
    for d, kind, p, cap in found:
        if kind not in best or d < best[kind][0]:
            best[kind] = (d, 1.5 if kind == 'ABOVE ' else 1.2,
                          'y %.2f z %.2f x %.2f' % (p.y / MM, p.z / MM, p.x / MM))
    for kind in ('ABOVE ', 'BELOW ', 'BESIDE'):
        if kind not in best:
            continue
        d, want, where = best[kind]
        ok = d >= want
        log.append('    %s %s cap: %.3f mm (want >= %.1f) at %s %s'
                   % (label, kind, d, want, where,
                      'OK' if ok else '** THE ARM HANGS OFF THIS **'))
    return min(d for d, _, _, _ in found) if found else 1e9


def verify_band(app, body, P, log, x0, weight_g, lkey, sfx='', stop_face=False):
    pn = lambda nm: nm + sfx
    cr = mmv(P, pn('cav_r')); cz = mmv(P, pn('bore_z'))
    ar = mmv(P, pn('arm_root')); atip = mmv(P, pn('arm_tip'))
    abl = mmv(P, pn('arm_blend'))
    rw = mmv(P, 'relief_w'); ra0 = degv(P, pn('relief_a0'))
    lz0 = mmv(P, pn('lip_z0')); lzt = mmv(P, pn('lip_zt')); bl = mmv(P, lkey)
    d = mmv(P, pn('grip_d'))
    xm = x0 + bl / 2.0
    worst = (1e9, '')

    rows = []
    for i in range(6):
        th = ra0 + (0.0 - ra0) * i / 5.0
        a = math.radians(th); q = 0.03
        while q < 9.0:
            yy = (cr + q) * math.cos(a); zz = cz + (cr + q) * math.sin(a)
            if body.pointContainment(p3(xm, yy, zz)) != 0:
                break
            q += 0.005
        rows.append((th, q))
        if q < worst[0]:
            worst = (q, '%.0f deg round the bore' % th)
    log.append('    arm round the bore: %s'
               % ', '.join('%.0fdeg=%.2f' % r for r in rows))

    rows = []
    for i in range(5):
        zz = cz + i * (lz0 - 0.05 - cz) / 4.0
        yw = probe_in(body, xm, zz)
        q = probe_out(body, xm, yw + 0.005, zz)
        rows.append((zz, q))
        if q < worst[0]:
            worst = (q, 'wall at z=%.2f' % zz)
    log.append('    arm up the wall: %s (tapering %.2f -> %.2f by design)'
               % (', '.join('z%.2f=%.2f' % r for r in rows), ar, atip))
    log.append('    THINNEST ANYWHERE %.2f mm = %.1f perimeters (%s) %s'
               % (worst[0], worst[0] / 0.4, worst[1],
                  'OK' if worst[0] >= atip - 0.05 else '** thinner than arm_tip - '
                  'something is eating the arm **'))

    if stop_face:
        # MEASURED, not asserted. The analytic engagement is the same number
        # whether or not a chamfer has eaten it, which is exactly the kind of
        # check that passed on the Olight for three revisions. Walk DOWN from
        # the bore's lowest point at the bed face and find where material
        # actually starts.
        zb = cz - cr
        bite, zz = 0.0, zb - 0.005
        while zz > zb - 1.2:
            if body.pointContainment(p3(x0 + 0.02, 0.0, zz)) == 0:
                break
            bite = zb - zz
            zz -= 0.005
        # The annulus is against the LARGER section that butts into it - the
        # cap, mmv('grip_d') - not against this band's own diameter.
        avail = (mmv(P, 'grip_d') - (2.0 * cr - 2.0 * PRINT_BIAS)) / 2.0
        log.append('    STOP FACE at the bed: the bore mouth is chamfered by '
                   '%.3f mm -> the %.2f shoulder lands on %.3f mm of radial '
                   'engagement, of the %.3f the bore leaves it as printed %s'
                   % (bite, mmv(P, 'grip_d'), avail - bite, avail,
                      'OK - unchamfered' if bite < 0.05 else
                      '** the chamfer has eaten %.0f%% of the engagement **'
                      % (100.0 * bite / max(avail, 1e-6))))

    measure_root_web(app, body, rw, log, 'root web', below_z=cz)

    # the column between the two slots, probed on the real solid
    col = 1e9
    zz = 0.5
    while zz < cz - 0.1:
        if body.pointContainment(p3(xm, 0.0, zz)) == 0:
            v = 0.0
            while v < cr and body.pointContainment(p3(xm, v, zz)) == 0:
                v += 0.005
            col = min(col, 2 * v)
        zz += 0.05
    log.append('    column between the two relief slots %.3f mm (want >= 1.20) %s'
               % (col, 'OK' if col >= 1.2 else '** the slots have nearly met **'))

    bore = 2 * probe_in(body, xm, cz)
    gap = 2 * probe_in(body, xm, lzt)
    log.append('    bore %.3f (part %.2f, %.3f clearance - the part rests on the '
               'cradle, arms relax when seated) | narrowest across the lip tips '
               '%.3f -> the part must splay the arms %.3f total'
               % (bore, d, bore - d, gap, d - gap))

    F, sig = flexure_check(log, bl, ar, atip, abl, cr, ra0, cz, lzt,
                           mmv(P, pn('lip_over')))
    push = 2 * F
    # NOT 2*F*1.8. That wedge factor belongs to a lip riding over a flat face;
    # on a cylinder the part's own radius sets the ramp and it is far shallower.
    pull, at_lift, travel = escape_curve(d / 2.0, gap / 2.0 - PRINT_BIAS, F)
    log.append('      -> %.0f N (%.1f kg) to PRESS the part in %s, %.0f N (%.1f kg) '
               'to pull it out = %.0fx the part\'s %.0f g. Arms are UNLOADED when '
               'seated, so no creep.'
               % (push, push / 9.81,
                  'OK' if push <= PUSH_BUDGET else '** over the %.0f N budget **'
                  % PUSH_BUDGET, pull, pull / 9.81,
                  pull / (weight_g * 9.81 / 1000.0), weight_g))
    log.append('      ESCAPE RAMP: the part travels %.2f mm from seated to free, '
               'peaking at %.0f N after %.2f mm. On a cylinder the ramp runs from '
               '~%.0f deg at first touch down to 0 at release, so it is FRICTION '
               'holding the part, not the spring, and pull-out is only %.2f x the '
               'press force however the clearances are set. %s'
               % (travel, pull, at_lift,
                  math.degrees(math.atan(math.sqrt(max((d / 2.0) ** 2 -
                      (gap / 2.0 - PRINT_BIAS) ** 2, 0.0)) / max(gap / 2.0 -
                      PRINT_BIAS, 1e-6))), pull / max(push, 1e-6),
                  'OK' if travel <= 1.5 else '** %.1f mm of travel on a %.0f mm '
                  'band - this is what reads as a loose fit **' % (travel, bl)))

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


SFX_B = '_b'   # Band B's own parameter set


def run(_context: str):
    app = adsk.core.Application.get()
    log = Log()
    pr = PROFILES[PART]
    doc_name = pr['doc']

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
        if df.name == doc_name:
            existing = df
            break
    if existing is not None:
        doc = app.documents.open(existing)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.timeline.markerPosition = 0
        design.timeline.deleteAllAfterMarker()
        log.append('rebuilding "%s" (was v%s)' % (doc_name, existing.versionNumber))
    else:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        log.append('creating "%s"' % doc_name)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    try:
        design.fusionUnitsManager.distanceDisplayUnits = \
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    except Exception:
        pass
    root = design.rootComponent
    P = add_params(design, pr)

    d = mmv(P, 'part_d'); L = mmv(P, 'part_len'); bt = mmv(P, 'base_t')
    cr = mmv(P, 'cav_r'); cz = mmv(P, 'bore_z'); pz = mmv(P, 'part_z')
    lz0 = mmv(P, 'lip_z0'); lzt = mmv(P, 'lip_zt'); gd0 = mmv(P, 'grip_d')
    log.append('user parameters: %d' % len(P))
    kinds = pr.get('kinds', ('snap', 'snap'))
    gdb = mmv(P, 'grip_d_b')
    log.append('%s: %.1f long | Band A (%s) grips %.2f (grip_d), Band B (%s) takes '
               '%.2f (grip_d_b)%s | Band A bore R%.2f centred z %.2f, part axis '
               'z %.2f (it rests %.2f below the bore centre) | capture lip 45/45, '
               'tip r%.2f reaching %.2f inboard of the widest point, ramp foot '
               'z %.2f, tip z %.2f'
               % (pr['label'], L, kinds[0].upper(), gd0, kinds[1].upper(), gdb,
                  ' - SAME, one-piece part' if abs(gd0 - d) < 0.01 else
                  ' - a STEPPED part, and the %.2f mm step between them is the '
                  'axial stop' % ((gd0 - d) / 2.0),
                  cr, cz, pz, cz - pz, mmv(P, 'lip_tipr'),
                  mmv(P, 'lip_over'), lz0, lzt))
    if kinds[1] == 'snap' and abs(gdb - gd0) > 0.01:
        # The two bands sit on different diameters, so they are two different
        # flexures and the axis they hold the part on has to be solved, not
        # assumed. This is the check rev D's cradle needed and did not have.
        axis_b = mmv(P, 'bore_z_b') - (mmv(P, 'cav_r_b') - gdb / 2.0)
        log.append('Band B bore R%.2f centred z %.2f -> it holds the %.2f body on '
                   'axis z %.2f against Band A\'s z %.2f %s'
                   % (mmv(P, 'cav_r_b'), mmv(P, 'bore_z_b'), gdb, axis_b, pz,
                      'OK - SAME AXIS' if abs(axis_b - pz) < 0.01 else
                      '** THE TWO BANDS HOLD THE PART AT DIFFERENT HEIGHTS - it '
                      'will rock between them **'))
    log.append('lip_clear %.2f - on a cylinder the part radius CANCELS out of the '
               'lip placement, so this is pure tolerance to the diameter being '
               'wrong: it absorbs %.2f mm of oversize before the lip touches at '
               'seated.' % (mmv(P, 'lip_clear'), mmv(P, 'lip_clear') / 0.854))
    log.append('')
    seat_check(log, P, '', 'Band A')
    if kinds[1] == 'snap' and abs(gdb - gd0) > 0.01:
        log.append('')
        seat_check(log, P, SFX_B, 'Band B')
    log.append('')

    part = build_part(root, P, pr, log)
    xa = mmv(P, 'band_a_x'); xb = mmv(P, 'band_b_x')
    a = build_band(root, P, log, xa, 'Band A', 'band_a_len') \
        if kinds[0] == 'snap' else \
        build_cradle(root, P, log, xa, 'Band A', 'band_a_len')
    b = build_band(root, P, log, xb, 'Band B', 'band_b_len', SFX_B,
                   stop_face=bool(pr.get('cap_len'))
                   and abs(mmv(P, 'grip_d_b') - gd0) > 0.01) \
        if kinds[1] == 'snap' else \
        build_cradle(root, P, log, xb, 'Band B', 'band_b_len')
    bl = mmv(P, 'band_b_len')
    log.append('Band A is a %s %.1f long at x %.1f; Band B is a %s %.1f long at '
               'x %.1f - %.1f mm apart = %d cells at %.0f mm pitch'
               % (kinds[0].upper(), mmv(P, 'band_a_len'), xa, kinds[1].upper(),
                  bl, xb, xb - xa, int(uv(P, 'band_cells')), mmv(P, 'grid_pitch')))

    log.append('')
    for body, x0, nm, kind, lk in ((a, xa, 'Band A', kinds[0], 'band_a_len'),
                                   (b, xb, 'Band B', kinds[1], 'band_b_len')):
        bb = body.boundingBox
        log.append('%-7s X %7.3f..%7.3f  Y %8.3f..%8.3f  Z %7.3f..%7.3f  vol %.1f mm3'
                   % (nm, bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM,
                      bb.maxPoint.y / MM, bb.minPoint.z / MM, bb.maxPoint.z / MM,
                      body.volume / (MM ** 3)))
        if kind == 'snap':
            sf = '' if nm == 'Band A' else SFX_B
            verify_band(app, body, P, log, x0, pr['weight_g'], lk, sf,
                        stop_face=bool(sf) and bool(pr.get('cap_len'))
                        and abs(mmv(P, 'grip_d_b') - gd0) > 0.01)
        else:
            verify_cradle(body, P, log, x0, lk)

    tbm = adsk.fusion.TemporaryBRepManager.get()
    log.append('')
    log.append('FITMENT (interference against the reference cylinder)')
    for body, nm in ((a, 'Band A'), (b, 'Band B')):
        v = clash(tbm, part, body)
        log.append('  seated vs %s: %.3f mm3 %s'
                   % (nm, v, 'CLEAR' if v < 0.01 else '** CLASH **'))
    # A cylinder does not clear the lip when its top corner passes it, the way a
    # rounded rectangle does - it clears when its LOWEST point rises above the
    # lip tip. Peak splay is at the point where its equator is level with the
    # tip, which is the force the fingers actually feel.
    gd = mmv(P, 'grip_d')
    for bd, nm, kd, sf in ((a, 'Band A', kinds[0], ''),
                           (b, 'Band B', kinds[1], SFX_B)):
        if kd != 'snap':
            continue
        gg = mmv(P, 'grip_d' + sf)
        zt = mmv(P, 'lip_zt' + sf)
        peak = zt - pz
        free = zt - pz + gg / 2.0
        for h, what in ((peak, 'peak splay - the equator is level with the lip tip'),
                        (free, 'the part is above the lip')):
            v = clash(tbm, part, bd, shift_matrix(h))
            log.append('  lifted %.2f mm vs %s: %.3f mm3  %s'
                       % (h, nm, v, ('clear - ' if v < 0.01 else 'arms splayed - ')
                          + what))
    # The AXIAL stop, which survives Band B becoming a snap: its bore is cut for
    # the BODY, so the larger CAP still cannot enter it and the light's own
    # shoulder lands on that bed face. Seated, the cap ends exactly ON the face
    # and the two touch with zero overlap, so drive it 1 mm past to see it.
    if pr.get('cap_len') and abs(mmv(P, 'grip_d_b') - gd) > 0.01:
        through = temp_cyl(tbm, gd, pz, xb, xb + 1.0)
        v = clash(tbm, through, b)
        eng = (gd - (mmv(P, 'cav_r_b') * 2.0 - 2.0 * PRINT_BIAS)) / 2.0
        log.append('  AXIAL: the stop is the annulus between Band B\'s bore and '
                   'the cap - %.2f mm of radial engagement as printed, over the '
                   'arc the shoulder lands on %s'
                   % (eng, 'OK' if eng >= 0.5 else '** thin - the shoulder may '
                      'ride over it **'))
        log.append('  AXIAL: driving the %.2f cap 1 mm past Band B\'s bed face '
                   'overlaps it by %.1f mm3 %s'
                   % (gd, v, 'OK - the cap cannot pass, so the part cannot slide '
                      'in' if v > 0.5 else '** the cap goes straight through - '
                      'there is no axial stop **'))
    if kinds[1] == 'cradle':
        log.append('  Band B is an OPEN CRADLE, so the part must be clear of it at '
                   'EVERY height - nothing there is allowed to grip:')
        bad = False
        for h in (0.25, 0.5, 1.0, 2.0, 4.0, 8.0):
            v = clash(tbm, part, b, shift_matrix(h))
            bad = bad or v >= 0.01
            log.append('    lifted %4.2f mm vs Band B: %.3f mm3 %s'
                       % (h, v, 'clear' if v < 0.01 else '** IT IS CATCHING **'))
        log.append('    -> the light lifts off its magnetic cap with nothing but '
                   'the magnet to beat %s' % ('OK' if not bad else '** NOT FREE **'))
    # Sketch geometry is frozen numbers, so re-expressing part_d would NOT move
    # the modelled part. Build a temporary cylinder at each diameter instead.
    log.append('')
    log.append('SENSITIVITY to the diameter. Seated must stay CLEAR at every one of '
               'these, because "held proud" is the failure that cannot be lived '
               'with; free lift is the recoverable direction.')
    if pr.get('cap_len'):
        cx0, cx1 = xb - mmv(P, 'cap_len'), xb
    else:
        cx0 = (xa + xb + bl) / 2.0 - L / 2.0
        cx1 = cx0 + L
    # THE RETENTION CLIFF. A snap retains because its throat is narrower than
    # the part; below that there is no detent at all, at any lift, and no amount
    # of lip_clear or cav_clear changes it. Print the threshold explicitly - it
    # is the single number that decides whether this band holds anything, and
    # deriving it by hand after a failed print has cost this part five of them.
    cliff = 2.0 * mmv(P, 'lip_tip_y') - 2.0 * PRINT_BIAS
    log.append('   THROAT as printed %.2f mm -> a cap at or under this diameter '
               'DROPS STRAIGHT THROUGH: no retention at any lift, whatever '
               'lip_clear and cav_clear say. Nominal grip dia %.2f, so the margin '
               'is %.2f mm and the part must hold its diameter to within that '
               'over the whole %.1f mm the band covers.'
               % (cliff, gd, gd - cliff, L))
    for err in (-1.20, -0.90, -0.60, -0.40, -0.20, 0.0, 0.20, 0.40, 0.60):
        dd = gd + err
        tc = temp_cyl(tbm, dd, bt + dd / 2.0, cx0, cx1)
        v = clash(tbm, tc, a)
        play = 0.0
        if v < 0.01:
            lo, hi = 0.0, 6.0
            for _ in range(14):
                md = (lo + hi) / 2.0
                if clash(tbm, tc, a, shift_matrix(md)) < 0.01:
                    lo = md
                else:
                    hi = md
            play = lo
        log.append('   GRIP dia %5.2f (%+.2f) -> seated %7.3f mm3 %s, lifts %.2f '
                   'mm before the lip bites%s'
                   % (dd, err, v, 'CLEAR' if v < 0.01 else 'CLASH ', play,
                      '  ** UNDER THE THROAT - NOT RETAINED AT ALL **'
                      if dd <= cliff else ''))

    if kinds[1] == 'snap' and abs(mmv(P, 'grip_d_b') - gd) > 0.01:
        # The BODY is its own measurement with its own error bar, and Band B is
        # now the band that holds it. Sweep it separately - sharing Band A's
        # sweep would be the same mistake as sharing its bore.
        bdy = mmv(P, 'grip_d_b')
        crb = mmv(P, 'cav_r_b'); czb = mmv(P, 'bore_z_b')
        bx0 = xb
        bx1 = xb + L - mmv(P, 'cap_len') if pr.get('cap_len') else xb + bl
        cliff_b = 2.0 * mmv(P, 'lip_tip_y_b') - 2.0 * PRINT_BIAS
        log.append('')
        log.append('   BAND B / the %.2f BODY. Throat as printed %.2f -> a body at '
                   'or under that drops straight through. Margin %.2f mm.'
                   % (bdy, cliff_b, bdy - cliff_b))
        for err in (-0.40, -0.20, 0.0, 0.20, 0.40):
            dd = bdy + err
            tc = temp_cyl(tbm, dd, czb - (crb - dd / 2.0), bx0, bx1)
            v = clash(tbm, tc, b)
            play = 0.0
            if v < 0.01:
                lo, hi = 0.0, 6.0
                for _ in range(14):
                    md = (lo + hi) / 2.0
                    if clash(tbm, tc, b, shift_matrix(md)) < 0.01:
                        lo = md
                    else:
                        hi = md
                play = lo
            log.append('   BODY dia %5.2f (%+.2f) -> seated %7.3f mm3 %s, lifts '
                       '%.2f mm before the lip bites%s'
                       % (dd, err, v, 'CLEAR' if v < 0.01 else 'CLASH ', play,
                          '  ** UNDER THE THROAT - NOT RETAINED **'
                          if dd <= cliff_b else ''))

    unhealthy = [design.timeline.item(i).name for i in range(design.timeline.count)
                 if design.timeline.item(i).healthState !=
                 adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    log.append('')
    log.append('timeline: %d features, %d unhealthy %s'
               % (design.timeline.count, len(unhealthy), unhealthy or ''))
    log.append('NOTE "%s" is a reference body, NOT printed. Export only Band A and '
               'Band B.' % part.name)

    if existing is not None:
        doc.save('Rebuilt from modgrid_round_holder.py')
    else:
        doc.saveAs(doc_name, folder, pr['blurb'], '')
    log.append('save issued for "%s" in "%s"' % (doc_name, folder.name))
    return '\n'.join(log)
