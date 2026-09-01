#!/usr/bin/env python3
"""Generate SELECT_LOGIC.kicad_sch and rebuild MICSW.kicad_sch for MeetingHub-4 v3."""
import json, uuid, os

PRJ = "/home/fac/MeetingHub-4/v2/hardware/KiCad/MeetingHub-4-v2"
SP  = "/tmp/claude-1000/-home-fac-MeetingHub-4/4f6efdf4-c26b-4fc0-859e-6637f4f9d120/scratchpad"
ROOT_UUID = "8b7deae6-c6d2-463d-9623-40608a842bd8"
SEL_SHEET_UUID = "1a2b3c4d-0005-4a1a-8a1a-000000000005"
MIC_SHEET_UUID = "1a2b3c4d-0004-4a1a-8a1a-000000000004"

symblocks = json.load(open(SP + "/symblocks.json"))

Q = 1.27
def SNAP(v):
    return round(round(float(v) / Q) * Q, 4)

# clean hand-authored 2N7000 in the PROJECT-LOCAL library so it never conflicts
# with (or is reported as "modified" vs) KiCad's Transistor_FET:2N7000.
# (the KiCad-lib copy also segfaults kicad-cli 7.0.11 netlist export.)
symblocks["MeetingHub-4-v2:2N7000"] = r'''(symbol "MeetingHub-4-v2:2N7000" (pin_names hide) (in_bom yes) (on_board yes)
    (property "Reference" "Q" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "2N7000" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "ki_description" "0.2A Id, N-Channel logic-level MOSFET, TO-92" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "ki_fp_filters" "TO?92*" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "2N7000_0_1"
      (rectangle (start -2.54 3.81) (end 2.54 -3.81) (stroke (width 0.254) (type default)) (fill (type none)))
    )
    (symbol "2N7000_1_1"
      (pin passive line (at 2.54 -5.08 90) (length 2.54) (name "S" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin input line (at -5.08 0 0) (length 2.54) (name "G" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      (pin passive line (at 2.54 5.08 270) (length 2.54) (name "D" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
    )
  )'''

# ---- custom CD4043B symbol (single unit, DIP-16) --------------------------------
CD4043B_SYM = r'''(symbol "MeetingHub-4-v2:CD4043B" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
    (property "Reference" "U" (at -15.24 27.94 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "CD4043B" (at 2.54 27.94 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Package_DIP:DIP-16_W7.62mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/cd4043b.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "ki_description" "Quad NOR R/S latch, 3-state outputs" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "ki_fp_filters" "DIP*W7.62mm*" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "CD4043B_0_1"
      (rectangle (start -12.7 25.4) (end 12.7 -25.4)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "CD4043B_1_1"
      (pin power_in line (at 0 30.48 270) (length 5.08) (name "VDD" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))
      (pin power_in line (at 0 -30.48 90) (length 5.08) (name "VSS" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 20.32 0) (length 5.08) (name "S1" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 15.24 0) (length 5.08) (name "R1" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 10.16 0) (length 5.08) (name "S2" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 5.08 0) (length 5.08) (name "R2" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 -2.54 0) (length 5.08) (name "S3" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 -7.62 0) (length 5.08) (name "R3" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 -12.7 0) (length 5.08) (name "S4" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 -17.78 0) (length 5.08) (name "R4" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))
      (pin input line (at -17.78 -22.86 0) (length 5.08) (name "EN" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
      (pin output line (at 17.78 20.32 180) (length 5.08) (name "Q1" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      (pin output line (at 17.78 12.7 180) (length 5.08) (name "Q2" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
      (pin output line (at 17.78 5.08 180) (length 5.08) (name "Q3" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
      (pin output line (at 17.78 -2.54 180) (length 5.08) (name "Q4" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin no_connect line (at 17.78 -20.32 180) (length 5.08) (name "NC" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
    )
  )'''

