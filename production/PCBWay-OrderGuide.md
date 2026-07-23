# PCBWay Guide - How to Order Board Manufacturing (for beginners)

Version: 1.0
Status: Final

Step-by-step guide for ordering PCB manufacturing for the MeetingHub-4 at
PCBWay (pcbway.com), written for someone who has never done this before. The
technical values below (size, layers, thickness) are the **real** values
extracted from the final project - use them to check whether the site
detected everything correctly, no need to know what they mean to follow
the guide.

**File to upload**: [`hardware/Gerbers/MeetingHub-4-Gerbers-v1.0.zip`](../hardware/Gerbers/MeetingHub-4-Gerbers-v1.0.zip)
(already contains gerbers for all layers + drilling, ready for upload).


# Board technical specifications (to check against what the site detects)

| Item | Value |
|---|---|
| Dimensions | 265.1 x 160.1 mm |
| Layers | **4** |
| Final thickness | 1.6 mm |
| Material | FR-4 (standard) |
| Minimum hole | 0.6 mm (within standard, no special option needed) |
| Solder mask color | your choice (green is the cheapest/fastest standard) |
| Silkscreen color | white (standard) |
| Surface finish | HASL (with lead) recommended - cheaper, and the board is 100% THT (manual soldering), no need for ENIG |
| Copper weight | 1oz (standard) |
| Suggested quantity | 5 units (PCBWay's common minimum for a prototype; leaves spare boards in case of an assembly error) |


# Step by step

## 1. Create an account

Go to [pcbway.com](https://www.pcbway.com) and create an account (email +
password, or login via Google). No company registration (CNPJ) or business
info needed - a personal account works.

## 2. Open the PCB instant quote

In the top menu, look for **"PCB Instant Quote"** (or "Quote Now" on the
home page, PCB section). This opens the board configuration form.

## 3. Upload the gerber file

In the form, there's a button labeled **"Add Gerber File"** (or "Upload
Gerber"). Upload the file `MeetingHub-4-Gerbers-v1.0.zip` (no need to
unzip it, the site accepts the zip directly).

PCBWay tries to automatically detect the size and number of layers from
the file. **Check**:
- **Dimension**: should show something close to `265.1 x 160.1 mm`. If
  it shows a very different value, the upload probably failed -
  try re-uploading before continuing.
- **Layer**: should be set to **4**. If it shows 2, the site didn't read
  the inner layers correctly - do not proceed, let me know.

If for some reason the site doesn't detect it automatically, fill it in
manually using the values from the table above.

## 4. Review/adjust the manufacturing options

On the same screen (or in the "Specification" tab), check each field
against the technical table above. The most important fields:

- **Layers**: 4
- **Material**: FR-4
- **Thickness**: 1.6mm
- **Min Track/Spacing**: you can leave the site's default (6/6mil) - the
  project doesn't use anything finer than that.
- **Min Hole Size**: you can leave the default (0.3mm) - the smallest
  hole in the project is 0.6mm, well within range.
- **Solder Mask**: choose whichever color you prefer (green is the
  standard, cheapest and fastest; other colors may cost a bit more/take
  a bit longer).
- **Silkscreen**: white (standard).
- **Surface Finish**: **HASL(with lead)** - cheaper, works well
  for manual soldering (which is how this prototype was designed to be
  assembled, with sockets for ICs U1/U2).
- **Via Process**: **Tenting vias** (default, cheaper).
- **Board Outline Tolerance**: you can leave it at default.
- Everything else (Panelization, Castellated Holes, Edge Plating,
  etc.): **don't check any extra option** - this project doesn't need
  any of them.

## 5. Quantity

Choose the quantity (suggestion: **5 units** - it's PCBWay's common
minimum for this size range, and it's good to have spare boards in case
something goes wrong during the first assembly/soldering).

## 6. Assembly (PCBA) - if you want the board pre-assembled

If you don't want to hand-solder the 75 components, PCBWay can
assemble the board for you (the **PCBA - "Assembly"** service, paid
separately, in addition to bare board manufacturing).

