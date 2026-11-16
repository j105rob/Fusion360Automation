# Slant 3D — Designing Out Overhangs (Chamfers, Tabs, Clips, Domes)

Research captured 2026-09-30 from transcripts of Slant 3D's playlist **"Design Your Own Supports for 3D Printing"**. This covers the videos about removing the *need* for support through geometry. For supports you model yourself, see `slant3d-designed-supports.md`.

## Principles
- Supports cost material, post-processing time, and labour (often a person has to pull them by hand). They also scar the surface where the part rested on them. The best support is none.
- Two failure cases need support: **overhangs** (a flat edge sticking out into air sags) and **bridges** (a span between two uprights sags on the first layer).
- **Fill it in.** If a cavity, notch, or overhang isn't needed for function, make it solid. Infill makes it cost about the same material as the support would have, and nothing needs removing.
- Reorienting can remove supports entirely. Example: chamfer a cube's edges and stand it 45° on one edge. It's stronger, looks better, and needs no support.

## Chamfer vs fillet on downward-facing edges
| Option | Verdict |
|---|---|
| Plain 90° overhang | Needs support. Avoid. |
| Fillet | Better, but still needs a little support: a fillet is **tangent to horizontal** where it meets the overhang, so its last bit is flat. A long overhang still needs a sliver of support there. |
| Fillet done fully | If a fillet is required for looks, carry it all the way so no horizontal land is left at the tip (round out the tip too). A small fillet makes the curve turn steep quickly, which is harder to print than a chamfer. |
| **Chamfer (45°)** | **Preferred.** Constant angle all the way, no horizontal region, no support. You can soften the sharp chamfer edges with small fillets afterwards if you like. |
| Chamfer at other angles | If 45° doesn't fit the design, a shallower or deeper chamfer is still better than a big fillet. Slant: "as high as 60° is generally fine" but shows higher risk of warping or sag if flow or cooling is off. For maximum robustness, use the **steepest** chamfer (closest to vertical) the design allows. |

*Angle convention:* the captions don't say which reference Slant's "60°" uses. Our rule stays **≤ 45° from vertical** for guaranteed prints, and **up to ~60° from vertical only on short spans** that we've test-printed in ABS.

## Horizontal mounting features
| Feature | Bad | Good |
|---|---|---|
| **Tab with a hole** (mounting ear) | Flat tab sticking out: needs support, ugly underside, costs more | Run a **chamfer (gusset) under the tab** down to the wall. Almost no extra material, no support, much stronger. Still mates the same. |
| If a flat tab is unavoidable | — | Round all its corners and its underside so the supported surface comes out as clean as possible |
| **Clips / snap clamps** | Finger sticking straight out into air | **Chamfer the underside** of the clip finger. Then re-tune thickness and length so it still flexes the right amount, since the chamfer stiffens it. |
| **Wire-retaining loops / guides** | Sideways loop with a flat ceiling | **Two chamfers:** chamfer the front face, then cut in and chamfer the inner edge so every downward face angles up ("up, then up again"). No flat ceiling left to sag. It can still include a snap for the wire. |

## Domes
The inside of a hemispherical dome overhangs and ends almost flat at the crown. It prints droopy and stringy, and on thin walls the distortion shows through to the outside.
| Fix | Detail |
|---|---|
| Change the shape | Make it slightly **egg-shaped**: raise the crown and taper the inside to a point, so there's no flat curved ceiling |
| **Different inside and outside** | Printing isn't moulding, so walls don't need uniform thickness. Keep the outside a true hemisphere and make the **inside a pointed or conical (≤45°) cavity**. Same look, clean print. |
| Inside must be spherical | Use a designed **mushroom support** (wide cap, thin stalk, ~0.5 mm+ gap), see `slant3d-designed-supports.md` |
| Very large dome / using auto supports | Keep the dome, but **cap the inside crown with a small flat** so auto supports have a clean flat target and pop off |

The same thinking applies to any **arch or round horizontal hole**: use a teardrop or pointed top instead of a round one (already in `design-for-fdm-printing.md`).

## Rules to apply in Fusion
| # | Rule |
|---|---|
| O1 | Before adding any support, try: fill it solid → chamfer it → reorient the part. |
| O2 | Downward-facing edges: **Chamfer, not fillet** (existing rule, confirmed). If a fillet is needed for looks, add it on top of a chamfer or on upward or vertical edges only. |
| O3 | Every cantilevered tab, ear, or boss gets a 45° gusset or chamfer underneath, running down to the wall it grows from. |
| O4 | Snap clips: chamfer the underside, then check the flex (thickness and length) with the chamfer included. Keep beam thickness, length, and chamfer as user parameters. |
| O5 | Loops and hooks: no flat ceilings. Chamfer each downward face of the opening. |
| O6 | Internal cavities (domes, arches, bores printed sideways): the inside can differ from the outside. Use a pointed or teardrop interior while keeping the cosmetic exterior. |
| O7 | Use variable wall thickness freely where it removes an overhang. FDM has no uniform-wall rule. |

## Sources (playlist: [Design Your Own Supports for 3D Printing](https://www.youtube.com/playlist?list=PLkUv8_afCbJ8Pu83Gx-j36phSagA9-R5D), transcripts pulled 2026-09-30)
- [Easiest Way to Eliminate Supports | 3D Printing Design for Beginners (2022-11-29)](https://www.youtube.com/watch?v=FMs-VGAu_PQ)
- [3D Printing Basics: Understanding and Managing Support Material (2023-06-23)](https://www.youtube.com/watch?v=WYQbxIVLz6Y)
- [Better Horizontal Mounting Features (2024-01-16)](https://www.youtube.com/watch?v=FF4D_Moywgk)
- [Secrets to Better 3D Printed Domes (2024-04-23)](https://www.youtube.com/watch?v=udEeJjzEQZI)
- [Stop Using Slicer Supports (2025-05-23)](https://www.youtube.com/watch?v=_R2E8VwyNz0), the "rotate 45° + chamfer" example
