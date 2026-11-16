# 10" (Mini) Rack — Standard Dimensions and 3D-Printed Frame Designs

Research captured 2026-10-19 before modelling a 6U 10" rack frame for printing in ABS on a Voron 2.4 (350 mm bed).

## The big caveat
**There is no published standard for the 10" rack.** EIA-310 / CEA-310 covers the 19" rack only. The 10" ("mini rack", "half rack") format borrows the 19" rack's *vertical* geometry exactly and uses a *de-facto* horizontal hole spacing that every serious source now agrees on. One vendor blog claims 254 mm hole spacing — that is wrong; 254 mm is the **panel width**, not the hole centres.

## Hard numbers

### Vertical (identical to 19", EIA-310)
| Dimension | Value |
|---|---|
| 1 rack unit (U) | **44.45 mm** (1.75 in) |
| Holes per U | **3** |
| Hole pitch within a U, bottom → top | **15.875, 15.875, 12.70 mm** (0.625, 0.625, 0.500 in) |
| Where the U boundary falls | **in the middle of the 12.70 mm gap** |
| ⇒ Hole centres measured from the bottom of a U | **6.35, 22.225, 38.10 mm** (0.25, 0.875, 1.50 in) |
| Next U's first hole | 44.45 + 6.35 = 50.80 mm (= 38.10 + 12.70 ✓) |
| 1U equipment panel height | **43.65 mm** (0.4 mm clearance top and bottom) |
| nU panel height | n × 44.45 − 0.8 mm |

### Horizontal (de-facto 10" convention)
| Dimension | Value | Note |
|---|---|---|
| Panel width including ears | **254.0 mm** (10 in) | This is what "10 inch" means |
| **Mounting hole centre-to-centre, left rail → right rail** | **236.525 mm** (9.312 in) | The number that decides fit. ±0.5 mm tolerance is normal |
| ⇒ Hole inset from each panel edge | (254 − 236.525)/2 = **8.7375 mm** | Mirrors the 19" rack exactly: (482.6 − 465.1)/2 = 8.75 mm |
| Rail face width | **15.875 mm** (0.625 in) | Same rail width as a 19" rack |
| Clear opening between rails | **≈ 222 mm** absolute max (8.75 in) | Lab Rax and DeskPi TL1 both quote 222 mm |
| Recommended usable width for gear | **≤ 210 mm** (8.45 in) | Project Mini Rack's planning figure |
| Panel width that drops between the rails | ~249 mm | e.g. 3drackmounts' panels; 254 mm is ears-outside-the-rails style |

### Depth — no standard at all
Most 10" racks are **200–300 mm** deep; few exceed 300 mm.
| Rack | Depth |
|---|---|
| DeskPi RackMate T1 | 200 mm (212 mm internal) |
| DeskPi RackMate T1 Plus / T2 | 260 mm |
| DeskPi RackMate TL1 | 272 mm external |
| Mac Pierce T-slot build | 1" extrusion posts 12" long for 6U |

### Fasteners
| Option | Detail |
|---|---|
| **M6** | What almost every 3D-printed 10" rack system uses (Lab Rax picked M6 for availability in EU/Asia/AU). M6×10 button head into brass heat-set inserts |
| #10-32 / #12-24 | The 19"-world threaded-rail sizes; some 10" gear ships with these |
| Square cage-nut slot | **9.5 × 9.5 mm**. Used by 3drackmounts' own rack |
| Printed-hole float | ~0.3 mm clearance per hole on panels is normal |

Mixed hardware is the reality of this format: most mini-rack gear ships with M6 or #10-32 and the two are close enough that an M6 clearance hole takes both.

## 6U arithmetic for our build
- Mounting height 6 × 44.45 = **266.70 mm**
- 18 hole positions per rail (3 per U), first at 6.35 mm above the bottom U boundary
- Post length ≈ 267 mm + top/bottom margins → **~280–300 mm**: fits a 350 mm Voron bed lying flat with lots of room

