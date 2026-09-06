#!/usr/bin/env python3
"""Build MeetingHub-4-v2 2-layer PCB: front/rear split, rounded outline,
placement + nets + GND zones + mounting holes + TP2."""
import re, math, pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

NET   = "/tmp/v2.net"
OUT   = "/home/fac/MeetingHub-4/v2/hardware/KiCad/MeetingHub-4-v2/MeetingHub-4-v2.kicad_pcb"
STDFP = "/usr/share/kicad/footprints"
LOCFP = "/home/fac/MeetingHub-4/v2/hardware/KiCad/MeetingHub-4-v2/MeetingHub-4-v2.pretty"

t = open(NET).read()
comp_fp = {m.group(1): m.group(2) for m in re.finditer(
    r'\(comp \(ref "([^"]+)"\)\s*\(value "[^"]*"\)\s*\(footprint "([^"]*)"\)', t)}
pad_net = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]+)"\)((?:\s*\(node[^\n]*)*)', t):
    name = m.group(1)
    if name.startswith("unconnected-"):
        continue
    for r, p in re.findall(r'\(ref "([^"]+)"\) \(pin "([^"]+)"', m.group(2)):
        pad_net[(r, p)] = name

board = pcbnew.BOARD()
board.SetCopperLayerCount(2)
nets = {}
for name in sorted(set(pad_net.values())):
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    nets[name] = ni

def load_fp(fpid):
    lib, name = fpid.split(":")
    d = LOCFP if lib.startswith("MeetingHub-4") else f"{STDFP}/{lib}.pretty"
    fp = pcbnew.FootprintLoad(d, name)
    if fp is not None:
        fp.SetFPID(pcbnew.LIB_ID(lib, name))     # keep the library nickname
    return fp

PLACED = []
def place(ref, x, y, rot=0, fpid=None):
    fid = fpid or comp_fp.get(ref)
    if fid is None:
        print("  MISSING in netlist:", ref); return None
    fp = load_fp(fid)
    if fp is None:
        raise RuntimeError("cannot load " + fid)
    fp.SetReference(ref)
    fp.SetPosition(VECTOR2I(FromMM(float(x)), FromMM(float(y))))
    if rot:
        fp.SetOrientationDegrees(rot)
    board.Add(fp)
    for pad in fp.Pads():
        k = (ref, pad.GetName())
        if k in pad_net:
            pad.SetNet(nets[pad_net[k]])
    PLACED.append((float(x), float(y), ref))
    return fp

def block(refs, x0, y0, cols, cw, ch, rot=0):
    for i, r in enumerate(refs):
        c, row = i % cols, i // cols
        place(r, x0 + c*cw, y0 + row*ch, rot)

# ================================================================ layout (mm)
# V2: smaller & more square than the v1 fabricated board.  y: rear small, front large.
REAR  = 12.0
FRONT = 168.0

# ---- REAR edge ----
place("J1", 40, REAR+9, 180)
place("D1", 40, REAR+22, 0)
place("F1", 56, REAR+22, 0)
place("C1", 70, REAR+22, 0)
place("TP1", 84, REAR+7, 0)
place("C2", 96, REAR+22, 0)
# J2-J5: rot 0. The local PJ-3200B-4A footprint (rev-11, rebuilt from the LCEDA
# land pattern) is pre-rotated so the insertion barrel points -Y; at rot 0 that
# barrel overhangs the REAR edge and the plug faces out. y = REAR+8.0 puts the
# jack body face ~at the board edge, the ~1.4 mm barrel nose overhanging, and the
# O1.50 NPTH locating posts ~2.3 / 9.3 mm inside the edge
# (verify the overhang vs the acrylic panel in the GUI / 3D view).
block(["J2","J3","J4","J5"], 112, REAR+8.0, 4, 23, 0, 0)

