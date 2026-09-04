#!/usr/bin/env python3
"""Apply a Freerouting .ses route result onto the .kicad_pcb (KiCad 7, no GUI)."""
import re, sys, pcbnew
from pcbnew import VECTOR2I, PCB_TRACK, PCB_VIA, FromMM

PCB = "/home/fac/MeetingHub-4/v3/hardware/KiCad/MeetingHub-4-v3/MeetingHub-4-v3.kicad_pcb"
SES = "/tmp/v3.ses"

board = pcbnew.LoadBoard(PCB)
# wipe any existing tracks/vias (idempotent re-runs)
for tr in list(board.GetTracks()):
    board.Remove(tr)

txt = open(SES).read()
LAY = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu}

def P(sx, sy):
    return VECTOR2I(int(round(float(sx) * 100)), int(round(-float(sy) * 100)))  # 0.1um -> nm

ntrack = nvia = 0
# iterate each (net "NAME" ... ) block within network_out
for nm in re.finditer(r'\(net "([^"]+)"\s*((?:.*?\n)*?)\s*\)\s*(?=\(net "|\)\s*\)\s*\)\s*$|\Z)', txt):
    pass

# simpler: split on (net " inside network_out
no = txt.split("(network_out", 1)[1]
blocks = re.split(r'\(net "', no)
for blk in blocks[1:]:
    name = blk[:blk.index('"')]
    net = board.FindNet(name)
    body = blk
    # wires
    for w in re.finditer(r'\(path (\S+) (\d+)\s*((?:-?\d+\s+)+)\)', body):
        layer, width, nums = w.group(1), int(w.group(2)), w.group(3).split()
        if layer not in LAY:
            continue
        coords = list(map(float, nums))
        pts = [P(coords[i], coords[i+1]) for i in range(0, len(coords)-1, 2)]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            t = PCB_TRACK(board)
            t.SetStart(a); t.SetEnd(b)
            t.SetWidth(int(round(width * 100)))     # 0.1um -> nm
            t.SetLayer(LAY[layer])
            if net: t.SetNet(net)
            board.Add(t); ntrack += 1
    # vias
    for v in re.finditer(r'\(via "[^"]*_(\d+):(\d+)_um" (-?\d+) (-?\d+)', body):
        pad, drill, x, y = v.groups()
        via = PCB_VIA(board)
        via.SetPosition(P(x, y))
        via.SetDrill(FromMM(int(drill)/1000.0))
        via.SetWidth(FromMM(int(pad)/1000.0))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        if net: via.SetNet(net)
        board.Add(via); nvia += 1

# refill zones
try:
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
except Exception as e:
    print("zone fill warn:", e)

pcbnew.SaveBoard(PCB, board)
print(f"applied {ntrack} track segments, {nvia} vias")
pcbnew.WriteDRCReport(board, "/tmp/drc_routed.rpt", pcbnew.EDA_UNITS_MILLIMETRES, True)
