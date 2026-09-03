"""
Renders v2/simulation/MeetingHub-4-v2-simulation.mp4 — a narrated run of the
three simulations that decide whether the board meets its requirements:

  scene 1  Power-on reset      : PORN decays, mic stays MUTED past the CD4043B
                                 threshold, then the latch is free -> requirement met
  scene 2  Volume-pot sweep    : RV1 turned full-CCW -> full-CW, headset waveform
                                 grows from silence to max  (bug-1 fix: CW = louder)
  scene 3  Frequency response  : swept 10 Hz -> 20 kHz, Bode trace + live tone,
                                 flat across the voice band into a 32 ohm headset
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mna import Circuit, db
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

from validate import build_chain, FSWP
OUT = os.path.join(os.path.dirname(__file__), "..", "MeetingHub-4-v2-simulation.mp4")
FPS = 25

# ---------------------------------------------------------------- scene 1 data
def por_curve():
    c = Circuit()
    c.V("V5", "p5", "0", pwl=[(0,0),(1e-4,5),(3,5)])
    c.C("C24", "p5", "porn", 10e-6)
    c.R("R37", "porn", "0", 100e3)
    c.R("Rload", "porn", "0", 25e3)          # D26-29 -> 4x 100k RST pulldowns
    r = c.tran(1.2, 1e-3, uic={"porn": 0.0})
    return r["t"], r["porn"]
T1, PORN = por_curve()
THR = 2.5
TW = T1[np.where(PORN >= THR)[0][-1]]

# ---------------------------------------------------------------- scene 2 data
FRAC = np.concatenate([np.linspace(0.0, 1.0, 60), np.ones(12)])
G2 = []
for fr in FRAC:
    c = build_chain(nsrc=1, rv_frac=fr, master_frac=1.0, load=32.0, src_ac=[0.447])
    _, rr = c.ac([1e3]); G2.append(rr["j6t"][0])
G2 = np.array(G2)          # complex gain*Vin at J6.T for a 0.447 Vpk, 1 kHz tone

# ---------------------------------------------------------------- scene 3 data
c = build_chain(nsrc=1, rv_frac=1.0, master_frac=1.0, load=32.0, src_ac=[0.447])
F3, R3 = c.ac(FSWP)
H3 = R3["j6t"]
ref1k = np.abs(np.interp(1e3, F3, H3))
REL3 = db(np.abs(H3)/ref1k)
SWEEPF = np.logspace(1, np.log10(20e3), 90)

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
fig.patch.set_facecolor("#0e1116")
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=0.42, wspace=0.22,
                      left=0.08, right=0.96, top=0.86, bottom=0.10)
axMain = fig.add_subplot(gs[0, :])
axL = fig.add_subplot(gs[1, 0])
axR = fig.add_subplot(gs[1, 1])
for a in (axMain, axL, axR):
    a.set_facecolor("#161b22")
    a.tick_params(colors="#9aa4b2"); a.grid(alpha=.18, color="#5b6673")
    for s in a.spines.values(): s.set_color("#3a434f")
title = fig.text(0.5, 0.955, "", ha="center", va="top", fontsize=18, color="#e6edf3", weight="bold")
subtitle = fig.text(0.5, 0.905, "", ha="center", va="top", fontsize=12, color="#7ee787")
foot = fig.text(0.5, 0.028, "MeetingHub-4 v2  ·  local MNA engine  ·  LTspice net in v2/simulation/ltspice/",
                ha="center", fontsize=9, color="#5b6673")

SC1 = int(6.5*FPS); SC2 = len(FRAC)+int(1.2*FPS); SC3 = len(SWEEPF)+int(1.4*FPS)
NF = SC1 + SC2 + SC3

def clear(ax):
    ax.clear(); ax.set_facecolor("#161b22")
    ax.tick_params(colors="#9aa4b2"); ax.grid(alpha=.18, color="#5b6673")
    for s in ax.spines.values(): s.set_color("#3a434f")

def frame(i):
    # ============================================================= SCENE 1
    if i < SC1:
        k = min(int(round(i*(len(T1)-1)/(SC1-1))), len(T1)-1)
        tt = T1[:k+1]*1e3; pp = PORN[:k+1]
        clear(axMain)
        axMain.plot(T1*1e3, PORN, color="#30363d", lw=1)
        axMain.plot(tt, pp, color="#58a6ff", lw=2.5)
        axMain.axhline(THR, color="#f85149", ls="--", lw=1.2)
        axMain.axvspan(0, TW*1e3, color="#f85149", alpha=.10)
        axMain.text(TW*1e3+20, 4.6, "reset window", color="#f85149", ha="left", fontsize=10)
        axMain.set_xlim(0, 1200); axMain.set_ylim(0, 5.2)
        axMain.set_xlabel("time  [ms]", color="#9aa4b2"); axMain.set_ylabel("PORN  [V]", color="#9aa4b2")
        now = T1[k]
        muted = now <= TW
        clear(axL)
        axL.set_xlim(0,1); axL.set_ylim(0,1); axL.axis("off")
        axL.text(0.5, 0.62, "MIC" , ha="center", fontsize=22, color="#e6edf3", weight="bold")
        axL.text(0.5, 0.32, "MUTED" if muted else "ARMED", ha="center", fontsize=30,
                 color="#f85149" if muted else "#7ee787", weight="bold")
        clear(axR)
        axR.set_xlim(0,1); axR.set_ylim(0,1); axR.axis("off")
        axR.text(0.02, 0.85, "Q1..Q4  (CD4043B latch outputs)", color="#9aa4b2", fontsize=10)
        for j in range(4):
            axR.add_patch(plt.Rectangle((0.05+j*0.16, 0.45), 0.12, 0.12, color="#30363d"))
            axR.text(0.11+j*0.16, 0.35, f"K{j+1}", ha="center", color="#9aa4b2", fontsize=9)
        axR.text(0.02, 0.15, "Q1..Q4 = 0 at power-up (POR) and stay 0\nuntil a select button is pressed  ->  mic muted",
                 color="#9aa4b2", fontsize=9)
        title.set_text("Scene 1 / 3   ·   Power-on reset")
        subtitle.set_text(f"C24 10uF + R37 100k  ·  reset held {TW*1e3:.0f} ms  ( > 20 ms required )   "
                          f"·   t = {now*1e3:6.0f} ms")
        return []
    # ============================================================= SCENE 2
    j = i - SC1
    if j < SC2:
        k = min(j, len(FRAC)-1)
        fr = FRAC[k]
        gain_c = G2[k]
        tono = np.linspace(0, 3e-3, 600)
        vin = 0.447*np.sin(2*np.pi*1e3*tono)
        vout = np.abs(gain_c)*np.sin(2*np.pi*1e3*tono + np.angle(gain_c))
        clear(axMain)
        axMain.plot(tono*1e3, vin, color="#484f58", lw=1.4, label="laptop line in  (0.447 Vpk)")
        axMain.plot(tono*1e3, vout, color="#7ee787", lw=2.4, label="headset J6.T")
        axMain.set_ylim(-0.6, 0.6); axMain.set_xlim(0, 3)
        axMain.set_xlabel("time  [ms]", color="#9aa4b2"); axMain.set_ylabel("V (about VBIAS)", color="#9aa4b2")
        axMain.legend(loc="upper right", facecolor="#161b22", edgecolor="#3a434f", labelcolor="#c9d1d9")
        clear(axL)
        ang = (1-fr)*300 - 150         # -150 deg (CCW) .. +150 deg (CW)
        axL.set_xlim(-1.3,1.3); axL.set_ylim(-1.3,1.3); axL.set_aspect("equal"); axL.axis("off")
        th = np.linspace(0, 2*np.pi, 100)
        axL.plot(np.cos(th), np.sin(th), color="#30363d", lw=3)
        a = np.deg2rad(ang+90)
        axL.plot([0, np.cos(a)], [0, np.sin(a)], color="#58a6ff", lw=4)
        axL.text(0, -1.15, "RV1  volume", ha="center", color="#9aa4b2", fontsize=10)
        axL.text(-1.0, 1.05, "CCW\nmute", ha="center", color="#f85149", fontsize=8)
        axL.text(1.0, 1.05, "CW\nloud", ha="center", color="#7ee787", fontsize=8)
        clear(axR)
        axR.bar([0], [np.abs(gain_c)], width=0.5, color="#7ee787")
        axR.set_xlim(-0.6, 0.6); axR.set_ylim(0, 0.42); axR.set_xticks([])
        axR.set_ylabel("headset level  [Vpk]", color="#9aa4b2")
        axR.text(0, np.abs(gain_c)+0.02, f"{np.abs(gain_c)*1e3:.0f} mVpk", ha="center", color="#e6edf3")
        title.set_text("Scene 2 / 3   ·   Volume pot sweep  (v1 bug #1 fix)")
        subtitle.set_text(f"RV1 rotation {fr*100:3.0f}% CW   ·   full-CCW = wiper at VBIAS = silent, "
                          f"full-CW = wiper at signal = loud")
        return []
    # ============================================================= SCENE 3
    m = i - SC1 - SC2
    k = min(m, len(SWEEPF)-1)
    fcur = SWEEPF[k]
    relcur = np.interp(fcur, F3, REL3)
    clear(axMain)
    axMain.semilogx(F3, REL3, color="#30363d", lw=1.2)
    sel = F3 <= fcur
    axMain.semilogx(F3[sel], REL3[sel], color="#58a6ff", lw=2.6)
    axMain.plot([fcur], [relcur], "o", color="#f85149", ms=9)
    axMain.axhline(-3, color="#f85149", ls="--", lw=1)
    axMain.axvspan(300, 3400, color="#7ee787", alpha=.08)
    axMain.text(1000, 1.4, "voice band", color="#7ee787", ha="center", fontsize=9)
    axMain.set_xlim(10, 20e3); axMain.set_ylim(-15, 3)
    axMain.set_xlabel("frequency  [Hz]", color="#9aa4b2"); axMain.set_ylabel("dB re 1 kHz", color="#9aa4b2")
    tono = np.linspace(0, 5/max(fcur,10), 600)
    gain_c = np.interp(fcur, F3, np.abs(H3))
    clear(axL)
    axL.plot(tono*1e3, 0.447*np.sin(2*np.pi*fcur*tono), color="#484f58", lw=1.3)
    axL.plot(tono*1e3, gain_c*np.sin(2*np.pi*fcur*tono), color="#7ee787", lw=2.2)
    axL.set_ylim(-0.5, 0.5); axL.set_xlabel("time  [ms]", color="#9aa4b2")
    axL.set_ylabel("V", color="#9aa4b2")
    clear(axR)
    axR.set_xlim(0,1); axR.set_ylim(0,1); axR.axis("off")
    axR.text(0.02, 0.80, f"f  = {fcur:8.0f} Hz", color="#e6edf3", fontsize=13, family="monospace")
    axR.text(0.02, 0.60, f"|H| = {relcur:+5.2f} dB", color="#e6edf3", fontsize=13, family="monospace")
    axR.text(0.02, 0.40, f"gain = {gain_c/0.447:5.3f} x", color="#e6edf3", fontsize=13, family="monospace")
    axR.text(0.02, 0.15, "flat 100 Hz-20 kHz into 32 ohm\nLF roll-off from the 1 uF couplers",
             color="#9aa4b2", fontsize=9)
    title.set_text("Scene 3 / 3   ·   Frequency response into a 32 ohm headset")
    subtitle.set_text("swept 10 Hz -> 20 kHz   ·   -3 dB at ~44 Hz   ·   voice band flat within 1 dB")
    return []

ani = FuncAnimation(fig, frame, frames=NF, interval=1000/FPS, blit=False)
w = FFMpegWriter(fps=FPS, bitrate=3200, codec="libx264")
ani.save(OUT, writer=w, dpi=100,
         savefig_kwargs={"facecolor": fig.get_facecolor()})
print("wrote", OUT, f"({NF} frames, {NF/FPS:.1f} s)")
