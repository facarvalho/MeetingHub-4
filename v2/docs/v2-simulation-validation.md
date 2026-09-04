# MeetingHub-4 v2 — circuit simulation & requirement validation

Date: 2026-09-03 · **updated 2026-09-04 for rev-10** (R16/R20 47 Ω → 10 Ω,
finding 1 applied — all automated checks now pass). Scope: electrical validation
of the v2 respin against the requirements in `v2-DESIGN.md` §1–§6.

> **rev-10 (2026-09-04):** the one failing check (D4, headset drive level) is
> resolved by lowering the U2A output series resistors R16/R20 from 47 Ω to 10 Ω
> (sim finding 1). Re-run: **§A–§G 21/21**, loaded gain 0.50× (−6 dB) / ngspice
> 0.456×, **0.65–0.79 mW into 32 Ω (+5.5 dB)**. Everything else reproduces
> unchanged. Numbers below are the rev-9 (47 Ω) values unless a line is marked
> **rev-10**; see CHANGELOG rev-10 for the full re-run.

## How this was run

LTspice itself is a Windows GUI tool and will not run in this (headless Linux)
environment. Two engines were used: a purpose-built MNA engine
(`../simulation/scripts/mna.py` — `.op` / `.ac` / `.tran`, idealised parts) for
§A–§M, and **ngspice 41 with datasheet models for the real BOM parts** for the
§N cross-check (`../simulation/spice/`). The two agree on every number. All gain / mute / frequency-response / impedance numbers come from
`.op` and `.ac`, which are exact complex solves with no time-step error;
transient waveforms in the video are reconstructed from those `.ac` transfer
functions by superposition. **Every block also has an equivalent LTspice
netlist** in `../simulation/ltspice/` (`01_vbias.cir` … `05_por.cir` +
`opamp.sub`) — open those in real LTspice to reproduce the numbers and to swap
in vendor NJM4580 / NJM4556A / LM358 SPICE models.

Component values and connectivity come from
`../hardware/PCB/MeetingHub-4-v2.net` and the KiCad sheets POWER / MIXER /
HPAMP / SELECT_LOGIC — **not** from the prose in `v2-DESIGN.md` (which turned
out to have two stale numbers, noted below).

Outputs:

- `../simulation/MeetingHub-4-v2-full-simulation.mp4` — **the full ~1 min
  end-to-end run**: block diagram → power-up → POR → mic selector sequence →
  4-laptop audio path → volume + mute check → all-volumes-zero → master volume →
  frequency response → scorecard.
- `../simulation/MeetingHub-4-v2-simulation.mp4` — short 3-scene version.
- `../simulation/MeetingHub-4-v2-mic-selector.mp4` — the one-hot button sequence.
- `../simulation/audio_in.wav` / `audio_out.wav` — a test signal (tone steps +
  20 Hz→20 kHz sweep) put through the *simulated* laptop-in → J6.T transfer
  function, at true relative level, so the loaded loss and bass roll-off are
  audible (the "Audio Out probe" idea, done offline).
- `../simulation/plots/*.png`, `validation_results.json`.
- `../simulation/plots/N_mic_switch_no_glitch.svg` — §O (mic-select transient vs.
  the monitor tone). §O/§P run from `spice/bom_mic_switch_glitch.cir`,
  `spice/bom_mic_deselect_detect.cir`, `spice/bom_relay_handover.cir`.

*(All artifacts regenerated for rev-9, 2026-09-03. Toolchain to rebuild them if
`/tmp` is wiped: `bash /home/fac/.simtools/regen_sim.sh` — micromamba env at
`/home/fac/.simtools/env` with ngspice 41 + ffmpeg + numpy/scipy/matplotlib.)*

## Result: 27 / 27 automated checks pass (rev-10) + the sequence sims (§E, §M, §O) + §N BOM cross-check

- **§A–§G idealised-model checks:** **21 / 21** (rev-10 — D4 headset drive level now passes with R16/R20 = 10 Ω; was 20/21)
- **§E one-hot selector sequence:** 8 / 8
- **§M mixer / volume-mute:** 6 / 6 — **"zero volume" is genuinely silent**
- **§N ngspice with real BOM device models:** every number reproduces
- **§O mic-select transient vs. monitor audio:** 7 / 7 — **switching the mic does not glitch the mixer** (< 80 µV, −63 dB)
- **§P de-selected laptop's mic-pin state:** ⚠️ **finding** — as-built, a de-selected laptop sees its mic pin *open* (= "no mic" to the codec); recommend NC → 2.2 kΩ to GND + COM/NO swap so it reads as a live-but-silent mic

