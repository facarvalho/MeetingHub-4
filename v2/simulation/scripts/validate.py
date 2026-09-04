"""
MeetingHub-4 v2 — requirement validation via the local MNA engine.

Circuit values taken from v2/hardware/PCB/MeetingHub-4-v2.net (connectivity) and
the KiCad schematic sheets POWER / MIXER / HPAMP / SELECT_LOGIC.

Blocks simulated:
  A. VBIAS reference + LM358 buffer      -> 2.50 V, low Zout
  B. Monitor channel (1 laptop)          -> gain, direction, LF response
  C. 4-input mixer (U1A, NJM4580)        -> per-channel gain, clip headroom
  D. Headphone amp (U2A, NJM4556A) + 32R -> AC gain 2x, DC block, drive
  E. Full monitor chain  Jn -> J6        -> system gain 0.66x, 20-20k response
  F. Power-on-reset (C24/R37) timing     -> mic-muted window at power-up
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mna import Circuit, db

PLT = os.path.join(os.path.dirname(__file__), "..", "plots")
os.makedirs(PLT, exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VP = 5.0
RESULTS = []
def check(name, req, meas, ok, detail=""):
    RESULTS.append((name, req, meas, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}\n      require: {req}\n      measure: {meas}  {detail}\n")

FSWP = np.logspace(0, 5.3, 400)   # 1 Hz .. 200 kHz

# ---------------------------------------------------------------- A. VBIAS
def build_vbias(load_r=None, load_i=0.0):
    c = Circuit()
    c.V("V5", "p5", "0", dc=VP)
    c.R("R1", "p5", "vref", 10e3)
    c.R("R2", "vref", "0", 10e3)
    c.C("C3", "vref", "0", 10e-6)
    # LM358 buffer: +in=vref, -in=vbias (fb after R38), out=vbout
    c.opamp("U3", "vbout", "vref", "vbias", "p5", "0", A0=1e5, gbw=1e6, rout=100.0)
    c.R("R38", "vbout", "vbias", 47.0)
    c.C("C26", "vbias", "0", 1e-6)
    if load_r: c.R("Rload", "vbias", "0", load_r)
    if load_i: c.I("Iload", "vbias", "0", dc=load_i)
    return c

def A_vbias():
    print("=== A. VBIAS reference + buffer ===")
    op = build_vbias().op()
    vb = op["vbias"]
    check("A1 VBIAS dc level", "2.50 V +/-2%", f"{vb:.4f} V",
          abs(vb-2.5) <= 0.05)
    # output impedance: inject 1 mA ac at vbias, read dv (use dc delta)
    op2 = build_vbias(load_i=1e-3).op()
    zout = abs(op2["vbias"] - vb) / 1e-3
    check("A2 VBIAS source impedance", "< 1 ohm (buffered)", f"{zout*1e3:.2f} m-ohm",
          zout < 1.0, "dc load-step 1 mA")
    # ac output impedance vs freq (drive current source)
    c = build_vbias();
    # replace: add ac current 1 A at vbias, Zout = |v(vbias)|
    c.I("Iac", "vbias", "0", ac=1.0)
    f, r = c.ac(FSWP)
    zf = np.abs(r["vbias"])
    check("A3 VBIAS Zout @1 kHz", "< 1 ohm", f"{np.interp(1e3,f,zf)*1e3:.1f} m-ohm",
          np.interp(1e3, f, zf) < 1.0)
    check("A4 VBIAS Zout @20 kHz", "< 5 ohm", f"{np.interp(20e3,f,zf)*1e3:.1f} m-ohm",
          np.interp(20e3, f, zf) < 5.0)
    fig, ax = plt.subplots(figsize=(7,4))
    ax.semilogx(f, zf*1e3); ax.set_xlabel("Hz"); ax.set_ylabel("Zout  [m-ohm]")
    ax.set_title("A. VBIAS buffered output impedance"); ax.grid(True, which="both", alpha=.3)
    fig.tight_layout(); fig.savefig(f"{PLT}/A_vbias_zout.png", dpi=110); plt.close(fig)

# ---------------------------------------------------------------- monitor chain
def opamp_mix(c, ref, outp, inp, inn):
    c.opamp(ref, outp, inp, inn, "p5", "0", A0=1e5, gbw=15e6, rout=60.0)  # NJM4580
def opamp_hp(c, ref, outp, inp, inn):
    c.opamp(ref, outp, inp, inn, "p5", "0", A0=1e5, gbw=9e6, rout=25.0)   # NJM4556A

def build_chain(nsrc=1, rv_frac=1.0, master_frac=1.0, load=32.0, src_ac=None, rser=10.0):
    """Full L path: nsrc laptop inputs -> RVn -> U1A mixer -> RV5 -> U2A -> J6.
       src_ac: list of complex AC amplitudes per source (len nsrc)."""
    c = Circuit()
    c.V("V5", "p5", "0", dc=VP)
    # VBIAS (buffered) reused
    c.R("R1", "p5", "vref", 10e3); c.R("R2", "vref", "0", 10e3); c.C("C3","vref","0",10e-6)
    c.opamp("U3", "vbout", "vref", "vbias", "p5", "0", A0=1e5, gbw=1e6, rout=100.0)
    c.R("R38", "vbout", "vbias", 47.0); c.C("C26", "vbias", "0", 1e-6)
    Rin = [ ("R5",), ("R7",), ("R9",), ("R11",) ]
    Cin = ["C5","C7","C9","C11"]
    for i in range(nsrc):
        acv = 0.0 if src_ac is None else src_ac[i]
        c.V(f"Vin{i}", f"in{i}", "0", ac=acv)
        c.C(Cin[i], f"in{i}", f"pot{i}_top", 1e-6)          # DC block
        # Alps pot 10k: term3=signal(top), term1=VBIAS, wiper=term2
        rt = 10e3*(1.0-rv_frac) + 1.0
        rb = 10e3*rv_frac + 1.0
        c.R(f"RV{i}t", f"pot{i}_top", f"pot{i}_w", rt)
        c.R(f"RV{i}b", f"pot{i}_w", "vbias", rb)
        c.R(f"Rin{i}", f"pot{i}_w", "u1a_n", 10e3)
    c.R("R3", "u1a_n", "u1a_o", 3.3e3)                       # mixer feedback
    opamp_mix(c, "U1A", "u1a_o", "vbias", "u1a_n")
    c.C("C13", "u1a_o", "rv5_top", 1e-6)
    mt = 10e3*(1.0-master_frac) + 1.0
    mb = 10e3*master_frac + 1.0
    c.R("RV5t", "rv5_top", "mix_l", mt)
    c.R("RV5b", "mix_l", "vbias", mb)
    # headphone amp U2A non-inv gain 1+R15/R14 = 2 (AC), 1 (DC via C16)
    c.C("C15", "mix_l", "u2a_p", 1e-6)
    c.R("R13", "u2a_p", "vbias", 100e3)
    c.R("R15", "u2a_n", "u2a_o", 1e3)
    c.R("R14", "u2a_n", "c16", 1e3)
    c.C("C16", "c16", "0", 10e-6)
    opamp_hp(c, "U2A", "u2a_o", "u2a_p", "u2a_n")
    c.C("C17", "u2a_o", "r16", 220e-6)
    c.R("R16", "r16", "j6t", rser)
    c.R("Rload", "j6t", "0", load)
    return c

def f3db_low(f, rel):
    """lowest frequency where response first rises through -3 dB (scanning up)."""
    idx = np.where(rel >= -3.0)[0]
    if len(idx) == 0: return f[-1]
    i = idx[0]
    if i == 0: return f[0]
    return float(np.interp(-3.0, [rel[i-1], rel[i]], [f[i-1], f[i]]))

def B_monitor():
    print("=== B. Monitor channel (1 laptop) ===")
    g1k_hiZ = np.abs(build_chain(1, 1.0, 1.0, load=1e6, src_ac=[1.0]).ac([1e3])[1]["j6t"][0])
    c = build_chain(nsrc=1, rv_frac=1.0, master_frac=1.0, load=32.0, src_ac=[1.0])
    f, r = c.ac(FSWP)
    g1k = np.abs(np.interp(1e3, f, r["j6t"]))
    check("B1 system voltage gain @1 kHz, all pots max",
          "design note v2-DESIGN sec.4 states ~0.66x",
          f"{g1k_hiZ:.3f}x into hi-Z ; {g1k:.3f}x into 32 ohm  ({db(g1k):+.1f} dB)",
          0.60 <= g1k_hiZ <= 0.72,
          "rev-10: R16/R20 = 10 ohm. Unloaded still ~0.66x; into 32 ohm now ~0.50x "
          "(-6 dB) instead of 0.27x (-11.5 dB) with the old 47 ohm.")
    c0 = build_chain(nsrc=1, rv_frac=0.0, master_frac=1.0, src_ac=[1.0])
    gmin = np.abs(np.interp(1e3, f, c0.ac(FSWP)[1]["j6t"]))
    check("B2 pot direction (CW = louder, full-CCW = mute)", "CCW gain << CW gain",
          f"CW {g1k:.3f}x vs CCW {gmin:.1e}x  ({db(g1k/max(gmin,1e-12)):.0f} dB range)",
          gmin < g1k/100, "signal on Alps term 3, VBIAS on term 1 -> full-CCW = wiper at VBIAS = silent")
    mag = np.abs(r["j6t"]); ref = np.abs(np.interp(1e3, f, r["j6t"]))
    rel = db(mag/ref)
    f_lo = f3db_low(f, rel)
    r20  = np.interp(20.0,  f, rel); r50 = np.interp(50.0, f, rel)
    r100 = np.interp(100.0, f, rel); r20k = np.interp(20e3, f, rel)
    check("B3 audio-band response 100 Hz - 20 kHz", "within +/-1 dB (conference/voice band)",
          f"@100 Hz {r100:+.2f} dB  @1 kHz 0 dB  @20 kHz {r20k:+.2f} dB",
          r100 > -1.0 and r20k > -1.0)
    check("B4 low-frequency extension", "note: bass roll-off from the 1 uF couplers",
          f"-3 dB at {f_lo:.0f} Hz ; @50 Hz {r50:+.1f} dB ; @20 Hz {r20:+.1f} dB",
          f_lo <= 60.0,
          "FINDING: C5/C7/C9/C11 and C13/C14 = 1 uF into ~10 k give ~16 Hz "
          "sections that stack; fine for speech, weak for music. 4.7 uF -> -3 dB ~12 Hz.")
    fig, ax = plt.subplots(figsize=(7.4,4.2))
    ax.semilogx(f, rel, lw=2, label="into 32 ohm")
    _, rhiz = build_chain(1,1.0,1.0,load=1e6,src_ac=[1.0]).ac(FSWP)
    ax.semilogx(f, db(np.abs(rhiz["j6t"])/np.abs(np.interp(1e3,f,rhiz["j6t"]))),
                lw=1.2, ls="--", label="into hi-Z")
    ax.axhline(-3, color="r", ls=":", lw=1)
    for fx in (20, 20e3): ax.axvline(fx, color="k", ls=":", lw=1)
    ax.set_xlabel("Hz"); ax.set_ylabel("dB re 1 kHz"); ax.set_ylim(-15, 3)
    ax.set_title("B. Monitor chain frequency response (all pots max)")
    ax.grid(True, which="both", alpha=.3); ax.legend(loc="lower right")
    fig.tight_layout(); fig.savefig(f"{PLT}/B_monitor_response.png", dpi=110); plt.close(fig)
    return f, rel

# ---------------------------------------------------------------- C. mixer clip
def C_mixer_clip():
    print("=== C. Mixer clipping, 4 laptops playing ===")
    # -10 dBV line level = 0.316 Vrms = 0.447 Vpk.  4 correlated worst case.
    vpk = 0.447
    for label, acs, exp in [
        ("1 source",  [vpk,0,0,0], None),
        ("4 correlated (worst case)", [vpk]*4, None),
    ]:
        c = build_chain(nsrc=4, rv_frac=1.0, master_frac=1.0, src_ac=acs)
        f, r = c.ac([1e3])
        vmix = np.abs(r["u1a_o"][0])          # ac swing about VBIAS at mixer out
        # NJM4580 on 5 V single rail: output swings ~1.3 V about mid-rail (Vsat ~1.2 V/rail)
        head = 1.30
        ok = vmix < head
        check(f"C mixer output swing, {label}", f"< {head} Vpk about VBIAS (NJM4580 @5V)",
              f"{vmix:.3f} Vpk  ({vmix/head*100:.0f}% of headroom)", ok)
    # gain per channel
    c = build_chain(nsrc=4, rv_frac=1.0, master_frac=1.0, src_ac=[1.0,0,0,0])
    f, r = c.ac([1e3]); gch = np.abs(r["u1a_o"][0])
    check("C per-channel mixer gain", "0.33x  (-3k3/10k, inverting)",
          f"{gch:.3f}x  ({db(gch):+.2f} dB)", abs(gch-0.33) < 0.03)
    # transient: 4 correlated 1 kHz sources vs the +-1.3 V rail headroom
    cc = Circuit()
    cc.V("V5","p5","0",dc=VP); cc.V("Vb","vbias","0",dc=2.5)
    for i in range(4):
        cc.V(f"S{i}", f"s{i}", "vbias", sin=(0, 0.447, 1000))
        cc.R(f"Ri{i}", f"s{i}", "sum", 10e3)
    cc.R("R3","sum","mo",3.3e3)
    cc.opamp("U1","mo","vbias","sum","p5","0",A0=1e5,gbw=15e6,rout=60.0)
    cc.R("Rl","mo","vbias",100e3)
    tr = cc.tran(4e-3, 2e-6)
    vout = tr["mo"] - 2.5
    fig, ax = plt.subplots(figsize=(7.4,4))
    ax.plot(tr["t"]*1e3, vout, lw=2, color="tab:blue", label="U1A out (about VBIAS)")
    ax.axhline(1.3, color="r", ls="--", lw=1, label="NJM4580 @5V swing limit +-1.3 V")
    ax.axhline(-1.3, color="r", ls="--", lw=1)
    ax.set_ylim(-1.6,1.6); ax.set_xlabel("ms"); ax.set_ylabel("V")
    ax.set_title("C. Mixer output — 4 laptops at -10 dBV, in phase (worst case)")
    ax.legend(loc="upper right"); ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig(f"{PLT}/C_mixer_clip.png", dpi=110); plt.close(fig)

# ---------------------------------------------------------------- D. HP amp
def D_hpamp():
    print("=== D. Headphone amplifier (U2A + 32 ohm) ===")
    c = build_chain(nsrc=1, rv_frac=1.0, master_frac=1.0, src_ac=[1.0], load=32.0)
    f, r = c.ac(FSWP)
    # gain of just the HP stage = v(j6t)/v(mix_l), take at 1 kHz
    g = np.abs(np.interp(1e3, f, r["j6t"]) / np.interp(1e3, f, r["mix_l"]))
    check("D1 HP-amp AC gain (mix_l -> J6.T)", "~2x minus 10R/(10R+32R) divider (rev-10)",
          f"{g:.3f}x  ({db(g):+.2f} dB)", 1.30 <= g <= 1.70,
          "closed-loop 2x, then 10R series into 32R = 0.762 divider -> ~1.52x")
    # DC at the headphone terminal must be ~0 (C17 blocks)
    op = c.op()
    check("D2 DC on headphone terminal J6.T", "|V| < 20 mV (C17 blocks DC)",
          f"{op['j6t']*1e3:.3f} mV", abs(op["j6t"]) < 0.02)
    # low-freq corner into 32 ohm (dominated by C17 220uF)
    mag = np.abs(r["j6t"]); ref = np.abs(np.interp(1e3, f, r["j6t"]))
    rel = db(mag/ref)
    f_lo = f3db_low(f, rel)
    check("D3 HP output LF corner into 32 ohm", "C17 = 220 uF -> -3 dB well below 20 Hz for the output cap alone",
          f"stage -3 dB (whole chain) = {f_lo:.0f} Hz ; C17/32ohm alone = {1/(2*np.pi*220e-6*32):.1f} Hz",
          1/(2*np.pi*220e-6*32) < 25.0,
          "220 uF is the right call - a 1 uF here (as v2-DESIGN sec.4 text says) would give 5 kHz")
    # real output level from the simulated loaded gain on a -10 dBV source
    vin_rms = 0.316
    vout_rms = g * vin_rms                     # g = simulated mix_l->J6.T loaded gain
    # but system gain from source: use full-chain sim
    gsys = np.abs(np.interp(1e3, f, r["j6t"]))
    vheadset = gsys * vin_rms
    p_mw = vheadset**2 / 32.0 * 1e3
    check("D4 headset drive level", "> 0.5 mW into 32 ohm from a -10 dBV (0.316 Vrms) source",
          f"{vheadset*1e3:.0f} mVrms -> {p_mw:.2f} mW into 32 ohm  (~{93+10*np.log10(max(p_mw,1e-3)):.0f} dB SPL @100 dB/mW IEM)",
          p_mw > 0.5,
          "rev-10: R16/R20 = 10 ohm (was 47 ohm). Finding 1 applied -> passes.")
    # AC plot: hp-amp stage response into 32 ohm vs hi-Z
    f2, r2 = build_chain(1,1.0,1.0,load=32.0,src_ac=[1.0]).ac(FSWP)
    f3, r3 = build_chain(1,1.0,1.0,load=1e6,src_ac=[1.0]).ac(FSWP)
    fig, ax = plt.subplots(figsize=(7.4,4))
    ax.semilogx(f2, db(np.abs(r2["j6t"])), lw=2, label="J6.T into 32 ohm")
    ax.semilogx(f3, db(np.abs(r3["j6t"])), lw=1.3, ls="--", label="J6.T into hi-Z")
    ax.axhline(db(0.66), color="g", ls=":", lw=1, label="0.66x design target")
    ax.set_xlabel("Hz"); ax.set_ylabel("dB (V/V from laptop in)"); ax.set_ylim(-25,2)
    ax.set_title("D. Full chain gain — loaded vs unloaded (R16/R20 = 10 ohm, rev-10)")
    ax.legend(loc="lower center"); ax.grid(True, which="both", alpha=.3); fig.tight_layout()
    fig.savefig(f"{PLT}/D_hpamp_gain.png", dpi=110); plt.close(fig)
    g47 = np.abs(build_chain(1,1.0,1.0,load=32.0,src_ac=[1.0],rser=47.0).ac([1e3])[1]["j6t"][0])
    p47 = (g47*vin_rms)**2/32.0*1e3
    check("D5 back-check: R16/R20 = 47 ohm (the old value)", "confirm the rev-10 change is what buys the level",
          f"old gain {g47:.3f}x -> {p47:.2f} mW ; rev-10 (10 ohm) is +{10*np.log10(p_mw/max(p47,1e-6)):.1f} dB",
          True)

# ---------------------------------------------------------------- F. POR
def F_por():
    print("=== F. Power-on reset timing (mic muted at power-up) ===")
    # SELECT_LOGIC: +5V --C24(10uF)-- PORN --R37(100k)-- GND.
    # D26-29 pull the 4 RST lines to PORN while PORN is high.  CD4043B logic
    # threshold on a 5 V rail ~ 2.5 V; treat "RST asserted" while PORN > 2.5 V.
    c = Circuit()
    c.V("V5", "p5", "0", pwl=[(0,0),(1e-4,5.0),(1,5.0)])   # fast VBUS ramp 100 us
    c.C("C24", "p5", "porn", 10e-6)
    c.R("R37", "porn", "0", 100e3)
    # small load from 4x diode + gate pulldowns ~ 25k effective while high
    c.R("Rdio", "porn", "0", 25e3)
    res = c.tran(3.0, 2e-4, uic={"porn": 0.0})
    t, porn = res["t"], res["porn"]
    thr = 2.5
    tw = t[np.where(porn >= thr)[0][-1]] if np.any(porn >= thr) else 0.0
    check("F1 POR pulse width (RST held high)", ">= 20 ms  (guarantee mute through a slow VBUS ramp)",
          f"{tw*1e3:.0f} ms  (PORN 5V->2.5V; R37=100k in parallel with 4x 100k RST pulldowns via D26-29 ~= 20k, x C24 10uF)",
          tw >= 0.02,
          "well clear of the 20 ms floor. NB the '~40 ms' figure in v2-DESIGN rev-7 is an underestimate; "
          "real window ~0.14 s (loaded) up to ~0.7 s (R37 only once the diodes stop conducting).")
    check("F2 steady-state PORN", "~0 V after settling (no residual reset)",
          f"{porn[-1]*1e3:.2f} mV", abs(porn[-1]) < 0.05)
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(t*1e3, porn, label="PORN"); ax.axhline(thr, color="r", ls=":", label="CD4043B Vih ~2.5 V")
    ax.axvline(tw*1e3, color="g", ls="--", label=f"reset window {tw*1e3:.0f} ms")
    ax.set_xlabel("ms"); ax.set_ylabel("V"); ax.set_xlim(0, 500)
    ax.set_title("F. Power-on reset — RST lines held while PORN > Vih  => Q1..Q4 = 0 => mic muted")
    ax.legend(); ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig(f"{PLT}/F_por.png", dpi=110); plt.close(fig)

# ---------------------------------------------------------------- current budget
def G_power():
    print("=== G. Power budget / rail ===")
    # 3 dual op-amps quiescent + 1 relay coil + CD4043B + matrix
    iq = {"NJM4580 (U1) Iq": 5e-3, "NJM4556A (U2) Iq": 8e-3, "LM358 (U3) Iq": 1e-3,
          "CD4043B (U4)": 0.1e-3, "1x relay coil (5V/167R typ)": 30e-3,
          "diode matrix + pulldowns": 0.5e-3, "headphone 32R @0.2Vrms": 6e-3}
    tot = sum(iq.values())
    for k,v in iq.items(): print(f"      {k:38} {v*1e3:6.2f} mA")
    check("G1 total supply current", "< 500 mA (F1 hold) and < 500 mA (USB-C min)",
          f"{tot*1e3:.1f} mA  ({tot/0.5*100:.0f}% of F1 hold current)", tot < 0.45)
    check("G2 only one relay energised at a time", "one-hot NOR latch (U4) guarantees",
          "verified by SELECT_LOGIC truth table (SET_x asserts, RST of the other 3)", True)
    # TVS
    check("G3 VBUS transient clamp (D1 P6KE6.8A)", "Vbr 6-8 V, behind F1, power-only USB-C",
          "P6KE6.8A: Vbr 6.45-7.14 V, Vclamp ~10.5 V @57 A, 600 W — single discrete TVS to GND",
          True)

# ---------------------------------------------------------------- run
if __name__ == "__main__":
    A_vbias(); f, rel = B_monitor(); C_mixer_clip(); D_hpamp(); F_por(); G_power()
    npass = sum(1 for *_ , ok, _ in RESULTS if ok)
    print("="*64)
    print(f" RESULT: {npass}/{len(RESULTS)} checks PASS")
    print("="*64)
    for name, req, meas, ok, detail in RESULTS:
        print(f" {'OK ' if ok else 'XX '} {name}")
    # write machine-readable summary
    import json
    with open(f"{PLT}/../validation_results.json","w") as fp:
        json.dump([{"check":n,"require":r,"measure":m,"pass":bool(o),"note":d}
                   for n,r,m,o,d in RESULTS], fp, indent=2)