# ---- MIXER (left lane x18..76) ----
place("U1", 44, 38, 0)
block(["R1","R2","R3","R4","R5","R6"],   20, 60, 3, 7, 14, 90)
block(["R7","R8","R9","R10","R11","R12"],20, 88, 3, 7, 14, 90)
place("U3", 44, 64, 0)
block(["R38","C3","C4","C25","C26"],     40, 92, 5, 7, 0, 90)
block(["C5","C6","C7","C8","C9","C10"],   20, 108, 6, 7, 0, 90)
block(["C11","C12","C13","C14","C15","C16"],20, 122, 6, 7, 0, 90)

# ---- HEADPHONE AMP (lane x82..122) ----
place("U2", 98, 42, 0)
block(["C17","C18","C19","C20","C21"], 84, 58, 5, 7, 0, 90)
block(["R13","R14","R15","R16"],        84, 74, 4, 7, 0, 90)
block(["R17","R18","R19","R20"],        84, 90, 4, 7, 0, 90)

# ---- MIC-SWITCH relays (right of hpamp, top) ----
block(["K1","K2"], 138, 36, 2, 26, 0, 0)
block(["K3","K4"], 138, 54, 2, 26, 0, 0)
block(["D2","D3"], 150, 38, 2, 26, 0, 90)
block(["D4","D5"], 150, 56, 2, 26, 0, 90)
# R39-R42: de-selected-laptop mic hold-up, 2k2 NC->GND (SCH-P). Horizontal
# stack in the open area below the Q-column / right of the R21-R37 array.
block(["R39","R40","R41","R42"], 168, 102, 1, 0, 6, 0)

# ---- SELECT LOGIC ----
place("U4", 148, 76, 90)                                       # CD4043B, long axis in X
block(["Q1","Q2","Q3","Q4"], 190, 40, 1, 0, 13, 0)            # right-edge column
block(["C22","C23","C24"], 116, 66, 1, 0, 9, 0)
block(["R21","R22","R23","R24","R25","R26",
       "R27","R28","R29","R30","R31","R32",
       "R33","R34","R35","R36","R37"], 124, 96, 6, 7, 14, 90)   # 3 rows (internal)
block(["D10","D11","D12","D13","D14","D15","D16","D17","D18","D19",
       "D20","D21","D22","D23","D24","D25","D26","D27","D28","D29"], 124, 140, 10, 7, 12, 90)  # 2 rows, right above the buttons

# ---- FRONT edge: pots + buttons + headset ----
# Enclosure is top+bottom acrylic only, sides OPEN (no front panel). Controls
# are operated directly, so each part's CAN body sits ~just behind the open
# edge and only the functional bit (shaft / plunger / barrel) overhangs.
# RV1-5: y=FRONT-5.5 -> RK097 9.55mm can ends ~0.5mm inside the edge, ~22mm of
#        M7 bushing + shaft overhangs for the knob.
block(["RV1","RV2","RV3","RV4","RV5"], 30, FRONT-5.5, 5, 15, 0, 90)
# SW2-5: right-angle PTS645 tact, rot 180 -> plunger points +Y (out the open
# front edge). y=FRONT-3 -> plunger tip ~1mm past the edge for a clean finger
# press (or a button cap).
block(["SW2","SW3","SW4","SW5"], 124, FRONT-3, 4, 14, 0, 180)
# J6: rot 180 -> the PJ-3200B-4A barrel (-Y end) points to the FRONT edge, plug out.
place("J6", 182, FRONT-8.0, 180)

tp2 = place("TP2", 118, 44, 0, "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm")
if tp2:
    for pad in tp2.Pads():
        pad.SetNet(nets["GND"])

# ================================================================ outline
xs = [p[0] for p in PLACED]
x1 = round(min(xs) - 10, 1); x2 = round(max(xs) + 12, 1)
y1 = round(REAR, 1);         y2 = round(FRONT, 1)
R  = 6.0                      # corner radius

# mounting holes: 4 corners + 2 near the front edge (MH5/MH6) so the long front
# edge with the 5 pot knobs is properly supported against push/turn force.
MH = "MountingHole:MountingHole_3.2mm_M3"
for i,(mx,my) in enumerate([(x1+8,y1+8),(x2-8,y1+8),(x1+8,y2-30),(x2-8,y2-30),
                            (x1+9,y2-12),(x2-9,y2-12)],1):
    place(f"MH{i}", mx, my, 0, MH)
