# PCBWay Guide - How to Order Board Manufacturing (for beginners)

Version: 4.0
Status: Final — updated 2026-08-06, SW2-SW5 (front-panel selector
switches) rotated 90° to lie horizontal, re-routed
(DRC-clean: 0 clearance errors, 0 unconnected pads, verified in KiCad)

Step-by-step guide for ordering **bare PCB manufacturing** for the
MeetingHub-4 at PCBWay (pcbway.com), written for someone who has never
done this before. **Assembly (PCBA) is a separate vendor, JLCPCB —
see step 6.** The
technical values below (size, layers, thickness) are the **real** values
extracted from the final project - use them to check whether the site
detected everything correctly, no need to know what they mean to follow
the guide.

**File to upload**: [`hardware/Gerbers/MeetingHub-4-Gerbers-v4.0.zip`](../hardware/Gerbers/MeetingHub-4-Gerbers-v4.0.zip)
(already contains gerbers for all layers + drilling, ready for upload).
**Do not use v1.0, v2.0 or v3.0** — v1.0/v2.0 reflect an older
265.1x160.1mm board revision that no longer exists; v3.0 has SW2-SW5
in the old vertical orientation, superseded by this horizontal layout.


# Board technical specifications (to check against what the site detects)

| Item | Value |
|---|---|
| Dimensions | 160.19 x 134.06 mm |
| Layers | **4** |
| Final thickness | 1.6 mm |
| Material | FR-4 (standard) |
| Minimum hole | 0.6 mm (within standard, no special option needed) |
| Solder mask color | your choice (green is the cheapest/fastest standard) |
| Silkscreen color | white (standard) |
| Surface finish | HASL (with lead) recommended - cheaper; the board is mostly THT with a handful of SMD passives (see note below), HASL still works fine for both |
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
Gerber"). Upload the file `MeetingHub-4-Gerbers-v3.0.zip` (no need to
unzip it, the site accepts the zip directly).

PCBWay tries to automatically detect the size and number of layers from
the file. **Check**:
- **Dimension**: should show something close to `160.19 x 134.06 mm`. If
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

**Assembly is not done through PCBWay for this project — use
[JLCPCB](https://jlcpcb.com) instead.** PCBWay in this guide is only
for the bare board (steps 1-5, 7-9 above). JLCPCB has direct
integration with the LCSC parts catalog, which is what
[BOM-003-SourcingLinks](../hardware/BOM/BOM-003-SourcingLinks.md)'s
LCSC codes are for — pick JLCPCB's own **"PCB Assembly"** flow at
jlcpcb.com, upload the gerbers there too (JLCPCB will also fabricate
the bare board as part of that flow, so this becomes a single order
instead of two separate ones with two vendors).

**Important note**: this project is **mostly THT**, with a small
number of SMD parts (C1/C4/C21, D1 — no THT stock exists for those 2
specific values at any supplier; J2-J6 also has SMD signal pads on an
otherwise THT jack). JLCPCB does handle mixed THT+SMD assembly, but
THT parts are placed by hand (not reflow) and add cost/lead time
compared to a pure-SMD board — confirm the quote reflects this before
paying.

Files you'll need to upload for the assembly quote (in addition to the
gerber zip from step 3, uploaded to JLCPCB instead of PCBWay):

- **[`hardware/BOM/BOM-PCBA-MeetingHub-4.csv`](../hardware/BOM/BOM-PCBA-MeetingHub-4.csv)**
  - bill of materials with manufacturer/part number, in the format
    assembly services usually request.
- **[`hardware/Gerbers/MeetingHub-4-Placement.csv`](../hardware/Gerbers/MeetingHub-4-Placement.csv)**
  - X/Y/rotation position of each component on the board (the
    "Component Placement" / "Pick and Place" file, required even for
    THT).

**This section is superseded** by
[BOM-003-SourcingLinks](../hardware/BOM/BOM-003-SourcingLinks.md) — a
straight shopping-list table (component, code, link, quantity) for
everything needed. All parts are confirmed in stock at LCSC as of
2026-08-06, with one exception:
- **SW2-SW5** (selector switches): the original CW Industries
  GPTS203211B is out of stock at LCSC with no in-stock pin-compatible
  equivalent found — buy 4 units separately (DigiKey CW181-ND or CW
  Industries direct) and consign them to the assembler.

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
