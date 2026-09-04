# MeetingHub-4 v3 — simulation / requirement validation

Scope: the **mic selector** (one-hot CD4043B latch + diode matrix + POR +
2N7000 drivers + G5V-1 relays) and the USB-C power entry. No audio path — v3
has none.

Two independent simulations (see `../docs/v3-simulation-validation.md`):

- **A. component-level** — real **ngspice-42** through `libngspice`
  (`scripts/ngspice_shared.py`, a ~150-line ctypes binding; the box has no
  `ngspice` binary and PySpice rejects ngspice 42). Datasheet device models in
  `../spice/models.lib`. **`scripts/spice_sim.py` → 25 / 25.**
- **B. analytic cross-check** — a small MNA engine (`mna.py`) + an event-stepped
  CD4043B logic model. **`scripts/validate.py` → 22 / 22.**

## Run

```
cd simulation
uv venv .venv && uv pip install --python .venv numpy scipy matplotlib imageio-ffmpeg PySpice
.venv/bin/python scripts/spice_sim.py       # A: ngspice component-level -> spice_results.json + spice/*.dat
.venv/bin/python scripts/validate.py        # B: MNA + logic cross-check -> validation_results.json
.venv/bin/python scripts/spice_video.py     # 42 s component-level video from the ngspice traces
.venv/bin/python scripts/select_logic.py    # one-hot sequence -> plots/S_select_logic.png + mic-selector.mp4
.venv/bin/python scripts/plots.py           # plots/P_por.png, plots/MIC_path.png, plots/scorecard.png
.venv/bin/python scripts/full_sim.py        # analytic end-to-end video
```

`ngspice_shared.py` finds `/usr/lib/.../libngspice.so*` on its own.

## Files

| file | what |
|---|---|
| `scripts/ngspice_shared.py` | ctypes binding to `libngspice` (load netlist, run, pull real + complex result vectors, capture the console) |
| `scripts/spice_sim.py` | **A** — builds every scenario netlist programmatically, runs it in ngspice with datasheet models, checks 25 requirements, writes `spice_results.json` + `spice/*.dat`, re-exports the `.cir` decks |
| `scripts/spice_video.py` | 42 s mp4 rendered straight from the ngspice traces (`spice/selector_tran.dat`, `mic_ac.dat`, `mic_xtalk.dat`) |
| `scripts/mna.py` | **B** — MNA solver (R/C/L, V/I with SIN/PWL/AC, VCVS/VCCS, 1-pole op-amp) — shared with v2 |
| `scripts/select_logic.py` | one-hot CD4043B logic/timing model + button-sequence video |
| `scripts/validate.py` | **B** — the S / P / PW / MIC checks against the MNA + logic model |
| `scripts/plots.py` | POR transient, mic-path AC, scorecard PNGs |
| `scripts/full_sim.py` | analytic end-to-end video |
| `../spice/models.lib` | datasheet models: 1N4148, 2N7000, P6KE6.8A, CD4043B NOR latch, G5V-1 coil+contact, electret JFET capsule |
| `../spice/selector.cir` | full one-hot logic + POR + drivers + relays + mic (ngspice/LTspice `tran`) |
| `../spice/por.cir` | power-on reset timing vs VBUS ramp rate |
| `../spice/mic_path.cir` | passive mic path: bias (selected + de-selected), AC, crosstalk |
| `../spice/*.dat` | raw ngspice traces used by the video |
| `../spice_results.json` / `../validation_results.json` | machine-readable pass/fail (A / B) |
| `../MeetingHub-4-v3-*.mp4` | spice-simulation (A) · mic-selector · full-simulation (B) |

## Result

**A: 25 / 25 (ngspice, datasheet models).  B: 22 / 22 (analytic).**

Design changes that came out of the sim:
1. **C5 (POR cap) 1 µF → 10 µF** — a slow USB-C soft-start ramp can't release the
   reset before the rail is up (`docs/v3-simulation-validation.md` §P).
2. **relay COM ↔ NO swapped + `R20–R23` 2.2 kΩ on each NC → GND** — a de-selected
   notebook reads ~1.1 V ("mic present") instead of open-circuit ("no mic")
   (§MIC7).
