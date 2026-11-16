# Design Rules and Guardrails

Every rule in this file was paid for with a printed part. Each one is written as the **rule**,
the **failure that produced it**, and where possible a **guardrail** — a check a script can
assert so the same mistake cannot pass review again.

This is the distilled rulebook. The narrative versions live in `CLAUDE.md` (per-project
history) and `research/design-for-fdm-printing.md` (full write-ups with workings). Where a
number appears in more than one place, **this file and the scripts are the authority**;
anything older that disagrees has been superseded.

Baseline: Voron 2.4 (350 mm, enclosed), 0.4 mm nozzle, 1.75 mm Polymaker ABS, slicer
supports **OFF**. Parts are fixed in the model, never in the slicer.

---

## 0. Measured constants

Numbers that came off calipers or off a printed part. Everything else is derived from these.
**Re-measure and reset all of them if the printer, nozzle or material changes — they are not
constants of nature.**

| Constant | Value | How it was obtained |
|---|---|---|
| `PRINT_BIAS` — dimensional bias | **0.07 mm per wall** | A 5.00 mm modelled hole printed **4.86** (2026-10-23) |
| Extrusion width | **0.40 mm** | 0.4 mm nozzle |
| Minimum flexure wall | **1.60 mm = 4 perimeters** | No gap-fill bond line down the middle |
| `SIG_LIMIT` — design stress | **15.0 MPa** | ABS in-plane yield ~40 MPa ÷ 2.5 design factor |
| ABS across layer interfaces | ~15–20 MPa (40–50% of in-plane) | Why orientation is a load-path decision |
| `MU_SEAT` — friction | **0.30**, so arctan(µ) ≈ **17°** | Standard ABS-on-anything working value |
| Baseplate `hole_clear` | **0.07 / side** (modelled 5.14 → true 5.00) | Compensates the bias outward |
| Clip `leg_clear` | **0.14** (modelled 4.76 → ~4.90) | Compensates the bias inward |
| Glue-joint clearance | **0.15 mm / side** | — |
| M2.5 heat-set insert | 3.6 mm hole, 5 mm deep, 7 mm boss | — |
| Sliding-fit floor | **0.50 mm modelled** | 0.20 modelled is 0.06 real and binds |

**Holes shrink and external features grow by the same bias, so a peg-in-hole fit sees it
twice.** Compensate at both ends or you have fixed half the error.

**Do not apply the compensation to an elastic feature.** A snap barb is meant to squeeze;
shrinking it with the shank costs retention and buys nothing.

---

## 1. The printability floor — features that must be big enough to exist

### 1.1 A retention feature must be at least ONE extrusion width in its working dimension, and TWO to print crisply
*Cost: five prints of the Olight band with no detent at all.*

`lip_over` was 0.35 mm — under one extrusion width **and** under `lip_tipr` (0.40) — so the
two 45° faces never existed and the slicer deleted the feature. Rob measured the printed
band's throat at **15.34 against a bore of 15.36**: the throat *was* the bore. A 15.10 cap
dropped straight through.

> **Guardrail:** `assert lip_over > lip_tipr` and `assert lip_over >= 2 * 0.40`.
> Two comparisons, four numbers, and they are invisible in a section view.

The 4-perimeter rule had been applied to the arm, and the one-nozzle-width rule to the lip's
*tip radius*. Neither was ever applied to the lip's **reach** — the dimension that does the
work.

### 1.2 Prefer a capture whose printed size comes from the CAVITY, not from the reach
Three of the four holders survived the same bad reach. The difference is what sets the
*printed size* of the capture:

| part | capture | printed size | reach | holds? |
|---|---|---|---|---|
| prybar | tangent bead, radius `cav_hw - lip_tip_y` | **1.08 mm** | 0.08 | yes |
| pen | constant 2.00 mm arc | **2.00 mm** | — | yes |
| pill bottle | lip doesn't print either — grips by its **BORE** | — | 0.35 | yes |
| Olight | 45/45 lip, size **IS** the reach | **0.35 mm** | 0.35 | **no** |

A tangent bead grows as the cavity opens, so it stays printable at any reach. A 45/45 lip's
only dimension is the reach, so it is the one shape where a small reach means **no feature**.

### 1.3 Quote wall thickness in extrusions, never in millimetres
1.2 mm at a 0.4 nozzle is 2.86 extrusions: 2 perimeters plus a sliver of gap fill **down the
middle of the flexure**, a bond line exactly where bending stress peaks. Use 1.6 (4), 2.0 (5),
2.4 (6), 2.8 (7).

### 1.4 Other minimums
- Bed-level slots **≥ 1.0 mm** so elephant foot cannot close them.
- A chamfer skips any edge shorter than `2 * chamfer + margin`. So **any deliberate land next
  to a chamfered edge must be longer than that threshold** or it prints as a sharp step
  between two chamfered ones (the Zippo `stop_gap` 1.00 → **1.20** against a 1.10 cutoff).
- Sprue/fin contacts: ≥ 2 perimeters (≥ 0.8 mm) in their widest direction or the slicer
  drops them.

---

## 2. Flexures and snap arms

### 2.1 A snap arm fails where it is ANCHORED, not along its length
*Cost: the prybar clip snapped on first insertion.*

Measured after the break: the relief slot's root cap sat **0.162 mm** from the bed chamfer.
The Zippo band was **0.016 mm**. They tore out at the root; they did not yield in bending.

| part | root web after the bed chamfer | outcome |
|---|---|---|
| prybar v1 (1.2 arm, wrap −130°) | **0.162 mm** | **snapped on first insertion** |
| Zippo band (1.6 arm, wrap −135°) | **0.016 mm** | caught by Measure before printing |
| both, rebuilt (tapered, −110/−115°) | **1.57–2.00 mm** | current |

> **Guardrail — `measure_root_web()`.** Take the relief slot's root cap and run
> `measureMinimumDistance` to **every other face** of the body, classified by direction:
> **ABOVE** the cap = the anchorage into the base (**≥ 1.5 mm**), **BELOW** = material down to
> the bed face (**≥ 1.2**), **BESIDE** = usually the opposite slot, i.e. the column between
> them (**≥ 1.2**). Report all three every build.

**The 17.5 MPa "measured ceiling" derived from that break is RETRACTED.** Nothing was measured
at 17.5 MPa; a part with a 0.16 mm ligament failed and a number was back-fitted to it. The
limit comes from the material: 15.0 MPa (§0).

### 2.2 Past −90° of wrap the root web stops being `arm_t` and starts collapsing
Up to −90° the slot runs at a constant offset from the cavity corner, so the web **is** the arm
thickness. Past −90° the cap tucks under the floor and the nearest cavity surface becomes the
**floor plane**:

```
web = -cav_r - (cav_r + arm_root + relief_w/2) * sin(th0) - relief_w/2
```

On the Zippo: 2.80 mm at −90°, 2.50 at −110°, **1.08 at −135°**. **It does not contain
`base_t`** — floor and slot rise together — so raising the base does nothing for it. Only a
shallower wrap or a thicker root helps. Hard stop: at −150° the slot cut clean through the
floor and split the band into loose pieces **while the timeline reported 0 unhealthy**.

