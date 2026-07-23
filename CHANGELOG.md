# Changelog

Milestone history of the MeetingHub-4 project, by phase. For the line-by-line history, see `git log`.

## v1.0 — Hardware complete (manufacturing-ready)

### Requirements and architecture definition
- Requirements specification (ERS-001) and hardware architecture document (HAD-001).
- Electrical block diagram (SCH-001) and schematic design plan (SCH-002).
- Detailed electrical design by block: power supply (SCH-003), TRRS interface (SCH-004), audio mixer (SCH-005), headphone amplifier (SCH-006), microphone switching (SCH-007), grounding and noise control (SCH-008), KiCad implementation plan (SCH-009).
- Architecture reviews (DR-001, DR-002) before schematic implementation.

### Schematic
- Complete schematic implemented across 5 sheets (POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP, MIC_SWITCHING) with footprints assigned.
- Implementation review (DR-003), with fidelity corrections against the original electrical design.
- Schematic frozen as v1.0 (netlist and PDF generated).

### PCB layout
- Complete layout guide (PCB-001), covering mechanical placement, zoning, ground plane, routing, DRC, and manufacturing preparation.
- Placement of all 66 components with real physical constraints (front/rear/top panels).
- Complete routing via Freerouting (autorouter), with manual trace-width adjustments for the power nets.
- Mounting holes for the enclosure.
- Ground plane, and later migration to a **4-layer board** with dedicated internal GND and +5V_AUDIO planes, eliminating a structural grounding connectivity problem that persisted across two rounds of 2-layer re-layout.
- Final validation: 0 unconnected pads, 0 DRC errors (confirmed via an actual DRC report), no silkscreen overlaps, 4-layer gerbers exported and validated.

### Documentation and licensing
- Professional reorganization of all project documentation.
- Commercial usage license with royalty ([LICENSE.md](LICENSE.md)).
- International patent registration guide ([docs/Legal/PATENT-GUIDE.md](docs/Legal/PATENT-GUIDE.md)).
