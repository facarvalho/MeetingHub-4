# RESOLVED (2026-08-06, updated): SW2-SW5 rotated horizontal, re-routed, DRC clean

**Status: ready for gerbers.** `MeetingHub-4.kicad_pcb` now has 0 real
DRC violations (0 clearance, 0 hole_clearance, 0 solder-mask bridges,
0 courtyard overlaps, 0 unconnected pads) — verified via KiCad's own
DRC. RV1-4 stayed in the diamond/staggered layout, RV5 is rotated 90°
and fully routed at the front panel next to SW1/J6.

**Latest round**: SW1 (MUTE pushbutton) was already horizontal at 0°
(its `SW_PUSH-12mm` footprint spans 12.5mm in X / 5mm in Y) so it was
left unchanged. SW2-SW5 (`SW_CW_GPTS203211B` selector switches) were
vertical at 0° (pads 5.3mm apart in Y) and are now rotated 90° to lie
horizontal, matching SW1's orientation. This required: re-bridging
each switch's pad2 (`Net-(D2-A)`..`Net-(D5-A)`) via a via-hop through
B.Cu to its new pad location (the F.Cu row was too congested with
existing trunk traces for a direct diagonal); shifting SW2 2mm to the
right (128.8→130.8mm) to clear a courtyard overlap with RV5 that the
rotation introduced; and re-routing one segment of the D5-A trunk that
came too close to SW3's new pad2 position. Zones were refilled after
all pad moves.

What got the board there originally: full board re-route via the
Freerouting autorouter (DSN export → `java -jar freerouting-*.jar -de
... -do ... -mp 5` → `File → Import → Specctra Session` in KiCad),
followed by manually closing one last VBIAS gap on RV5 (pad6→pad3, a
2.5mm bridge that needed to dodge MIX_L/MIX_R traces running through
the same pocket).

**Fabrication files regenerated (2026-08-06) and ready to order:**
- `hardware/Gerbers/MeetingHub-4-Gerbers-v4.0.zip` — gerbers + drill +
  job file for the current 160.19x134.06mm routed board, with SW2-SW5
  horizontal. **v1.0/v2.0 in that folder are stale (old
  265.1x160.1mm board); v3.0 has SW2-SW5 still vertical — don't use
  either.**
- `hardware/Gerbers/MeetingHub-4-Placement.csv` and `-drl_map.pdf`
  regenerated to match.
- [production/PCBWay-OrderGuide.md](../../../production/PCBWay-OrderGuide.md)
  updated to v4.0 / current dimensions.
- [hardware/BOM/BOM-003-SourcingLinks.md](../../BOM/BOM-003-SourcingLinks.md)
  rewritten as a single shopping-list table.

Remaining, not DRC-blocking:
- `lib_footprint_issues` warnings are a local library-path artifact,
  not present when DRC is run from the actual KiCad install — ignore.
- A couple of cosmetic `silk_over_copper` / `silk_edge_clearance`
  warnings — check visually, not required to fix.
- A stray `MeetingHub-4.dsn`/`.ses` may be sitting next to this file
  from the autorouter export — safe to delete, not part of the design.

---

# Superseded below: earlier handoff from the manual-routing attempt

Status: **Work in progress, NOT ready for fabrication**. Open
`MeetingHub-4.kicad_pcb` in KiCad to finish.

**Do not generate gerbers or place an order from the current file
state.** Gerbers/Placement.csv in `hardware/Gerbers/` are stale —
they reflect the *previous* fully-validated 265.1x160.1mm version. To
fall back to that instead of finishing this layout, the backup is at
(outside the repo, ask Claude to restore it into the repo again):
`/tmp/claude-1000/-home-fac-MeetingHub-4/70b6b083-68e6-432f-bf44-7f5a21f890f3/scratchpad/revert-work/bigboard-everything-soldered-VALIDATED.kicad_pcb`


# Progress this round: RV5 relocated to the front panel, board-wide violations 442 → 389

RV5 is the **microphone volume control** and needed to be on the front
edge, near MUTE (SW1) or J6. It's now placed **between SW1 and SW2**,
which required reflowing the whole front row to fit within the
existing board width (no size change, per instruction):

| Ref | Old X | New X | Y (unchanged) |
|---|---|---|---|
| SW1 (MUTE) | 75.4 | *unchanged* | 207.4 |
| **RV5** | *(was 214, near J6)* | **119.0** | 207.4 |
| SW2 | 107.2 | 128.8 | 207.4 |
| SW3 | 123.2 | 145.8 | 207.4 |
| SW4 | 139.2 | 162.8 | 207.4 |
| SW5 | 157.0 | 179.8 | 207.4 |
| J6 | 195.58 (rot 90) | 201.6 (rot 90) | 209.105 |

All 7 items fit left-to-right with ~2.5-3mm gaps, well inside the
160.1mm board width (rightmost point ~214, board edge at 220.09).

