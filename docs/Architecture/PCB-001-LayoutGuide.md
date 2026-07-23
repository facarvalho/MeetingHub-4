# PCB-001 - Layout Guide (Phases 2-10)

Version: 1.0
Status: Final — layout complete, routed and validated (0 unconnected, 0 DRC errors)

Practical guide for the phases that depend on the KiCad graphical interface and
on physical components - work that only you can perform. This document
exists for you to follow step by step while you assemble the PCB.


# Phase 2 - Create the PCB

1. Open the `MeetingHub-4.kicad_pro` project in KiCad.
2. Open the **PCB Editor** (board icon, or double-click
   `MeetingHub-4.kicad_pcb` in the project tree).
3. Menu **Tools → Update PCB from Schematic** (the shortcut hasn't changed
   across recent versions; if you can't find it in the Tools menu, look for
   the toolbar icon with a lightning bolt ⚡ over a board).
4. A dialog will open listing the changes. You should see **66 new
   footprints** (all the components from the 5 sheets, except the GND ones).
   Check that no "Footprint not found" appears - if it does, it's a sign that
   some footprint I assigned doesn't exist in your KiCad installation
   (check that the standard libraries are installed).
5. Click **Update PCB**. The 66 footprints will appear stacked near the
   origin, on top of each other - this is normal, nothing has been
   positioned yet.
6. Save the `.kicad_pcb` immediately (Ctrl+S) to make sure the
   schematic↔PCB association was recorded.

**Do not route anything in this phase.** The goal is just to have the 66
footprints loaded onto the board.


# Phase 3 - Define the mechanics

This is the most important phase according to your own assessment, and I
agree: a wrong decision here forces you to redo the entire placement later.

Answer before touching any footprint:

## 3.1 Which components need to touch the enclosure panel

Based on the schematic, these **11 components have a panel function** (the
user needs to reach them from outside). The final decision about **which
face/side** for each one follows the logic of use (what the operator touches
most often goes on the front; permanent/rare connections go on the back):

