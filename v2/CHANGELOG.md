# MeetingHub-4 v2 — changelog

## 2026-09-04 — v2 rev-10 (headphone drive level — sim finding 1 applied) · FABRICATION AUTHORIZED

**Problem (validation finding 1, carried since 2026-09-03):** `R16`/`R20` = 47 Ω
sit **outside** the U2A feedback loop, so with a 16–32 Ω headset they form a
47/(47+32) ≈ 0.4 divider — loaded system gain **0.27×** (−11.5 dB), ~0.22 mW into
32 Ω. Fine for voice/IEMs, quiet for 32 Ω over-ear headsets. This was the single
failing automated check (D4).

**Fix — two resistor values, nothing else:**

| ref | was | now |
|---|---|---|
| R16, R20 (U2A / U2B headphone output series) | 47 Ω (Yageo MFR-25FBF52-47R5, C3373549) | **10 Ω** 1/4 W metal-film THT axial — UNI-ROYAL MFR0W4F100JA50, **LCSC C57437** (±1% ±50 ppm, D2.2×6.5 mm, JLC ~10 800 in stock) |
| R38 (VBIAS buffer isolation) | 47 Ω | **unchanged** — still 47R5 / C3373549 |

- **Same footprint** (`R_Axial_DIN0207_…P10.16mm`), same pads, same position,
  same rotation. **Netlist connectivity byte-identical to rev-9** (95 nets, node
  sets verified equal). **No re-route.** Gerbers, drill and CPL are unchanged;
  only the schematic PDF and the 3 BOM files change.
- **Result (both engines re-run):** MNA §A–§G now **21/21** (was 20/21); loaded
  system gain **0.50×** (−6 dB) MNA / **0.456×** (−6.8 dB) ngspice+BOM-models;
  **0.65–0.79 mW into 32 Ω** (was 0.22 mW) → **+5.5 dB**, D4 passes. §M mute
  6/6, §E one-hot 8/8, §O mic-switch glitch < 80 µV, §P 1.25 V hold-up — all
  still reproduce. Full artifact set regenerated (`plots/*.png`,
  `validation_results.json`, `audio_*.wav`, 3 MP4s).
- **Short-circuit safety:** NJM4556A is a 70 mA line driver with internal
  current limit; 10 Ω still limits a dead-short at the jack and keeps the stage
  unconditionally stable (checked in `.ac`, no peaking).
- Files: `HPAMP.kicad_sch` (R16/R20 = 10), `hardware/PCB/*.net` (regenerated),
  3 BOM CSVs, `bomcpl.py` (10 Ω DB entry), sim scripts + `spice/bom_audio.cir`
  + `spice/bom_mic_switch_glitch*.cir` + `ltspice/03_hpamp.cir` +
  `ltspice/04_fullchain.cir`.

**Pre-order checklist that still stands (not design issues):**
1. **Bench-check the Alps RK09712200HA terminal convention** — knob full-CCW ⇒
   wiper (term 2) ↔ term 1 ≈ 0 Ω. Netlist is wired correctly for that
   convention; a reversed pot is a wire swap, not a respin. This is the exact
   class of the v1 bug — do not skip it.
2. **R16/R20 part (resolved 2026-09-04):** the first pick (Yageo CFR-25JB-52-10R,
   C1364480) had only ~9 pcs of JLC stock. Replaced with **UNI-ROYAL
   MFR0W4F100JA50 / LCSC C57437** — 10 Ω 1/4 W **metal film ±1% ±50 ppm**,
   D2.2×6.5 mm, **~10 800 in JLC stock**. This *restores* the metal-film ±1% tier
   the position originally had (the 47R5 it replaces was Yageo MFR-25FBF52, also
   metal film ±1%) — a step up from the ±5% carbon-film first pick. Same
   DIN0207 P10.16 mm footprint. Drop-in alt if ever needed: Yageo MFR-25JT-52-10R
   (C176452, metal film ±5%, ~12 000 stock).
3. **Bench-verify de-selected-mic OS behaviour** on the target laptops (codec
   firmware — the board side is correct, §P).

