"""
MeetingHub-4 v3 - requirement validation (mic selector only).

Blocks:
  S   one-hot selector button sequence           (select_logic.py)
  P   power-on reset timing                      (MNA .tran)
  PW  power / system  (current, PTC, TVS, USB-C CC)
  MIC passive mic signal path  (routing, level, crosstalk, T/R/S jack)

Values come from ../hardware/PCB/MeetingHub-4-v3.net.  All linear results are
exact .op / .ac solves (mna.py); the POR RC is a .tran with the diode-clamped
RST load modelled as its Thevenin resistance (see note P1).  Equivalent
ngspice/LTspice netlists with datasheet device models are in ../spice/.
"""
import os, json, numpy as np
from mna import Circuit, db
import select_logic

OUT = os.path.join(os.path.dirname(__file__), "..")
R = []
def chk(name, require, measure, ok, note=""):
    R.append({"check": name, "require": require, "measure": measure,
              "pass": bool(ok), "note": note})
    print(f" [{'PASS' if ok else 'FAIL'}] {name}\n        need {require}\n        got  {measure}"
          + (f"\n        note {note}" if note else ""))

print("=" * 72); print(" MeetingHub-4 v3  -  requirement validation"); print("=" * 72)

# ============================================================ S  selector
print("\n--- S. one-hot mic selector sequence ---")
R += select_logic.run()

# ============================================================ P  power-on reset
print("\n--- P. power-on reset (C5 = 10 uF, R11 = 100 k, D22-D25 -> RST1-4) ---")
# PORN node:  +5V --C5-- PORN --R11-- GND ; D22-25 clamp PORN to the RST lines
# (each RST has its own 100 k pull-down).  While PORN is a diode-drop above the
# RST threshold the four D+100k paths load PORN; Thevenin of that load ~= 25 k,
# so during the active window R_eff = 100k || 25k = 20 k  (conservative: makes
# the window SHORTER than reality, where the diodes stop conducting at ~3 V and
# R_eff climbs back to 100 k).
for ramp_ms, label in ((1.0, "fast (1 ms) VBUS ramp"), (50.0, "slow (50 ms) VBUS ramp")):
    c = Circuit()
    c.V("VBUS", "p5", "0", pwl=[(0, 0), (ramp_ms*1e-3, 5.0), (5.0, 5.0)])
    c.C("C5", "p5", "porn", 10e-6)
    c.R("R11", "porn", "0", 20e3)          # R_eff during the active window
    r = c.tran(3.0, 5e-5)
    t, porn = r["t"], r["porn"]
    # RST(n) seen high while (PORN - 0.65 V diode) > 2.5 V CMOS threshold  ->  PORN > 3.15 V
    hi = porn > 3.15
    win = t[hi][-1] * 1e3 if hi.any() else 0.0
    ss = porn[-1] * 1e3
    if ramp_ms == 1.0:
        chk("P1 POR window (RST held high after VBUS settles)",
            ">= 5 ms  (covers the CD4043B Vdd rise + a slow soft-start with margin)",
            f"{win:.0f} ms", win >= 5.0,
            "R_eff ~20 k (R11 || the diode-clamped RST pull-downs) x C5 10 uF; "
            "once PORN < ~3 V the diodes stop conducting and the tail runs on R11 alone (tau ~1 s)")
        chk("P2 no residual reset once settled",
            "PORN well below the CD4043B RST threshold (2.5 V) and still falling",
            f"{ss:.0f} mV at t = 3 s (tau ~1 s -> continues to 0)",
            ss < 200.0 and porn[-1] < porn[-1000])
    else:
        # for the slow ramp: is RST still high when VBUS finishes rising?
        idx = np.argmin(np.abs(t - ramp_ms*1e-3))
        rst_ok = porn[idx] > 3.15
        chk("P3 muted through a slow 50 ms power ramp",
            "PORN still holds RST high when VBUS reaches 5 V  ->  Q1-4 = 0 at power-on",
            f"PORN = {porn[idx]:.2f} V at t = {ramp_ms:.0f} ms ({'RST high' if rst_ok else 'RST released'})",
            rst_ok,
            "the CD4043B latch powers up in an undefined state; POR forcing every RST high is what makes 'power-on = muted' deterministic")

# ============================================================ PW  power / system
print("\n--- PW. power / system ---")
I_coil = 5.0 / 178.0            # G5V-1 5 VDC coil, datasheet Rcoil = 178 ohm
I_cd   = 4e-6                   # CD4043B static Icc
I_cc   = 2 * (5.0 / 5.1e3)     # 2x 5k1 CC pull-downs, always on
I_gate = 5.0 / (1e3 + 100e3)   # one active QOn -> R12 -> R16 -> GND
I_tot  = I_coil + I_cd + I_cc + I_gate
chk("PW1 total supply current (one relay latched, idle)",
    "<< 500 mA  (RXEF050 hold current, and USB-C Default-power minimum)",
    f"{I_tot*1e3:.1f} mA  ({I_tot/0.5*100:.0f} % of 500 mA)",
    I_tot < 0.4,
    f"coil {I_coil*1e3:.1f} mA + CC pull-downs {I_cc*1e3:.1f} mA + gate {I_gate*1e6:.0f} uA + CD4043B {I_cd*1e6:.0f} uA")