### 2.3 TAPER the arm — thick at the root, thinner at the tip
The bending moment is `F × (lip_z - z)`: largest at the root, zero at the lip. A constant
section is overstressed at one end and wasted at the other. Taper it and the thicker root
pushes the relief slot outboard, which is exactly what thickens the root web — one change
fixes the stress distribution *and* the anchorage.

Build it by sloping the slot's **inner** edge inboard over `arm_blend` while its outer edge
stays vertical: the rail keeps constant thickness and the slot simply widens higher up.

### 2.4 Do not thin an arm to buy reach
The reach **is** the deflection, so it is a stress-budget *input*, not something to maximise.
A stiff, thick, properly anchored arm with a modest reach beats a thin arm with a deep one:

| Zippo band | arm | reach | root web | stress as printed | pull-out |
|---|---|---|---|---|---|
| the version this rule replaced | 1.60 flat | 0.98 | **0.016 mm** | 14.8 MPa | 1.3 kg |
| rebuilt | **2.80 → 2.00 taper** | 0.60 | **2.00 mm** | 13.8 MPa | **6.3 kg** |

### 2.5 An arm between two VOIDS prints THICKER, and that belongs in the stress check
A flexure arm sits between the cavity and the relief slot. Both are voids, both print inward,
so the arm comes out **2 × 0.07 = 0.14 mm thicker** than modelled.

```
sigma = 3*E*delta*t / (2*L^2)      stress scales with t
F     = E*b*t^3*delta / (4*L^3)    force  scales with t^3
```

A 1.60 arm printing at 1.74 is 9% more stressed and **28% stiffer**. Ignoring it under-reports
stress ~5% and insertion force ~20%.

> **Guardrail:** bias both the **deflection** (cavities print under, so the lip reaches
> further in) **and the arm's own thickness** in `flexure_check`.

Two corollaries: **any wall bounded by two cut features gets the bias twice, with the sign
that makes it thicker**; a wall bounded by a cut and the outside gets it once; a free-standing
rib gets it the other way and comes out **thin**. And **suspect this first when a part computes
comfortably but is too stiff to assemble by hand** — insertion force is the `t³` term.

### 2.6 Measure a flexure over its WHOLE length, including past the working point
The Zippo arm was verified "2.00 mm constant" — but the check sampled only from the slot root
*up to the lip tip*, and the arm continues to the top of the band. There the opening's 45°
lead-in moved outward faster than the slot's arc did and the arm feathered to **0.09 mm**.
The working point is where the load is applied; it is not where the section is thinnest.

Also: **a lead-in ramp on the inner face must be matched on the outer face** or it eats the
wall. Usually the right answer is no ramp — the part's own edge radius cams the arms open.

### 2.7 Prefer a lip to a pinch in ABS
A pinch holds the arms splayed forever and **ABS creeps**, so the grip goes slack over months.
A lip leaves the arms unstressed when seated and only strains them during insertion and
removal. (The direct consequence is §4.1 — unloaded arms means no axial friction.)

---

## 3. Seating, self-locking and contact geometry

### 3.1 A snap must be checked for SELF-LOCKING, not just for clearance and stress
*Cost: the Zippo band printed with a round bead and the lighter would not seat — it stuck
~2 mm proud with the arms splayed. Interference clear, 92% of stress limit, 2.0 mm root web.
Nothing was looking at friction.*

Only the **downward** component of the contact normal pulls the part home, and friction
resists with µN, so for the whole stroke:

```
contact face angle from horizontal  >  arctan(mu)  ≈ 17°
```

A round bead violates this **by construction**: its normal runs centre-to-centre and rotates
through horizontal at the crest. On a 2.8 mm case corner that is a **0.83 mm self-locking
band**, and the arms' own spring force parks the part in it — about 2 mm proud, exactly where
the photographs showed it.

**The fix: a straight 45/45 capture face with a tip RADIUS of one nozzle width (0.40).** 45° is
2.7 × arctan(µ) so it cams the part home everywhere; a *radius* parks the part for
`2*r*sin(arctan µ)` ≈ 0.23 mm where a flat *land* parks it for its full width. Profile going
up the cavity wall: wall → 45° rising INBOARD (capture) → tip radius → 45° rising OUTBOARD
(lead-in) → wall. **Peak splay is unchanged, so stress and pull-out are identical — the lip is
strictly better for free.**

> **Guardrail — `seat_check()`.** Walk the part up in 0.02 mm steps against the arm's inner
> face expressed as `y = f(z)`, and at each step report the required splay **and the local
> face angle** at the governing contact point. Sweep it across the whole plausible corner
> radius. Report the "sticky zone" width; it must be **0.00**.

### 3.2 A bead is only "above the top face" if its TIP reaches `w/2 - part_r`
Satisfying it in z and missing it in y is the same bug twice. The Zippo bead's *bottom* was
above the case's top face, but its tip reached only 0.60 mm inboard of the side face while the
flat does not begin until ~2.0 mm in — so **100% of the capture was on the corner arc**, on the
one dimension nobody had measured. Write the comparison down explicitly.

**And you cannot just reach further.** Getting onto a Zippo's flat needs ~3 mm of reach, hence
~3 mm of deflection; at 15 MPa on a 13 mm arm you get 0.67 mm. On a part whose corner radius
is much bigger than the reach budget, **capture over the flat is not available at any arm
geometry** — so the design must be sound while landing on the corner.

### 3.3 Make the cavity SQUARER than the part — except on a cylinder, where it must be ROUNDER
A cavity corner **rounder** than the part lands on the part's corners and holds it off the
floor: the part rides proud and nothing else touches. A corner deliberately **squarer** than
the part clears everywhere and cannot jam, whatever the real radius turns out to be. Worth the
lost contact — contact is the lip's job. (`cav_r` 0.30 on the Skeletool; 1.50 on the Zippo.)

**On a cylinder it reverses, for the same reason.** A cradle arc *larger* than the cylinder
touches at one point at the bottom and cannot jam; a smaller one catches it on two points up
the sides and holds it proud. So **make a round cradle rounder than the part**.

### 3.4 Place the lip off the SQUAREST plausible corner radius
The underside is the line `y + z = K`, and the lowest it can sit while standing `clear` off a
corner of radius `R` is

```
K = sqrt(2)*(R + clear) + w/2 + part_top - 2*R
```

which **decreases** as R grows — so the binding case is the **smallest** R. Solve at
`case_r_min` and the error falls the recoverable way: a squarer-than-expected part can never be
held proud, and a rounder one only lifts further before the lip bites. The Skeletool's first
attempt used `tool_r_min` 0.50 and the sweep caught a 0.20 mm edge **clashing at seated**;
0.20 costs 0.18 mm of free lift and removes the jam.

> **Bias every estimated dimension toward the recoverable failure.** Too low and the part will
> not seat at all; too high and it gains a few tenths of lift play. Then have `run()` print the
> fit across the whole plausible range instead of asserting one value.

**The residual cost of not measuring a corner radius is free lift, and only that** — 0.16 mm at
R2.0 rising to 1.53 at R4.0 on the Zippo. Measuring it buys that back; nothing else does.

### 3.5 A clearance derived against an INFINITE face is not the clearance you built
*Cost: three "still too loose" reports on the Olight after two defensible tightenings.*

