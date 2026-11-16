# MOD-GRID (EDC) — System Specification

Research captured 2026-10-21 before modelling a parametric MOD-GRID baseplate.

MOD-GRID is a modular EDC (everyday-carry) organisation system by **TinyToolShop / 3dedc**,
published free on MakerWorld as STEP/STL. A flat perforated baseplate carries accessory holders
(knife, plier, bit, ratchet, lighter holders) that clip in with a shared connector.

## How these numbers were obtained
**Measured directly from the official files**, not from listings. The MakerWorld pages block
automated fetching (HTTP 403) and the public write-ups contradict each other — "5 mm grid"
and "5.3 mm" are both quoted, and one vendor blog confuses the hole size with the pitch.

The geometry below was extracted from the meshes in the user's Fusion `MODGRID` folder
(`MOD-GRID 4x12` and `MOD-GRID Modular connector v4`) by clustering the mesh vertices.
Both resolve the ambiguity: **5 mm is the hole, 8 mm is the pitch, 5.3 mm is the connector peg.**

> **Import scale warning:** both meshes in that folder are imported **10× oversize**
> (the 4x12 plate measures 990 × 350 × 30 mm in Fusion). The real dimensions are 1/10 of what
> Fusion reports. Everything below is already converted to real mm.

## The grid
| Property | Value | Notes |
|---|---|---|
| **Grid pitch** | **8.000 mm** | both axes, measured over 12 cells |
| **Hole** | **5.000 mm square** | sharp corners, **prismatic straight through** — top and bottom outlines are identical, so no taper, chamfer or undercut |
| Wall between holes | **3.000 mm** | 8 − 5 |
| **Plate thickness** | **3.000 mm** | |
| Border, edge to first hole | **3.0 mm** | exact on the Y axis of the stock plate |
| **Plate size rule** | **8n + 3 mm** | 4×12 → 8(12)+3 = **99.000**, 8(4)+3 = **35.000** ✓ |
| Outer corner radius | ~3 mm | coarsely tessellated in the mesh |

Cross-check: a community parametric plate defaults to 163.3 × 122.7 mm at 20 × 15 cells.
8(20)+3 = 163 and 8(15)+3 = 123 — the same rule.

### One quirk in the stock file
On the stock 4×12 the hole field is **offset ~0.49 mm in X**: margins measure 2.51 / 3.48 mm
instead of 3.0 / 3.0. The Y margins are a clean 3.004 / 2.991. The pitch itself is exactly 8.000
throughout, so this is a modelling slip in the original, not a design feature. It constrains
nothing — accessories register on *pitch*, not on distance to the plate edge — so a new plate
should centre the field symmetrically (3.0 mm all round).

There is also ~0.005 mm of float drift accumulated across 99 mm in the mesh. Ignore it.

## The connector (`MOD-GRID Modular connector v4`)
Overall **15.0 × 5.298 × 5.000 mm**. A **double-ended split peg**:
| Property | Value |
|---|---|
| Peg centre-to-centre | **8.10 mm** ≈ one grid pitch |
| Peg width | **~5.26 mm nominal**, i.e. oversize against the 5.0 mm hole |
| Relief slot in each peg | **~1.0 mm** wide, splitting the peg so it compresses |
| Height | **5.0 mm** = 3 mm through the plate + 2 mm proud |

### Peg geometry in detail (recorded before the MODGRID folder was deleted)
| Property | Value |
|---|---|
| Peg height | **5.00 mm** |
| Split-axis width | **5.26 mm at the root, 5.02 mm at the tip** - a one-axis lead-in taper (~1.4 deg) |
| Solid-axis width | **5.13 mm**, constant (no slot on this axis) |
| Split slot | **~1.02 mm**, constant, parallel to the line joining the two pegs |

~~So retention is an interference fit, not a snap.~~ **SUPERSEDED - see the measured section
below. It is a barbed snap-fit; there IS an undercut and it does catch under the plate.** The split peg squeezes to enter the 5.0 mm hole and springs back against the walls.
The tapered axis enters at near clearance and tightens progressively as it seats; the solid axis
is a straight 0.13 mm crush. The baseplate carries no retention geometry of its own.

**The 5 mm height is load-bearing design, not packaging.** Each split half is a cantilever, and
bending stress goes as 1/L^2 while stiffness goes as 1/L^3. At 5 mm a finger deflecting 0.13 mm
sees ~33 MPa, just inside ABS yield (~40). Shorten it to 2.8 mm - as you would to make an
integrated peg sit flush in a 3 mm plate - and the same deflection becomes ~120 MPa, so the peg
crushes permanently on first insertion instead of springing. The official connector gets its
length by spanning the holder socket (2 mm) plus the plate (3 mm). **An integrated peg must
either run the full 5 mm (and protrude 2 mm below the plate) or have its root relieved into the
body to free the same finger length.**

**Consequence for the baseplate:** hole size is the one tolerance that matters. Too tight and the
connector will not seat; too loose and accessories rattle. Keep a `hole_clear` parameter at 0 and
tune after a test print.

