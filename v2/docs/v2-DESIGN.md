# MeetingHub-4 v2 — design notes & circuit review

Date: 2026-08-31 · KiCad 7.0.11 · board revision: initial v2

---

## 1. Scope of this respin

Requested: a **new project in `v2/`**, same function as v1, but

1. **2-layer** PCB (v1 was 4-layer with GND/5 V planes),
2. **100 % through-hole** — no SMD anywhere,
3. **fix the 3 bugs** found on the first fabricated batch (JLCPCB lot
   `W2026080810364558`),
4. the **one-hot exclusive mic selector** (`../../v1/docs/Architecture/SCH-010-OneHotMicSelector.md`)
   built onto the main board,
5. **no mute button**.

## 2. The three v1 bugs — status in v2

| # | v1 bug | v2 |
|---|---|---|
| 1 | Volume pots wired backwards (signal & VBIAS on swapped terminals) → reversed direction, wouldn't fully mute | **Fixed.** Signal on terminal 3/6, VBIAS on terminal 1/4, wiper 2/5 → output. Alps datasheet: terminal 1 = full-CCW end, terminal 3 = full-CW end. So **CW = wiper toward signal = louder**, full-CCW = wiper at VBIAS = silent. Matches "aumentar à direita". |
| 2 | Mic relays K1–K4: coil and contacts swapped → coils never energised, mic dead | **Fixed + re-architected for one-hot.** Coil = pins 2 (+5 V) & 9 (MOSFET drain); COM = 5/6 → `HEADSET_MIC`; NO = 10 → `NBx_MIC`; NC = 1 open. D2–D5 are the coil free-wheel diodes, cathode → +5 V. |
| 3 | VBIAS unbuffered (10k/10k + 10 µF) → bleed at min volume | **Fixed.** `R1/R2` (10k/10k) + `C3` (10 µF) make `VBIAS_REF` (2.5 V); `U3A` (LM358) buffers it, `R38` (47 Ω) isolates the `C26` (1 µF) load with feedback taken *after* R38 so DC is exact and the LM358 stays stable. `VBIAS` now has < 1 Ω source impedance. |

## 3. What else changed (review findings, see §6)

| Change | Why |
|---|---|
| `U1` NE5532 → **NJM4580** | NE5532's recommended supply is ±3 V (6 V); on the 5 V single rail it is out of spec. NJM4580 is ±2 V min, pin-compatible DIP-8, audio-grade. |
| Mixer feedback `R3/R4` 10k → **3k3** | Unity gain per channel meant 4 laptops playing together could sum past the ±2.2 V output headroom at 5 V. 3k3 gives 0.33×/channel; 4 correlated full-scale inputs ≈ 0.6 V pk, comfortably inside the rail. |
| `C1/C4/C21` 0603 → **THT disc**, `D1` SOD-323 → **P6KE6.8A DO-15** | all-THT requirement. P6KE6.8A: 600 W unidirectional TVS, V_BR 6.45–7.14 V — the literature-recommended architecture for a **power-only** USB-C VBUS (no data lines here) is a single discrete TVS to GND with V_BR 6–8 V, behind the PTC fuse. |
| SW1 (mute) removed; SW2–SW5 → **momentary** 6 mm THT | no mute button; one-hot latch needs momentary inputs. |
| New sheet **SELECT_LOGIC** | U4 CD4043B + 20× 1N4148 matrix + POR (C24/R37/D26–29) + 4× 2N7000 drivers + pulldowns. |

## 4. Circuit walk-through (as built)

### Power
`J1` VBUS → `F1` (500 mA PTC) → `+5V_AUDIO`. `D1` (TVS) clamps VBUS→GND at the
entry (a surge is shunted by D1, not forced through F1). Bulk/decoupling:
C1, C2 (10 µF), C21, C22, C25 (100 nF), C23 (100 µF near the logic).

