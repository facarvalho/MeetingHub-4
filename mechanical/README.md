# MeetingHub-4 Enclosure - v0.1 (draft)

Status: **draft, not visually verified** - I don't have any
3D CAD tool available in this environment (no OpenSCAD, FreeCAD, and
no access to install one), so I have never seen this model rendered. You
need to open it in OpenSCAD and check it before sending it to print.

File: [`MeetingHub-4-Case.scad`](MeetingHub-4-Case.scad)


# What is a project fact vs. what is my estimate

**Comes directly from the real `.kicad_pcb` (reliable)**:
- Board dimensions: 265.1 x 160.1mm
- Position of the 4 M3 mounting holes (MH1-4)
- Position of J1 (USB-C), J2-J5 (laptop TRRS), J6 (headset TRRS),
  RV1-5 (potentiometers), SW1-5 (JST anchors)
- Which enclosure face each component uses (back/front/top) -
  this was already decided and documented in
  [PCB-001 Phase 3.1](../docs/Architecture/PCB-001-LayoutGuide.md)
  since the board layout design, it is not a new invention.

**These are my estimates, with no source in the project (check before
printing)**:
- **Component height** (`component_clearance` in the file,
  20mm): I used typical datasheet values for the G5V-1 relay (~15.7mm),
  DIP-8 socket (~10mm), and 220µF radial electrolytic capacitor (~16mm) -
  I don't have the actual datasheets open, so this is a "part family"
  estimate, not an exact measurement. If any component is taller
  than this, the lid won't close.
- **Connector cutout size** (`trrs_cut_*`, `usb_cut_*`):
  I made **generous** cutouts (window-style, not a tight hole) because
  how far each connector actually protrudes beyond the board edge
  is not documented in any file - sub-millimeter precision cannot be
  relied upon here. Trade-off: there may be visible slack
  around the connector once assembled.
- **Potentiometer shaft hole diameter** (`pot_hole_d`, 7mm) and
  **switch hole** (`sw_hole_d`, 7mm): typical values for
  the RK097 and a common mini toggle/pushbutton switch - **the
  physical switches (SW1-5) haven't been chosen yet** (they are
  wired via JST, with no fixed position on the board), so this hole
  is just a placeholder until you decide which physical switch to
  use and give me its actual hole diameter.


# How to check and generate the file for printing

1. Install [OpenSCAD](https://openscad.org/downloads.html) (free,
   Windows/Mac/Linux).
2. Open `MeetingHub-4-Case.scad`.
3. Press **F5** (preview) for a quick look at the model, or **F6**
   (full render, slower but more accurate) before exporting.
4. The file shows the enclosure base and lid side by side. Rotate the
   camera and check:
   - The 4 board mounting holes (smaller, more internal posts)
     match the corners of your actual board.
   - The rear cutouts (J1 + J2-J5) and front cutout (J6) look right
     in position/size.
   - The 5 lid holes (RV1-5) align with the potentiometers.
5. After checking - **and only then** - export each part
   separately as STL: in the file, comment out the line for the part
   you don't want to export (add `//` in front) and use **File → Export →
   Export as STL**. Export the base and the lid as two separate
   STL files (you'll need to print and send both).


# Adjusting before printing

The most important parameters are at the top of the file, with a
comment explaining each one:

- `component_clearance`: increase if any component is taller than
  the estimated value (measure the actual tallest component above the
  board with a ruler, and use that value + about 2-3mm of clearance).
- `sw_hole_d`: replace with the actual diameter of the physical switch
  you buy for SW1-5.
- `trrs_cut_*` / `usb_cut_*`: if you want a tighter cutout (less
  visible slack), you can reduce these - but I recommend testing first
  with the draft's generous clearance, it's easier to guarantee a fit.

After editing any parameter, press F5/F6 again to see the
effect before re-exporting.


# Before printing the full batch

Since I wasn't able to verify this visually, the safest approach is:

1. **Print only the lid first** (it's the cheapest and fastest part) and
   check whether the 5 potentiometer holes align with the actual
   assembled board.
2. If it fits, print the base and do a dry fit (without screwing it in)
   with the real board before finalizing/painting/screwing everything
   together.
3. Only after that, order production printing (via PCBWay or another
   3D printing service) - they accept STL files directly.

For any measurement adjustment, let me know the actual measurement you
took and I'll update the `.scad`.