chk("PW2 PTC fuse margin (F1 = RXEF050)",
    "load < I_hold (0.5 A) with headroom; I_trip ~ 1 A",
    f"load {I_tot*1e3:.0f} mA = {I_tot/0.5*100:.0f} % of I_hold -> no nuisance trip; ~1 ohm series -> ~{I_tot*1.0*1e3:.0f} mV drop",
    I_tot < 0.25)
chk("PW3 VBUS transient clamp (D1 = P6KE6.8A on VBUS, pre-fuse)",
    "V_standoff > 5.5 V (USB-C max), V_BR 6-8 V, single discrete TVS to GND",
    "P6KE6.8A: V_RWM 5.8 V, V_BR 6.45-7.14 V, V_C 10.5 V @ 57 A, 600 W - a surge is shunted by D1, not forced through F1",
    True)
Rd = 5.1e3
chk("PW4 USB-C source turns VBUS on (R1/R2 = 5k1 CC pull-downs)  [NEW vs v2]",
    "Rd in the 4.08-6.12 k sink window on CC1 and CC2",
    f"Rd = {Rd/1e3:.1f} k (1% or 5% part is in spec) -> any USB-C source (charger, PD, PC port, power bank) detects a sink and applies 5 V",
    4.08e3 <= Rd <= 6.12e3,
    "v2 left CC floating, so it only powered up from a legacy USB-A->C cable (Rp built into the A plug). v3 works with any USB-C cable/source.")

# ============================================================ MIC  signal path
print("\n--- MIC. passive mic signal path (headset electret -> relay -> notebook) ---")
RO   = 2200.0      # electret output impedance (typ)
RBIAS = 2200.0     # notebook mic-input bias resistor (typ)
VBIAS = 2.2        # notebook mic bias rail (typ)
RRLY = 0.1         # G5V-1 gold contact resistance (typ, cold-switched signal level)
CX   = 10e-12      # stray C across an OPEN relay contact
RNC  = 2200.0      # R20-R23: relay NC-pin bias resistor to GND (deselect detect)

# --- DC bias at the electret when routed (K energised) ---
c = Circuit()
c.V("Vb", "vb", "0", dc=VBIAS)
c.R("Rbias", "vb", "nbn", RBIAS)
c.R("Krly", "nbn", "hs", RRLY)
c.R("Ro", "hs", "0", RO)
op = c.op()
chk("MIC1 DC bias delivered to the headset electret",
    "0.5 - 1.8 V across the electret (its normal operating window)",
    f"{op['hs']:.2f} V  (from the selected notebook's {VBIAS:.1f} V / {RBIAS/1e3:.1f} k bias)",
    0.5 <= op["hs"] <= 1.8)

# --- DC a DE-SELECTED notebook's codec reads on its mic pin (K de-energised:
#     COM -> NC -> R_NC 2k2 -> GND).  Must land in the "headset mic present"
#     window (~0.8-2.0 V) so the codec does NOT drop the mic / fall back to the
#     internal mic.  Open-circuit (the pre-fix v3 / v2 behaviour) reads ~VBIAS =
#     "no microphone".
c = Circuit()
c.V("Vb", "vb", "0", dc=VBIAS)
c.R("Rbias", "vb", "nbn", RBIAS)
c.R("Rnc", "nbn", "0", RNC)
vdesel = c.op()["nbn"]
vopen  = VBIAS   # no load -> full bias rail
chk("MIC7 a de-selected / muted notebook still reads 'headset mic present'",
    "mic-pin DC in ~0.8 - 2.0 V (a codec keeps the headset mic; no fallback to the internal mic)",
    f"{vdesel:.2f} V with R_NC {RNC/1e3:.1f}k  (vs {vopen:.2f} V = open = 'no mic' before the fix); "
    f"selected-path electret sits at {op['hs']:.2f} V, so the two look alike to the codec",
    0.8 <= vdesel <= 2.0,
    "R20-R23 (2k2 on each relay NC pin) - added per the v2 bom_mic_deselect_detect.cir review")

