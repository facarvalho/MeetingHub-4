# MeetingHub-4 v2

Analog audio hub for 4 laptops — monitor all four at once, talk on one — with a
single TRRS headset. No drivers, no firmware, 100 % analog.

**v2 = a clean respin of the design:** 2-layer PCB, every part through-hole and
hand-solderable, the mic selector's exclusive "one-hot" logic now on the board
itself, no mute button, and all three bugs from the first fabricated batch fixed.

| | |
|---|---|
| **Status** | Schematic complete, PCB **fully auto-routed** (2 layers), DRC clean apart from known cosmetic items. Not yet fabricated. Open in KiCad to tidy silkscreen and run native DRC before ordering. |
| **PCB** | 2 layers, ~328 × 128 mm, GND pour both sides. |
| **Supply** | USB-C, 5 V only (no regulator, no boost). |
| **BOM** | 118 parts, 100 % THT — [`hardware/BOM/BOM-MeetingHub-4-v2.csv`](hardware/BOM/BOM-MeetingHub-4-v2.csv) |
| **Fab files** | [`hardware/Gerbers/MeetingHub-4-v2-Gerbers.zip`](hardware/Gerbers/) — order as **2-layer**, 1.6 mm, HASL is fine. |

## How it works

- **Monitor:** each laptop plugs into J2–J5 (TRRS). Its L/R audio goes through a
  DC-block, a per-laptop volume pot (RV1–RV2), a 4-input stereo summing mixer
  (U1 NJM4580), a master volume (RV5), a headphone amp (U2 NJM4556A), out to the
  headset J6. All four are always summed.
- **Talk:** the headset mic (J6 sleeve) is routed by one of four signal relays
  (K1–K4) to exactly one laptop's mic pin.
- **Selecting:** four momentary buttons (SW2–SW5). Press NB2 → laptop 2's relay
  latches on and any other releases (KVM-style). The latch is a CD4043B
  (U4) + diode matrix + 4× 2N7000 coil drivers (the SELECT_LOGIC sheet).
- **Mute:** there is no mute button. **At power-on nothing is latched → the mic
  reaches no laptop → muted.** During a call, mute in the meeting app, or hold
  any two select buttons.
- **Volume direction:** clockwise = louder on every pot (verified against the
  Alps terminal convention — see the design doc).

## Reading order

1. [`docs/v2-DESIGN.md`](docs/v2-DESIGN.md) — what changed from v1, the
   one-hot logic, and the 3-pass circuit review (4 laptops connected).
2. [`CLAUDE.md`](CLAUDE.md) — repo layout and how the files were generated.
3. [`CHANGELOG.md`](CHANGELOG.md).
4. The KiCad project in [`hardware/KiCad/MeetingHub-4-v2/`](hardware/KiCad/MeetingHub-4-v2/).

The v1/v2 design and its hand-rework guides are in the parent folder and are
**not** part of v2.

## License

Inherits the parent project's commercial license with usage royalty — see
`../LICENSE.md`. Not open-source hardware.
