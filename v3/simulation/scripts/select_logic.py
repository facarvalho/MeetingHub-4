"""
MeetingHub-4 v3 - one-hot mic selector: logic / timing simulation + video.

Faithful to hardware/PCB/MeetingHub-4-v3.net.  Diode matrix D6-D21
(anode = BTNn, cathode = SET/RST line) + POR diodes D22-D25 (anode = PORN):

  BTN1 (SW1): D6->SET1  D7->RST2  D8->RST3  D9->RST4
  BTN2 (SW2): D10->SET2 D11->RST1 D12->RST3 D13->RST4
  BTN3 (SW3): D14->SET3 D15->RST1 D16->RST2 D17->RST4
  BTN4 (SW4): D18->SET4 D19->RST1 D20->RST2 D21->RST3
  PORN      : D22->RST1 D23->RST2 D24->RST3 D25->RST4
  pull-downs: R3-R6 (SET1-4) 100k, R7-R10 (RST1-4) 100k -> low when nothing drives

U1 CD4043B = 4x NOR R/S latch, OE (pin 5) = +5V so Qn is always driven:
  Sn=1,Rn=0 -> Qn=1 ;  Rn=1 -> Qn=0 (covers S=R=1) ;  0,0 -> hold
  (pin map S/R/Q  1:4/3/2  2:6/7/9  3:12/11/10  4:14/15/1)

Driver + relay:  Qn -> R12-15 (1k) -> GATEn -> Q1-4 (2N7000, R16-19 100k pull-down)
  Qn=1 -> 2N7000 on -> COILn to GND -> Kn energises
  Kn on  -> NBn_MIC (COM 5/6) tied to HS_MIC (NO 10) -> notebook n gets the mic
  Kn off -> NBn_MIC on NC(1) -> 2k2 -> GND -> notebook n reads ~1.1 V ("mic
           present, silent"), not an open circuit ("no mic")
"""
import os, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
OUT = os.path.join(os.path.dirname(__file__), "..")

MATRIX = {                       # button -> (SET latch, [RST latches])   0-based
    0: (0, [1, 2, 3]),
    1: (1, [0, 2, 3]),
    2: (2, [0, 1, 3]),
    3: (3, [0, 1, 2]),
}

class OneHot:
    def __init__(self):
        self.Q = [0, 0, 0, 0]
    def step(self, buttons, porn_high):
        SET = [0, 0, 0, 0]; RST = [0, 0, 0, 0]
        for b, pressed in enumerate(buttons):
            if pressed:
                s, rs = MATRIX[b]
                SET[s] = 1
                for r in rs:
                    RST[r] = 1
        if porn_high:
            RST = [1, 1, 1, 1]
        newQ = []
        for i in range(4):
            if SET[i] and not RST[i]: newQ.append(1)
            elif RST[i]:              newQ.append(0)
            else:                     newQ.append(self.Q[i])
        self.Q = newQ
        return SET, RST, list(self.Q)

def route(Q):
    on = [i for i, q in enumerate(Q) if q]
    if len(on) == 1: return f"mic -> NOTEBOOK {on[0]+1}"
    if len(on) == 0: return "mic MUTED (no relay)"
    return f"FAULT: {len(on)} relays energised"


