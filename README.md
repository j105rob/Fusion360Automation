# Fusion360Automation

Parametric 3D-printable parts designed in Autodesk Fusion by **script**, driven through
Fusion's built-in `fusion360` MCP server. Every part in here is built by running one Python
file against a live Fusion session — there is no hand-modelled geometry to preserve.

Printed on a Voron 2.4 (350 mm, enclosed), 0.4 mm nozzle, Polymaker ABS, **slicer supports
off**. Printability is fixed in the model, never in the slicer.

## Layout

| path | what it is |
|---|---|
| `RULES.md` | **The rulebook.** Every design rule and guardrail, as rule / the failure that produced it / the check that catches it. Plus the current state of every part. Start here. |
| `CLAUDE.md` | Working notes and the full revision history of each part, newest reasoning appended. The authority on *why* a number is what it is. |
| `research/` | Topic write-ups with sources — design-for-FDM, the MOD-GRID system spec, the 10" rack standard, Slant 3D technique notes. |
| `scripts/` | One Python file per part. Entry point is `run(_context)`; `print()` is the only output channel. |
| `exports/` | STL / STEP / f3d as printed. The record of what actually came off the plate. |

## Parts

Most of these are holders for the [MOD-GRID](https://3dedc.com) EDC plate system.

- **MOD-GRID baseplate** — parametric grid plate, verified 1x1 to 30x6
- **Prybar holder** — two-body holder for a titanium "Mighty Bar"
- **Pen clip** — top-entry snap for a 9.84 mm pen
- **Zippo clip** — two bands plus a C-shaped axial stop
- **Skeletool holder** — snap band plus a conforming blind tip pocket
- **Round-part holders** — one script, two profiles (pill bottle, Olight i Mini 2)
- **10" rack frame** — 6U open mini-rack, `rack_u` parametric
- **RPI shelf** — 1U shelf for 2× Raspberry Pi 5

## Working on these

Read `RULES.md` first. The short version of what it cost to learn:

- A retention feature must be **at least two extrusion widths** in its working dimension, or
  the slicer deletes it and the part holds nothing.
- A snap arm fails where it is **anchored**, not along its length.
- Check a snap for **self-locking** (contact angle > arctan µ), not just for clearance.
- Verify against the **real solid** with `measureMinimumDistance` and interference booleans.
  An analytic probe confirms whatever formula you fed it.
- "It's loose" is a **direction**. Ask which one before changing anything.