| Component | Function | Enclosure face/side |
|---|---|---|
| J6 (TRRS) | operator's headset | **front** |
| SW1-SW5 (via JST-XH + wire) | mute + laptop selection | **front** (physical switch off-board, connected by wire to the JST connector; they sit near J6, since it's what the operator handles most) |
| RV1-RV5 (dual potentiometer) | individual volume + master | **top** (the RK097 shaft points upward, accessible from the top panel) |
| J2-J5 (TRRS) | 4 laptops (3.5mm jack) | **back** (the cable stays connected all the time, doesn't need to be accessible during use) |
| J1 (USB-C) | power supply input | **back**, next to the 3.5mm jacks |

Everything else (U1, U2, K1-K4, R1-R20, C1-C21, F1, D1-D5, TP1) is
**internal**, with no panel restriction.

**Why this split:** the operator interacts with the headset and the
microphone selectors all the time (front) and adjusts the volume
occasionally (top) - these go on the easy-access faces. The laptop cables
and the power supply are plugged in once and rarely touched again - they go
to the back, out of the way.

## 3.2 Board dimensions

- Measure the internal space of the enclosure (or define the enclosure
  first, if you haven't chosen one yet).
- Rule of thumb: the board must be **at least wide enough to line up 5 TRRS
  jacks (J2-J6) + clearance for tightening the panel nut**. A 3.5mm panel
  jack (PJ320D type) typically needs ~12-15mm center-to-center so the nut
  doesn't bump into its neighbor - for 5 jacks in a row that's already
  ~60-75mm just for the jack front.
- If the 5 potentiometers (RV1-RV5) are also going on the same front face,
  that's 5 more shaft holes, each needing ~20-25mm center-to-center (the
  RK097 has a larger body than the jack). If it doesn't all fit in a single
  row, plan for two rows (jacks on the bottom, pots on top, for example).
- Sketch this arrangement on paper or in a vector editor **before**
  defining the board outline in KiCad - the board outline (`Edge.Cuts`)
  should come from the panel drawing, not the other way around.

## 3.3 Draw the board outline

### 3.3.1 Before drawing

- Decide which enclosure path you're going to follow (see the earlier
  discussion: off-the-shelf catalog vs. custom-made via
  PCBWay/JLC3D/JLCMC/acrylic sandwich). This changes what "correct" means
  here:
  - **Off-the-shelf enclosure**: the outline needs to match **exactly** the
    internal dimensions from the datasheet of the chosen enclosure,
    including clearance for internal ribs/rails that many plastic cases
    have near the edges - measure or check the case manufacturer's
    technical drawing, don't rely only on the external measurement.
  - **Custom-made enclosure (later)**: the outline can be a simple
    rectangle, sized to whatever remains after positioning the panel
    components (Phase 3.2) plus a margin of ~3-5mm on each side. The case
    will be cut/printed to order based on the STEP/Gerber file you export
    later - it doesn't need to be exact on the first try.
- Adjust the **grid** before drawing: `View → Grid Properties` (or the grid
  icon in the side toolbar), set it to 1mm (or 0.5mm if you want more
  precision at the corners). Drawing "by eye" without a grid is the most
  common cause of outlines with gaps.

### 3.3.2 Step by step in KiCad

1. In the layers list (right side, by default), click **Edge.Cuts** to
   select it as the active layer - it usually appears in yellow.
2. Use the **Add Rectangle** tool (rectangle icon in the right-side
   toolbar, or shortcut key `R`) if the outline is a simple rectangle.
   Click a corner, drag to the opposite corner, click again to close it.
3. If the outline is **not** a simple rectangle (e.g., a cutout so the
   jacks stick out further, or a chamfered corner), use **Add Line**
   (shortcut `Alt+L` or the line icon) segment by segment, always closing
   at the point where you started.
4. **Don't rely on the mouse click for exact measurements.** After drawing
   it approximately, right-click each segment → **Properties** (or key
   `E`) and type the exact **Start X/Y** and **End X/Y** values manually.
   That's how you make sure the outline is, for example, exactly
   90mm x 60mm, and not "89.7mm because your hand shook".
5. For rounded corners (common in custom enclosures, easier to
   print/cut): in KiCad 7, select the two segments that form the corner
   and use **Edit → Fillet Lines** - enter the desired radius (e.g., 3mm)
   and it automatically replaces the sharp corner with an arc, with the
   geometry properly closed.

### 3.3.3 Mounting holes

**Applied directly in the `.kicad_pcb`**: 4 `MountingHole_3.2mm_M3`
footprints (3.2mm non-plated hole, no net, suitable for an M3 screw), one
in each corner, with a 6mm margin from the edge (within the recommended
5-6mm range, without colliding with any component - all 4 corners were
free):

| Reference | Position (X, Y) | Corner |
|---|---|---|
| MH1 | 66.0mm, 91.0mm | top-left |
| MH2 | 319.0mm, 91.0mm | top-right |
| MH3 | 66.0mm, 239.0mm | bottom-left |
| MH4 | 319.0mm, 239.0mm | bottom-right |

(The board spans x=60-325mm, y=85-245mm; 6mm margin on each axis from the
edge.)

- If the enclosure has already been chosen, check whether this position
  matches the case's mounting holes/rails before manufacturing - if it
  doesn't match, just move the 4 footprints in KiCad (Properties → X/Y) to
  the correct position, the hole geometry itself doesn't change.
- If the enclosure is custom-made (later), these positions become the
  reference for the case manufacturer to align their holes.
- Validated: file paren balance, no collision with neighboring footprints
  (no other component within 20mm of any corner), and a clean
  `kicad-cli pcb export gerbers`.

### 3.3.4 Check that the outline closed correctly

An outline with a gap (not closed) is the most common error in this phase,
and it only shows up when generating Gerbers/manufacturing if you don't
check beforehand:

1. Run the DRC (getting a bit ahead of Phase 8, just for the outline):
   **Inspect → Design Rules Checker → Run DRC**. An open outline shows up
   as an error of type *"board outline"* or *"Unclosed board outline"*.
2. Visual alternative: open the **3D viewer** (`View → 3D Viewer`, or
   `Alt+3`) - if the outline didn't close, the board appears "punctured"
   or oddly shaped instead of as a solid piece.
3. Only after confirming the outline is closed and error-free is it worth
   moving on to Phase 4 (final placement) with confidence that the board
   geometry is correct.


# Phase 4 - Placement

The order below prioritizes components with mechanical constraints (panel)
over those with only electrical constraints - and it has already been
**applied directly in the `.kicad_pcb`** (exact positions per reference,
validated by script: no pair of components with anchors closer than 6mm,
closed outline, clean `kicad-cli pcb export gerbers`). The on-screen visual
check and Phase 9 (1:1 mockup) are still needed before considering it
final.

1. **J2-J5 (3.5mm jacks) + J1 (USB-C)** - back row (y=100mm), 40mm pitch
   between the 4 laptop jacks; J1 set apart to the side (x=290mm), with the
   POWER cluster (F1, D1, C1, C2, TP1) right next to it.
2. **RV1-RV5 (potentiometers)** - "top" row (y=170mm), each aligned on the
   same X column as the corresponding laptop jack (RV1 above J2, RV2 above
   J3, etc.); RV5 (master) in the fifth column.
3. **J6 (headset) + SW1-SW5** - front row: J6 at the edge (y=230mm),
   SW1-SW5 right behind it (y=218mm, 15mm pitch) - they sit close to what
   they serve.
4. **K1-K4 + D2-D5 (mic switching)** - near the SW group, but in its own
   band (y=190/203mm) so as not to collide with them; K1 aligned with SW2,
   K2 with SW3, etc.
5. **U1 (mixer) + R1-R12 + C3-C14** - 5x5 grid between the back row and the
   top row (x=75mm, y=118mm onward, **15x11mm pitch** - the X pitch was
   widened from 13 to 15mm in a second round, for the same reason as the
   HPAMP: it caused too much congestion for the GND plane to connect 2
   specific pads without violating clearance - see the note at the end of
   this phase) - it's literally the midpoint of the signal path (3.5mm jack
   → volume → mixer).
