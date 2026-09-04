#!/usr/bin/env python3
"""Generate the v1-standard BOMs (simple + PCBA) and the JLCPCB CPL for
MeetingHub-4 v3.  English only (see project memory)."""
import re, csv, collections, pcbnew

PRJ  = "/home/fac/MeetingHub-4/v3"
NAME = "MeetingHub-4-v3"
PCB  = f"{PRJ}/hardware/KiCad/{NAME}/{NAME}.kicad_pcb"
NET  = "/tmp/v3.net"
if not __import__("os").path.exists(NET):
    NET = f"{PRJ}/hardware/PCB/{NAME}.net"        # committed copy (fab.py keeps it current)

# value -> (package, mfr, mpn, lcsc, description)   -- codes carried over from v2
DB = {
 '100nF': ('C_Disc_D5.0mm_P5.00mm', 'Vishay', 'K104K15X7RF5TH5', 'C2167231',
           '100nF 50V X7R radial ceramic, THT 5mm pitch'),
 '1uF':   ('C_Disc_D5.0mm_P2.50mm', 'Vishay', 'K105K20X7RF5TH5', 'C2167638',
           '1uF X7R ceramic capacitor, THT disc (POR timing)'),
 '10uF':  ('CP_Radial_D5.0mm_P2.00mm', 'CX', 'KM106M016D11RR0VH2FP0', 'C43799',
           '10uF 16V aluminium electrolytic, THT radial'),
 '47uF':  ('CP_Radial_D5.0mm_P2.00mm', 'Chengx', 'KM476M016C11RR0VH3FP0', 'C177036',
           '47uF 16V aluminium electrolytic, THT radial D5 (relay-coil bulk) - verify exact code'),
 'P6KE6.8A (TVS 5V uni)': ('D_DO-15_P3.81mm', 'BORN', 'P6KE6.8A', 'C152132',
           'P6KE6.8A 600W unidirectional TVS diode, DO-15 THT (USB VBUS clamp), mounted vertically'),
 '1N4148': ('D_DO-35_P2.54mm', 'LGE', '1N4148', 'C402212',
           '1N4148 small-signal switching diode, DO-35 THT, mounted vertically'),
 '2N7000': ('TO-92_Inline', 'onsemi', '2N7000', 'C9114',
           '2N7000 N-channel logic-level MOSFET, TO-92 (relay-coil driver)'),
 'CD4043B': ('DIP-16_W7.62mm', 'lingxingic', 'CD4043BE', 'C22390239',
           'CD4043B CMOS quad NOR R/S latch, DIP-16 (one-hot mic selector)'),
 '500mA': ('Fuse_Bourns_MF-RG500', 'Littelfuse', 'RXEF050', 'C76399',
           'RXEF050 resettable PTC fuse, 500mA hold, 5.1mm radial'),
 '5k1':   ('R_Axial_DIN0207_P2.54mm_Vertical', 'UNI-ROYAL', 'CFR0W4J0512A50', 'C22962',
           '5.1k 1/4W axial resistor, THT, mounted vertically (USB-C CC pull-down) - verify code'),
 '1k':    ('R_Axial_DIN0207_P2.54mm_Vertical', 'CCO', 'CF1/4W-1KR-J', 'C120055',
           '1k 1/4W axial resistor, THT, mounted vertically (MOSFET gate series)'),
 '2k2':   ('R_Axial_DIN0207_P2.54mm_Vertical', 'UNI-ROYAL', 'CFR0W4J0222A50', 'C22975',
           '2.2k 1/4W axial resistor, THT, mounted vertically (relay NC bias -> keeps a '
           'de-selected notebook seeing ~1.1 V, not open-circuit) - verify code'),
 '100k':  ('R_Axial_DIN0207_P2.54mm_Vertical', 'Yageo', 'MFR-25FBF52-100K', 'C1364475',
           '100k 1/4W axial resistor, THT, mounted vertically (pull-downs / POR)'),
 'USB-C 5V IN': ('USB_C_Receptacle_GCT_USB4085', 'GCT', 'USB4085-GF-A', 'C7095263',
           'USB Type-C receptacle, power only (VBUS/GND/CC)'),
}
JACK  = ('Jack_3.5mm_3pole_THT_Horizontal', 'SHOU HAN', 'PJ-320A-3P DIP', 'C17701689',
         'P2 (3.5 mm) 3-conductor audio jack, right-angle THROUGH-HOLE. Datasheet terminals: '
         'pin 3 = tip (mic), pins 2 & 4 = ring/sleeve (both to GND). Local footprint from the '
         'LCSC/EasyEDA C17701689 pad data + datasheet. Bring-up: confirm pin 3 is the tip contact.')
RELAY = ('Relay_SPDT_Omron_G5V-1', 'Omron', 'G5V-1-DC5', 'C28695',
         'SPDT signal relay, 5VDC coil (mic routing)')