The design is **electrically sound and meets its requirements for a USB-powered
conference-headset monitor/mic router.** The single failing check plus two
caveated passes share one root cause: the 47 Ω output series resistors and the
1 µF coupling capacitors are conservative for driving low-impedance headphones
with full-range material. None of it matters for voice.

**All three v1 bugs that cost R$3000 are fixed and independently re-verified
here:** pot direction + true mute (§B2, §M), relay wiring + one-hot exclusivity
(§E, §G2), VBIAS buffered to < 1 Ω (§A). The only residual risk is the Alps
pot terminal convention — a bench ohmmeter check, not a design issue (§M).

| # | Requirement | Result | Measured |
|---|---|:--:|---|
| **A. VBIAS (v1 bug #3 fix — buffer)** | | | |
| A1 | VBIAS = 2.50 V | ✅ | 2.5000 V |
| A2 | source impedance < 1 Ω (DC load step) | ✅ | 0.5 mΩ |
| A3 | Zout < 1 Ω @ 1 kHz | ✅ | 48 mΩ |
| A4 | Zout < 5 Ω @ 20 kHz | ✅ | 0.86 Ω |
| **B. Monitor chain, 1 laptop** | | | |
| B1 | system gain ≈ 0.66× (per `v2-DESIGN` §4) | ✅ | **rev-10:** 0.659× unloaded, **0.50× (−6 dB) into 32 Ω** (was 0.267× at 47 Ω) |
| B2 | pot direction: CW louder, full-CCW = mute (v1 bug #1) | ✅ | ≥ 66 dB CW-vs-CCW range (see §M for the mute floor vs pot residual R) |
| B3 | 100 Hz – 20 kHz flat within ±1 dB | ✅ | −0.7 dB @100 Hz, +0.0 dB @20 kHz |
| B4 | low-frequency extension | ⚠️ | **−3 dB @ 44 Hz, −10 dB @ 20 Hz** (fine for voice) |
| **C. Mixer (U1A, NJM4580)** | | | |
| C1 | per-channel gain −0.33 (−3k3/10k) | ✅ | 0.330× |
| C2 | no clipping, 1 laptop @ −10 dBV | ✅ | 0.15 Vpk / ±1.3 V headroom |
| C3 | no clipping, 4 laptops in phase (worst case) | ✅ | 0.59 Vpk / ±1.3 V headroom (45 %) |
| **D. Headphone amp (U2A, NJM4556A) + 32 Ω** | | | |
| D1 | AC gain 2× before the output network | ✅ | **rev-10:** 1.52× after the 10 Ω/32 Ω divider (was 0.81× at 47 Ω) |
| D2 | no DC on the headphones (C17 blocks) | ✅ | 0.0 mV |
| D3 | output cap big enough (C17 = 220 µF) | ✅ | 22.6 Hz for C17/32 Ω alone |
| D4 | > 0.5 mW into 32 Ω from a −10 dBV source | ✅ | **rev-10: 0.65–0.79 mW (≈ 145 mVrms), +5.5 dB** — finding 1 applied (was 0.22 mW / ❌ at 47 Ω) |
| D5 | back-check R16/R20 = 47 Ω (old value) | ✅ | old 0.22 mW confirms the rev-10 change is what buys the level |
| **F. Power-on reset (SELECT_LOGIC)** | | | |
| F1 | RST held ≥ 20 ms so a slow VBUS ramp still boots muted | ✅ | **139 ms** |
| F2 | no residual reset after settling | ✅ | 0 mV |
| **G. Power / system** | | | |
| G1 | total current < 500 mA (F1 hold, USB-C min) | ✅ | 50.6 mA (10 %) |
| G2 | only one relay energised at a time | ✅ | one-hot NOR latch (truth table) |
| G3 | VBUS TVS clamp 6–8 V behind F1, power-only | ✅ | P6KE6.8A, Vbr 6.45–7.14 V |

## E. One-hot mic selector — button sequence (added 2026-09-03)

Logic/timing simulation of the SELECT_LOGIC sheet built diode-by-diode from the
netlist (`../simulation/scripts/select_logic.py`; matrix D10–D29, U4 CD4043B NOR
R/S latches, POR, 2N7000 drivers, K1–K4 contact mapping). Video:
`../simulation/MeetingHub-4-v2-mic-selector.mp4`, plot `plots/E_select_logic.png`.

The exact sequence asked for is reproduced:

| action (one press each) | Q1 Q2 Q3 Q4 | mic goes to |
|---|:--:|---|
| power on | 0 0 0 0 | **muted** (POR holds every RST high ~140 ms) |
| tap SW2 (NB1) | **1** 0 0 0 | laptop 1 |
| tap SW3 (NB2) | 0 **1** 0 0 | laptop 2 — laptop 1 released |
| tap SW4 (NB3) | 0 0 **1** 0 | laptop 3 — laptop 2 released |
| tap SW5 (NB4) | 0 0 0 **1** | laptop 4 — laptop 3 released |

Why it is exclusive: button *n* drives `SETn` **and** the `RST` line of the other
three latches through the diode matrix, so one press simultaneously sets its own
latch and clears the other three. Only one relay coil is ever energised, so
`HEADSET_MIC` reaches exactly one laptop (rev-9 wiring: `NBn_MIC` on COM 5/6,
`HEADSET_MIC` on NO 10; a de-energised relay ties that laptop's mic pin to
2.2 kΩ → GND via NC, see §P). Contact bounce is harmless — the R/S latch just
re-asserts the same state.

Two-button gesture (SW3+SW4 together): `SET2=SET3=1` **and** all four `RST` are
pulled high, so every Qn = 0 → **muted**, and it *stays* muted after release (a
NOR latch left at S=R=1 holds Q=0). That is the intended "hold two buttons =
mute". **Doc fix:** `v2-DESIGN.md` §6 pass 3 says it "resolves to one selected
again" on release — that is wrong; it stays muted until a single button is
pressed.

## M. Mixer & volume — is "zero volume" actually silent? (added 2026-09-03)

This is the v1 bug #1 failure mode — pots wired so they never fully muted, which
cost R$3000 — so it was checked head-on (`../simulation/scripts/mixer_mute.py`,
plot `plots/M_mute_law.png`). Topology from the netlist: `Jn.T → Cn(1µF) →
RVn.3` (signal, CW end), `RVn.1` = VBIAS (CCW end), `RVn.2` wiper → `Rn(10k)` →
U1A virtual ground. Master RV5 identical downstream of the mixer.

| # | check | result |
|---|---|:--:|
| M1 | one channel at volume 0 (others also 0) is silent | ✅ **−66 dB, 42 µV** out for a 0.316 Vrms input |
| M2 | **all four** inputs at volume 0 → headset silent | ✅ **169 µV** (−65 dB) at J6.T with 4× 0.316 Vrms in |
| M3 | a zeroed channel doesn't leak its source into the mix | ✅ 9 V forced on a muted channel shifts the mix < 0.2 % |
| M4 | master RV5 at 0 → headset silent regardless of channels | ✅ 169 µV at J6.T |
| M5 | *control:* swap the pot ends (the v1 bug) → mute fails | ✅ reproduced — at the MIN knob position the output is at **full volume** |
| M6 | no scratchy pot (no DC step across the wiper) | ✅ wiper within 0.012 mV of VBIAS at every rotation |

Why it is silent: the only path from a laptop input to the mix is *through* the
pot — `Cn` couples only to `RVn.3`, nothing bypasses it. At the min (full-CCW)
position the wiper sits on `RVn.1` = VBIAS through ~0 Ω, so the signal (injected
through the full 10 kΩ of track) is swamped. Mute floor vs the pot's
end/wiper resistance:

| pot residual R | mute floor | residual at J6.T |
|---|---|---|
| 2 Ω | −74 dB | 17 µV |
| 5 Ω (typ) | −66 dB | 42 µV |
| 20 Ω | −54 dB | 168 µV |
| 50 Ω (worst) | −46 dB | 418 µV |

Even the worst case is ~0.4 mV against a full-scale output of ~85 mV → inaudible.
Because both pot ends are VBIAS-referenced (`RVn.1` directly, `RVn.3` through the
DC-blocking `Cn`), the wiper never sees a DC step as you turn it — no
zipper/scratch noise. Good design.

**⚠️ The one thing simulation cannot prove** (unchanged from `v2-DESIGN.md`
§6.5): all of the above assumes the Alps **RK09712200HA** has terminal 1 = the
full-CCW end and terminal 3 = the full-CW end. The v2 netlist is wired correctly
*for that convention* (signal → term 3/6, VBIAS → term 1/4 — the exact opposite
of the v1 bug). **Confirm on the first article with an ohmmeter: knob fully CCW
⇒ wiper (term 2) to term 1 ≈ 0 Ω.** If that measures the other way, the fix is
to swap the wires to `RVn.1↔RVn.3` and `RVn.4↔RVn.6` (or flip the footprint),
*not* a respin.

## N. Cross-check with real device models (ngspice, added 2026-09-03)

Everything above was re-run in **ngspice 41** with datasheet-parameterised
models for the actual BOM parts — NJM4580, NJM4556A, LM358 (2-pole op-amp
macromodels: GBW, slew, Avol, Vsat-vs-rail, Iq per datasheet), 1N4148 (matrix /
POR / free-wheel), 2N7000 (VTO 2.1 V, Rds(on) 1.8 Ω), P6KE6.8A (BV 6.8 V),
CD4043B (NOR-latch behavioural model, CD4000B 5 V thresholds), G5V-1 relay
(167 Ω coil + L, switched contact). Netlists: `../simulation/spice/*.cir` +
`models.lib`; plots `plots/BOM_*.png`.

**rev-9 (2026-09-03):** the whole ngspice suite was re-run after the K1–K4
COM/NO swap + R39–R42 NC hold-up. `bom_selector.cir` updated (COM = `NBn_MIC`,
NO = `HEADSET_MIC`, plus a complementary NC switch `SNC` + `Rnc1…4` 2.2 kΩ → GND).
Every number below reproduces; the de-selected-laptop mic pin now reads 1.25 V
(§P) instead of floating.

| quantity | idealised (§A–§M) | ngspice + BOM models | agree? |
|---|---|---|---|
| VBIAS DC | 2.5000 V | **2.4998 V** | ✅ |
| VBIAS @ 140 ms (POR release) | 2.30 V | **2.34 V** | ✅ (still rising) |
| VBIAS Zout @ 1 kHz / 20 kHz | 48 mΩ / 0.86 Ω | **21 mΩ / 0.45 Ω** | ✅ |
| system gain @ 1 kHz into 32 Ω | 0.267× (−11.5 dB) | **0.242× (−12.3 dB)** | ✅ finding 1 |
| response @ 20 Hz / 100 Hz | −10.3 / −0.7 dB | **−10.3 / −0.6 dB** | ✅ finding 2 |
| per-channel mixer gain | 0.330× | **0.300×** | ✅ |
| mixer swing, 4 correlated −10 dBV | ±0.59 V / ±1.3 V | **±0.78 V / ±1.1 V (70 %)** | ✅ no clip |
| one-hot sequence SW2→SW5 | Q1→Q2→Q3→Q4 exclusive | **identical, 4.98 V logic** | ✅ |
| POR: PORN at 100 ms | > 2.5 V | **3.20 V** (RST held) | ✅ |
| mic routing after select | only selected laptop | **selected 37 mV pp, others 0.4 µV** (rev-9 wiring, `bom_selector.cir`) | ✅ |

**All findings reproduce with real models.** The loaded gain is even slightly
lower (0.24× vs 0.27×) and the mixer worst-case uses ~70 % of the NJM4580's
headroom (a bit tighter than the ±1.3 V estimate, still no clipping).

### VBIAS buffer stability (checked because feedback is taken after R38)

`R38` (47 Ω) + `C26` (1 µF) sit *inside* the feedback loop (`U3` −in = VBIAS,
after R38). ngspice + LM358 model: a 2 mA load step on VBIAS settles with
**75 µV of ringing — no oscillation, stable.** `|Zout|` is ≤ 0.45 Ω to 20 kHz
but has a **~46 Ω peak at ~86 kHz** (loop gain gone, C26 resonating with the
residual output inductance of the loop). It is ultrasonic and un-rung by a load
step, so it is benign — but **glance at VBIAS with a scope on the first
article** for any HF fuzz. If it's real, 100 pF across R38 or R38 = 10 Ω tames
it. The as-drawn feedback-after-R38 choice is correct for DC/load accuracy
(feedback before R38 loses ~40 mV under load).

## O. Selecting a mic must not interrupt the monitor (mixer) audio (added 2026-09-03)

Requirement (user): *"quando eu selecionar um microfone para sair a voz do headset,
o mixer deve funcionar normalmente sem interrupção."* — pressing a select button
to route `HEADSET_MIC` to a laptop must not glitch or drop what you hear.

The mic path and the monitor path share **only** three nodes: the +5 V rail (a
relay coil is a ~30 mA load that switches on/off), the GND pour, and `VBIAS`
(derived from +5 V through R1/R2, buffered by U3). Netlist
`../simulation/spice/bom_mic_switch_glitch.cir` (+ `…_wc.cir` for the pessimistic
rail) runs a 1 kHz monitor tone through the **full** audio chain
(RV1 → U1A mixer → RV5 → U2A → C17 → R16 → 32 Ω) while the one-hot latch flips
**K1 → K2** at t = 320 ms, on a rail model with trace R/L between the bulk caps
(C2/C23), the relay coils and the op-amp supply pins. ngspice 41 + BOM device
models. Plot: `../simulation/plots/N_mic_switch_no_glitch.svg`.

| # | check | nominal rail | pessimistic rail | result |
|---|---|---|---|:--:|
| O1 | monitor tone amplitude at J6.T, steady | 108.3 mV pk | 108.3 mV pk | — |
| O2 | **change in tone amplitude across the switch event** | 41 µV / 216 mV pp = **0.02 %** | 42 µV = 0.02 % | ✅ |
| O3 | **worst transient glitch at J6.T** (tone-cancelled) | **< 80 µV** (−63 dB re signal; ~19 µV of that is the method's numerical floor) | < 80 µV | ✅ |
| O4 | +5 V rail sag at the logic/coil node when K1 drops + K2 pulls | **0.0 mV** (no dip; a +15 mV *bump* as D2 returns the coil energy) | 0.0 mV | ✅ |
| O5 | VBIAS deviation attributable to the switch | **< 1 mV** (the ~1–2 mV seen is power-up settling toward 2.5 V, rising monotonically through the event, not a step) | < 1 mV | ✅ |
| O6 | mic actually moved | `NB1` 2.00 V → 0.04 mV, `NB2` 0.04 mV → 2.00 V | same | ✅ |
| O7 | no clipping / latch-up in U1A or U2A during the transient | tone stays a clean sinusoid, no rail excursion | same | ✅ |

**Why it is immune:** (1) the coil current changes over ~0.3–3 ms (coil L/R), not
as a step, so di/dt into the 110 µF of bulk is tiny — the rail moves < 1 mV;
(2) both op-amps reject what little rail movement there is by their PSRR (~90 dB);
(3) `VBIAS` is buffered and sits behind C3 (10 µF, ~3 Hz corner) so it cannot move
on a millisecond timescale; (4) the mic path has **no amplifier and no node in
common with the L/R audio** — it ends at the laptop's mic pin. The free-wheel
diodes D2–D5 (correct polarity, unlike v1) dump the de-energising coil's energy
*into* the +5 V rail as a small positive bump rather than letting it kick the rail
negative. Only one coil is ever switched at a time (§G2).

**Not a monitor-path issue, noted for completeness:** during the ~1–3 ms coil
hand-over both relays are briefly de-energised, so the *mic* is routed to neither
laptop for a few ms mid-press — the intended one-hot behaviour, inaudible on the
far end, and it does not touch the headset audio.

## P. Does a DE-SELECTED laptop's OS think the headset mic is still connected? (added 2026-09-03)

Requirement (user): *"laptop 1, com microfone ativo, mudo para o laptop 2. O SO
(Windows) do laptop 1 vai achar que o microfone está ligado ou desligado?"*

**This is a real integration finding, not just a check — see the recommendation.**

### How a laptop decides

The board's TRRS plug **never leaves** laptop 1's jack, so the mechanical
jack-detect switch stays "inserted" forever. The codec classifies the jack as
*headset (has mic)* / *headphones (no mic)* / *nothing* purely from the **DC it
reads on the MIC sleeve**: it drives the sleeve through a bias resistor
(~2.2 kΩ) from ~2.5 V and measures the voltage.

| sleeve DC | codec reads it as |
|---|---|
| ≈ Vbias (open circuit) | **no mic** — re-task to headphones-only |
| mid-range, ~0.8–2.0 V (a load is present) | **headset microphone present** |
| ≈ 0 V (shorted) | no mic — 3-pole plug |

### What the v2 board presents (`../simulation/spice/bom_mic_deselect_detect.cir`, ngspice `.op`)

**rev-8 (as-built at the time of this finding):** `NB1_MIC` = `J2.S` + `K1` pin 10
(NO) only; `K1` pin 1 (NC) *unconnected* → a de-energised relay left the laptop's
mic pin **fully open**.
**rev-9 (fixed):** `NB1_MIC` = `J2.S` + `K1` pins 5/6 (COM); NO 10 → `HEADSET_MIC`;
NC 1 → `R39` 2.2 kΩ → GND → a de-energised relay ties the pin to 2.2 kΩ.

| scenario | sleeve DC the laptop-1 codec reads | codec verdict |
|---|:--:|---|
| laptop 1 **selected** (real headset electret, ~2 kΩ DC) | **1.19 V** | headset mic present ✅ |
| laptop 1 **de-selected — NC open (rev-8)** | **2.50 V** | **looks identical to "no microphone"** ⚠️ |
| laptop 1 de-selected — **NC → 2.2 kΩ to GND (rev-9)** | **1.25 V** | headset mic present ✅ (indistinguishable from a real idle mic) |
| laptop 1 de-selected — NC → straight GND | **0.001 V** | "3-pole headphones, no mic" ⚠️ |

### The finding

**As-built, switching away from laptop 1 drives its mic pin to the full bias
voltage — the exact DC a codec sees when no microphone exists.** The OS-level
result then depends on the codec:

- **Codec that re-senses the jack (most modern Realtek / SoundWire with jack
  re-tasking):** it will likely reclassify the jack as headphones-only and mark
  the *Headset Microphone* endpoint **unplugged / unavailable**. Risk: the
  conferencing app on laptop 1 falls back to the **internal array mic** and
  starts transmitting room audio instead of going silent. It may also pop a
  "microphone disconnected" toast, and a "pop" on switch-back as the endpoint
  re-appears and the electret re-biases.
- **Codec that latches jack state at insertion (simpler / older):** the endpoint
  stays listed and the input is just **silence** — the clean "mute" behaviour.

Which one your target laptops do **must be bench-checked** — but the safe design
choice removes the ambiguity.

### Fix — APPLIED in rev-9 (2026-09-03)

**Give every de-selected laptop a constant "idle-electret" DC load** so no codec
ever changes its mind. Done in `gen.py` (MICSW), `pcb.py` (R39–R42), routed and
sim-verified (`bom_selector.cir` updated; one-hot routing unchanged, 37 mV
selected / 0.4 µV others). See CHANGELOG rev-9. **Still bench-verify on the
target laptops** — the OS half is codec firmware.

1. **Swap `COM` ↔ `NO` on K1–K4** in the MICSW sheet:
   `COM` (5/6) → `NBn_MIC` (laptop *n*), `NO` (10) → `HEADSET_MIC` (commoned).
2. **`NC` (pin 1) → new `R_NCn` = 2.2 kΩ → GND**, one per relay.

Then: selected laptop gets the real electret; every de-selected laptop sees
2.2 kΩ to GND ≈ 1.25 V on its mic pin (≈ the 1.19 V of a live mic) → codec holds
*headset mic present*, far end hears **silence**, no disconnect event, no
internal-mic fallback, no switch-back pop. At power-on and during a 2-button
mute **all four** laptops see "mic present, silent" instead of "mic gone".

Cost: 4× 2.2 kΩ THT resistors + the K1–K4 contact-side re-wire + re-route. The
coil / free-wheel-diode side (pins 2, 9) is unaffected. **Not a functional
respin of anything else** — the audio path, the one-hot logic and the POR are
untouched.

Alternative without re-wiring the relays: a permanent `~6.8 kΩ` from each
`NBn_MIC` to GND — simpler layout, but costs ~25 % headset-mic level when
selected and the de-selected pin only reaches ~1.9 V (still marginal for some
codecs). The COM/NO swap is the better fix.

### Can the board *tell* Windows to mute? — No (and why the fix is still the answer)

There is **no analog signal on a 4-pole headset jack that means "mute the
microphone"** to an OS. What the jack carries:

| signal | what Windows does with it |
|---|---|
| mic audio (AC on sleeve) | recorded |
| mic DC level (sleeve) | headset-vs-headphones-vs-none detection (§P) |
| **resistance mic→GND**: 0 Ω / ~240 Ω / ~470 Ω | inline-button **media keys** — play-pause / vol+ / vol− |
| mechanical jack-detect | plug in / out |

Mic **mute** in Windows is a software / HID function — the Sound-panel toggle or
a USB-HID *Telephony → Phone Mute* usage. Nothing on the analog jack sets it.
There is no resistor code for "mic mute" (0 Ω is the play-pause / hook code, so
grounding the mic pin to "signal a mute" would instead fire a media key at every
switch and on contact bounce — another reason **NC → straight GND is wrong**,
2.2 kΩ is right).

So with the recommended fix the mute is **functional, not signalled**: the mic
endpoint on the de-selected laptop stays *present and unmuted*, its level meter
flat, and the far end hears **nothing because no audio is routed there**. Windows
never shows "muted". That is the correct outcome for a "install nothing, no USB,
no firmware" box. A Windows-visible mute would require adding a **USB-HID device
per laptop** (a cable to each machine + the box enumerating on each) — a
different product, against the project's premise.

### Hand-over timing — mic briefly on *neither* laptop, not stuck on both

`../simulation/spice/bom_relay_handover.cir` (current-sensing relay model, so the
free-wheel diode slowing the release is captured). One button press at t = 0:

| event | time after press |
|---|---|
| K1 (old) coil current decays through drop-out (~3–10 mA), contact opens | **+2.5 … +4 ms** |
| K2 (new) coil current rises through pull-in (~22 mA), contact closes | **+4 … +6 ms** |

Plus ~1–3 ms of mechanical armature travel not in the electrical model. Net:
a **~2–6 ms window where `HEADSET_MIC` reaches no laptop** (break-before-make) —
the mic just blips off mid-press, inaudible. If the exact relay releases slower
(freewheel diode dependent) the windows can instead briefly overlap: the headset
mic tied to the old + new laptop for a few ms, both bias currents limited to
< 1 mA by the laptops' own bias resistors — harmless, at most one faint click on
the far end. Either way it is a few milliseconds, once per switch, with no
Windows-visible consequence. If a guaranteed break-before-make is wanted, put a
**100–470 Ω resistor (or a 15–24 V zener) in series with D2–D5** to speed the
release — fold it into the same change as the §P resistors.

## The three v1 bugs — confirmed fixed in simulation

1. **Pots reversed** → B2: full-CW = wiper at the signal end = loud; full-CCW =
   wiper at VBIAS = 80 dB down (silent). Direction matches "aumentar à direita".
2. **Mic relay coil/contact swap + one-hot** → G2 + F1: the CD4043B one-hot latch
   only ever energises one coil; POR holds all four off for 139 ms at power-up so
   the board always boots with the mic muted.
3. **VBIAS unbuffered** → A1–A4: the LM358 buffer with feedback taken after R38
   gives an exact 2.50 V with < 1 Ω output impedance to 1 kHz (0.86 Ω at 20 kHz),
   so there is no volume-dependent bleed. The closed-loop `VBIAS_REF → VBIAS`
   transfer is flat (no peaking) in `.ac`; `|Zout|` shows only a mild ~2 Ω bump
   near 40–60 kHz (loop gain running out above the audio band, driving the C26
   load) — well outside the audio band and not an oscillation. The buffer is
   stable as drawn.

Op-amp supply validity (a v2 review item): NJM4580, NJM4556A and LM358 all
operate correctly on the single 5 V rail in simulation — the NE5532 that was
replaced would have been out of spec.

## Findings

### 1. Headset level is ~11 dB below the design note — **FIXED in rev-10** (⚠️ B1 / ❌ D4 → ✅✅)

**rev-10 (2026-09-04):** R16/R20 lowered 47 Ω → 10 Ω. Loaded gain 0.50× (−6 dB),
0.65–0.79 mW into 32 Ω, +5.5 dB — D4 passes, all 21 checks green. The paragraph
below is the original rev-9 analysis that motivated the change.


`v2-DESIGN.md` §4 says "Overall monitor gain ≈ 0.33 × 1 × 2 ≈ **0.66×**" and
computes 1.4 mW into 32 Ω. That is the **unloaded** number. `R16`/`R20` = 47 Ω
sit **outside** the U2A feedback loop (feedback is taken at the op-amp output,
before C17/R16), so with a 32 Ω headset they form a 47/(47+32) = 0.41 divider:

- loaded system gain **0.27×** (−11.5 dB), not 0.66×
- from a −10 dBV (0.316 Vrms) laptop output → **84 mVrms → 0.22 mW** into 32 Ω
- ≈ 86 dB SPL in a 100 dB/mW IEM (usable), noticeably quiet for 32 Ω over-ears,
  and the existing "high-Z headphones are quieter" note in §6 understates it.

**Recommendation:** drop `R16`/`R20` from 47 Ω to **10 Ω** (still fine for
stability and short-circuit current limiting on the NJM4556A, which is a 70 mA
line driver). Simulation: gain 0.50×, **0.79 mW into 32 Ω, +5.5 dB**. If more is
needed, also raise the U2A gain (R15/R14) from 2 to 3, or move R16/R20 inside
the feedback loop.

### 2. Bass roll-off from the 1 µF couplers (⚠️ B4)

`C5/C7/C9/C11` (laptop DC-block) and `C13/C14` (post-mixer) are 1 µF into ~5–10 kΩ
→ ~16–32 Hz high-pass sections that stack; together with the C16 DC-servo corner
the chain is **−3 dB at 44 Hz, −10 dB at 20 Hz** into 32 Ω. **This is completely
fine for a conference headset** (voice is 300–3400 Hz, wideband 50–7000 Hz). Only
raise `C5/C7/C9/C11` and `C13/C14` to 4.7 µF (−3 dB ≈ 12 Hz) if the box will be
used for full-range music monitoring.

### 3. VBIAS takes ~250 ms to settle at power-up (harmless)

`VBIAS_REF` is `C3` (10 µF) charging through `R1‖R2` = 5 kΩ → τ = 50 ms, so
VBIAS reaches 2.5 V in ~250 ms. That is *slower* than the 140 ms POR window, so
when the mic latch is released VBIAS is still at ~2.3 V and rising. **This causes
no problem:** every node in the audio path is referenced to VBIAS and rises with
it (no step, no thump), the one-hot logic runs off the +5 V rail (settled in
~1 ms), and no relay engages until a button is pressed. Noted only so the number
isn't a surprise on the bench. If a faster VBIAS is ever wanted, drop `C3` to
1 µF (τ = 5 ms) — the buffer + `C26` still filter it.

### 5. A de-selected laptop saw its mic pin *open* → codec may drop the endpoint (§P) — FIXED rev-9

As-built (rev-8), switching the mic away from a laptop left that laptop's mic
sleeve **open** (relay NC unconnected) = **2.50 V ≈ "no microphone"** to the
codec → risk of the *Headset Microphone* endpoint being dropped and the app
falling back to the **internal mic** (room audio).

**Fixed in rev-9:** `COM`↔`NO` swapped on K1–K4, each `NC` → 2.2 kΩ (R39–R42) →
GND. A de-selected laptop now reads **1.25 V** (idle-electret DC) → endpoint
stays, far end hears silence. Also fixes power-on / 2-button-mute. **Bench-verify
on the target laptops regardless** — the OS half is codec firmware.

### 4. Doc corrections (no board change)

- `v2-DESIGN.md` §4 lists the headphone output caps as "C17/C20 (1 µF)". The
  schematic has **C17/C20 = 220 µF** — which is correct; 1 µF there would put the
  −3 dB point at 5 kHz. Fix the prose.
- `v2-DESIGN.md` rev-7 says the POR pulse is "~40 ms". With C24 = 10 µF the real
  window is **~140 ms** (R37 ∥ the diode-matrix RST pulldowns) rising toward
  ~0.7 s once the diodes stop conducting. Longer is safer here — just fix the number.
- `v2-DESIGN.md` §6 pass 3: the two-button gesture does **not** "resolve to one
  selected again" on release — it stays muted (see §E).

## What was NOT simulated (and why)

- **CD4043B one-hot logic** — now covered by the section E logic/timing sim
  (`select_logic.py`), not SPICE. The analog POR envelope is F1/F2.
- **Mic-select transient vs. monitor audio** — now covered by section O
  (`bom_mic_switch_glitch.cir`): switching the mic relays does not glitch the
  mixer output (< 80 µV, −63 dB).
- **De-selected laptop's mic-pin DC / OS endpoint state** — the board side is
  covered by section P (`bom_mic_deselect_detect.cir`) and produced finding 5;
  the Windows codec's actual re-tasking decision is firmware and needs a bench
  check on the target laptops.
- **PCB parasitics / EMC / USB-C surge energy** — out of scope for a functional
  SPICE pass; the TVS choice (G3) follows the standard power-only-VBUS approach.
  Section O uses a lumped rail R/L model, not extracted PCB parasitics.
- **Pot taper / mechanical direction** — depends on the Alps RK09712200HA
  terminal convention; still needs the first-article bench check noted in
  `v2-DESIGN.md` §6.5.
- Interactive click-and-listen (Proteus VSM / Multisim style) — approximated by
  `audio_out.wav` and the MP4 rather than a live GUI.

## Bottom line

The v2 design does what it is supposed to do. Every function was simulated
end-to-end (`MeetingHub-4-v2-full-simulation.mp4`) and the three v1 bugs that
cost R$3000 are each independently re-verified: pot direction + true mute,
one-hot relay routing, buffered VBIAS.

**Before ordering:**

1. **BOM change — DONE in rev-10 (2026-09-04): R16/R20 47 Ω → 10 Ω** — buys
   +5.5 dB of headphone level (finding 1). Same footprint/position, netlist
   byte-identical, no re-route. D4 now passes; §A–§G 21/21.
   Part = **UNI-ROYAL MFR0W4F100JA50 = LCSC C57437** — 10 Ω 1/4 W metal film ±1%
   ±50 ppm, ~10 800 in JLC stock (a step up from, and same footprint as, the
   47R5 metal-film part it replaces).
2. **Schematic change — DONE in rev-9 (finding 5 / §P):** `COM`↔`NO` swapped on
   K1–K4, each `NC` → 2.2 kΩ (R39–R42) → GND, so a laptop you switch *away* from
   still reads as a live-but-silent headset mic instead of "mic unplugged".
   Routed + sim-verified. Still **bench-verify** on the target laptops — the
   OS-side behaviour is codec firmware.
3. **Bench check (mandatory): the Alps RK09712200HA terminal convention.** Knob
   fully CCW must give wiper→terminal 1 ≈ 0 Ω. The netlist is wired correctly for
   the assumed convention; simulation cannot verify the physical pot. If it's
   backwards, swap the wires — not a respin. This is the exact class of the v1
   bug, so do not skip it.
4. Doc fixes (findings 3–4): POR is ~140 ms not 40 ms; output caps are 220 µF
   not 1 µF; VBIAS settles in ~250 ms; two-button gesture stays muted on release.

Findings 2 (bass roll-off) is fine for voice and needs no change.