6. **U2 (headphone amp) + R13-R20 + C15-C21** - 4x4 grid near J6 (x=215mm,
   y=182mm onward, 12x11mm pitch).

**Exact coordinates per reference** are in the `.kicad_pcb` - there's no
separate copy here because it would go out of date with every fine
adjustment you make on screen. If you need to check a specific value, open
KiCad and select the component (the properties panel shows X/Y).

**Note on the mixer grid re-layout (pitch 13→15mm)**: after the first
routing pass (Phase 7), the GND plane ended up with pads trapped in copper
pockets isolated from the main plane - the cause was a lack of space for
the zone filler to lay down a proper "spoke" to those pads without
violating clearance with neighboring signal traces. Widening the grid's X
pitch, repositioning the 25 components, and re-running Freerouting from
scratch fixed C4, R2, C1 and C3 (via manual GND stitching + small detours
in neighboring signal traces - NB2_L/NB3_L/NB2_R - to open up real space,
and a solid connection instead of a thermal relief for C1/C3). Validated
by script (paren balance, count of unconnected items via `pcbnew`,
pad-to-pad and trace-to-pad clearance per layer, clean
`kicad-cli pcb export gerbers`) and confirmed by an on-screen real DRC
after each round.

**Resolved: U1 pin 4 (GND), via migration to 4 layers.** This specific pin
had no copper path available to the GND plane on the 2-layer board, within
the minimum manufacturing clearance (0.15mm). Root cause: in a DIP-8
package, pin 4 sits physically between pin 3 and pin 5 (that's how the
package numbering wraps around), so this local tightness is inherent to
the chip's pinout, not to the surrounding layout - confirmed by trying:
(a) widening the mixer grid's X pitch and then also the Y pitch (2
complete rounds of re-layout + rerouting), (b) rotating U1 by 90° (same
pinout, same tightness, only the direction changes), (c) an exhaustive
script-based search (A*, neighboring trace bulging) finding no path with
reliable clearance, and (d) a manual on-screen attempt by the user, same
conclusion.

Since no placement adjustment addresses the real cause (the chip's own
pinout), the solution was to migrate the board to **4 layers** with a
dedicated GND plane (see Phase 6) - this eliminates the problem
structurally, since pin 4 now touches the plane directly through its own
through-hole, without competing for space with any signal trace. Confirmed
by a real headless DRC (`pcbnew.WriteDRCReport`, see note below): **0
unconnected pads, 0 real errors**.

**TP2** (same footprint as TP1,
`TestPoint_THTPad_D1.5mm_Drill0.7mm`), connected to the GND net, at
position (67.0mm, 125.62mm), was kept as a generic GND test point (useful
for touching a multimeter/oscilloscope probe to) - the manual jumper
instruction that was on the silkscreen was removed, since it's no longer
needed.

