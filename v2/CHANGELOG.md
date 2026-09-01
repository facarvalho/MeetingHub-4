# MeetingHub-4 v2 — changelog

## 2026-09-01 — v2 rev-7 (review follow-ups: POR + front support)

Circuit review (session dd4368fd) confirmed the 3 v1 bugs and the one-hot mic
logic are all correct in the netlist, and that the **jack orientation was
already right** (a mid-review claim that J2-J6 faced inward was mistaken and
retracted — on the PJ-320E the plug enters at the footprint's -Y barrel nub,
so J2-J5 at rot 0 / J6 at rot 180 have the barrels overhanging their edges,
openings facing out; unchanged). Two real changes, board re-routed:

- **C24 1 uF -> 10 uF** (Device:C_Polarized, CP_Radial_D5.0mm_P2.00mm, reuses
  the C43799 electrolytic already in the BOM). Stretches the power-on-reset
  pulse from ~4 ms to ~40 ms so a slow USB-C VBUS ramp still guarantees
  Q1-Q4 = 0 (mic muted) at power-on. Netlist connectivity byte-identical.
- **Added MH5, MH6** (M3) ~12 mm behind the front edge, near the left/right
  ends, to support the long front edge that carries the 5 pot knobs. BOM
  mounting-hole count 4 -> 6.
- Re-routed: **848 segments / 35 vias, 0 unconnected pads, 0 SMD pads.**
  DRC unchanged (8 J1-internal pad-pitch items that pass in the GUI at the
  0.15 mm netclass; 10 cosmetic silk-over-copper).
- BOMs + JLCPCB CPL + gerbers + schematic PDF regenerated.

Still verify on the bench: Alps RK097 terminal 1 = full-CCW end (the
pot-direction fix rests on the standard T1=CCW / T3=CW convention).

## 2026-09-01 — v2 (smaller / near-square board)

Started as a near-square re-layout of the same schematic as an earlier `v3/`
draft (larger landscape board; that draft was removed in the 2026-09-01
restructure and its history folded in here). Same schematic, symbols,
footprints, one-hot logic and all the v1 bug fixes — only the PCB layout
changed:

- **Board 192 x 156 mm** (v1 was 265 x 160) — near-square, ~29 % less area.
- Front controls (RV1-RV5, SW2-SW5, J6) pushed **~3-4 mm from the front edge**,
  bodies overhanging. Rear edge = J1 + J2-J5.
- Denser middle: mixer/hpamp resistor & cap banks in 2-3 short rows, relays
  2x2, select-logic diode matrix directly above the buttons, CD4043B rotated.
- Fully auto-routed: 0 unconnected pads, ~838 segments / 35 vias.
- DRC 0 errors (J1 pad-pitch passes at netclass 0.15 mm); ~10 cosmetic
  silk-over-copper warnings.
- BOM (v1 format, x2) + JLCPCB CPL regenerated for v2.

# MeetingHub-4 v2 — changelog

## 2026-09-01 — v2 rev-4 (smaller board, front controls at the edge, JLCPCB files)

- **Board 260 x 140 mm** (was 282x157) — tighter placement, more square.
- **Front controls hard against the front edge.** RV1-RV5 pads now ~4-6 mm
  from the edge (were ~9-21) with the bodies overhanging; SW2-SW5 and J6 the
  same. The select-logic resistor bank was moved out of the front strip.
- **All 5 pots identical**: Alps RK09712200HA horizontal (C470545).
- **All-THT jacks**: J2-J6 = PJ-320E (local footprint, silk trimmed);
  J1 stays the stock GCT USB4085. Board has 0 SMD pads.
- **DRC 0 errors** — the J1 pad-pitch clearances pass at the netclass 0.15 mm
  that v1 also used (set in .kicad_pro); only silk-over-copper warnings remain.
- **BOM now in the v1 format**: `BOM-MeetingHub-4-v2.csv` (Designators, Qty,
  Value, Footprint) + `BOM-PCBA-MeetingHub-4-v2.csv` (Item..LCSC..Notes,
  fitted parts only).
- **JLCPCB CPL**: `hardware/Gerbers/MeetingHub-4-v2-CPL.csv`
  (Designator, Mid X, Mid Y, Layer, Rotation; Y negated; no MH/TP) — replaces
  the KiCad-native pos file that JLCPCB rejected.
- Re-routed: 0 unconnected pads, ~880 segments / 36 vias.


## 2026-09-01 — v2 rev-3b (DRC clean)

- **DRC now 0 errors.** The 8 `clearance` errors were all between J1's own
  USB-C pads (0.85 mm pitch) — fixed by setting the netclass clearance to
  0.15 mm, the value v1 actually shipped with (JLCPCB floor is 0.127 mm).
  The 1 `starved_thermal` fixed by switching the GND zones to solid pad
  connection. C20's silk reference (the one `silk_overlap`) hidden.
- 20 `silk_edge_clearance` **warnings** remain — silk of the edge-mounted
  pots/jacks/M3-holes near the rounded outline; cosmetic, KiCad clips silk at
  plot. See `docs/v2-ERC-DRC-status.md`.


## 2026-09-01 — v2 rev-3

- **All 5 volume pots identical and horizontal.** RV1–RV2 changed from the
  vertical Alps RK09L1240A12 to the **horizontal RK09712200HA (C470545)** —
  the same part as the master RV5. All five sit on the front edge, bodies
  overhanging, one BOM line.