**Net DRC change: 442 → 389 violations** (fewer than before this
round started) — the repositioning itself introduced **zero** new
clearance violations against SW2-5/J6/RV5 (verified by name-matching
every clearance violation against those 6 designators: 0 hits).
Verified 3x via fresh `pcbnew.WriteDRCReport` reloads, identical
389/389/389.

The net improvement over the baseline came from cleaning up stale
copper that predated this round and was already causing violations:
- A dangling `VBIAS` detour fragment (leftover from an earlier,
  abandoned "RV5 near MUTE" attempt) that went nowhere useful.
- A 56mm stray `Net-(D5-A)` trace and another stub going to an old,
  no-longer-relevant SW5 position.
- An incomplete `HEADSET_MIC` zigzag that dead-ended in open space
  (never actually reached J6) — deleted, and the *real* `HEADSET_MIC`
  bus was given a clean detour under RV5's new footprint (south strip,
  Y~217, confirmed clear of other copper) so it no longer clips RV5's
  pin2/pin5 row.


# What's left — routing (this is real, contained work, not guesswork)

**RV5**: still has 0 of 6 pins routed. Both a north-side approach
(through the gap between the K1-K4 relay cluster and the switch row)
and a south-side approach (below the switch row) were tried via
scripted routing this round and hit real, repeated collisions — this
whole area is far more electrically congested than it looks:
- The K1-K4 → D2-D5 relay-control routing occupies almost the entire
  Y180-207 band across X70-130 (both F.Cu and B.Cu), not just the
  relay footprints themselves.
- `HEADSET_MIC` runs the full board width at Y=209.563 on F.Cu.
- RV5's own pins are a tight 2.5mm-pitch 2x3 grid, so any bridge
  needs a dedicated lane per pin (see the 3-segment technique used
  for RV1-4) — workable in principle, but combined with the above
  it needs to be done **visually in KiCad**, not blind coordinate
  scripting. Multiple scripted attempts each looked clear on paper
  and then collided with something not visible without rendering the
  board.
- RV5's real net neighbors: pin1/pin4 → `C13`/`C14` (near X100,
  Y141.5), pin2 → `MIX_L` (no close existing stub — needs a fresh
  run, likely from `C15` at X173.8,Y142.5), pin3/pin6 → `VBIAS` (the
  shared bias rail — closest existing point is at (91.3, 207.35), 3mm
  west of RV5's pad1), pin5 → `MIX_R` (existing point at (96.3,
  207.35), same area).

**SW2, SW3, SW4, SW5 pad2** (the `Net-(D2-A)` .. `Net-(D5-A)` relay
control signals): each old chain still ends at roughly its *old*
X position (dangling) and needs a fresh short bridge to the new pad2
location. These are simple 2-terminal bridges (not a tight pin grid
like RV5) — much easier than RV5, but also collided with each other
and with `HEADSET_MIC`/RV5 when routed blind this round, so they were
reverted rather than left half-broken. Old dangling ends:
- D2-A: (109.7, 207.4) → new SW2 pad2 (128.8, 212.7)
- D3-A: (118.94, 205.998) → new SW3 pad2 (145.8, 212.7) — routing
  through here needs to clear RV5's pad1 by at least ~1.5mm
- D4-A: (131.5, 207.4) → new SW4 pad2 (162.8, 212.7)
- D5-A: (142.4, 207.4) → new SW5 pad2 (179.8, 212.7)

**Also unconnected, not part of this round's scope** — a pad each on
C12, C15, C18, C21, and 4 pads on J6 (J6's own signal routing appears
to have been incomplete even before this round — the deleted
`HEADSET_MIC` zigzag never actually reached it).


# Current layout reference

| Ref | Position | Status |
|---|---|---|
| RV1, RV2 | (90,150) / (122,150), 0° | ✅ Clean |
| RV3, RV4 | (117.5,167) / (149.5,167), 0° | ✅ Clean |
| RV5 | **(119.0, 207.4), 0°** — front row, between SW1 and SW2 | ⚠️ Positioned, not routed |
| SW1 | (75.4, 207.4), 0° | unchanged |
| SW2, SW3, SW4 | (128.8,207.4) / (145.8,207.4) / (162.8,207.4), 0° | ⚠️ pad2 needs re-bridge |
| SW5 | (179.8, 207.4), 0° | ⚠️ pad2 needs re-bridge |
| J6 | (201.6, 209.105), rot 90° | position only |


# After routing is finished

1. Run DRC inside KiCad until 0 errors (ignore `lib_footprint_issues`
   and `silk_over_copper`, both cosmetic/environment artifacts).
2. Re-run zone fill (`B`) one more time after routing.
3. Regenerate gerbers/drill (`File → Fabrication Outputs`, or
   `kicad-cli pcb export gerbers` / `export drill` — see
   [PCBWay-OrderGuide.md](../../production/PCBWay-OrderGuide.md)).
4. Update [BOM-003-SourcingLinks.md](../../hardware/BOM/BOM-003-SourcingLinks.md)
   status and re-zip `hardware/Gerbers/MeetingHub-4-Gerbers-v1.0.zip`
   before submitting a new assembly quote.