print("board mm: %.1f x %.1f   (%.1f,%.1f)-(%.1f,%.1f)" % (x2-x1, y2-y1, x1, y1, x2, y2))

# GND corner stitching vias: the rounded-corner pinch in the GND pour can leave a
# thin lobe near a corner that the router doesn't tie back (-> 1 "unconnected"
# DRC item). One pre-placed GND via just inside each corner keeps both pours and
# both lobes bonded there. Kept clear of the corner MountingHoles.
gnd_ni = nets["GND"]
for cx, cy in [(x1+4, y1+4), (x2-4, y1+4), (x1+4, y2-4), (x2-4, y2-4)]:
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(VECTOR2I(FromMM(cx), FromMM(cy)))
    v.SetDrill(FromMM(0.4)); v.SetWidth(FromMM(0.8))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd_ni)
    board.Add(v)
print("4 GND corner stitching vias placed")

pcbnew.SaveBoard(OUT, board)
s = open(OUT).read()

def gr_line(ax, ay, bx, by, i):
    return (f'  (gr_line (start {ax} {ay}) (end {bx} {by}) '
            f'(stroke (width 0.15) (type solid)) (layer "Edge.Cuts") '
            f'(tstamp aaaa0000-0000-0000-0000-0000000000{i:02d}))\n')
def gr_arc(sx, sy, mx, my, ex, ey, i):
    return (f'  (gr_arc (start {sx} {sy}) (mid {mx} {my}) (end {ex} {ey}) '
            f'(stroke (width 0.15) (type solid)) (layer "Edge.Cuts") '
            f'(tstamp aaaa0000-0000-0000-0000-0000000001{i:02d}))\n')

edge = ""
# straight segments (inset by R at each end)
edge += gr_line(x1+R, y1, x2-R, y1, 0)      # rear
edge += gr_line(x2,   y1+R, x2,  y2-R, 1)   # right
edge += gr_line(x2-R, y2, x1+R, y2, 2)      # front
edge += gr_line(x1,   y2-R, x1,  y1+R, 3)   # left
# rounded corners: mid point on the 45deg of the quarter circle
k = R * (1 - math.sqrt(0.5))
edge += gr_arc(x1+R, y1, x1+k, y1+k, x1, y1+R, 0)   # top-left
edge += gr_arc(x2, y1+R, x2-k, y1+k, x2-R, y1, 1)   # top-right
edge += gr_arc(x2-R, y2, x2-k, y2-k, x2, y2-R, 2)   # bottom-right
edge += gr_arc(x1, y2-R, x1+k, y2-k, x1+R, y2, 3)   # bottom-left

gnd_code = re.search(r'\(net (\d+) "GND"\)', s).group(1)
# zone outline follows the rounded rectangle: chamfer each corner by R so the
# pour never pokes outside Edge.Cuts (a sharp-corner sliver there ends up as an
# isolated island -> 1 "unconnected" DRC item).
zpts = [(x1+R, y1), (x2-R, y1), (x2, y1+R), (x2, y2-R),
        (x2-R, y2), (x1+R, y2), (x1, y2-R), (x1, y1+R)]
zpoly = " ".join(f"(xy {px} {py})" for px, py in zpts)
zones = ""
for i, ly in enumerate(("F.Cu", "B.Cu")):
    zones += (f'  (zone (net {gnd_code}) (net_name "GND") (layer "{ly}") '
              f'(tstamp bbbb0000-0000-0000-0000-00000000000{i}) (hatch edge 0.5)\n'
              f'    (connect_pads (clearance 0.3))\n'
              f'    (min_thickness 0.25) (filled_areas_thickness no)\n'
              f'    (fill (thermal_gap 0.3) (thermal_bridge_width 0.4))\n'
              f'    (polygon (pts {zpoly}))\n'
              f'  )\n')

s = s.rstrip()[:-1] + edge + zones + ")\n"
open(OUT, "w").write(s)
print("rounded edge + zones appended; GND net =", gnd_code)