### VBIAS
`+5V` –R1(10k)– `VBIAS_REF` –R2(10k)– GND, filtered by C3 (10 µF). `U3A`
non-inverting unity buffer → `VB_OUT` –R38(47 Ω)– `VBIAS` (+ C26 1 µF), −in fed
back from `VBIAS`. U3 powered from +5 V / GND (C25 decouple). U3B unused,
wired as a grounded follower (no floating input).

### Monitor path (repeats for all 4 laptops, both channels)
`Jn.T/R1` → `Cx` (1 µF DC-block) → `RVn.3/6` (signal), `RVn.1/4` = VBIAS,
`RVn.2/5` wiper → `Rin` (10k: R5/R7/R9/R11 left, R6/R8/R10/R12 right) →
`U1.2` / `U1.6` (virtual ground at VBIAS).
`U1A/B` = inverting summers, Rf = R3/R4 = 3k3 → gain −0.33 per channel,
all four summed. Out (U1.1 / U1.7) → C13/C14 (1 µF) → `RV5.3/6` (master),
`RV5.1/4` = VBIAS, wiper → `MIX_L` / `MIX_R`.
`MIX_x` → C15/C18 (1 µF) → `U2.3` / `U2.5` (+in), biased to VBIAS via R13/R17.
`U2A/B` (NJM4556A) non-inverting, gain = 1 + R15/R14 = **2** at audio, 1 at DC
(C16/C19 block the feedback divider at DC). Out → C17/C20 (1 µF) → R16/R20
(47 Ω series, stability + short protection) → `J6.T` / `J6.R1` (headset L/R).
`J6.R2` = GND.

Overall monitor gain ≈ 0.33 × 1 (master max) × 2 ≈ **0.66×**. A −10 dBV line
source (0.32 V rms) → ~0.21 V rms into the headset → ~1.4 mW into 32 Ω
(≈ 100 dB SPL in phone-style earbuds). Loud enough for 16–32 Ω CTIA headsets;
**high-impedance (>150 Ω) headphones will be noticeably quieter** — if that
matters, raise R3/R4 to 4k7.

### Mic path
`J6.S` (`HEADSET_MIC`) → K1–K4 COM (pins 5/6). `Kn` NO (pin 10) → `NBn_MIC` →
`Jn.S` → laptop n mic input. `Kn` NC (pin 1) is open, so a de-energised relay
leaves the mic **disconnected** from that laptop. The electret in the headset
is biased by whichever laptop is selected (passive switching, as v1).

### One-hot select logic (SELECT_LOGIC sheet)
- 4 momentary buttons: `SW2→BTN1 … SW5→BTN4`, other side +5 V.
- Diode matrix (D10–D25): button *X* drives `SETx` **and** the `RST` line of the
  other three latches. Pulldowns R21–R24 (`SET1–4`), R25–R28 (`RST1–4`), 100 k.
- `U4` CD4043B (quad NOR R/S latch, ENABLE=+5 V so outputs are always active):
  latch A S1=4/R1=3/Q1=2 · B S2=6/R2=7/Q2=9 · C S3=12/R3=11/Q3=10 ·
  D S4=14/R4=15/Q4=1 (matches the datasheet / SCH-010).
- Power-on reset: C24 (1 µF) couples the +5 V step to `PORN`; R37 (100 k)
  discharges it (~100 ms); D26–D29 pull all `RST` high during that window →
  all Q = 0 → **no relay at power-on = muted**.
- Coil drivers: `QOn` –R29–32 (1k)– `GATEn` (–R33–36 100 k– GND) → 2N7000 gate.
  `Qn` on → `COILn` (relay pin 9) to GND → relay n energises. D2–D5 clamp the
  coil's fly-back to +5 V.

## 5. Verification performed

- **Netlist** (`kicad-cli sch export netlist`, the only ERC substitute in
  KiCad 7 CLI) parsed and checked pin-by-pin: 118 components, no single-node
  nets, all power pins driven, matrix / latch / driver / relay / audio nets
  match intent.
