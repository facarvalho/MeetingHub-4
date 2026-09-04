# MeetingHub-4 v3 — design notes & circuit review

Date: 2026-09-03 · KiCad 7.0.11 · board revision: initial v3

---

## 1. Scope

Requested: a **new project in `v3/`** that is **only the microphone selector**,
on the **smallest practical board**. Audio/monitoring is done off-board — the
user splits each notebook's 3.5 mm combo jack with a TRRS Y-cable (headphones →
external mixer, mic → this board) and does the same on the headset.

So everything in v2 that is *not* the mic selector is deleted:

| removed from v2 | why it is gone |
|---|---|
| `U1` NJM4580 4-input mixer, `R1–R12` input/feedback, `C3–C16` | no monitor path |
| `U2` NJM4556A headphone amp, `R13–R20`, `C17–C21` | no headphones on the board |
| `U3` LM358 VBIAS buffer, `R38`, `C25/C26`, the 10k/10k divider | mic path is passive; nothing needs a 2.5 V rail |
| `RV1–RV5` volume pots | no levels to set (mixer does that) |
| the TRRS tip/ring1 (L/R audio) wiring on every jack | only tip (mic) + ring & sleeve (gnd) are used |

## 2. What was kept **verbatim** from v2

The one-hot selector is unchanged — it is the part v2's SPICE run validated
(`../v2/simulation/`, session 2026-09-03, "all 3 v1 bugs confirmed fixed",
20/21 checks OK). Net-for-net identical:

- **`U1` CD4043B** quad NOR R/S latch, ENABLE tied high, pinout per the TI
  datasheet (1Q–4Q = 2,9,10,1; 1R–4R = 3,7,11,15; 1S–4S = 4,6,12,14; OE = 5).
- **16-diode steering matrix** `D6–D21` (1N4148): button *b* drives `SETb` **and**
  the `RST` line of the other three latches. Pull-downs `R3–R6` (SET1–4),
  `R7–R10` (RST1–4), 100 k.
- **Power-on reset** `C5` (10 µF) + `R11` (100 k) → `PORN` tracks `VBUS` on the
  way up and then decays (~0.1 s to the RST threshold, τ ≈ 1 s tail);
  `D22–D25` pull every `RST` high during that window → all Q = 0 →
  **no relay at power-on → mic muted**, deterministic for any ramp (see the
  simulation §P).
- **Coil drivers** `QO1–4` –`R12–15` (1k)– gate –`R16–19` (100k)– GND →
  `Q1–Q4` 2N7000; drain → `COILn` (relay pin 9); `D2–D5` clamp the fly-back to
  +5 V (cathode → +5 V).
- **Relays** `K1–K4` Omron **G5V-1**: coil pins 2 (+5 V) & 9 (drain). Contact
  side rewired vs v2 (see §3): **COM 5/6 → `NBn_MIC`**, **NO 10 → `HS_MIC`**
  (common to all four), **NC 1 → `R20–R23` 2.2 kΩ → GND**.

## 3. What changed on purpose (improvements over v2)

