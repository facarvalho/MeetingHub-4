# Changelog

Milestone history of the MeetingHub-4 project, by phase. For the line-by-line history, see `git log`.

## DRC pass on the SW1-SW5 / RV1-RV4 footprint changes (2026-08-07)

Ran a real DRC via `pcbnew.WriteDRCReport` (only path available - this
KiCad 7.0.11 CLI has no `drc` subcommand) against the board after the
two changes below, compared to a fresh baseline report from the
pre-change commit. Two self-inflicted issues found and fixed directly
(no rerouting needed):

- **8 unconnected pads on SW1-SW5**: caused by assigning the same net
  to *both* physical copper legs of each same-numbered pad (e.g. both
  "1" pads). That's electrically true (the real switch bridges them
  internally) but KiCad's DRC then expects a *routed* copper connection
  between the two pads, which doesn't exist on this board. Fixed by
  matching the convention the project's own prior SW1 footprint
  (`SW_PUSH-12mm`) already used: net only on the first pad of each
  number, second left with no net (still gets a drilled/soldered hole,
  just not routed — harmless, since the physical switch bridges it).
- **2 solder-mask-bridge errors on RV1/RV2 pad 1**: the official
  `Potentiometer_Alps_RK09L_Double_Vertical` footprint draws pad 1 as a
  sharp-cornered `rect`; at this exact position that aperture was close
  enough to a neighboring track to bridge solder mask between nets.
  Changed pad 1 to `roundrect` (rratio 0.25, same size/position/drill)
  matching the old RK097 footprint's pad 1 shape - resolved it without
  touching any track.
- Also refilled the GND/+5V_AUDIO inner-layer zones via
  `pcbnew.ZONE_FILLER` (editing pads/footprints doesn't auto-refill
  zones; the stale fill was itself producing extra clearance/thermal
  violations against the new pad shapes).

**Remaining — needs manual rerouting, not fixed here**: SW1-SW5's new
pads sit in different positions than the parts they replaced (the
switches have a genuinely different physical pin layout, not just a
size change like RV1-RV4 was). ~8-11 DRC errors remain, all on short
existing trace segments that no longer reach the new pad locations by
2-3mm: SW1 (HEADSET_MIC, Net-(SW1-B)), SW2 (Net-(D2-A), Net-(D3-A)),
SW3 (Net-(D3-A), Net-(D4-A)), SW4 (Net-(D4-A), Net-(D5-A)), SW5
(Net-(D5-A), Net-(J6-PadR1)) - all near the front-row +5V_AUDIO feed
and each switch's diode-side signal pad. RV1-RV4 have zero remaining
errors. Full list in `hardware/KiCad/MeetingHub-4/DRC.rpt` (local,
gitignored, regenerate with the same `pcbnew.WriteDRCReport` approach
after rerouting).

## RV1-RV4 potentiometer body change (2026-08-07)

- **RV1-RV4 switched to a compact/square body**: Alps RK09L1240A12 (LCSC
  C380211, 881 in stock), replacing the wide RK09712200HA (29.6x9.5mm)
  they shared with RV5. New body is 14.5x17.9mm, much closer to square.
  RV5 (master volume, front panel, horizontal) was intentionally left
  unchanged on RK09712200HA — only RV1-RV4 were in scope.
- New footprint `Potentiometer_Alps_RK09L_Double_Vertical` added to the
  project-local library. It's a copy of KiCad's own standard
  `Potentiometer_THT.pretty` footprint of the same name (already
  vetted, matches the Alps RK09L datasheet), with one change: the 2
  "MP" mechanical-only pads from the official footprint were dropped.
  One of them landed 0.13mm from an existing track on this board — a
  real clearance conflict — and since MP pads carry no signal (pure
  mechanical support, commonly left unpopulated), removing them was
  lower-risk than moving the track or the component. The 6 signal pads
  keep the exact same size, drill, and position as the pads they
  replace, so all existing routing to RV1-RV4 was unaffected.
