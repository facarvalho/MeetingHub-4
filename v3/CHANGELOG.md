# MeetingHub-4 v3 — changelog

## 2026-09-03 — v3 initial (mic selector only)

New project, spun from `../v2/`. **Only the one-hot microphone selector** — the
audio/monitor half of v2 is deleted (mixer `U1`, headphone amp `U2`, VBIAS
buffer `U3`, pots `RV1–5`, all their passives, and the L/R jack wiring). The
user monitors on an external mixer and feeds this board a mic-only plug per
notebook via a TRRS Y-cable.

**Kept net-for-net from v2** (the part its SPICE run validated): `CD4043B` `U1`
quad NOR R/S latch, the 16-diode steering matrix `D6–D21`, SET/RST pull-downs
`R3–R10`, power-on-reset `C5`/`R11` + `D22–D25` (power-on = muted), MOSFET coil
drivers `Q1–Q4` (2N7000) + `R12–R19`, fly-back diodes `D2–D5`, and the four
Omron `G5V-1` relays `K1–K4` (COM → `HS_MIC`, NO → `NBn_MIC`).

**Changed on purpose:**

| # | change | reason |
|---|---|---|
| 1 | added `R1`/`R2` = 5.1 k, CC1/CC2 → GND | v2 left the USB-C CC pins floating; a C-to-C cable to a charger then never turns VBUS on. With Rd present any USB-C source delivers 5 V. |
| 2 | jacks `J2–J6` → **3-pole 3.5 mm TRS** (new local footprint `Jack_3.5mm_3pole_THT_Horizontal`); tip **and** ring both tied to the mic net | v2's 4-pole TRRS jack cannot correctly receive a Y-splitter's mic plug (its long sleeve bridges the R2 and S springs). A 3-pole jack with T+R paralleled accepts "mic on tip" and "mic on tip+ring" wiring alike. |
| 3 | `D1` TVS explicitly on **VBUS (pre-fuse)** | surge shunted by D1, not forced through F1. |
| 4 | `C3` 100 µF → **47 µF** (D5 radial) | one relay coil ≈ 30 mA; 47 µF + 10 µF + 100 nF is ample. |
| 5 | all axial R / D → **vertical** footprints (`…_P2.54mm_Vertical`) | biggest single board-area saving. |
| 6 | **flat single-sheet** schematic; refs renumbered `U1`, `SW1–4`, `D1–D25`, `R1–R19`, `C1–C5` | 60 parts don't need hierarchy. |