| change | why |
|---|---|
| **5.1 k CC pull-downs** `R1/R2` on `J1` CC1/CC2 | v2 left CC floating, so a C-to-C cable to a charger never enables VBUS. With Rd present, any USB-C source (charger, power bank, PC port) delivers 5 V. |
| **3-pole P2 (3.5 mm) jacks**: Tip = mic, **Ring + Sleeve = GND** | v2's 4-pole TRRS jack is wrong for receiving a Y-splitter's *mic* plug. A CTIA TRRS→2×3.5 splitter puts the mic on the **tip** and ties the mic-plug **ring and sleeve to ground** — so grounding both the jack Ring and Sleeve is the universal choice (mono, CTIA, and PC-"pink" mic-on-tip plugs all work, nothing shorts); tying Ring to the mic net instead would short the mic on a large fraction of splitters. *This started as "Tip + Ring both to mic", was briefly "Ring = NC", and settled on "Ring + Sleeve = GND" during the simulation review.* |
| TVS `D1` on **VBUS (pre-fuse)** | a surge is shunted straight to GND by D1, not forced through F1 (same intent as v2's note, wired explicitly here). |
| POR cap `C5` **10 µF** (electrolytic) | started at 1 µF; the sim (§P3) showed that a slow (>~30 ms) USB-C soft-start VBUS ramp releases the reset *before the rail is up*, so the CD4043B could latch a relay at power-on. 10 µF holds `PORN` ≈ `VBUS` through any realistic ramp → deterministically muted. Same value/reason as v2's C24. |
| bulk cap `C3` 100 µF → **47 µF** | only one relay coil is ever energised (~30 mA); 47 µF + 10 µF + 100 nF is ample and fits a D5 radial. |
| **vertical** axial R/D footprints (`…P2.54mm_Vertical`) | the single biggest board-area saving — 17 resistors + 20 diodes go from ~10 mm to ~3 mm each. |
| flat single-sheet schematic | 60 parts doesn't need hierarchy. |
| **relay COM ↔ NO swapped + `R20–R23` 2.2 kΩ on each NC pin → GND** | v2 (and early v3) left a de-selected notebook's mic pin **open** — its codec reads the full bias rail (~2.5 V) = *"no microphone"*, so codecs that re-sense the jack drop the headset mic and fall back to the notebook's **internal** mic (room audio on the call), with a disconnect toast + a pop on return. With COM on the notebook and NC pulled to GND through 2.2 kΩ, a de-selected notebook reads **~1.1 V** — the same as the selected path's live electret — so every codec keeps *"headset mic present, silent"*. Confirmed by the v2 `bom_mic_deselect_detect.cir` `.op` and v3 sim check **MIC7**. Costs 4 resistors; audio, one-hot logic and POR are untouched. |

## 4. Circuit walk-through (as built)

### Power
`J1` VBUS → `F1` (500 mA PTC) → `+5V`. `D1` (P6KE6.8A TVS, V_BR 6.45–7.14 V)
clamps VBUS→GND at the entry. `C1` (100 nF) + `C2` (10 µF) + `C3` (47 µF)
decouple the 5 V rail; `C4` (100 nF) sits on `U1` VDD. `R1`/`R2` (5.1 k) pull
CC1/CC2 to GND so a Type-C source presents 5 V on VBUS.

### Select logic — see §2. Truth table (unchanged from v2 / SCH-010):
- power-on → POR → Q1–Q4 = 0 → **muted** ✔
- press NB2 → SET2 = 1, RST1 = RST3 = RST4 = 1 → **only K2** ✔
- then press NB4 → K2 drops, K4 latches ✔
- NB2 + NB3 held together → SET2 = RST2 = 1 and SET3 = RST3 = 1 → Q2 = Q3 = 0,
  RST1/RST4 high → **all off (muted)** while held ✔

### Mic path
`J6` tip (`HS_MIC`) → the **NO** pin of all four relays, commoned. Each relay's
**COM** → `NBn_MIC` → `Jn` tip → notebook *n*'s mic pin (via the Y-splitter).
Each relay's **NC** → `R20–R23` 2.2 kΩ → GND. Every jack Ring **and** Sleeve →
board GND → `J1` GND.

- **`Kn` energised:** `NBn_MIC` ↔ `HS_MIC` → notebook *n* biases and reads the
  headset electret (passive switching, exactly as v1/v2). Sim: 1.10 V at the
  electret, contact loss < 0.001 dB.
- **`Kn` de-energised:** `NBn_MIC` ↔ 2.2 kΩ ↔ GND → notebook *n* reads ~1.1 V on
  its mic pin (looks like an idle electret) and hears nothing. It does **not**
  see an open circuit, so it never reports the headset mic gone. Crosstalk from
  `HS_MIC` is only the ~10 pF across the open NO contact (< −60 dB in-band).

## 5. Verification performed

- **Netlist** (`kicad-cli sch export netlist`) parsed pin-by-pin: 75 components,
  no single-node nets other than the intended NCs (J1 D±/SBU, U1 pin 13),
  every power pin driven, matrix / latch / driver / relay / jack nets match
  intent. `gen_sch.py check()` asserts no two nets share a pin coordinate
  (188 distinct pin nodes, no collisions).
- **Routing:** Freerouting 2.2.4 headless, **4 layers** (F/B signal, In1 = GND
  plane, In2 = +5 V plane; the DSN marks the inner layers `power` so the router
  keeps signals on F/B). **0 unrouted.** The dense selector would not route
  clean on 2 layers - every 2-layer plane split fragmented a pour.
- **DRC** (`pcbnew.WriteDRCReport`): **0 unconnected pads**. The only errors are
  **10 clearance items, all between two pads of `J1`** — the stock GCT USB4085
  footprint has 0.8 mm pad pitch; `.kicad_dru` documents it (passes in the GUI
  at the 0.15 mm netclass, exactly as on v2). 0 SMD pads. Silk-overlap /
  silk-over-copper warnings on the dense passive clusters are cosmetic — tidy in
  the GUI before fab.

## 6. Open items / limitations (not blocking)

1. **No runtime "none selected".** Once a notebook is chosen the mic stays on it
   until power-cycle or a deliberate 2-button press. Accepted (no mute button).
2. **Jack = HX PJ-320A-3P DIP, LCSC C17701689** — P2 (3.5 mm) 3-conductor,
   right-angle **through-hole**. The local footprint
   `Jack_3.5mm_3pole_THT_Horizontal` is built from the **EasyEDA/LCSC pad vector
   data for C17701689** (part uuid `c718c744…`) and the HX datasheet: three
   1.2 × 0.6 mm oval THT pads numbered **2 / 3 / 4** (inline pair 7 mm apart +
   offset sleeve) and two Ø1.0 mm NPTH locating posts 6.0 mm apart. The
   datasheet schematic draws **terminal 3 as the tip leaf-spring** → pin 3 is
   wired to the mic net; **pins 2 and 4 both go to GND**, which is correct
   whichever of them is ring vs sleeve and safe for any CTIA Y-splitter.
   Bring-up: insert a 3.5 mm plug and meter continuity from its tip to pin 3; if
   the tip lands on pin 4 instead, move the mic net to pin 4 (one-line change).
   *(The earlier BOM code `C145843` was a bad placeholder — a slide switch.)*
3. **`5k1`, `2k2` and `47µF` LCSC codes** are best-guess — verify in your cart.
4. **2N7000 / CD4043B symbols are project-local** — sanity-check the TO-92
   pinout (S-G-D = 1-2-3) and the DIP-16 pin 1 on bring-up.
5. **Silkscreen** reference designators overlap on the matrix / pull-down
   clusters (cosmetic DRC warnings) — reposition or shrink in the KiCad GUI.
6. Board is ~106 × 86 mm (4-layer); the diode-matrix block can still be tightened
   by hand if a smaller board matters more than assembly comfort. Going back to
   2 layers is **not** an option at this density (see §5).
7. **All jack sleeves are commoned to board GND** (same topology as v1/v2). Power
   the board from an isolated USB charger / power bank, **not** from one of the
   four notebooks, to avoid a ground loop between the notebooks' audio grounds.
8. The KiCad schematic is generated in a **net-label-per-pin** style (labels sit
   directly on the pins, no drawn wires) — electrically complete and it
   netlists correctly, but open it in KiCad if you want a wired drawing.

## 7. Bring-up checklist

1. Power via USB-C. Measure `TP1` = 5.0 V. No relay should click. Nothing hot.
2. Press NB1 → `K1` clicks; `NB1_MIC ↔ HS_MIC` continuity; NB2/3/4 open.
   Press NB2 → `K1` releases, `K2` clicks. Press NB1 + NB2 → all release.
3. One notebook on `J2` (through its Y-splitter mic leg), headset mic on `J6`.
   Join a call, select NB1 → the notebook hears the headset mic. Its headphone
   leg + your headphones go to the external mixer as usual.
4. Four notebooks on `J2–J5`: mic follows the last button pressed, one at a time.
