#!/usr/bin/env python3
"""Post-process the routed v3 board: solid zone connect, 0.15 mm netclass,
stitch any plane pad the router left isolated, tidy silk, final DRC."""
import pcbnew, re, json, collections, math

PCB = "/home/fac/MeetingHub-4/v3/hardware/KiCad/MeetingHub-4-v3/MeetingHub-4-v3.kicad_pcb"
PRO = "/home/fac/MeetingHub-4/v3/hardware/KiCad/MeetingHub-4-v3/MeetingHub-4-v3.kicad_pro"

s = open(PCB).read()
s = s.replace('(connect_pads (clearance 0.3))', '(connect_pads yes (clearance 0.25))')
open(PCB, "w").write(s)

b = pcbnew.LoadBoard(PCB)
try: b.GetDesignSettings().m_MinClearance = pcbnew.FromMM(0.15)
except Exception as e: print("minclr warn", e)

MM = pcbnew.FromMM

# --- silkscreen tidy -------------------------------------------------------
# The diode matrix + pull-down + POR clusters put ~50 tiny R/D/C parts on a
# tight grid; their silk reference text is what trips almost every silk_overlap
# / silk_over_copper DRC item.  Move those references to F.Fab (they stay in the
# assembly drawing / CPL, just off the silkscreen) and keep silk refs only on
# the parts a hand-assembler actually hunts for: connectors, relays, the IC,
# transistors, buttons, fuse, test points.
KEEP_SILK = ("J", "K", "U", "Q", "SW", "F")   # TP/MH: ref not useful, drop to Fab
import re as _re
FCu, FS, FF = pcbnew.F_Cu, pcbnew.F_SilkS, pcbnew.F_Fab
for f in b.GetFootprints():
    pre = _re.match(r"[A-Za-z]+", f.GetReference()).group(0)
    keep = pre in KEEP_SILK
    # value text always to Fab; on non-keep parts push every silk text (ref +
    # polarity marks like "A"/"K"/"+") to Fab too
    ref_t = f.Reference()
    texts = [ref_t, f.Value()] + [g for g in f.GraphicalItems()
                                  if isinstance(g, pcbnew.FP_TEXT)]
    for t in texts:
        if (t is ref_t and keep):
            continue
        if t.GetLayer() == FS:
            t.SetLayer(FF)
    r = f.Reference()
    if not keep:
        r.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        r.SetTextThickness(pcbnew.FromMM(0.12))
        continue
    r.SetLayer(FS); r.SetVisible(True)
    r.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.9), pcbnew.FromMM(0.9)))
    r.SetTextThickness(pcbnew.FromMM(0.15))
    # park the ref clear of this part's own pads: step out from the footprint
    # centre until the ref bbox clears every pad of the footprint
    pos = f.GetPosition()
    pads = [p.GetBoundingBox() for p in f.Pads()]
    X0, X1, Y0, Y1 = MM(5), MM(105), MM(13), MM(93)
    def clears(px, py):
        if not (X0 < px < X1 and Y0 < py < Y1):
            return False
        r.SetPosition(pcbnew.VECTOR2I(int(px), int(py)))
        rb = r.GetBoundingBox()
        return not any(rb.Intersects(pb) for pb in pads)
    for dy in (5.0, -5.0, 6.5, -6.5, 8.0, -8.0, 3.5, -3.5):
        if clears(pos.x, pos.y + MM(dy)):
            break
    else:
        r.SetPosition(pcbnew.VECTOR2I(pos.x, int(min(max(pos.y + MM(5.0), Y0), Y1))))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)

MM = pcbnew.FromMM

# --- reconnect any GND / +5V pad the plane pour left trapped on an island -----
# (U1.5, U1.8 and the jack Sleeve pads are pre-laid in gen_pcb; this is the
#  backup for whatever the router still boxed in.)  Route an L-path from the pad
#  to the nearest point of the main pour body.
b = pcbnew.LoadBoard(PCB)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())

