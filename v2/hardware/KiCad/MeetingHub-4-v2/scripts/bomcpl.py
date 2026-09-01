#!/usr/bin/env python3
"""Generate v1-standard BOM (simple + PCBA) and JLCPCB CPL for a MeetingHub-4 variant."""
import sys, re, csv, collections, pcbnew

PRJ  = sys.argv[1] if len(sys.argv) > 1 else "/home/fac/MeetingHub-4/v2"
NAME = sys.argv[2] if len(sys.argv) > 2 else "MeetingHub-4-v2"
PCB  = f"{PRJ}/hardware/KiCad/{NAME}/{NAME}.kicad_pcb"
NET  = f"{PRJ}/hardware/PCB/{NAME}.net"

# ---- part database: value -> (pkg, mfr, mpn, lcsc, desc) --------------------
DB = {
 '100nF': ('C_Disc_D5.0mm_P5.00mm','multicomp','MCCA000175','C49678','100nF ceramic capacitor, THT disc'),
 '1uF':   ('C_Disc_D5.0mm_P2.50mm','Vishay','K105K20X7RF5TH5','C2167638','1uF X7R ceramic capacitor, THT disc'),
 '10uF':  ('CP_Radial_D5.0mm_P2.00mm','CX','KM106M016D11RR0VH2FP0','C43799','10uF 16V aluminium electrolytic, THT radial'),
 '220uF': ('CP_Radial_D8.0mm_P3.50mm','Chengx','KM227M035F12RR0VH2FP0','C2063','220uF 16V aluminium electrolytic, THT radial'),
 '100uF': ('CP_Radial_D6.3mm_P2.50mm','Chengx','KM108M016D6R3RR0VH2FP0','C2909340','100uF 16V aluminium electrolytic, THT radial'),
 'P6KE6.8A (TVS 5V uni)': ('D_DO-15_P10.16mm','MDD','P6KE6.8A','C736020','P6KE6.8A 600W unidirectional TVS diode, DO-15 THT (USB VBUS clamp)'),
 '1N4148': ('D_DO-35_P7.62mm','LGE','1N4148','C402212','1N4148 small-signal switching diode, DO-35 THT'),
 '2N7000': ('TO-92_Inline','onsemi','2N7000','C9114','2N7000 N-channel logic-level MOSFET, TO-92'),
 'CD4043B':('DIP-16_W7.62mm','Texas Instruments','CD4043BE','C39537','CD4043B CMOS quad NOR R/S latch, DIP-16'),
 'LM358':  ('DIP-8_W7.62mm','onsemi','LM358P','C7950','LM358 dual op-amp (single-supply), DIP-8 (VBIAS buffer)'),
 'NJM4580':('DIP-8_W7.62mm','Nisshinbo (JRC)','NJM4580D','C7466','NJM4580 dual audio op-amp, DIP-8 (4-input mixer)'),
 'NJM4556A':('DIP-8_W7.62mm','Nisshinbo (JRC)','NJM4556AD','C2838125','NJM4556A dual high-current op-amp 70mA, DIP-8 (headphone driver)'),
 '500mA':  ('Fuse_Bourns_MF-RG500','Bourns','MF-RG500','C1562150','MF-RG500 resettable PTC fuse, 500mA hold'),
 '10k':    ('R_Axial_DIN0207_P10.16mm','Yageo','CFR-25JB-52-10K','C5618323','10k 1/4W axial resistor, THT'),
 '3k3':    ('R_Axial_DIN0207_P10.16mm','Yageo','CFR-25JB-52-3K3','C22978','3k3 1/4W axial resistor, THT (mixer feedback)'),
 '1k':     ('R_Axial_DIN0207_P10.16mm','CCO','CF1/4W-1KR-J','C120055','1k 1/4W axial resistor, THT'),
 '100k':   ('R_Axial_DIN0207_P10.16mm','Yageo','MFR-25FBF52-100K','C1364475','100k 1/4W axial resistor, THT'),
 '47':     ('R_Axial_DIN0207_P10.16mm','VO','CR1/4W-47R-OT52','C2896824','47R 1/4W axial resistor, THT'),
 '47R':    ('R_Axial_DIN0207_P10.16mm','VO','CR1/4W-47R-OT52','C2896824','47R 1/4W axial resistor, THT (VBIAS buffer isolation)'),
 'USB-C POWER IN': ('USB_C_Receptacle_GCT_USB4085','GCT','USB4085-GF-A','C7095263','USB Type-C receptacle, power only (VBUS/GND)'),
}
POT  = ('Potentiometer_Alps_RK097_Dual_Horizontal','Alps Alpine','RK09712200HA','C470545',
        '10k dual audio-taper potentiometer, horizontal PCB mount')
