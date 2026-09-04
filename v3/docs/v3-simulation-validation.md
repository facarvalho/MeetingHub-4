# MeetingHub-4 v3 — circuit simulation & requirement validation

Date: 2026-09-04 · scope: electrical validation of the **mic selector** against
the requirements in `v3-DESIGN.md`.

## Two independent simulations

| | engine | models | checks | script |
|---|---|---|---|---|
| **A. Component-level** | **ngspice-42** (via `libngspice`, `scripts/ngspice_shared.py`) | datasheet device cards — 1N4148, 2N7000, Omron G5V-1 coil+contact, CD4043B NOR latch, electret JFET capsule (`spice/models.lib`) | **25 / 25** | `scripts/spice_sim.py` → `spice_results.json` |
| **B. Analytic cross-check** | purpose-built MNA solver (`scripts/mna.py`, ~300 lines: `.op`/`.ac`/`.tran`) + an event-stepped CD4043B logic model | ideal R/C/L + 1-pole devices | **22 / 22** | `scripts/validate.py` → `validation_results.json` |

Simulation A is the primary result — it runs the **actual circuit netlist with
the actual parts**, driven the way the board is really used (VBUS ramps, buttons
pressed in sequence, real notebook mic-bias spread). Simulation B is a fast
sanity net that re-derives the key numbers from first principles; the two agree
to within the tolerance of the behavioural models.

LTspice users: `spice/selector.cir`, `spice/por.cir`, `spice/mic_path.cir` are
standalone decks (`.include models.lib`) that reproduce the A scenarios — open
them in LTspice and drop in vendor models.

Outputs: `MeetingHub-4-v3-spice-simulation.mp4` (component-level, 42 s),
`MeetingHub-4-v3-mic-selector.mp4` (button sequence),
`MeetingHub-4-v3-full-simulation.mp4` (analytic overview),
`plots/*.png`, `spice/*.dat`, `spice_results.json`, `validation_results.json`.

---

## A. Component-level ngspice results — 25 / 25

### S. one-hot selector — full transient with the real parts (8 / 8)

`spice/selector.cir`: VBUS PWL ramp → `RF1` (PTC) → `C1/C2/C3/C4`; four button
PWL sources → `SWB` switches → the 16× `D1N4148` matrix → four `CD4043LATCH`
(OE tied high) → `R12–R19` + `XQ1–XQ4` (`Q2N7000` + body diode) → `XK1–XK4`
(`RELAY_G5V1`: 178 Ω / 0.46 H coil, SPDT gold contact) → the electret on
`HS_MIC` and four notebook bias loads. Single `tran` over the whole KVM
sequence; the relay energised at each checkpoint is read from `v(qoN)`.

| action (single press) | expected | measured |
|---|---|---|
| power on | muted (no relay) | **relay 0 — mic muted** ✔ |
| tap SW1 | mic → NB1 | **relay 1** ✔ |
| tap SW2 | mic → NB2, NB1 released | **relay 2** ✔ |
| tap SW3 | mic → NB3 | **relay 3** ✔ |
| tap SW4 | mic → NB4 | **relay 4** ✔ |
| hold SW2 + SW3 | muted while held | **relay 0** ✔ |
| release the two buttons | **stays muted** | **relay 0** at t = 2.95 s ✔ |
| — during the VBUS ramp | POR keeps it muted | **PORN = 4.6 V at 20 ms**, every Q = 0 ✔ |

Exclusive because button *n* forward-biases `SETn` **and** the `RSTx` of the
other three through the diode matrix. Only one coil is ever energised
(≈ 27.6 mA). A NOR latch left at S = R = 1 holds Q = 0, so two buttons held →
all four muted, and it stays muted when they're released.

### P. power-on reset vs VBUS ramp rate (10 / 10 — 6 ramps × {no latch, PORN holds})

`C5 = 10 µF` / `R11 = 100 k`, `D22–D25` clamp `PORN` onto the four `RST` lines.
The VBUS PWL ramp is swept **0.05 ms → 100 ms**:

| VBUS ramp | max Q over the whole run | PORN when the rail settles |
|---|---|---|
| 0.05 ms | 0.00 V | 2.26 V *(latches just power up at 0; faster than any real inrush-limited supply)* |
| 0.5 ms | 0.00 V | 4.92 V |
| 2 ms | 0.00 V | 4.97 V |
| 10 ms | 0.00 V | 4.84 V |
| 50 ms | 0.00 V | 4.26 V |
| 100 ms | 0.00 V | 3.69 V |

