# Slant 3D — Diagonal (45°) Printing with Designed Fin Supports

Research captured 2026-09-30 from the transcript of Slant 3D's video *"The Correct Orientation to Print Boxes | Design for Mass Production 3D Printing"* (uploaded 2024-01-25, ~6 min). This is the original video behind the "fins and sprues" technique in `design-for-fdm-printing.md`.

It is part of the playlist [Design Your Own Supports for 3D Printing](https://www.youtube.com/playlist?list=PLkUv8_afCbJ8Pu83Gx-j36phSagA9-R5D). The other support types from that playlist are in `slant3d-designed-supports.md`. Note that the later video "You Don't Use Fins Enough" says sprues must be **horizontal to the bed**, which this video also says.

The video is short and conceptual. It gives **one hard number** (fin-to-part gap) and a few qualitative rules. It does **not** give fin thickness, sprue size, sprue spacing, or fin height. Those numbers in `design-for-fdm-printing.md` come from the written sources and the Shop Therapy video (see `fusion-slant3d-fin-support-workflow.md`).

## Problem it solves
Enclosures (open boxes) are usually printed one of two ways:
| Orientation | Upside | Downside |
|---|---|---|
| Flat (opening up, floor on bed) | Rigid, reliable, good bed adhesion, layer lines horizontal throughout | Needs a large bed. Layers can split along the plane when a screw is driven or the part is pulled. |
| Vertical (on its end) | Fits a small bed | Needs support under and inside the part: lots of post-processing and cost. Layer lines form a weak bending plane. |

Slant's third option: **print the enclosure diagonally, tipped about 45°**, with one edge on the bed and a designed fin supporting the back.

## Why 45°
- 45° is the steepest self-supporting overhang. At that tilt, neither the shallow back face nor the steep front face overhangs past the limit.
- **Strength:** no feature has all its layers stacked along one splitting plane. Screw bosses and lid holes are looped all the way around by perimeters instead of being layered across, so an oversized screw can't split them along a layer line. Side walls and flanges get the same benefit.
- Every face ends up printed at an angle, which gives even surface quality on all sides. Stair-stepping is spread over each face instead of piling up on the flat tops.

## The support fin, as Slant designs it
1. **Why a support at all:** tipped at 45°, the part's centre of mass is no longer over its bed contact line, so it will topple mid-print without something behind it.
2. **Why not slicer supports:** auto supports cost more material and are less reliable. They also sit a small distance from the part so they can be removed, and that gap lets the part **flex and wobble** as it grows. A designed fin is **rigidly joined** through sprues, so the part stays stiff.
3. **Fin geometry:**
   - A flat fin coming off the bed at **45°**, running **parallel to the back face** of the part.
   - **Gap between fin and part: about 0.5–1 mm.**
   - **Sprues:** short horizontal ribs running from the fin into the part, in a row up the fin like a comb. Horizontal = parallel to the bed, so each sprue is a short bridge or ledge that prints cleanly.
4. **Removal:** break it off. It leaves a few small divots, which you can sand or just leave.
5. **Break notch (optional):** add a small notch or "break tooth" in each sprue near the part surface so it snaps flush with the part instead of leaving a stub.
6. **Flat on the bed edge:** flatten the part's bed-contact edge a little (a small flat or chamfer) so a real strip of the part touches the bed, not a knife edge.

## Other enclosure-design points from the video
- Take advantage of FDM and make areas that carry loads chunky: thick outer flanges give solid screw points.
- Keep the areas that fasteners clamp through at the original thickness so the original fastener lengths still work.
- **Walls: 2 mm minimum, up to 5–10 mm** where useful. FDM has none of the sink or shrink limits of moulded parts.
- Use the thick walls to add a mating ridge on the rim. The lid has a lip on its inside that locates on it.
- The lid was printed at **~35°** (less steep than the box). The tilt can be tuned per part and doesn't have to be exactly 45°.
- Optional: add fuzzy-skin or noise texture to outside faces. It hides layer lines and looks good.

## Rules to apply in Fusion
| # | Rule | Source value |
|---|---|---|
| S1 | For boxes and enclosures, consider a diagonal print (≈35–45°) when you need strength in all directions or even finish on every face. For one-offs, flat is still fine (see `design-for-fdm-printing.md`). | 45° box, 35° lid |
| S2 | If the part's centre of mass falls outside its bed contact at the chosen tilt, add a designed fin. Never rely on slicer supports. | — |
| S3 | Fin is a flat plate at 45° off the bed, parallel to the part face it supports. | 45° |
| S4 | Fin-to-part gap | **0.5–1 mm** |
| S5 | Sprues run **horizontal** (parallel to bed) from fin into part, spaced along the fin's full height. | spacing not given |
| S6 | Add a break notch in each sprue close to the part surface for a clean snap-off. | size not given |
| S7 | Flatten the bed-contact edge so it has a real footprint. Add a brim if the footprint is small. | — |
| S8 | Walls 2 mm minimum. Thicken load paths (screw flanges, rims). | 2–10 mm |

## Sources
- [Slant 3D — The Correct Orientation to Print Boxes (YouTube)](https://youtu.be/8NKVNwVaZU0), transcript pulled 2026-09-30
