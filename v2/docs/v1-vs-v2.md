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
| Board | 265 × 160 mm, square corners | **192 × 156 mm, rounded corners (R6), 6× M3 holes** |
| SMD parts | C1/C4/C21 (0603), D1 (SOD-964), **4 SMD pads on each of J2–J6** | **none anywhere — 100 % through-hole**, verified pad-by-pad |
| Enclosure | (panel-wired controls) | **top + bottom acrylic only, sides open** — controls PCB-mounted on the front edge, operated directly (no front panel) |
| Front edge | pots RV1–RV5 + selectors SW2–SW5 + headset J6 | can bodies ~flush with the open edge, only shafts / plungers / barrel overhang |
| Rear edge | — | the 4 notebook TRRS jacks J2–J5 + USB-C power J1 |
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
| C1, C4, C21, **C22, C25** | 5 | 100 nF | Yageo CC0603KRX7R9BB104 **SMD 0603** (C14663) | Vishay K104K15X7RF5TH5, X7R radial P5 (C2167231) | **Δ** SMD→THT; qty 3→5 |
| C2, C3, C16, C19, **C24** | 5 | 10 µF | CX KM106M016D11RR0VH2FP0 (C43799) | same (C43799) | **~** was 4 — C24 moved here (POR cap 1 µF → 10 µF for a longer power-on reset) |
| C5–C15, C18 | 12 | 1 µF | Vishay K105K20X7RF5TH5 (C2167638) | same (C2167638) | **=** (12) |
| C17, C20 | 2 | 220 µF | Chengx KM227M035F12RR0VH2FP0 (C2063) | same (C2063) | **=** |
| **C23** | 1 | 100 µF | — | Jianghai NXA16V100M5×11, 16 V radial 2.5 mm pitch (C346930) | **+** select-logic +5 V bulk |
| **C26** | 1 | 1 µF | — | same as C5 group (C2167638) | **+** VBIAS bulk |
| D1 | 1 | TVS 5 V | Nexperia PTVS5V0Z1USKYL **SMD SOD-964** (C553448) | **BORN P6KE6.8A** 600 W uni, **DO-15 THT** (C152132) | **Δ** SMD→THT, bigger clamp |
| D2–D5 | 4 | 1N4148 | LGE 1N4148 DO-35 (C402212) | same (C402212) | **=** (free-wheel) |
| **D10–D29** | 20 | 1N4148 | — | same part (C402212) | **+** 20× one-hot diode matrix |
| F1 | 1 | 500 mA PTC | Bourns MF-RG500 (C1562150) | **Littelfuse RXEF050** (C76399) | **Δ** MF-RG500 was thin stock; same PTC spec |
| J1 | 1 | USB-C | GCT USB4085-GF-A (C7095263) | same (C7095263) | **=** — now on the **rear** edge, 180° |
| J2–J6 | 5 | 3.5 mm TRRS | HanElectricity PJ-320D — **hybrid THT body + 4 SMD signal pads** (C22459515) | **Korean Hroparts PJ-3200B-4A — 4-conductor TRRS, 100 % THT** (C136687), pads T/R1/R2/S. Local footprint `Jack_3.5mm_PJ-3200B-4A_Horizontal` built from the HRO datasheet. | **Δ** all-THT; J2–J5 barrels overhang the **rear** edge (CPL 90°), J6 the **front** edge (CPL 270°). No SMD pads → the v1 SMD-pad DFM issue is gone. |
| K1–K4 | 4 | SPDT relay | Omron G5V-1-DC5 (C28695) | same (C28695) | **=** — coil re-wired for MOSFET low-side drive |
| R1, R2, R5–R12 | 10 | 10 k | Yageo CFR-25JB-52-10K (C5618323) | same (C5618323) | **~** was 12, now 10 |
| **R3, R4** | 2 | **3k3** | was 10 k (C5618323) | CCO MF1/4W-3.3K ±1% axial THT (C119335) | **Δ** mixer feedback 10k→3k3 (0.33×/ch — 4 sources cannot clip) |
| R13, R17, **R21–R28, R33–R37** | 15 | 100 k | Yageo MFR-25FBF52-100K (C1364475) | same (C1364475) | **~** was 2, now 15 (one-hot pulldowns) |
| R14, R15, R18, R19, **R29–R32** | 8 | 1 k | CCO CF1/4W-1KR-J (C120055) | same (C120055) | **~** was 4, now 8 (MOSFET gate series) |
| R16, R20 | 2 | 47 R | VO CR1/4W-47R-OT52 (C2896824) | Yageo MFR-25FBF52-47R5 (47.5 Ω ±1 %) (C3373549) | **Δ** thin stock on the VO part; 1 % off nominal, series/isolation only |
| **R38** | 1 | 47 R | — | same part (C3373549) | **+** VBIAS buffer isolation |
| RV1–RV4 | 4 | 10 k dual | Alps **RK09L1240A12**, **vertical** (C380211) | Alps **RK09712200HA**, **horizontal** (C470545) — same as RV5 | **Δ** now horizontal, all 5 pots one identical part. In stock but JLC's BOM tool needs it selected manually (Extended part). |
| RV5 | 1 | 10 k dual, horizontal | Alps RK09712200HA (C470545) | same (C470545) | **=** — RV1–RV5 on the front edge, can body ~flush with the open edge (y = FRONT-5.5), ~20 mm of bushing + shaft overhang for the knob. |
| SW2–SW5 | 4 | mic select | G-Switch PS-22F03NC **latching** (C2848947) | **C&K PTS645VK392LFS** — 6 mm right-angle (side-actuated) momentary tact, THT (C285519) | **Δ** latching→momentary (one-hot does the latching); right-angle so the plunger faces out the open front edge |
| SW1 | 0 | MUTE | (removed in the repo before v2) | **not present** | removed |
| U1 | 1 | mixer op-amp | **NE5532** HGSEMI NE5532N (C2987282) | **NJM4580DD** JRC, DIP-8 (C5184871) | **Δ** NE5532 is out of spec at 5 V single supply |
| U2 | 1 | headphone op-amp | JRC NJM4556A (C2838125) | same (C2838125) | **=** |
| **U3** | 1 | VBIAS buffer | — | **TI LM358P** DIP-8 (C5213) | **+** buffers the 2.5 V mid-rail (v1 bug 3) |
| **U4** | 1 | one-hot latch | — | **CD4043BE** lingxingic, DIP-16 (C22390239) | **+** exclusive mic selector |
| **Q1–Q4** | 4 | coil driver | — | **2N7000** TO-92 (C9114) | **+** relay low-side drivers |
| TP1 | 1 | +5 V test point | TestPoint_THTPad (—) | same | **=** |
| **TP2** | 1 | GND test point | (mechanical-only on v1 PCB) | added, wired to GND | **+** |
| **MH1–MH6** | 6 | M3 hole | MountingHole_3.2mm_M3 (—) | same | **+** 4 corners + **MH5/MH6** (rev-7) ~12 mm behind the front edge to support the pot-knob row |