- **Zero SMD, verified pad-by-pad.** J2–J6 changed from the hybrid PJ-320D
  (THT body + 4 SMD signal pads) to the **fully through-hole PJ-320E**
  (verify LCSC C2939642); the R1/R2/S/T pad names are identical so no
  schematic rewire. A `pcbnew` scan now reports **0 SMD pads on the whole
  board.** (This also removes the v1 PJ-320D SMD-pad-size DFM problem.)
- Board re-placed and re-routed: **282 × 157 mm**, 0 unconnected pads,
  ~837 track segments / 33 vias. (Q1–Q4 moved to a clean right-edge column so
  every MOSFET-source GND pad routes.)
- Netlist byte-identical to rev-2 (only footprint/part properties changed).

## 2026-08-31 — v2 rev-2 (after first ERC/DRC + layout feedback)

- **ERC now clean.** The 216 `endpoint_off_grid` warnings were from the
  generated SELECT_LOGIC/MICSW sheets sitting off the 1.27 mm grid — the
  generator now snaps every coordinate. The `2N7000 modified in library`
  warnings are gone: the hand-authored 2N7000 lives in the project-local
  `MeetingHub-4-v2` symbol library, not shadowing `Transistor_FET`.
- **DRC `lib_footprint_issues` (118) fixed** — `pcb.py` now stamps each
  footprint with its library nickname (`SetFPID`).
- **Front / rear layout.** Front edge: RV1–RV2, RV5, SW2–SW5, J6 (headset).
  Rear edge: J1 (USB-C power) + J2–J5 (the four notebook jacks); barrels
  overhang their edge for panel mounting. Everything else in the middle.
- **Rounded board outline** (R8 corners), 4× M3 mounting holes just inside the
  corners/edges, GND test point **TP2** added near U1.
- **Board 286 × 157 mm**, 2 layers, fully auto-routed (0 unconnected pads,
  ~840 segments / 29 vias). Only DRC items left: 8 clearance errors between
  J1's own pads (KiCad USB-C footprint pitch — `.kicad_dru` documents it),
  ~39 cosmetic silk-overlap warnings, 2 starved-thermal.
- **Confirmed for the user:** there is **no microphone volume control** — the
  mic path is passive relay switching with no amplifier, so there is nothing
  to remove. The **mute button is already gone** (removed with SW1); mute =
  the power-on state, or hold any two select buttons.
- BOM CSV gained Manufacturer / MPN / LCSC columns; see `docs/v1-vs-v2.md`
  for the full v1↔v2 part comparison.

## 2026-08-31 — v2 initial

New self-contained project in `v2/`, derived from the v1 schematic with the
first-article fixes, then re-worked:

- **2-layer PCB** (was 4). GND pour on both copper layers instead of dedicated
  inner planes. ~328 × 128 mm, fully auto-routed (Freerouting), 0 unconnected
  pads, 842 track segments / 50 vias.
- **100 % through-hole.** `C1/C4/C21` 0603 → THT disc; `D1` SOD-323 TVS →
  `P6KE6.8A` DO-15. No SMD parts remain.
- **Bug 1 (pots) — fixed & verified.** Signal on Alps terminal 3/6, VBIAS on
  1/4, wiper 2/5. Clockwise = louder.
- **Bug 2 (relays) — fixed & re-architected.** Coil pins 2 (+5 V) / 9 (drive),
  COM 5/6 = HEADSET_MIC, NO 10 = NBx_MIC, NC 1 open. D2–D5 reoriented as coil
  fly-back diodes.
- **Bug 3 (VBIAS) — fixed.** Added `U3` (LM358) unity buffer + `R38` 47 Ω
  isolation with post-R feedback; `C26` 1 µF. `VBIAS_REF` label split off the
  divider in MIXER.
- **One-hot mic selector on-board.** New sheet `SELECT_LOGIC.kicad_sch`:
  `U4` CD4043B (local symbol), 20× 1N4148 diode matrix, power-on-reset
  (C24/R37/D26–29), 4× 2N7000 coil drivers with gate resistors. Buttons
  SW2–SW5 are now momentary 6 mm THT. Power-on state = nothing latched = mic
  muted. Press NBx → Kx on, others release.
- **No mute button.** SW1 removed. Mute = power-on state, or hold any two
  select buttons.
- **U1 NE5532 → NJM4580.** NE5532 is out of spec on the 5 V single rail;
  NJM4580 (±2 V min) is not, and is pin-compatible.
- **Mixer feedback R3/R4 10k → 3k3.** Gain −0.33/channel so four laptops
  playing together cannot clip U1 on the 5 V rail.
- Local libraries: `MeetingHub-4-v2.kicad_sym` (CD4043B), `.pretty` with the
  two Alps pot footprints (RK097 Edge.Cuts line moved to Dwgs.User so the
  board outline stays a clean rectangle).
- `.kicad_dru` rule relaxing clearance between two J1 pads (KiCad stock USB-C
  footprint pitch; not a real spacing issue).
- Build scripts kept in `hardware/KiCad/MeetingHub-4-v2/scripts/`.

### Known, non-blocking
- 29 silkscreen-overlap DRC warnings (dense THT ref designators) — tidy in GUI.
- 8 J1 footprint clearance errors (see `.kicad_dru`).
- Board larger than v1 — SELECT_LOGIC block can be compacted.
- High-impedance headphones will be quiet at the 0.66× system gain.