**Important note**: this project is **100% THT** (no SMD
components) - PCBWay's automatic quoting flow is designed primarily
for SMD assembly (reflow). THT assembly (wave/manual soldering) usually
does **not** get an instant quote - it typically requires opening a
manual quote request or contacting PCBWay support/sales after
uploading the files, instead of simply clicking "Add to Cart". Lead
time and cost tend to be higher than an equivalent SMD assembly. Confirm
this directly with PCBWay before assuming it will be as automatic as
ordering the bare board.

Files you'll need to upload for the assembly quote (in addition to the
gerber zip from step 3):

- **[`hardware/BOM/BOM-PCBA-MeetingHub-4.csv`](../hardware/BOM/BOM-PCBA-MeetingHub-4.csv)**
  - bill of materials with manufacturer/part number, in the format
    assembly services usually request.
- **[`hardware/Gerbers/MeetingHub-4-Placement.csv`](../hardware/Gerbers/MeetingHub-4-Placement.csv)**
  - X/Y/rotation position of each component on the board (the
    "Component Placement" / "Pick and Place" file, required even for
    THT).

**Before uploading, read the "Confidence" column of the BOM-PCBA**: most
components have a real, confirmed part number, but **3 items need your
confirmation before buying in quantity**:
- **J1** (USB-C): the footprint was modeled on the GCT USB4085 family,
  but the exact part number suffix isn't confirmed in the project.
- **RV1-RV5** (potentiometers): the Alps RK097 family is confirmed, but
  the exact suffix (shaft length, shaft type, response taper) is
  not - this also affects whether the shaft reaches the enclosure hole
  (see [mechanical/README.md](../mechanical/README.md)).
- **K1-K4** (relays): the 5VDC coil voltage was **inferred** (the board
  only has one supply rail, +5V_AUDIO), it is not an explicit
  specification from any project document - confirm before buying
  in quantity.

If you're unsure about any of these 3, it's safer to buy one unit of
each first and physically confirm against the board footprint before
placing an assembly order for dozens of units.

If you'd rather assemble it yourself instead of paying for the assembly
service: the bare board alone (without this service) is sufficient, and
the original BOM in
[BOM-002-AsBuilt](../hardware/BOM/BOM-002-AsBuilt.md) recommends using
sockets for ICs U1/U2 to make it easier.

## 7. Add to cart and review the price

After confirming the options, click **"Add to Cart"** (or
similar) and review the final price before continuing - it changes
depending on the mask color, finish, and quantity chosen.

## 8. Payment and shipping

Choose the shipping method (PCBWay generally offers a few carrier
options with different price/lead times - the cheapest one usually
takes much longer to arrive in Brazil). Complete the payment
(international credit cards are usually accepted directly).

**Watch out for import taxes**: since it ships from outside Brazil, it
may be held at customs and charged import tax (ICMS + fees) on
delivery, depending on the declared value and the chosen carrier - this
is an import matter, not something related to PCBWay itself; if you've
never imported anything before, it's worth researching how it works
before finalizing the order (e.g., the Remessa Conforme program, if
the store is registered).

## 9. Tracking the order

PCBWay sends email updates at each stage (production, inspection,
shipping, tracking code). The standard manufacturing lead time is
usually a few business days (varies with the production queue);
international shipping tends to be the slowest part of the whole
process.


# When the board arrives

1. Visually check it against Phase 1 of [TEST-001](../docs/Architecture/TEST-001-BringUpGuide.md)
   before mounting any component (also checking whether the
   silkscreen/holes match what's expected).
2. Follow [TEST-001](../docs/Architecture/TEST-001-BringUpGuide.md) in
   order (visual inspection → continuity → first power-up → functional
   test) to assemble and validate the board safely.


# Note about this guide

The PCBWay website's interface changes from time to time (button names,
field positions). If any step doesn't exactly match what you see on
screen, **always check against the technical specifications at the top of
this document** (those values are the real ones, extracted from the
final project file) rather than the step-by-step text, and let me know
if anything looks off before finalizing the order.