# CD4043B pin free-end coords (symbol space, Y up) and outward dir
CD_PINS = {
 "16":(0,30.48,(0,-1)), "8":(0,-30.48,(0,1)),
 "4":(-17.78,20.32,(-1,0)), "3":(-17.78,15.24,(-1,0)),
 "6":(-17.78,10.16,(-1,0)), "7":(-17.78,5.08,(-1,0)),
 "12":(-17.78,-2.54,(-1,0)),"11":(-17.78,-7.62,(-1,0)),
 "14":(-17.78,-12.7,(-1,0)),"15":(-17.78,-17.78,(-1,0)),
 "5":(-17.78,-22.86,(-1,0)),
 "2":(17.78,20.32,(1,0)), "9":(17.78,12.7,(1,0)),
 "10":(17.78,5.08,(1,0)), "1":(17.78,-2.54,(1,0)),
 "13":(17.78,-20.32,(1,0)),
}
# opamp (LM2904 symbol) pin free ends
OP_PINS = {
 "1":(7.62,0,(1,0)),   "2":(-7.62,-2.54,(-1,0)), "3":(-7.62,2.54,(-1,0)),
 "7":(7.62,0,(1,0)),   "6":(-7.62,-2.54,(-1,0)), "5":(-7.62,2.54,(-1,0)),
 "8":(-2.54,7.62,(0,-1)), "4":(-2.54,-7.62,(0,1)),
}
R_PINS = {"1":(0,3.81,(0,-1)), "2":(0,-3.81,(0,1))}
C_PINS = {"1":(0,3.81,(0,-1)), "2":(0,-3.81,(0,1))}
D_PINS = {"1":(-3.81,0,(-1,0)), "2":(3.81,0,(1,0))}   # 1=K 2=A
Q_PINS = {"1":(2.54,-5.08,(0,1)), "2":(-5.08,0,(-1,0)), "3":(2.54,5.08,(0,-1))}  # S G D
SW_PINS= {"1":(-5.08,0,(-1,0)), "2":(5.08,0,(1,0))}
GND_PINS={"1":(0,0,(0,1))}
K_PINS = {"1":(2.54,7.62,(0,-1)), "10":(7.62,7.62,(0,-1)), "2":(-5.08,7.62,(0,-1)),
          "5":(5.08,-7.62,(0,1)), "6":(5.08,-7.62,(0,1)), "9":(-5.08,-7.62,(0,1))}