**No relay ever latches, on any ramp.** This is the fix that came out of the
sim: at **C5 = 1 µF** a slow (> ~30 ms) ramp releases `PORN` below the 2.5 V RST
threshold *before the rail is up* and a latch could power up energised. **10 µF**
(same value / reason as v2's C24) holds `PORN` ≈ `VBUS` through any realistic
ramp.

### MIC. passive mic path (7 / 7)

`spice/mic_path.cir`: one relay energised (`Vc2 = 0.08 V`, the 2N7000 `Vds(on)`),
the other three idle; electret JFET capsule on `HS_MIC`; each notebook a
2.2 V / 2.2 k source with 40 pF of jack/wiring stray.

| # | requirement | result | ngspice |
|---|---|:--:|---|
| MIC1 | usable DC bias reaches the electret (selected) | ✅ | **0.89 V** at the capsule (0.5–1.8 V window) |
| MIC7 | **a de-selected / muted notebook still reads "mic present"** | ✅ | **1.10 V** via NC → 2.2 kΩ → GND — vs **2.20 V** (open) before the fix, which reads as *"no microphone"* and makes many codecs fall back to the internal mic |
| MIC2 | routed-path response (selected) | ✅ | **0.00 dB ripple** 300 Hz–3.4 kHz, −3 dB at **200 kHz** |
| MIC3 | crosstalk to a de-selected notebook | ✅ | **−83 dB @1 kHz, −63 dB @10 kHz** (10 pF across the open NO contact into 2k2‖2k2) |
| MIC4 | mic reads "present" across the notebook bias spread | ✅ | electret + de-selected pin both sit at **45–69 % of the rail** for every rail 1.0–2.7 V / source 1.0–2.7 k — never near 0 (short), never near the rail ("no mic") |
| MIC5 | jack wiring: **pin 3 (tip) = mic, pins 2 & 4 = GND** | ✅ | datasheet terminal 3 is the tip leaf-spring; grounding **both** 2 and 4 is robust to a CTIA Y-splitter *and* to the ring-vs-sleeve pin-order question. Verified against the LCSC/EasyEDA pad data (part uuid `c718c744…`) + the HX PJ-320A-3P datasheet. Bring-up: meter pin 3 to the plug tip. |
| MIC6 | mute states carry no headset audio; every NB still "present" | ✅ | all four COMs rest on NC (2k2 → GND), none on `HS_MIC`; each notebook reads **1.10 V** |

### PW. power / system (4 / 4)

| # | requirement | result | ngspice |
|---|---|:--:|---|
| PW1 | total current ≪ 500 mA PTC hold and ≪ USB-C default | ✅ | **28.4 mA** (coil 27.6 + 2× CC 1.3 + Iq ≈ 0.1) |
| PW2 | PTC (RXEF050) margin | ✅ | 6 % of I_hold; ~1 Ω hot → ~28 mV drop |
| PW3 | VBUS transient clamp (P6KE6.8A, cathode → VBUS, pre-fuse) | ✅ | bus clamps at **≈ 7 V** under a 15 A surge — far below the ~18 V CD4043B abs-max; the surge returns through D1 to GND, not through F1 |
| PW4 | any USB-C source turns VBUS on (R1/R2 = 5k1 Rd) | ✅ | 5.1 kΩ is inside the 4.08–6.12 kΩ sink-detect window (v2 left CC floating) |

---

## B. Analytic MNA cross-check — 22 / 22

Same requirements, re-derived with the MNA solver and the logic model:
S (8, `select_logic.py`), P1–P3 (POR `.tran`, C5 = 10 µF), PW1–PW4 (power
arithmetic + CC window), MIC1–MIC7 (electret RO = 2200, RBIAS = 2200,
VBIAS = 2.2, R_contact = 0.1 Ω, R_NC = 2200). Every number matches simulation A
within the behavioural-model tolerance. Detail in `validation_results.json`.

---

## Limitations

- The CD4043B, 2N7000 and G5V-1 are **behavioural / datasheet-level** models, not
  vendor SPICE. Pin-outs are the project-local symbols — **verified against the
  TI CD4043B and ON-Semi 2N7000 datasheets** (S1 = pin 4, R1 = pin 3, OE = pin 5;
  2N7000 S-G-D = 1-2-3), still worth a continuity check on the first article.
- The G5V-1 coil inductance (~0.46 H) and pull-in/drop-out are estimated from the
  5 ms operate time — the logic result (exclusivity, power-on mute) does not
  depend on the exact value.
- Electret and notebook mic-input parameters are typical; the MIC4 sweep covers
  the realistic spread (1.0–2.7 V / 1.0–2.7 k) and every check still passes.
- The 10 J1-internal DRC clearance items (GCT USB4085 pad pitch) are a
  footprint/layout matter, not electrical — documented in `.kicad_dru`.