`lip_z0` placed the lip's underside **line** `lip_clear` off the seated cylinder. Exact
arithmetic — about an **infinite 45° plane**. The real lip is `lip_proj` = 0.72 mm tall and
sits well below where that line touches the cylinder (the part's own 45° point at
`z = part_z + 0.707*D/2`). The part never reaches that face. Its closest approach is to the
lip's **tip radius**, which stood **0.67 mm** off a part the parameter claimed was 0.30 away.

| | parameter said | lip tip really stood off | free lift |
|---|---|---|---|
| as printed, twice | 0.30 | **0.67** | **1.52 mm** |
| placed off the tip radius | 0.30 | 0.30 | 0.68 mm |
| shipped (`lip_clear` 0.25) | 0.25 | 0.25 | **0.54 mm** |

**Free lift goes as the SQUARE ROOT of the clearance** — near contact the cylinder's surface
runs almost parallel to the lift direction — so 2.2× the clearance came out as 2.8× the
rattle. That ratio is why it hid: every number in the build log was small and plausible.

Closed form against the feature that exists — put the tip-radius **centre** at
`R + clear + tipr` from the seated axis:

```
lip_zt = part_z + sqrt((D/2 + clear + tipr)^2 - lip_cy^2)
```

valid while the arc's closest normal (~23° here) lies inside the ±45° the tip spans — **check
that, don't assume it**.

Three rules out of it:
1. **When you simplify a feature to a line or plane to derive a clearance, check the contact
   lands on the part of it you actually built.** A 0.72 mm face is not a plane. The giveaway is
   a derivation that never mentions the feature's **extent**.
2. **A clearance parameter must be ASSERTED against the model, not just fed into it.**
   `seat_check()` printed the real 0.70 in the same block as the 0.30 it was supposed to be,
   for three revisions. Nothing compared them, so nobody read them as a pair.
3. **Measure the assertion in the direction the parameter is defined in.** The first version
   compared `lip_clear` to a HORIZONTAL gap and false-alarmed on the pill holder, whose contact
   sits at 30° and differs by `1/cos`. A guard that is 15% out is a guard that gets switched off.

### 3.6 Size `lip_clear` from how well the part was MEASURED
Never leave it at the printer bias. 0.10 modelled became 0.05 as printed — near enough to
nothing that any error in the part's thickness, in `base_t`, or in the corner radius put the lip
back **on** the part and held it proud.

| part | `lip_clear` | why |
|---|---|---|
| Zippo (caliper-checked 38.05) | **0.40** | absorbs 0.57 mm of vertical error |
| Skeletool (published spec 13.20, wiki says 16) | **0.60** | absorbs 0.85 mm |
| Olight (measured 15.10 at every location) | **0.25** | the *balanced* value — lip and cradle run out of tolerance at the same +0.26 of diameter error, so neither is wasted on the other |

**Do not cut `lip_clear` below 0.40 on the Zippo** to chase free lift: as printed it is already
only 0.13 of seated clearance and 0.25 would hold the lighter proud.

---

## 4. Direction of load — the questions nobody asks

### 4.1 "Loose" is a DIRECTION, and nobody says which one
*Cost: four reports on the Olight, three radial fixes, against an axial complaint.*

| # | what was changed | what it moved |
|---|---|---|
| 1 | `cav_clear` 1.00 → 0.40 | bore 15.96 → 15.36 printed |
| 2 | `lip_clear` 0.50 → 0.30 | nothing real (§3.5) |
| 3 | `lip_z0` derivation fixed | free lift 1.52 → 0.54 mm |

All three radial. The light snapped in correctly and then **slid along its own axis**. Not one
of the three resisted that by a single newton — hence report #4: *"it still feels the same as
the previous 2 iterations."*

> **Ask at the FIRST report: does it rattle across, lift out, slide along, or fall out under
> load?** Four different defects, four different fixes, and the checks written for one are
> blind to the other three. One question at report #1 would have saved three prints.

**The structural fact underneath it:** these bands are deliberately designed so the arms are
**unloaded when seated** (§2.7), so there is almost no friction along the axis. **Every
band-style holder needs an axial stop as an explicit feature**, and only the Zippo had one.

### 4.2 Check the LOAD PATH against layer direction, not just the overhangs
*Cost: the pen clip sheared its lip on the first pen removal.*

The geometry was sound and there were zero overhangs in that orientation. The mistake was
choosing the orientation to make the **pegs** print well and never asking which way the
**working** stress ran: the lip's bending stress was **~59 MPa pulling straight across the
layer interfaces** (limit 15–20).

1. A part can be flawless on overhangs and still be oriented wrong. Add *"which direction does
   the load pull, and is that along or across layers?"* next to the overhang scan.
2. **Flexures are the usual victim** — any snap, clip, lip or living hinge is a beam in
   bending and its stress runs along its own length. Orient so that length lies **in** the
   layer plane.
3. **Beware a wedge-shaped flexure.** A straight relief slot beside a round bore makes the lip
   a wedge, because the bore curves away from the slot: 2.59 mm at the root, **0.60 at the bore
   equator**, 0.77 at the tip. 0.60 is 1.5 extrusion widths — blobs, stringing, no stiffness.
   Two complaints ("hard to print", "won't hold"), one cause. **Fix: make the relief slot an
   annular sector that follows the bore at a fixed offset**, so the lip is a
   constant-thickness curved spring.

### 4.3 Can the part even TRANSMIT the insertion force?
*Cost: the Olight "too big to clip in" — it was correctly sized all along.*

The i Mini 2 is **two pieces held together by a magnet**. Pressing the assembled light in
needs 26 N; the magnet is nowhere near that, so **it came apart in the hand instead of going
in**.

> **A multi-piece part has its own weakest link and the insertion force runs through it.** A
> magnet, a hinge, a battery door, a pocket clip, a screw-on tailcap: any of them lets go long
> before a correctly sized snap does. Before blaming a clearance, ask what the part is made of
> and what the press force passes through. **Press the sub-assembly that can take it.**

**And change the removal motion from axial to RADIAL, and the axial load stops existing.** One
band = a normal snap on the sub-assembly that can take it; the other = an **open cradle with no
capture lip**, walls stopping below the part's equator, so the rest lifts straight out.

Two numbers make that work:
1. **The cradle's top face must sit below the part's widest point** by more than `cav_clear/2`.
   A cradle has no relief slots and therefore **no arms** — if its walls rise past the equator
   the part is trapped in rigid material with nothing to flex, far worse than loose.
   `assert cradle_drop > cav_clear/2`.
2. **A cradle band must be SUNK by `cradle_r - part_d/2`** relative to the snap band, so both
   hold the part on the same axis. The cradle is cut larger than the part, so the part rests
   lower in it than the geometric centre. Get it wrong and the part rocks between the bands.

**A cradle has no arms and must never grip.** Give it its own `cradle_clear`, decoupled from
`cav_clear` — closing the Olight's bore dragged the cradle channel to zero, which prints 0.14
**under** the body, so it could not nest and sat 0.39 mm high, tilting the light.

### 4.4 A lipped clip and a captive socket are kinematically incompatible
Once the tip is captive, the far end can only descend by the whole part **rotating about the
socket** — and to drop under a lip at the top face it must descend the part's full thickness.