**JLCPCB stock snapshot (2026-09-04, full BOM re-checked via the assembly API):**
all 25 lines / 121 parts in assembly stock. Five low-stock lines cap the batch
size and should be pre-reserved / re-checked at order:
`RK09712200HA` C470545 **175** (×5/board → ~35 boards, the limiter) ·
`NJM4556AD` C2838125 **169** · `P6KE6.8A` C152132 **33** (any 600 W uni TVS
V_BR 6–8 V DO-15 substitutes, e.g. 1.5KE6.8A) · `CD4043BE` C22390239 488 ·
`NJM4580DD` C5184871 491. Everything else > 1000.

## 2026-09-03 — v2 rev-9 (de-selected-laptop mic hold-up, SCH-P)

**Problem (validation §P):** switching the mic away from a laptop left that
laptop's mic-jack sleeve **open**, which a Windows audio codec reads as "no
microphone" — it can drop the *Headset Microphone* endpoint and the conferencing
app can fall back to the laptop's **internal mic** (room audio) instead of going
silent.

**Fix — K1–K4 contact re-wire + 4 resistors:**

| relay pin | was | now |
|---|---|---|
| COM (5/6) | `HEADSET_MIC` | **`NBn_MIC`** (laptop *n*'s mic pin) |
| NO (10) | `NBn_MIC` | **`HEADSET_MIC`** (headset electret, commoned K1–K4) |
| NC (1) | *unconnected* | **`R39…R42` (2.2 kΩ) → GND**, one per relay |

Energised Kn still ties laptop *n* to the headset electret (talk). De-energised
Kn now ties laptop *n* to **2.2 kΩ → GND** — the DC of an idle electret
(sim §P: 1.25 V on the sleeve vs 1.19 V for a live mic) — so the codec keeps the
mic endpoint alive and the far end just hears silence. Also removes the same
"mic gone" ambiguity at power-on and during a 2-button mute.

- **New parts:** R39–R42, 2.2 kΩ 1/4 W carbon-film axial THT, YAGEO
  CFR-25JB-52-2K2, **LCSC C1364486** (JLCPCB in stock). BOM: 117 → **121 parts**,
  24 PCBA lines.
- **Coil / free-wheel-diode side (K1–K4 pins 2, 9; D2–D5) unchanged.** Audio
  path, one-hot logic (U4), POR, VBIAS — all untouched.
- **Layout:** R39–R42 placed as a horizontal stack at (168, 102…120) mm, open
  area right of the R21–R37 array. Board stays **192 × 156 mm**.
- **Re-routed** (Freerouting 2.2.4, `--random 0`): 902 seg / 35 vias, **0
  unconnected, 0 SMD pads**. DRC unchanged: the 8 J1 USB-C internal pad-pitch
  clearances (documented, pass in the GUI at netclass 0.15) + 5 cosmetic
  `silk_over_copper`.
- **Simulation re-run — nothing broke:** §A–§G 20/21 (the 1 = finding 1, R16/R20,
  pre-existing), §M 6/6, §E 8/8, §N ngspice all reproduce (`bom_selector.cir`
  updated for the swap: one-hot routing still 37 mV selected / 0.4 µV others),
  §O mic-switch glitch < 80 µV, §P now 1.25 V on a de-selected sleeve.
  **All artifacts regenerated** for rev-9: `plots/*.png`, `validation_results.json`,
  `audio_*.wav`, and the three MP4s (`…-full-simulation`, `…-simulation`,
  `…-mic-selector`). Rebuildable toolchain: `bash /home/fac/.simtools/regen_sim.sh`
  (micromamba env: ngspice 41 + ffmpeg + numpy/scipy/matplotlib — the previous
  session's `/tmp` env was lost to a reboot and rebuilt outside `/tmp`).
- Files: `gen.py` (MICSW), `pcb.py` (R39–R42 placement), `bomcpl.py` (2k2 part),
  `simulation/spice/bom_selector.cir`. Still **bench-verify the OS behaviour on
  the target laptops** — the codec half is firmware.

## 2026-09-03 — v2 rev-8 (JLCPCB stock substitutions)

Audited **every** BOM LCSC code against JLCPCB's assembly library
(`POST jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`,
keyword = code; exact-match only). Every code on the old "verify" list was
either not in the PCBA library or pointed at the wrong part (SMD or a
completely different component). All fixed; **every part in rev-8 is now in
JLCPCB assembly stock, min-order 1**:

| ref | was | now | why the old code was bad |
|---|---|---|---|
| C1,C4,C21,C22,C25 (100 nF) | C49678 | **C2167231** (Vishay K104K15X7RF5TH5, 100 nF 50 V X7R, 5 mm pitch) | C49678 is an **0805 SMD** cap; the interim C5128365 had no LCEDA footprint/model. C2167231 is the same Vishay K-series as the 1 µF (C2167638). |
| C23 (100 µF 16 V) | C2909340 | **C346930** (NXA 100 µF 16 V, D5×11, 2.5 mm pitch — fits the D6.3/P2.5 pad) | C2909340 is a **0402 24 Ω resistor** |
| D1 | C736020 (MDD P6KE6.8A) | **C152132** (BORN P6KE6.8A, DO-15, uni, 5 k stock) | C736020 not in the PCBA library |
| R3,R4 (3k3) | C22978 | **C119335** (CCO MF1/4W-3.3K, 1/4 W metal-film axial +/-1%) | C22978 is an **0603 SMD** resistor; the interim C1369023 (TE LR1F3K3) had no LCEDA model. C119335 is the same CCO family as the 1 k (C120055). |
| J2–J6 | C2939642 "PJ-320E" | **C136687** (Korean Hroparts / HTC **PJ-3200B-4A**, 4-conductor TRRS, THT) | C2939642 is not a real LCSC code; HTC has no PJ-320-series THT jack in JLC stock |
| SW2–SW5 | C318884 | **C285519** (C&K **PTS645VK392LFS**, 6 mm right-angle THT tact) | C318884 is an **SMD-4P tact**; user wants a horizontal side-actuated button |
| U1 | C7466 | **C5184871** (NJM4580DD DIP-8) | C7466 resolves to a **SN74AHC1G04** single inverter (SOT-353) |
| U3 | C7950 | **C5213** (TI LM358P DIP-8) | C7950 is an LM358 in **SOIC-8**, not DIP |
| U4 | C39537 (0 stock, min 14) | **C22390239** (CD4043BE(LX/lingxingic) DIP-16, 490 stock) | genuine drop-in DIP CD4043B, no logic change. The interim C18723483 (XBLW) had no LCEDA footprint/model ("completed after order paid, +1 day"); C22390239 has a full footprint + 3D model. |
| F1 | C1562150 (Bourns MF-RG500, 60 stock) | **C76399** (Littelfuse RXEF050, 500 mA hold, 5.1 mm radial, 6 k stock) | stock too thin; same PTC spec |
| R16,R20,R38 (47R) | C2896824 (VO, insufficient stock for the order) | **C3373549** (Yageo MFR-25FBF52-**47R5** = 47.5 Ω 1 %, 7 k stock) | 1 % off nominal — series/isolation resistors, value not critical; same series as the other axials |

RV1–RV5 (C470545, Alps RK09712200HA) is in stock (185) but the JLCPCB BOM tool
does not auto-assign it (Extended part). **Fix: upload
`hardware/BOM/BOM-JLC-MeetingHub-4-v2.csv`** — new native-format BOM
(`Comment, Designator, Footprint, JLCPCB Part #`) that makes JLC use the LCSC
code for *every* part directly, no fuzzy matching. The PCBA BOM's LCSC column
was also renamed `JLCPCB Part #`.

**CPL / orientation — corrected.** JLC's 3D preview showed several THT parts
rotated wrong. `bomcpl.py` now applies a per-footprint rotation offset in the
CPL: for each footprint the KiCad pads were aligned to JLCPCB's own LCEDA
library footprint (`easyeda.com/api/products/<code>/components`) and the
0deg-to-0deg delta computed, calibrated against the PJ-3200B-4A barrel
direction. `CPL angle = KiCad orientation - offset`.

| footprint | offset | refs | CPL was -> now |
|---|---|---|---|
| DIP-8_W7.62mm | 270 | U1 U2 U3 | 0 -> **90** |
| DIP-16_W7.62mm | 270 | U4 | 90 -> **180** |
| Relay_SPDT_Omron_G5V-1 | 270 | K1-K4 | 0 -> **90** |
| Jack_3.5mm_PJ-3200B-4A_Horizontal | 270 | J2-J5 / J6 | 0 -> **90** / 180 -> **270** |
| Potentiometer_Alps_RK097_Dual_Horizontal | 180 | RV1-5 | 90 -> **270** |
| SW_Tactile_SPST_Angled_PTS645Vx39-2LFS | 180 | SW2-5 | 180 -> **0** |

The RK097 and PTS645 needed a second pass: JLC's 3D preview showed the pot
shafts pointing *into* the board. Their pad grids are too symmetric for the
pad-fit to resolve 0 vs 180, but the LCEDA footprint draws the body/actuator on
the opposite side of the pins from KiCad (KiCad's RK097 body is on the -X side,
matching the Alps datasheet top view; LCEDA's is on +X) -> offset 180, so the
shaft/plunger points off the front edge like the board silk shows.

Everything else matched at offset 0 and is unchanged (elec caps, all diodes,
TO-92, all axial R, ceramics, USB-C J1). Still worth a glance at JLC's upload
preview: electrolytic + diode polarity vs the silk, the DIP/relay pin-1 dot, and
that the J/RV/SW barrel/shaft/plunger points off the right board edge - THT
assembly at JLC is manual + a production review.

**Front-edge controls re-positioned.** Enclosure decided: top + bottom acrylic
only, **sides open, no front panel**. Controls are operated directly, so each
part's can body now sits ~flush with / just behind the open edge and only the
functional bit overhangs:
- RV1-5: y FRONT-3 -> **FRONT-5.5** (pull back 2.5 mm). RK097 9.55 mm can ends
  ~0.5 mm inside the edge; ~20 mm of M7 bushing + shaft overhangs for the knob.
  (Note: that shaft is only held by the 6 THT pins - no locating peg on this
  horizontal variant - so mount the knob near the body.)
- SW2-5: y FRONT-4.5 -> **FRONT-3** (push forward 1.5 mm). PTS645 plunger tip now
  ~1 mm past the edge for a clean finger press / button cap.
Re-routed **850 seg / 30 vias, 0 unconnected, 0 SMD**, DRC unchanged (8 J1 +
5 silk), no courtyard overlaps, no hole crosses the edge. Netlist node-identical.

New local footprint **`Jack_3.5mm_PJ-3200B-4A_Horizontal`** (pads T/R1/R2/S)
built from the HRO PJ-3200B datasheet (rev A): 3.00/4.00 mm pad pitch + offset
pin 1, 2×Ø1.30 locating posts, barrel nose 2.0 mm past the body face. Rotated
so the barrel overhangs −Y like the old PJ-320E fp. **Pin→function
confirmed** two ways: the datasheet schematic (pin 1 = barrel/Sleeve; springs
2/4/3 = Tip/Ring1/Ring2 by insertion depth) and the KiCad PJ320E pad pattern
(4 mm-gap end = T, 3 mm-gap end = R2). → T=pin2, R1=pin4, R2=pin3, S=pin1.

SW2–SW5 → `Button_Switch_THT:SW_Tactile_SPST_Angled_PTS645Vx39-2LFS`.
**Plunger direction confirmed** from the C&K PTS645 datasheet: the "V"
(vertical) termination actuates in the board plane; the KiCad fp's actuator is
at −Y, so **rot 180** points it at the FRONT edge. Placed at FRONT−4.5 → plunger
tip ~0.7 mm inside the edge (enclosure needs a hole/cap per button).

Board re-placed (jacks at REAR/FRONT ± 10.2 → body face ~at the edge, 2 mm
barrel overhang, Ø1.30 posts ~2.5 mm inboard; angled buttons rot 180) and
re-routed: **848 track segments / 39 vias, 0 unconnected pads, 0 SMD pads.**
DRC unchanged (8 J1-internal pad-pitch items that pass in the GUI at the
0.15 mm netclass; 5 cosmetic silk-over-copper). Netlist connectivity
node-identical to rev-7. BOMs + CPL + gerbers + schematic PDF regenerated.

**Still owed — a KiCad GUI / 3D pass before ordering** (mechanical only, the
electrical netlist is unchanged and already reviewed):
1. Open the 3D view, confirm the PJ-3200B-4A barrel overhang (~2 mm) and the
   PTS645 plunger reach vs the real acrylic panel; nudge REAR/FRONT offsets and
   re-route if the enclosure needs it.
2. Tidy silkscreen (5 silk-over-copper), run native ERC + DRC.
3. Update the acrylic enclosure cut plan for the new (larger) jack cut-outs.
4. First article: confirm the Alps RK097 T1=CCW / T3=CW pot convention.

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
