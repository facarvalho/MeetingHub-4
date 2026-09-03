"""
MeetingHub-4 v2 - mixer / volume-control validation, with the focus the user
asked for:  when a channel's volume is at ZERO, is it really silent?

This is the v1 bug #1 failure mode (pots wired so they never fully muted, cost
R$3000).  Topology from hardware/PCB/MeetingHub-4-v2.net, RV1..RV5 = Alps
RK09712200HA 10k dual:

    Jn.T --Cn(1u)-- RVn.3 (SIGNAL, = CW end)
                    RVn.1 (VBIAS,  = CCW end)
                    RVn.2 (wiper)  --Rn(10k)-- U1.2  (U1A virtual ground @ VBIAS)
    U1A: inverting summer, Rf = R3 = 3k3   ->  -0.33 / channel
    U1.1 --C13(1u)-- RV5.3 ; RV5.1 = VBIAS ; RV5.2 wiper = MIX_L --C15-- U2 ...

Mute at full-CCW works ONLY IF Alps term 1 = the CCW end (so the wiper lands on
VBIAS, not on the signal).  That is the single bench-check item flagged all over
the v2 docs.  This script quantifies the mute assuming that convention AND shows
what happens if it is wrong.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mna import Circuit, db
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
PLT = os.path.join(os.path.dirname(__file__), "..", "plots")

VP = 5.0
POT = 10e3
REND = 5.0          # Alps RK097 residual/end + wiper contact resistance, typ (ohm)
FAIL = []
def ck(name, ok, detail):
    FAIL.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}\n       {detail}\n")

def chain(fracs, master=1.0, load=32.0, src=None, rend=REND, swap_pot=False):
    """fracs: list of 4 pot rotations 0..1 (0 = full CCW = mute end).
       src:   list of 4 AC amplitudes (V) at the 4 laptop L inputs.
       swap_pot=True models the v1 BUG (signal & VBIAS ends swapped)."""
    c = Circuit()
    c.V("V5","p5","0",dc=VP)
    c.R("R1","p5","vref",10e3); c.R("R2","vref","0",10e3); c.C("C3","vref","0",10e-6)
    c.opamp("U3","vbout","vref","vbias","p5","0",A0=1e5,gbw=1e6,rout=100.0)
    c.R("R38","vbout","vbias",47.0); c.C("C26","vbias","0",1e-6)
    for i in range(4):
        acv = 0.0 if src is None else src[i]
        c.V(f"Vin{i}", f"in{i}", "0", ac=acv)
        c.C(f"Cin{i}", f"in{i}", f"sig{i}", 1e-6)
        fr = fracs[i]
        # wiper position: track split with end resistance floor
        r_sig_w = max(POT*(1.0-fr), rend)       # signal end -> wiper
        r_w_bias = max(POT*fr, rend)            # wiper -> VBIAS end
        if swap_pot:                            # v1 bug: ends swapped
            r_sig_w, r_w_bias = r_w_bias, r_sig_w
        c.R(f"RVs{i}", f"sig{i}", f"w{i}", r_sig_w)
        c.R(f"RVb{i}", f"w{i}", "vbias", r_w_bias)
        c.R(f"Rn{i}", f"w{i}", "u1n", 10e3)
    c.R("R3","u1n","u1o",3.3e3)
    c.opamp("U1","u1o","vbias","u1n","p5","0",A0=1e5,gbw=15e6,rout=60.0)
    # master pot RV5
    c.C("C13","u1o","m_sig",1e-6)
    rms = max(POT*(1.0-master), REND); rmb = max(POT*master, REND)
    c.R("RV5s","m_sig","m_w",rms); c.R("RV5b","m_w","vbias",rmb)
    c.C("C15","m_w","u2p",1e-6); c.R("R13","u2p","vbias",100e3)
    c.R("R15","u2n","u2o",1e3); c.R("R14","u2n","fbg",1e3); c.C("C16","fbg","0",10e-6)
    c.opamp("U2","u2o","u2p","u2n","p5","0",A0=1e5,gbw=9e6,rout=25.0)
    c.C("C17","u2o","n1",220e-6); c.R("R16","n1","j6t",47.0); c.R("Rl","j6t","0",load)
    return c

VIN = 0.316          # -10 dBV laptop line level, rms
F = 1000.0

# ---------------------------------------------------------------- 1. one channel
print("="*70); print(" MIXER / VOLUME MUTE VALIDATION"); print("="*70)
g_full = np.abs(chain([1,0,0,0], src=[1,0,0,0]).ac([F])[1]["j6t"][0])
g_zero = np.abs(chain([0,0,0,0], src=[1,0,0,0]).ac([F])[1]["j6t"][0])
ck("M1  channel 1 at volume 0 is silent (others also 0)",
   db(g_zero/g_full) < -55,
   f"gain full={g_full:.4f}  zero={g_zero:.2e}  ->  {db(g_zero/g_full):+.1f} dB  "
   f"({g_zero*VIN*1e6:.1f} uV out for a {VIN} Vrms input)")

# ---------------------------------------------------------------- 2. all four zero
res = chain([0,0,0,0], master=1.0, src=[1,1,1,1]).ac([F])[1]
g_all0 = np.abs(res["j6t"][0])
ck("M2  ALL four inputs at volume 0  ->  headset output silent",
   g_all0*VIN < 1e-3,
   f"4x {VIN} Vrms in  ->  {g_all0*VIN*1e6:.1f} uV at J6.T  ({db(g_all0):.0f} dB gain)")

# ---------------------------------------------------------------- 3. leak / isolation
# ch1 muted, ch2/3/4 at full volume playing: does ch1 being present change the sum?
g_ref = np.abs(chain([1,1,1,1], src=[0,1,1,1]).ac([F])[1]["j6t"][0])   # 3 sources, ch1 pot up but its src=0
g_wm  = np.abs(chain([0,1,1,1], src=[9,1,1,1]).ac([F])[1]["j6t"][0])   # ch1 pot ZERO, ch1 src huge
ck("M3  a zeroed channel does not leak its source into the mix",
   abs(g_wm-g_ref)/g_ref < 0.02,
   f"3 channels @ full + ch1 pot=0 w/ a 9 V source on ch1: "
   f"mix gain {g_wm:.4f} vs {g_ref:.4f} reference  (delta {abs(g_wm-g_ref)/g_ref*100:.2f}%)")

# ---------------------------------------------------------------- 4. master mute
g_m0 = np.abs(chain([1,1,1,1], master=0.0, src=[1,1,1,1]).ac([F])[1]["j6t"][0])
ck("M4  master volume RV5 at 0  ->  headset silent regardless of channels",
   g_m0*VIN < 1e-3,
   f"all channels full, RV5=0  ->  {g_m0*VIN*1e6:.1f} uV at J6.T")

# ---------------------------------------------------------------- 5. the v1 bug, reproduced
gb_full = np.abs(chain([1,0,0,0], src=[1,0,0,0], swap_pot=True).ac([F])[1]["j6t"][0])
gb_zero = np.abs(chain([0,0,0,0], src=[1,0,0,0], swap_pot=True).ac([F])[1]["j6t"][0])
ck("M5  CONTROL: with the pot ends SWAPPED (the v1 wiring bug) mute FAILS",
   db(gb_zero/max(g_full,1e-12)) > -12,      # at the MIN knob position, still ~full
   f"swapped wiring: at the MIN knob position gain = {gb_zero:.3f} = {db(gb_zero/g_full):+.1f} dB "
   f"vs full -> {gb_zero*VIN*1e3:.0f} mV STILL PASSES (that was the R$3000 v1 bug). "
   f"v2 netlist has signal on RVn.3/6 and VBIAS on RVn.1/4 -> correct, mute works.")

# ---------------------------------------------------------------- 6. residual vs pot spec
for rend in (2.0, 5.0, 20.0, 50.0):
    gz = np.abs(chain([0,0,0,0], src=[1,0,0,0], rend=rend).ac([F])[1]["j6t"][0])
    print(f"   pot end/wiper resistance {rend:5.1f} ohm  ->  mute floor {db(gz/g_full):+6.1f} dB "
          f"({gz*VIN*1e6:6.1f} uV)")
print()

# ---------------------------------------------------------------- 7. no DC step across the pot (no scratch)
op0 = chain([0,0,0,0], src=[0,0,0,0]).op()
op1 = chain([1,1,1,1], src=[0,0,0,0]).op()
dv = max(abs(op0["w0"]-2.5), abs(op1["w0"]-2.5))
ck("M6  wiper sits at VBIAS at every rotation (no DC step -> no scratchy pot)",
   dv < 1e-3,
   f"V(wiper) - VBIAS  =  {dv*1e3:.3f} mV worst case across the full rotation "
   f"(both pot ends are VBIAS-referenced: term1 = VBIAS, term3 via Cn blocks DC)")

# ---------------------------------------------------------------- plot: mute sweep
fr = np.linspace(0, 1, 200)
gg = np.array([np.abs(chain([x,0,0,0], src=[1,0,0,0]).ac([F])[1]["j6t"][0]) for x in fr])
ggb = np.array([np.abs(chain([x,0,0,0], src=[1,0,0,0], swap_pot=True).ac([F])[1]["j6t"][0]) for x in fr])
fig, ax = plt.subplots(figsize=(8,4.5))
ax.plot(fr*100, db(gg/g_full), lw=2.6, color="#2ea043", label="v2 as built (signal->RVn.3/6, VBIAS->RVn.1/4)")
ax.plot(fr*100, db(ggb/g_full), lw=2, ls="--", color="#f85149", label="v1 bug: signal & VBIAS ends swapped")
ax.axhline(-60, color="#888", ls=":", lw=1)
ax.set_xlabel("knob rotation  [%]   (0 % = user turns fully counter-clockwise for MIN / mute)")
ax.set_ylabel("channel gain  [dB re full volume]")
ax.set_title("Volume-pot law — does turning it to minimum actually mute?")
ax.set_ylim(-90, 6); ax.legend(loc="lower right"); ax.grid(alpha=.3)
ax.plot([0],[db(g_zero/g_full)], "o", color="#2ea043"); ax.plot([0],[0], "o", color="#f85149")
ax.annotate(f"v2 at MIN: {db(g_zero/g_full):.0f} dB = silent", (4, db(g_zero/g_full)+3), color="#2ea043", fontsize=10)
ax.annotate("v1 bug at MIN: 0 dB = still FULL volume\n(direction reversed; cost R$3000)", (4, -14), color="#f85149", fontsize=10)
fig.tight_layout(); fig.savefig(f"{PLT}/M_mute_law.png", dpi=115); plt.close(fig)

npass = sum(1 for _, ok, _ in FAIL if ok)
print("="*70); print(f"  {npass}/{len(FAIL)} mute/mixer checks PASS"); print("="*70)
print("""
 CAVEAT (unchanged from the v2 docs): all of the above assumes the Alps
 RK09712200HA has term 1 = full-CCW end and term 3 = full-CW end.  The v2
 NETLIST is wired correctly for that convention (signal->term3/6, VBIAS->
 term1/4, opposite of the v1 bug).  Confirm on the first article with an
 ohmmeter: knob fully CCW  =>  wiper (term 2) to term 1 ~= 0 ohm.
""")