- Net-to-pad mapping carried over directly (pad N → pad N): both the
  old RK097 and new RK09L footprints use the identical KiCad-authored
  2.5mm/3x2 pad grid and numbering (pads 2 and 5 are the wiper of each
  gang), confirmed against the actual pad positions in both library
  files before mapping, not assumed from naming alone.
- Checked for physical collisions after the swap: initial generic
  bounding-box comparison flagged apparent overlaps with C12/C13/C14/
  C18 and between RV2/RV3, but re-checking with the real F.CrtYd
  courtyard rectangles (the bbox check also counts silkscreen
  reference/value text, which overstates the footprint) showed no
  actual courtyard overlap in any case — false alarms.
- Applied to `MeetingHub-4.kicad_pcb` (same position/rotation, nets
  preserved) and `MIXER.kicad_sch` (Footprint property updated for
  RV1-RV4; RV5's Footprint property was also corrected to match what's
  actually on the board, `Potentiometer_Alps_RK097_Dual_Horizontal`,
  fixing the last of the schematic/PCB staleness noted in the SW1-SW5
  entry below).
- BOM-MeetingHub-4.csv, BOM-PCBA-MeetingHub-4.csv, and
  BOM-003-SourcingLinks.md updated accordingly.
- **Not verified**: whether the existing "eixo chato 6mm" knobs
  (bought for RK09712200HA's shaft) fit RK09L1240A12's shaft — same
  family, but shaft type/diameter wasn't cross-checked against a
  datasheet. Also, as with the SW1-SW5 change, DRC/ERC could not be
  re-run via `kicad-cli` (no `drc`/`erc` subcommand in this KiCad
  7.0.11 build) — verified via `pcbnew` Python (pad positions/nets,
  track-proximity check within 1.2mm of every pad) and clean
  `kicad-cli sch export pdf` / `pcb export svg` runs instead. Open in
  the KiCad GUI and run DRC/ERC there before fabrication.

## SW1-SW5 switch standardization (2026-08-07)

- **SW1-SW5 unified onto one part**: SHOU HAN TS665ZJ (LCSC C557599), a
  THT right-angle tactile switch with mounting bracket, SPST, 6.2x7.5x5mm,
  71,560 in stock. Replaces both prior parts — SW1's Omron B3F-4005
  (C397283) and SW2-SW5's CW Industries GPTS203211B, which was
  CONSIGNED (not on LCSC, had to be bought separately from DigiKey).
  That consignment requirement is now gone.
- New custom footprint `SW_SHOUHAN_TS665ZJ`, added to a new project-local
  library (`hardware/KiCad/MeetingHub-4/MeetingHub-4.pretty/` +
  `fp-lib-table`, since the project previously relied only on KiCad's
  global standard libraries). Geometry (pad pitch, drill, body outline)
  was taken directly from LCSC's own EasyEDA source data for C557599,
  not estimated — but not yet cross-checked against a physical unit or
  a manufacturer datasheet PDF, and has no 3D model yet.
- 4 physical THT pads (2 legs per pole, same "duplicate pad number per
  node" pattern already used by SW1's previous `SW_PUSH-12mm`
  footprint), so both legs of each pole are tied to the same net.
- Applied to `MeetingHub-4.kicad_pcb` (all 5 footprint instances
  swapped in place — same position, rotation, and net assignments
  preserved) and to `MICSW.kicad_sch` (Footprint property updated,
  fixing the schematic/PCB staleness on this component; RV1-RV5 remains
  stale per the note above).
- BOM-MeetingHub-4.csv, BOM-PCBA-MeetingHub-4.csv, and
  BOM-003-SourcingLinks.md updated accordingly.
- **Not done as part of this change**: the PCBWay PCBA quote in
  `production/Suppliers/` was based on the old SW1/SW2-5 parts and is
  now stale for those 5 line items — re-verify with PCBWay before
  ordering. DRC/ERC could not be re-run via `kicad-cli` in this
  environment (this KiCad 7.0.11 CLI build has no `drc`/`erc`
  subcommand); verification here was done via `pcbnew` Python
  (footprint load, position, net-by-net pad check) and a clean
  `kicad-cli sch export pdf` — open in the KiCad GUI and run DRC/ERC
  there before fabrication.

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
