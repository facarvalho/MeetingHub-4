# DR-003 - Schematic Implementation Review

Version: 1.0
Status: Review


# 1. Objective

Document what was actually implemented and validated during the construction
of the MeetingHub-4 KiCad schematic (SCH-001 to SCH-009), and make explicit
what this validation covers and what it does **not** cover, to guide the
full technical review before manufacturing.


# 2. What was built

The project was organized into five hierarchical sheets in
`hardware/KiCad/MeetingHub-4/`:

## POWER (POWER.kicad_sch)

- Power supply USB-C connector (J1)
- Protection fuse (F1, 500mA)
- Protection TVS diode (D1)
- +5V_AUDIO power supply filtering (C1/C2)
- Test point (TP1)

**Note:** this sheet **does not have a voltage regulator**. The
`+5V_AUDIO` power supply corresponds to the USB-C VBUS, protected and
filtered, without active regulation.

## TRRS_INPUTS (TRRS.kicad_sch)

- Four TRRS connectors for the laptops (J2-J5)
- Distribution of the audio signals coming from the laptops

## AUDIO_MIXER (MIXER.kicad_sch)

- Individual channel adjustment potentiometers (RV1-RV4) + master (RV5)
- **Active** stereo mixer based on an NE5532 operational amplifier (U1)
- Summing feedback network
- Generation of the **VBIAS** reference by a resistive divider (10 kΩ / 10 kΩ)
  with a decoupling capacitor

**Note:** VBIAS is used as the half-supply reference for the operational
amplifiers (U1 and U2). It does **not** supply bias to the microphones,
which continue to use the power supplied by the laptop, in accordance with
the transparency requirements of SCH-004/SCH-007.

## HEADPHONE_AMP (HPAMP.kicad_sch)

- Headphone amplifier based on the NJM4556A (U2)
- Input/output coupling via capacitor
- Power supply decoupling
- Operator headset TRRS connector (J6)

## MIC_SWITCHING (MICSW.kicad_sch)

- Mute switch (SW1)
- Four Omron G5V-1 relays (K1-K4)
- Flyback diodes (D2-D5)
- Individual selection of the four microphones
- JST-XH connectors for external buttons (SW1-SW5)

In the end, the project contains **66 components**, all with footprints
assigned (except global power symbols). BOM generated at
`hardware/BOM/BOM-MeetingHub-4.csv` and schematic PDF at
`hardware/Schematics/MeetingHub-4-Schematic.pdf`.


# 3. Block diagrams

A single mixed-topology diagram tends to confuse power supply with signal.
For this reason, three separate diagrams are used:

## 3.1 Power supply distribution

```text
USB-C (J1)
   │
 POWER
   │ +5V_AUDIO
   ├──► AUDIO_MIXER    (U1 NE5532)
   ├──► HEADPHONE_AMP  (U2 NJM4556A)
   └──► MIC_SWITCHING  (K1-K4 relay coils, via SW2-SW5)
```

## 3.2 Audio path (Laptop -> Headset)

```text
TRRS_INPUTS                 AUDIO_MIXER                HEADPHONE_AMP
J2 NB1_L/R ──┐
J3 NB2_L/R ──┤   individual        active sum      MIX_L/R    gain      J6
J4 NB3_L/R ──┼──► volume ──────► (U1) ──────────────────────► (U2) ──► Headset
J5 NB4_L/R ──┘   (RV1-RV4)                                             (L/R)
```

## 3.3 Microphone path (Headset -> Selected laptop)

```text
Headset (J6, sleeve)
   │ HEADSET_MIC
 MIC_SWITCHING (SW1 mute + K1-K4 selection)
   │
   ├──► NB1_MIC ──► J2 (TRRS_INPUTS)
   ├──► NB2_MIC ──► J3
   ├──► NB3_MIC ──► J4
   └──► NB4_MIC ──► J5      (only one relay should be energized at a time)
```


# 4. What was validated, and how