class Sheet:
    def __init__(self, sheet_uuid, page):
        self.sheet_uuid = sheet_uuid; self.page = page
        self.syms=[]; self.wires=[]; self.labels=[]; self.glabels=[]; self.ncs=[]
        self.used_libs=set()
    def sym(self, lib_id, ref, value, x, y, footprint, pinmap, unit=1, extra_props=""):
        x, y = SNAP(x), SNAP(y)
        u=str(uuid.uuid4())
        self.used_libs.add(lib_id)
        pins="".join(f'    (pin "{p}" (uuid {uuid.uuid4()}))\n' for p in pinmap)
        block=f'''  (symbol (lib_id "{lib_id}") (at {x} {y} 0) (unit {unit})
    (in_bom yes) (on_board yes) (dnp no)
    (uuid {u})
    (property "Reference" "{ref}" (at {x} {y-12} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {x} {y+12} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "{footprint}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
{extra_props}{pins}    (instances
      (project "MeetingHub-4-v2"
        (path "/{ROOT_UUID}/{self.sheet_uuid}" (reference "{ref}") (unit {unit}))
      )
    )
  )
'''
        self.syms.append(block)
    def pin_xy(self, cx, cy, pinsdef, pin):
        rx,ry,_=pinsdef[pin]
        return (SNAP(cx+rx), SNAP(cy-ry))
    def connect(self, cx, cy, pinsdef, pin, net, glob=False, stub=2.54):
        rx,ry,(ox,oy)=pinsdef[pin]
        px,py=SNAP(cx+rx), SNAP(cy-ry)
        ex,ey=SNAP(px+ox*stub), SNAP(py+oy*stub)
        self.wires.append((px,py,ex,ey))
        if glob:
            self.glabels.append((net,ex,ey))
        else:
            self.labels.append((net,ex,ey))
    def wire(self,x1,y1,x2,y2): self.wires.append((SNAP(x1),SNAP(y1),SNAP(x2),SNAP(y2)))
    def nc(self, cx, cy, pinsdef, pin):
        rx,ry,_=pinsdef[pin]
        self.ncs.append((SNAP(cx+rx), SNAP(cy-ry)))
    def render(self, libsym_text):
        w="".join(f'  (wire (pts (xy {a} {b}) (xy {c} {d})) (stroke (width 0) (type default)) (uuid {uuid.uuid4()}))\n'
                  for a,b,c,d in self.wires)
        L="".join(f'  (label "{n}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uuid.uuid4()}))\n'
                  for n,x,y in self.labels)
        G="".join(f'  (global_label "{n}" (shape input) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uuid.uuid4()})'
                  f' (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)))\n'
                  for n,x,y in self.glabels)
        N="".join(f'  (no_connect (at {x} {y}) (uuid {uuid.uuid4()}))\n' for x,y in self.ncs)
        S="".join(self.syms)
        return f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid {self.sheet_uuid})
  (paper "A4")
  (lib_symbols
{libsym_text}
  )
{w}{L}{G}{N}{S})
'''

# ============================ SELECT_LOGIC ======================================
s = Sheet(SEL_SHEET_UUID, "7")
FP_R = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
FP_C = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
FP_CP= "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"
FP_CP5="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm"
FP_D = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
FP_Q = "Package_TO_SOT_THT:TO-92_Inline"
FP_SW= "Button_Switch_THT:SW_PUSH_6mm"
FP_DIP8="Package_DIP:DIP-8_W7.62mm"
FP_DIP16="Package_DIP:DIP-16_W7.62mm"

# ---- push buttons SW2..SW5 (momentary) : pin1=+5V, pin2=BTNn ----
for i,ref in enumerate(["SW2","SW3","SW4","SW5"]):
    x,y = 30, 30+ i*22
    s.sym("Switch:SW_SPST", ref, f"Select NB{i+1} (momentary)", x, y, FP_SW, ["1","2"])
    s.connect(x,y,SW_PINS,"1","+5V_AUDIO",glob=True)
    s.connect(x,y,SW_PINS,"2",f"BTN{i+1}")

# ---- diode matrix : anode(2)=BTNn , cathode(1)=target line ----
# target[b] = list of (line) for button b (1-based); first entry is SET b, rest are RST of others
matrix = {
 1:["SET1","RST2","RST3","RST4"],
 2:["SET2","RST1","RST3","RST4"],
 3:["SET3","RST1","RST2","RST4"],
 4:["SET4","RST1","RST2","RST3"],
}
dref=10
for b in (1,2,3,4):
    for k,line in enumerate(matrix[b]):
        x = 78
        y = 20 + (b-1)*30 + k*7
        s.sym("Device:D", f"D{dref}", "1N4148", x, y, FP_D, ["1","2"])
        s.connect(x,y,D_PINS,"2",f"BTN{b}")     # anode -> button
        s.connect(x,y,D_PINS,"1",line)          # cathode -> S/R line
        dref+=1

# ---- pull-downs on SET1..4 (R21..R24) and RST1..4 (R25..R28) : 100k to GND ----
rref=21
for grp,pre in ((["SET1","SET2","SET3","SET4"],"S"),(["RST1","RST2","RST3","RST4"],"R")):
    for j,line in enumerate(grp):
        x = 108 if pre=="S" else 118
        y = 25 + j*30 + (0 if pre=="S" else 12)
        s.sym("Device:R", f"R{rref}", "100k", x, y, FP_R, ["1","2"])
        s.connect(x,y,R_PINS,"1",line)
        s.connect(x,y,R_PINS,"2","GND",glob=True)
        rref+=1

# ---- CD4043B U4 ----
ux,uy = 150, 70
s.sym("MeetingHub-4-v2:CD4043B", "U4", "CD4043B", ux, uy, FP_DIP16,
      ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"])
s.connect(ux,uy,CD_PINS,"16","+5V_AUDIO",glob=True)
s.connect(ux,uy,CD_PINS,"8","GND",glob=True)
s.connect(ux,uy,CD_PINS,"5","+5V_AUDIO",glob=True)      # ENABLE
s.connect(ux,uy,CD_PINS,"4","SET1"); s.connect(ux,uy,CD_PINS,"3","RST1")
s.connect(ux,uy,CD_PINS,"6","SET2"); s.connect(ux,uy,CD_PINS,"7","RST2")
s.connect(ux,uy,CD_PINS,"12","SET3");s.connect(ux,uy,CD_PINS,"11","RST3")
s.connect(ux,uy,CD_PINS,"14","SET4");s.connect(ux,uy,CD_PINS,"15","RST4")
s.connect(ux,uy,CD_PINS,"2","QO1"); s.connect(ux,uy,CD_PINS,"9","QO2")
s.connect(ux,uy,CD_PINS,"10","QO3");s.connect(ux,uy,CD_PINS,"1","QO4")
s.nc(ux,uy,CD_PINS,"13")

# ---- U4 decoupling C22 100nF, bulk C23 100uF ----
s.sym("Device:C","C22","100nF",176,66,FP_C,["1","2"])
s.connect(176,66,C_PINS,"1","+5V_AUDIO",glob=True)
s.connect(176,66,C_PINS,"2","GND",glob=True)
s.sym("Device:C_Polarized","C23","100uF",134,120,FP_CP,["1","2"])
s.connect(134,120,C_PINS,"1","+5V_AUDIO",glob=True)
s.connect(134,120,C_PINS,"2","GND",glob=True)

# ---- power-on reset : +5V -C24- PORN -R37- GND ; PORN -> D26..29 -> RST1..4 ----
# C24 = 10uF electrolytic (was 1uF): stretches the reset window to ~40ms so a
# slow USB-C VBUS ramp still guarantees Q1..Q4 = 0 (mic muted) at power-on.
# Polarity: pin1(+) -> +5V, pin2(-) -> PORN (PORN never rises above +5V).
s.sym("Device:C_Polarized","C24","10uF",40,150,FP_CP5,["1","2"])
s.connect(40,150,C_PINS,"1","+5V_AUDIO",glob=True)
s.connect(40,150,C_PINS,"2","PORN")
s.sym("Device:R","R37","100k",40,168,FP_R,["1","2"])
s.connect(40,168,R_PINS,"1","PORN")
s.connect(40,168,R_PINS,"2","GND",glob=True)
for j,line in enumerate(["RST1","RST2","RST3","RST4"]):
    x,y = 58, 140+j*8
    s.sym("Device:D", f"D{26+j}", "1N4148", x, y, FP_D, ["1","2"])
    s.connect(x,y,D_PINS,"2","PORN")     # anode -> PORN
    s.connect(x,y,D_PINS,"1",line)       # cathode -> RST line

# ---- MOSFET coil drivers Q1..Q4 : QOn -R(1k)- GATEn -R(100k)- GND ; Q.G=GATEn Q.S=GND Q.D=COILn
for n in (1,2,3,4):
    qx,qy = 200, 30+(n-1)*30
    s.sym("MeetingHub-4-v2:2N7000", f"Q{n}", "2N7000", qx, qy, FP_Q, ["1","2","3"])
    s.connect(qx,qy,Q_PINS,"2",f"GATE{n}")
    s.connect(qx,qy,Q_PINS,"1","GND",glob=True)
    s.connect(qx,qy,Q_PINS,"3",f"COIL{n}",glob=True)
    # series 1k  R29..R32
    rx,ry = 180, 30+(n-1)*30
    s.sym("Device:R", f"R{28+n}", "1k", rx, ry, FP_R, ["1","2"])
    s.connect(rx,ry,R_PINS,"1",f"QO{n}")
    s.connect(rx,ry,R_PINS,"2",f"GATE{n}")
    # gate pulldown 100k  R33..R36
    gx,gy = 190, 42+(n-1)*30
    s.sym("Device:R", f"R{32+n}", "100k", gx, gy, FP_R, ["1","2"])
    s.connect(gx,gy,R_PINS,"1",f"GATE{n}")
    s.connect(gx,gy,R_PINS,"2","GND",glob=True)

# ---- VBIAS buffer U3 (dual op-amp, LM358, single +5V rail) ----
# U3A: non-inverting unity follower. Isolation R38 (47R) between op-amp output
# (VB_OUT) and the distributed VBIAS net; feedback (-in) taken AFTER R38 so DC is
# exact and the 1uF load cap can't destabilise the LM358.
bx,by = 250, 70
s.sym("Amplifier_Operational:LM2904","U3","LM358",bx,by,FP_DIP8,["1","2","3"],unit=1)
s.connect(bx,by,OP_PINS,"3","VBIAS_REF",glob=True)
s.connect(bx,by,OP_PINS,"1","VB_OUT")
s.connect(bx,by,OP_PINS,"2","VBIAS",glob=True)
s.sym("Device:R","R38","47R",268,70,FP_R,["1","2"])
s.connect(268,70,R_PINS,"1","VB_OUT")
s.connect(268,70,R_PINS,"2","VBIAS",glob=True)
# unit 3 (power)
s.sym("Amplifier_Operational:LM2904","U3","LM358",bx,by-40,FP_DIP8,["4","8"],unit=3)
s.connect(bx,by-40,OP_PINS,"8","+5V_AUDIO",glob=True)
s.connect(bx,by-40,OP_PINS,"4","GND",glob=True)
# unit 2 (spare) : +in -> GND, -in -> out (follower), out only to its own -in
s.sym("Amplifier_Operational:LM2904","U3","LM358",bx,by+40,FP_DIP8,["5","6","7"],unit=2)
s.connect(bx,by+40,OP_PINS,"5","GND",glob=True)
s.connect(bx,by+40,OP_PINS,"6","U3B_FB")
s.connect(bx,by+40,OP_PINS,"7","U3B_FB")
# C25 opamp decap, C26 VBIAS bulk
s.sym("Device:C","C25","100nF",285,45,FP_C,["1","2"])
s.connect(285,45,C_PINS,"1","+5V_AUDIO",glob=True)
s.connect(285,45,C_PINS,"2","GND",glob=True)
s.sym("Device:C","C26","1uF",285,95,FP_C,["1","2"])
s.connect(285,95,C_PINS,"1","VBIAS",glob=True)
s.connect(285,95,C_PINS,"2","GND",glob=True)

# assemble lib_symbols for SELECT_LOGIC
need = ["Device:R","Device:C","Device:C_Polarized","Device:D","power:GND",
        "Switch:SW_SPST","MeetingHub-4-v2:2N7000","Amplifier_Operational:LM2904"]
libtext = "\n".join(symblocks[k] for k in need) + "\n" + CD4043B_SYM
open(PRJ+"/SELECT_LOGIC.kicad_sch","w").write(s.render(libtext))
print("SELECT_LOGIC written; refs:", "R21..R37, C22..C26, D10..D29, Q1..Q4, U3, U4, SW2..SW5")

# ============================ MICSW rebuild =====================================
m = Sheet(MIC_SHEET_UUID, "6")
FP_RELAY="Relay_THT:Relay_SPDT_Omron_G5V-1"
FP_D2="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
for n in (1,2,3,4):
    kx,ky = 90, 40+(n-1)*40
    m.sym("Relay:G5V-1", f"K{n}", f"Select NB{n}", kx, ky, FP_RELAY,
          ["1","2","5","6","9","10"])
    m.connect(kx,ky,K_PINS,"2","+5V_AUDIO",glob=True)
    m.connect(kx,ky,K_PINS,"9",f"COIL{n}",glob=True)
    m.connect(kx,ky,K_PINS,"5","HEADSET_MIC",glob=True)
    m.connect(kx,ky,K_PINS,"6","HEADSET_MIC",glob=True)
    m.connect(kx,ky,K_PINS,"10",f"NB{n}_MIC",glob=True)
    m.nc(kx,ky,K_PINS,"1")
    # freewheel diode : cathode(1) -> +5V(pin2 side) ; anode(2) -> COILn (pin9 side)
    dx,dy = 120, 40+(n-1)*40
    m.sym("Device:D", f"D{n+1}", "1N4148", dx, dy, FP_D2, ["1","2"])
    m.connect(dx,dy,D_PINS,"1","+5V_AUDIO",glob=True)
    m.connect(dx,dy,D_PINS,"2",f"COIL{n}",glob=True)

need_m=["Device:D","power:GND","Relay:G5V-1"]
libtext_m="\n".join(symblocks[k] for k in need_m)
open(PRJ+"/MICSW.kicad_sch","w").write(m.render(libtext_m))
print("MICSW rebuilt")
