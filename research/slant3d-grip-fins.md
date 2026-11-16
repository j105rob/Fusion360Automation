# Slant 3D — Grip Fins for Self-Adjusting Holes and Press Fits

Research captured 2026-09-30 from the transcript of Slant 3D's *"You Don't Use Fins Enough"* (2026-02-10), part of the **"Design Your Own Supports for 3D Printing"** playlist. The support-fin half of that video is in `slant3d-designed-supports.md`.

## Problem
A plain hole sized to fit a pin works on one printer with one material. Shrinkage (ABS ~0.5–0.7 %), machine settings, flow and expansion, nozzle size, and even filament colour all change the real clearance. Chasing a perfect dimension doesn't work across machines.

## Grip fins
Flexible fingers around the inside of a hole (or around a lid rim) that **spring out to grip an undersized pin and push back to admit an oversized one**. The joint works across a range of sizes instead of at one exact value.

### How to model them (Slant's recommended method)
1. Make the hole **slightly smaller than the pin**. That guarantees an interference fit, so the fins always have something to grip.
2. **Cut slots** radially around the hole wall. The material left between slots becomes the fins.
3. **Free the fins at the base.** This is the step people miss. Cut a **disc (an undercut) beneath the fins** at the bottom of the hole so each fin flexes along its whole length instead of being fused to the hole floor.

The alternative, drawing inward-pointing fins into a nominal hole, is harder because you lose track of the effective diameter.

### Tuning
| Change | Effect |
|---|---|
| Longer fins | softer |
| Thinner fins | softer |
| Shorter or thicker fins | stiffer, higher insertion force |

It works on round pins and holes, and also on square or rectangular lids, slots, and rims.

## Rules to apply in Fusion
| # | Rule |
|---|---|
| G1 | For **press-fit** joints that must work across printers or materials, use grip fins instead of chasing clearance. (Glue joints keep the 0.15 mm/side clearance rule. Grip fins suit dry-fit, removable, or friction joints.) |
| G2 | Hole diameter = pin diameter minus interference (a user parameter, e.g. `grip_interference`). |
| G3 | Slot count, slot width, fin length, and base-relief disc depth are user parameters, so the fit can be tuned after one test print. |
| G4 | Always add the base-relief undercut. Check that the undercut itself doesn't create an unsupported flat ceiling in the print orientation. Chamfer it or make it a teardrop if the hole is horizontal. |
| G5 | Slot width ≥ ~0.8 mm (≥ 2 extrusion widths) so the slots don't fuse shut. At bed level, keep ≥ 1.0 mm per the elephant-foot rule. |
| G6 | Fins bend across layer lines if the hole axis is vertical (Z). That's fine for small deflection. For stiff or repeated use, orient so the fins bend within layers. |

G5 and G6 are our own inferences from the general FDM rules, not numbers from the video.

## Sources
- [Slant 3D — You Don't Use Fins Enough (YouTube)](https://www.youtube.com/watch?v=6gPPAiqSkBc), transcript pulled 2026-09-30
