#!/usr/bin/env python3
"""Generate the flat single-sheet schematic for MeetingHub-4 v3 (mic selector only).

v3 = the v2 one-hot mic selector, nothing else:
  USB-C 5V in -> PTC -> TVS -> CD4043B quad NOR R/S latch (one-hot) driven by a
  16-diode button matrix + power-on-reset, 4x 2N7000 coil drivers, 4x G5V-1
  signal relays that route the headset mic (J6) to exactly one notebook (J2-J5).
No audio path: the user splits each notebook with a Y-cable and monitors on an
external mixer.  100% through-hole.
"""
import re, uuid, os

PRJ  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2   = "/home/fac/MeetingHub-4/v2/hardware/KiCad/MeetingHub-4-v2"
ROOT_UUID = "c3d4e5f6-0000-4c3c-8c3c-00000000000a"

# ---------------------------------------------------------------- symbol harvest
def grab(path, name):
    """Extract one top-level (symbol "name" ...) block by paren-matching."""
    s = open(path).read()
    i = s.index(f'(symbol "{name}"')
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '(': depth += 1
        elif s[j] == ')':
            depth -= 1
            if depth == 0:
                return s[i:j+1]
    raise RuntimeError(name)

SYM = {
 "Device:R":            grab(f"{V2}/SELECT_LOGIC.kicad_sch", "Device:R"),
 "Device:C":            grab(f"{V2}/SELECT_LOGIC.kicad_sch", "Device:C"),
 "Device:C_Polarized":  grab(f"{V2}/SELECT_LOGIC.kicad_sch", "Device:C_Polarized"),
 "Device:D":            grab(f"{V2}/SELECT_LOGIC.kicad_sch", "Device:D"),
 "power:GND":           grab(f"{V2}/SELECT_LOGIC.kicad_sch", "power:GND"),
 "Switch:SW_SPST":      grab(f"{V2}/SELECT_LOGIC.kicad_sch", "Switch:SW_SPST"),
 "Relay:G5V-1":         grab(f"{V2}/MICSW.kicad_sch",        "Relay:G5V-1"),
 "Device:Polyfuse":     grab(f"{V2}/POWER.kicad_sch",        "Device:Polyfuse"),
 "Diode:ZPYxx":         grab(f"{V2}/POWER.kicad_sch",        "Diode:ZPYxx"),
 "Connector:TestPoint": grab(f"{V2}/POWER.kicad_sch",        "Connector:TestPoint"),
 "power:PWR_FLAG":      grab(f"{V2}/POWER.kicad_sch",        "power:PWR_FLAG"),
 "Connector:USB_C_Receptacle_USB2.0_16P":
        grab(f"{V2}/POWER.kicad_sch", "Connector:USB_C_Receptacle_USB2.0_16P"),
}
# local lib symbols, renamed to the v3 nickname
_ks = open(f"{PRJ}/MeetingHub-4-v3.kicad_sym").read()
def kslib(name):
    i = _ks.index(f'(symbol "{name}"'); depth = 0
    for j in range(i, len(_ks)):
        if _ks[j] == '(': depth += 1
        elif _ks[j] == ')':
            depth -= 1
            if depth == 0: return _ks[i:j+1]
SYM["MeetingHub-4-v3:CD4043B"] = kslib("CD4043B").replace('(symbol "CD4043B"',
                                    '(symbol "MeetingHub-4-v3:CD4043B"', 1)
SYM["MeetingHub-4-v3:2N7000"]  = kslib("2N7000").replace('(symbol "2N7000"',
                                    '(symbol "MeetingHub-4-v3:2N7000"', 1)

# 3-pin audio-jack symbol for the HX PJ-320A-3P DIP (LCSC C17701689).
# Datasheet terminal numbers: 3 = TIP (mic), 2 & 4 = ring / sleeve (-> GND).
SYM["MeetingHub-4-v3:Jack3"] = r'''(symbol "MeetingHub-4-v3:Jack3" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Jack3" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "ki_description" "PJ-320A-3P DIP 3.5mm 3-conductor audio jack (pin 3 = tip)" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "Jack3_0_1"
      (rectangle (start -3.81 3.81) (end 3.81 -3.81) (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "Jack3_1_1"
      (pin passive line (at -6.35 2.54 0) (length 2.54) (name "TIP" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
      (pin passive line (at -6.35 0 0) (length 2.54) (name "R_S" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      (pin passive line (at -6.35 -2.54 0) (length 2.54) (name "R_S" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
    )
  )'''

