# Changelog

Milestone history of the MeetingHub-4 project, by phase. For the line-by-line history, see `git log`.

## v1.0 (post-freeze rework, 2026-08-06) — No enclosure, all direct-solder

Reversed the previous rework's enclosure decision: no MDF box, no
panel — the bare PCB is the final product, resting on 4 rubber feet.
See [BOM-003-SourcingLinks](hardware/BOM/BOM-003-SourcingLinks.md) §2
for the full history.

- **RV1-RV5 reverted to direct-solder** Alps RK097 potentiometers
  (were 6-pin JST-XH headers wired to an off-board panel pot).
- **SW1-SW5 became direct-solder switches** — SW1 a 12mm THT
  pushbutton (`SW_PUSH-12mm`), SW2-SW5 a real SPST slide switch (CW
  Industries GPTS203211B, LCSC C3314371). These were off-board via JST
  even in the original v1.0 design, so this is new work, not a revert.
- **Board size reverted to 265.1x160.1mm** (recovered from git history,
  pre-dating the size-reduction commit) to fit the RK097 bodies
  directly. The 3 THT→SMD footprint changes (C1/C4/C21, D1) from the
  previous rework were re-applied on top — that fix doesn't depend on
  enclosure/board-size decisions, still zero real THT stock for those 2
  parts at any supplier.
- Implemented via a `pcbnew` script (footprint swap matched net-by-net
  on pad number), 2 local placement/routing conflicts resolved (SW1
  shifted 3mm to clear a courtyard overlap with SW2; C4's GND via
  rerouted around 3 existing bus traces in the mixer grid). Re-verified
  3 times via `pcbnew.WriteDRCReport`, fresh board load each time: 0
  unconnected pads, 0 dangling tracks, 0 courtyard/clearance errors.
- Gerbers, drill, and component position file regenerated.
  `mechanical/` (MDF box plan, PDF, 3D-printed case draft) is now
  obsolete, kept in the repo for history.

## v1.0 (post-freeze rework, 2026-08-05) — Assembly-ready

Driven by preparing the real JLCPCB/PCBWay assembly order — see
[BOM-003-SourcingLinks](hardware/BOM/BOM-003-SourcingLinks.md) for full
detail and sourcing links per component.

- **Board resized**: 265.1x160.1mm → 160.1x108.96mm, rounded corners.
- **RV1-RV5 moved off-board**: converted from direct-solder Alps RK097
  potentiometers to 6-pin JST-XH headers (RK097 body was the single
  largest space consumer on the old layout, ~150mm of board width for
  5 units). RV5 uses a horizontal-mount header variant and moved to the
  front row, next to SW1.
- **3 footprints changed THT → SMD**: C1/C4/C21 (100nF ceramic) and D1
  (TVS diode) — no THT stock exists for either at any supplier
  (confirmed by live catalog search, not just a JLCPCB gap). Implemented
  via a `pcbnew` script: footprint swapped, connectivity to the inner
  GND/+5V_AUDIO planes restored with added vias (THT holes provided this
  for free; SMD pads don't), zones refilled, re-verified 0 unconnected
  pads / 0 dangling tracks by DRC.
- **J2-J6 (TRRS jack) verified, no PCB change needed**: the footprint
  was already hybrid THT+SMD. Compared the matched LCSC part's real
  manufacturer datasheet dimensions against the footprint directly —
  mechanical hole spacing and SMD pad pitch both match exactly.
- Gerbers and drill regenerated (now includes F/B.Paste layers for the
  SMD stencil), all 19 assembly BOM lines resolved to a confirmed,
  in-stock part.

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