def run():
    POR_MS = 130            # C5 10uF holds PORN ~ VBUS through any ramp; ~130 ms tail after settle
    EVENTS = [
        (0,    "power on",              [0, 0, 0, 0]),
        (400,  "tap NB1 (SW1)",         [1, 0, 0, 0]),
        (900,  "tap NB2 (SW2)",         [0, 1, 0, 0]),
        (1400, "tap NB3 (SW3)",         [0, 0, 1, 0]),
        (1900, "tap NB4 (SW4)",         [0, 0, 0, 1]),
        (2400, "(idle - stays on NB4)", [0, 0, 0, 0]),
        (2800, "hold SW2 + SW3",        [0, 1, 1, 0]),
        (3200, "release",               [0, 0, 0, 0]),
    ]
    TAP_MS, DT = 45, 1.0
    T = np.arange(0, 3700, DT)
    sim = OneHot()
    rec = {k: np.zeros(len(T)) for k in
           ["BTN1", "BTN2", "BTN3", "BTN4", "Q1", "Q2", "Q3", "Q4", "PORN"]}
    for ti, t in enumerate(T):
        btn = [0, 0, 0, 0]
        for te, lbl, bp in EVENTS:
            if te <= t < te + TAP_MS:
                btn = [max(a, b) for a, b in zip(btn, bp)]
            if any(bp) and te <= t < te + 8 and int(t - te) % 2 == 0:   # contact bounce
                btn = [0, 0, 0, 0]
        porn = t < POR_MS
        _, _, Q = sim.step(btn, porn)
        for i in range(4):
            rec[f"BTN{i+1}"][ti] = btn[i]; rec[f"Q{i+1}"][ti] = Q[i]
        rec["PORN"][ti] = 1 if porn else 0

    print("=" * 70)
    print(" MeetingHub-4 v3  -  one-hot mic selector, single-press sequence")
    print("=" * 70)
    got, exp = [], ["mic MUTED (no relay)", "mic -> NOTEBOOK 1", "mic -> NOTEBOOK 2",
                    "mic -> NOTEBOOK 3", "mic -> NOTEBOOK 4", "mic -> NOTEBOOK 4",
                    "mic MUTED (no relay)", "mic MUTED (no relay)"]
    for te, lbl, _ in EVENTS:
        idx = min(int((te + TAP_MS + 30) / DT), len(T) - 1)
        Q = [int(rec[f"Q{i+1}"][idx]) for i in range(4)]
        got.append(route(Q))
        print(f"  t={te:5d} ms  {lbl:22s}  Q={Q}   {route(Q)}")
    ok = got == exp
    print("=" * 70)
    print(f" matches the requested KVM behaviour: {'YES' if ok else 'NO'}")
    for e, g, (te, lbl, _) in zip(exp, got, EVENTS):
        print(f"   {'ok ' if e == g else 'XX '} {lbl:22s} expect '{e}'  got '{g}'")

    checks = []
    for (te, lbl, _), e, g in zip(EVENTS, exp, got):
        checks.append({"check": f"S {lbl}", "require": e, "measure": g, "pass": e == g, "note": ""})

    # ---- static plot
    fig, axes = plt.subplots(5, 1, figsize=(11, 8), sharex=True)
    def band(ax, sig, color, label):
        ax.fill_between(T, 0, sig, step="pre", color=color, alpha=.85)
        ax.set_ylim(-0.2, 1.2); ax.set_yticks([])
        ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=9)
    band(axes[0], rec["PORN"], "#f85149", "PORN")
    for i in range(4):
        band(axes[i+1], rec[f"BTN{i+1}"], "#8b949e", f"SW{i+1}\n(NB{i+1})")
        a2 = axes[i+1].twinx(); a2.plot(T, rec[f"Q{i+1}"], color="#2ea043", lw=2)
        a2.set_ylim(-0.2, 1.2); a2.set_yticks([0, 1])
        a2.set_ylabel(f"Q{i+1}", color="#2ea043")
    for te, lbl, _ in EVENTS:
        for ax in axes:
            ax.axvline(te, color="#ccc", lw=.6, ls=":")
        axes[0].annotate(lbl, (te, 1.35), fontsize=7.5, rotation=25, va="bottom")
    axes[-1].set_xlabel("time  [ms]")
    axes[0].set_title("SELECT_LOGIC  -  grey = button press, green = latch output Qn "
                      f"(POR holds every RST high for the first ~{POR_MS} ms)")
    fig.tight_layout(); fig.savefig(f"{OUT}/plots/S_select_logic.png", dpi=110)
    plt.close(fig)
    print(f"\n wrote plots/S_select_logic.png")

    # ---- standalone video
    FPS = 25
    frames = list(range(0, len(T), int(1000 / FPS / DT)))
    figv = plt.figure(figsize=(12.8, 7.2), dpi=100); figv.patch.set_facecolor("#0e1116")
    gsl = figv.add_gridspec(1, 2, width_ratios=[1.15, 1], left=.06, right=.97,
                            top=.82, bottom=.1, wspace=.18)
    axT = figv.add_subplot(gsl[0]); axS = figv.add_subplot(gsl[1])
    ttl = figv.text(.5, .94, "", ha="center", fontsize=18, color="#e6edf3", weight="bold")
    sub = figv.text(.5, .875, "", ha="center", fontsize=12, color="#7ee787")
    rows = ["PORN", "BTN1", "Q1", "BTN2", "Q2", "BTN3", "Q3", "BTN4", "Q4"]
    cols = {r: ("#f85149" if r == "PORN" else "#8b949e" if r.startswith("BTN") else "#2ea043")
            for r in rows}
    def vframe(fi):
        ti = frames[fi]; t = T[ti]
        for a in (axT, axS):
            a.clear(); a.set_facecolor("#161b22")
            for sp in a.spines.values(): sp.set_color("#3a434f")
            a.tick_params(colors="#9aa4b2")
        w = (T >= t - 1200) & (T <= t)
        for k, name in enumerate(rows):
            y0 = len(rows) - k
            axT.fill_between(T[w], y0, y0 + rec[name][w] * 0.8, step="pre",
                             color=cols[name], alpha=.85)
            axT.text(t - 1200, y0 + 0.3, name, color="#c9d1d9", fontsize=9, ha="left")
        axT.set_xlim(t - 1200, t + 30); axT.set_ylim(0.5, len(rows) + 1.2)
        axT.set_yticks([]); axT.set_xlabel("time  [ms]", color="#9aa4b2")
        axT.axvline(t, color="#58a6ff", lw=1)
        Q = [int(rec[f"Q{i+1}"][ti]) for i in range(4)]
        axS.set_xlim(0, 10); axS.set_ylim(0, 10); axS.axis("off")
        axS.text(1.2, 9.2, "HEADSET MIC", color="#e6edf3", fontsize=12, weight="bold")
        axS.plot([2.0, 2.0], [1, 8.8], color="#8b949e", lw=3)
        for i in range(4):
            y = 7.5 - i * 1.9; onc = Q[i] == 1
            axS.add_patch(plt.Rectangle((4.3, y - .45), 1.4, .9,
                          color="#2ea043" if onc else "#30363d"))
            axS.text(5.0, y, "K" + str(i + 1), ha="center", va="center",
                     color="#0e1116" if onc else "#8b949e", fontsize=10, weight="bold")
            axS.text(7.2, y, f"NOTEBOOK {i+1}", va="center",
                     color="#7ee787" if onc else "#6e7681", fontsize=12,
                     weight="bold" if onc else "normal")
            axS.plot([2.0, 4.3], [y, y], color="#2ea043" if onc else "#30363d",
                     lw=3 if onc else 2, ls="-" if onc else ":")
            if onc:
                axS.plot([5.7, 6.9], [y, y], color="#2ea043", lw=3)
        axS.text(5.0, 0.2, route(Q), ha="center",
                 color="#f85149" if 1 not in Q else "#7ee787", fontsize=14, weight="bold")
        cur = ""
        for te, lbl, _ in EVENTS:
            if t >= te: cur = lbl
        ttl.set_text("MeetingHub-4 v3  -  one-hot mic selector")
        porn = "  |  POR active (mic force-muted)" if t < POR_MS else ""
        sub.set_text(f"t = {t:5.0f} ms   |   last action: {cur}{porn}")
        return []
    ani = FuncAnimation(figv, vframe, frames=len(frames), interval=1000 / FPS)
    ani.save(f"{OUT}/MeetingHub-4-v3-mic-selector.mp4",
             writer=FFMpegWriter(fps=FPS, bitrate=3000, codec="libx264"),
             savefig_kwargs={"facecolor": figv.get_facecolor()})
    plt.close(figv)
    print(" wrote MeetingHub-4-v3-mic-selector.mp4")
    return checks


if __name__ == "__main__":
    run()