- **Structural connectivity**: `kicad-cli sch export netlist` run
  repeatedly (multiple times, deterministically) on the complete project,
  with no error. The named nets (`+5V_AUDIO`, `VBIAS`, `NB1-4_L/R/MIC`,
  `MIX_L/R`, `HEADSET_MIC`, `GND`) appear correctly in the exported
  netlist, connecting the 5 sheets to each other as expected.
- **Visual rendering**: `kicad-cli sch export pdf` generated and inspected
  page by page (all 6 pages), confirming that the components appear on
  the correct sheets with the expected labels.
- **Footprints**: a post-processing script verified that 100% of the
  components (except GND symbols, which do not use a footprint) have a
  non-empty footprint assigned.

**This is equivalent to a structural integrity check of the file, not an
ERC.** None of these checks replace the full KiCad ERC (pin type
conflicts, floating input, unpowered power pin, etc.), which only runs
through the graphical interface in this version of `kicad-cli` (7.0.11 -
the `sch erc` and `pcb drc` subcommands only exist starting from KiCad 8).


# 5. Important limitation of the review

The validation above was performed **on the complete project** (all 5
sheets + root), not on isolated fragments. Even so, the review was
predominantly automated (parsing/export via `kicad-cli`) and visual
(inspection of the rendered PDF). It does not replace:

- a full ERC in the KiCad graphical interface;
- manual review, sheet by sheet, of each junction/label against the
  electrical intent (especially the microphone line and grounding);
- review of gain, impedance, and noise values by someone who can
  simulate or physically bench-test the circuit.


# 6. Technical decisions made during implementation

Points that require human confirmation before routing the PCB:

- **VBIAS**: generated by a passive resistive divider (10k/10k + 10uF),
  without an active buffer. This works because the op-amp input
  impedance is high, but it is the simplest possible choice - if
  audible background noise is present in the prototype, this is the
  first point to review (replace with a dedicated active buffer).
- **Gains**: summing mixer with unity gain per source (Rf = Rin = 10k);
  headphone stage with gain of ~2x (Rf/Rg = 1k/1k). These have not been
  validated against actual laptop output levels or against the
  sensitivity of 16-64 ohm headphones - reasonable starting values, not
  calibrated.
- **Microphone selection**: implemented with manual SPST switches
  (SW2-SW5) feeding each relay coil independently. There is no
  electrical interlock - it is the end user's responsibility to
  activate only one selection at a time, as already specified in
  SCH-007.
- **kicad-cli bug workaround**: symbols with `(extends "Base")` (e.g.
  NE5532/NJM4556A derived from LM2904, TVS derived from ZPYxx) and
  cached symbol names without the library prefix caused a deterministic
  segfault in `kicad-cli sch export netlist` (KiCad 7.0.11). The symbols
  were embedded using the base symbol directly with the Value field
  overridden, and the cached names were prefixed (`Device:R`,
  `Diode:ZPYxx`, etc.). This is only a file/tool quirk - it does not
  affect the electrical design, but it is recorded here in case another
  symbol with `extends` is added in the future.


# 7. Pending items before manufacturing

Confirmed in this review, still open:

- Full ERC via KiCad (GUI).
- PCB layout (placement of jacks/potentiometers/relays, audio vs. power
  supply separation, ground plane) and DRC from the chosen manufacturer.
- Mechanical review of pinout/footprint against the datasheets of the
  parts actually purchased: USB-C, TRRS jacks (PJ320D), G5V-1, dual
  potentiometers (RK097).
- Dimensional check against the enclosure.
- Generation of Gerbers, drill files (Excellon), final BOM, and Pick &
  Place (if automated assembly is used).
- Full manual technical review (power supply, analog grounding,
  audio levels/impedance, relays, USB-C, op-amps, mixer, microphone
  selection, possible ground loops) before generating the manufacturing
  files.


# 8. Status

Schematic structurally valid and ready for the PCB layout stage.
Not approved for manufacturing - depends on the pending items in section 7.
