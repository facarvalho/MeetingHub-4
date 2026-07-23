# MeetingHub-4

Analog audio hub for 4 laptops, with a single TRRS headset and microphone selection — no drivers, no firmware, no software.

| | |
|---|---|
| **Status** | Hardware complete — schematic frozen v1.0, PCB routed and validated, ready for manufacturing |
| **Version** | v1.0 |
| **PCB layers** | 4 (F.Cu / In1.Cu GND / In2.Cu +5V_AUDIO / B.Cu) |
| **License** | Commercial, with usage royalty — see [LICENSE.md](LICENSE.md) |

## What it is

MeetingHub-4 connects up to 4 laptops simultaneously via a 3.5mm TRRS (P2) input, allowing the user to:

- **monitor audio from all four sources at the same time**, with individual volume per laptop and an overall volume;
- **speak on only one laptop at a time**, selecting the headset microphone with a physical switch;
- **use a single TRRS CTIA headset** (the same as a mobile phone's), with no adapter;
- **work without installing anything** — each laptop sees the equipment as a regular headset connected directly to its P2 jack.

It is a **100% analog** project: no Bluetooth, no USB audio, no firmware, no digital processing. See [ERS-001](docs/ERS/ERS-001.md) for the complete requirements specification.

## Repository structure

```
docs/
  ERS/                    Requirements specification (what the product needs to do)
  Architecture/           Hardware architecture and schematic design (HAD, SCH-001 to SCH-009, PCB-001)
  DesignReviews/          Design reviews (DR-001 to DR-003)
  Legal/                  International patent registration guide

hardware/
  KiCad/MeetingHub-4/     Complete KiCad project (schematic + PCB, source of truth)
  Schematics/             Exported schematic PDF
  BOM/                    Bill of materials (conceptual and as-built)
  PCB/                    Exported netlist
  Gerbers/                Gerbers + drill files ready for manufacturing (zip ready for upload)

mechanical/                3D model of the enclosure (OpenSCAD, v0.1 draft)

production/                Guides on how to order manufacturing (PCB, enclosure)

LICENSE.md                Commercial usage license (with royalty)
CHANGELOG.md              Project milestone history
```

## Where to start reading

1. **[ERS-001](docs/ERS/ERS-001.md)** — what the equipment needs to do, and why.
2. **[HAD-001](docs/Architecture/HAD-001.md)** — how the hardware architecture meets the requirements.
3. **SCH-001 to SCH-009** (in `docs/Architecture/`) — electrical design decisions, block by block (power supply, TRRS, mixer, headphone amplifier, microphone switching, grounding).
4. **[DR-001](docs/DesignReviews/DR-001-ArchitectureReview.md), [DR-002](docs/DesignReviews/DR-002-ElectricalArchitectureReview.md), [DR-003](docs/DesignReviews/DR-003-SchematicImplementationReview.md)** — critical design reviews before each subsequent stage.
5. **[PCB-001](docs/Architecture/PCB-001-LayoutGuide.md)** — complete PCB layout guide (phases 2 to 10), including every decision and fix applied through the final state.
6. **[BOM-002-AsBuilt](hardware/BOM/BOM-002-AsBuilt.md)** — actual bill of materials, extracted from the final design.
7. **[TEST-001](docs/Architecture/TEST-001-BringUpGuide.md)** — assembled board test guide, from visual inspection to full operation with the 4 laptops.
8. **[PCBWay-OrderGuide](production/PCBWay-OrderGuide.md)** — step-by-step guide to ordering board manufacturing from PCBWay.

## Hardware status

- Schematic: 5 sheets (POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP, MIC_SWITCHING), frozen as v1.0.
- PCB: 66 components, all THT, routed in 4 layers (dedicated GND and +5V_AUDIO planes on the inner layers — see Phase 6 of PCB-001 for the reasoning).
- Validation: 0 unconnected pads, 0 DRC errors. The only remaining warning is cosmetic and documented (library mismatch on potentiometers RV1-RV5 — see Phase 8 of PCB-001).
- Manufacturing files: generated and validated (clean `kicad-cli pcb export gerbers` run). **When ordering manufacturing, explicitly select a 4-layer board.**

## Licensing and intellectual property

This project is distributed under a **commercial license with usage royalty payment** — see [LICENSE.md](LICENSE.md) for the complete terms. It is not an open source hardware project; commercial use requires a paid license from the rights holder.

For anyone intending to seek patent protection before commercializing, see the **[International Patent Registration Guide](docs/Legal/PATENT-GUIDE.md)** — it includes an important warning about patentability that should be read before starting any filing.

**No document in this repository constitutes legal advice.** Both the license and the patent guide are starting points drafted for review by a qualified attorney/industrial property agent before any commercial use or actual filing.