JACK = ('Jack_3.5mm_PJ320E_Horizontal','Korean Hroparts','PJ-320E','C2939642',
        '3.5mm TRRS jack, 100% through-hole (PJ-320E)')
RELAY= ('Relay_SPDT_Omron_G5V-1','Omron','G5V-1-DC5','C28695','SPDT signal relay, 5VDC coil')
BTN  = ('SW_PUSH_6mm','generic','6x6mm tact','C318884','6mm momentary tact pushbutton, THT')
for k in ('10k Vol NB1','10k Vol NB2','10k Vol NB3','10k Vol NB4','10k Master'): DB[k]=POT
for k in ('TRRS Notebook 1','TRRS Notebook 2','TRRS Notebook 3','TRRS Notebook 4','Headset (User)'): DB[k]=JACK
for k in ('Select NB1','Select NB2','Select NB3','Select NB4'): DB[k]=RELAY
for i in (1,2,3,4): DB[f'Select NB{i} (momentary)']=BTN

# ---- read netlist for value/footprint per ref --------------------------------
t = open(NET).read()
comp = {m.group(1): (m.group(2), m.group(3).split(':')[-1])
        for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)\s*\(footprint "([^"]*)"\)', t)}
comp['TP1'] = ('+5V_AUDIO', 'TestPoint_THTPad_D1.5mm')
comp['TP2'] = ('GND', 'TestPoint_THTPad_D1.5mm')
for i in range(1, 7): comp[f'MH{i}'] = ('M3 mounting hole', 'MountingHole_3.2mm_M3')

def rk(r):
    m = re.match(r'([A-Za-z]+)(\d+)', r); return (m.group(1), int(m.group(2)))

# ---- BOM 1: simple (Designators, Quantity, Value, Footprint) -----------------
g = collections.defaultdict(list)
for r, (v, fp) in comp.items():
    g[(v, fp)].append(r)
rows = []
for (v, fp), rs in g.items():
    rs = sorted(rs, key=rk)
    rows.append([', '.join(rs), len(rs), v, fp])
rows.sort(key=lambda x: rk(x[0].split(',')[0]))
with open(f"{PRJ}/hardware/BOM/BOM-{NAME}.csv", "w", newline='') as f:
    w = csv.writer(f); w.writerow(['Designators', 'Quantity', 'Value', 'Footprint'])
    w.writerows(rows)

# ---- BOM 2: PCBA (Item, Designator, Qty, Value/Description, Package, Mfr, MPN, LCSC, Notes)
fitted = {r: vf for r, vf in comp.items() if not r.startswith(('MH', 'TP'))}
g2 = collections.defaultdict(list)
for r, (v, fp) in fitted.items():
    g2[v].append(r)
prows = []
for v, rs in g2.items():
    rs = sorted(rs, key=rk)
    pkg, mfr, mpn, lcsc, desc = DB.get(v, ('', '', '', '', v))
    prows.append([', '.join(rs), len(rs), desc, pkg, mfr, mpn, lcsc, ''])
prows.sort(key=lambda x: rk(x[0].split(',')[0]))
with open(f"{PRJ}/hardware/BOM/BOM-PCBA-{NAME}.csv", "w", newline='') as f:
    w = csv.writer(f)
    w.writerow(['Item', 'Designator', 'Qty', 'Value/Description', 'Package',
                'Manufacturer', 'Manufacturer Part Number', 'LCSC', 'Notes'])
    for i, r in enumerate(prows, 1):
        w.writerow([i] + r)

# ---- CPL (JLCPCB): Designator, Mid X, Mid Y, Layer, Rotation -----------------
b = pcbnew.LoadBoard(PCB)
cpl = []
for f in b.GetFootprints():
    ref = f.GetReference()
    if ref.startswith(('MH', 'TP')):
        continue
    p = f.GetPosition()
    layer = 'Top' if f.GetLayer() == pcbnew.F_Cu else 'Bottom'
    cpl.append([ref, f"{pcbnew.ToMM(p.x):.4f}", f"{-pcbnew.ToMM(p.y):.4f}",
                layer, f"{f.GetOrientationDegrees():.4f}"])
cpl.sort(key=lambda x: rk(x[0]))
with open(f"{PRJ}/hardware/Gerbers/{NAME}-CPL.csv", "w", newline='') as f:
    w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    w.writerows(cpl)

print(f"BOM simple: {len(rows)} lines")
print(f"BOM PCBA  : {len(prows)} lines, {sum(r[1] for r in prows)} parts")
print(f"CPL       : {len(cpl)} placements")
