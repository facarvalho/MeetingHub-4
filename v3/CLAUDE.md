# MeetingHub-4 **v3** — local context

Self-contained **mic-selector-only** spin. The v2 one-hot microphone selector,
nothing else: **no mixer, no headphone amp, no volume pots, no VBIAS**. Audio is
handled off-board (external mixer + a TRRS Y-cable per notebook). 4-layer
(Sig / GND plane / +5V plane / Sig), 100 % THT, ~106 × 86 mm. Nothing is shared
with `../v2/` — when working v3, stay in `v3/`.

## What v3 is (vs v2)

| | v2 | v3 |
|---|---|---|
| Scope | monitor 4 + talk on 1 (full analog hub) | **talk on 1 only** — the selector |
| Audio path | 4-in mixer + master + NJM4556A headphone amp + 5 pots + VBIAS buffer | **none** — removed entirely |
| Mic selector logic | CD4043B + 16-diode matrix + POR + 4× 2N7000 + 4× G5V-1 | **identical** (kept verbatim) |
| Relay contacts | COM→HS_MIC, NO→NBn_MIC, NC open | **swapped**: COM→NBn_MIC, NO→HS_MIC (common), NC→**2k2** (`R20–R23`) →GND — a de-selected notebook reads ~1.1 V ("mic present"), not open ("mic gone" → codec falls back to the internal mic) |
| Jacks | 5× 4-pole TRRS (PJ-3200B-4A) | **5× 3-pole P2** (HX PJ-320A-3P DIP, LCSC C17701689; local fp from the EasyEDA pad data). Datasheet pins: **3 = tip → mic, 2 & 4 = ring/sleeve → GND** |
| USB-C CC | left floating (needs a legacy A→C cable) | **5k1 Rd pull-downs** (R1/R2) → works with any USB-C source incl. C-to-C |
| Jacks (mic) | 4-pole TRRS | **3-pole P2**: pin 3 (tip) = mic, **pins 2 & 4 (ring/sleeve) = GND** — CTIA Y-splitters ground the mic-plug ring; grounding both is universal and moots the ring-vs-sleeve pin question |
| POR cap | C24 10 µF | **C5 10 µF** (was 1 µF — sim found a slow ramp releases reset too early) |
| Bulk cap | C23 100 µF | C3 47 µF (one relay coil ≈ 30 mA) |
| Passives | axial horizontal, P10.16 | **axial vertical, P2.54** — main size win |
| Board | 2-layer, 192 × 156 mm | **4-layer (Sig/GND/PWR/Sig), ~106 × 86 mm** |
| BOM | 117 parts | ~73 parts |
| Simulation | `v2/simulation/` | `v3/simulation/` — **real ngspice-42 + datasheet models, 25/25** (`spice_sim.py`), plus a 22/22 MNA cross-check (`validate.py`) |

Refs: `J1` USB-C · `J2–J5` notebook mic · `J6` headset mic · `K1–K4` relays ·
`Q1–Q4` 2N7000 · `U1` CD4043B · `SW1–SW4` buttons · `F1` PTC · `D1` TVS ·
`D2–D5` freewheel · `D6–D21` matrix · `D22–D25` POR · `R1/R2` CC ·
`R3–R10` SET/RST pull-downs · `R11` POR · `R12–R15` gate series · `R16–R19`
gate pull-downs · `R20–R23` 2k2 relay-NC bias · `C1` 100n · `C2` 10µ ·
`C3` 47µ · `C4` 100n · `C5` 10µ POR.

## Files

- `hardware/KiCad/MeetingHub-4-v3/` — KiCad 7 project, **flat single sheet**.
  - `MeetingHub-4-v3.kicad_sym` + `sym-lib-table` — local **CD4043B** + **2N7000**.
  - `MeetingHub-4-v3.pretty/Jack_3.5mm_3pole_THT_Horizontal.kicad_mod` — local
    3-pole P2 THT jack **built from the LCSC/EasyEDA pad data + datasheet for
    C17701689** (HX PJ-320A-3P DIP). Pads numbered **2 / 3 / 4** as the
    datasheet: pin 3 = tip, pins 2 & 4 = ring/sleeve. 7 mm inline pitch, offset
    sleeve, two Ø1.0 NPTH posts 6 mm apart.
  - `MeetingHub-4-v3.kicad_dru` — relaxes clearance between two J1 pads (stock
    GCT USB4085 footprint has 0.8 mm pad pitch; DRC otherwise flags it).
  - `scripts/` — `gen_sch.py`, `gen_pcb.py`, `route.py`, `ses_import.py`, `post.py`,
    `bomcpl.py`, `fab.py`.