**Note on validation in this phase**: I discovered that
`pcbnew.WriteDRCReport()` generates a real, complete DRC report even
without the GUI (unlike what was assumed at the start of the project, that
this KiCad version had no DRC via command line/script) - the approximate
script-based checks used in earlier phases of the session were replaced
with this function wherever possible from here on. One side effect noted:
running this function outside the full KiCad environment (without the
footprint library table configured) generates false `lib_footprint_issues`
warnings ("footprint not found in library") for practically every
component - this is a limitation of the headless environment used to
generate the report, not a real board problem; it doesn't happen when
running DRC through the KiCad GUI.

**Pending**: the 6mm clearance used in validation is only between anchors
(footprint center), not between actual bodies - the RK097 potentiometer,
G5V-1 relay and PJ320D jack have larger bodies than that. Confirm visually
before routing.


# Phase 5 - Layout planning (regions)

Zoning **actually applied** (Phase 4), organized by enclosure face instead
of by schematic sheet - but the noise-isolation principle from SCH-008
still holds, just expressed as front/back instead of side by side:

```text
                    BACK (y=100-135)
┌───────────────────────────────────────────────────┐
│  J2 J3 J4 J5        J1          F1 D1 C1 C2 TP1     │  <- 3.5mm jacks + USB-C + POWER
│                                                     │
│  ┌──────────────┐              ┌─────────────┐     │
│  │ AUDIO_MIXER  │              │             │     │
│  │ U1,R1-12,     │              │             │     │
│  │ C3-14         │              │             │     │
│  └──────────────┘              │             │     │
│                                                     │
│  RV1 RV2 RV3 RV4 RV5                                │  <- TOP (y=170)
│                                                     │
│  ┌──────┐                      ┌──────────────┐    │
│  │MIC_SW│                      │ HEADPHONE_AMP│    │
│  │K1-4  │                      │ U2,R13-20,   │    │
│  │D2-5  │                      │ C15-21       │    │
│  └──────┘                      └──────────────┘    │
│  SW1 SW2 SW3 SW4 SW5              J6                │  <- FRONT (y=218-230)
└───────────────────────────────────────────────────┘
                    FRONT (user)
```

Central idea, adapted: **the power supply (POWER) and the 3.5mm jacks stay
at the back, away from the operator; the microphone line (MIC_SWITCHING)
stays at the front**, close to where it ends (SW1-SW5) and far from where
the power supply comes in (back). The audio path (3.5mm jack → volume →
mixer → headphone amp → J6) crosses the board from back to front in a
straight line, without crossing back - same logic as before (SCH-008),
except the "front" of the enclosure now plays the role of the opposite end
from the power supply, instead of a specific schematic sheet.


# Phase 6 - Ground plane

**Updated: the board was migrated from 2 to 4 copper layers**
specifically to definitively resolve the problem described in Phase 8 (U1
pin 4 trapped in an isolated GND pocket, even after two rounds of
re-layout). With 2 layers, the GND plane competed for space with signal
traces on the same layer (B.Cu), and at some points in the mixer grid
there wasn't enough legal space for the zone filler to connect certain
pads without violating clearance. The standard professional solution to
this problem is to dedicate entire layers solely to planes, with no signal
trace competing for space on them - this is what was applied:

- **F.Cu** (top) and **B.Cu** (bottom): signal only - this is where
  Freerouting routes the ~105 signal nets (audio, mic, relay control).
- **In1.Cu** (internal layer 1): solid **GND** plane, covering the entire
  board, with no signal traces.
- **In2.Cu** (internal layer 2): solid **+5V_AUDIO** plane, same coverage.
- Since all 66 components are through-hole (THT), any GND or +5V_AUDIO pin
  already touches these two internal layers directly through its own hole
  - no extra trace or via is needed in most cases. **Exception**: the "R2"
  (shield) pins of the TRRS connectors (J2-J6), which are SMD only on the
  F.Cu layer in the `Jack_3.5mm_PJ320D_Horizontal` footprint - these 5
  points needed a dedicated via going down to the GND plane, already
  applied.
