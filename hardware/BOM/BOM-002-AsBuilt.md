# BOM-002 - As-Built Bill of Materials

Version: 1.0
Status: Final — matches the final 4-layer PCB (complete and validated layout)

Supersedes: BOM-001 (conceptual list, prior to the real schematic)


# 1. Purpose

Record the actual bill of materials, extracted directly from the KiCad
schematic (5 sheets: POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP,
MIC_SWITCHING), with reference, value, and footprint for each component,
plus the items added directly on the PCB during layout (mounting holes
and GND test point).

Raw file: [BOM-MeetingHub-4.csv](BOM-MeetingHub-4.csv)


# 2. Summary

- 75 distinct physical items (36 rows after grouping by value+footprint):
  70 schematic components + TP2 (GND test point) + MH1-4
  (M3 mounting holes) - these last 5 have no schematic symbol
  since they are mechanical-only, added directly on the PCB (see PCB-001
  Phases 3.3.3 and 8).
- 100% of components have an assigned footprint (except GND symbols)
- All active and passive components are THT, favoring manual assembly


# 3. Footprint selection notes

- **J1** (USB-C): `Connector_USB:USB_C_Receptacle_GCT_USB4085` - common
  part, used in various open-hardware projects.
- **J2-J6** (3.5mm TRRS, 4-pole): `Connector_Audio:Jack_3.5mm_PJ320D_Horizontal`
  - metallic panel jack. Mechanically confirm against the actual purchased
  part before routing the PCB.
- **K1-K4** (relay): `Relay_THT:Relay_SPDT_Omron_G5V-1` - official
  footprint for the real G5V-1.
- **RV1-RV5** (dual potentiometer): `Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal`
  - check alignment against the front panel holes.
- **SW1-SW5** (MUTE + laptop selection): `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`
  - switches are located on the panel, wired to the board (not PCB-mounted
  buttons).
- **U1, U2** (NE5532 / NJM4556A): `Package_DIP:DIP-8_W7.62mm` - DIP-8 to
  ease manual assembly of the prototype (use a socket). Migrate to SOIC-8
  for series production, if it becomes necessary to reduce board area.
- **D1** (TVS protection): footprint `Diode_THT:D_DO-41_SOD81`; the actual
  purchased value is PTVS5V0Z1USK (the symbol used in the library is the
  generic ZPYxx, without altering pinout/geometry).
- **TP1, TP2** (test points): `TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm`
  - TP1 on the +5V_AUDIO net (POWER sheet), TP2 on the GND net, near U1.
    TP2 is a mechanical-only footprint, added directly on the PCB (no
    schematic symbol) - see PCB-001 Phase 8 for the history of why it
    exists (generic GND test point, useful for measurement).
- **MH1-MH4** (enclosure mounting holes): `MountingHole:MountingHole_3.2mm_M3`
  - unplated 3.2mm hole for M3 screw, one at each corner of the board,
    6mm margin from the edge. Mechanical-only, no schematic symbol - see
    PCB-001 Phase 3.3.3 for the exact positions.


# 4. Manufacturing status

- ✅ Complete PCB layout (placement of jacks, potentiometers,
  relays; audio/power separation by enclosure face - see PCB-001
  Phases 3-5).
- ✅ Real DRC (via KiCad, confirmed 23/07/2026): 0 unconnected pads,
  0 errors. Only 5 remaining warnings are cosmetic and accepted
  (library discrepancy for potentiometers RV1-RV5 - see PCB-001
  Phase 8).
- ✅ Board migrated to 4 layers (dedicated GND and +5V_AUDIO planes on
  the inner layers - see PCB-001 Phase 6).
- ✅ Gerbers, drill file (Excellon), and placement files exported and
  validated via `kicad-cli` (no export errors).
- ✅ ERC run (via KiCad, by the user), in two rounds, and all
  real errors were fixed - see PCB-001 Phase 11 for the detail of
  each one:
  - **TP1 was never actually connected to +5V_AUDIO** (neither in the
    schematic nor on the PCB) - the pin was visually placed over an
    existing wire without an electrical junction. Fixed in both files.
  - **TP2 also wasn't connected to GND on the PCB** (mechanical-only
    footprint, added without a net). Fixed - now actually on the GND net.
  - `power_pin_not_driven` on U1 (V+/V- pins): fixed with two
    `power:PWR_FLAG` symbols in POWER.kicad_sch. On the first attempt the
    +5V_AUDIO flag was connected on the wrong side of fuse F1 (it still
    resolved the GND side, but not V+) - fixed on the second round, by
    moving the flag to the same node that already feeds TP1 and the
    +5V_AUDIO global label.
  - `lib_symbol_issues` on J2-J6 (AudioJack4): the symbol was referenced
    as `Connector:AudioJack4`, a library that no longer exists at that
    location in current KiCad (the symbol was moved to `Connector_Audio`).
    Fixed the `lib_id` to `Connector_Audio:AudioJack4` in TRRS.kicad_sch
    (J2-J5) and HPAMP.kicad_sch (J6) - geometry and pins checked byte by
    byte against the system library before the change.
  - `pin_not_connected` (error, not warning) on the 9 data/CC/SBU/shield
    pins of J1 (USB-C: D+, D-, CC1, CC2, SBU1, SBU2, SHIELD) and on pin 10
    of relays K1-K4 (duplicate pin of the reverse contact of the G5V-1,
    not used in this SPDT topology): both cases are intentional (J1 is
    only used as a power input - see DR-002/DR-003), but were listed as
    an **error** regardless. Fixed by adding explicit "no connect"
    markers on each pin, the standard KiCad way of saying "I know this
    pin is intentionally floating".
  - `endpoint_off_grid` (233 warnings, practically every pin/wire in the
    schematic): root cause identified - the entire schematic was drawn
    at round positions in millimeters, which are not multiples of the
    1.27mm (50 mil) grid that ERC uses for this check. Fixed via a script
    that realigns every symbol, wire, and junction across the 5 sheets to
    the nearest multiple of 1.27mm, preserving the electrical topology
    (two points that already coincided still coincide, because they use
    the same deterministic rounding function). **Validated with
    `kicad-cli sch export netlist` before/after - the project's 72 nets
    match node by node, none changed.** A single case needed manual
    adjustment: the realignment brought D1 too close to the D+ pin of J1
    (which sits next to it, unused), almost touching the two - fixed by
    moving D1 one extra grid step away.
  - **Confirmed by the user via a real KiCad report (23/07/2026,
    16:27): 0 errors, 0 warnings.** ERC 100% clean.

**Real pending item, outside the scope of this BOM**: final mechanical
verification of the above footprints (J1-J6, K1-K4, RV1-RV5) against the
datasheets of the parts actually purchased, at the time of purchase/receipt -
recommended even with the layout validated, since small variations between
suppliers of the same component may exist.