- **Routing:** Freerouting 2.2.4 headless, 2 layers → **0 unconnected pads**
  (842 track segments, 50 vias). GND pour on F.Cu and B.Cu, refilled.
- **DRC** (`pcbnew.WriteDRCReport`): the only errors are 8 clearance/mask
  items **between two pads of J1** — the KiCad stock USB-C footprint
  (`USB_C_Receptacle_GCT_USB4085`) has 0.8 mm pad pitch; the connector is
  built that way. A `.kicad_dru` rule documents this. 29 silkscreen-overlap
  warnings (reference designators on tightly-packed THT parts) and 1
  starved-thermal warning are cosmetic — tidy in the GUI before ordering.
  (~124 `lib_footprint_issues` from headless DRC are a known KiCad path
  artifact — ignore, as noted for v1.)

## 6. Three-pass circuit review (4 laptops + headset connected)

### Pass 1 — DC / bias
- Every IC supply pin verified: U1/U2/U3 pin 8 = +5 V, pin 4 = GND; U4 pin 16
  = +5 V, pin 8 = GND, pin 5 (ENABLE) = +5 V. ✔
- VBIAS = 2.5 V, buffered, feeds all 10 pot cold-ends + R13/R17 + C26. ✔
- 2N7000 gates pulled to GND when idle; sources to GND; drains to coils. ✔
- Op-amp supply check: NJM4580 ±2 V min, NJM4556A ±2 V min, LM358 3–32 V —
  **all valid on the 5 V rail** (NE5532 was not → replaced). ✔
- Current budget: 3 op-amp packages (~10 mA) + 1 relay coil (~30 mA) + CD4043B
  (~0.1 mA) + matrix leakage ≈ **< 60 mA**. F1 (500 mA hold) and USB-C (min
  500 mA / 3 A typ) have wide margin. Only one relay is ever on. ✔

### Pass 2 — monitor audio, all four laptops playing
- Signal path L and R traced end-to-end for NB1…NB4 (§4). All four wipers sum
  into U1A (L) / U1B (R). Independent volume RV1–RV2, master RV5. ✔
- **Clipping check:** mixer gain −0.33/ch. Worst case 4 correlated −10 dBV
  sources at full pot = 4 × 0.45 V pk × 0.33 = 0.6 V pk; NJM4580 on 5 V swings
  ~±2.2 V about VBIAS. **No clipping.** With the old 10k feedback it would
  clip at ~2 sources — that is why R3/R4 changed. ✔
- Headphone amp gain 2×, DC-servo'd to VBIAS, 47 Ω series output, C17/C20 keep
  DC off the headphones. NJM4556A delivers 70 mA — fine for 16–32 Ω. ✔
- Pot direction: full-CW → wiper at terminal 3 (signal) → **loud**; full-CCW →
  wiper at terminal 1 (VBIAS) → **silent/mute**. Correct and matches request. ✔

### Pass 3 — mic routing & one-hot logic
- Truth table walked for each button and for the 2-button case:
  - power-on → POR → Q1–Q4 = 0 → no relay → **mic muted**. ✔
  - press NB2 → SET2=1, RST1=RST3=RST4=1 → Q2=1, Q1=Q3=Q4=0 → **only K2**. ✔
  - then press NB4 → K2 drops, K4 latches. ✔
  - press NB2 + NB3 together → SET2=RST2=1 and SET3=RST3=1 → Q2=Q3=0, and RST1
    /RST4 high → **all off (muted)** while held; on release it resolves to one
    selected again (documented in SCH-010). ✔
- Relay contact mapping: COM(5/6)=HEADSET_MIC, NO(10)=NBx_MIC, NC(1)=open →
  de-energised = mic disconnected from that laptop. ✔
- Free-wheel diodes D2–D5: anode = coil/drain, cathode = +5 V → correct
  fly-back clamp (v1 had these backwards). ✔
- Contact bounce on the buttons: the RS latch re-asserts the same state, immune.
  ✔