## Existing 3D-printed 10" frames reviewed
| Design | Construction | Notes |
|---|---|---|
| **Lab Rax** (The DIY Life) | Fully printed. 4 posts (1U–5U sections) + 4 edge pieces + 4 horizontals + feet/handles, every joint **one M6×10 button head into an 8 mm OD brass insert**. Slide-in side/top panels. | Designed for a 250 mm bed, so it is split more than we need. 5U frame ≈ 10 plates / 26 h. Post strength limits it to ~10U. Insert holes 5.5 mm deep → use 4–5 mm inserts, not 6 mm |
| **Mac Pierce 10" mini rack** | 4 × 1" T-slot extrusion posts (12" long for 6U), printed top/bottom plates, **16 printed 1U rack ears** on end-feed T-nuts, 3 × M5 heat-set inserts per ear | Strongest option, but needs extrusion + tapping 1/4-20 |
| **MackRack** (Thingiverse) | 2020 extrusion + printed corners, offered 4U/6U/8U | |
| **jaytkay 10" Rack 6U** (Printables) | Fully printed, **M5 bolts threaded straight into the plastic**, no supports needed | Simplest possible approach |
| **Parametric generators** (MakerWorld CXDESIGNS; vrsn3ptoh FreeCAD) | Script-driven, 0.5 mm tolerance recommended | Licences restrict derivatives — reference only, don't copy geometry |
| **HomeRacker, MiniRax, LabStack mini, bwees** | Listed by Project Mini Rack without endorsement | |

## Design implications for our model
1. Drive everything from `rack_u` (default 6). Mounting height = `rack_u × 44.45`.
2. Hole grid: for u in 0..rack_u−1, hole centres at `u×44.45 + {6.35, 22.225, 38.10}` above the bottom U boundary, on both rails at ±118.2625 mm from the centre plane.
3. Keep ≥ 222 mm clear between the inner faces of the rails, and keep nothing (screw bosses, gussets, panel rails) intruding into the 210 mm × full-height equipment envelope at the front.
4. Posts print lying flat on the bed — the hole axes then run **horizontally in the print frame**, so every rail hole must be a **teardrop** (point up) per `design-for-fdm-printing.md`, or the holes must face up in the print orientation.
5. ABS shrinkage 0.5–0.7 % over 266.7 mm is ~1.5 mm. **The 236.525 mm hole spacing must be held to ±0.5 mm**, so slicer shrink compensation matters more here than on any part we've printed so far — or the rails get slotted holes.

## Sources
- [Project MINI RACK — Jeff Geerling](https://mini-rack.jeffgeerling.com/)
- [Computing for Geeks — 10-Inch Rack Homelab: Mini Rack Build, Dimensions and NAS Fit](https://computingforgeeks.com/build-10-inch-mini-rack-homelab/)
- [3DRackMounts — 10 Inch Rack Dimensions and Hole Spacing (four-layers.com)](https://four-layers.com/blogs/guides/10-inch-rack-dimensions-every-measurement-that-matters)
- [Micropolis — Rack Mounting FAQ](https://www.micropolis.com/support/kb/rack-mounting-faq)
- [Wikipedia — Rack unit](https://en.wikipedia.org/wiki/Rack_unit)
- [Wikipedia — 19-inch rack](https://en.wikipedia.org/wiki/19-inch_rack)
- [AudioRax — Rack Rail Hole Spacing Explained](https://www.audiorax.com/rack-rail-hole-spacing-explained)
- [The DIY Life — Introducing Lab Rax: A 3D Printable & Modular 10" Rack System](https://the-diy-life.com/introducing-lab-rax-a-3d-printable-modular-10-rack-system/)
- [Mac Pierce — DIY 10" Mini rack using T-slot extrusion + 3D prints](https://www.macpierce.com/blog/2025/8/11/10in-mini-rack)
- [DeskPi RackMate T1 wiki](https://wiki.deskpi.com/rackmate/rackmate-t1/)
- [MakerWorld — Parametric 10 & 6 Inch Mini Rack Generator](https://makerworld.com/en/models/2323552-parametric-10-6-inch-mini-rack-generator)
- [Printables — 10" Rack 6U by jaytkay](https://www.printables.com/model/1380527-10-rack-6u)
- [Thingiverse — MackRack](https://www.thingiverse.com/thing:6983101)
