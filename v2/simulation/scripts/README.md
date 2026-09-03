# MeetingHub-4 v2 — simulation / requirement validation

`LTspice` proper needs Windows/Wine + a GUI and cannot run in this environment,
so the electrical validation was done with a small purpose-built MNA engine
(`scripts/mna.py`: `.op` / `.ac` / `.tran`, ~300 lines) driven by circuit values
pulled straight from `../hardware/PCB/MeetingHub-4-v2.net` and the KiCad sheets.
All gain / mute / frequency-response / impedance numbers come from `.op` / `.ac`
(exact complex solves — no time-step error). Equivalent **LTspice `.cir`
netlists** are in `../ltspice/` — open them in real LTspice
(`File ▸ Open`, or `ltspice -b 0x_*.cir`) to reproduce every result and to drop
in vendor NJM4580 / NJM4556A / LM358 models.

## Run

```
uv venv && uv pip install numpy scipy matplotlib imageio-ffmpeg
.venv/bin/python scripts/validate.py       # 21 A–G checks  -> plots/ + validation_results.json
.venv/bin/python scripts/mixer_mute.py     # 6 mute/mixer checks -> plots/M_mute_law.png
.venv/bin/python scripts/select_logic.py   # one-hot sequence -> plots/E_select_logic.png + mic-selector.mp4
.venv/bin/python scripts/full_sim.py       # the full ~70 s end-to-end video (slow, ~4 min render)
.venv/bin/python scripts/video.py          # short 3-scene video
.venv/bin/python scripts/audio.py          # audio_in.wav / audio_out.wav
```

## Files

| file | what |
|---|---|
| `scripts/mna.py` | MNA solver (R/C/L, V/I with SIN/PWL/AC, VCVS/VCCS, 1-pole op-amp macro) |
| `scripts/validate.py` | the 21 requirement checks, blocks A–G |
| `scripts/mixer_mute.py` | "is zero volume actually silent?" — 6 checks + the v1-bug control |
| `scripts/select_logic.py` | one-hot CD4043B logic/timing sim + button-sequence video |
| `scripts/full_sim.py` | 10-chapter end-to-end video |
| `scripts/video.py` | short 3-scene video |
| `scripts/audio.py` | filters a test signal through the simulated Jn→J6 transfer function |
| `../ltspice/*.cir` + `opamp.sub` | LTspice-runnable equivalents |
| `../plots/*.png` | A VBIAS Zout · B monitor resp · C mixer clip · D chain gain · E select logic · F POR · M mute law |
| `../MeetingHub-4-v2-*.mp4` | full-simulation · simulation (short) · mic-selector |
| `../audio_in.wav` / `../audio_out.wav` | dry vs. processed (headset-jack) audio |
| `../validation_results.json` | machine-readable pass/fail |

## ngspice cross-check (real BOM device models) — `../spice/`

`bom_power_vbias.cir`, `bom_audio.cir`, `bom_selector.cir`, `vbias_stability.cir`
+ `models.lib` (datasheet models: NJM4580 / NJM4556A / LM358 macromodels,
1N4148, 2N7000, P6KE6.8A, CD4043B latch, G5V-1 relay). Run:

```
ngspice -b bom_power_vbias.cir      # VBIAS 2.4998 V, Zout, power-up, stability
ngspice -b bom_audio.cir           # gain 0.24x loaded, response, mixer clip
ngspice -b bom_selector.cir        # SW2->PC1 … SW5->PC4, mic routing, POR
python scripts/plot_bom.py         # -> plots/BOM_*.png
```

ngspice was installed rootless via micromamba + conda-forge (`ngspice` package).
All results match the idealised MNA runs (see `docs/v2-simulation-validation.md` §N).
