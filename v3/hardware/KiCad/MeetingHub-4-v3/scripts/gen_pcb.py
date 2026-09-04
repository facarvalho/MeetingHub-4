#!/usr/bin/env python3
"""Build the MeetingHub-4 v3 2-layer PCB: compact placement, rounded outline,
GND pour on both layers (+5V routed), 4x M3.  Smallest sensible all-THT layout for the mic
selector.  Front edge = the 4 select buttons + headset jack; rear edge = USB-C +
the 4 notebook mic jacks; everything else in the middle."""
import re, math, pcbnew
from pcbnew import VECTOR2I, FromMM

NET   = "/tmp/v3.net"
OUT   = "/home/fac/MeetingHub-4/v3/hardware/KiCad/MeetingHub-4-v3/MeetingHub-4-v3.kicad_pcb"
STDFP = "/usr/share/kicad/footprints"
LOCFP = "/home/fac/MeetingHub-4/v3/hardware/KiCad/MeetingHub-4-v3/MeetingHub-4-v3.pretty"

t = open(NET).read()
comp_fp = {m.group(1): m.group(2) for m in re.finditer(
    r'\(comp \(ref "([^"]+)"\)\s*\(value "[^"]*"\)\s*\(footprint "([^"]*)"\)', t)}
pad_net = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]+)"\)((?:\s*\(node[^\n]*)*)', t):
    name = m.group(1)
    if name.startswith("unconnected-"): continue
    for r, p in re.findall(r'\(ref "([^"]+)"\) \(pin "([^"]+)"', m.group(2)):
        pad_net[(r, p)] = name

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)     # F.Cu sig / In1.Cu GND / In2.Cu +5V / B.Cu sig
board.SetLayerName(pcbnew.In1_Cu, "In1.Cu")
board.SetLayerName(pcbnew.In2_Cu, "In2.Cu")
nets = {}
for name in sorted(set(pad_net.values())):
    ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); nets[name] = ni

def load_fp(fpid):
    lib, name = fpid.split(":")
    d = LOCFP if lib.startswith("MeetingHub-4") else f"{STDFP}/{lib}.pretty"
    fp = pcbnew.FootprintLoad(d, name)
    if fp is not None:
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp

PLACED = []
BBOX = []   # (ref, x0,y0,x1,y1) courtyard bounding boxes, for overlap warnings
def place(ref, x, y, rot=0, fpid=None):
    fid = fpid or comp_fp.get(ref)
    if fid is None:
        print("  MISSING:", ref); return None
    fp = load_fp(fid)
    if fp is None: raise RuntimeError("cannot load " + fid)
    fp.SetReference(ref)
    fp.SetPosition(VECTOR2I(FromMM(float(x)), FromMM(float(y))))
    if rot: fp.SetOrientationDegrees(rot)
    board.Add(fp)
    for pad in fp.Pads():
        k = (ref, pad.GetName())
        if k in pad_net: pad.SetNet(nets[pad_net[k]])
    PLACED.append((float(x), float(y), ref))
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if not bb.GetWidth():
        bb = fp.GetBoundingBox(False, False)
    x0,y0,x1,y1 = (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                   pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))
    for (r2,a0,b0,a1,b1) in BBOX:
        if x0 < a1-0.05 and a0 < x1-0.05 and y0 < b1-0.05 and b0 < y1-0.05:
            print(f"  OVERLAP {ref} <-> {r2}")
    BBOX.append((ref,x0,y0,x1,y1))
    return fp

def row(refs, x0, y, dx, rot=0):
    for i, r in enumerate(refs): place(r, x0 + i*dx, y, rot)