BTN   = ('SW_Tactile_SPST_Angled_PTS645Vx39-2LFS', 'C&K', 'PTS645VK392LFS', 'C285519',
         '6mm right-angle (horizontal) momentary tact pushbutton, THT (select buttons)')
for k in ('Mic NB1', 'Mic NB2', 'Mic NB3', 'Mic NB4', 'Headset MIC'): DB[k] = JACK
for k in ('Route NB1', 'Route NB2', 'Route NB3', 'Route NB4'):        DB[k] = RELAY
for k in ('Select NB1', 'Select NB2', 'Select NB3', 'Select NB4'):    DB[k] = BTN

t = open(NET).read()
comp = {m.group(1): (m.group(2), m.group(3).split(':')[-1])
        for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)\s*\(footprint "([^"]*)"\)', t)}
comp['TP1'] = ('+5V', 'TestPoint_THTPad_D1.5mm')
comp['TP2'] = ('GND', 'TestPoint_THTPad_D1.5mm')
for i in range(1, 5): comp[f'MH{i}'] = ('M3 mounting hole', 'MountingHole_3.2mm_M3')

def rk(r):
    m = re.match(r'([A-Za-z]+)(\d+)', r); return (m.group(1), int(m.group(2)))

# BOM 1: simple
g = collections.defaultdict(list)
for r, (v, fp) in comp.items(): g[(v, fp)].append(r)
rows = [[', '.join(sorted(rs, key=rk)), len(rs), v, fp] for (v, fp), rs in g.items()]
rows.sort(key=lambda x: rk(x[0].split(',')[0]))
with open(f"{PRJ}/hardware/BOM/BOM-{NAME}.csv", "w", newline='') as f:
    w = csv.writer(f); w.writerow(['Designators', 'Quantity', 'Value', 'Footprint']); w.writerows(rows)

# BOM 2: PCBA
fitted = {r: vf for r, vf in comp.items() if not r.startswith(('MH', 'TP'))}
g2 = collections.defaultdict(list); meta = {}
for r, (v, fp) in fitted.items():
    pkg, mfr, mpn, lcsc, desc = DB.get(v, ('', '', '', '', v))
    key = (desc, pkg, mfr, mpn, lcsc); g2[key].append(r); meta[key] = (pkg, mfr, mpn, lcsc, desc)
prows = []
for key, rs in g2.items():
    pkg, mfr, mpn, lcsc, desc = meta[key]
    prows.append([', '.join(sorted(rs, key=rk)), len(rs), desc, pkg, mfr, mpn, lcsc, ''])
prows.sort(key=lambda x: rk(x[0].split(',')[0]))
with open(f"{PRJ}/hardware/BOM/BOM-PCBA-{NAME}.csv", "w", newline='') as f:
    w = csv.writer(f)
    w.writerow(['Item', 'Designator', 'Qty', 'Value/Description', 'Package',
                'Manufacturer', 'Manufacturer Part Number', 'JLCPCB Part #', 'Notes'])
    for i, r in enumerate(prows, 1): w.writerow([i] + r)

# BOM 3: JLCPCB native
with open(f"{PRJ}/hardware/BOM/BOM-JLC-{NAME}.csv", "w", newline='') as f:
    w = csv.writer(f); w.writerow(['Comment', 'Designator', 'Footprint', 'JLCPCB Part #'])
    for rs_join, qty, desc, pkg, mfr, mpn, lcsc, _ in prows:
        w.writerow([mpn or desc, rs_join, pkg, lcsc])

# CPL (JLCPCB)
FP_ROT_OFFSET = {
    'DIP-16_W7.62mm': 270,
    'Relay_SPDT_Omron_G5V-1': 270,
    'SW_Tactile_SPST_Angled_PTS645Vx39-2LFS': 180,
    'TO-92_Inline': 180,
}
b = pcbnew.LoadBoard(PCB)
cpl = []
for f in b.GetFootprints():
    ref = f.GetReference()
    if ref.startswith(('MH', 'TP')): continue
    p = f.GetPosition()
    layer = 'Top' if f.GetLayer() == pcbnew.F_Cu else 'Bottom'
    fpname = f.GetFPIDAsString().split(':')[-1]
    rot = (f.GetOrientationDegrees() - FP_ROT_OFFSET.get(fpname, 0)) % 360
    cpl.append([ref, f"{pcbnew.ToMM(p.x):.4f}", f"{-pcbnew.ToMM(p.y):.4f}", layer, f"{rot:.4f}"])
cpl.sort(key=lambda x: rk(x[0]))
with open(f"{PRJ}/hardware/Gerbers/{NAME}-CPL.csv", "w", newline='') as f:
    w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation']); w.writerows(cpl)

print(f"BOM simple {len(rows)} lines | PCBA {len(prows)} lines / {sum(r[1] for r in prows)} parts | CPL {len(cpl)}")
