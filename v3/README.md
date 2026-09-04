# MeetingHub-4 v3 — Mic Selector

A stripped-down spin of MeetingHub-4: **only the microphone selector**. One
headset microphone is routed to **exactly one** of four notebooks, KVM-style,
with four buttons. There is **no audio/monitor path** — you split each notebook
with a TRRS Y-cable and monitor all four on an external mixer.

|  |  |
|---|---|
| **Status** | Schematic complete, PCB routed (4 layers, 0 unrouted), DRC clean (0 errors, 1 cosmetic silk item). **Simulated with the real parts in ngspice: 25 / 25**, plus a 22 / 22 analytic cross-check (`docs/v3-simulation-validation.md`). **Not fabricated.** Open in KiCad, run native ERC/DRC before ordering. |
| **PCB** | **4 layers** (F/B signal, In1 = GND plane, In2 = +5V plane), ~**106 × 86 mm** (≈ ⅓ the area of v2), R3 corners, 4× M3. |
| **Supply** | USB-C, 5 V only (PTC fuse + TVS, CC pull-downs so any USB-C source turns VBUS on). |
| **BOM** | ~73 parts, **100 % through-hole**, hand-solderable. Vertical-mount resistors/diodes keep it small. |
| **Fab files** | `hardware/Gerbers/` (order **4-layer**, 1.6 mm) + `…-CPL.csv`. |

## How it works

- **Route:** the headset mic (`J6` tip) goes to the **NO** contact of all four
  signal relays `K1–K4`, commoned. Each relay's **COM** goes to one notebook's
  mic jack (`J2–J5`); its **NC** goes through a 2.2 kΩ resistor (`R20–R23`) to
  ground. Energise `Kn` → notebook *n* gets the headset mic. De-energise it →
  that notebook's mic pin sees 2.2 kΩ to ground (~1.1 V), which a laptop codec
  reads as *"headset mic present, silent"* — **not** an open circuit, which many
  codecs read as *"mic unplugged"* and then fall back to the notebook's internal
  mic (transmitting room audio). See `docs/v3-simulation-validation.md` MIC7.
- **Select:** four momentary buttons `SW1–SW4`. Press NB2 → `K2` latches on and
  any other relay drops (exclusive / one-hot). The latch is a **CD4043B** quad
  NOR R/S latch (`U1`) + a 16-diode steering matrix + `2N7000` coil drivers —
  the exact logic proven in v2's simulation.
- **Mute:** there is no mute button. **At power-on nothing is latched → the mic
  reaches no notebook → muted.** A ~0.1 s power-on-reset pulse (`C5`/`R11` +
  `D22–D25`) guarantees this even on a slow VBUS ramp. During a call, mute in
  the meeting app, or hold any two select buttons. In every muted state each
  notebook still sees the 2.2 kΩ NC bias, so none of them report the mic gone.

## The rest of your setup (not on this board)

```
notebook 3.5 mm combo jack ──[ TRRS Y-splitter ]──┬── headphone plug ──► external mixer
                                                  └── mic plug ────────► MeetingHub-4 v3  Jn
headset ──┬── headphones ──► external mixer
          └── mic plug ─────► MeetingHub-4 v3  J6
```

All five jacks (`J2–J6`) are **P2 (3.5 mm) 3-conductor through-hole** — HX
PJ-320A-3P DIP, **LCSC C17701689**. The footprint pins are numbered **2 / 3 / 4**
per the datasheet: **pin 3 = tip → mic, pins 2 & 4 = ring/sleeve → ground**
(a CTIA Y-splitter's mic plug puts the mic on the tip and grounds the rest;
grounding both 2 and 4 also means it doesn't matter which is ring and which is
sleeve). On bring-up, meter continuity from a plug's tip to **pin 3** to confirm.
Power the board from a **separate** USB charger or power bank (not one of the
four notebooks) so the notebooks' audio grounds don't form a loop through the box.

## Reading order

1. [`docs/v3-DESIGN.md`](docs/v3-DESIGN.md) — what was kept from v2, what was
   dropped, the one-hot logic, and the circuit review.
2. [`docs/v3-simulation-validation.md`](docs/v3-simulation-validation.md) — the
   ngspice component-level simulation (25 checks) + the analytic cross-check.
3. [`CLAUDE.md`](CLAUDE.md) — repo layout and how the files are generated.
4. [`CHANGELOG.md`](CHANGELOG.md).
5. The KiCad project in [`hardware/KiCad/MeetingHub-4-v3/`](hardware/KiCad/MeetingHub-4-v3/).

## License

Inherits the parent project's commercial license with usage royalty — see
`../LICENSE.md`. Not open-source hardware.