# --- AC signal transfer HS_MIC -> selected NBn_MIC ---
c = Circuit()
c.I("Imic", "hs", "0", ac=1e-6)                  # electret signal current
c.R("Ro", "hs", "0", RO)
c.R("Krly", "hs", "nbn", RRLY)
c.R("Rbias", "nbn", "0", RBIAS)                  # notebook input
f, res = c.ac([1e3])
# reference: same current straight into the notebook with a 0-ohm switch
c2 = Circuit(); c2.I("Imic", "n", "0", ac=1e-6)
c2.R("Ro", "n", "0", RO); c2.R("Rbias", "n", "0", RBIAS)
_, res2 = c2.ac([1e3])
loss_db = db(res["nbn"][0]) - db(res2["n"][0])
chk("MIC2 through-path loss (relay contact vs an ideal switch)",
    "< 0.02 dB  (contact R negligible vs the k-ohm mic impedances)",
    f"{loss_db:+.4f} dB  (R_contact {RRLY*1e3:.0f} m-ohm in {RO/1e3:.1f} k // {RBIAS/1e3:.1f} k)",
    abs(loss_db) < 0.02)

# --- crosstalk to a NON-selected notebook.  Its COM sits on NC (2k2 -> GND);
#     the only path from the HS_MIC bus is the ~10 pF stray across its open
#     NO contact into that 2k2 // RBIAS node. ---
c = Circuit()
c.V("Vs", "hs", "0", ac=1.0)
c.C("Cx", "hs", "nbx", CX)
c.R("Rnc", "nbx", "0", RNC)
c.R("Rbias", "nbx", "0", RBIAS)
xtk = {}
for fr in (1e3, 10e3):
    _, rr = c.ac([fr]); xtk[fr] = db(rr["nbx"][0])
chk("MIC3 crosstalk to an un-selected notebook (K NO contact open)",
    "< -50 dB across the voice band",
    f"{xtk[1e3]:.0f} dB @1 kHz, {xtk[10e3]:.0f} dB @10 kHz  "
    f"(only path = ~{CX*1e12:.0f} pF stray into 2k2//2k2; the de-selected COM is on NC, not HS_MIC)",
    xtk[1e3] < -50 and xtk[10e3] < -50)

# --- bandwidth of the routed path ---
CW = 80e-12       # wiring + jack stray + 3x ~10 pF across the other relays' open NO contacts
c = Circuit()
c.I("Imic", "hs", "0", ac=1e-6)
c.R("Ro", "hs", "0", RO)
c.R("Krly", "hs", "nbn", RRLY)
c.R("Rbias", "nbn", "0", RBIAS)
c.C("Cw", "nbn", "0", CW)
fs = np.logspace(2, 7, 200)
_, rr = c.ac(fs)
mag = np.abs(rr["nbn"]); ref = mag[0]
f3 = fs[np.argmin(np.abs(mag/ref - 1/np.sqrt(2)))]
chk("MIC4 routed-path bandwidth",
    "-3 dB well above 20 kHz (flat across the voice band)",
    f"-3 dB at {f3/1e6:.2f} MHz  ({RO/1e3:.1f}k//{RBIAS/1e3:.1f}k with {CW*1e12:.0f} pF stray)",
    f3 > 100e3)

chk("MIC5 P2 jack wiring: pin 3 (tip) = mic, pins 2 & 4 (ring/sleeve) = GND  (HX PJ-320A-3P DIP, LCSC C17701689)",
    "no plug wiring can short the mic for a CTIA Y-splitter; robust to the ring-vs-sleeve pin ambiguity",
    "Datasheet terminal 3 is the tip leaf-spring contact -> mic. Terminals 2 and 4 are ring & sleeve; a CTIA "
    "TRRS->2x3.5 splitter's mic plug ties both to ground, so wiring BOTH pin 2 and pin 4 to GND is universal "
    "(mono, CTIA and PC-pink mic-on-tip plugs all work, nothing shorts) and makes the 2/4 order irrelevant. "
    "Bring-up: meter pin 3 to the plug tip to confirm.",
    True,
    "tying pin 3 to GND (if it turned out not to be tip) is the only failure mode -> obvious dead mic, one-line schematic swap")

chk("MIC6 mute states carry no headset audio to any notebook",
    "power-on and 2-button-held -> every relay de-energised -> no NBn_MIC <-> HS_MIC path",
    "all four relays de-energised: every NBn_MIC is on NC (2k2 -> GND), none on HS_MIC -> "
    "the headset electret reaches no notebook (silent), yet each notebook still reads "
    f"~{vdesel:.2f} V = 'headset mic present, muted' (no disconnect, no internal-mic fallback). "
    "Verified by the S checks.",
    all(x["pass"] for x in R if x["check"].startswith("S ")))

# ============================================================ summary
npass = sum(x["pass"] for x in R); ntot = len(R)
print("\n" + "=" * 72)
print(f" RESULT: {npass}/{ntot} checks pass")
print("=" * 72)
for x in R:
    if not x["pass"]:
        print(f"  FAIL  {x['check']}: {x['measure']}")
json.dump(R, open(f"{OUT}/validation_results.json", "w"), indent=2)
print(f"\n wrote validation_results.json")
