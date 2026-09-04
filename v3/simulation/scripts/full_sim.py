"""
MeetingHub-4 v3 - end-to-end simulation video (single-axes, robust render).

Chapters:  0 what the board is  ->  1 power-up + POR (muted)  ->  2 the KVM
button-sequence timeline  ->  3 mic routing / crosstalk  ->  4 scorecard.
"""
import os, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg
from mna import Circuit
from select_logic import OneHot, route

plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
OUT = os.path.join(os.path.dirname(__file__), "..")
BG, FG, GR, RD, BL, GY = "#0e1116", "#e6edf3", "#2ea043", "#f85149", "#58a6ff", "#8b949e"

# POR transient
c = Circuit()
c.V("VBUS", "p5", "0", pwl=[(0, 0), (8e-3, 5.0), (5, 5.0)])
c.C("C5", "p5", "porn", 10e-6); c.R("Reff", "porn", "0", 20e3)
por = c.tran(1.5, 5e-4)
PT, PPORN, PVBUS = por["t"] * 1e3, por["porn"], por["p5"]
PWIN = PT[PPORN > 3.15][-1] if (PPORN > 3.15).any() else 0

# one-hot sequence
EVENTS = [(0, "power on", [0, 0, 0, 0]), (600, "tap SW1  ->  NB1", [1, 0, 0, 0]),
          (1200, "tap SW2  ->  NB2", [0, 1, 0, 0]), (1800, "tap SW3  ->  NB3", [0, 0, 1, 0]),
          (2400, "tap SW4  ->  NB4", [0, 0, 0, 1]), (3100, "hold SW2 + SW3", [0, 1, 1, 0]),
          (3700, "release", [0, 0, 0, 0])]
DT, TAP, POR_MS = 2.0, 60, 130
T = np.arange(0, 4300, DT); sim = OneHot()
Q = np.zeros((len(T), 4)); B = np.zeros((len(T), 4)); PN = np.zeros(len(T))
for i, t in enumerate(T):
    btn = [0, 0, 0, 0]
    for te, _, bp in EVENTS:
        if te <= t < te + TAP:
            btn = [max(a, b) for a, b in zip(btn, bp)]
    _, _, q = sim.step(btn, t < POR_MS)
    Q[i], B[i], PN[i] = q, btn, (t < POR_MS)

SCORE = json.load(open(f"{OUT}/validation_results.json"))
NPASS = sum(x["pass"] for x in SCORE)
M = {x["check"].split()[0]: x for x in SCORE}

FPS = 25
CH = [("what it is", 5), ("power-up + POR", 6), ("KVM button sequence", 12),
      ("mic routing", 6), ("scorecard", 8)]
BND = np.cumsum([0] + [d for _, d in CH])
DUR = BND[-1]
NF = int(DUR * FPS)

fig = plt.figure(figsize=(12.8, 7.2), dpi=100); fig.patch.set_facecolor(BG)
ax = fig.add_axes([0.07, 0.09, 0.86, 0.66]); ax.set_facecolor("#161b22")
ttl = fig.text(0.5, 0.93, "", ha="center", fontsize=19, color=FG, weight="bold")
sub = fig.text(0.5, 0.85, "", ha="center", fontsize=12.5, color=GR)
nav = fig.text(0.07, 0.033, "", fontsize=9.5, color=GY, family="monospace")


def relaydiag(q, tcur=None):
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.text(1.3, 9.4, "HEADSET MIC", color=FG, fontsize=13, weight="bold")
    ax.plot([2, 2], [0.6, 9.0], color=GY, lw=3)
    for i in range(4):
        y = 7.7 - i * 1.95; on = q[i] == 1
        ax.add_patch(plt.Rectangle((4.3, y - .45), 1.5, .9, color=GR if on else "#30363d"))
        ax.text(5.05, y, f"K{i+1}", ha="center", va="center", color=BG if on else GY,
                fontsize=11, weight="bold")
        ax.text(7.5, y, f"NOTEBOOK {i+1}", va="center", fontsize=13,
                color="#7ee787" if on else "#6e7681", weight="bold" if on else "normal")
        ax.plot([2, 4.3], [y, y], color=GR if on else "#30363d", lw=3 if on else 2,
                ls="-" if on else ":")
        if on:
            ax.plot([5.8, 7.1], [y, y], color=GR, lw=3)
    ax.text(5.0, -0.2, route(q), ha="center", fontsize=15, weight="bold",
            color=RD if 1 not in q else "#7ee787")