def grid(refs, x0, y0, cols, dx, dy, rot=0):
    for i, r in enumerate(refs):
        place(r, x0 + (i % cols)*dx, y0 + (i // cols)*dy, rot)

# ================================================================ layout (mm)
# vertical DIN0207 / DO-35 footprints are ~5.1 x 3.0 mm; at rot 90 ~3.0 x 5.1.
REAR, FRONT = 10.0, 96.0

# ---- REAR edge: USB-C + 4 notebook mic jacks (barrels overhang -Y) ----
place("J1", 20, REAR+10, 180)
place("R1", 25, REAR+5, 90)                     # CC1 pull-down 5k1
place("R2", 29, REAR+5, 90)                     # CC2 pull-down 5k1
row(["J2", "J3", "J4", "J5"], 38, REAR+7.0, 11.5, 0)

# ---- power cluster (rear-right, clear of the relay stack below) ----
place("F1", 88, REAR+6, 0)
place("C1", 82, REAR+13, 90)
place("C2", 88, REAR+13, 90)
place("C3", 94, REAR+13, 90)
place("D1", 99, REAR+20, 90)                    # TVS

# ---- SET/RST pull-downs R3-R10 + POR R11 : a column near the LEFT EDGE, rot 180
#      so the GND pad sits against the board-edge GND pour. ----
for i in range(8):
    place(f"R{3+i}", 7, 26 + i*6.0, 180)
place("R11", 7, 74, 180)
place("TP1", 104, 30, 0)
place("TP2", 104, 36, 0)

# ---- CD4043B: shifted left so its S/R pins sit right beside the pull-down
#      column and pin 8 (VSS) faces open B.Cu GND ----
place("U1", 30, 34, 0)
place("C4", 15, 82, 90)

# ---- diode matrix D6-D21 (16) rot90, 8 cols x 2 rows (centre, below U1) ----
grid(["D6","D7","D8","D9","D10","D11","D12","D13",
      "D14","D15","D16","D17","D18","D19","D20","D21"], 22, 62, 8, 3.6, 7.0, 90)
# ---- POR caps/diodes ----
place("C5", 22, 82, 90)
row(["D22","D23","D24","D25"], 27, 82, 3.6, 90)

# ---- drivers Q1-4 + gate R + relays K1-4 + freewheel D2-5 (centre-right) ----
for i in range(4):
    y = 30 + i*14
    place(f"R{12+i}", 53, y, 90)                # QOn series 1k
    place(f"Q{i+1}", 58, y, 0)
    place(f"R{16+i}", 64, y, 90)                # gate pull-down 100k
    place(f"D{i+2}", 72, y, 90)                 # freewheel
    place(f"K{i+1}", 82, y, 0)
    place(f"R{20+i}", 92, y, 90)                # NC-bias 2k2 -> GND (deselect detect)

# ---- FRONT edge: 4 buttons + headset jack ----
row(["SW1", "SW2", "SW3", "SW4"], 20, FRONT-3, 12.0, 180)
place("J6", 70, FRONT-7.0, 180)

# ================================================================ outline
x1, x2 = 2.0, 108.0
y1 = round(REAR, 1); y2 = round(FRONT, 1)
R = 3.0
MH = "MountingHole:MountingHole_3.2mm_M3"
for i, (mx, my) in enumerate([(x1+5, y1+5), (x2-5, y1+5),
                              (x1+5, y2-5), (x2-5, y2-5)], 1):
    place(f"MH{i}", mx, my, 0, MH)
print("board mm: %.1f x %.1f   (%.1f,%.1f)-(%.1f,%.1f)" % (x2-x1, y2-y1, x1, y1, x2, y2))

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

k = R * (1 - math.sqrt(0.5))
edge = ""
edge += gr_line(x1+R, y1, x2-R, y1, 0)
edge += gr_line(x2, y1+R, x2, y2-R, 1)
edge += gr_line(x2-R, y2, x1+R, y2, 2)
edge += gr_line(x1, y2-R, x1, y1+R, 3)
edge += gr_arc(x1+R, y1, x1+k, y1+k, x1, y1+R, 0)
edge += gr_arc(x2, y1+R, x2-k, y1+k, x2-R, y1, 1)
edge += gr_arc(x2-R, y2, x2-k, y2-k, x2, y2-R, 2)
edge += gr_arc(x1, y2-R, x1+k, y2-k, x1+R, y2, 3)

gnd_code = re.search(r'\(net (\d+) "GND"\)', s).group(1)
p5_code  = re.search(r'\(net (\d+) "\+5V"\)', s).group(1)
# 4-layer: In1.Cu = solid GND plane, In2.Cu = solid +5V plane, F.Cu / B.Cu are
# open for signals.  Every GND / +5V THT pin drops straight through to its inner
# plane; the auto-router only handles the signal nets, on two full layers.  No
# plane fragmentation, no escape stubs needed.
zones = ""
for i, (ly, code, nm) in enumerate((("In1.Cu", gnd_code, "GND"), ("In2.Cu", p5_code, "+5V"))):
    zones += (f'  (zone (net {code}) (net_name "{nm}") (layer "{ly}") '
              f'(tstamp bbbb0000-0000-0000-0000-00000000000{i}) (hatch edge 0.5)\n'
              f'    (connect_pads yes (clearance 0.25))\n'
              f'    (min_thickness 0.25) (filled_areas_thickness no)\n'
              f'    (fill (thermal_gap 0.3) (thermal_bridge_width 0.4))\n'
              f'    (polygon (pts (xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2})))\n'
              f'  )\n')

s = s.rstrip()[:-1] + edge + zones + ")\n"
open(OUT, "w").write(s)
print(f"edge + In1.Cu GND / In2.Cu +5V planes (GND {gnd_code}, +5V {p5_code})")