- To set this up in KiCad (if you're reproducing it from scratch):
  **File → Board Setup → Physical Stackup**, change "Copper Layers" to 4,
  and mark In1.Cu/In2.Cu as type **Power** (not Signal) in
  **Board Setup → Layers** - this is what stops the autorouter from
  dropping signal traces on these layers.
- **Star grounding** (already decided in SCH-008/DR-002): the GND return
  from POWER and the GND return from the analog block
  (TRRS/MIXER/HPAMP) must meet at a single physical point - with the
  dedicated internal plane, this is now naturally satisfied (the whole
  plane is a single node).
- A concern that **is no longer necessary** with the dedicated plane: the
  original worry about the K1-K4 coil current sharing a plane segment with
  the MIC/audio return no longer applies in the same way, since the GND
  plane now has no signal trace competing for a path within it - but it's
  still worth positioning K1-K4 near the POWER region for the general
  organization of the layout.


# Phase 7 - Routing

Follow the order you proposed. Suggested trace widths for this board
(power supplied via USB, ~500mA at the fuse):

| Signal type | Suggested width |
|---|---|
| +5V_AUDIO, GND (power) | 0.6-0.8mm |
| Audio signal (NB*_L/R, MIX_L/R) | 0.25-0.3mm |
| Microphone line (NB*_MIC, HEADSET_MIC) | 0.25-0.3mm, **avoid running parallel and close alongside a +5V_AUDIO trace or relay coil** - if crossing, cross perpendicularly, never parallel for more than a few mm |
| Relay control (coil, +5V_AUDIO→SWx→K) | 0.4-0.5mm |

Routing order (yours is correct):

1. Power supply (+5V_AUDIO, from J1 to POWER, then to MIXER/HPAMP/MICSW)
2. GND (plane, plus the few cases that can't be resolved with the plane
   alone)
3. Op-amp signals (U1 and U2 feedback loops - keep these traces short,
   they're the most sensitive to picking up noise)
4. Microphones (NB1-4_MIC, HEADSET_MIC - a "transparent" line, with no
   amplification, so any noise picked up here goes straight to the laptop)
5. Headphones (MIX_L/R, J6 output)
6. Control (relay coils, SW1-SW5)
7. USB-C last, as you suggested - the 4 data pins (D+/D-/CC1/CC2) are
   **intentionally unused** in this project (only VBUS+GND matter), so
   they don't even need any trace - ignore the "unconnected" warnings
   KiCad reports for these pins.


# Phase 8 - DRC

1. In the PCB Editor: **Inspect → Design Rules Checker** (or the
   "bug"/magnifying-glass icon in the toolbar).
2. Before running it, check **File → Board Setup → Design Rules →
   Constraints** and set **Minimum track width** and **Minimum clearance**
   to a safety floor above the factory minimum (JLCPCB's default is
   0.153mm trace and 0.127mm spacing).
   **Correction to this guide's original suggestion**: with the board
   already routed (Phase 7, via Freerouting), most signal traces use
   0.2mm and the clearance validated throughout the whole session is
   0.15mm - using 0.25mm/0.2mm (the original suggestion, written before
   the routing existed) would create ~400 false "trace width error" flags
   on traces that are already correct. Use **0.2mm minimum track width and
   0.15mm minimum clearance** instead - still comfortably above the
   JLCPCB minimum, but compatible with what has already been routed.
3. Click **Run DRC**. Fix one error at a time, running it again after each
   fix - don't try to fix everything at once and only run it at the end.
4. Most likely errors on this board: clearance between the large
   G5V-1/USB-C pads and neighboring traces, and unrouted traces
   (unconnected net) if some footprint is left without every trace
   connected.
5. Only consider Phase 8 complete with **zero errors and zero unjustified
   warnings** (a "short trace" warning or similar may be acceptable, but
   document why).

**Accepted and documented warning**: the 4 mounting holes (MH1-MH4, Phase
3.3.3) trigger `[extra_footprint]` (warning severity) because they are
mechanical-only footprints, added directly in the `.kicad_pcb` with no
corresponding symbol in the schematic - this is expected and safe for
`MountingHole`, which has no electrical function and therefore normally
doesn't go into the schematic. You can ignore this specific warning (@MH1,
MH2, MH3, MH4) without worry.


# Phase 9 - 1:1 scale mechanical review

1. In the PCB Editor: **File → Print**.
2. Check the **1:1** scale option (sometimes called "Scale 1" or "No
   scaling" depending on the version) - **never use "fit to page"**, it
   distorts the scale.
3. Before trusting the printout, measure a known dimension on the paper
   with a ruler (e.g., the distance between two mounting holes) to confirm
   the printer didn't scale anything.
4. With the printed sheet, physically overlay:
   - a G5V-1 relay (or its drawn footprint) over the K1-K4 pads;
   - a TRRS jack (the actual model you'll buy) over J2-J6;
   - an RK097 potentiometer over RV1-RV5;
   - the USB-C connector over J1.
5. Check whether the panel mounting holes (if any) line up with the actual
   position of the components, and whether no two components are trying to
   occupy the same physical space (e.g., the potentiometer body touching
   the neighboring relay).


# Phase 10 - Manufacturing

**4-layer board** (see Phase 6) - when requesting a quote/manufacturing on
the manufacturer's website, explicitly select **"4 layers"** (or
equivalent) in the order options, not the default 2-layer one. This
usually costs more than 2 layers (most manufacturers charge about 30-70%
more for small batches), but it's mandatory - the generated gerbers
already include the internal layers (`In1_Cu`, `In2_Cu`), so the
manufacturer will notice it's 4 layers from the files themselves, but
confirm the order option matches before finalizing the purchase.

Files to generate (via **File → Fabrication Outputs** in the PCB Editor,
or the `kicad-cli pcb export` command line):

- **Gerbers** (all 4 copper layers + mask + silk + Edge.Cuts)
- **Excellon** (drill file)
- **Final BOM** - we already have one generated at
  `hardware/BOM/BOM-MeetingHub-4.csv`; confirm it still matches the final
  `.kicad_pcb` before sending it.
- **Assembly PDF** (component positions, useful for yourself when
  soldering)
- **Schematic PDF** - we already have one at `hardware/Schematics/`

**Note on Pick & Place**: all 66 components in this project have a **THT**
footprint (no SMD). This means that, strictly speaking, you **don't need
to generate a Pick & Place file** for this batch, unless you decide to
hire automated wave/selective soldering assembly from some manufacturer
that asks for this file even for THT. For manual assembly, Gerbers +
Excellon + BOM + assembly PDF are already enough.

Once everything is generated, call me back and I'll check:
- whether the files open and are consistent with each other (via
  `kicad-cli`);
- whether the final BOM matches the `.kicad_pcb`;
- whether any footprint was left without a value/reference before closing
  out the manufacturing package.


# Phase 11 - Post-ERC fixes (TP1/TP2 with no net on the PCB)

Running the real schematic ERC (via GUI, only possible in this KiCad
version through the interface - see BOM-002-AsBuilt Section 4), a
`pin_not_connected` appeared on TP1. Investigating, the TP1 pin was
visually sitting on top of an existing wire in the schematic (POWER sheet)
without an electrical **junction** there - a classic KiCad mistake
(visual overlap ≠ connection). Fixed in the schematic with a `junction` at
the exact point.

Checking the PCB afterward, the problem was worse than just the
schematic: **the TP1 pad on the board also had no net at all**
(`unconnected-(TP1-Pad1)`), and **neither did TP2** (empty net) - both
test points were physically floating on the final board, despite the
documentation saying they were on +5V_AUDIO/GND. Fixed via a Python script
(`pcbnew`): assigned the `+5V_AUDIO` net to the TP1 pad and `GND` to the
TP2 pad, followed by recalculating the planes (`ZONE_FILLER.Fill`) so that
each pad's solder ring actually connects to the corresponding internal
plane. Confirmed afterward via
`board.GetConnectivity().GetUnconnectedCount(False)` = 0 and a new
`WriteDRCReport` with no real errors.

Also fixed, by the same ERC: the `power_pin_not_driven` on U1 (pins
V+/V-) - added two `power:PWR_FLAG` symbols in POWER.kicad_sch (KiCad's
standard idiom for when a net's power comes from a connector pin, here the
VBUS of J1/USB-C, rather than from a dedicated power symbol); and the
`lib_symbol_issues` on J2-J6 - the `lib_id` was pointing to
`Connector:AudioJack4`, an old library that no longer exists at that
location in the installed KiCad (the symbol was reorganized into
`Connector_Audio` in newer versions of the standard library). Fixed the
`lib_id` to `Connector_Audio:AudioJack4` - geometry and pins checked
byte-for-byte against the system library before the change, with no
difference.

**Lesson for the next project**: test points (TP) added directly on the
PCB (with no schematic symbol, like TP2) need to have their net assigned
and checked manually - they don't show up in the schematic ERC (they
don't exist there) and don't generate an obvious DRC error if left without
a net (there's no neighboring pad to complain about being "unconnected"
with a single isolated pad). The way this was caught was by checking
net-by-net via script, not just by looking at the DRC report.

In a second round of ERC (after pulling in the fixes above), the user
reported that the `power_pin_not_driven` on U1 **persisted** on pin V+
(pin 8), even with the `PWR_FLAG` already added. Investigating, the flag
had been attached to the wrong wire: there were two similar-looking nodes
in the POWER sheet near fuse F1 - one **before** the fuse (coming from
VBUS/TVS protection) and another **after** it (the actual +5V_AUDIO net,
the same one carrying the `+5V_AUDIO` global label and TP1). The flag had
landed on the node before the fuse, which doesn't share the same net name
and therefore doesn't count toward the ERC as a +5V_AUDIO source. Fixed by
moving the `PWR_FLAG` to the correct node (the same one as TP1 and the
global label).

This same round also confirmed 13 `pin_not_connected` errors that had
existed since the first version of the schematic, but which I had only
documented as "intentional" instead of actually resolving: the 9
data/CC/SBU/shield pins on J1 (USB-C, unused because J1 is power-only) and
pin 10 on the 4 relays (a duplicated pin, unused in the SPDT topology).
Fixed by adding an explicit **no connect** (`no_connect`) on each of these
13 pins - the correct, definitive way to zero out this type of ERC error,
instead of leaving it as a pending note in the documentation.

After confirming 0 errors, 232 `endpoint_off_grid` warnings remained - on
practically every pin and wire across the 5 sheets. Root cause: the entire
schematic was drawn using round positions in millimeters (e.g., 55.0,
85.0, 115.0mm), which **are not multiples of the 1.27mm grid (50 mil)**
that the ERC check uses as its reference - so almost every symbol falls
"off grid" even though it was positioned in a perfectly deliberate way.

Fixing this manually, symbol by symbol, would be too risky at this scale
(~70 components, hundreds of wires, 5 files) - it's easy to disconnect
something without noticing. Instead, I used a mathematical property: if I
apply the **same rounding function** (`snap to the nearest multiple of
1.27mm`) to every coordinate in the file (symbol position, wire endpoint,
junction), two points that were already **exactly equal** before (the
definition of "connected" in the KiCad format) remain exactly equal
afterward - the function is deterministic, so the same input always gives
the same output. This makes it possible to realign the entire project to
the grid without, in principle, changing any connection.

I wrote a script (`snap_grid.py`) that does exactly this: it parses each
sheet into a tree (without touching `lib_symbols`, which is just the
cached library, not the on-page instance), finds every symbol/wire/
junction/global label/no-connect at the schematic level, and rounds their
coordinates. I ran it on all 5 sheets (716 adjustments on AUDIO_MIXER
alone, the largest one).

**Validation**: `kicad-cli sch export netlist` has an output format
(`kicadsexpr`) that lists every net and its nodes - I ran it before and
after the realignment and compared net by net (by node set, ignoring net
name/code, which change). It confirmed 1 real problem: the realignment
brought D1 (TVS protection) close enough to the D+ pin of J1 (USB-C,
unused) that the two landed on the same grid point, merging two nets that
should have stayed separate - exactly the kind of case "two statistically
close points collapse onto the same grid square" that I had already
anticipated as a theoretical risk before starting. Fixed by moving D1 one
extra grid step away (and the wire connecting to GND, which depended on
D1's old position). A second round of `export netlist` confirmed the
project's 72 nets matching node-for-node, with no difference at all.

**Lesson**: this kind of "bulk snap" is safe in expectation, but it's not
zero risk - it's always worth validating with a connectivity comparison
tool (netlist, not just an error/warning count) after any batch geometric
transformation, because a clean DRC/ERC doesn't guarantee the topology
didn't change, only that it didn't violate the rules being checked.
