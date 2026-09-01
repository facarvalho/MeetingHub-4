# MeetingHub-4 — v1 vs v2 component comparison

"v1" = the fabricated 4-layer board (JLCPCB lot `W2026080810364558`, as built —
see `../../v1/hardware/BOM/BOM-PCBA-MeetingHub-4-v1.csv`).
"v2" = this project.

LCSC part links: `https://www.lcsc.com/product-detail/<code>.html`
(e.g. [C43799](https://www.lcsc.com/product-detail/C43799.html)).

## 1. Summary

| | v1 | v2 |
|---|---|---|
| PCB layers | 4 (GND + 5 V inner planes) | **2** (F.Cu / B.Cu, GND pour both sides) |
| Board | 265 × 160 mm, square corners | **286 × 157 mm, rounded corners (R8), 4× M3 holes** |
| SMD parts | C1/C4/C21 (0603), D1 (SOD-964), **4 SMD pads on each of J2–J6** | **none anywhere — 100 % through-hole**, verified pad-by-pad |
| Front panel | pots + selectors + headset (panel-wired) | **pots + selectors + headset, PCB-mounted, on the front edge** |
| Rear | — | **the 4 notebook TRRS jacks + USB-C power, on the rear edge** |
| Mic selector | latching push-locks, relay driven straight from the button | **on-board one-hot latch** (U4 CD4043B + diode matrix + 4× 2N7000), momentary buttons |
| Mute button | SW1 | **removed** (power-on = nothing latched = mic muted) |
| Mic volume | none (mic path is passive) | **still none — passive, no mic amp, nothing to remove** |
| Op-amp supply | NE5532 / NJM4556A on 5 V (NE5532 out of spec) | **NJM4580** (mixer) + NJM4556A — both valid at 5 V |
| Distinct parts | ~19 lines | ~28 lines |

## 2. Part-by-part

Legend: **=** identical to v1 · **~** same part, different quantity ·
**Δ** changed part · **+** new in v2.

| v2 ref(s) | Qty | Value | v1 part (LCSC) | v2 part (LCSC) | Status |
|---|---|---|---|---|---|
| C1, C4, C21, **C22, C25** | 5 | 100 nF | Yageo CC0603KRX7R9BB104 **SMD 0603** (C14663) | 100 nF THT ceramic disc, P5.0 (verify C49678) | **Δ** SMD→THT; qty 3→5 |
| C2, C3, C16, C19, **C24** | 5 | 10 µF | CX KM106M016D11RR0VH2FP0 (C43799) | same (C43799) | **~** was 4 — C24 moved here (POR cap 1 µF → 10 µF for a longer power-on reset) |
| C5–C15, C18 | 12 | 1 µF | Vishay K105K20X7RF5TH5 (C2167638) | same (C2167638) | **=** (12) |
| C17, C20 | 2 | 220 µF | Chengx KM227M035F12RR0VH2FP0 (C2063) | same (C2063) | **=** |
| **C23** | 1 | 100 µF | — | 100 µF 16 V THT radial D6.3 (verify C2909340) | **+** select-logic +5 V bulk |
| **C26** | 1 | 1 µF | — | same as C5 group (C2167638) | **+** VBIAS bulk |
| D1 | 1 | TVS 5 V | Nexperia PTVS5V0Z1USKYL **SMD SOD-964** (C553448) | **P6KE6.8A** 600 W uni, **DO-15 THT** (verify C736020) | **Δ** SMD→THT, bigger clamp |
| D2–D5 | 4 | 1N4148 | LGE 1N4148 DO-35 (C402212) | same (C402212) | **=** (free-wheel) |
| **D10–D29** | 20 | 1N4148 | — | same part (C402212) | **+** 20× one-hot diode matrix |
| F1 | 1 | 500 mA PTC | Bourns MF-RG500 (C1562150) | same (C1562150) | **=** |
| J1 | 1 | USB-C | GCT USB4085-GF-A (C7095263) | same (C7095263) | **=** — now on the **rear** edge, 180° |
| J2–J6 | 5 | 3.5 mm TRRS | HanElectricity PJ-320D — **hybrid THT body + 4 SMD signal pads** (C22459515) | **PJ-320E — 100 % through-hole** (verify C2939642), same R1/R2/S/T pad names | **Δ** all-THT; J2–J5 (rot 0) barrels overhang the **rear** edge, J6 (rot 180) barrel overhangs the **front** edge (plug enters at the footprint's −Y). No SMD pads anywhere, so the v1 SMD-pad-size DFM issue is gone. |
| K1–K4 | 4 | SPDT relay | Omron G5V-1-DC5 (C28695) | same (C28695) | **=** — coil re-wired for MOSFET low-side drive |
| R1, R2, R5–R12 | 10 | 10 k | Yageo CFR-25JB-52-10K (C5618323) | same (C5618323) | **~** was 12, now 10 |
| **R3, R4** | 2 | **3k3** | was 10 k (C5618323) | 3k3 axial THT (verify C22978) | **Δ** mixer feedback 10k→3k3 (0.33×/ch — 4 sources cannot clip) |
| R13, R17, **R21–R28, R33–R37** | 15 | 100 k | Yageo MFR-25FBF52-100K (C1364475) | same (C1364475) | **~** was 2, now 15 (one-hot pulldowns) |
| R14, R15, R18, R19, **R29–R32** | 8 | 1 k | CCO CF1/4W-1KR-J (C120055) | same (C120055) | **~** was 4, now 8 (MOSFET gate series) |
| R16, R20 | 2 | 47 R | VO CR1/4W-47R-OT52 (C2896824) | same (C2896824) | **=** |
| **R38** | 1 | 47 R | — | same part (C2896824) | **+** VBIAS buffer isolation |
| RV1–RV2 | 4 | 10 k dual | Alps **RK09L1240A12**, **vertical** (C380211) | Alps **RK09712200HA**, **horizontal** (C470545) — same as RV5 | **Δ** now horizontal, all 5 pots one identical part |
| RV5 | 1 | 10 k dual, horizontal | Alps RK09712200HA (C470545) | same (C470545) | **=** — footprint's Edge.Cuts slot moved to Dwgs.User (rounded rectangle outline instead). RV1–RV5 all on the front edge, bodies overhang. |
| SW2–SW5 | 4 | mic select | G-Switch PS-22F03NC **latching** (C2848947) | **6 mm momentary tact THT** (verify C318884) | **Δ** latching→momentary (one-hot does the latching) |
| SW1 | 0 | MUTE | (removed in the repo before v2) | **not present** | removed |
| U1 | 1 | mixer op-amp | **NE5532** HGSEMI NE5532N (C2987282) | **NJM4580** JRC NJM4580D (verify C7466) | **Δ** NE5532 is out of spec at 5 V single supply |
| U2 | 1 | headphone op-amp | JRC NJM4556A (C2838125) | same (C2838125) | **=** |
| **U3** | 1 | VBIAS buffer | — | **LM358** DIP-8 (verify C7950) | **+** buffers the 2.5 V mid-rail (v1 bug 3) |
| **U4** | 1 | one-hot latch | — | **CD4043BE** TI, DIP-16 (C39537) | **+** exclusive mic selector |
| **Q1–Q4** | 4 | coil driver | — | **2N7000** TO-92 (C9114) | **+** relay low-side drivers |
| TP1 | 1 | +5 V test point | TestPoint_THTPad (—) | same | **=** |
| **TP2** | 1 | GND test point | (mechanical-only on v1 PCB) | added, wired to GND | **+** |
| **MH1–MH6** | 6 | M3 hole | MountingHole_3.2mm_M3 (—) | same | **+** 4 corners + **MH5/MH6** (rev-7) ~12 mm behind the front edge to support the pot-knob row |

**Total fitted parts (excl. MH/TP): 118.**  Distinct sourced lines: ~28.

## Bring-up check (rev-7)

The pot-direction fix assumes the standard Alps RK097 terminal convention:
**terminal 1 = full-CCW end, terminal 3 = full-CW end** (v2 wires the signal to
3/6, VBIAS to 1/4, wiper to 2/5 → CW = louder, full-CCW = wiper on VBIAS =
silent). Confirm on the first article: with the pot full-CCW, resistance
wiper↔terminal 1 should read ≈ 0 Ω.

## 3. What you can re-use from a v1 build

Direct carry-over, no new sourcing:  **C2/C3/C16/C19, C5–C15/C18, C17/C20,
D2–D5, F1, J1, K1–K4, R16/R20, RV5, U2, TP parts, mounting holes.**

New sourcing for v2:  **U1→NJM4580, U3 LM358, U4 CD4043BE, Q1–Q4 2N7000,
+20× 1N4148, +11× 100 k, +4× 1 k, +2× 3k3, +1× 47 R, +C22–C26, D1→P6KE6.8A,
SW2–SW5→6 mm tacts, J2–J6→PJ-320E (all-THT), RV1–RV2→RK09712200HA (5× same
part as RV5).**  Everything is a jelly-bean THT part.

> LCSC codes marked "verify" were filled from catalogue knowledge, not an
> in-stock check — confirm each on lcsc.com (value, package, price, stock)
> before ordering, the same as v1's BOM-003 process.