# ---------------------------------------------------------------- pin geometry
# (rx, ry, (out_x, out_y))   ry positive = up in symbol space
R_PINS  = {"1":(0,3.81,(0,1)), "2":(0,-3.81,(0,-1))}
C_PINS  = {"1":(0,3.81,(0,1)), "2":(0,-3.81,(0,-1))}
D_PINS  = {"1":(-3.81,0,(-1,0)), "2":(3.81,0,(1,0))}          # 1=K 2=A
Q_PINS  = {"1":(2.54,-5.08,(0,-1)), "2":(-5.08,0,(-1,0)), "3":(2.54,5.08,(0,1))}  # S G D
SW_PINS = {"1":(-5.08,0,(-1,0)), "2":(5.08,0,(1,0))}
GND_PINS= {"1":(0,0,(0,-1))}
FLG_PINS= {"1":(0,0,(0,1))}
TP_PINS = {"1":(0,0,(0,-1))}
K_PINS  = {"1":(2.54,7.62,(0,1)), "10":(7.62,7.62,(0,1)), "2":(-5.08,7.62,(0,1)),
           "5":(5.08,-7.62,(0,-1)), "6":(5.08,-7.62,(0,-1)), "9":(-5.08,-7.62,(0,-1))}
J3_PINS = {"3":(-6.35,2.54,(-1,0)), "2":(-6.35,0,(-1,0)), "4":(-6.35,-2.54,(-1,0))}  # 3=tip 2/4=ring&sleeve
CD_PINS = {
 "16":(0,30.48,(0,1)), "8":(0,-30.48,(0,-1)),
 "4":(-17.78,20.32,(-1,0)), "3":(-17.78,15.24,(-1,0)),
 "6":(-17.78,10.16,(-1,0)), "7":(-17.78,5.08,(-1,0)),
 "12":(-17.78,-2.54,(-1,0)),"11":(-17.78,-7.62,(-1,0)),
 "14":(-17.78,-12.7,(-1,0)),"15":(-17.78,-17.78,(-1,0)),
 "5":(-17.78,-22.86,(-1,0)),
 "2":(17.78,20.32,(1,0)), "9":(17.78,12.7,(1,0)),
 "10":(17.78,5.08,(1,0)), "1":(17.78,-2.54,(1,0)),
 "13":(17.78,-20.32,(1,0)),
}
# USB-C receptacle (symbol pin free-ends); we only wire power + CC
USB_PINS = {
 "A4":(15.24,15.24,(1,0)), "A9":(15.24,15.24,(1,0)),
 "B4":(15.24,15.24,(1,0)), "B9":(15.24,15.24,(1,0)),
 "A5":(15.24,10.16,(1,0)), "B5":(15.24,7.62,(1,0)),
 "A6":(15.24,-2.54,(1,0)), "A7":(15.24,2.54,(1,0)),
 "B6":(15.24,-5.08,(1,0)), "B7":(15.24,0,(1,0)),
 "A8":(15.24,-12.7,(1,0)), "B8":(15.24,-15.24,(1,0)),
 "A1":(0,-22.86,(0,-1)), "A12":(0,-22.86,(0,-1)),
 "B1":(0,-22.86,(0,-1)), "B12":(0,-22.86,(0,-1)),
 "S1":(-7.62,-22.86,(0,-1)),
}

Q = 1.27
def SNAP(v): return round(round(float(v)/Q)*Q, 4)

