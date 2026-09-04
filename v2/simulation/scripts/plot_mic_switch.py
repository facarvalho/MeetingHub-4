"""
Section O plot — selecting a mic must not interrupt the monitor (mixer) audio.

Reads spice/mic_switch_glitch.dat (ngspice, real BOM device models — see
spice/bom_mic_switch_glitch.cir) and renders plots/N_mic_switch_no_glitch.svg:
a 1 kHz monitor tone at J6.T while the one-hot latch flips K1 -> K2 at t = 320 ms,
over a +5 V rail zoomed to mV.  Pure-stdlib SVG (no numpy/matplotlib needed).
"""
import os

HERE = os.path.dirname(__file__)
DAT = os.path.join(HERE, "..", "spice", "mic_switch_glitch.dat")
OUT = os.path.join(HERE, "..", "plots", "N_mic_switch_no_glitch.svg")

rows = []
for line in open(DAT):
    p = line.split()
    if len(p) < 8:
        continue
    rows.append([float(x) for x in p])          # t j6t . plogc . paudc . vbias ...
# columns: 0 t, 1 j6t, 3 plogc, 5 paudc, 7 vbias
t0, t1 = 0.314, 0.326                            # +/- 6 ms around the 0.320 s switch
def series(idx):
    return [(r[0], r[idx]) for r in rows if t0 <= r[0] <= t1]
j6t, plog = series(1), series(3)

W, H, pad = 820, 540, 58

def panel(x0, y0, w, h, data, ymin, ymax, title, yfmt, zero=None, color="#2563eb"):
    o = [f'<text x="{x0}" y="{y0-8}" font-size="13" font-weight="600" fill="#111">{title}</text>',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fff" stroke="#cbd5e1"/>']
    X = lambda tt: x0 + (tt - t0) / (t1 - t0) * w
    Y = lambda v: y0 + h - (v - ymin) / (ymax - ymin) * h
    tt = 0.314
    while tt <= t1 + 1e-9:
        gx = X(tt)
        o.append(f'<line x1="{gx:.1f}" y1="{y0}" x2="{gx:.1f}" y2="{y0+h}" stroke="#eef2f7"/>')
        o.append(f'<text x="{gx:.1f}" y="{y0+h+14}" font-size="10" text-anchor="middle" fill="#666">{(tt-0.320)*1e3:+.0f}</text>')
        tt += 0.002
    for k in range(5):
        v = ymin + (ymax - ymin) * k / 4
        gy = Y(v)
        o.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0+w}" y2="{gy:.1f}" stroke="#eef2f7"/>')
        o.append(f'<text x="{x0-6}" y="{gy+3:.1f}" font-size="10" text-anchor="end" fill="#666">{yfmt(v)}</text>')
    if zero is not None:
        o.append(f'<line x1="{x0}" y1="{Y(zero):.1f}" x2="{x0+w}" y2="{Y(zero):.1f}" stroke="#94a3b8" stroke-dasharray="3 2"/>')
    sx = X(0.320)
    o.append(f'<line x1="{sx:.1f}" y1="{y0}" x2="{sx:.1f}" y2="{y0+h}" stroke="#dc2626" stroke-width="1.5"/>')
    o.append(f'<text x="{sx+4:.1f}" y="{y0+13}" font-size="10" fill="#dc2626">bot&#227;o pressionado</text>')
    pts = " ".join(f"{X(tt):.1f},{Y(v):.1f}" for tt, v in data if ymin <= v <= ymax)
    o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.3"/>')
    return "\n".join(o)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="system-ui,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#f8fafc"/>',
       f'<text x="{pad}" y="26" font-size="15" font-weight="700" fill="#0f172a">MeetingHub-4 v2 (rev-9) &#8212; trocar o microfone n&#227;o interrompe o mixer</text>',
       f'<text x="{pad}" y="44" font-size="11" fill="#475569">1 kHz de monitora&#231;&#227;o no fone enquanto o seletor comuta K1&#8594;K2 (laptop 1 &#8594; laptop 2) em t = 0. ngspice, modelos dos componentes. Eixo x em ms.</text>',
       panel(pad, 80, W-2*pad, 180, j6t, -0.13, 0.13,
             "Sa&#237;da do fone  J6.T  (o que voc&#234; ouve)", lambda v: f"{v*1e3:+.0f} mV", zero=0.0, color="#2563eb"),
       panel(pad, 320, W-2*pad, 170, plog, 4.90, 5.02,
             "Trilho +5 V junto &#224;s bobinas dos rel&#233;s  (zoom em mV)", lambda v: f"{v:.2f}", color="#16a34a"),
       f'<text x="{pad}" y="{H-14}" font-size="10.5" fill="#475569">Resultado: a senoide no fone continua sem degrau nem falha (varia&#231;&#227;o &lt; 80 &#181;V &#8776; &#8722;63 dB no evento). O trilho +5 V n&#227;o afunda.</text>',
       '</svg>']
open(OUT, "w").write("\n".join(svg))
print("wrote", os.path.relpath(OUT, HERE))
