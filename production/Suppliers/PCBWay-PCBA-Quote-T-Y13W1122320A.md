# PCBWay PCBA Quotation — T-Y13W1122320A

Status: Received 2026-08-07 — reviewed against [BOM-002-AsBuilt](../../hardware/BOM/BOM-002-AsBuilt.md) and [BOM-003-SourcingLinks](../../hardware/BOM/BOM-003-SourcingLinks.md). **Verdict: covers the full assembly BOM correctly; 3 line items need clarification with PCBWay before accepting — see §4.**

Note: this is an **assembly (PCBA)** quote from PCBWay. [PCBWay-OrderGuide.md](../PCBWay-OrderGuide.md) currently tells the user to source assembly from JLCPCB instead and use PCBWay only for the bare board — if PCBWay's PCBA price/lead time here is preferred, that guide should be updated to match (not done as part of this review; flagging so it isn't forgotten).


# 1. Quotation summary

| Field | Value |
|---|---|
| Product No. | T-Y13W1122320A |
| Quantity quoted | 5 assembled boards |
| Component cost | $279.41 |
| Assembly cost | $29.00 |
| PCB cost | $94.56 |
| Discount (V0 member) | $0.00 (0%) |
| **Total (5 units)** | **$402.97** |
| Cost per board | ≈ $80.59 |
| Lead time | 27-29 days (SW2-SW5 consigned parts quoted separately at 7-10 workdays) |


# 2. Line items (as quoted)

| # | Designator | Qty/bd | Manufacturer | Mfg Part # | Package | Unit Price (×5bd) | Total | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | C1, C4, C21 | 3 | YAGEO | CC0603KRX7R9BB104 | C_0603_1608Metric | $0.059 | $0.885 | THT→SMD change, documented |
| 2 | C2, C3, C16, C19 | 4 | Honor Elec | UD2E100M1010 | CP_Radial_D5.0mm_P2.00mm | $0.289 | $5.780 | |
| 3 | C5-C15, C18 | 12 | VISHAY | K105K20X7RF5TH5 | C_Disc_D5.0mm_W2.5mm_P2.50mm | $0.909 | $54.540 | ⚠️ price outlier, see §4 |
| 4 | C17, C20 | 2 | Chengx | KM227M035F12RR0VH2FP0 | CP_Radial_D8.0mm_P3.50mm | $0.069 | $0.690 | |
| 5 | D1 | 1 | Nexperia | PTVS5V0Z1USKYL | D_SOD-323 | $0.242 | $1.210 | THT→SMD change, documented |
| 6 | D2, D3, D4, D5 | 4 | LGE | 1N4148 | D_DO-35_SOD27_P7.62mm_Horizontal | $0.032 | $0.640 | |
| 7 | F1 | 1 | Bourns | MF-RG500 | Fuse_Bourns_MF-RG500 | $1.892 | $9.460 | ⚠️ price outlier, see §4 |
| 8 | J1 | 1 | GCT | USB4085-GF-A | USB_C_Receptacle_GCT_USB4085 | $1.691 | $8.455 | ⚠️ CC pulldown note, see §4 |
| 9 | J2, J3, J4, J5, J6 | 5 | HanElectricity | PJ-320D | Jack_3.5mm_PJ320D_Horizontal | $0.062 | $1.550 | |
| 10 | K1, K2, K3, K4 | 4 | Omron | G5V-1-DC5 | Relay_SPDT_Omron_G5V-1 | $0.784 | $15.680 | |
| 11 | R1-R12 | 12 | YAGEO | CFR-25JB-52-10K | R_Axial_DIN0207... | $0.037 | $2.220 | |
| 12 | R13, R17 | 2 | YAGEO | MFR-25FBF52-100K | R_Axial_DIN0207... | $0.047 | $0.470 | |
| 13 | R14, R15, R18, R19 | 4 | CCO | CF1/4W-1KR-J | R_Axial_DIN0207... | $0.041 | $0.820 | substituted, documented |
| 14 | R16, R20 | 2 | VO | CR1/4W-47R-OT52 | R_Axial_DIN0207... | $0.075 | $0.750 | |
| 15 | RV1-RV4 | 4 | Alps Alpine | RK09712200HA | Potentiometer_Alps_RK097_Dual_Horizontal | $4.328 | $86.560 | mounted vertical (0°) |
| 16 | RV5 | 1 | Alps Alpine | RK09712200HA | Potentiometer_Alps_RK097_Dual_Horizontal | $4.328 | $21.640 | mounted horizontal (90°), front panel |
| 17 | SW1 | 1 | Omron | B3F-4005 | SW_PUSH-12mm | $0.604 | $3.020 | substituted, documented |
| 18 | SW2, SW3, SW4, SW5 | 4 | CW Industries | GPTS203211B | SW_CW_GPTS203211B | $2.970 | $59.400 | ⚠️ marked CONSIGNED, see §4 |
| 19 | U1 | 1 | HGSEMI | NE5532N | DIP-8_W7.62mm | $0.402 | $2.010 | socket recommended |
| 20 | U2 | 1 | JRC | NJM4556A | DIP-8_W7.62mm | $0.725 | $3.625 | socket recommended |