class Sheet:
    def __init__(self):
        self.syms=[]; self.wires=[]; self.labels=[]; self.glabels=[]; self.ncs=[]
        self.libs=set(); self.pinpts={}
    def sym(self, lib_id, ref, value, x, y, footprint, pinmap, rot=0, unit=1):
        x,y = SNAP(x), SNAP(y); u=str(uuid.uuid4()); self.libs.add(lib_id)
        pins="".join(f'    (pin "{p}" (uuid {uuid.uuid4()}))\n' for p in pinmap)
        self.syms.append(f'''  (symbol (lib_id "{lib_id}") (at {x} {y} {rot}) (unit {unit})
    (in_bom yes) (on_board yes) (dnp no)
    (uuid {u})
    (property "Reference" "{ref}" (at {x} {y-15} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {x} {y+15} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "{footprint}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
{pins}    (instances
      (project "MeetingHub-4-v3"
        (path "/{ROOT_UUID}" (reference "{ref}") (unit {unit}))
      )
    )
  )
''')
    def connect(self, cx, cy, pinsdef, pin, net, glob=False):
        # place the label exactly on the pin's connection point - no wire, no
        # stub, so two nets can only ever merge if two pins truly coincide
        # (asserted in check()).
        rx,ry,_=pinsdef[pin]
        px,py=round(SNAP(cx)+rx,4), round(SNAP(cy)-ry,4)
        (self.glabels if glob else self.labels).append((net,px,py))
        self.pinpts.setdefault((px,py),set()).add(net)
    def nc(self, cx, cy, pinsdef, pin):
        rx,ry,_=pinsdef[pin]
        self.ncs.append((round(SNAP(cx)+rx,4), round(SNAP(cy)-ry,4)))
    def check(self):
        bad=[(k,v) for k,v in self.pinpts.items() if len(v)>1]
        if bad:
            for (x,y),v in bad: print(f"  !! collision at {x},{y}: {sorted(v)}")
            raise SystemExit("net collision(s) - fix placement")
        print(f"check OK: {len(self.pinpts)} distinct pin nodes, no collisions")
    def render(self):
        lib="\n".join(SYM[k] for k in sorted(self.libs))
        w="".join(f'  (wire (pts (xy {a} {b}) (xy {c} {d})) (stroke (width 0) (type default)) (uuid {uuid.uuid4()}))\n'
                  for a,b,c,d in self.wires)
        L="".join(f'  (label "{n}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uuid.uuid4()}))\n'
                  for n,x,y in self.labels)
        G="".join(f'  (global_label "{n}" (shape input) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uuid.uuid4()})'
                  f' (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)))\n'
                  for n,x,y in self.glabels)
        N="".join(f'  (no_connect (at {x} {y}) (uuid {uuid.uuid4()}))\n' for x,y in self.ncs)
        return f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid {ROOT_UUID})
  (paper "A2")
  (title_block
    (title "MeetingHub-4 v3 - Mic Selector")
    (rev "v3")
    (company "Open Hardware Project")
    (comment 1 "One-hot headset-mic router for 4 notebooks (audio handled externally)")
  )
  (lib_symbols
{lib}
  )
{w}{L}{G}{N}{"".join(self.syms)}  (sheet_instances
    (path "/" (page "1"))
  )
)
'''

FP_R   = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical"
FP_C   = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
FP_C25 = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"
FP_CP  = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"
FP_CP5 = "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm"
FP_D   = "Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_AnodeUp"
FP_TVS = "Diode_THT:D_DO-15_P3.81mm_Vertical_AnodeUp"
FP_Q   = "Package_TO_SOT_THT:TO-92_Inline"
FP_SW  = "Button_Switch_THT:SW_Tactile_SPST_Angled_PTS645Vx39-2LFS"
FP_DIP16="Package_DIP:DIP-16_W7.62mm"
FP_RELAY="Relay_THT:Relay_SPDT_Omron_G5V-1"
FP_FUSE= "Fuse:Fuse_Bourns_MF-RG500"
FP_USB = "Connector_USB:USB_C_Receptacle_GCT_USB4085"
FP_JACK= "MeetingHub-4-v3:Jack_3.5mm_3pole_THT_Horizontal"
FP_TP  = "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm"

# Connections are made by placing a net LABEL directly on each pin's connection
# point (no wires). Components are spread on a wide grid so no two pins ever
# share a coordinate; check() asserts that before the file is written.
s = Sheet()
GX = 20.32   # generous column pitch (16 grid units)

# ---------------- POWER (bottom-left) ----------------
ux,uy = 60, 320
s.sym("Connector:USB_C_Receptacle_USB2.0_16P","J1","USB-C 5V IN",ux,uy,FP_USB,
      list(USB_PINS.keys()))
s.connect(ux,uy,USB_PINS,"A4","VBUS")
s.connect(ux,uy,USB_PINS,"A1","GND",glob=True)
s.connect(ux,uy,USB_PINS,"S1","GND",glob=True)
for p in ("A6","A7","B6","B7","A8","B8"): s.nc(ux,uy,USB_PINS,p)
s.connect(ux,uy,USB_PINS,"A5","CC1"); s.connect(ux,uy,USB_PINS,"B5","CC2")
s.sym("Device:R","R1","5k1",100,300,FP_R,["1","2"])
s.connect(100,300,R_PINS,"1","CC1"); s.connect(100,300,R_PINS,"2","GND",glob=True)
s.sym("Device:R","R2","5k1",120,300,FP_R,["1","2"])
s.connect(120,300,R_PINS,"1","CC2"); s.connect(120,300,R_PINS,"2","GND",glob=True)
s.sym("Device:Polyfuse","F1","500mA",100,330,FP_FUSE,["1","2"])
s.connect(100,330,R_PINS,"1","VBUS"); s.connect(100,330,R_PINS,"2","+5V",glob=True)
# TVS at the connector entry (pre-fuse): a surge is shunted by D1, not forced through F1
s.sym("Diode:ZPYxx","D1","P6KE6.8A (TVS 5V uni)",120,340,FP_TVS,["1","2"])
s.connect(120,340,D_PINS,"1","VBUS"); s.connect(120,340,D_PINS,"2","GND",glob=True)
s.sym("Device:C","C1","100nF",140,340,FP_C,["1","2"])
s.connect(140,340,C_PINS,"1","+5V",glob=True); s.connect(140,340,C_PINS,"2","GND",glob=True)
s.sym("Device:C_Polarized","C2","10uF",160,340,FP_CP5,["1","2"])
s.connect(160,340,C_PINS,"1","+5V",glob=True); s.connect(160,340,C_PINS,"2","GND",glob=True)
s.sym("Device:C_Polarized","C3","47uF",180,340,FP_CP5,["1","2"])
s.connect(180,340,C_PINS,"1","+5V",glob=True); s.connect(180,340,C_PINS,"2","GND",glob=True)
s.sym("power:PWR_FLAG","#FLG1","PWR_FLAG",100,360,"",["1"])
s.connect(100,360,FLG_PINS,"1","VBUS")
s.sym("power:PWR_FLAG","#FLG2","PWR_FLAG",140,360,"",["1"])
s.connect(140,360,FLG_PINS,"1","GND",glob=True)
s.sym("power:PWR_FLAG","#FLG3","PWR_FLAG",120,360,"",["1"])
s.connect(120,360,FLG_PINS,"1","+5V",glob=True)
s.sym("Connector:TestPoint","TP1","+5V",200,330,FP_TP,["1"])
s.connect(200,330,TP_PINS,"1","+5V",glob=True)
s.sym("Connector:TestPoint","TP2","GND",220,330,FP_TP,["1"])
s.connect(220,330,TP_PINS,"1","GND",glob=True)

# ---------------- JACKS (left column) : SHOU HAN PJ-320A-3P DIP (LCSC C17701689) --
# P2 (3.5 mm) 3-conductor THT jack.  Datasheet terminal numbers:
#   pin 3 = TIP  -> mic signal
#   pin 2, pin 4 = ring & sleeve -> GND
# A CTIA TRRS->2x3.5 Y-splitter puts the mic on the plug tip and ties the mic
# plug's ring + sleeve to ground, so grounding BOTH pin 2 and pin 4 is safe and
# universal (mono, CTIA and PC-"pink" mic-on-tip plugs all work; nothing shorts
# the mic) - and it makes the 2/4 = ring-vs-sleeve question moot.
# Bring-up: confirm pin 3 is the tip contact with a meter (plug in, ring out).
for n in (1,2,3,4):
    jx,jy = 40, 150 + (n-1)*24
    s.sym("MeetingHub-4-v3:Jack3", f"J{n+1}", f"Mic NB{n}", jx, jy, FP_JACK, ["3","2","4"])
    s.connect(jx,jy,J3_PINS,"3",f"NB{n}_MIC",glob=True)
    s.connect(jx,jy,J3_PINS,"2","GND",glob=True)
    s.connect(jx,jy,J3_PINS,"4","GND",glob=True)
s.sym("MeetingHub-4-v3:Jack3","J6","Headset MIC",40,252,FP_JACK,["3","2","4"])
s.connect(40,252,J3_PINS,"3","HS_MIC",glob=True)
s.connect(40,252,J3_PINS,"2","GND",glob=True)
s.connect(40,252,J3_PINS,"4","GND",glob=True)

# ---------------- BUTTONS (top-left) ----------------
for i,ref in enumerate(["SW1","SW2","SW3","SW4"]):
    x,y = 40, 40 + i*20
    s.sym("Switch:SW_SPST", ref, f"Select NB{i+1}", x, y, FP_SW, ["1","2"])
    s.connect(x,y,SW_PINS,"1","+5V",glob=True)
    s.connect(x,y,SW_PINS,"2",f"BTN{i+1}")

# ---------------- DIODE MATRIX (4 rows x 4 cols) ----------------
matrix = {1:["SET1","RST2","RST3","RST4"], 2:["SET2","RST1","RST3","RST4"],
          3:["SET3","RST1","RST2","RST4"], 4:["SET4","RST1","RST2","RST3"]}
dref = 6
for b in (1,2,3,4):
    for k,line in enumerate(matrix[b]):
        x = 110 + k*GX
        y = 30 + (b-1)*15.24
        s.sym("Device:D", f"D{dref}", "1N4148", x, y, FP_D, ["1","2"])
        s.connect(x,y,D_PINS,"2",f"BTN{b}")   # anode (pin2, right) -> button
        s.connect(x,y,D_PINS,"1",line)        # cathode (pin1, left) -> S/R line
        dref += 1

# ---------------- PULL-DOWNS SET1-4 (R3-R6) / RST1-4 (R7-R10) 100k -> GND ----
rref = 3
for row,grp in ((0,["SET1","SET2","SET3","SET4"]), (1,["RST1","RST2","RST3","RST4"])):
    for j,line in enumerate(grp):
        x = 110 + j*GX
        y = 110 + row*20
        s.sym("Device:R", f"R{rref}", "100k", x, y, FP_R, ["1","2"])
        s.connect(x,y,R_PINS,"1",line)
        s.connect(x,y,R_PINS,"2","GND",glob=True)
        rref += 1

# ---------------- CD4043B U1 ----------------
cx,cy = 250, 90
s.sym("MeetingHub-4-v3:CD4043B","U1","CD4043B",cx,cy,FP_DIP16,
      [str(i) for i in range(1,17)])
s.connect(cx,cy,CD_PINS,"16","+5V",glob=True)
s.connect(cx,cy,CD_PINS,"8","GND",glob=True)
s.connect(cx,cy,CD_PINS,"5","+5V",glob=True)     # ENABLE high
for pin,net in (("4","SET1"),("3","RST1"),("6","SET2"),("7","RST2"),
                ("12","SET3"),("11","RST3"),("14","SET4"),("15","RST4"),
                ("2","QO1"),("9","QO2"),("10","QO3"),("1","QO4")):
    s.connect(cx,cy,CD_PINS,pin,net)
s.nc(cx,cy,CD_PINS,"13")
s.sym("Device:C","C4","100nF",300,60,FP_C,["1","2"])
s.connect(300,60,C_PINS,"1","+5V",glob=True); s.connect(300,60,C_PINS,"2","GND",glob=True)

# ---------------- POWER-ON RESET: +5V -C5(10uF)- PORN -R11(100k)- GND ----------
# 10 uF (not 1 uF): with 1 uF a slow (>~30 ms) VBUS ramp releases RST before the
# rail settles, and the CD4043B could latch a relay at power-on.  10 uF holds
# PORN ~ VBUS through any realistic ramp -> deterministically muted (matches v2).
# Polarity: pin 1 (+) -> +5V, pin 2 (-) -> PORN  (PORN never exceeds +5V).
s.sym("Device:C_Polarized","C5","10uF",200,220,FP_CP5,["1","2"])
s.connect(200,220,C_PINS,"1","+5V",glob=True); s.connect(200,220,C_PINS,"2","PORN")
s.sym("Device:R","R11","100k",220,220,FP_R,["1","2"])
s.connect(220,220,R_PINS,"1","PORN"); s.connect(220,220,R_PINS,"2","GND",glob=True)
for j,line in enumerate(["RST1","RST2","RST3","RST4"]):
    x,y = 250 + j*GX, 220
    s.sym("Device:D", f"D{22+j}", "1N4148", x, y, FP_D, ["1","2"])
    s.connect(x,y,D_PINS,"2","PORN")      # anode (pin2) -> PORN
    s.connect(x,y,D_PINS,"1",line)        # cathode (pin1) -> RST

# ---------------- RELAYS + freewheel diodes (right) ----------------
# Contact side (per the v2 ngspice bom_mic_deselect_detect.cir review):
#   COM (5/6) -> NBn_MIC          (this notebook's mic pin)
#   NO  (10)  -> HS_MIC           (the headset electret, common to all 4)
#   NC  (1)   -> R_NCn 2k2 -> GND
# Energised relay n: NBn_MIC <-> HS_MIC  -> that notebook gets the real electret.
# De-energised relay n: NBn_MIC <-> 2k2 -> GND  -> that notebook's codec reads
#   ~1.1 V on its mic pin (like an idle electret) instead of an open circuit.
#   An open circuit reads as "no microphone" and makes many codecs drop the
#   headset mic and fall back to the notebook's internal mic (room audio!).
#   The 2k2 load keeps every de-selected / muted notebook showing "headset mic
#   present, silent" - no disconnect event, no internal-mic fallback, no pop.
# Coil side (pins 2, 9) is unchanged.
for n in (1,2,3,4):
    kx,ky = 380, 60 + (n-1)*40
    s.sym("Relay:G5V-1", f"K{n}", f"Route NB{n}", kx, ky, FP_RELAY, ["1","2","5","6","9","10"])
    s.connect(kx,ky,K_PINS,"2","+5V",glob=True)
    s.connect(kx,ky,K_PINS,"9",f"COIL{n}")
    s.connect(kx,ky,K_PINS,"5",f"NB{n}_MIC",glob=True)   # COM -> notebook n mic
    s.connect(kx,ky,K_PINS,"6",f"NB{n}_MIC",glob=True)   # COM (2nd common pin)
    s.connect(kx,ky,K_PINS,"10","HS_MIC",glob=True)      # NO -> headset electret (common)
    s.connect(kx,ky,K_PINS,"1",f"NCBIAS{n}")             # NC -> 2k2 -> GND
    s.sym("Device:R", f"R{19+n}", "2k2", 520, 40 + (n-1)*40, FP_R, ["1","2"])  # R20..R23
    s.connect(520,40+(n-1)*40,R_PINS,"1",f"NCBIAS{n}")
    s.connect(520,40+(n-1)*40,R_PINS,"2","GND",glob=True)
    dx,dy = 350, 60 + (n-1)*40
    s.sym("Device:D", f"D{n+1}", "1N4148", dx, dy, FP_D, ["1","2"])   # freewheel
    s.connect(dx,dy,D_PINS,"1","+5V",glob=True)
    s.connect(dx,dy,D_PINS,"2",f"COIL{n}")

# ---------------- COIL DRIVERS Q1-Q4 ----------------
for n in (1,2,3,4):
    qx,qy = 440, 60 + (n-1)*40
    s.sym("MeetingHub-4-v3:2N7000", f"Q{n}", "2N7000", qx, qy, FP_Q, ["1","2","3"])
    s.connect(qx,qy,Q_PINS,"2",f"GATE{n}")
    s.connect(qx,qy,Q_PINS,"1","GND",glob=True)
    s.connect(qx,qy,Q_PINS,"3",f"COIL{n}")
    s.sym("Device:R", f"R{11+n}", "1k", 420, 60 + (n-1)*40, FP_R, ["1","2"])   # R12..R15
    s.connect(420,60+(n-1)*40,R_PINS,"1",f"QO{n}")
    s.connect(420,60+(n-1)*40,R_PINS,"2",f"GATE{n}")
    s.sym("Device:R", f"R{15+n}", "100k", 460, 60 + (n-1)*40, FP_R, ["1","2"])  # R16..R19
    s.connect(460,60+(n-1)*40,R_PINS,"1",f"GATE{n}")
    s.connect(460,60+(n-1)*40,R_PINS,"2","GND",glob=True)

s.check()
open(f"{PRJ}/MeetingHub-4-v3.kicad_sch","w").write(s.render())
print("wrote MeetingHub-4-v3.kicad_sch")
print("refs: J1-6, K1-4, Q1-4, U1, SW1-4, F1, D1-25, R1-23, C1-5, TP1-2")