| scheme | descent needed at the clip | verdict |
|---|---|---|
| lip over the top face | the part's full thickness | ~12° of tilt on a 19 mm lever; the socket would have to be sloppy |
| **pinch clip** (parallel arms, throat narrower than the part, no lip) | the arms splay **continuously**, and the width presented is the same at any tilt | works |

Second trap, found only once a reference model existed: with the far end captive, tilting the
part makes the **captive end dip BELOW its seated height**. A deep blind socket with its floor
at the seated height blocks that outright — the first attempt was a 40 mm captive socket that
could not be assembled at all, **and trigonometry said it was fine, because the trig was
checking the wrong contact**.

- **Make the captive end a SHORT cap right at the tip, not a long socket.** The pivot moves as
  far from the clip as possible (51 mm and 4.5°, against 19 mm and 12°) and there is barely any
  length inside for the tip to foul.
- **Drop the cap's cavity floor below the seated height** by ≥ `(cap length) × tan(swing)`.
- **A conforming pocket and a swing-in are mutually exclusive.** If the pocket follows the part
  at its seated height, insertion becomes **axial**: snap the free end in first, then slide
  forward to a blind stop. Give the pocket the **same taper as the part** so the faces stay
  parallel and it slides instead of wedging. **Decide which you want before designing the
  clip** — it changes the motion the user performs.
- **Re-check the decision when the layout moves.** A lip was rejected at a 14 mm span (~20° of
  swing) and became available at 38 mm (9°). The constraint is the clip's **inboard** end, the
  point nearest the pivot, which rises least.
- **Check the grip band against holes and slots in the part, not just its outside profile.** A
  pinch bears on the side faces, so a lanyard slot through those faces is a hole in the contact
  patch. On the prybar, 55% of the contact length sat over an opening with the arm tips landing
  on the slot edges. Two numbers, invisible in a render.

---

## 5. Force budget — press force and pull-out

### 5.1 Budget the INSERTION FORCE, not just the stress
*Cost: two parts signed off at 95–105% of stress limit, clear on interference, zero sticky
zone — and reported as "there is no way this pry bar will fit" and "the Zippo still pops the
lighter out", with **"stop worrying about tension, and make the parts fit."***

What a person feels is `insertion force = 2 * k * (lip_over + PRINT_BIAS)`, and `k` had been
quietly maximised because every earlier fix spent its budget on retention. The prybar wanted
**56 N** to press a 6 mm bar between two 12 mm arms: both thumbs, hard, on a part with nothing
to grip.

1. **Print the push force on the same line as the pull force**, so the trade is visible when it
   is being made and not after a print. Aim ~25–35 N total for a part held in two fingers.
2. **Retention is a RATIO.** State it as multiples of the part's weight. Past ~20× you are
   paying with the user's thumbs.
3. **When a part comes back "it doesn't fit", open every clearance and cut the reach in ONE
   pass.** Do not re-derive the mechanism first. Clearances are cheap and reversible and they
   cover several candidate causes at once. *(But see §1.1 — that pass cut four reaches below
   the printability floor. Re-assert the floor on the way down.)*
4. Stress falls as a free side effect, because **the splay IS the deflection**.

### 5.2 `pull = 2 * F * 1.8` is WRONG, and it was in every band script
1.8 is the wedge factor of a 45° face with friction — right for a lip riding over a flat or a
small corner, **badly wrong on a cylinder**, where the lip tip radius (0.40) is dwarfed by the
part radius (7.55) so **the PART sets the escape ramp**. A cylinder near its equator is a
nearly vertical wall = a nearly **horizontal** ramp.

```
splay   s(u) = sqrt(R^2 - u^2) - y_tip        u = tip height above the axis
ramp    ds/dh = u / sqrt(R^2 - u^2)
travel  u0 = sqrt(R^2 - y_tip^2)              seated-to-free lift
force   F(u) = 2*k*s*(ds/dh + mu) / (1 - mu*ds/dh),   k = F_arm/(R - y_tip)
```

At `lip_over` 0.35 that ramp ran **18° at first touch down to 0° at release** — at or under
arctan(µ) throughout — so friction did the holding and **the resistance died away exactly as
the part was escaping**. Peak **11 N, not the 52 N on record: 4.8× optimistic**, ~3.6× on the
Zippo. **Every "kg of pull-out" written before 2026-10-28 is 3–5× high.**

| escape geometry | pull-out ÷ press force |
|---|---|
| smooth 7.55 mm cylinder | **0.38** |
| 2.8 mm corner (Zippo) | **0.62** |
| lip reaching past the corner onto the flat | `2F(1+µ)/(1-µ)` — the strong case |

Two keepers: **pull-out on a smooth cylinder is only ~0.4× the press force whatever the
clearances are**, so a light press and a firm hold cannot coexist there and no amount of
`cav_clear` or `lip_clear` moves the ratio; and **the travel is pure geometry**,
`sqrt(R² - y_tip²)` = 2.5–3.5 mm on a 15 mm part, so **a cylinder holder always moves before it
bites**. Shrinking the travel means shrinking the reach, which is the one thing that must not
shrink.

> **Guardrail — `escape_curve()`**, in `modgrid_round_holder.py`,
> `modgrid_zippo_clip.py` and `modgrid_skeletool_holder.py`. Print the **ramp angle beside the
> force**. The Skeletool's version has **two branches** — if the tip reaches past the corner it
> rides its own 45° face, else the corner-arc integral with the slope **capped at `1/µ` (73°)**,
> past which the contact self-locks and the formula would otherwise report infinite force.

### 5.3 A throat cannot be opened without deleting the capture
**Opening `cav_clear` does NOT open the throat.** `lip_tip_y = part_w/2 - lip_over`, so the
narrowest point stays put whatever the cavity does — `bead_r` simply grows with `cav_hw` to
keep reaching the same distance past the part's face. That is not a bug: a snap retains by
having its throat narrower than the part. **If the part still will not pass, the number that is
wrong is the PART DIMENSION, not a clearance** — and raising it moves the bead, the section and
the reference body together. `exports/PRYBAR FIT GAUGE.stl` answers that in one print.

### 5.4 On a cylinder, several things are free that are not on a flat-walled part
Put a cylinder through the lip-placement formula (`w = D`, `R = D/2`,
`part_top = base_t + D`) and it collapses to `K = sqrt(2)*(D/2 + clear) + D/2 + base_t`, whose
distance to the axis minus `D/2` is **exactly `clear`, for any D**. So:

- **No corner-radius estimate and no radius sweep are needed** — the only uncertain number is
  the **diameter**, and a part `dia_err` oversize eats `0.854 * dia_err` of `lip_clear`. Size
  `lip_clear` from how well the diameter is known, and **sweep the diameter instead**.
- **`cav_hw` cancels out of `lip_zt` and out of `K`**, so cradle clearance changes the splay,
  the push force, the stress and the seated lip clearance by **exactly nothing** — only the
  band gets wider. (The same cancellation holds on the flat-walled bands: moving the Zippo's
  walls in 1 mm changed none of its forces and only narrowed the band.)
- **A cylinder self-centres at the bottom of a larger cylindrical cradle**, so that clearance
  buys tolerance without buying rattle.

**But that formula is about an INFINITE PLANE — see §3.5, which cost three prints.**

---

## 6. Axial stops and features inside cavities

### 6.1 Measure EVERY diameter of a multi-piece part, and then the step is free
*Cost: one of the Olight's two bands had never touched the light.*