# 3. Match against the project BOM

Checked every designator, quantity, manufacturer part number, and footprint against [BOM-002-AsBuilt](../../hardware/BOM/BOM-002-AsBuilt.md) (as-designed) and [BOM-003-SourcingLinks](../../hardware/BOM/BOM-003-SourcingLinks.md) (as-sourced, 2026-08-06):

- **All 20 PCBA line items match** — same designators, quantities, LCSC codes (where applicable), and footprints as BOM-003, including the three documented 2026-08-06 substitutions (R14/15/18/19, RV1-5, SW1) and the two THT→SMD footprint changes (C1/C4/C21, D1).
- **Cost arithmetic checks out**: each `Total` = `Unit Price × Qty × 5 boards`, and the 20 line totals sum to $279.405 ≈ the quoted $279.41 component cost.
- Knobs and rubber feet (BOM-003 §"mechanical") are correctly **absent** from this quote — they aren't PCBA parts, the user sources them separately.
- SW2-SW5 correctly flagged as not sourceable through LCSC, consistent with BOM-003's own note.


# 4. Items to clarify with PCBWay before accepting

1. **SW2-SW5 consigned but priced ($59.40 total)** — the Vendor Part# column says "CONSIGNED - not on LCSC", meaning the user is expected to buy and ship these 4 switches to PCBWay directly (as BOM-003 also states). A consigned part shouldn't carry a per-unit *component* price from the assembler — ask PCBWay whether $2.970/unit is a **handling/placement fee** for consigned parts (common, and fine if so) or an accidental component charge for parts they don't actually source. This is 21% of the component-cost line and worth a direct answer before paying.
2. **1uF THT ceramic disc capacitor (item 3) at $0.909/unit** — high for a basic leaded ceramic cap; typical LCSC pricing for this class of part is a fraction of that even in small quantities. Worth a quick check against LCSC's own listed price for C2167638 before accepting.
3. **PTC fuse (item 7) at $1.892/unit** — same concern, this part is typically inexpensive; confirm it's not a pricing/qty entry error.
4. **Assembly cost ($29.00 for 5 boards, ~$5.80/board)** — this board is mostly THT (hand-placed, not reflow) with 75 components including 5 potentiometers, 4 relays, and 2 socketed DIP-8s. Confirm this figure genuinely includes full THT hand-soldering labor for all 5 boards, not just a base SMT setup fee — [PCBWay-OrderGuide.md](../PCBWay-OrderGuide.md) already flags that mixed THT+SMD assembly "adds cost/lead time compared to a pure-SMD board."
5. **J1 USB-C CC pulldown note is a real design gap, not just a quote caveat.** PCBWay's own note on item 8 ("some USB-C-to-C chargers may not enable VBUS without CC pulldown") matches what's in the schematic: [BOM-002-AsBuilt §4](../../hardware/BOM/BOM-002-AsBuilt.md) confirms J1's CC1/CC2 pins are explicitly marked "no connect" during the ERC cleanup — there are no 5.1kΩ pulldown resistors on CC1/CC2 anywhere in the design. As built, the board will power up reliably from USB-A-to-C cables/chargers (which supply 5V unconditionally) but **may fail to power up from a compliant USB-C-to-C source** (e.g. a laptop's own USB-C port, or a USB-C PD charger) that waits for CC-based sink detection before enabling VBUS. Not a PCBWay issue to fix — a schematic/BOM change (2× 5.1kΩ 1% resistors from CC1/CC2 to GND) would need to go through a new PCB revision if C-to-C compatibility matters.


# 5. Verdict

The quote **matches the project's as-built BOM line-for-line** and the totals are internally consistent — no missing or extra parts, no designator/footprint mismatches. It's reasonable to proceed on that basis, but get written clarification on the 3 pricing/consignment questions in §4.1-4.3 before paying, and treat §4.5 (USB-C CC pulldowns) as a known compatibility limitation of the current hardware revision, independent of this order.
