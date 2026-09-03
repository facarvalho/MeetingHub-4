"""Plots from the ngspice (real-device-model) runs in ../spice/."""
import numpy as np, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
S = os.path.join(os.path.dirname(__file__), "..", "spice")
P = os.path.join(os.path.dirname(__file__), "..", "plots")

def cols(fn):
    d = np.loadtxt(os.path.join(S, fn))
    return [d[:, i] for i in range(d.shape[1])]

# ---- 1. VBIAS power-up + Zout
t, vbus, _, p5, _, vref, _, vbias = cols("power_vbias_tran.dat")
fz = np.loadtxt(os.path.join(S, "power_vbias_zout.dat"))
f, zout = fz[:, 0], fz[:, 1]
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(t*1e3, p5, label="+5V rail", color="tab:blue")
ax[0].plot(t*1e3, vbias, label="VBIAS", color="tab:green", lw=2)
ax[0].plot(t*1e3, vref, label="VBIAS_REF", color="tab:orange", ls="--")
ax[0].axhline(2.5, color="k", ls=":", lw=1); ax[0].set_xlim(0, 400)
ax[0].set_xlabel("ms"); ax[0].set_ylabel("V"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[0].set_title("VBIAS power-up (ngspice + LM358 model)")
ax[1].loglog(f, np.maximum(zout, 1e-3), color="tab:purple")
ax[1].axvspan(20, 20e3, color="g", alpha=.07)
ax[1].axvline(20e3, color="k", ls=":", lw=1)
ax[1].set_xlabel("Hz"); ax[1].set_ylabel("|Zout|  [ohm]"); ax[1].grid(alpha=.3, which="both")
ax[1].set_title("VBIAS Zout: <0.5 Ω in-band, benign 46 Ω peak @86 kHz (ultrasonic)")
ax[1].set_ylim(1e-2, 1e2)
fig.tight_layout(); fig.savefig(f"{P}/BOM_vbias.png", dpi=110); plt.close(fig)

# ---- 2. audio AC response
d = np.loadtxt(os.path.join(S, "audio_ac.dat"))
f = d[:, 0]; j6 = d[:, 1]; u1 = d[:, 3]; mx = d[:, 5]
ref = np.interp(1000, f, j6)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.semilogx(f, j6-ref, lw=2, label="headset J6.T (into 32 Ω)")
ax.axhline(-3, color="r", ls=":", lw=1); ax.axvspan(300, 3400, color="g", alpha=.08)
ax.set_xlabel("Hz"); ax.set_ylabel("dB re 1 kHz"); ax.set_ylim(-15, 3); ax.grid(alpha=.3, which="both")
ax.set_title("End-to-end frequency response — ngspice, NJM4580 + NJM4556A models")
ax.text(1000, 1.3, "voice band", ha="center", color="g", fontsize=9)
fig.tight_layout(); fig.savefig(f"{P}/BOM_audio_response.png", dpi=110); plt.close(fig)

# ---- 3. selector timing
d = np.loadtxt(os.path.join(S, "selector_tran.dat"))
t = d[:, 0]
porn, q1, q2, q3, q4 = d[:, 1], d[:, 3], d[:, 5], d[:, 7], d[:, 9]
b1, b2, b3, b4 = d[:, 11], d[:, 13], d[:, 15], d[:, 17]
fig, axes = plt.subplots(5, 1, figsize=(11, 8), sharex=True)
axes[0].plot(t, porn, color="tab:red"); axes[0].axhline(2.5, color="k", ls=":", lw=1)
axes[0].set_ylabel("PORN", rotation=0, ha="right", va="center")
for i, (q, b) in enumerate([(q1, b1), (q2, b2), (q3, b3), (q4, b4)]):
    axes[i+1].fill_between(t, 0, b, step="pre", color="#bbb", label="button")
    axes[i+1].plot(t, q, color="tab:green", lw=2, label=f"Q{i+1}")
    axes[i+1].set_ylabel(f"SW{i+2}\nQ{i+1}", rotation=0, ha="right", va="center")
    axes[i+1].set_ylim(-0.5, 5.5)
for a in axes:
    for x in (0.4, 0.9, 1.4, 1.9, 2.5): a.axvline(x, color="#ccc", ls=":", lw=.7)
axes[-1].set_xlabel("s"); axes[0].set_xlim(0, 3)
axes[0].set_title("One-hot selector — ngspice with CD4043B latch + 2N7000 + G5V-1 relay models")
fig.tight_layout(); fig.savefig(f"{P}/BOM_selector.png", dpi=110); plt.close(fig)

print("wrote BOM_vbias.png  BOM_audio_response.png  BOM_selector.png")