### rev-2 layout (2026-08-31)
- **Front / rear split** per request: front board edge carries RV1–RV2, RV5
  (body overhangs the edge), SW2–SW5 and J6 (headset, barrel overhangs);
  rear edge carries J1 (USB-C, 180°) and J2–J5 (barrels overhang for panel
  mounting). Everything else is in the middle.
- **Rounded outline** (8 mm corner radius), **286 × 157 mm**, 2 layers.
- **4× M3 mounting holes** just inside the corners/edges; **TP2** GND test
  point added near U1.
- ERC-grid and footprint-library issues from the first review round are fixed
  — see `v2-ERC-DRC-status.md`.

### Confirmations for the review notes
- **Mic volume:** there is **no** microphone volume control anywhere in the
  design. The mic path is a passive relay switch (J6 sleeve → relay COM →
  selected laptop's mic pin) with **no amplifier**, so there is nothing to
  remove. RV1–RV2 and RV5 act **only** on the monitor/headphone path.
- **Mute button:** already removed (was SW1). "Mute" = the power-on state
  (nothing latched), or hold any two select buttons.

### rev-7 (2026-09-01) — circuit review follow-ups
- **Jack orientation: no change — the original is correct.** A mid-review
  claim that J2–J6 faced inward was wrong: on the PJ-320E the plug enters at
  the footprint's **-Y** end (the barrel nub), so J2–J5 at rot 0 have the
  barrel overhanging the rear edge and J6 at rot 180 has it overhanging the
  front edge, openings facing out. Left as-is.
- **C24 1 µF → 10 µF** (electrolytic, C43799): POR pulse ~4 ms → ~40 ms, so a
  slow VBUS ramp still guarantees mic-muted at power-on. Netlist unchanged.
- **MH5/MH6 added** ~12 mm behind the front edge to stiffen the pot-knob edge.
- **CD4043B pinout confirmed** against the TI datasheet (1Q–4Q = 2,9,10,1;
  1R–4R = 3,7,11,15; 1S–4S = 4,6,12,14; OE = 5; NC = 13) — the project-local
  symbol is correct.
- Re-routed: 848 seg / 35 vias, 0 unconnected, 0 SMD pads.

### Open items / limitations (not blocking)
1. **No runtime "none selected".** Once a laptop is chosen the mic stays on it
   until power-cycle or a deliberate 2-button press. Accepted trade-off for
   having no mute button. SCH-010 §3.5 adds a 5th "mute/reset" button if wanted.
2. **High-Z headphones** are quiet at 0.66× system gain — raise R3/R4 to 4k7.
3. **Board 192 × 156 mm** — the SELECT_LOGIC block can still be tightened.
4. **Silkscreen** ref designators overlap on dense clusters (cosmetic DRC
   warnings) — reposition/scale in the KiCad GUI before fab.
5. **Pot direction rests on the RK097 T1 = full-CCW / T3 = full-CW convention.**
   Confirm on the first article (full-CCW → wiper↔T1 ≈ 0 Ω).
6. **J1 footprint** trips 8 clearance DRC — `.kicad_dru` documents it; passes
   in the GUI at the 0.15 mm netclass.
7. **2N7000 symbol** is project-local — sanity-check the TO-92 pinout (S-G-D =
   1-2-3) on first bring-up.

## 7. Bring-up checklist (bench, then 1 laptop, then 4)

1. Power via USB-C. Measure `TP1` = 5.0 V, `VBIAS` = 2.50 V, `VBIAS_REF` ≈
   2.50 V. No relay should click. No IC hot.
2. Press NB1: K1 clicks. `NB1_MIC`↔`HEADSET_MIC` continuity; NB2/3/4 open.
   Press NB2: K1 releases, K2 clicks. Press NB2+NB3: all release.
3. One laptop on J2, headset on J6. Play audio → adjust RV1 and RV5, CW = louder.
   Join a call → NB1 selected → the laptop hears the headset mic.
4. Four laptops on J2–J5. Confirm all four are audible together, each RV1–RV2
   independent, RV5 master. Mic follows the last button pressed, one at a time.