def frame(fi):
    t = fi / FPS
    ci = int(np.searchsorted(BND, t, "right") - 1); ci = min(ci, len(CH) - 1)
    local = (t - BND[ci]) / CH[ci][1]
    ax.clear(); ax.set_facecolor("#161b22")
    for s in ax.spines.values():
        s.set_color("#3a434f")
    ax.tick_params(colors="#9aa4b2")
    nav.set_text("   ".join((">" if k == ci else " ") + f" {n}" for k, (n, _) in enumerate(CH)))

    if ci == 0:
        ttl.set_text("MeetingHub-4 v3  -  headset-mic KVM for 4 notebooks")
        sub.set_text("one headset mic  ->  routed to exactly one notebook   (audio goes to an external mixer)")
        ax.axis("off")
        for i, ln in enumerate([
            "each notebook 3.5 mm combo jack --[ TRRS Y-splitter ]--  headphones -> external mixer",
            "                                                        mic  -> MeetingHub-4 v3  (J2-J5)",
            "headset                        --[ Y-splitter ]-------   headphones -> external mixer",
            "                                                        mic  -> MeetingHub-4 v3  (J6)",
            "",
            "on the board:  4 buttons -> CD4043B one-hot latch -> 4x 2N7000 -> 4x G5V-1 signal relay",
            "power-on:      the POR resets every latch  ->  no relay  ->  mic muted",
            "power in:      USB-C 5 V, PTC + TVS + 5k1 CC pull-downs (works with any USB-C source)"]):
            ax.text(0.02, 0.92 - i * 0.115, ln, transform=ax.transAxes, family="monospace",
                    fontsize=11.5, color=FG if i >= 5 else "#9aa4b2")

    elif ci == 1:
        ttl.set_text("Power-up  -  the POR makes 'muted' deterministic")
        tt = 1.5 * local
        ax.plot(PT, PVBUS, color=BL, lw=2, label="VBUS (rail)")
        ax.plot(PT, PPORN, color=RD, lw=2, label="PORN (holds every RST high)")
        ax.axhline(3.15, color=GY, ls=":", lw=1)
        ax.text(950, 3.35, "RST seen high above ~3.1 V", color=GY, fontsize=9)
        ax.axvline(tt * 1e3, color=FG, lw=1)
        ax.set_xlim(0, 1500); ax.set_ylim(-0.3, 6)
        ax.set_xlabel("time  [ms]", color="#9aa4b2"); ax.set_ylabel("V", color="#9aa4b2")
        ax.legend(loc="lower right", facecolor="#161b22", edgecolor="#3a434f", labelcolor=FG)
        sub.set_text(f"C5 10 uF + R11 100 k  ->  RST held ~{PWIN:.0f} ms after the rail settles  ->  Q1..Q4 = 0   "
                     f"(P3: still muted through a 50 ms soft-start ramp)")

    elif ci == 2:
        ttl.set_text("One press  =  select that notebook, drop the others")
        tms = local * T[-1]
        idx = min(int(tms / DT), len(T) - 1)
        w = (T >= tms - 1500) & (T <= tms + 20)
        rows = ["PORN", "SW1", "Q1", "SW2", "Q2", "SW3", "Q3", "SW4", "Q4"]
        for k, nm in enumerate(rows):
            y0 = len(rows) - k
            if nm == "PORN": sig, col = PN, RD
            elif nm.startswith("SW"): sig, col = B[:, int(nm[2]) - 1], GY
            else: sig, col = Q[:, int(nm[1]) - 1], GR
            ax.fill_between(T[w], y0, y0 + sig[w] * 0.8, step="pre", color=col, alpha=.85)
            ax.text(tms - 1490, y0 + 0.26, nm, color="#c9d1d9", fontsize=9)
        ax.set_xlim(tms - 1500, tms + 20); ax.set_ylim(0.5, len(rows) + 1)
        ax.set_yticks([]); ax.set_xlabel("time  [ms]", color="#9aa4b2")
        ax.axvline(tms, color=BL, lw=1)
        cur = next((lbl for te, lbl, _ in EVENTS if tms >= te), "")
        r = route(Q[idx])
        sub.set_text(f"t = {tms:4.0f} ms    {cur}    ->    {r}"
                     + ("     |  POR active" if tms < POR_MS else ""))

    elif ci == 3:
        ttl.set_text("Mic routing  -  passive, lossless, de-selected NBs still 'mic present'")
        relaydiag([0, 1, 0, 0])
        sub.set_text(f"through-path loss {M['MIC2']['measure'].split()[0]} dB    "
                     f"crosstalk {M['MIC3']['measure'].split(',')[0]}    "
                     f"electret bias {M['MIC1']['measure'].split()[0]} V    "
                     f"de-selected NB reads {M['MIC7']['measure'].split()[0]} V (2k2 on NC)")

    else:
        ttl.set_text(f"Requirement check  -  {NPASS} / {len(SCORE)} pass")
        sub.set_text("full sheet: docs/v3-simulation-validation.md")
        ax.axis("off")
        shown = [x for x in SCORE if not x["check"].startswith("S ")]
        for i, x in enumerate(shown):
            ax.text(0.01, 0.97 - i * 0.072, "PASS" if x["pass"] else "FAIL",
                    transform=ax.transAxes, family="monospace", fontsize=10,
                    color=GR if x["pass"] else RD, weight="bold")
            ax.text(0.09, 0.97 - i * 0.072, x["check"][:80], transform=ax.transAxes,
                    family="monospace", fontsize=10, color=FG)
    return []


ani = FuncAnimation(fig, frame, frames=NF, interval=1000 / FPS)
ani.save(f"{OUT}/MeetingHub-4-v3-full-simulation.mp4",
         writer=FFMpegWriter(fps=FPS, bitrate=3500, codec="libx264"),
         savefig_kwargs={"facecolor": BG})
print(f"wrote MeetingHub-4-v3-full-simulation.mp4  ({DUR}s, {NF} frames)")