It had been modelled as one 15.10 cylinder for 55 mm. That measurement was real — of the
**keyring cap**. The body is **13.25**, so the cradle sat **0.93 mm clear of it at every
point**, and the interference sweep reported CLEAR at every lift height — correctly, against a
reference body that does not exist.

> **A reference model built from one measurement of a multi-piece part will confirm whatever
> you assumed.**

**The step is a ready-made axial stop.** Bore the second band for the **smaller** section and
put its **bed face** at the step: the part's own shoulder lands on it (0.76–0.92 mm of
engagement over 160° of arc, measured on the solid). **Prefer a stop made of a face the part
already has** — no clearance budget, no overhang, nothing to fillet, and it cannot be eaten by
a fillet.

Three traps, all of which bit:
- **Do not chamfer the stop face's inner edge.** A 0.50 bed chamfer takes most of a 0.76 mm
  engagement — the same rule as the barb catch. Leave it sharp: elephant foot there *adds*
  material to the stop, and the part drops in radially so a tight mouth costs nothing.
- **A longer band still gets only ONE row of mount legs.** A second row a whole grid pitch
  along is right on the plate and wrong in the printer — the band stands on its bed face, so
  that row starts 16 mm **up** the print as an island in mid-air.
- **Check how much of the grip band actually lands on the gripped section.** The band is where
  the grid pitch puts it; the step is where the part puts it. They do not have to agree, and
  the overlap is what the flexure numbers are really computed on.

### 6.2 A first-layer chamfer on a through-hole opens its underside, which is where a snap barb catches
On the baseplate a 0.5 mm bed chamfer left the barb only **0.19 mm** of catch; 0.3 mm gives
0.39. **Keep the bed chamfer as small as elephant foot allows wherever something latches under
the part** — and do not chamfer an internal relief slot at all (0.5 off both sides of a 1.2 mm
slot collapses it, and elephant foot inside a relief slot is harmless anyway).

### 6.3 A feature added INSIDE a cavity must respect the cavity's radii AND its chamfer
The Zippo's C-stop was positioned back from `cav_hw` — but **the floor only stays FLAT out to
`cav_hw - cav_r`**, so the limbs ended 0.50 mm from the bottom corner arc and the blend fillet
had nowhere to live.

> **Dimension a feature inside a cavity from the cavity's FLAT extent, not its nominal half
> width**, then set it back by the blend radius plus a margin:
> `stop_hw = cav_hw - cav_r - stop_blend - stop_gap`.

> **Add the feature BEFORE the first-layer chamfer.** Added after, the chamfer has already run
> round the cavity floor and the new feature sits over it — an undercut groove along its base
> and an unchamfered island inside a chamfered pocket. Check it by the count: **"16 edges, 2
> left sharp" → "32 edges, 0 left sharp"**. (This is the **opposite** of the rule for mount
> **legs**, which must come *after*, because they break the body's OUTER outline and terminate
> the chamfer chain. A feature inside the cavity only adds an inner loop, so it is safe.)

### 6.4 The three things that make a retention stop a C rather than a wall
1. Open at the top, so a finger reaches through the bed face to push the part out.
2. **Its limbs stop `stop_gap` short of the cavity wall, so it attaches to the solid BASE and
   never to the flexing arms.** A stop reaching the walls braces them over its own length,
   right at the root where the bending moment peaks. *(This is the one that matters.)*
3. It is the first few mm of the print, flat on the plate — no overhang, better adhesion.

Keep the **gripping** length at the full `band_len` and make the body `band_len + stop_t`:
force scales with the loaded width and stress does not scale with width at all, so the flexure
numbers stay valid.

---

## 7. Printability, orientation and supports

### 7.1 "No overhangs" is not the same as "no support"
The pen clip was printed standing on end, where **every face of every cross-section is
vertical** — genuinely zero overhangs. It still needed support, because the mount legs were
**centred** along the part: their 4.90 mm extent began 4.55 mm up the print, so a
4.64 × 4.90 island appeared in mid-air.

> **Overhang analysis is per-cross-section; this is a different question. Ask it separately:
> for every feature, does it either reach the bed itself, or sit on top of something that
> does?**

A feature spanning only part of the build axis must be pushed to the **bed end** of that span.
Stopping early is free (it is just a top face); **starting late costs support**.

Related: once the legs reached the bed face the first-layer chamfer failed
(`ASM_BL_CAP_COMPLEX`), because the legs broke the body outline into segments and the chamfer
chain terminated mid-face. **Apply the chamfer before adding the legs** — their own bed edges
stay sharp, which is correct anyway since a 0.94 mm leg cannot take a 0.5 mm chamfer.

