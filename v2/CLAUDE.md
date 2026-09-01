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
| TRRS jacks | PJ-320D (hybrid) | **PJ-320E all-THT** (C2939642, local fp, silk trimmed) — J2-J5 rot 0 (barrel overhangs rear edge), J6 rot 180 (barrel overhangs front edge) |
| Board | 265×160 square | **192 × 156 mm (near-square), rounded R6**, front = RV1-5/SW2-5/J6, rear = J1+J2-5, **6× M3** (MH5/6 behind the front edge), TP2 |

All 3 v1 first-article bugs fixed + verified (netlist review, session dd4368fd).
Pot direction: CW = louder (signal on Alps term 3, VBIAS on term 1) — **rests on
the RK097 T1=CCW / T3=CW convention, confirm on the first article.**
CD4043B pinout verified vs the TI datasheet. Jack orientation verified correct
(PJ-320E plug enters at the footprint's −Y). Front controls ~3-4 mm from the
front edge, bodies overhanging. **rev-7:** C24 1 µF → 10 µF (longer POR),
MH5/MH6 added; jacks unchanged.

## Files

- `hardware/KiCad/MeetingHub-4-v2/` — KiCad 7 project. 6 sheets (POWER, TRRS,
  MIXER, HPAMP, MICSW, **SELECT_LOGIC**).
  - `MeetingHub-4-v2.kicad_sym` + `sym-lib-table` — local **CD4043B** + **2N7000**.
  - `MeetingHub-4-v2.pretty` — local footprints: 2 Alps pots + PJ-320E (silk
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

Fully routed, 2-layer, **848 seg / 35 vias, 0 unconnected, 0 SMD pads**
(rev-7). **DRC 0 errors** in the GUI (the 8 J1 pad-pitch clearances pass at the
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
