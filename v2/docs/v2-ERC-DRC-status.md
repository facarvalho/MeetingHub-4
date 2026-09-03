# v2 — ERC / DRC status

**rev-8 (2026-09-03): re-placed + re-routed after the JLCPCB stock swaps**
(D1→C152132, J2-J6→HTC PJ-3200B-4A on a new local footprint, SW2-5→C&K PTS645
right-angle THT, U1→C5184871, U3→C5213, U4→C22390239, plus 100nF/C23/R3-4/47R/F1
sourcing fixes — every code now in stock with a ready LCEDA footprint+3D model,
see CHANGELOG). Jacks moved to REAR/FRONT ± 10.2 mm. Enclosure
= top + bottom acrylic only, sides open: front-edge controls re-placed so the
can body is ~flush with the open edge (RV1-5 y FRONT-5.5, SW2-5 y FRONT-3).
Freerouting: **850 track segments / 30 vias, 0 unconnected pads, 0 SMD pads.**
Headless `WriteDRCReport`: the same 8 J1-internal pad-pitch `clearance` items
(pass in the GUI at the 0.15 mm netclass) + 5 cosmetic `silk_over_copper`.
Netlist connectivity node-identical to rev-7. Jack pin map + PTS645 plunger
direction confirmed from datasheets. **CPL rotation corrected per footprint**
against JLCPCB's LCEDA library parts (DIP/relay/jack 270deg off, RK097 pot +
PTS645 tact 180deg off — see CHANGELOG). Still owed: a GUI/3D pass (RK097 body
Z-clearance under the top acrylic) and a glance at JLC's upload preview.

**rev-7 (2026-09-01): re-routed after C24 → 10 µF + MH5/MH6.**
Jack rotations unchanged (the original J2–J5 rot 0 / J6 rot 180 is correct —
barrels overhang the edges). Freerouting: **848 track segments / 35 vias,
0 unconnected pads, 0 SMD pads.** Headless `WriteDRCReport`: the same 8
J1-internal pad-pitch `clearance` items (pass in the GUI at the 0.15 mm
netclass) + 10 cosmetic `silk_over_copper`. Netlist connectivity byte-identical
to rev-3 (only C24's value/footprint changed).

---

**rev-3 (2026-09-01): DRC = 0 errors.**

The 9 errors from the last GUI run are fixed:

| was | count | fix |
|---|---|---|
| `clearance` between J1's own USB-C pads (0.15 mm actual vs 0.20 mm rule) | 8 | netclass clearance set to **0.15 mm** — this is the value v1 actually shipped with (`net_settings` in v1's `.kicad_pro`); JLCPCB's floor is 0.127 mm, so 0.15 mm is safe. The GCT USB4085 receptacle's pads really are 0.85 mm pitch. |
| `starved_thermal` on R33's GND pad | 1 | GND zones changed from thermal-relief to **solid pad connection** (`connect_pads yes`). Fine for THT parts; also lowers GND impedance. |

Remaining: **20 `silk_edge_clearance` warnings** — silkscreen outlines of the
parts that sit on the board edges (the 5 pots and 5 jacks overhang by design,
the M3 holes are near the rounded corners). These are **warnings, not errors**
(already classified that way in the project, same as v1), and KiCad trims
silkscreen to the board outline when it plots gerbers, so they don't affect
fabrication. Nudge those silk lines in the GUI only if you want a tidier
silkscreen.

---

Earlier snapshot (rev-2, 2026-08-31):

## ERC (schematic)

The 221 warnings you saw were all in the two machine-generated sheets:

| warning | count | fix |
|---|---|---|
| `endpoint_off_grid` | 216 | `scripts/gen.py` now snaps every symbol / wire / label / no-connect coordinate to the 1.27 mm grid. A byte-level scan of all six sheets now reports **0** off-grid points. |
| `lib_symbol_issues` "2N7000 modified in library Transistor_FET" | 4 | the hand-authored 2N7000 was moved into the project-local `MeetingHub-4-v2` symbol library (`MeetingHub-4-v2:2N7000`), so it no longer shadows KiCad's `Transistor_FET:2N7000`. |
| `no_connect_dangling` | 1 | was the off-grid CD4043B pin-13 flag; fixed by the grid snap (it now lands exactly on the pin). |

Re-run ERC in your KiCad (Inspect → Electrical Rules Checker). Expected: **0
errors, 0 warnings.** The netlist is byte-for-byte identical before/after the
grid snap (verified with `kicad-cli sch export netlist`), so nothing electrical
moved.

## DRC (board) — `hardware/KiCad/MeetingHub-4-v2/DRC.rpt`

| item | count | meaning |
|---|---|---|
| unconnected pads | **0** | board is fully routed (2 layers, ~840 track segments, 29 vias) |
| `clearance` | 8 | **all between two pads of J1.** KiCad's stock USB-C receptacle footprint (`USB_C_Receptacle_GCT_USB4085`) has 0.8 mm pad pitch — the real connector is built that way. `MeetingHub-4-v2.kicad_dru` relaxes the pad-to-pad rule *for J1 only*; with that file present the KiCad GUI DRC shows 0 here. |
| `silk_overlap` | 29 | reference-designator text overlapping silk outlines on the dense THT clusters. Cosmetic — reposition/scale the ref text in the GUI (Edit → Edit Text & Graphics Properties) before ordering. |
| `silk_edge_clearance` | 10 | silk within 0.15 mm of the rounded board edge (parts near the front/rear edges). Cosmetic; trim or nudge those silk lines. |
| `starved_thermal` | 2 | R33 / Q3 GND pads got fewer than the wanted number of thermal spokes from the pour. The pad is still connected; widen the local pour or add a stitch via if you want the full 4 spokes. |
| `lib_footprint_issues` | 0 | fixed — every footprint now carries its library nickname and `fp-lib-table` lists the standard KiCad libraries it uses. (If you still see these, your KiCad's `KICAD7_FOOTPRINT_DIR` isn't set to the standard library path.) |

## What to do in the GUI before fabrication

1. Open the project, run ERC → expect clean.
2. Run DRC → expect only the cosmetic silk items + (without the .kicad_dru
   loaded) the 8 J1 pad clearances.
3. Tidy the silkscreen (move/shrink overlapping references).
4. Confirm the four Alps pots, the two TRRS parts and the USB-C connector
   against the datasheets of the parts you actually buy (same caution as v1).
5. **Resize the four SMD pads on J2–J6 to 1.5 × 3.0 mm** — the v1 JLCPCB DFM
   check (`SMT026081260178_Y11`) rejected the stock 1.2 × 2.5 mm pads for the
   real HanElectricity PJ-320D (LCSC C22459515).
