# Design for FDM Printing — Designing Out Slicer Supports

Research captured 2026-09-30 while preparing the **RPI shelf** (1U 10" mini-rack shelf for 2× Raspberry Pi 5 + 52Pi adapters) for printing in Polymaker ABS on a Voron 2.4 (350 mm), 0.4 mm nozzle.

Goal: fix printability problems **in the CAD model**, not in the slicer. Slicer "supports" setting should be able to stay **off**.

## Core philosophy (Slant 3D)

1. **Design the overhang out first.** Most support needs can be removed by changing geometry: chamfers instead of flat ledges or fillets, teardrop holes, choosing the print orientation up front.
2. **When a support is unavoidable, model it yourself** as a thin fin that touches the part through tiny "sprue" contacts, so it snaps off cleanly and uses far less material and time than auto-generated supports.
3. **Design for the first layer** — chamfer bed-contact edges so elephant-foot doesn't ruin fits.

## Rules and numbers

### Overhangs
| Rule | Value |
|---|---|
| Self-supporting overhang | ≤ 45° from vertical |
| Chamfer vs fillet on a downward-facing edge | **Chamfer.** A fillet's overhang angle keeps increasing toward horizontal and eventually needs support; a 45° chamfer stays constant. Fillets are fine on vertical edges and upward-facing edges. |
| Flat ceiling / ledge | Not self-supporting — redesign (45° chamfer, wedge, or teardrop) |

### Bridges
| Rule | Value |
|---|---|
| Bridge anchored on both ends | OK up to ~10–15 mm |
| Cantilever (anchored one end) | Treat as an overhang — not OK when flat |
| Longer bridges | Slant says most machines bridge 25–50 mm. We keep ≤ 10–15 mm for ABS unless test-printed. Beyond that, use a designed bridge block (0.2 mm top / 0.2–0.3 mm bottom clearance, crush-hole, "SUPPORT" label). See `slant3d-designed-supports.md`. |

### Holes and pins
- **Horizontal holes:** use a **teardrop** — round bottom, two 45° lines meeting in a point on top. Prints in any orientation with no support.
- **Horizontal pins/pegs:** same teardrop, **point down**. The 45° flanks are self-supporting; the tip line still cantilevers, so give it a designed-in fin (see below). Truncate the tip to a ~0.4 mm flat so the sprue has something to land on.
- A pin that mates into a hole must have a matching teardrop hole (hole = pin profile offset by the clearance).
- **Sacrificial bridge layer** (alternative for counterbored/stepped holes): model a one-layer-thick membrane across the hole so the printer bridges it first; drill/poke out afterward.

### Designed-in support fins (Slant 3D style)
| Parameter | Value | Notes |
|---|---|---|
| Fin thickness | 0.8–1.2 mm | 2–3 perimeters at 0.4 mm nozzle; snaps cleanly. ~2 mm on large or tall parts (Shop Therapy: 2 mm fin, 1×1 mm sprues, 230 mm part) |
| Sprue contact width | 0.2–0.4 mm | 0.2 barely connects; 0.3–0.4 is more reliable. Slant: side-tied sprues ~0.5 mm tall × 0.5–1 mm wide; comb/thumbtack sprues 1 mm |
| Sprue taper | 45° from fin body down to the contact ridge | keeps the fin itself self-supporting |
| Z-gap alternative (no contact) | exactly one layer height (0.2 mm at 0.2 mm layers) | first part layer droops onto the support and releases. **Use only under a narrow tip, never under a broad flat face** — see below |
| XY clearance from part walls | 0.4–0.8 mm | prevents fusing to vertical walls. Slant's video: fin-to-part gap 0.5–1 mm; Shop Therapy used 1 mm |
| Fin base | slightly wider foot than top | prevents mid-print tip-over on tall fins |
| Stacking | a fin may stand on a lower part feature via its own sprue | used for the upper pin on the shelf |
| Sprue direction | **horizontal in the print frame** (parallel to bed), never perpendicular to a tilted face. Perpendicular tines print as isolated tips that snap off and blob. | Slant: "You Don't Use Fins Enough" |
| Break notch | small notch in each sprue next to the part so it snaps flush | Slant video |
| Fin height / count | ≥ ½ (ideally ¾) of the supported face. Use several fins on large parts. | Shop Therapy: 1 fin on 230 mm wobbled |
| Fin foot | flat plate on the bed, rounded corners, chamfer gusset at the fin root | Shop Therapy: 1 mm plate, 20 mm fillets, 2×10 mm chamfer |

**The Z-gap trick does not scale to a broad flat face (added 2026-10-21).** Orca flagged the
MOD-GRID pen clip as having a floating layer, and it was right: a 0.2 mm gap under a
5.26 x 5.0 mm peg underside makes that whole face an island printed into air, relying on droop.
Every body did reach the bed — the warning was about the part's own first layer over the gap, not
about grounding. Two further problems: the gap only equals one layer if it happens to land on the
layer grid (at 0.25 mm layers the same model gave zero empty layers, at 0.20 it gave one), and a
slicer's static check will flag it regardless.

Under a broad flat face, **make the support touch** instead:
| Rule | Value |
|---|---|
| Contact | two narrow ridges at the supported face's edges, overlapping the part ~0.05 mm |
| Ridge width | 0.6 mm — small enough to snap, wide enough for the slicer to keep |
| Ridge spacing | leave a span the printer can bridge; 3.6 mm used here |
| Overhang outboard of the ridges | keep ≤ ~0.3 mm |
| Where to land the ridges | on a non-critical face, and prefer the edges over the middle so marks sit near corners |

Modelling approach used in Fusion:
- Fins are **separate bodies** named `Support - …` so they're visible and easy to hide.
- Each fin overlaps the part by ~0.05 mm at the sprue ridge so the slicer treats it as connected.
- **Export the part and its support bodies together** as one STL/3MF so the slicer unions them.
- Exclude support bodies from assembly interference checks.

### First layer / elephant foot
- Chamfer every edge that touches the bed by **0.5–1 mm** (0.5 mm used on the shelf).
- Applies to hole and cutout edges on the bed face as well as the outer perimeter.
- Keep narrow bed-level slots **≥ 1.0 mm** so elephant foot can't close them.

### Orientation and strength
- Put the largest flat face on the bed.
- Layer lines are the weak direction — orient parts so bending/shear loads run **along** layers, not across them. Horizontal pins printed lying down are stronger than vertical pins.
- Slant 3D also prints enclosures at 45° (corner down) for strength and auto-eject, with a fin support on the back — useful for mass production, not needed for one-offs.
- Round vertical edges for cleaner toolpaths; texture outer faces to hide layer lines (optional).

#### Peg-in-hole fits: the printer's bias compounds, so compensate at both ends (2026-10-23)
Legs copied dimension-for-dimension from a working official part still crushed on insertion. The
cause was not the design: a **5.00 mm modelled hole printed 4.86** - 0.07 mm per wall undersize.

| | Modelled | In a 4.86 printed hole |
|---|---|---|
| Leg length 4.90 | 0.10 clearance | **-0.04 interference** |
| Shank span 4.78 | 0.22 clearance | 0.08, effectively nothing |

**Holes shrink and external features grow by the same bias, so a peg-in-hole fit sees it twice.**
Compensating only one side leaves half the error. Fix both: enlarge the modelled hole by the bias
per side (which also makes the part correct for anybody else's accessory), and shrink the modelled
peg by the full bias.

**Do not apply the compensation to an elastic feature.** The barb is meant to squeeze; shrinking it
along with the shank would have cut retention for no benefit. Compensate the parts that must
clear - the shank and the length - and leave the spring alone.

Measure one printed hole before trusting any press-fit dimension. It is one caliper reading and it
turns three guesses into arithmetic.

#### Flexures: what actually broke one (2026-10-24, and this REPLACES the version written earlier the same day)

The prybar clip's arms **snapped on the first insertion**. The first diagnosis written here blamed bending stress along the arm, concluded that ABS only delivers 17.5 MPa in this application, and told the next person to make flexures **thinner** to stay under it. That advice was then applied to the Zippo band and made it measurably worse. Both the diagnosis and the advice were wrong, and this is what actually happened.

**The arm tore out at its ANCHORAGE.** A Measure between two faces in Fusion found the relief slot's rounded root cap sitting **0.016 mm** from the bed chamfer on the Zippo band. Checking the prybar the same way gave **0.162 mm** on the version that broke. Neither part had an arm problem; both had no root.

| part | root web after the bed chamfer | outcome |
|---|---|---|
| prybar clip v1 (1.2 arm, wrap -130) | **0.162 mm** | **snapped on first insertion** |
| prybar clip v2 (1.6 arm, wrap -115) | 0.847 mm | thin, not yet failed |
| Zippo band (1.6 arm, wrap -135) | **0.016 mm** | never printed; caught by Measure |
| both, rebuilt (tapered, wrap -110/-115) | **1.57-2.00 mm** | current |

**Why nothing caught it.** The script *had* a web check. It walked down from the slot toward the bed, found 3.28 mm, and passed - a true number about the wrong piece of material. The anchorage is **above** the cap, between it and the cavity floor, and the first-layer chamfer cuts into exactly that. An analytic probe only looks where you point it.

> **Measure the neighbourhood of a flexure on the real faces.** `measure_root_web()` takes the slot's root cap and runs `measureMinimumDistance` against every other face of the body, then classifies each result by direction: **ABOVE** the cap = the anchorage into the base (want >= 1.5 mm), **BELOW** = material down to the bed face (>= 1.2), **BESIDE** = usually the opposite slot, i.e. the column between the two (>= 1.2). It finds the narrowest place whatever the cause, including causes nobody thought of.

**The geometry that destroys the web.** Up to -90 deg the relief slot runs at a constant offset from the cavity corner, so the root web simply *is* the arm thickness. Past -90 the cap tucks under the cavity floor and the nearest cavity surface becomes the **floor plane**:

    web = -cav_r - (cav_r + arm_root + relief_w/2) * sin(th0) - relief_w/2

and it falls away fast: on the Zippo, 2.80 mm at -90, 2.50 at -110, 1.08 at -135. **It does not contain `base_t`** - the floor and the slot rise together - so the old advice to "raise the surrounding geometry" does nothing for it. Only a shallower wrap or a thicker root helps. Deepening the wrap buys arm length and spends root web; that is the real trade, and it has a hard stop (at -150 the Zippo slot cut clean through the floor and split the band into pieces while the timeline still reported 0 unhealthy).

**What replaces the 17.5 MPa ceiling.** Nothing was measured at 17.5 MPa; a part with a 0.16 mm ligament failed and the number was back-fitted to it. The limit now comes from the material. These arms flex **within** the layer plane (both parts print standing on an end face) and are >= 4 perimeters with no gap-fill bond line down the middle, so the across-layer knockdown does not apply: ABS in-plane yield ~40 MPa, 2.5x design factor, **15 MPa**. Evaluate it **as printed**: cavities come out ~0.07/wall under, so the bead reaches further in than modelled and the arm flexes ~0.07 mm more than drawn. The working pen clip computes ~9 MPa by this method.

**TAPER the arm - thick at the root, thinner at the tip.** The bending moment is `F x (bead_z - z)`: largest at the root, zero at the bead. A constant section is therefore overstressed at one end and wasted at the other. Taper it and a second thing falls out for free: a thicker root pushes the relief slot outboard, which is precisely what thickens the root web. One change fixes the stress distribution and the anchorage together. Build it by sloping the slot's **inner** edge inboard over a blend height while its outer edge stays vertical - the rail keeps a constant thickness and the slot just gets wider further up, which costs nothing.

**Do not thin an arm to buy bead reach.** The reach *is* the deflection, so it belongs in the stress budget as an input, not maximised as an output. A stiff, thick, properly anchored arm with a modest reach beats a thin arm with a deep one, by a lot:

| Zippo band | arm | reach | root web | stress as printed | pull-out |
|---|---|---|---|---|---|
| the version this rule replaced | 1.60 flat | 0.98 | **0.016 mm** | 14.8 MPa | 1.3 kg |
| current | **2.80 -> 2.00 taper** | 0.60 | **2.00 mm** | 13.8 MPa | **6.3 kg** |

| prybar clip | arm | reach | root web | stress as printed | pull-out |
|---|---|---|---|---|---|
| v1, snapped | 1.20 flat | 0.70 | **0.162 mm** | - | - |
| current | **2.40 -> 1.60 taper** | 0.15 | **1.57 mm** | 14.6 MPa | **8.5 kg** |

**A flexure wall must be an integer multiple of the extrusion width, and at least 4 of them.** This part of the old rule stands. 1.2 mm at a 0.4 nozzle is 2.86 extrusions, so the slicer lays 2 perimeters plus a sliver of gap fill **down the middle of the flexure** - a bond line where bending stress peaks. Use 1.6 (4), 2.0 (5), 2.4 (6), 2.8 (7). Quote wall thicknesses in extrusions, not millimetres.

**Clearances on a sliding fit need the printer bias added, every time.** The prybar's nose pocket was modelled at 0.20 mm over the wedge; cavities print ~0.14 under on this printer, leaving 0.06, and it would not go in. For a surface that slides along its mate, start from 0.5 mm modelled.

#### Bias the FLEXURE'S OWN THICKNESS for the printer, not just its deflection (2026-10-26)

`flexure_check` had been adding the printer bias to the deflection only - cavities print about
0.07 mm/wall under, so a capture lip reaches further inboard than modelled and the arm flexes
further. True, and half the story.

**The arm is bounded by the cavity on one side and the relief slot on the other. Both are voids.
Both print inward. So the arm itself comes out `2 x 0.07 = 0.14 mm` THICKER than modelled.**

For a deflection imposed by geometry (which is what a snap does):

        sigma = 3 * E * delta * t / (2 * L^2)        stress scales with t
        F     = E * b * t^3 * delta / (4 * L^3)      force  scales with t^3

so a 1.60 mm arm printing at 1.74 is 9% more stressed and 28% stiffer. Across the three current
parts, correcting it cost about 5% on stress and 20% on force:

| part | modelled | as printed, deflection only | as printed, deflection AND thickness |
|---|---|---|---|
| prybar clip | 10.0 MPa | 14.6 (97%) | **15.7 MPa (105%) - over** |
| Zippo band | 12.8 MPa | 14.3 (95%) | **15.2 (102%) - over**, cut to 14.2 at lip_over 0.55 |
| Skeletool band | 12.1 MPa | 13.6 (91%) | 14.2 (94%) |

Two things follow:

1. **Any wall bounded by two cut features gets the bias twice, with the sign that makes it
   thicker.** A wall bounded by a cut on one side and the part's outside on the other gets it
   once. A free-standing rib gets it the other way and comes out thin. Work out which case you
   are in before trusting a wall thickness.
2. **Suspect this first when a part computes comfortably but is too stiff to assemble by hand.**
   Insertion force is the `t^3` term, so it is where the error shows up largest - a flexure that
   is 9% thicker than drawn needs 28% more force to snap together, and that is the difference
   between a firm press and "it will not go in".

#### Insertion force is the SPLAY times the STIFFNESS, and it is the thing the user feels (2026-10-26)

Two parts came back from printing with the same verdict in plain language: *"there is no way
this pry bar will fit into the holder"* and *"the Zippo still pops the lighter out so it doesn't
sit flat"*, followed by **"stop worrying about tension, and make the parts fit."**

Both had been signed off on numbers that looked good - stress at 95-105 % of limit, interference
clear, root web sound, sticky zone zero. None of those numbers is what a person feels. What they
feel is:

        insertion force  =  2 * k * (lip_over + PRINT_BIAS)

and `k` had quietly been maximised, because every previous fix spent its budget buying retention.
The prybar needed **56 N** to press a 6 mm bar between two 12 mm arms. That is both thumbs, hard,
on a part with nothing to grip.

| part | was | now | what changed |
|---|---|---|---|
| prybar clip | 56 N push, 10.2 kg pull | **35 N push, 6.4 kg pull** | `lip_over` 0.15 -> 0.08, `arm_blend` 3.0 -> 1.5 |
| Zippo band | 41 N push, 7.5 kg pull | **29 N push, 5.3 kg pull** | `lip_over` 0.55 -> 0.40 |
| Skeletool band | 31 N push, 5.8 kg pull | **23 N push, 4.3 kg pull** | `lip_over` 0.55 -> 0.45 |

The retention that was given up was never needed. These hold a 35 g bar, a 65 g lighter and a
142 g tool; 4.3 kg is **thirty times** the heaviest of them. Stress fell to 69-77 % of limit as a
free side effect, because the splay is the deflection.

**Rules:**
1. **Budget the insertion force explicitly, next to the stress.** Aim for ~25-35 N total on a
   part held in two fingers. Print the push force in the same line as the pull force so the trade
   is visible when it is being made, not after a print.
2. **Retention is a RATIO, not a number.** State it as multiples of the part's weight. Anything
   past ~20x is being bought with the user's thumbs.
3. **Seated clearance on a capture lip needs real margin, not the printer bias.** The Zippo lip
   stood `lip_clear` 0.10 off the case, which the 0.07/wall bias cut to 0.05 - so any error in
   the part's THICKNESS, in `base_t`, or in the corner radius put the lip back onto the part and
   held it proud. 0.40-0.60 absorbs 0.6-0.9 mm of vertical error and costs only free lift, which
   nobody complains about. **Size `lip_clear` from how well the part is MEASURED**: 0.40 on the
   caliper-checked Zippo, 0.60 on the Skeletool whose thickness is still a published spec.
4. **When a part comes back "it doesn't fit", open every clearance and cut the reach in one
   pass.** Do not re-derive the mechanism first. The clearances are cheap, reversible and they
   cover more than one candidate cause at once; a clever mechanism that is 0.05 mm from touching
   is not a design, it is a coin toss.

#### A face picked by RADIUS alone will find the wrong face (2026-10-26)

`measure_root_web()` collects the relief slot's root caps as "every cylindrical face whose radius
is within 0.05 of `relief_w / 2`". Cutting the prybar's `lip_over` to 0.08 made `bead_r` 0.58
against a `relief_w / 2` of 0.60 - so the **capture bead** was measured as a slot cap and the
build reported `root web ABOVE cap: 0.300 mm ** THE ARM HANGS OFF THIS **` on a part whose root
web was a healthy 1.572. A real alarm on imaginary geometry is as expensive as no alarm.

> **Identify a face by radius AND position.** The slot caps are the only cylinders of that radius
> *below the cavity floor*, so one `origin.z < base_t` test disambiguates them permanently. Any
> check that selects geometry by a single scalar property will eventually select something else
> that happens to share it.

#### "Loose" is a direction, and nobody says which one (2026-10-28)

The MOD-GRID Olight band was reported loose **four times**. Three fixes went in between
them, each defensible, each measured, each reported as an improvement:

| # | what was changed | what it moved |
|---|---|---|
| 1 | `cav_clear` 1.00 -> 0.40 | bore 15.96 -> 15.36 printed |
| 2 | `lip_clear` 0.50 -> 0.30 | nothing real (see the clearance rule above) |
| 3 | `lip_z0` derivation fixed, `lip_clear` 0.25 | free lift 1.52 -> 0.54 mm |

All three are **radial**. The complaint was **axial**: the light snapped in correctly and then
slid along its own axis through the band. Not one of the three fixes resisted that by a single
newton, which is exactly why the fourth report said *"it still feels the same as the previous
2 iterations."*

> **"It's loose" names a symptom, not a direction. Ask which one before changing anything:
> does it rattle across, lift out, slide along, or fall out under load?** Those are four
> different defects with four different fixes, and three of them are invisible to the checks
> written for the fourth. One question at report #1 would have saved three prints.

**And the structural fact underneath it.** A band grips radially, and these bands are designed
so the arms are *unloaded* when the part is seated - that is deliberate, because a permanently
splayed arm creeps in ABS. The direct consequence is that **there is almost no friction along
the axis**: the part is free to slide until something physically blocks it. Every band-style
holder needs an axial stop as a separate, explicit feature. The Zippo got a C-stop at its bed
face; the Olight was built without one and nobody noticed, because no check was looking along
the axis.

#### Measure EVERY diameter of a stepped part, and then the step is free (2026-10-28)

The same holder had a second defect the same report uncovered. The light had been modelled as
one 15.10 cylinder for its whole 55 mm, from a measurement that was real - but was of the
**keyring cap only**. Put a caliper on the body and it is **13.25**.

Two things follow, and the first one is worse than it sounds:

1. **The cradle band had never touched the light.** It was bored for 15.10 and sunk to match a
   15.10 part, so a 13.25 body sat **0.93 mm clear of it at every point**. One of the two
   bands in a two-band holder was decorative, and the interference check said CLEAR at every
   lift height - correctly, against a reference body that did not exist. **A reference model
   built from one measurement of a multi-piece part will confirm whatever you assumed.**
2. **The step is a ready-made axial stop, and it costs nothing to use.** Bore the second band
   for the SMALLER section, put its **bed face** at the step, and the part's own shoulder
   lands on it. Here that is 0.76-0.92 mm of radial engagement over 160 deg of arc, measured
   on the solid - the part's whole weight carried on a face instead of on friction.

> Prefer a stop made of **a face the part already has** over one you add. It needs no
> clearance budget, no overhang, no extra feature, and it cannot be eaten by a fillet.

**Three traps in doing it this way, all of which bit here:**

- **Do not chamfer the stop face's inner edge.** The first-layer chamfer would take 0.50 of a
  0.76 mm engagement - the same rule as "do not chamfer the hole a snap barb catches under".
  Leave that edge sharp; elephant foot there *adds* material to the stop, and the part drops
  in radially so a tight mouth costs nothing.
- **A longer band does not get a second row of mount legs.** The second row would sit a whole
  number of grid cells along, which is correct on the plate and wrong in the printer: the band
  stands on its bed face, so a row 16 mm along begins 16 mm **up** the print as an island in
  mid-air. One row at the bed face, however long the band.
- **Check how much of the grip band actually lands on the gripped section.** The band is where
  the grid pitch puts it; the step is where the part puts it. They do not have to agree, and
  the overlap is what the flexure numbers are really computed on.

#### A clearance derived against an INFINITE face is not the clearance you built (2026-10-28)

The MOD-GRID Olight band came back loose three times. The first two fixes were both
reasonable and both missed: `cav_clear` 1.00 -> 0.40 (bore down to 0.13 mm per side as
printed, as tight as the proven Zippo band) and `lip_clear` 0.50 -> 0.30. The third report
was the same word - **"still too loose"** - which is the signal that the number being
adjusted is not the number that is wrong.

It was not the bore. It was **1.52 mm of vertical play**: the cap could lift that far before
the capture lip touched it, on a band only 12 mm tall. And `lip_clear` said 0.30.

**The derivation was exact for geometry that is not there.** The lip's underside is the line
`y + z = K`, and `lip_z0` was solved so that line stands `lip_clear` off the seated cylinder.
That is correct arithmetic about an **infinite 45 deg plane**. The real lip is `lip_proj`
tall - **0.72 mm** - and it sits well below the point where that line touches the cylinder,
which is the part's own 45 deg point at `z = part_z + 0.707 * D/2`. The part never reaches
the face the clearance was measured on. Its actual closest approach is to the lip's **tip
radius**, and that stood **0.67 mm** off a part the parameter claimed was 0.30 away.

| | parameter said | lip tip really stood off | free lift |
|---|---|---|---|
| Olight band, as printed twice | 0.30 | **0.67** | **1.52 mm** |
| same lip_clear, placed off the tip radius | 0.30 | 0.30 | 0.68 mm |
| shipped (lip_clear 0.25) | 0.25 | 0.25 | **0.54 mm** |

**Free lift goes as the SQUARE ROOT of the clearance**, because near contact the cylinder's
surface runs almost parallel to the direction it is being lifted. So 2.2x the clearance was
2.8x the lift, and tenths of a millimetre of modelling error came out as a millimetre and a
half of rattle. That ratio is why this hid for so long: every number in the build log was
small and plausible.

**The fix is a closed form against the feature that exists.** Put the tip-radius CENTRE at
`R + clear + tipr` from the seated axis:

        lip_zt = part_z + sqrt( (D/2 + clear + tipr)^2 - lip_cy^2 )

valid as long as the arc's closest normal (~23 deg here) lies inside the +/-45 deg the tip
radius spans - check that, do not assume it. It is no harder than the formula it replaces and
it measures the thing the part touches.

Three rules, and the last is the one that would have caught it:

1. **When you simplify a feature to a line or a plane to derive a clearance, check that the
   contact point lands on the part of it you actually built.** A 0.72 mm face is not a plane.
   The giveaway is a derivation that never mentions the feature's extent.
2. **A clearance parameter must be verified against the model, not just fed into it.**
   `seat_check()` had been printing the real gap - 0.70 mm - in the same block as the 0.30
   it was supposed to be, for three revisions. Nothing compared them, so nobody read them as
   a pair. The script now measures the gap off the profile and asserts it equals `lip_clear`.
3. **Measure the check in the direction the parameter is defined in.** The first version of
   that assertion compared `lip_clear` against a HORIZONTAL gap and fired a false alarm on
   the pill holder, where the contact sits at 30 deg and the two differ by `1/cos`. A guard
   that is 15% out is a guard that gets switched off.

**And the process rule.** "Still too loose", twice, after two defensible tightenings, means
stop turning the knob and go and measure what the part is actually touching. The first two
changes were not wasted - the bore genuinely needed them - but neither was ever going to fix
a defect in the derivation.

#### A RETENTION FEATURE MUST BE AT LEAST ONE EXTRUSION WIDTH DEEP (2026-10-28)

The Olight band was reported loose five times. Four fixes went in - the bore, `lip_clear`
twice, the `lip_z0` derivation - and the fifth report was *"still super loose. Not retained
at all."* Then Rob put calipers across the printed band's opening:

| | modelled | printed, predicted | printed, MEASURED |
|---|---|---|---|
| bore | 15.50 | 15.36 | - |
| throat at the lip tips | 14.40 | 14.26 | **15.34** |

**The throat WAS the bore. The lip had never printed, in any of the five prints.** A 15.10
cap dropped through a 15.34 opening with a quarter millimetre to spare, which is exactly
"not retained at all", and every tightening had been applied to a bore that was not the
problem.

`lip_over` was **0.35 mm** - *smaller than one extrusion width, and smaller than `lip_tipr`
(0.40)*. So the two 45 deg faces never existed at all: the whole feature was a 0.35 x 0.72
bump, under one bead in both directions, and the slicer dropped it.

> **A feature that has to do mechanical work must be at least one extrusion width in its
> working dimension, and two to print crisply.** The project already applied this to arm
> thickness ("4 perimeters minimum") and to the lip's TIP RADIUS ("one nozzle width - a
> knife edge will not print"). It was never applied to the lip's **reach**, which is the
> dimension that actually retains the part. **Check `lip_over >= 2 * extrusion_width`, and
> assert `lip_over > lip_tipr`** - a lip that reaches less far than its own tip rounding is
> not a lip, it is a bump, and that comparison is two numbers.

**Where the bad numbers came from.** The 2026-10-26 "FIT FIRST" pass cut every reach in the
project to bring insertion forces down - prybar 0.15 -> **0.08**, Zippo 0.55 -> 0.40,
Skeletool 0.55 -> 0.45, round 0.50 -> 0.35. Insertion force was the right thing to fix and
the fix worked, but nothing checked the reaches against the printer's resolution on the way
down, so the retention was being traded against a limit nobody had written down.

**Why three of the four still work.** Rob's verdict on the set was *"the prybar is a super
tight fit, the pill bottle is a super tight fit, the pen is a super tight fit... the
flashlight has never been right."* The difference is not the reach, it is **what sets the
printed SIZE of the capture feature**:

| part | capture | printed size | reach | holds? |
|---|---|---|---|---|
| prybar | tangent bead, radius `cav_hw - lip_tip_y` | **1.08 mm** | 0.08 | yes |
| pen | constant 2.00 mm arc | **2.00 mm** | - | yes |
| pill bottle | lip does not print either - it grips by its **BORE** | - | 0.35 | yes |
| Olight | 45/45 lip, size IS `lip_over` | **0.35 mm** | 0.35 | **no** |

> **Prefer a capture whose printed size comes from the CAVITY rather than from the reach.**
> A tangent bead of radius `cav_hw - lip_tip_y` grows as the cavity opens, so it stays
> printable at any reach - which is why the prybar holds a 6 mm bar on 0.08 mm of bite. A
> 45/45 lip's only dimension is the reach, so it is the one shape where a small reach means
> no feature at all. The two are not interchangeable and the difference is invisible in a
> section view.

#### A LIP ON A CYLINDER IS HELD BY FRICTION, NOT BY THE SPRING (2026-10-28)

Found while hunting the above. `pull = 2 * F * 1.8` had been the pull-out model for every
band in the project. 1.8 is the wedge factor of a 45 deg face with friction - right for a
lip riding over a flat or a small corner, and badly wrong on a cylinder.

**On a cylinder the escape ramp is set by the PART, not by the lip's face.** The lip tip
radius is 0.40 and the cap's radius is 7.55, so the contact is governed by the cylinder, and
a cylinder near its equator is a nearly vertical wall - a nearly HORIZONTAL ramp for this
purpose. With the lip tip at radius `y_t` and the part radius `R`:

        splay  s(u) = sqrt(R^2 - u^2) - y_t        u = height of the tip above the axis
        ramp   ds/dh = u / sqrt(R^2 - u^2)
        travel u0 = sqrt(R^2 - y_t^2)              seated-to-free lift
        F(u)  = 2*k*s*(ds/dh + mu) / (1 - mu*ds/dh)

At `lip_over` 0.35 that ramp ran from **18 deg at first touch down to 0 at release** - at or
under arctan(mu) for the whole stroke - so the part was held by friction, and the resistance
**died away exactly as it got closest to escaping**. Peak 11 N, not the 52 N on record: the
old model was **4.8x optimistic**, and about 3.6x optimistic on the Zippo.

| | old model | real peak | travel |
|---|---|---|---|
| Olight, lip_over 0.35 | 52 N | **11 N** | 2.5 mm |
| Olight, lip_over 0.80 | 99 N | **22 N**, ramp starts at 28 deg | 3.5 mm |
| Zippo corner R2.8 | 52 N | **14 N** | 1.6 mm |

Two things worth carrying forward. **Pull-out on a smooth cylinder is only ~0.4x the press
force, whatever the clearances are** - so a light press and a firm hold are mutually
exclusive there, and no amount of `cav_clear` or `lip_clear` moves the ratio. And **the
travel is geometry**: `sqrt(R^2 - y_t^2)` is 2.5-3.5 mm on a 15 mm part, so a cylinder
holder always feels like it moves before it bites. Shrinking the travel means shrinking the
reach, which is the one thing that must not shrink. `escape_curve()` in
`modgrid_round_holder.py` computes all of it and prints the ramp angle beside the force.

#### A SECOND BAND ON A DIFFERENT DIAMETER IS A SECOND PART, NOT A COPY (2026-11-16)

The Olight holder was reported as not holding in a trouser pocket. The diagnosis was quick for
once, because the defect was by design: **Band B was an open cradle with no capture lip and its
walls stopping below the body's equator, so it had ZERO radial retention.** The cradle existed
to let the body lift straight off its magnetic cap (see the section below), and in a pocket that
is indistinguishable from the light falling out. Worse, the light switches on as it separates,
so a loose body means **the torch can come on in your pocket** - the failure nobody had ranked.

Converting it into a real snap band produced four lessons that have nothing to do with
flashlights.

**1. Two bands on two diameters need two parameter sets.** Every lip dimension in that script
derived from one `grip_d`. Band A grips the cap (15.10) and Band B the body (13.25), so sharing
the set would have bored Band B 1.85 mm oversize - which is exactly the rev D defect, where a
band sized for a diameter the part does not have at that station **touched nothing at all for
three revisions while the interference check said CLEAR**. The fix is a suffixed set
(`grip_d_b`, `cav_r_b`, `lip_z0_b`, …) with every default pointing at Band A's value, so a
one-piece part builds bit-identically and a stepped one states its second section explicitly.

> **And the axis has to be SOLVED, not inherited.** A part rests at the bottom of a bore larger
> than itself, so a band gripping a *smaller* section needs its bore centre *higher* to hold the
> part on the same axis: `bore_z_b = part_z + cav_r_b - grip_d_b/2`. Get it wrong and the part
> rocks between the two bands. Assert it - the check is one line and it prints both axes.

**2. The exceptions a special case carries are the reasons it was special.** The cradle had its
own builder, which deliberately left its channel mouth **unchamfered**, because a 0.50 mm bed
chamfer eats most of a 0.86 mm axial stop. Routing the new snap band through the generic builder
silently reinstated that chamfer - and it took the flexure's anchorage from 1.60 mm down to
**1.100 against a 1.5 floor** along with the stop. Both were caught by checks, but only because
the checks measure the solid.

> Before deleting a special case, list what it was doing differently and why. Generalising code
> generalises its defaults over your exceptions.

**3. A chamfer's edge selection is not authoritative while tangent chaining is on.** Fusion's
`isTangentChain` (the third argument to `addEqualDistanceChamferEdgeSet`) means the chamfer runs
on into any edge tangent to one you picked. These cavity walls are tangent to the bore at its
equator *by design*, so excluding the bore arc from the selection changed nothing - the chamfer
arrived through the wall edge. Turning chaining off is not the answer either: the chain then ends
on that tangent point and the feature fails with `ASM_BL_END_TOO_CMPLX`. **Exclude the whole
tangent group, and verify by the edge count.**

**4. A guard must measure the MATERIAL, not the CENTRES.** The pre-cut guard reported
`column between the two slots 1.24 mm OK` on a band whose column measured **0.050 mm**:

        col = 2 * r_mid * cos(theta)              # distance between cap CENTRES - wrong
        col = 2 * r_mid * cos(theta) - relief_w   # material actually left

One whole `relief_w` of optimism, on every band ever built with it, hidden only because every
previous wrap was shallow enough that 1.2 mm of error never crossed the floor. Same family as
"a face picked by radius alone finds the wrong face": **a guard that names a quantity has to
compute that quantity.**

> **The geometric fact it was hiding is worth keeping on its own: on a band whose relief slots
> are CONCENTRIC with the bore, a SMALLER bore can wrap LESS deeply, not more.** `r_mid` shrinks
> with the bore, so the two slot roots sit closer to the centreline at the same angle. The
> intuition runs the other way and it is wrong: at -86 deg on a 13.25 bore the slots passed
> 0.041 mm apart and the measured root web read **0.74 / 0.82 / 0.04** against floors of
> 1.5 / 1.2 / 1.2.

**The cost of the change, stated plainly**, since it is the trade rather than a free win: the
body now comes out past a lip instead of lifting off the magnet, and Band B runs at **147% of
the 15 MPa rule while being the DAILY-CYCLED flexure** - Band A's 162% is pressed once and left.
Arm length is the only lever that reduces stress without reducing the reach, the reach is at its
printability floor, and the wrap is at its collision limit - so the remaining fix is the one
already on record: **curl the relief slots outboard for a -110 deg wrap**, which would pay back
both bands at once.

#### Can the part even TRANSMIT the insertion force? (2026-10-27)

The MOD-GRID Olight holder was reported as "too big for the flashlight to clip into it and hold
it". It was not too big. The light measures 15.10 and the band's printed throat is 14.26, so the
snap was correctly sized. The problem was that **the i Mini 2 is two pieces held together by a
magnet**, and pressing the assembled light into the band needs 26 N - far more than the magnet
can carry. It came apart in the hand instead of going in.

> **A multi-piece part has its own weakest link, and the insertion force runs through it.** A
> magnet, a hinge, a battery door, a pocket clip, a screw-on tailcap: any of them will let go
> long before a correctly sized snap does. Before blaming a clearance, ask what the part is made
> of and what the press force actually passes through. Press the sub-assembly that can take it.

**The axial trap that follows.** Once you decide to grip only the base and let the user pull the
rest off, the load changes direction: a band grips RADIALLY and its arms are deliberately
unloaded when seated, so there is essentially no friction along the axis. Pull the light off and
the base slides out of the cradle after it. The obvious answer - a collar bearing on the step
where the two halves meet - is unavailable, because **when the part is assembled the other half
is sitting on that step**. There is nothing there to grab.

**Fix: change the removal motion from axial to RADIAL, and the axial load stops existing.**

| band | what it does |
|---|---|
| on the base | a normal SNAP, pressed in on its own with no magnet in the load path |
| under the body | an **open cradle with no capture lip**, walls stopping BELOW the part's equator |

The body then lifts straight up out of the cradle, peeling off the magnet as it goes, and the
base stays snapped down. Two numbers make it work and both are worth checking in the script:

1. **The cradle's top face must sit below the part's widest point**, by more than `cav_clear/2`.
   A cradle band has no relief slots and therefore no arms - if its walls rise past the equator
   the part is trapped in rigid material with nothing to flex, which is a far worse failure than
   a loose fit.
2. **A cradle band must be SUNK by `cradle_r - part_d/2` relative to the snap band**, so both
   hold the part on the same axis. The cradle is cut larger than the part, so the part rests
   lower in it than the geometric centre; ignore that and the part rocks between the two bands.

#### A round bead self-locks on a rounded corner: check the CONTACT ANGLE, not just the clearance (2026-10-25)

The Zippo band was printed with the corrected arms (2.80 -> 2.00 taper, 2.0 mm root web,
13.8 MPa, 6.3 kg of computed pull-out). The lighter **would not seat**: it stuck about 2 mm
proud with the arms visibly splayed, and the band's top edge finished level with the case's top
face instead of standing 1.95 mm above it. Reported as "the arms are still not long enough to
retain the lighter case, and the spring force is forcing the lighter to not seat correctly" -
and both halves of that were right.

Every existing check passed. Interference: clear. Stress: 92 % of limit. Root web: 2.0 mm.
Cavity: a 0.50 slip fit. Nothing was looking at **friction**.

**The mechanism.** Where the capture feature touches the part, the contact normal is
perpendicular to the surface there. Only the normal's DOWNWARD component pulls the part home;
friction resists with up to `mu * N`. So the joint seats only while

        contact face angle from horizontal  >  arctan(mu)        (~17 deg at mu = 0.3)

A round bead violates that **by construction near its crest**. Its normal runs centre to
centre, so as the part rises past the bead the normal rotates smoothly through HORIZONTAL at
the point where the two centres are level. Everything within `arctan(mu)` of that is a
self-locking wedge, and the arms' own spring force parks the part there:

| case corner radius | crest, mm proud | self-locking zone | 
|---|---|---|
| R2.0 | 2.10 | 1.45 - 2.10 (0.65 mm) |
| R2.8 (the Zippo) | 2.90 | **2.07 - 2.90 (0.83 mm)** |
| R4.0 | 4.10 | 2.85 - 4.10 (1.25 mm) |

About 2 mm proud is exactly where the photographs show it.

**Why the bead was on the corner at all.** The bead reached `lip_over` = 0.60 mm inboard of the
case's side face, i.e. to y 18.43. The case's top FLAT does not begin until `w/2 - case_r`,
about y 16.0. **The bead tip was 2.0 mm short of the flat, so 100 % of the capture happened on
the corner arc** - on the one dimension that has never been measured. "Put the bead above the
part's top FACE" was satisfied in z and missed entirely in y.

> **A bead "above the top face" is not above the top face unless its TIP reaches `w/2 - part_r`.**
> Write that comparison down explicitly. It is two numbers and it is invisible in a section view.

**Why you cannot just reach further.** Getting onto a Zippo's flat needs ~3 mm of reach, hence
~3 mm of arm deflection. Deflection goes as `2*sigma*L^2/(3*E*t)`: at 15 MPa with a 13 mm arm
you get 0.67 mm, and 3 mm would need the arm 2.6x longer. On a part with a corner radius much
bigger than the reach budget, **capture over the flat is not available at any arm geometry** -
so the design has to be sound while landing on the corner.

**The fix: a straight 45 deg capture face with a ROUNDED tip.** A straight face holds its angle
for the whole stroke - 45 deg is 2.7x arctan(mu), so it cams the part home everywhere. The only
place the normal can still reach horizontal is the tip itself, so make the tip a **radius of one
nozzle width (0.40 mm)** rather than a flat land: a flat land parks the part for its full width,
a radius parks it for `2 * r * sin(arctan mu)` ~ 0.23 mm and presents a 45 deg cam immediately
below. Profile going up the cavity wall: wall, 45 deg rising INBOARD (the capture face), tip
radius, 45 deg rising OUTBOARD (the lead-in), wall.

Peak splay is unchanged, because what sets it is the tip reaching past the part's widest point -
**so the stress budget and the pull-out force are identical**. The lip is strictly better for
free.

| Zippo band | capture | sticky zone | seated clearance | stress | pull-out |
|---|---|---|---|---|---|
| bead r0.85 at z 19.06 | corner arc only | **0.83 mm - it stuck here** | 0.41 | 13.8 MPa | 6.3 kg |
| 45/45 lip, tip r0.40 | corner arc, 45 deg throughout | **none** | 0.43 | 14.3 MPa | 6.8 kg |

**Place the lip off the SQUAREST plausible part, not the expected one.** The underside is the
line `y + z = K`; the lowest it can sit and still stand `clear` off a corner of radius `R` is

        K = sqrt(2) * (R + clear) + w/2 + part_top - 2*R

which **decreases** as R grows, so the binding case is the smallest R. Solve it at `case_r_min`
and the bias falls the recoverable way: a squarer-than-expected part can never be held proud,
and a rounder one only lifts further before the lip bites. On the Skeletool the first attempt
used `tool_r_min` 0.50 and the sweep caught a 0.20 mm edge clashing at seated; 0.20 (matching
what `cav_r` already assumed) costs 0.18 mm of free lift and removes the jam.

**The residual cost of not measuring the radius is free lift**, and only that: 0.16 mm at R2.0
rising to 1.53 mm at R4.0 on the Zippo. Measuring the corner radius buys it straight back -
nothing else does.

**Check it in the script, not by eye.** `seat_check()` walks the part up in 0.02 mm steps against
the arm's inner face expressed as `y = f(z)`, and at each step reports the required splay and the
LOCAL FACE ANGLE at the governing contact point, swept across the whole plausible corner radius.
It is a dozen lines because the profile is single-valued in z; it would have caught this before
the print.

#### A feature added INSIDE a cavity has to respect the cavity's own radii and its chamfer (2026-10-27)

A C-shaped retention stop was added inside the Zippo band's cavity, standing on the cavity floor.
It was positioned by setting its half width back from `cav_hw`, the cavity's half width, which
looked right and was not: **the floor only stays FLAT out to `cav_hw - cav_r`**, because the
cavity's bottom corner arc eats the rest. The stop's limbs ended up 0.50 mm from where that arc
starts, so a blend fillet at the junction had nowhere to live and the transition came out as a
cramped sliver.

Two rules, both of which generalise to any boss, rib or stop added inside a pocket:

> **Dimension a feature inside a cavity from the cavity's FLAT extent, not from its nominal half
> width.** Then set it back further by the blend radius you intend plus a margin. Here:
> `stop_hw = cav_hw - cav_r - stop_blend - stop_gap`.

> **Add the feature BEFORE the first-layer chamfer, not after.** Added after, the chamfer has
> already run round the cavity floor, and the new feature then sits over that chamfer - leaving
> an undercut groove along its base and an unchamfered island inside a chamfered pocket. Added
> before, one chamfer runs continuously round the whole bed outline. (This is the opposite of
> the rule for the mount LEGS, which must come after, because they break the body's OUTER outline
> and terminate the chamfer chain. A feature inside the cavity only adds an inner loop, so it is
> safe.) Check it by the count: the band went from "16 edges, 2 left sharp" to "32 edges, 0 left
> sharp".

**And a third, smaller trap underneath both of them.** The chamfer skips any edge shorter than
`2 * chamfer + margin`, which is correct - a chamfer longer than its own edge eats the part. But
that means a short land left between two chamfered edges is silently skipped and prints as a
sharp step between two chamfered ones. So **any deliberate land next to a chamfered edge must be
longer than that threshold**: the 1.00 mm margin here became 1.20 against a 1.10 mm cutoff. The
build log reporting "N left sharp" is what makes this visible, and it is worth printing.

#### A relief slot starves the web at its root (2026-10-23)
Freeing a flexure with a relief slot moves the problem: whatever is left between the slot's
closed end and the nearest face becomes the flexure's **entire anchorage**, and it is easy to
starve without noticing because the slot itself looks fine. On the Zippo clip that web measured
**0.80 mm** - the arm would have torn out at its root on first use.

| Rule | Value |
|---|---|
| Web between a relief slot's end and the nearest face | **>= 1.0 mm**, and check it with a probe rather than by eye |
| Preferred fix | **Raise the surrounding geometry, do not shorten the flexure** - but be clear WHICH web you are fixing. `base_t` only moves the slot relative to the **bed face below it**: on the Zippo, 2.0 -> 3.0 took that gap 0.80 -> 1.80 mm with the arm, and its stress, unchanged. It does **nothing** for the ROOT web between the slot cap and the cavity floor, because the floor rises with it - see the 2026-10-24 flexure section above, where confusing the two let an arm end up anchored on 0.016 mm. |

Worth noting the pattern across the last three fixes: the flexure itself was fine each time, and
the failure was always somewhere adjacent that no check was looking at - above the working point,
at the slot root, at the bed face. **Probe the neighbourhood of a flexure, not just the flexure.**

#### Measure a flexure over its WHOLE length, including past the working point (2026-10-23)
Third variant of the same mistake. The Zippo clip's arm was verified "2.00 mm constant" - but the
check only sampled from the relief-slot root **up to the lip tip**, and the arm continues above
that to the top of the band. In that stretch the opening's 45 deg lead-in ramp moved outward
faster than the relief slot's arc did, so the two converged and the arm feathered to **0.09 mm**.

Two rules out of it:
1. **Sample the full extent of the flexure, not just the part you were thinking about.** The
   working point (the lip tip) is where the load is applied; it is not where the section is
   thinnest.
2. **A lead-in ramp on the inner face must be matched on the outer face**, or it eats the wall.
   Easiest fix is usually no ramp at all - on the Zippo the lighter's own 6.35 mm rounded edge
   cams the arms open, so the ramp bought nothing and cost the whole arm tip.

Also note the probe artefact that briefly hid the fix: a point sampled exactly **on** a face
returns "on surface" (1), not "inside" (0), so a walk that starts there bails immediately and
reports a false near-zero. Sample 0.02 inside the face.

#### "No overhangs" is not the same as "no support" (added 2026-10-22)
A third failure on the same part, caught by the slicer rather than by me. The MOD-GRID pen clip
was printed standing on end, where every face of every cross-section is vertical - genuinely zero
overhangs. It still needed support, because the **mount legs were centred along the part** instead
of flush with the bed face. Their 4.90 mm extent began 4.55 mm up the print, so a
4.64 x 4.90 mm island of material appeared in mid-air with nothing beneath it.

**Overhang analysis is per-cross-section; this is a different question.** Ask it separately:

> For every feature, does it either reach the bed itself, or sit on top of something that does?

A feature that spans only part of the build axis must be pushed to the **bed end** of that span,
not centred, or its first layer floats. The official MOD-GRID holders do exactly this - legs span
0..4.90 of a body that runs 0..7.95, both starting at the bed; the legs simply stop early. Stopping
early is free (it is just a top face); starting late costs support.

Related gotcha from the same fix: once the legs reached the bed face, the **first-layer chamfer
failed** (`ASM_BL_CAP_COMPLEX`) because the legs broke the body outline into segments and the
chamfer chain terminated mid-face. Applying the chamfer *before* adding the legs solves it - the
legs' own bed edges stay sharp, which is correct anyway since a 0.94 mm leg cannot take a 0.5 mm
chamfer.

#### Check the LOAD PATH against layer direction, not just the overhangs (added 2026-10-21)
Confirmed by a real break: the MOD-GRID pen clip sheared its retaining lip on the first pen
removal. The geometry was sound and there were no overhangs at all in that orientation - the
mistake was choosing the orientation purely to make the *pegs* print well, then never asking
which way the *working* stress ran.

| | Value |
|---|---|
| ABS in-plane (along layers) | ~40 MPa |
| ABS across layer interfaces | **~15-20 MPa**, i.e. 40-50 % |
| Lip bending stress as printed | **~59 MPa**, pulling straight across the interfaces |

Three lessons:
1. **A part can be flawless on overhangs and still be oriented wrong.** Add "which direction does
   the load pull, and is that along or across layers?" to the orientation step, next to the
   overhang scan.
2. **Flexures are the usual victim.** Any snap, clip, lip or living hinge is a beam in bending;
   its stress runs along its own length. Orient so that length lies *in* the layer plane.
3. **Beware a wedge-shaped flexure.** A lip that is thick at the root and thin at the tip does
   nearly all its flexing at the tip while concentrating stress at the thick root, and
   lengthening it makes the root thicker too, so `c` grows about as fast as `L^2` helps.

   **Confirmed on the second print.** Cutting the relief slot as a straight vertical slot beside
   a round bore makes the lip a wedge, because the bore curves away from the slot:

   | height | lip thickness |
   |---|---|
   | relief root | 2.59 mm |
   | bore equator | **0.60 mm** |
   | lip tip (where the pen pushes) | 0.77 mm |

   0.60 mm is **1.5 extrusion widths** at a 0.4 nozzle: the slicer cannot lay a solid wall, so
   that is exactly where blobs, stringing and seam artefacts appear - and it has so little
   bending stiffness that it deflects aside instead of retaining anything. Two separate
   complaints ("hard to print" and "won't hold"), one cause.

   **Fix: make the relief slot an annular sector that follows the bore at a fixed offset**, so
   the lip is a constant-thickness curved spring. Same part went to a uniform 2.00 mm (5
   perimeters) over a 7.5 mm arc, ~16 MPa at 0.15 mm deflection, 2.5x margin.

   **Rule: state a flexure's minimum thickness in extrusion widths, not millimetres, and check
   it along the whole flexure - not just at the root.** Below ~3 widths, redesign.

The fix that worked: stand the part on end so the pen axis is vertical. The lip stress then runs
along layers (~24 MPa against a 40 MPa limit, 1.7x margin), the bore becomes a true vertical hole
needing no teardrop, and the body becomes a pure extrusion with identical layers throughout. The
cost was that the pegs turned sideways and needed designed support blocks under them - which is
the right trade, because support is recoverable and a sheared flexure is not.

#### A lipped clip and a captive socket are kinematically incompatible (2026-10-24)

Found designing the MOD-GRID prybar holder: *slide the tip into a socket, then clip the other end down*. The obvious build is a tip socket plus a C-clip with lips over the part's top face. It cannot work, and the reason generalises to any two-point holder.

Once the tip is captive, **the far end can only descend by the whole part rotating about the socket.** To drop under a lip at the part's top face, the far end must descend the part's **full thickness**. Over the lever between the two mounts that is a large angle, and the socket can only supply it by being short and loose — at which point it is not a socket.

| Scheme | Descent needed at the clip | Verdict |
|---|---|---|
| Lip over the top face | the part's full thickness | needs ~12° of tilt on a 19 mm lever; the socket would have to be sloppy to allow it |
| **Pinch clip** (parallel arms, throat narrower than the part, no lip) | still the arm height, but the arms splay **continuously** and the part's width presented to them is **the same at any tilt** | works; retention is spring force, not a catch |

**The second trap, found 2026-10-24 once a reference model of the part existed:** with the far end captive, tilting the part square-end-up makes the **captive end dip BELOW its seated height**. A deep blind socket with its floor at the seated height blocks that outright — the first attempt here was a 40 mm captive socket, and it could not be assembled at all. Trigonometry had said it was fine, because the trig was checking the wrong contact.

Rules:
- For a socket-plus-clip holder, use a **pinch**, not a lip. Grip the lower part of the section and leave the top proud — that also makes the part easy to pinch out.
- Keep the clip **low**: `clip_height - base` is how far the far end must descend, so it sets the swing angle.
- **Make the captive end a SHORT cap right at the tip, not a long socket.** Two wins at once: the pivot moves as far from the clip as possible (longest lever, smallest angle — 51 mm and 4.5° here, against 19 mm and 12° for the long socket), and there is barely any length inside the cap for the tip to foul.
- **Drop the cap's cavity floor below the part's seated height** by at least `(cap length) x tan(swing angle)`. 1.5 mm covered 4.5° over an 18 mm cap. The part rests on the clip and on nothing else at that end, which is fine — it is rigid.
- **Build a reference model of the part being held, and check fitment by interference, not arithmetic.** Rotate a `TemporaryBRepManager` copy to the insertion angle and intersect it with each holder. It caught two errors here in one run that hand calculation had missed: the end cap sitting through the part (a placement formula rounding down where it had to round up), and the floor-dip problem above. Sample the swing at several angles and go ~25% past the needed one. Name it `Reference - …` and keep it out of the export.
- **Check the grip band against holes and slots in the part, not just its outside profile.** A pinch clip bears on the part's side faces, so a lanyard slot through those faces is a hole in the contact patch. On the prybar the slot runs x 2.0-8.5 and the clip had been placed at x 3-13: 55% of the contact length over an opening, with the arm tips landing on the slot edges. Moving the clip to x 11 fixed it and cost nothing, because the grid cell count simply dropped from 7 to 6 and the other holder did not move. Make the overlap an explicit check - it is two numbers and it is invisible in a render.
- **When a fit fails twice, stop adjusting clearances and sweep the shape.** The Zippo clip failed three times while the cross-section was assumed to be an obround. One interference sweep of the band against a parametric case settled it in a single run: it fitted only a true semicircle (R6.47 -> 0.003 mm3) and jammed on anything squarer (R3.00 -> 136 mm3), with the overlap in the LOWER half, which matched the reported symptom exactly. Sweeping the uncertain *shape* parameter finds what repeated clearance tweaks never will.
- **Make the cavity SQUARER than the part, not a copy of it.** A cavity corner rounder than the part's lands on the part's corners and holds it off the floor - the part rides proud and nothing else touches. A corner radius deliberately smaller than the part's clears everywhere and cannot jam, whatever the real radius turns out to be. Worth the few tenths of lost contact: contact is the bead's job.
- **Bias an estimated dimension toward the recoverable failure.** The bead height here follows an estimated corner radius. Too low and the part will not seat at all; too high and it gains a few tenths of lift play. So the estimate is deliberately set to the squarer end of what the photos support, and `run()` prints the fit across the whole plausible range rather than asserting one value.
- **Prefer a tangent BEAD to a pointed lip - ONLY on a part with small edge radii.** A lip with a flat tip between two 45 deg ramps puts a 0.4 mm feature on a 1.2 mm arm - the obvious thing to snap off. A half circle of radius `cav_hw - lip_tip_y`, centred ON the cavity wall, is tangent to the wall above and below, so the arm's inner face is one continuous curve with no corner anywhere; the bead is a local thickening rather than a thin tooth. That reasoning holds on the prybar (R0.5 edges on a 6 mm bar). **It does NOT survive a big corner radius - see "A round bead self-locks on a rounded corner" below, which is why the Zippo band went back to a 45/45 lip with a ROUNDED tip** (a radius, not a flat land, so it is not a thin tooth either). The real rule is about what the bead lands on, not about beads.
- **A conforming pocket and a swing-in assembly are mutually exclusive.** If the captive end's pocket follows the part at its seated height, the part has nowhere to dip and cannot rotate at all - so insertion becomes axial: snap the free end into the clip first, then slide the part forward until it stops. Give the pocket the SAME taper as the part so the two faces stay parallel and it slides home instead of wedging, and let a blind face set the axial stop. Decide which you want before designing the clip, because it changes the motion the user performs.
- **A lip is possible once the captive end is far enough away - re-check the decision when the layout moves.** Rejected here at first because the socket sat 14 mm from the clip (~20 deg of swing); with the nose moved out to the point, the span became 38 mm and the same full-depth capture needs only 9 deg. The constraint is the clip's INBOARD end, the point nearest the pivot, which rises least.
- **Prefer a lip to a pinch in ABS when you can afford it.** A pinch holds the arms splayed forever and ABS creeps, so the grip goes slack over months; a lip leaves the arms unstressed when seated and only strains them during insertion and removal. That also justifies a lower stress margin (1.8x here) than a permanently loaded arm would need.
- **Rounded part edges eat lip engagement.** An R0.5 edge on a 6 mm bar leaves its top face only 5.0 mm wide, so a lip must reach 0.5 mm in before it bites anything at all. Size `lip_over` from the FLAT, not from the overall width. What actually retains the part is the splay needed to release it, so a modest bite onto the flat is fine as long as the splay is real.
- **Lip profile for printing on end:** 45 deg lead-in on top, a flat tip of one nozzle width (a knife edge will not print), 45 deg release ramp underneath. The underside must rise as it goes OUTBOARD - slope it inward-down and it cuts into the part's top corner radius instead of sitting over the flat.
- Sanity-check the grip: two arms at ~18 MPa over a 10 mm band give ~12 N of squeeze, about 350 g of friction at µ≈0.3. For a 35 g part that is 10×, so the lip buys nothing anyway.

## Material notes — ABS on a Voron 2.4
- Shrinkage ~0.5–0.7 %: over 254 mm that's ~1.5 mm. Calibrate shrink compensation in the slicer (~100.5–100.7 %) or print a test strip before trusting rack-ear spacing.
- Warping on long, thin flat parts: see **Warping / corner lift** below.
- Heat-set inserts in ABS: ~220–240 °C iron temperature.
- Gluing ABS: acetone or ABS slurry solvent-welds (strongest). Thin CA needs ~0.1–0.15 mm joint gaps; gap-filling CA for looser fits.
- Glue-joint clearance used: **0.15 mm per side**.

### Topic files (Slant 3D playlist, 2026-09-30)
- `slant3d-designing-out-overhangs.md`: chamfer vs fillet, gussets under tabs, clips, wire loops, domes, fill-it-solid
- `slant3d-designed-supports.md`: catalogue of fins, combs, thumbtacks, offset shells, bridge blocks, mushrooms
- `slant3d-grip-fins.md`: self-adjusting holes and press fits
- `slant3d-diagonal-print-fin-supports.md` and `fusion-slant3d-fin-support-workflow.md`: 45° printing and building fins in Fusion

### Warping / corner lift (ABS) — added 2026-10-01 after severe corner lift on the RPI shelf
Corners lift because cooled upper layers shrink and pull the edges up. The longest, stiffest runs and tall walls on a thin plate make it worst. Fix it in the model first, then in the printer environment.

**In the model**
| Rule | Value |
|---|---|
| Mouse ears on every **sharp** bed corner | Separate `Support - Mouse Ear …` bodies, discs **0.4 mm thick** (2 layers), **R 6–8 mm**, centre pushed ~2 mm outward diagonally so the corner sits well inside the disc. Export them with the part. Trim with a knife afterwards. |
| **No ears on a rounded corner** | **A filleted footprint corner has no stress concentration to lift, so an ear there is redundant** — it only adds a part to trim off and a scar to clean up. Ears are for SHARP corners. If a corner is already rounded (and especially if it is also first-layer chamfered), leave it bare. Added 2026-10-23; the MOD-GRID baseplates are R3 all round, so they carry no ears. |
| Keep ears off nearby holes and slots | Shrink the radius or move the ear so it doesn't bridge a bed-level slot (panel ears are R 6 to clear the rack-ear slots). |
| Round sharp footprint corners where function allows | Spreads the corner stress. Shelf rear corners R 10 and all 4 panel corners R 4 (2026-10-01). The shelf front corners stay square because they mate with the channel. Put the fillet **before** the first-layer chamfer in the timeline. If the chamfer doesn't pick up the new arc edges, add a matching 0.5 mm chamfer on them. Re-centre the mouse ears on the arc midpoint (2 mm outside it). |
| Avoid tall stiff walls standing on thin plates at the edges | Or accept them and put ears at the plate corners nearest them |

**In the printer (Voron 2.4, enclosed)**: heat-soak the chamber to **≥ 50–60 °C** before starting (30–45 min). Bed **100–110 °C**. Part cooling **off** for the first ~5 layers and ≤ 20–30 % after. Keep the panels and lid closed, and keep exhaust or filter fans from blowing across the bed. Use a clean textured PEI sheet (or glue stick or ABS slurry on smooth PEI), and slow the first layer down.

## Checklist before calling a part "print-ready"
1. Fix the print orientation for every body.
2. In that orientation, look for: flat downward faces, cantilevers, horizontal round holes/pins, bridges > 10 mm, bed-level slots < 1 mm.
3. Redesign first: fill it solid, 45° chamfer or gusset under tabs and clips, wedge, teardrop or pointed cavity, thin from the top instead of the bottom.
4. Anything left → designed-in fin or comb with **horizontal** sprues (see `slant3d-designed-supports.md`).
5. First-layer chamfer on bed-contact edges. Mouse ears on **sharp** bed corners of long or flat ABS parts — not on rounded ones, where they are redundant.
6. Verify: all features healthy, parts don't interfere, point checks for critical geometry.

## Applied to the RPI shelf (2026-09-30)
| Problem (print orientation) | Fix |
|---|---|
| Rabbet under shelf front edge = 6 mm flat ledge, 1.35 mm above bed | 45° chamfer on shelf edge sitting on a 45° wedge on the panel |
| Latch tongues thinned from below = 20 mm cantilever 1 mm above bed | Tongues print on the bed, thinned from the top; slots widened to 1.0 mm |
| Horizontal round locating pins on the gussets | Teardrop pins (point down) + teardrop holes + 4 designed-in sprue fins |
| Elephant foot on fitted faces | 0.5 mm chamfer on panel front face and shelf outer bottom edges |
| *(2026-10-01)* Snap tongues and barbs | Replaced with 4 teardrop locating pins (R 1.75, 0.4 mm flat **printed directly on the bed**, so no fin) on 6 mm bosses, into teardrop holes (R 1.9) in the panel's former latch blocks. Latch features suppressed, not deleted. Retention now comes from glue (channel + pins). |
| *(2026-10-01)* Pin fins only touched from below; the tall upper fins balanced on a 0.4 mm ridge | Tied each fin to the gusset front face with **horizontal** 0.5 × 0.8 mm sprues bridging the 0.4 mm gap (1 on each lower fin, 3 on each upper fin) |
| *(2026-10-01)* Severe corner lift | Mouse ears: 4 on the shelf (R 8), 4 on the panel face (R 5.5, 0.5 mm clear of rack-ear slots), 0.4 mm thick. Shelf rear corners R 10, panel corners R 4, first-layer chamfer carried around the arcs. |

## Sources
- [Hackaday — Designing To Remove Supports (Slant 3D)](https://hackaday.com/2022/12/05/designing-to-remove-supports/)
- [Hackaday — An Alternative Orientation For 3D Printed Enclosures (Slant 3D fins & sprues)](https://hackaday.com/2024/02/02/an-alternative-orientation-for-3d-printed-enclosures/)
- [Manual Support Fins for 3D Printing (masukomi)](https://weblog.masukomi.org/2024/03/11/manual-support-fins-for-3d-printing/)
- [Hackaday — Forget Trees, Add Fins To Your 3D Prints Instead](https://hackaday.com/2026/09/23/forget-trees-add-fins-to-your-3d-prints-instead/)
- [Dreaming3D — Stop Fighting Your Slicer: Design Your Own Supports in CAD](https://dreaming3d.net/blogs/news/stop-fighting-your-slicer-design-your-own-supports-in-cad)
- [Slant 3D — Best Tips for Lowering Your Design Cost in 3D Printing](https://www.slant3d.com/slant3d-blog/best-tips-for-lowering-your-design-cost-in-3d-printing)
- [Hackaday — Sacrificial Bridge Avoids 3D Printed Supports](https://hackaday.com/2017/10/17/sacrificial-bridge-avoids-3d-printed-supports/)

### Videos (transcripts reviewed 2026-09-30)
- [Slant 3D — The Correct Orientation to Print Boxes](https://youtu.be/8NKVNwVaZU0): see `slant3d-diagonal-print-fin-supports.md`
- [Shop Therapy — Autodesk Fusion: Make supports like Slant 3D](https://www.youtube.com/watch?v=sn2u949g7dM): see `fusion-slant3d-fin-support-workflow.md`
- [Slant 3D playlist — Design Your Own Supports for 3D Printing (9 videos)](https://www.youtube.com/playlist?list=PLkUv8_afCbJ8Pu83Gx-j36phSagA9-R5D): see the three `slant3d-*` topic files above