### 7.2 Overhangs, bridges, holes
| Rule | Value |
|---|---|
| Self-supporting overhang | **≤ 45° from vertical** |
| Downward-facing edge | **CHAMFER, not fillet.** A fillet is tangent to horizontal where it meets the overhang, so its last stretch is flat and still needs a sliver of support. A 45° chamfer holds its angle. Fillets are fine on vertical and upward-facing edges. |
| Flat ceiling / ledge | Not self-supporting — redesign (chamfer, wedge, teardrop) |
| Bridge anchored both ends | OK to ~**10–15 mm** in ABS (Slant says most machines do 25–50; we don't bank it) |
| Cantilever | Treat as an overhang |
| Horizontal hole | **Teardrop** — round bottom, two 45° lines meeting in a point on top |
| Horizontal pin | Same teardrop, **point down**, tip truncated to a ~0.4 mm flat for a sprue to land on |
| Internal cavity | The inside need not match the outside. Keep the cosmetic exterior and make the interior pointed or conical. |

**Design the overhang out first** (fill it solid → chamfer → reorient), **then** model your own
support, and never rely on the slicer. Every cantilevered tab, ear or boss gets a 45° gusset
underneath. Loops and hooks: chamfer each downward face so there is no flat ceiling.

### 7.3 Designed-in fins and sprues
| Parameter | Value |
|---|---|
| Fin thickness | 0.8–1.2 mm small parts; ~2 mm on large or tall ones |
| Fin-to-part XY gap | 0.4–0.8 mm (Slant: 0.5–1) |
| Fin height | ≥ ½, ideally ¾ of the supported face; ≥ 1 fin per ~80–100 mm of face width |
| Sprue contact | 0.2–0.4 mm tapered, or a 1 × 1 mm tooth for break-off fins; ≥ 2 perimeters wide |
| **Sprue direction** | **HORIZONTAL in the print frame**, never perpendicular to a tilted face. Horizontal sprues print as one continuous extrusion and fuse; perpendicular ones become isolated tips that snap off mid-print and blob. Slant calls it "a universal mistake". |
| Break notch | Small notch in each sprue next to the part so it snaps flush |
| Fin foot | Flat plate on the bed, rounded corners, chamfer gusset at the root (≥ ~30 mm tall fins) |
| Bed contact | **Never stand a part on a sharp edge** — chamfer it to a real flat strip |

**The Z-gap trick does not scale to a broad flat face.** A 0.2 mm gap under a 5.26 × 5.0 mm
underside makes that whole face an island printed into air relying on droop; the gap only
equals one layer if it lands on the layer grid (one empty layer at 0.20 mm, zero at 0.25), and
a slicer's static check flags it regardless. Under a broad face, **make the support touch**:
two 0.6 mm ridges at the face's edges overlapping the part ~0.05 mm, spaced so the printer can
bridge between them, ≤ 0.3 mm of overhang outboard, landed on a non-critical face near corners.

Model supports as separate `Support - …` bodies, overlap ~0.05 mm, **export them together with
the part**, and leave them out of interference checks.

### 7.4 Mouse ears only on SHARP bed corners
A rounded footprint corner has no stress concentration to lift, so an ear there is redundant —
it adds a part to trim and a scar to clean. **Round the corners instead; if they are already
rounded, no ears.** (The MOD-GRID 12x8 baseplate is R3 all round and carries none.)

Where they are needed: separate `Support - Mouse Ear …` bodies, discs **0.4 mm thick** (2
layers), **R6–8**, centre pushed ~2 mm outward diagonally. Keep them off bed-level slots.

### 7.5 First layer, warping, material
- Chamfer every bed-contact edge **0.5–1 mm**, including hole and cutout edges — subject to
  §6.2 wherever something catches underneath.
- ABS shrinkage **0.5–0.7%**: ~1.5 mm over 254 mm. Calibrate shrink compensation.
- Chamber heat-soaked to **≥ 50–60 °C** (30–45 min), bed **100–110 °C**, part cooling **off**
  for the first ~5 layers and ≤ 20–30% after, panels closed, clean textured PEI, slow first
  layer.
- Heat-set inserts in ABS: 220–240 °C. Gluing: acetone or ABS slurry solvent-welds strongest.
- Put the largest flat face on the bed; round vertical edges for cleaner toolpaths.

---

## 8. Verification — what a check must actually look at

### 8.1 Verifying a cavity against an ANALYTIC MODEL of the part is not verification
The prybar's conformity probes read a clean +0.20 clearance the whole way while the real bodies
overlapped by **15.6 mm³** — because the probe and the pocket used the **same wrong section
formula**. Intersect the actual bodies with `TemporaryBRepManager`; **the bounding box of the
overlap points straight at the cause.**

> Build a **reference model** of the part being held, named `Reference - …`, kept out of the
> export, and check fitment **by interference, not arithmetic**. Rotate a temp copy to the
> insertion angle and intersect it with each holder, sampling the swing at several angles and
> going ~25% past the needed one. That caught two errors in one run that hand calculation had
> missed.

### 8.2 Measure on real faces, not with probes aimed where you expect trouble
The root-web check *existed*. It walked down from the slot toward the bed, found **3.28 mm**,
and passed — **a true number about the wrong piece of material** (§2.1). An analytic probe only
looks where you point it; `measureMinimumDistance` against every face finds the narrowest place
whatever the cause, **including causes nobody thought of**.

Probe artefact worth knowing: **a point sampled exactly ON a face returns "on surface" (1),
not "inside" (0)**, so a walk that starts there bails immediately and reports a false
near-zero. Sample 0.02 inside the face.

### 8.3 A face selected by RADIUS alone will eventually select the wrong face
`measure_root_web()` took "every cylinder within 0.05 of `relief_w/2`" as a slot root cap.
Cutting the prybar's `lip_over` to 0.08 made `bead_r` 0.58 against a `relief_w/2` of 0.60 — so
the **capture bead** was measured as a slot cap and the build cried
`root web ABOVE cap: 0.300 mm ** THE ARM HANGS OFF THIS **` on a part whose web was 1.572.
**A real alarm on imaginary geometry costs as much as no alarm.**

> **Add a POSITION test to any check that picks geometry by one scalar.** The caps are the only
> such cylinders *below the cavity floor*, so one `origin.z < base_t` filter disambiguates them
> permanently.

### 8.3b A check must measure the MATERIAL, not the centres (2026-11-16)
The round holder's pre-cut guard reported `column between the two slots 1.24 mm OK` on a band
whose column measured **0.050 mm** on the solid. The formula was
`2 * r_mid * cos(theta)` — the distance between the two slot root **cap centres** — so it was
one whole `relief_w` too big, every time, on every band ever built with it. The measured
`verify_band` column caught it; the guard that exists to catch it early did not.

> Same family as §8.3: a guard that names a quantity must compute *that* quantity. Subtract the
> feature's own size. `col = 2 * r_mid * cos(theta) - relief_w`.

**And the geometric fact it was hiding:** on a band whose relief slots are concentric with the
bore, **a SMALLER bore can wrap LESS deeply, not more.** `r_mid` shrinks with the bore, so the
two slot roots sit closer to the centreline at the same angle. Band B's 13.25 bore caps out at
−82°, against −80° on Band A's 15.10 — the first attempt at −86° put the slots 0.041 mm apart
and the measured root web read **0.74 / 0.82 / 0.04** against floors of 1.5 / 1.2 / 1.2.

### 8.4 A cut that SPLITS a body still reports 0 unhealthy
Deepening the Zippo relief slot to −150° ran its inner arc through the cavity floor and cut
each band into loose pieces. The timeline was clean; **only the bounding box and the volume
showed it.**

> **Count `root.bRepBodies` before and after every cut**, and check the geometry that
> constrains it (here: the slot's inner arc at `ccz + (cav_r+arm_t)*sin(theta)` must stay below
> the cavity floor).

### 8.5 A chamfer bigger than the land it sits on silently eats the part
0.5 mm on a 0.50 mm land **halved** the prybar clip's volume and deleted its whole outer rail —
and the timeline still reported **0 unhealthy**. Severe self-intersection shows first as
`ASM_BL_NON_MAN_EDVERT`.

> **Skip any edge shorter than `2 * chamfer + margin`, and check volume and bounding box after
> every chamfer** — not just health. **Chamfering a face only chamfers its OUTER loop**, so a
> face with 48 holes gets the perimeter done and all 48 mouths left sharp. **Verify by volume,
> not by eye.**

### 8.6 Log the bounding box and volume after EVERY feature
It localises a bad feature in one run. Inspecting only the finished body cost several rounds of
guessing. Print the "N chamfer edges, M left sharp" count too — it is what makes §6.3 and §1.4
visible.

### 8.7 When a fit fails twice, stop adjusting clearances and sweep the SHAPE
The Zippo failed three times while the cross-section was assumed to be an obround. One
interference sweep against a parametric case settled it in a single run: it fitted only a true
semicircle (R6.47 → 0.003 mm³) and jammed on anything squarer (R3.00 → 136 mm³), **with the
overlap in the LOWER half**, which matched the reported symptom exactly. **Sweeping the
uncertain *shape* parameter finds what repeated clearance tweaks never will.**

### 8.8 Apply a rule to EVERY instance, not the one you are thinking about
The prybar's nose pocket got the +0.14 bias correction and the clip cavity did not, so a 6.30
cavity on a 6.00 bar printed to 0.08/side and would not seat.

> **When a bias or clearance rule comes up, grep the script for every clearance parameter and
> fix them all in one go.**

---

## 9. Process rules — working from a failure report

1. **Trust the physical report over the model.** If Rob's hands contradict the arithmetic, the
   arithmetic is wrong. Every single time so far.
2. **The same complaint twice means the wrong knob.** Stop turning it and go measure what the
   part is actually touching. Two defensible tightenings that change nothing are the signature
   of a defect in a **derivation**, not in a value.
3. **Ask which DIRECTION** before changing anything (§4.1).
4. **Ask which parts already feel right, and diff against them.** *"The prybar is a super tight
   fit, the pill bottle is a super tight fit, the pen is a super tight fit… the flashlight has
   never been right"* located the defect in one message, after five prints. The working parts
   are the control group.
5. **Rob wants a TIGHT fit.** *"I like the tight fit."* When a tolerance decision is balanced,
   go tight.
6. **Rob exports the STLs himself** from Fusion. Do not run exports.
7. **State what changed and what must be reprinted.** A parameter that feeds `band_hw` changes
   bodies you were not thinking about.
8. **Warn before a timeline rebuild** (`markerPosition = 0; deleteAllAfterMarker()`) — it wipes
   manual edits.
9. **When you promote a special-cased body to the general builder, re-check every exception
   the special case carried (2026-11-16).** The Olight's Band B was an open cradle with its own
   builder, which deliberately left the channel mouth **unchamfered** so a 0.50 chamfer could
   not eat a 0.86 mm axial stop. Turning it into a snap band routed it through the generic
   `build_band`, which chamfers the whole bed outline — silently undoing that decision and
   taking the arm's anchorage down to 1.10 against a 1.5 floor with it. The exceptions a
   special case carries are the *reasons* it was special. List them before deleting it.
10. **Capture every new rule here and in `research/`** with the date, the failure, and the
   guardrail. A rule without the failure it came from gets argued away later.

---

## 10. Fusion API gotchas

**Scripting through the MCP server**
- Entry point is `def run(_context)`; **`print()` is the only output channel**; **never call
  `ui.messageBox`** (it blocks the call); **do not catch exceptions** — the traceback is the
  only debugging signal.
- **A script that raises rolls back everything it did**, even work that built fine before the
  error. Keep reporting and verification code defensive and re-check the timeline after any
  failure.
- `readOnly: true` scripts cannot change visibility (`isLightBulbOn`) or anything else.
- The server is **built into Fusion** (`NsMCP10.dylib`), not an add-in — it will not appear
  under Scripts and Add-Ins. Keys `MCPServerEnabled` / `MCPServerPort`, endpoint
  `http://127.0.0.1:27182/mcp`. **If it accepts connections but closes them with no response,
  restart Fusion.**

**Sketches**
- **Sketch geometry is created in SKETCH SPACE, not world space.** Convert with
  `sketch.modelToSketchSpace(point)`. World coords on anything but XY put geometry out of
  plane; the feature still builds and the profile breaks later with *"Curves tracked in old
  profile are not coplanar anymore"*.
- **Numeric sketch geometry is not parametric.** Points passed to `addTwoPointRectangle` are
  frozen numbers; only extrude distances and pattern counts follow expressions. For a sketch
  that must resize, add driving dimensions (`addDistanceDimension`, then
  `dim.parameter.expression = 'plate_x'`) and anchor a corner coincident to
  `sketch.originPoint`.
- **A parameter sweep must REBUILD the body** for the same reason — re-expressing `case_r` gave
  an identical answer at every radius. Build a `TemporaryBRepManager` body per value.
- **`addByThreePoints` may swap an arc's start and end** to keep its sweep direction, so on a
  mirrored side `arc.endSketchPoint` is **not** the point you passed last. Never close a loop
  by referencing an arc's SketchPoints — draw every connecting line from **explicit
  coordinates** and let the solver merge coincident points. Symptom: one side builds correctly
  and the mirror closes across itself.
- **A point added only to CLOSE a profile must not sit on the functional line.** The reference
  bar's wedge started 1 mm clear of the top face "to be safe", which tilted the line
  0.32 → 0.38/mm and moved the wedge start 2.6 mm. **Close the profile on the far side, away
  from the edge that matters.**
- Relief slots need **rounded ends** — a straight radial end cut leaves a sharp V-notch, ragged
  and a stress riser. Build them as a sector plus a capping circle at each end; capping with
  three-point arcs malformed on the mirrored side.

**Features**
- Naming a sketch and its feature the same makes Fusion rename the feature to `Name (1)`. Look
  features up by substring, or keep references from creation.
- For multi-body designs, **set `participantBodies` on every JOIN/CUT extrude**.
- **Make cuts direction-agnostic** where the far side meets no material:
  `setTwoSidesExtent(d, d)` avoids depending on which way a profile's normal points.
- The root **XZ** plane's normal is **+Y**. Check `plane.geometry.normal` before choosing an
  offset or extrude direction.
- **A tapered cut landing exactly tangent to an existing hole wall** fails with
  `EXTRUDE_CREATION_FAIL_ERROR`. Use `holeFeatures.createCountersinkInput(...)` and let it cut
  the clearance hole too.
- **A chamfer's EDGE SELECTION is not authoritative while tangent chaining is on (2026-11-16).**
  `addEqualDistanceChamferEdgeSet(edges, d, True)` — that third argument is `isTangentChain`,
  and it means the chamfer runs on into any edge tangent to one you picked. The round holder's
  cavity walls are tangent to its bore at the equator *by design*, so excluding the bore arc
  from the selection changed nothing: the chamfer arrived via the wall edge and ate 0.50 mm of
  the part's axial stop and of the arm's anchorage. **Passing `False` is not the fix** — the
  chain then ends ON that tangent point and the feature fails outright with
  `ASM_BL_END_TOO_CMPLX`. Exclude the whole tangent group instead, and verify by the edge
  count.
- **To chamfer a hole that gets patterned, chamfer one cell then pattern the cut and the
  chamfer together.** Selecting edges after the pattern stores one reference per edge and every
  one breaks ("Edge N missing") as soon as the count shrinks.
- `BRepBody.pointContainment`: **0 = inside, 1 = on the surface, 2 = outside.**

**Documents**
- **The root component cannot be renamed** (`root component name cannot be changed`). Name the
  document instead.
- `Document.saveAs()` returns a **bool** (check it) and the cloud publish is **asynchronous** —
  the file will not appear in `folder.dataFiles` in the same script, so a save-landed check
  right afterwards is a false alarm. Re-check in a later call.
- **Never `dataFile.deleteMe()` then `saveAs()` under the same name.** The delete is
  asynchronous and can land *after* the save, silently taking the new file with it — and it can
  wedge the lineage server-side (`PIM data publish is not finished.`), after which the document
  can no longer produce a temp file and even STEP/STL export fails with
  `InternalValidationError` / `Failed to get temporary file`. **To replace a design: open the
  existing document, `timeline.markerPosition = 0; deleteAllAfterMarker()`, rebuild,
  `doc.save()` a new version.**
- **Name a document by its variant** (`MOD-GRID Baseplate 12x8`) only where the variant is
  stable. The pill holder's `17x40` name orphaned a document the moment the size changed.
- **Meshes imported into these documents can be 10× oversize** (the MOD-GRID files are). Check
  a known dimension before trusting any measurement off an imported mesh.

---

## 11. Checklist before calling a part print-ready

1. Fix the **print orientation** of every body.
2. In that orientation, scan for: flat downward faces, cantilevers, horizontal round
   holes/pins, bridges > 10–15 mm, bed-level slots < 1 mm.
3. Ask §7.1 separately: **does every feature reach the bed or sit on something that does?**
4. Ask §4.2: **which way does the working load pull, and is that along or across layers?**
5. Redesign first (fill solid, chamfer, gusset, wedge, teardrop); only then model a fin with
   **horizontal** sprues.
6. First-layer chamfer on bed-contact edges — **minus** anything a barb or a shoulder catches
   under (§6.2, §6.1).
7. Mouse ears on **sharp** bed corners only.
8. Assert the printability floor: `lip_over > lip_tipr`, `lip_over >= 0.80`, every flexure wall
   an integer multiple of 0.40 and ≥ 1.60.
9. Run the numeric checks and read them as a set:
   - `measure_root_web()` — above / below / beside, on real faces
   - `flexure_check()` — stress as printed, **both** biases applied, against 15.0 MPa
   - **press force** and `escape_curve()` **pull-out with the ramp angle**, pull quoted as a
     multiple of the part's weight
   - `seat_check()` — sticky zone **0.00**, swept across the plausible corner radius, with
     `lip_clear` **asserted** against the model in the direction it is defined in
   - interference against the `Reference - …` body, seated and through the insertion motion
   - body **count**, **volume** and **bounding box** after every cut and chamfer; chamfer
     "N edges, M left sharp"
10. State what changed, which bodies moved, and what has to be reprinted.

---

## 12. Current state of the parts

Forces are press / pull-out, pull-out from `escape_curve()` (the old `2*F*1.8` numbers are
withdrawn — §5.2). Stress is as printed against the 15.0 MPa rule.

| part | rev | press | pull-out | stress | note |
|---|---|---|---|---|---|
| Prybar holder | 2026-10-26 | 33 N | 6.1 kg = 180× | 11.4 MPa / 76% | **Rob: super tight.** Reach 0.08 survives because the capture is a 1.08 mm tangent bead (§1.2). Left alone. |
| Pen clip 9.84 | — | — | — | ~16 MPa | **Rob: super tight.** 2.00 mm constant arc. Left alone. |
| Pill bottle holder | 2026-10-27 | 26 N | 1.0 kg = 33× | 11.1 MPa / 74% | **Rob: super tight.** Grips by its **bore**; its lip does not print either. Section physically confirmed on the bottle — do not "fix" it. (The 4.7 kg on record was the retracted ×1.8 model; `escape_curve` says 1.0.) |
| Zippo clip | **G** | 31 N | 2.0 kg = 31× | 17.3 MPa / 116% | `lip_over` 0.80, arms 2.40 → 1.60. Root web 1.64 **at the floor**. Band A (with C-stop) **at the LOW end**. Both bands reprint. |
| Skeletool holder | **D** | 22 N | 4.2 / 2.1 / 1.4 kg at `tool_r` 0.20 / 1.50 / 3.00 | 16.5 MPa / 110% | Press went **down** while grip went **up**. Best geometry in the set — nearly square, so the lip rides its own 45° cam. Both bodies reprint. |
| Olight iMini 2 — Band A (cap) | **F** | 50 N | 2.3 kg = 115× | 24.3 MPa / **162%** | Unchanged from rev E. Deliberate overstress: a printable lip, a tight bore and low stress cannot coexist on a 15 mm cylinder. Pressed **once** — the cap lives in the holder. |
| Olight iMini 2 — Band B (body) | **F** | 28 N | 1.3 kg = 68× | 22.0 MPa / **147%** | **New: both ends now clamp.** Was an open cradle with zero radial retention. This is the **daily-cycled** flexure, so 147% is the number to watch. Band B **at the LOW end**. |

**Accepted exceptions, and why**
- **Olight at 162% of the stress rule.** Rob asked for tight, the cap is pressed in once, and
  the failures that have actually broken arms here were starved root webs (0.016–0.162 mm), not
  bending. `lip_over` 0.60 gives ~38 N / 1.6 kg at 125%; the principled fix is curling the
  relief slots outboard for a −110° wrap (31 N, 119%) — not implemented.
- **Zippo `cav_clear` 0.40** = 0.13/side printed, below the 0.50 sliding-fit floor. Accepted
  because the case is measured at 38.05 and the lip does the holding. First knob to open if it
  binds going down the walls.
- **Olight `cav_clear` 0.14** so the bore prints 15.10 **line-to-line** on the cap. 0.00 was
  tried and printed 0.14 **under**.

**Do not thin further:** Zippo root web **1.64** and Skeletool thinnest arm **1.59** are both at
their floors at a −110° wrap.

**Numbers still unmeasured that cost real grip**
1. **Skeletool handle-edge corner radius** — decides between 4.2 kg and 1.4 kg. The highest-value
   caliper reading left in the project.
2. **Zippo case corner radius** — worth ~0.6 mm of free lift (0.50 at R2.00, 1.10 at the
   estimated R2.80).
3. **Skeletool `tool_w` / `tool_t`** (31.50 × 13.20, Leatherman spec; multitool.org says 33 × 16).
4. **Skeletool band: 14 chamfer edges, 2 left sharp** — not localised, not chased.

---

## 13. Rule index

| § | Rule | Cost |
|---|---|---|
| 1.1 | A retention feature must be ≥ 1 extrusion width deep, 2 to print crisply | 5 prints, no detent at all |
| 1.2 | Prefer a capture sized by the CAVITY, not by the reach | the same 5 |
| 2.1 | A snap arm fails where it is ANCHORED | an arm snapped on first insertion |
| 2.2 | Past −90° the root web collapses; `base_t` does not help | a band cut into loose pieces |
| 2.5 | An arm between two voids prints THICKER | ~20% under-reported insertion force |
| 3.1 | Check for SELF-LOCKING, not just clearance and stress | a lighter that would not seat |
| 3.2 | "Above the top face" needs the TIP to reach `w/2 - part_r` | capture entirely on an unmeasured arc |
| 3.5 | A clearance derived against an INFINITE face is not the one you built | 3 prints, 1.52 mm of rattle |
| 4.1 | "Loose" is a DIRECTION — ask which one | 3 radial fixes for an axial defect |
| 4.2 | Check the LOAD PATH against layer direction | a sheared lip, 59 MPa across layers |
| 4.3 | Can the part even TRANSMIT the insertion force? | a magnet that let go first |
| 5.1 | Budget the INSERTION FORCE, not just the stress | "there is no way this will fit" |
| 5.2 | `pull = 2*F*1.8` is wrong on a curve | every pull-out number 3–5× high |
| 6.1 | Measure EVERY diameter of a multi-piece part | one band of two was decorative |
| 7.1 | "No overhangs" ≠ "no support" | a floating island, flagged by the slicer |
| 8.1 | Verifying against an analytic model is not verification | 15.6 mm³ of overlap read as +0.20 clear |
| 8.3 | A face picked by RADIUS alone finds the wrong face | a false alarm on imaginary geometry |
| 8.3b | A check must measure the MATERIAL, not the centres | "1.24 OK" on a 0.050 mm column |
| 9.9 | Re-check a special case's exceptions when you generalise it | a chamfer ate an axial stop and an anchorage |
| 8.4 | A cut that splits a body still reports 0 unhealthy | caught only by volume |
| 8.5 | A chamfer bigger than its land eats the part | half a body, 0 unhealthy |
| 9.2 | The same complaint twice means the wrong knob | the through-line of this whole file |