def pour(board, net):
    layer = pcbnew.In1_Cu if net == "GND" else pcbnew.In2_Cu
    for z in board.Zones():
        if z.GetNetname() == net and z.GetLayer() == layer:
            pl = z.GetFilledPolysList(layer)
            outs = sorted((pl.Outline(i) for i in range(pl.OutlineCount())),
                          key=lambda o: o.Area())
            return (outs[-1], outs[:-1]) if outs else (None, [])
    return None, []

def trapped(board):
    out = []
    for net in ("GND", "+5V"):
        _, isl = pour(board, net)
        for f in board.GetFootprints():
            for pad in f.Pads():
                if pad.GetNetname() != net:
                    continue
                q = pad.GetPosition()
                if any(o.PointInside(pcbnew.VECTOR2I(q.x, q.y)) for o in isl):
                    out.append((f.GetReference(), pad.GetName(), q.x, q.y, net))
    return out

fixed = 0
bad = []
for ref, pn, qx, qy, net in trapped(b):
    layer = pcbnew.In1_Cu if net == "GND" else pcbnew.In2_Cu
    ni = b.FindNet(net)
    main, _ = pour(b, net)
    best, bd = None, 1e18
    for i in range(main.PointCount()):
        p = main.CPoint(i)
        d = (p.x - qx) ** 2 + (p.y - qy) ** 2
        if d < bd:
            bd, best = d, (p.x, p.y)
    tx = best[0] + (MM(2) if best[0] > qx else -MM(2))
    ty = best[1] + (MM(2) if best[1] > qy else -MM(2))
    ok = False
    for mid in ((tx, qy), (qx, ty), ((qx + tx) // 2, (qy + ty) // 2)):
        segs = []
        for a, c in (((qx, qy), mid), (mid, (tx, ty))):
            if a == c:
                continue
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(int(a[0]), int(a[1])))
            t.SetEnd(pcbnew.VECTOR2I(int(c[0]), int(c[1])))
            t.SetWidth(MM(0.3)); t.SetLayer(layer); t.SetNet(ni)
            b.Add(t); segs.append(t)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        if not any(r == ref and p == pn for r, p, *_ in trapped(b)):
            ok = True; break
        for t in segs:
            b.Remove(t)
    if ok:
        fixed += 1
    else:
        bad.append(f"{net} {ref}.{pn} @({round(pcbnew.ToMM(qx),1)},{round(pcbnew.ToMM(qy),1)})")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print(f"freed {fixed} trapped plane pads" + (f"; STILL TRAPPED: {bad}" if bad else ""))

# --- finish any signal connection the auto-router left short -----------------
RPT = "/tmp/v3_fin.rpt"
def unconn_pairs(board):
    pcbnew.WriteDRCReport(board, RPT, pcbnew.EDA_UNITS_MILLIMETRES, True)
    txt = open(RPT).read()
    pairs = []
    # KiCad 7 report: "[unconnected_items]: Missing connection between items"
    # followed by a severity line then exactly two "@(x mm, y mm): <what> [/net] ..."
    for blk in re.findall(r'\[unconnected_items\]:[^\n]*\n(?:[^\n]*\n)?'
                          r'((?:\s*@\([^\n]*\n){2})', txt):
        pts = re.findall(r'@\(([\d.]+) mm, ([\d.]+) mm\):[^\[]*\[([^\]]+)\]', blk)
        if len(pts) == 2 and pts[0][2] == pts[1][2]:
            pairs.append((float(pts[0][0]), float(pts[0][1]),
                          float(pts[1][0]), float(pts[1][1]), pts[0][2].lstrip('/')))
    return pairs

def drc_counts(board):
    pcbnew.WriteDRCReport(board, RPT, pcbnew.EDA_UNITS_MILLIMETRES, True)
    rp = open(RPT).read()
    unc = int(re.search(r'\*\* Found (\d+) unconnected pads', rp).group(1))
    bad = rp.count('[shorting_items]') + rp.count('[clearance]') + rp.count('[track_dangling]')
    return unc, bad

def polylines(A, B):
    """Candidate routes A->B: direct, both L-corners, and Z / detour paths that
    step perpendicular by d mm to get around an obstacle grid."""
    yield [A, B]
    yield [A, pcbnew.VECTOR2I(B.x, A.y), B]
    yield [A, pcbnew.VECTOR2I(A.x, B.y), B]
    dx, dy = B.x - A.x, B.y - A.y
    for d in (2, 3, 4, 5, 6, 8, 10, -2, -3, -4, -5, -6, -8, -10):
        o = int(MM(d))
        if abs(dx) >= abs(dy):                       # mostly horizontal -> detour in Y
            yield [A, pcbnew.VECTOR2I(A.x, A.y + o),
                   pcbnew.VECTOR2I(B.x, B.y + o), B]
            mx = (A.x + B.x) // 2
            yield [A, pcbnew.VECTOR2I(mx, A.y), pcbnew.VECTOR2I(mx, A.y + o),
                   pcbnew.VECTOR2I(mx, B.y), B]
        else:                                        # mostly vertical -> detour in X
            yield [A, pcbnew.VECTOR2I(A.x + o, A.y),
                   pcbnew.VECTOR2I(B.x + o, B.y), B]
            my = (A.y + B.y) // 2
            yield [A, pcbnew.VECTOR2I(A.x, my), pcbnew.VECTOR2I(A.x + o, my),
                   pcbnew.VECTOR2I(B.x, my), B]

b = pcbnew.LoadBoard(PCB)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
base_unc, base_bad = drc_counts(b)
done = 0
for ax, ay, bx, by, net in unconn_pairs(b):
    ni = b.FindNet(net)
    if ni is None:
        continue
    A = pcbnew.VECTOR2I(int(MM(ax)), int(MM(ay)))
    B = pcbnew.VECTOR2I(int(MM(bx)), int(MM(by)))
    ok = False
    for layer in (pcbnew.B_Cu, pcbnew.F_Cu):
        for pts in polylines(A, B):
            segs = []
            for p, q in zip(pts, pts[1:]):
                if p == q:
                    continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(p); t.SetEnd(q)
                t.SetWidth(MM(0.25)); t.SetLayer(layer); t.SetNet(ni)
                b.Add(t); segs.append(t)
            unc, bad = drc_counts(b)
            if unc <= base_unc - 1 and bad <= base_bad:
                base_unc = unc
                ok = True
                break
            for t in segs:
                b.Remove(t)
        if ok:
            break
    done += ok
    if not ok:
        print("  !! could not finish", net, f"({ax:.1f},{ay:.1f})-({bx:.1f},{by:.1f})")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print(f"finished {done} short signal net(s)")

# --- restore .kicad_pro (SaveBoard wipes sheet list / tightens rules) ----------
d = json.load(open(PRO))
d['sheets'] = [["c3d4e5f6-0000-4c3c-8c3c-00000000000a", ""]]
r = d['board']['design_settings']['rules']
r['min_clearance'] = 0.15
r['min_copper_edge_clearance'] = 0.3
d['net_settings']['classes'][0]['clearance'] = 0.15
json.dump(d, open(PRO, "w"), indent=2)

# --- final DRC ----------------------------------------------------------------
sev = json.load(open(PRO))['board']['design_settings']['rule_severities']
b = pcbnew.LoadBoard(PCB)
rpt = PCB.replace(".kicad_pcb", ".DRC.rpt")
pcbnew.WriteDRCReport(b, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
t = open(rpt).read()
it = collections.Counter(re.findall(r'\[([a-z_]+)\]', t))
err = {k: v for k, v in it.items() if sev.get(k, 'error') == 'error'}
war = {k: v for k, v in it.items() if sev.get(k, 'error') == 'warning'}
print("ERRORS  :", err or "NONE")
print("warnings:", war or "NONE")
print(re.search(r'\*\* Found \d+ unconnected pads \*\*', t).group(0))
smd = {f.GetReference() for f in b.GetFootprints()
       for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD}
print("SMD pads:", smd or "NONE - 100% THT")
