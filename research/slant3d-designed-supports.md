# Slant 3D — Designed Supports: Fins, Sprues, Combs, Thumbtacks, Blocks

Research captured 2026-09-30 from transcripts of Slant 3D's YouTube playlist **"Design Your Own Supports for 3D Printing"** (9 videos). This file is the catalogue of **support types you model in CAD**. Related files:
- `slant3d-designing-out-overhangs.md`: geometry changes that remove the need for support (try these first).
- `slant3d-grip-fins.md`: grip fins for holes and press fits (a tolerance technique, not a support).
- `slant3d-diagonal-print-fin-supports.md`: the 45° enclosure video in the same playlist.
- `fusion-slant3d-fin-support-workflow.md`: a step-by-step Fusion build of a fin.

A caveat on the numbers: these come from auto-generated captions, and Slant rarely states numbers carefully. Where the captions are ambiguous (for example "2 to 3 mm" where the context clearly means 0.2–0.3 mm), the interpretation is marked.

## Why not slicer supports (the argument across the playlist)
- Auto supports are a generic answer and give generic results. They depend on each person's slicer settings, so a design shared or sent to a print service comes out differently for everyone.
- **Auto supports don't touch the part.** They keep an air gap so they can be removed. Narrow features growing up from nothing (a tooth, a beak, a part printed on its edge) can **lean, wobble, or settle into the support "nest"**, which leaves distortion or banding on the surface.
- Slicers often miss small downward-pointing tips ("icicle" overhangs) entirely.
- Designed supports go only where they're needed, use less material, can be **tied rigidly to the part**, and can carry instructions such as a "SUPPORT" label.
- They're fine for one-offs at home. For anything shared, sold, or repeated, design the support in CAD.

## Order of preference
1. **No support:** reorient (for example, tilt 45° onto a chamfered edge), chamfer the overhang, or fill the cavity solid. See `slant3d-designing-out-overhangs.md`.
2. **Designed support tied to the part** by sprues: fin, comb.
3. **Designed support sitting on the bed or on the part with a gap**: offset shell, mushroom, bridge block.
4. **Prepare the part so auto supports behave:** thumbtacks, a flat cap on dome interiors, supports exported from the slicer.

## Support types

### 1. Support fin (tied to the part with sprues)
Used when a part printed at an angle or on its edge would **topple** because its centre of gravity isn't over its bed contact, or to stiffen tall thin parts.
| Rule | Value / detail | Video |
|---|---|---|
| Shape | Triangular prism or thin plate under or beside the part, spaced off it | Stop Using Slicer Supports; You Don't Use Fins Enough |
| Fin-to-part gap | ~0.2 mm when the fin face follows the part face ("0.2 mm away"). 0.5–1 mm in the 45° box video. | Fins; Correct Orientation |
| **Sprue direction** | **Horizontal, parallel to the build plate**, NOT perpendicular to the part face. Horizontal sprues print as one continuous extrusion from fin into part and fuse fully. Perpendicular ones become tiny isolated "tips" in each layer: weak, they snap off mid-print, and they leave blobs. Slant calls this "a universal mistake". | Fins |
| Sprue size | about **0.5 mm thick × 0.5–1 mm wide**, horizontal so each is roughly a single layer tall where it enters the part | Stop Using Slicer Supports |
| Sprue count | "a few" is enough. They only need to stop the part sliding or tipping. | Stop Using Slicer Supports |
| One-sided | A fin tied to the part holds it both ways, so you only need a fin on **one side**. A loose (untied) support has to be on both sides. | Fins |
| Thin fin | Keep the fin plate thin to save material and so it can flex off. Give it a **wide base (an ellipse foot)** so it doesn't peel off the bed. | Fins; Stop Using Slicer Supports |
| Thick fin | If you make it fat, **chamfer or fillet its front** so the sprues are reachable for twisting or snipping. Don't bury sprues inside a thick block. | Stop Using Slicer Supports |
| Bed contact of part | Never stand a part on a sharp corner or edge. **Chamfer it to a flat strip** or it won't stick (Slant shows a failed print). | Fins |
| Break notch | optional notch near the part surface so sprues snap flush | Correct Orientation |

### 2. Support comb (tall, thin parts)
A **vertical post with a wide base** and a row of **horizontal sprues** reaching into the side of a tall thin part. It stops Z-banding and wobble near the top, especially on bed-slinger printers.
| Rule | Value / detail |
|---|---|
| Sprue diameter | **1 mm**, "smallest reasonable size for most printers" at 0.4 mm |
| Sprue direction | perfectly horizontal: the nozzle runs out to the tip and back, leaving a thread fused into the part |
| Placement | post **as close to the part as possible** (any gap = flex). Stop below the very top of the part. |
| Fitting to a curved part | Model the sprues extra long. Subtract a copy of the part to trim them to its profile, discard the pieces that poke out the far side, then push the comb **slightly into the part** so the sprues overlap. Union them. |
| Removal | flush cutters. Leaves small pock marks, like resin-print support marks. A heat gun softens them on PLA. |
| Benefit | Tall thin parts can print upright, in the strong layer orientation, with no big flat bed face |

