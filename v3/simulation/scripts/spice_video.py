#!/usr/bin/env python3
"""Render the MeetingHub-4 v3 component-level simulation to an mp4.

Uses the REAL ngspice traces written by spice_sim.py:
  spice/selector_tran.dat   full one-hot sequence transient
  spice/mic_ac.dat          routed mic path AC response
  spice/mic_xtalk.dat       crosstalk to a de-selected notebook
  spice_results.json        25-check scorecard

Chapters: 0 what it is | 1 power-up + POR | 2 the KVM button sequence |
          3 mic routing (DC + AC) | 4 scorecard
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg

SIM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

BG, FG, GY = "#0d1117", "#e6edf3", "#8b949e"
GR, RD, BL, YE = "#3fb950", "#f85149", "#58a6ff", "#d29922"


def load_wrdata(path, names):
    """ngspice wrdata writes columns  t v1 t v2 t v3 ...  -> {name: array}, plus 't'."""
    raw = np.loadtxt(path)
    out = {"t": raw[:, 0]}
    for i, nm in enumerate(names):
        out[nm] = raw[:, 2 * i + 1]
    return out


SEL = load_wrdata(f"{SIM}/spice/selector_tran.dat",
                  ["porn", "qo1", "qo2", "qo3", "qo4", "btn1", "btn2", "btn3",
                   "btn4", "nb1", "nb2", "nb3", "nb4", "hmic"])
AC = np.loadtxt(f"{SIM}/spice/mic_ac.dat")          # f, vdb(nb2), f, vdb(nb1)
XT = np.loadtxt(f"{SIM}/spice/mic_xtalk.dat")       # f, vdb(nb1)
SCORE = json.load(open(f"{SIM}/spice_results.json"))
NPASS = sum(x["pass"] for x in SCORE)
M = {x["check"].split()[0] + " " + x["check"].split()[1] if len(x["check"].split()) > 1
     else x["check"]: x for x in SCORE}


def qstate(t):
    i = min(int(np.searchsorted(SEL["t"], t)), len(SEL["t"]) - 1)
    return [SEL[f"qo{n}"][i] > 2.5 for n in (1, 2, 3, 4)]


def route_txt(q):
    on = [n for n, v in enumerate(q, 1) if v]
    return f"headset mic  ->  NOTEBOOK {on[0]}" if len(on) == 1 else "headset mic  ->  (muted)"


EVENTS = [(0.00, "power on"), (0.40, "tap SW1  ->  NB1"), (0.90, "tap SW2  ->  NB2"),
          (1.40, "tap SW3  ->  NB3"), (1.90, "tap SW4  ->  NB4"),
          (2.50, "hold SW2 + SW3  ->  mute"), (2.70, "release")]

FPS = 25
CH = [("what it is", 4), ("power-up + POR", 7), ("KVM button sequence", 16),
      ("mic routing", 9), ("scorecard", 6)]
BND = np.cumsum([0] + [d for _, d in CH])
NF = int(BND[-1] * FPS)

fig, ax = plt.subplots(figsize=(12, 6.75), dpi=100)
fig.patch.set_facecolor(BG)
ttl = fig.text(0.5, 0.945, "", ha="center", color=FG, fontsize=17, weight="bold")
sub = fig.text(0.5, 0.895, "", ha="center", color=GY, fontsize=11)
nav = fig.text(0.5, 0.02, "", ha="center", color=GY, fontsize=9, family="monospace")


def dark(a):
    a.set_facecolor("#161b22")
    for s in a.spines.values():
        s.set_color("#3a434f")
    a.tick_params(colors=GY, labelsize=8)
    a.xaxis.label.set_color(GY)
    a.yaxis.label.set_color(GY)
    a.title.set_color(FG)


def relaydiag(a, q, note=""):
    a.set_xlim(0, 10)
    a.set_ylim(0, 10)
    a.axis("off")
    a.text(1.4, 9.3, "HEADSET MIC", color=FG, fontsize=12, weight="bold")
    a.plot([2, 2], [0.7, 8.7], color=GY, lw=3)
    for i in range(4):
        y = 7.5 - i * 1.9
        on = q[i]
        a.add_patch(plt.Rectangle((4.3, y - .42), 1.5, .84, color=GR if on else "#30363d"))
        a.text(5.05, y, f"K{i+1}", ha="center", va="center", color=BG if on else GY,
               fontsize=10, weight="bold")
        a.text(7.5, y, f"NOTEBOOK {i+1}", va="center", fontsize=12,
               color="#7ee787" if on else "#6e7681", weight="bold" if on else "normal")
        a.plot([2, 4.3], [y, y], color=GR if on else "#30363d", lw=3 if on else 1.5,
               ls="-" if on else ":")
        if on:
            a.plot([5.8, 7.0], [y, y], color=GR, lw=3)
        else:
            a.text(6.4, y - 0.7, "2k2->GND (~1.1 V, 'mic present')", ha="center",
                   fontsize=7.5, color=GY, style="italic")
    a.text(5.0, -0.1, route_txt(q), ha="center", fontsize=14, weight="bold",
           color=RD if sum(q) != 1 else "#7ee787")
    if note:
        a.text(5.0, 9.8, note, ha="center", fontsize=9, color=YE)


def frame(fi):
    t = fi / FPS
    ci = min(int(np.searchsorted(BND, t, "right") - 1), len(CH) - 1)
    local = t - BND[ci]
    ax.clear()
    ax.set_position([0.09, 0.13, 0.84, 0.7])
    nav.set_text("   ".join((">" if k == ci else " ") + f"{n}" for k, (n, _) in enumerate(CH)))

    if ci == 0:
        ax.axis("off")
        ttl.set_text("MeetingHub-4 v3  -  headset-mic KVM, simulated with the real parts")
        sub.set_text("ngspice + datasheet models: 1N4148 - 2N7000 - CD4043B - Omron G5V-1 - electret")
        for i, ln in enumerate([
            "one headset mic  ->  routed to exactly ONE of four notebooks, KVM-style",
            "4 buttons  ->  CD4043B one-hot NOR latch  ->  4x 2N7000  ->  4x G5V-1 signal relay",
            "power-on / two buttons held  =  no relay  =  mic muted (deterministic, POR-backed)",
            "de-selected notebooks see 2k2 -> GND on the relay NC  =  '.mic present, silent'",
            "audio (headphones) is split off with a Y-cable to an external mixer - not on this board",
        ]):
            ax.text(0.5, 0.8 - i * 0.14, ln, transform=ax.transAxes, ha="center",
                    fontsize=11.5, color=FG if i < 4 else GY)
        return

    if ci == 1:
        dark(ax)
        ttl.set_text("Power-up  -  the POR pins every RST high until the rail is up")
        sub.set_text("C5 10 uF / R11 100 k  +  D22-25  ->  every latch forced to 0  ->  muted")
        tm = min(local / CH[1][1], 1.0) * 0.30
        m = SEL["t"] <= max(tm, 0.02)
        ax.plot(SEL["t"][m] * 1e3, SEL["porn"][m], color=YE, lw=2, label="PORN")
        for n, c in zip((1, 2, 3, 4), (GR, BL, "#bc8cff", "#ff9bce")):
            ax.plot(SEL["t"][m] * 1e3, SEL[f"qo{n}"][m], color=c, lw=1.3, label=f"Q{n}")
        ax.axhline(2.5, color=RD, ls="--", lw=1, alpha=.6)
        ax.text(0.3, 2.65, "CD4043B logic threshold ~2.5 V", color=RD, fontsize=8)
        ax.set_xlim(0, 300)
        ax.set_ylim(-0.3, 5.3)
        ax.set_xlabel("time  [ms]")
        ax.set_ylabel("volts")
        ax.legend(loc="upper right", fontsize=8, ncol=5, facecolor="#161b22",
                  edgecolor="#3a434f", labelcolor=FG)
        ax.set_title("PORN holds > 2.5 V through the ramp; Q1-Q4 never leave 0  ->  no relay")
        return

    if ci == 2:
        dark(ax)
        ttl.set_text("KVM button sequence  -  one-hot, exclusive")
        tcur = 0.15 + min(local / CH[2][1], 1.0) * 2.85
        m = SEL["t"] <= tcur
        for n, c in zip((1, 2, 3, 4), (GR, BL, "#bc8cff", "#ff9bce")):
            ax.plot(SEL["t"][m], SEL[f"qo{n}"][m], color=c, lw=1.8, label=f"Q{n} (K{n})")
        ax.set_xlim(0, 3.0)
        ax.set_ylim(-0.4, 6.2)
        ax.set_xlabel("time  [s]")
        ax.set_ylabel("latch output  [V]")
        for te, lbl in EVENTS:
            if tcur >= te:
                ax.axvline(te, color=GY, ls=":", lw=0.8, alpha=.5)
        ax.axvline(tcur, color=FG, lw=1)
        ax.legend(loc="upper left", ncol=4, fontsize=8, facecolor="#161b22",
                  edgecolor="#3a434f", labelcolor=FG)
        cur = next((l for tt, l in reversed(EVENTS) if tcur >= tt - 0.02), "")
        q = qstate(tcur)
        ax.set_title(f"t = {tcur:4.2f} s    {cur}")
        sub.set_text(route_txt(q) + ("      |  POR" if tcur < 0.13 else ""))
        return

    if ci == 3:
        dark(ax)
        ttl.set_text("Mic routing  -  passive, lossless, de-selected NBs stay 'present'")
        half = CH[3][1] / 2
        if local < half:                       # DC bias bar chart
            vsel = float(M["MIC1 electret"]["measure"].split()[0])
            vdes = float(M["MIC7 a"]["measure"].split()[0]) if "MIC7 a" in M \
                else float([x for x in SCORE if x["check"].startswith("MIC7")][0]["measure"].split()[0])
            bars = [("selected NB\n(live electret)", vsel, GR),
                    ("de-selected NB\n(2k2 -> GND)", vdes, BL),
                    ("de-selected,\nNC open (old / v2)", 2.2, RD)]
            for i, (lab, v, c) in enumerate(bars):
                ax.bar(i, v, 0.6, color=c)
                ax.text(i, v + 0.06, f"{v:.2f} V", ha="center", color=FG, fontsize=11, weight="bold")
                ax.text(i, -0.25, lab, ha="center", color=GY, fontsize=9)
            ax.axhspan(0.8, 2.0, color=GR, alpha=.10)
            ax.text(2.6, 1.4, "codec reads\n'headset mic\npresent'", fontsize=8, color=GR, ha="center")
            ax.axhline(2.2, color=RD, ls="--", lw=1, alpha=.5)
            ax.text(0.0, 2.32, "full bias rail = 'no microphone'", fontsize=8, color=RD)
            ax.set_xticks([])
            ax.set_ylim(0, 2.7)
            ax.set_ylabel("DC at the notebook mic pin  [V]")
            ax.set_title("The 2k2 on the relay NC keeps every idle notebook looking like a live mic")
            sub.set_text("ngspice .op with the electret JFET + G5V-1 contact + notebook bias")
        else:                                  # AC response + crosstalk
            f1, g1 = AC[:, 0], AC[:, 1]
            f2, g2 = AC[:, 2], AC[:, 3]
            fx, gx = XT[:, 0], XT[:, 1]
            ref = g1[np.argmin(np.abs(f1 - 1e3))]
            ax.semilogx(f1, g1 - ref, color=GR, lw=2, label="routed notebook (K closed)")
            ax.semilogx(fx, gx, color=RD, lw=2, label="de-selected notebook (crosstalk)")
            ax.axvspan(300, 3400, color=BL, alpha=.12)
            ax.text(1000, 3, "voice band", color=BL, fontsize=9, ha="center")
            ax.set_xlim(20, 2e5)
            ax.set_ylim(-95, 8)
            ax.set_xlabel("frequency  [Hz]")
            ax.set_ylabel("dB")
            ax.legend(loc="lower left", fontsize=8.5, facecolor="#161b22",
                      edgecolor="#3a434f", labelcolor=FG)
            ax.set_title("Flat & lossless to the selected notebook, < -60 dB to the rest")
            sub.set_text("ngspice .ac  -  electret source impedance + 10 pF across the open NO contact")
        return

    # scorecard
    dark(ax)
    ax.axis("off")
    ttl.set_text(f"Component-level simulation  -  {NPASS} / {len(SCORE)} checks pass")
    sub.set_text("full detail: docs/v3-simulation-validation.md")
    groups = {}
    for x in SCORE:
        groups.setdefault(x["check"].split()[0], []).append(x["pass"])
    order = ["S", "P", "MIC1", "MIC2", "MIC3", "MIC4", "MIC5", "MIC6", "MIC7", "PW1", "PW2", "PW3", "PW4"]
    seen = []
    y = 0.92
    col = 0
    for k in ["S", "P", "MIC", "PW"]:
        ks = [g for g in groups if g.startswith(k)]
        n = sum(len(groups[g]) for g in ks)
        p = sum(sum(groups[g]) for g in ks)
        label = {"S": "one-hot selector sequence", "P": "power-on reset vs ramp rate",
                 "MIC": "passive mic path + deselect detect", "PW": "power / USB-C / TVS"}[k]
        ax.text(0.12, y, ("PASS" if p == n else "----"), transform=ax.transAxes,
                color=GR if p == n else RD, fontsize=13, weight="bold", family="monospace")
        ax.text(0.26, y, f"{label}", transform=ax.transAxes, color=FG, fontsize=12)
        ax.text(0.88, y, f"{p}/{n}", transform=ax.transAxes, color=GY, fontsize=12, ha="right")
        y -= 0.16
    ax.text(0.5, 0.06, "ngspice-42  -  datasheet models  -  1N4148 / 2N7000 / CD4043B / G5V-1 / electret",
            transform=ax.transAxes, ha="center", color=GY, fontsize=9)


if __name__ == "__main__":
    ani = FuncAnimation(fig, frame, frames=NF, interval=1000 / FPS)
    out = f"{SIM}/MeetingHub-4-v3-spice-simulation.mp4"
    ani.save(out, writer=FFMpegWriter(fps=FPS, bitrate=2600))
    print(f"wrote {out}  ({BND[-1]:.0f}s, {NF} frames)")
