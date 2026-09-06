# MeetingHub-4 **v2** — local context

Self-contained respin of the fabricated `../v1/` board: **2-layer, 100 % THT,
on-board one-hot mic selector, near-square 192 × 156 mm**. Nothing is shared
with `../v1/` — when working v2, stay in `v2/`. **Do not commit.**
(An earlier `v3/` draft — a larger landscape variant of the same schematic —
was removed in the 2026-09-01 restructure.)

## What v2 is (vs v1)

| | v1 | v2 |
|---|---|---|
| Layers | 4 (planes) | **2** (F/B, GND pour both sides) |
| SMD | C1/C4/C21, D1, +4 pads/jack | **0 SMD pads** — verified pad-by-pad |
| Mic selector | latching buttons → relay | **on-board one-hot**: U4 CD4043B + 20-diode matrix + POR + 4× 2N7000 |
| Mute button | SW1 | **none** (power-on = muted; or hold 2 select buttons) |
| Mic volume | none (passive) | **still none** — no mic amp, nothing to remove |
| VBIAS | unbuffered (bug 3) | **buffered** (U3 LM358 + R38) |
| Mixer op-amp | NE5532 (OOS at 5 V) | **NJM4580** |
| Mixer fb R3/R4 | 10k (clips w/ 4 srcs) | **3k3** (0.33×/ch) |
| Volume pots | RV1-4 vert RK09L, RV5 horiz RK097 | **all 5 = Alps RK09712200HA horiz** (C470545) |
| TRRS jacks | PJ-320D (hybrid) | **Korean Hroparts PJ-3200B-4A all-THT** (C136687, local fp `Jack_3.5mm_PJ-3200B-4A_Horizontal`) — J2-J5 rot 0 (barrel overhangs rear edge), J6 rot 180 (barrel overhangs front edge). rev-8: was PJ-320E/C2939642 (bad code, no HTC THT stock). |
| Board | 265×160 square | **192 × 156 mm (near-square), rounded R6**, front = RV1-5/SW2-5/J6, rear = J1+J2-5, **6× M3** (MH5/6 behind the front edge), TP2 |

All 3 v1 first-article bugs fixed + verified (netlist review, session dd4368fd).
Pot direction: CW = louder (signal on Alps term 3, VBIAS on term 1) — **rests on
the RK097 T1=CCW / T3=CW convention, confirm on the first article.**
CD4043B pinout verified vs the TI datasheet. Jack orientation verified correct
(barrel overhangs the board edge, opening faces out). Front controls ~3-4 mm
from the front edge, bodies overhanging. **rev-7:** C24 1 µF → 10 µF (longer
POR), MH5/MH6 added. **rev-8 (2026-09-03):** full JLCPCB stock audit — every
BOM code re-verified, all now in stock with a ready LCEDA footprint+3D model
(D1→C152132, J2-6→HTC PJ-3200B-4A C136687 (new local fp), SW2-5→C&K PTS645
right-angle THT C285519, U1→C5184871, U3→C5213, U4→C22390239, 100nF→C2167231,
3k3→C119335, 100µF→C346930, 47R→C3373549, F1→C76399). Enclosure = top+bottom
acrylic, sides open: front controls repositioned (RV1-5 y=FRONT-5.5, SW2-5
y=FRONT-3). CPL rotation corrected per footprint vs the LCEDA parts. Re-routed
850 seg / 30 vias. New `BOM-JLC-*.csv` (native format). See CHANGELOG rev-8.
**rev-9 (2026-09-03):** de-selected-laptop mic hold-up (sim §P). K1-K4 contacts
re-wired: COM 5/6→`NBn_MIC`, NO 10→`HEADSET_MIC` (commoned), NC 1→**R39-R42 2k2→GND**
(YAGEO CFR-25JB-52-2K2, LCSC C1364486). A laptop switched *away* from now reads
as a live-but-silent mic (1.25 V sleeve) instead of "mic unplugged" → no
internal-mic fallback. Coil/D2-D5 side, audio, one-hot, POR unchanged. BOM 117→121.
Re-routed (Freerouting `--random 0`) **902 seg / 35 vias, 0 unconnected, 0 SMD**,
DRC unchanged (8 J1 + 5 silk). Full sim suite re-run, all reproduces
(`bom_selector.cir` updated for the swap). See CHANGELOG rev-9. Bench-verify OS
behaviour on real laptops (codec firmware).

## Files