**Total fitted parts (excl. MH/TP): 117.**  Distinct sourced lines: 23.

## Bring-up check

The pot-direction fix assumes the standard Alps RK097 terminal convention:
**terminal 1 = full-CCW end, terminal 3 = full-CW end** (v2 wires the signal to
3/6, VBIAS to 1/4, wiper to 2/5 → CW = louder, full-CCW = wiper on VBIAS =
silent). Confirm on the first article: with the pot full-CCW, resistance
wiper↔terminal 1 should read ≈ 0 Ω.

## 3. Ordering (rev-8)

Every LCSC code was re-verified against JLCPCB's assembly library on
2026-09-03: all **in stock, min-order 1, with a ready LCEDA footprint + 3D
model** (no "footprint designed after payment" delay). See the components
reference (`components.html`) or `hardware/BOM/BOM-PCBA-MeetingHub-4-v2.csv`.

**Upload `hardware/BOM/BOM-JLC-MeetingHub-4-v2.csv`** (native
`Comment,Designator,Footprint,JLCPCB Part #` format) so JLC assigns every part
by code directly — the plain PCBA BOM leaves Extended parts (RV1–RV5 /
C470545) unmatched in the auto-matcher.

Direct carry-over from a v1 build (unchanged part): **C2/C3/C16/C19,
C5–C15/C18, C17/C20, D2–D5, J1, K1–K4, RV5, U2, TP parts, mounting holes.**

Watch stock: U2 NJM4556AD (~170), RK09712200HA (~185, need 5), CD4043BE(LX)
(~490).
