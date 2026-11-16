# Fusion Workflow — Building Slant-3D-Style Fin Supports

Research captured 2026-09-30 from the transcript of Shop Therapy's *"Autodesk Fusion: Make supports like Slant 3D"* (uploaded 2024-12-19, ~24 min). It is a hands-on Fusion build of the fin described in `slant3d-diagonal-print-fin-supports.md`, followed by an actual print and a review of the result.

## Test case
- Large single-body base (a Helix 7 ice-fishing conversion kit): **210 × 230 mm, ~460 g**, nearly filling a Bambu P1S bed. Printed in PETG-HF, 0.2 mm layers, ~4 walls, ~15 % infill.
- Printed flat, the top faces show visible stair-stepping. The goal of the tilt was a clean finish on all faces (for example, if the part were used as a casting master).
- Tilted **45°** so that only one chamfered edge touches the bed, with a **single fin** in the middle of the back face.

## Fusion steps (as done in the video)
1. **Sketch on the mid-plane** (the YZ origin plane in his case) through the middle of the part, perpendicular to the edge that will sit on the bed.
2. **Project** the part's bottom outline into the sketch (`P`) so you can hide the body and still see its edges.
3. **Bed line:** a line at **45°** from the bed-contact edge. It stands in for the print bed in the tilted frame. (Tab into the angle field and type 45.)
4. **Fin profile:**
   - Make the projected back-face line a construction line and **offset it by 1 mm** away from the part. The offset line is the fin's inner edge, leaving a **1 mm gap**.
   - Close a triangle: fin inner edge → a line back to the bed line at 90° → the bed line. Run the fin **past halfway up the part face, ideally about ¾**.
5. **Sprue "comb":** draw a **1 × 1 mm square** bridging the 1 mm gap between fin edge and part face. Use **Rectangular Pattern** to repeat it along the fin edge (**10 teeth** over ~¾ of the face). Precision isn't critical.
6. **Extrude the fin** with **Symmetric, whole length = 2 mm** (fin thickness 2 mm). Watch the Symmetric option: "half length" doubles the value.
7. **Extrude the sprue squares:** Symmetric, whole length **1 mm**, **Join** to the fin. The sprues are narrower than the fin: 1 × 1 mm cross-section touching the part.
8. **Fin foot / base plate:** sketch on the fin's bed face with a **centre rectangle, 60 mm** long, and extrude **1 mm** into a flat foot plate. Check that it doesn't touch the part.
9. **Round the foot's corners** (he used **20 mm fillets**) so the plate doesn't curl or lift.
10. **Strengthen the fin-to-foot joint** with a two-distance chamfer (**2 mm up the fin × 10 mm along the foot**), then optionally a second **2 mm equal** chamfer on top. This is a gusset that keeps the tall fin from wobbling.
11. **Slice:** "Lay on face" with the bed-contact face, then turn on an **outer brim (5 mm)**. The part's only bed contact is one chamfer edge plus the fin foot.

## Print result and lessons
| Observation | Takeaway |
|---|---|
| Supports "just bent right off", leaving only small marks where the sprues joined | 1 × 1 mm sprues on a 2 mm fin with a 1 mm gap snap off cleanly in PETG |
| Every face flat and clean. Pockets and fits dimensionally accurate. | The 45° tilt works even on a bed-filling part |
| Some ghosting and ringing around holes and edges; walls not perfectly smooth | Likely wobble: a huge part on a single fin |
| Some corners printed badly | Those corners had no support in the tilted orientation. Check **every** local overhang in the tilted frame, not just the main face. |
| Bottom face very slightly rocked or rounded | Possibly flex from too little support. Author would use **2–3 fins** next time. |
| Summary | On smaller parts one fin is plenty. On large parts, spread several fins across the back face. |

## Rules to apply in Fusion
| # | Rule | Value from video | Our default (`design-for-fdm-printing.md`) |
|---|---|---|---|
| F1 | Sketch the fin profile on a mid-plane perpendicular to the bed-contact edge. Project the part outline first. | — | same |
| F2 | Draw a construction "bed line" in the tilted frame so all angles are measured against the real bed. | 45° | same |
| F3 | Fin inner edge = part face offset by the gap | 1 mm | 0.5–1 mm (Slant: 0.5–1 mm) |
| F4 | Fin height | > ½, ideally ~¾ of the supported face | same |
| F5 | Fin thickness | 2 mm (large PETG part) | 0.8–1.2 mm for small parts. Go to ~2 mm on large or tall parts. |
| F6 | Sprues: sketch one tooth, then Rectangular Pattern along the fin | 1 × 1 mm, 10 teeth over ~170 mm (~15–20 mm pitch) | contact 0.2–0.4 mm wide when tapered. A 1 mm square tooth is fine for break-off fins. |
| F7 | Build fin and sprues as **separate bodies** from the part (the video joins them to each other, not to the part) | — | `Support - …` bodies, ~0.05 mm overlap into the part, export together |
| F8 | Fin foot plate on the bed, with rounded corners so it doesn't warp | 60 × 1 mm plate, 20 mm corner fillets | Scale the plate to the fin. For ABS, round the corners and consider mouse-ears. |
| F9 | Gusset chamfer between fin and foot | 2 × 10 mm + 2 mm | Add on any fin taller than ~30 mm |
| F10 | Check nothing but the sprues touches the part (foot plate, fin, gusset) | — | Interference check with `TemporaryBRepManager`, excluding supports from the assembly check |
| F11 | Brim when bed contact is only an edge | 5 mm outer brim | A brim is a slicer adhesion aid, not a support, so it's allowed |
| F12 | Big parts: several fins spaced across the face | 1 fin wobbled on 230 mm | ≥ 1 fin per ~80–100 mm of face width (our judgment, not from the video) |
| F13 | After placing the tilt, re-scan every edge and corner for local overhangs > 45°. Add a small fin or chamfer them. | missed corners printed badly | checklist step 2 |

## Fusion API equivalents (for our scripts)
- Mid-plane sketch: `sketches.add(rootComp.yZConstructionPlane)` or a construction plane at the part's centre. Project with `sketch.project(edge)`.
- Offset gap: `sketch.offset(curves, dirPoint, gap)` or `SketchLines.addByTwoPoints` from computed points.
- Sprue teeth: draw one rectangle and use `rectangularPatterns` on the extruded tooth body (or loop in Python to draw N rectangles, which is simpler and parametric).
- Symmetric extrude: `extInput.setSymmetricExtent(ValueInput.createByString('fin_t'), True)` — `True` = whole length. This avoids the half-length trap from step 6.
- Keep `fin_gap`, `fin_t`, `sprue_w`, `sprue_pitch`, `fin_height_frac` as user parameters.

## Sources
- [Shop Therapy — Autodesk Fusion: Make supports like Slant 3D (YouTube)](https://www.youtube.com/watch?v=sn2u949g7dM), transcript pulled 2026-09-30
- [Slant 3D — The Correct Orientation to Print Boxes (YouTube)](https://youtu.be/8NKVNwVaZU0), the source video it follows