- `hardware/KiCad/MeetingHub-4-v2/` — KiCad 7 project. 6 sheets (POWER, TRRS,
  MIXER, HPAMP, MICSW, **SELECT_LOGIC**).
  - `MeetingHub-4-v2.kicad_sym` + `sym-lib-table` — local **CD4043B** + **2N7000**.
  - `MeetingHub-4-v2.pretty` — local footprints: 2 Alps pots + PJ-3200B-4A (silk
    near the overhang trimmed so it doesn't trip `silk_edge_clearance`).
  - `.kicad_dru` — relaxes clearance between two J1 pads.
  - `scripts/` — `gen.py`, `pcb.py`, `ses_import.py`, `post.py`, `bomcpl.py`.
- `hardware/BOM/` — **v1-format**: `BOM-MeetingHub-4-v2.csv` (Designators,
  Quantity, Value, Footprint) + `BOM-PCBA-MeetingHub-4-v2.csv` (Item…LCSC…Notes).
- `hardware/Gerbers/` — 2-layer gerber set + `…-Gerbers.zip`, `…-CPL.csv`
  (**JLCPCB format**: Designator, Mid X, Mid Y (negated), Layer Top/Bottom,
  Rotation; no MH/TP), `…drl`.
- `hardware/PCB/…net`, `hardware/Schematics/…pdf`.

## State

**rev-11 (2026-09-05) — J2–J6 footprint rebuilt after a JLC SMT DFM reject.**
The rev-8 hand-drawn `Jack_3.5mm_PJ-3200B-4A_Horizontal` had the Sleeve pad and
both Ø1.3 locating posts in the wrong places; JLC could not assemble J2–J6 and
the fabricated boards from that order are scrap. The footprint is now rebuilt
from JLC's own LCEDA land pattern for C136687 (`easyeda2kicad`): slotted pads
0.9×1.8, T–R1–R2 at 4.00/3.34, offset Sleeve, 2× Ø1.5 NPTH 7.0 mm apart. Pin
mapping (T/R1/R2/S) and the netlist are unchanged. Board re-placed (jacks at
REAR+8.0 / FRONT−8.0), re-routed, **DRC 0 errors / 0 unconnected** (project
loaded), gerbers+BOM+CPL regenerated. Reply **C** to JLC and re-upload rev-11.
Bench-confirm the jack pinout (plug continuity) and the CPL rotation in JLC's
preview. See CHANGELOG rev-11. Everything below is still current.

**rev-10 (2026-09-04) — FABRICATION AUTHORIZED.** R16/R20 47 Ω → 10 Ω (sim
finding 1: +5.5 dB headphone drive; netlist byte-identical, no re-route,
gerbers/drill/CPL unchanged). Full sim suite re-run both engines: **§A–§G
21/21**, §M 6/6, §E 8/8, §O < 80 µV, §P 1.25 V. Headless DRC with the project
loaded (`SETTINGS_MANAGER.LoadProject`) = **0 errors, 0 unconnected, 5 cosmetic
`silk_over_copper` on RV1–5** (clipped at plot time). Deliverables: validation
report + user manual + usage animation (artifacts). Pre-order bench items:
(1) Alps RK097 terminal convention, (2) 10 Ω R16/R20 LCSC code, (3) de-selected
mic OS behaviour on target laptops.

Fully routed, 2-layer, **902 seg / 35 vias, 0 unconnected, 0 SMD pads** (rev-9)
(rev-8). **DRC 0 errors** in the GUI (the 8 J1 pad-pitch clearances pass at the
netclass **0.15 mm** that v1 also used — set in `.kicad_pro`; headless
`WriteDRCReport` still lists them). Remaining: ~10 cosmetic `silk_over_copper`
warnings. Open in the GUI, run native ERC/DRC, tidy silk, verify the
"verify …" LCSC codes + the RK097 terminal convention before ordering.

## How it's built (KiCad 7.0.11: no CLI ERC, no CLI DSN/SES, no eeschema API)

1. `scripts/gen.py` → regenerates SELECT_LOGIC + MICSW sheets (label-per-pin,
   1.27 mm grid), embeds CD4043B/2N7000. MIXER/POWER/HPAMP hand-edited.
2. `kicad-cli sch export netlist` → parse to verify connectivity (ERC substitute).
3. `scripts/pcb.py` → build 2-layer `.kicad_pcb` (`pcbnew`), rounded Edge.Cuts
   (lines+arcs), 2 GND zones, M3 holes, TP2. **Layout lives in this file** —
   `FRONT`/`REAR` set height; blocks set the rest.
4. `ExportSpecctraDSN` → `freerouting-2.2.4.jar -de x.dsn -do x.ses -mp 100`
   → `scripts/ses_import.py` (apply tracks/vias, refill).
5. `scripts/post.py` → netclass 0.15, solid GND pad connection, shrink refs to
   0.8 mm, hide silk refs that overlap, **restore `.kicad_pro` sheets** (SaveBoard
   wipes them).
6. `scripts/bomcpl.py PRJ NAME` → the 2 BOMs + the JLCPCB CPL.
   DRC/exports need `export KICAD7_FOOTPRINT_DIR=/usr/share/kicad/footprints`.

Regenerate: gen → pcb → route → ses_import → post → bomcpl → gerbers/pdf.
Netlist must stay node-identical (checked each pass).