**Board:** initially 2-layer, ~104 × 86 mm (≈ ⅓ of v2's 192 × 156), R3 corners,
4× M3, 100 % through-hole, ~69 parts. *(Later changed to 4-layer / 106 × 86 mm —
see the "4-layer" and "jack part finalised" entries below.)*

## 2026-09-03 — simulation + two fixes

Added `simulation/` (see `docs/v3-simulation-validation.md`): MNA + logic model
for the selector, POR, power and the passive mic path, plus ngspice/LTspice
`.cir` decks. Two changes came out of it:

| # | change | reason |
|---|---|---|
| 7 | jacks `J2–J6` → **Tip = mic, Ring + Sleeve = GND** (was Tip+Ring both to mic) | a CTIA TRRS→2×3.5 Y-splitter puts the mic on the tip and ties the mic-plug ring/sleeve to ground — tying the jack Ring to the mic net shorts the mic on ~half the splitters sold. Grounding Ring + Sleeve is universal. |
| 8 | POR cap `C5` 1 µF → **10 µF** (electrolytic) | with 1 µF a slow (>~30 ms) USB-C soft-start ramp releases the reset before the rail settles → the CD4043B could latch a relay at power-on. 10 µF holds PORN ≈ VBUS through any ramp → deterministically muted (same value/reason as v2's C24). |

## 2026-09-03 — 4-layer

The selector is 4× denser than in v2 (same CD4043B + 16-diode matrix + relays in
¼ the area) and would not route clean on 2 layers — every 2-layer plane split
(F.Cu +5V / B.Cu GND, GND-only, GND-both) fragmented a pour and trapped a
GND/+5V pin or two. **v3 is now 4-layer:** `F.Cu` + `B.Cu` signal, `In1.Cu` =
solid GND plane, `In2.Cu` = solid +5V plane. Routes clean, no fragmentation, no
escape stubs. Order as **4-layer, 1.6 mm** (JLCPCB 4-layer at ~106 × 86 mm is a
few dollars over 2-layer — negligible next to shipping at hobby quantities, and
it buys a quiet, properly-grounded board).

## 2026-09-03 — jack part finalised

`J2–J6` = **SHOU HAN PJ-320A-3P DIP, LCSC C17701689** — P2 (3.5 mm) 3-conductor
right-angle **through-hole** jack. The local footprint
`Jack_3.5mm_3pole_THT_Horizontal` was rebuilt to the standard PJ-320 THT pin
pattern (T/R 4 mm apart, S offset, barrel overhangs -Y), 1.8 mm round pads.
Board grew to **106 × 86 mm** to fit the wider jack bodies. **Still verify the
T/R/S pin map with a multimeter on the real part before assembly.**

*(The earlier BOM code `C145843` was a wrong placeholder — it is a Korean
Hroparts slide switch, not a jack. Caught by the user.)*

User note: "componentes J2–J6 devem ser P2" — confirmed, all 5 are P2 (3.5 mm);
the only non-P2 connector is J1 (USB-C, power only).

**Toolchain:** `gen_sch.py` (label-on-pin, collision-asserted) → `kicad-cli`
netlist → `gen_pcb.py` (`pcbnew`, courtyard-overlap warner) → `route.py`
(ExportSpecctraDSN + patch inner layers to `power` + Freerouting 2.2.4, retrying
strategies until 0 unrouted) → `ses_import.py` → `post.py` (zone stitch + finish
any short net + DRC) → `bomcpl.py`.

## 2026-09-03 — mic-deselect detection (relay contact side)

The v2 ngspice `.op` (`bom_mic_deselect_detect.cir`) showed that with the NC pin
open, a de-selected notebook's mic pin floats to the full ~2.5 V bias rail —
identical to what its codec sees with **no microphone plugged in**. Codecs that
re-sense the jack then mark the headset mic gone and fall back to the notebook's
**internal** mic (Teams/Zoom would transmit room audio instead of silence), often
with a "mic disconnected" toast and a pop on return.

**Fix (4 resistors, no logic/POR/power change):**

| # | change | reason |
|---|---|---|
| 9 | swap relay **COM ↔ NO**: `COM` (5/6) → `NBn_MIC`, `NO` (10) → `HS_MIC` (common) | frees the NC contact to carry a bias load in the de-energised state |
| 10 | `NC` (1) → **`R20–R23` 2.2 kΩ → GND**, one per relay | a de-selected / muted notebook now reads **~1.1 V** on its mic pin — the same as the selected path's live electret (sim MIC7) — so every codec keeps "headset mic present, silent": no disconnect event, no internal-mic fallback, no pop. Bonus: at power-on and 2-button mute all four notebooks read "mic present, muted". |

Sim: `simulation/` updated (SPDT relay model, `mic_path.cir` / `selector.cir`
rewired, new check **MIC7**). BOM ~73 parts.

## 2026-09-04 — jack footprint from the real part data + component-level ngspice sim

**Jack footprint rebuilt from the LCSC/EasyEDA data for C17701689** (part uuid
`c718c744…`) and the HX PJ-320A-3P datasheet, replacing the earlier guess that
followed the generic KiCad PJ320E pattern (T/R 4 mm apart). The real part:
three 1.2 × 0.6 mm oval THT pads **numbered 2 / 3 / 4** (inline pair **7 mm**
apart + offset sleeve), two Ø1.0 mm NPTH posts 6.0 mm apart. The datasheet
schematic draws **terminal 3 as the tip leaf-spring**, so the schematic symbol
and footprint now use pins 2/3/4 and wire **pin 3 → mic, pins 2 & 4 → GND**
(grounding both moots the ring-vs-sleeve question). `bomcpl.py` gets a TO-92
CPL rotation offset. Silk tidied in `post.py` — DRC silk warnings 114 → 1.

**Component-level simulation added.** The box has `libngspice` but no `ngspice`
binary and PySpice rejects ngspice 42, so `scripts/ngspice_shared.py` is a small
ctypes binding to the shared library. `scripts/spice_sim.py` builds every
scenario netlist programmatically and runs it in **real ngspice-42** with
datasheet models (1N4148, 2N7000, G5V-1 coil+contact, CD4043B NOR latch,
electret JFET): full KVM button sequence, POR swept over VBUS ramps 0.05–100 ms,
mic path over the notebook bias spread 1.0–2.7 V / 1.0–2.7 k, power/TVS/CC.
**25 / 25 pass.** The MNA `validate.py` stays as a **22 / 22** analytic
cross-check. `scripts/spice_video.py` renders a 42 s mp4 from the ngspice traces.
Local symbol pinouts verified against the TI CD4043B / ON-Semi 2N7000 datasheets
(S1 = pin 4, R1 = pin 3, OE = pin 5; 2N7000 S-G-D = 1-2-3).

**Known items:** J1 GCT USB4085 pad-pitch clearance (documented in
`.kicad_dru`); cosmetic silk overlaps on the passive clusters; verify the exact
3.5 mm jack pin map and the `5k1` / `47µF` LCSC codes before ordering.
