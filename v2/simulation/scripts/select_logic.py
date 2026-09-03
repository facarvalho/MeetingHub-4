"""
MeetingHub-4 v2 - SELECT_LOGIC one-hot mic selector: logic/timing simulation.

Faithful to hardware/PCB/MeetingHub-4-v2.net.  Each diode of the D10-D29 matrix
is listed with the net it ties (anode = button / PORN, cathode = SET/RST line):

  BTN1 (SW2): D10->SET1  D11->RST2  D12->RST3  D13->RST4
  BTN2 (SW3): D14->SET2  D15->RST1  D16->RST3  D17->RST4
  BTN3 (SW4): D18->SET3  D19->RST1  D20->RST2  D21->RST4
  BTN4 (SW5): D22->SET4  D23->RST1  D24->RST2  D25->RST3
  PORN      : D26->RST1  D27->RST2  D28->RST3  D29->RST4
  pulldowns : R21-24 (SET1-4) 100k, R25-28 (RST1-4) 100k -> low when nothing drives

U4 CD4043B = 4x NOR R/S latch, OE (pin5) = +5V so Qn always driven:
  latch n:  Sn=1,Rn=0 -> Qn=1 ;  Sn=0,Rn=1 -> Qn=0 ;  0,0 -> hold ;  1,1 -> Qn=0
  (pin map S/R/Q  1:4/3/2  2:6/7/9  3:12/11/10  4:14/15/1)

Driver+relay:  Qn -> R29-32 (1k) -> GATEn -> 2N7000 (R33-36 100k pulldown)
  Qn=1 -> 2N7000 on -> COILn to GND -> Kn energises
  Kn energised -> HEADSET_MIC (COM 5/6) tied to NBn_MIC (NO 10) -> laptop n mic
  Kn idle      -> NC(1) open -> headset mic disconnected from laptop n
"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
OUT = os.path.join(os.path.dirname(__file__), "..")

# matrix: button -> (SET index or None, [RST indices])   (0-based latch ids)
MATRIX = {
    0: (0, [1, 2, 3]),   # BTN1 -> SET1, RST2/3/4
    1: (1, [0, 2, 3]),   # BTN2 -> SET2, RST1/3/4
    2: (2, [0, 1, 3]),   # BTN3 -> SET3, RST1/2/4
    3: (3, [0, 1, 2]),   # BTN4 -> SET4, RST1/2/3
}

class OneHot:
    """event-stepped model of U4 + matrix + POR."""
    def __init__(self):
        self.Q = [0, 0, 0, 0]

    def step(self, buttons, porn_high):
        SET = [0, 0, 0, 0]; RST = [0, 0, 0, 0]
        for b, pressed in enumerate(buttons):
            if pressed:
                s, rs = MATRIX[b]
                if s is not None: SET[s] = 1
                for r in rs: RST[r] = 1
        if porn_high:
            RST = [1, 1, 1, 1]
        newQ = []
        for i in range(4):
            if SET[i] and not RST[i]:      q = 1
            elif RST[i]:                   q = 0        # covers R=1 (incl. S=R=1)
            else:                          q = self.Q[i]
            newQ.append(q)
        self.Q = newQ
        return SET, RST, list(self.Q)

def relay_route(Q):
    on = [i for i, q in enumerate(Q) if q]
    if len(on) == 1:  return f"mic -> LAPTOP {on[0]+1}"
    if len(on) == 0:  return "mic MUTED (no relay)"
    return f"FAULT: {len(on)} relays on"


def _run():
    POR_MS = 140
    EVENTS = [
        (0,    "power on",             [0,0,0,0]),
        (400,  "tap SW2  (laptop 1)",  [1,0,0,0]),
        (900,  "tap SW3  (laptop 2)",  [0,1,0,0]),
        (1400, "tap SW4  (laptop 3)",  [0,0,1,0]),
        (1900, "tap SW5  (laptop 4)",  [0,0,0,1]),
        (2500, "(idle)",               [0,0,0,0]),
        (2900, "SW3+SW4 held together",[0,1,1,0]),
        (3300, "release",              [0,0,0,0]),
    ]
    TAP_MS = 45; DT = 1.0
    T = np.arange(0, 3800, DT)
    sim = OneHot()
    rec = {k: np.zeros(len(T)) for k in
           ["BTN1","BTN2","BTN3","BTN4","Q1","Q2","Q3","Q4","PORN"]}
    route = []
    for ti, t in enumerate(T):
        btn = [0,0,0,0]
        for (te, lbl, bp) in EVENTS:
            if te <= t < te + TAP_MS:
                btn = [max(a,b) for a,b in zip(btn, bp)]
        for (te, lbl, bp) in EVENTS:            # contact bounce, first 8 ms
            if any(bp) and te <= t < te+8 and int(t-te) % 2 == 0:
                btn = [0,0,0,0]
        porn = t < POR_MS
        SET, RST, Q = sim.step(btn, porn)
        for i in range(4):
            rec[f"BTN{i+1}"][ti]=btn[i]; rec[f"Q{i+1}"][ti]=Q[i]
        rec["PORN"][ti] = 1 if porn else 0
        route.append(relay_route(Q))

    print("="*68); print(" one-hot mic selector - event sequence"); print("="*68)
    got = []
    for (te, lbl, _) in EVENTS:
        idx = min(int((te+TAP_MS+30)/DT), len(T)-1)
        Q = [int(rec[f"Q{i+1}"][idx]) for i in range(4)]
        got.append(relay_route(Q))
        print(f" t={te:5d} ms  {lbl:26s}  Q={Q}   {relay_route(Q)}")
    print("="*68)
    exp = ["mic MUTED (no relay)", "mic -> LAPTOP 1", "mic -> LAPTOP 2",
           "mic -> LAPTOP 3", "mic -> LAPTOP 4", "mic -> LAPTOP 4",
           "mic MUTED (no relay)", "mic MUTED (no relay)"]
    print(f"\n matches requested behaviour: {'YES' if got==exp else 'NO'}")
    for e,g,(te,lbl,_) in zip(exp,got,EVENTS):
        print(f"   {'ok ' if e==g else 'XX '} {lbl:26s} expect '{e}'  got '{g}'")

    fig, axes = plt.subplots(5, 1, figsize=(11, 8), sharex=True)
    def band(ax, sig, color, label):
        ax.fill_between(T, 0, sig, step="pre", color=color, alpha=.85)
        ax.set_ylim(-0.2, 1.2); ax.set_yticks([])
        ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=9)
    band(axes[0], rec["PORN"], "#f85149", "PORN")
    for i in range(4):
        band(axes[i+1], rec[f"BTN{i+1}"], "#8b949e", f"SW{i+2}\n(NB{i+1})")
        a2 = axes[i+1].twinx(); a2.plot(T, rec[f"Q{i+1}"], color="#2ea043", lw=2)
        a2.set_ylim(-0.2,1.2); a2.set_yticks([0,1]); a2.set_ylabel(f"Q{i+1}", color="#2ea043")
    for (te,lbl,_) in EVENTS:
        for ax in axes: ax.axvline(te, color="#ccc", lw=.6, ls=":")
        axes[0].annotate(lbl, (te, 1.35), fontsize=7.5, rotation=25, va="bottom")
    axes[-1].set_xlabel("time  [ms]")
    axes[0].set_title("SELECT_LOGIC - grey = button press, green = latch output Qn "
                      "(POR holds every RST high for the first 140 ms)")
    fig.tight_layout(); fig.savefig(f"{OUT}/plots/E_select_logic.png", dpi=110); plt.close(fig)
    print("\n wrote plots/E_select_logic.png")

    # ---- standalone video
    FPS = 25
    frames = list(range(0, len(T), int(1000/FPS/DT)))
    figv = plt.figure(figsize=(12.8, 7.2), dpi=100); figv.patch.set_facecolor("#0e1116")
    gsl = figv.add_gridspec(1,2, width_ratios=[1.15,1], left=.06, right=.97, top=.82, bottom=.1, wspace=.18)
    axT = figv.add_subplot(gsl[0]); axS = figv.add_subplot(gsl[1])
    ttl = figv.text(.5,.94,"", ha="center", fontsize=18, color="#e6edf3", weight="bold")
    sub = figv.text(.5,.875,"", ha="center", fontsize=12, color="#7ee787")
    def vframe(fi):
        ti = frames[fi]; t = T[ti]
        for a in (axT, axS):
            a.clear(); a.set_facecolor("#161b22")
            for s in a.spines.values(): s.set_color("#3a434f")
            a.tick_params(colors="#9aa4b2")
        w = (T >= t-1200) & (T <= t)
        rows = ["PORN","BTN1","Q1","BTN2","Q2","BTN3","Q3","BTN4","Q4"]
        cols = {"PORN":"#f85149","BTN1":"#8b949e","BTN2":"#8b949e","BTN3":"#8b949e",
                "BTN4":"#8b949e","Q1":"#2ea043","Q2":"#2ea043","Q3":"#2ea043","Q4":"#2ea043"}
        for k,name in enumerate(rows):
            y0 = len(rows)-k
            axT.fill_between(T[w], y0, y0+rec[name][w]*0.8, step="pre", color=cols[name], alpha=.85)
            axT.text(t-1200, y0+0.3, name, color="#c9d1d9", fontsize=9, ha="left")
        axT.set_xlim(t-1200, t+30); axT.set_ylim(0.5, len(rows)+1.2)
        axT.set_yticks([]); axT.set_xlabel("time  [ms]", color="#9aa4b2")
        axT.axvline(t, color="#58a6ff", lw=1)
        Q = [int(rec[f"Q{i+1}"][ti]) for i in range(4)]
        axS.set_xlim(0,10); axS.set_ylim(0,10); axS.axis("off")
        axS.text(1.2, 9.2, "HEADSET MIC", color="#e6edf3", fontsize=12, weight="bold")
        axS.plot([2.0,2.0],[1,8.8], color="#8b949e", lw=3)
        for i in range(4):
            y = 7.5 - i*1.9; onc = Q[i]==1
            axS.add_patch(plt.Rectangle((4.3,y-.45),1.4,.9, color="#2ea043" if onc else "#30363d"))
            axS.text(5.0, y, "K"+str(i+1), ha="center", va="center",
                     color="#0e1116" if onc else "#8b949e", fontsize=10, weight="bold")
            axS.text(7.2, y, f"LAPTOP {i+1}", va="center",
                     color="#7ee787" if onc else "#6e7681", fontsize=12,
                     weight="bold" if onc else "normal")
            if onc:
                axS.plot([2.0,4.3],[y,y], color="#2ea043", lw=3)
                axS.plot([5.7,6.9],[y,y], color="#2ea043", lw=3)
            else:
                axS.plot([2.0,4.3],[y,y], color="#30363d", lw=2, ls=":")
        axS.text(5.0, 0.2, relay_route(Q), ha="center",
                 color="#f85149" if 1 not in Q else "#7ee787", fontsize=14, weight="bold")
        cur = ""
        for (te,lbl,_) in EVENTS:
            if t >= te: cur = lbl
        ttl.set_text("One-hot mic selector - single-press sequence")
        porn = "  |  POR active (mic force-muted)" if t < POR_MS else ""
        sub.set_text(f"t = {t:5.0f} ms   |   last action: {cur}{porn}")
        return []
    ani = FuncAnimation(figv, vframe, frames=len(frames), interval=1000/FPS)
    ani.save(f"{OUT}/MeetingHub-4-v2-mic-selector.mp4",
             writer=FFMpegWriter(fps=FPS, bitrate=3000, codec="libx264"),
             savefig_kwargs={"facecolor": figv.get_facecolor()})
    print(" wrote MeetingHub-4-v2-mic-selector.mp4")


if __name__ == "__main__":
    _run()