### 3. Thumbtack (icicle tips and small downward points)
A small **pin on top of a wide platform**, placed under a downward-pointing tip (beak, tooth). The auto supports then land on the wide platform, not the fragile tip, and the tip grows from a firm base.
| Rule | Value / detail |
|---|---|
| Stem | **1 mm wide = two perimeters of a 0.4 mm nozzle** plus a little room. Don't scale thumbtacks much, or the slicer drops the stem. |
| Variants | **standard** (vertical only); **spherical** (can be rotated to reach in from the side); **omnidirectional** (many spines, only needs rough placement); **comb thumbtack** (a row of ~5 sprues under a long lower edge such as a chin or fingertips) |
| Placement | Press spines in as far as possible, but keep contact points on non-visible faces, because snipping leaves a divot |
| Caveat | A thumbtack still needs support underneath. A tall thin thumbtack column **can fall over** (it happened during filming). Where you can, prefer a comb or fin tied to the main part with sprues. |
| Use for our work | Mainly organic or figure shapes. Rarely needed for mechanical parts, where a chamfer or teardrop handles tips. |

### 4. Offset support shell (contoured, not tied)
A support body that **follows the underside of the overhang with a small offset** (Offset Face or Shell in CAD).
| Rule | Value / detail |
|---|---|
| Gap | Captions say "about 2 to 3 mm". This almost certainly means **0.2–0.3 mm**, consistent with the fin (0.2 mm) and block (0.2 / 0.2–0.3 mm) values in the same playlist. **Test-print to confirm for each material.** |
| Limitation | Sensitive to material expansion and machine. Verify with a couple of test prints before trusting it. |

### 5. Bridge block (tunnels and long bridges)
| Rule | Value / detail |
|---|---|
| When | Most printers bridge "1 to 2 inches" (25–50 mm) fine, so only for spans beyond that or when you need a clean ceiling. (For ABS we keep our own ≤10–15 mm rule.) |
| Clearance | **Top 0.2 mm, bottom 0.2–0.3 mm** (the generic starting point; test per material) |
| Make it removable | Cut a **hole through the block** so pliers can crush it and pull it out. If it's too big to hollow, **chamfer its edges** so it can be twisted loose. |
| Label | **Emboss "SUPPORT"** on the block so post-processors and customers know to remove it. It can double as a shipping restraint. |

### 6. Hollow pointed block (under a local overhang)
Seen in "Understanding and Managing Support Material": a small block **printed hollow** that rises to a **point or ridge** touching the overhang. It uses little material and breaks off easily.
- Where the block sits on a lower surface of the part, give its base a **slightly rounded (teardrop) bottom** to cut friction and bonding. Keep it only slightly rounded so the block stays stable.

### 7. Mushroom (dome interiors)
- A wide **cap** under the dome's crown on a **thin stalk** that can still stand on its own.
- **Gap to the dome: ~0.5 mm or more.**

### 8. Preparing the part for auto supports (when you do use them)
- **Dome interior:** cap the inside tip with a small **flat** so auto supports have a clean flat target to land on and pop off.
- **PrusaSlicer trick:** switch the printer profile to SLA, generate **thick tree supports**, and **export them as an STL**. They become designed geometry you can ship with the part. (Optional. They may need thickening for FDM.)

## Rules to apply in Fusion
| # | Rule |
|---|---|
| D1 | Work through the order of preference above. Only model a support after reorienting, chamfering, or filling has failed. |
| D2 | **Sprues are horizontal in the print frame.** For a part printed tilted, compute the bed normal in model coordinates and extrude sprues **perpendicular to that normal**, not along the face normal. |
| D3 | Side-tied sprue: ~0.5 mm tall (Z in the print frame) × 0.5–1 mm wide. Comb or thumbtack sprue: 1 mm round or square. Keep sprues ≥ 2 perimeters wide (≥ 0.8 mm) in their widest direction or the slicer may drop them. |
| D4 | Tied fin gap ~0.2–1 mm. Untied contoured shell or block gap 0.2–0.3 mm. Mushroom gap ≥ 0.5 mm. These are PLA/PETG starting points: **test-print for ABS.** |
| D5 | A fin tied to the part needs to be on one side only. Thin plate + wide foot (ellipse or rounded plate), or a thick fin with a chamfered front. |
| D6 | Anything standing on the bed at an angle gets a chamfered flat on its bed edge. |
| D7 | Large bridge blocks: crush-hole through the middle or chamfered edges, plus embossed "SUPPORT" text. |
| D8 | Keep sprue contact on non-cosmetic faces. Snipping leaves a pock mark. |
| D9 | Model supports as separate `Support - …` bodies, overlap them into the part ~0.05 mm, and export them together with the part (existing convention). |
| D10 | **Existing shelf pin fins:** those fins stand *under* the teardrop pin tip (contact from below, a Z contact), so the "perpendicular tine" warning doesn't apply. The warning applies to fins that touch a part **from the side**. |

## Sources (playlist: [Design Your Own Supports for 3D Printing](https://www.youtube.com/playlist?list=PLkUv8_afCbJ8Pu83Gx-j36phSagA9-R5D), transcripts pulled 2026-09-30)
- [Stop Using Slicer Supports | Design for 3D Printing (2025-05-23)](https://www.youtube.com/watch?v=_R2E8VwyNz0)
- [You Don't Use Fins Enough (2026-02-10)](https://www.youtube.com/watch?v=6gPPAiqSkBc)
- [Stop Tall Prints From Falling Over (2023-04-04)](https://www.youtube.com/watch?v=3Acks3Wzjjo)
- [These Free STL's are Better than Tree Supports (2023-02-04)](https://www.youtube.com/watch?v=YL5lYEXbLDo)
- [3D Printing Basics: Understanding and Managing Support Material (2023-06-23)](https://www.youtube.com/watch?v=WYQbxIVLz6Y)
- [Secrets to Better 3D Printed Domes (2024-04-23)](https://www.youtube.com/watch?v=udEeJjzEQZI)
- [The Correct Orientation to Print Boxes (2024-01-25)](https://youtu.be/8NKVNwVaZU0), see `slant3d-diagonal-print-fin-supports.md`