## How official holders actually mount (measured 2026-10-22 from the STL library)

Measured directly from `~/Downloads/MOD-GRID/` (22 official STLs, all at 1:1 - the
`MOD-GRID 4x12` reads exactly 99.000 x 35.000 x 3.000, which independently confirms the grid
spec above and confirms the 10x in the Fusion copies was an import artefact).

**Retention is a BARBED SNAP-FIT, not an interference/friction fit. Earlier notes in this file
said friction; that was wrong, and it was inferred from a partial vertex measurement.**

**Holders carry the mount legs integrally.** They do not use the separate connector. The
`MOD-GRID Modular connector v4` STL turns out to contain **two disconnected solids** - it is two
standalone clips on one plate, an accessory, not the part holders rely on.

### Leg geometry, measured off `MOD-GRID Olfa holder v4`
Axes as the STL sits: X across the legs (flex direction), Y = insertion into the plate,
Z = the holder's third axis and the one that sits in the hole.

| Feature | Value |
|---|---|
| Leg extent along the hole axis (Z) | **4.90 mm** - 0.10 clearance in the 5.00 hole |
| Leg shank thickness | **0.86 mm** |
| Gap between the two legs of a pair | **2.92 mm** - generous, so each leg is a long soft cantilever |
| Pair outer span, relaxed shank | **4.78 mm** (0.22 clearance in the hole) |
| Pair outer span at the barb | **6.38 mm** -> must squeeze **1.38 mm total**, 0.69 per side |
| Barb protrusion | **0.84 mm per side** |
| Barb lead-in ramp | ~45 deg, over y 0.4 -> 1.5 |
| Barb catch face | steep, y 1.5 -> 1.8 - a real undercut, not a taper |
| Shoulder face to barb catch | **3.1 mm** = the 3.0 mm plate plus a whisker |
| Leg pairs per holder | **2**, at **8.10 mm** pitch (one grid cell) |
| Holder width for a 2-pair mount | 15.000 mm, pairs at +/-4.05 from centre |

So: the legs drop into two adjacent holes, the barbs squeeze in, pass the 3 mm plate, and spring
out underneath while the shoulder seats on top. Nothing is crushed and nothing relies on
interference, which is why these parts survive repeated remounting.

### The orientation rule this implies
Holders are **prismatic through the leg zone** (the cross-section is constant from the base up to
the leg top at 4.90; above that the legs stop and the body continues to ~7.95). They are not pure
extrusions overall - roughly a third of the triangles are chamfers and pocket detail - but the
mount is.

Printed with that prismatic axis vertical:
* the legs are vertical walls - no overhang, no support;
* the barbs flare sideways, i.e. **within the layer plane**;
* the leg flexes in X, so its bending stress runs **along layers**, never across them.

That is the same conclusion we reached the hard way after shearing a lip (see the load-path
section in `design-for-fdm-printing.md`). The official system has it designed in from the start.

## Design implications
1. Drive the plate from `grid_x` / `grid_y`; size = `8 * n + 3` on each axis.
2. Holes are plain square through-cuts — printed flat, the hole axis is vertical, so no overhang,
   no bridge, nothing to design out. The only FDM concern is the first layer.
3. **Elephant foot closes holes.** A 5 mm hole with 0.5 mm of elephant foot becomes ~4.5 mm and
   the connector will not fit. Chamfer the bed-face edges of every hole (house rule:
   `design-for-fdm-printing.md`, first-layer chamfer 0.5 mm, applies to hole edges too).
4. **ABS shrinkage attacks the pitch.** At 0.5–0.7 %, 8 mm becomes ~7.95 mm — trivial per cell but
   **0.5 mm cumulative over 12 cells**, enough to misalign a multi-peg accessory at the far end.
   PLA (what the ecosystem is designed and printed in) is the safe choice; in ABS, calibrate
   shrink compensation first.
5. A 3 mm plate is thin and wide — a prime warping candidate in ABS. Rounded corners and mouse
   ears if printed in ABS.

## Sources
- Primary: direct mesh measurement of `MOD-GRID 4x12` and `MOD-GRID Modular connector v4`
  in the user's Fusion `MODGRID` folder, 2026-10-21.
- [MakerWorld — MOD-GRID (TinyToolShop / 3dedc)](https://makerworld.com/en/models/2811701-mod-grid)
- [MakerWorld — MOD GRID parametric base plate](https://makerworld.com/en/models/2871590-mod-grid-parametric-base-plate)
- [MakerWorld — Mod Grid Magnet Plates](https://makerworld.com/en/models/2822575-mod-grid-magnet-plates)
- [MakerWorld — 3dedc profile](https://makerworld.com/en/@3dedc)
- [MakerWorld — MOD-GRID holder for Wuben G5 (5 mm grid)](https://makerworld.com/en/models/3002494-mod-grid-holder-for-wuben-g5-5mm-grid)
- [YouTube — MOD-GRID: Modular EDC Organization](https://www.youtube.com/watch?v=Q-XCzn5icIo)
