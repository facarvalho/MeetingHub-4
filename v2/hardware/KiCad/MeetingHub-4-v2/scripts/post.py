#!/usr/bin/env python3
"""Post-process after ses_import: 0.15mm clearance, solid GND pads, silk tidy."""
import pcbnew, re, json, collections

PCB = "/home/fac/MeetingHub-4/v2/hardware/KiCad/MeetingHub-4-v2/MeetingHub-4-v2.kicad_pcb"
PRO = "/home/fac/MeetingHub-4/v2/hardware/KiCad/MeetingHub-4-v2/MeetingHub-4-v2.kicad_pro"
EDGE_FP = set("J2 J3 J4 J5 J6 RV1 RV2 RV3 RV4 RV5".split())

# --- zone connect_pads -> solid (text) ---
s = open(PCB).read()
s = s.replace('(connect_pads (clearance 0.3))', '(connect_pads yes (clearance 0.25))')
open(PCB, "w").write(s)

b = pcbnew.LoadBoard(PCB)

# --- netclass clearance 0.15 (matches v1) ---
ds = b.GetDesignSettings()
try:
    ns = b.GetAllNetClasses() if hasattr(b, "GetAllNetClasses") else None
except Exception:
    ns = None
for nc in [b.GetDesignSettings().GetDefault()] if hasattr(b.GetDesignSettings(),"GetDefault") else []:
    nc.SetClearance(pcbnew.FromMM(0.15))
try:
    b.GetDesignSettings().m_MinClearance = pcbnew.FromMM(0.15)
except Exception as e: print("minclr warn",e)

# --- shrink all reference text to 0.8mm; hide the F.Fab value (= footprint name,
#     KiCad-script default) so it doesn't clutter assembly renders ---
for f in b.GetFootprints():
    r = f.Reference()
    r.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
    r.SetTextThickness(pcbnew.FromMM(0.12))
    f.Value().SetVisible(False)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)

# --- hide any reference still causing silk_overlap ---
sev = json.load(open(PRO))['board']['design_settings']['rule_severities']
pcbnew.WriteDRCReport(b, "/tmp/p.rpt", pcbnew.EDA_UNITS_MILLIMETRES, True)
t = open("/tmp/p.rpt").read()
ov = set(re.findall(r"silk_overlap[\s\S]*?Reference '([^']+)'", t))
ov |= set(re.findall(r"silk_overlap[\s\S]*?@\([^)]*\): Reference '([^']+)'", t))
if ov:
    b = pcbnew.LoadBoard(PCB)
    for f in b.GetFootprints():
        if f.GetReference() in ov:
            f.Reference().SetVisible(False)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)
    print("hid silk ref on:", sorted(ov))

# --- restore .kicad_pro (SaveBoard wipes sheets) ---
d = json.load(open(PRO))
d['sheets'] = [["8b7deae6-c6d2-463d-9623-40608a842bd8", ""],
               ["7adc5442-2532-4675-a48f-0351bbf6b21b", "POWER"],
               ["1a2b3c4d-0001-4a1a-8a1a-000000000001", "TRRS_INPUTS"],
               ["1a2b3c4d-0002-4a1a-8a1a-000000000002", "AUDIO_MIXER"],
               ["1a2b3c4d-0003-4a1a-8a1a-000000000003", "HEADPHONE_AMP"],
               ["1a2b3c4d-0004-4a1a-8a1a-000000000004", "MIC_SWITCHING"],
               ["1a2b3c4d-0005-4a1a-8a1a-000000000005", "SELECT_LOGIC"]]
r = d['board']['design_settings']['rules']
r['min_copper_edge_clearance'] = 0.3
r['min_track_width'] = 0.2
r['min_via_diameter'] = 0.6
r['min_clearance'] = 0.15
d['net_settings']['classes'][0]['clearance'] = 0.15
json.dump(d, open(PRO, "w"), indent=2)

# --- final DRC by project severity ---
b = pcbnew.LoadBoard(PCB)
pcbnew.WriteDRCReport(b, PCB.replace("MeetingHub-4-v2.kicad_pcb", "DRC.rpt"),
                      pcbnew.EDA_UNITS_MILLIMETRES, True)
t = open(PCB.replace("MeetingHub-4-v2.kicad_pcb", "DRC.rpt")).read()
it = collections.Counter(re.findall(r'\[([a-z_]+)\]', t))
err = {k: v for k, v in it.items() if sev.get(k, 'error') == 'error'}
war = {k: v for k, v in it.items() if sev.get(k, 'error') == 'warning'}
print("ERRORS  :", err or "NONE")
print("warnings:", war or "NONE")
print(re.search(r'\*\* Found \d+ unconnected pads \*\*', t).group(0))
smd = [f.GetReference() for f in b.GetFootprints()
       for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
print("SMD pads:", set(smd) or "NONE - 100% THT")