- `hardware/BOM/` — v1-format `BOM-…` + `BOM-PCBA-…` + native `BOM-JLC-…`.
- `hardware/Gerbers/` (4-layer), `hardware/PCB/…net`, `hardware/Schematics/…pdf`.
- `simulation/` — **two sims**: (A) real ngspice-42 via `scripts/ngspice_shared.py`
  + datasheet models (`spice/models.lib`), driven by `scripts/spice_sim.py`
  (**25/25**, `spice_results.json`); (B) MNA + logic cross-check `scripts/validate.py`
  (**22/22**, `validation_results.json`). `spice_video.py` renders the 42 s
  component-level mp4 from the ngspice traces. venv: `uv venv simulation/.venv &&
  uv pip install --python simulation/.venv numpy scipy matplotlib imageio-ffmpeg PySpice`.

## How it's built (KiCad 7.0.11: no CLI ERC, no CLI DSN/SES)

1. `scripts/gen_sch.py` → emits the whole flat `MeetingHub-4-v3.kicad_sch`.
   Connections are made by placing a net **label on each pin's connection
   point** (no wires); `check()` asserts no two nets share a coordinate.
2. `kicad-cli sch export netlist` → `/tmp/v3.net`, parsed to verify connectivity
   (the only ERC substitute in the CLI).
3. `scripts/gen_pcb.py` → build the **4-layer** `.kicad_pcb` (`pcbnew`): compact
   placement (with a courtyard-overlap warner), rounded Edge.Cuts, `In1.Cu` =
   solid GND plane, `In2.Cu` = solid +5V plane, F.Cu/B.Cu for signal, 4× M3.
   **No pre-laid tracks** — freerouting 2.2.4 hangs on a DSN that contains any
   pre-routed wiring.
4. `scripts/route.py` → `ExportSpecctraDSN`, **patch the DSN** (`In1.Cu`/`In2.Cu`
   → `(type power)`, or freerouting lays signal traces on the planes and
   `ses_import` drops them), then run `freerouting-2.2.4.jar` retrying
   `-is`/`-us`/`-mp` strategies and keeping the best `.ses` (0 unrouted).
   Grab the jar from `../../v2/hardware/KiCad/MeetingHub-4-v2/` (not committed).
5. `scripts/ses_import.py` → apply tracks/vias, refill zones.
6. `scripts/post.py` → solid zone connect, 0.15 mm netclass, a maze-ish finisher
   for any stub the router left, **silk tidy** (R/D/C/TP/MH refs → F.Fab, the
   ~30 "hunt-for-it" parts keep a shrunk silk ref parked clear of their pads),
   restore `.kicad_pro`, final DRC (0 unconnected, 0 errors, ~1 cosmetic silk).
7. `scripts/bomcpl.py` → the 2 BOMs + JLCPCB BOM + CPL.  `scripts/fab.py` →
   gerbers (**incl. In1.Cu/In2.Cu**) + drill + zip + schematic PDF + netlist + BOMs.

Regenerate: gen_sch → netlist → gen_pcb → route → ses_import → post → bomcpl → fab.
`export KICAD7_FOOTPRINT_DIR=/usr/share/kicad/footprints` first.

Layout gotchas learned:
- freerouting 2.2.4 hangs on a DSN with a LONG pre-laid F.Cu trunk, but is fine
  with SHORT pre-laid stubs. v3 pre-lays nothing.
- **2-layer does not work at this density.** The selector is ¼ of v2's area with
  the same CD4043B (12 I/O) + 16-diode matrix + 5 deep jacks + 4 relays. Every
  2-layer plane arrangement tried (F.Cu +5V / B.Cu GND, GND-only, GND-both-with-
  stitching, B.Cu-as-power) fragmented a pour and trapped a GND or +5V pin
  (U1.5, U1.8 walled by SET/RST tracks, jack Sleeve pads, the pull-down column).
  Best 2-layer result was ~1–2 trapped pins + escape-stub gymnastics.
- **v3 is 4-layer:** `In1.Cu` solid GND, `In2.Cu` solid +5V, F.Cu/B.Cu signal
  only → 0 trapped pins, 0 unrouted, no pre-laid stubs. `post.py` still carries
  the trapped-plane-pad reconnect + short-signal-finish passes as a backup;
  on the 4-layer board they both do nothing.
- freerouting must be told the inner layers are `power`, not `signal` (see
  build step 4) or it routes traces on the planes.
