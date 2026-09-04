"""MeetingHub-4 v3 - static result plots (POR transient, mic-path AC, scorecard)."""
import os, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mna import Circuit, db

OUT = os.path.join(os.path.dirname(__file__), "..")
plt.rcParams.update({"figure.facecolor": "white", "axes.grid": True,
                     "grid.alpha": .3})

# ---- P. power-on reset ------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5))
for ramp_ms, c in ((1.0, "#2ea043"), (50.0, "#f85149")):
    ck = Circuit()
    ck.V("VBUS", "p5", "0", pwl=[(0, 0), (ramp_ms*1e-3, 5), (5, 5)])
    ck.C("C5", "p5", "porn", 10e-6); ck.R("Reff", "porn", "0", 20e3)
    r = ck.tran(1.5, 2e-4)
    ax.plot(r["t"]*1e3, r["porn"], color=c, lw=2,
            label=f"PORN, {ramp_ms:.0f} ms VBUS ramp")
ck = Circuit(); ck.V("VBUS", "p5", "0", pwl=[(0, 0), (1e-3, 5), (5, 5)])
ck.C("C5", "p5", "porn", 10e-6); ck.R("Reff", "porn", "0", 20e3)
r = ck.tran(1.5, 2e-4)
ax.plot(r["t"]*1e3, r["p5"], color="#58a6ff", lw=1.3, ls="--", label="VBUS (fast)")
ax.axhline(3.15, color="#8b949e", ls=":", label="RST-high threshold (~3.1 V)")
ax.set_xlabel("time  [ms]"); ax.set_ylabel("V"); ax.set_xlim(0, 1500); ax.set_ylim(-.3, 6)
ax.set_title("P. power-on reset  -  C5 10 uF + R11 100 k hold every CD4043B RST high\n"
             "long enough that Q1..Q4 = 0 at power-on for any realistic ramp")
ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/plots/P_por.png", dpi=120); plt.close(fig)

# ---- MIC. routed path + crosstalk AC --------------------------------------
RO, RB, RRLY, CX, CW = 2200., 2200., 0.1, 10e-12, 50e-12
fs = np.logspace(1, 6.5, 400)
c = Circuit()
c.I("Imic", "hs", "0", ac=1e-6); c.R("Ro", "hs", "0", RO)
c.R("K", "hs", "nbn", RRLY); c.R("Rb", "nbn", "0", RB); c.C("Cw", "nbn", "0", CW)
_, thru = c.ac(fs)
c2 = Circuit()
c2.V("Vs", "hs", "0", ac=1.0); c2.C("Cx", "hs", "nbx", CX)
c2.R("Rb", "nbx", "0", RB); c2.R("Rnc", "nbx", "0", 2200.0)
_, xt = c2.ac(fs)
ref = np.abs(thru["nbn"][np.argmin(np.abs(fs-1000))])
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.semilogx(fs, db(thru["nbn"]/ref), color="#2ea043", lw=2, label="routed notebook (K closed)")
ax.semilogx(fs, db(xt["nbx"]), color="#f85149", lw=2, label="de-selected notebook (K open, ~10 pF stray into 2k2)")
ax.axvspan(300, 3400, color="#58a6ff", alpha=.12, label="voice band")
ax.set_xlabel("frequency  [Hz]"); ax.set_ylabel("dB"); ax.set_ylim(-90, 5)
ax.set_title("MIC. passive mic path  -  flat & lossless to the selected notebook,\n"
             "< -50 dB to the others (de-selected COM rests on NC = 2k2 -> GND)")
ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/plots/MIC_path.png", dpi=120); plt.close(fig)

# ---- scorecard ------------------------------------------------------------
S = json.load(open(f"{OUT}/validation_results.json"))
fig, ax = plt.subplots(figsize=(10, 0.36*len(S)+1.2)); ax.axis("off")
for i, x in enumerate(S):
    y = 1 - (i+0.5)/len(S)
    ax.text(0.01, y, "PASS" if x["pass"] else "FAIL", color="#2ea043" if x["pass"] else "#f85149",
            fontsize=9, family="monospace", weight="bold", transform=ax.transAxes)
    ax.text(0.08, y, x["check"][:70], fontsize=9, family="monospace", transform=ax.transAxes)
    ax.text(0.66, y, x["measure"][:46], fontsize=8, color="#444", family="monospace", transform=ax.transAxes)
npass = sum(x["pass"] for x in S)
ax.text(0.01, 1.02, f"MeetingHub-4 v3  -  {npass}/{len(S)} checks pass",
        fontsize=12, weight="bold", transform=ax.transAxes)
fig.savefig(f"{OUT}/plots/scorecard.png", dpi=120, bbox_inches="tight"); plt.close(fig)
print("wrote plots/P_por.png, plots/MIC_path.png, plots/scorecard.png")
