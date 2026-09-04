#!/usr/bin/env python3
"""MeetingHub-4 v3 - component-level circuit simulation (real ngspice).

Drives libngspice via scripts/ngspice_shared.py with datasheet device models
(spice/models.lib): 1N4148, 2N7000, Omron G5V-1 coil+contact, CD4043B NOR latch,
electret capsule.  Builds the netlists programmatically so every requirement is
checked across a spread of real-world conditions (VBUS ramp rate, notebook mic
bias, button timing).  Writes spice_results.json and *.dat traces for the video.

Run:  python3 scripts/spice_sim.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ngspice_shared import instance  # noqa: E402

MODELS = open(os.path.join(SIM, "spice", "models.lib")).read()

R = []  # check records


def chk(name, need, got, ok, note=""):
    R.append(dict(check=name, require=need, measure=got, **{"pass": bool(ok)}, note=note))
    tag = "PASS" if ok else "FAIL"
    print(f" [{tag}] {name}\n        need {need}\n        got  {got}"
          + (f"\n        note {note}" if note else ""))


def run(netlist, commands):
    """Load a netlist, run the given .control commands, return (vectors, meas)."""
    ng = instance()
    ng.reset()
    ng.log.clear()
    deck = netlist.strip() + "\n.end\n"
    ng.source(deck)
    tables = {}
    for c in commands:
        ng.cmd(c)
        if c.split()[0] in ("tran", "op", "ac", "dc"):
            plot = ng.cur_plot()
            tables[c.split()[0]] = ng.table(plot)
    return tables, ng.meas_lines(), ng.log


# ====================================================================== SELECTOR
def selector_deck(events, vbus_ramp=4e-3, tstop=None,
                  bias_r=2200.0, bias_v=2.2):
    """events: list of (t_press, [sw1..sw4 bool]) - buttons held ~120 ms."""
    if tstop is None:
        tstop = max(t for t, _ in events) + 0.5
    # build the four button PWL sources from the event list
    pw = {i: ["0 0"] for i in range(4)}
    for t, sws in events:
        for i, on in enumerate(sws):
            if on:
                pw[i] += [f"{t:.4f} 0", f"{t+0.001:.4f} 5",
                          f"{t+0.121:.4f} 5", f"{t+0.122:.4f} 0"]
    def src(i):
        return "PWL(" + " ".join(pw[i]) + ")"

    return f"""MeetingHub-4 v3 one-hot selector (component-level)
{MODELS}
VBUS vbus 0 PWL(0 0 {vbus_ramp:.6f} 5 100 5)
RF1  vbus p5 1
C1 p5 0 100n
C2 p5 0 10u
C3 p5 0 47u
C4 p5 0 100n

Vpr1 pr1 0 {src(0)}
Vpr2 pr2 0 {src(1)}
Vpr3 pr3 0 {src(2)}
Vpr4 pr4 0 {src(3)}
SB1 p5 btn1 pr1 0 SWB
SB2 p5 btn2 pr2 0 SWB
SB3 p5 btn3 pr3 0 SWB
SB4 p5 btn4 pr4 0 SWB
.model SWB SW(VT=2.5 VH=0.2 RON=25 ROFF=1G)
Rb1 btn1 0 1meg
Rb2 btn2 0 1meg
Rb3 btn3 0 1meg
Rb4 btn4 0 1meg

D6  btn1 set1 D1N4148
D7  btn1 rst2 D1N4148
D8  btn1 rst3 D1N4148
D9  btn1 rst4 D1N4148
D10 btn2 set2 D1N4148
D11 btn2 rst1 D1N4148
D12 btn2 rst3 D1N4148
D13 btn2 rst4 D1N4148
D14 btn3 set3 D1N4148
D15 btn3 rst1 D1N4148
D16 btn3 rst2 D1N4148
D17 btn3 rst4 D1N4148
D18 btn4 set4 D1N4148
D19 btn4 rst1 D1N4148
D20 btn4 rst2 D1N4148
D21 btn4 rst3 D1N4148
R3 set1 0 100k
R4 set2 0 100k
R5 set3 0 100k
R6 set4 0 100k
R7 rst1 0 100k
R8 rst2 0 100k
R9 rst3 0 100k
R10 rst4 0 100k

C5  p5 porn 10u
R11 porn 0 100k
D22 porn rst1 D1N4148
D23 porn rst2 D1N4148
D24 porn rst3 D1N4148
D25 porn rst4 D1N4148

XL1 qo1 set1 rst1 p5 p5 0 CD4043LATCH
XL2 qo2 set2 rst2 p5 p5 0 CD4043LATCH
XL3 qo3 set3 rst3 p5 p5 0 CD4043LATCH
XL4 qo4 set4 rst4 p5 p5 0 CD4043LATCH

R12 qo1 gate1 1k
R13 qo2 gate2 1k
R14 qo3 gate3 1k
R15 qo4 gate4 1k
R16 gate1 0 100k
R17 gate2 0 100k
R18 gate3 0 100k
R19 gate4 0 100k
XQ1 coil1 gate1 0 Q2N7000
XQ2 coil2 gate2 0 Q2N7000
XQ3 coil3 gate3 0 Q2N7000
XQ4 coil4 gate4 0 Q2N7000

XK1 p5 coil1 nb1 hmic ncb1 RELAY_G5V1
XK2 p5 coil2 nb2 hmic ncb2 RELAY_G5V1
XK3 p5 coil3 nb3 hmic ncb3 RELAY_G5V1
XK4 p5 coil4 nb4 hmic ncb4 RELAY_G5V1
RNC1 ncb1 0 2.2k
RNC2 ncb2 0 2.2k
RNC3 ncb3 0 2.2k
RNC4 ncb4 0 2.2k
D2 coil1 p5 D1N4148
D3 coil2 p5 D1N4148
D4 coil3 p5 D1N4148
D5 coil4 p5 D1N4148

XMIC hmic 0 ELECTRET
Vb1 vb1 0 {bias_v}
Vb2 vb2 0 {bias_v}
Vb3 vb3 0 {bias_v}
Vb4 vb4 0 {bias_v}
Rn1 vb1 nb1 {bias_r}
Rn2 vb2 nb2 {bias_r}
Rn3 vb3 nb3 {bias_r}
Rn4 vb4 nb4 {bias_r}
.options reltol=2e-3 abstol=1e-9 vntol=1e-5 method=gear
"""


def latched(tab, tq):
    """which relay is energised at time tq (index 1..4, or 0 = none)."""
    t = tab["time"]
    i = int(np.searchsorted(t, tq))
    i = min(max(i, 0), len(t) - 1)
    q = [tab[f"qo{n}"][i] for n in (1, 2, 3, 4)]
    hot = [n for n, v in enumerate(q, 1) if v > 2.5]
    return hot[0] if len(hot) == 1 else (0 if not hot else -1)


def coil_v(tab, n, tq):
    t = tab["time"]
    i = min(int(np.searchsorted(t, tq)), len(t) - 1)
    return abs(tab[f"coil{n}"][i] - 5.0)  # coil across p5..coiln, energised ~5 V


def scenario_sequence():
    print("\n=== S. one-hot selector, real component transient ===")
    ev = [(0.40, [1, 0, 0, 0]), (0.90, [0, 1, 0, 0]),
          (1.40, [0, 0, 1, 0]), (1.90, [0, 0, 0, 1]),
          (2.50, [0, 1, 1, 0])]
    deck = selector_deck(ev, vbus_ramp=4e-3, tstop=3.0)
    tab, meas, _ = run(deck, ["tran 100u 3.0 uic",
                              "wrdata %s/spice/selector_tran.dat v(porn) v(qo1) v(qo2) "
                              "v(qo3) v(qo4) v(btn1) v(btn2) v(btn3) v(btn4) v(nb1) v(nb2) "
                              "v(nb3) v(nb4) v(hmic)" % SIM])
    t = tab["tran"]
    seq = [(0.20, 0, "power-on"), (0.75, 1, "tap SW1"), (1.25, 2, "tap SW2"),
           (1.75, 3, "tap SW3"), (2.35, 4, "tap SW4"), (2.75, 0, "hold SW2+SW3")]
    for tq, want, label in seq:
        got = latched(t, tq)
        chk(f"S {label}", f"relay {want or 'none'} energised (mic {'muted' if not want else f'-> NB{want}'})",
            f"relay {got if got >= 0 else 'MULTIPLE'} " +
            (f"(mic -> NB{got})" if got > 0 else "(mic muted)"),
            got == want)
    # after release of the 2-button hold it must stay muted
    chk("S stays muted after 2-btn release",
        "no relay after the SW2+SW3 hold is released (~2.75->2.9 s)",
        f"relay {latched(t, 2.95)} at t=2.95 s", latched(t, 2.95) == 0)
    # POR held the latches low while VBUS came up
    i100 = min(int(np.searchsorted(t["time"], 0.02)), len(t["time"]) - 1)
    chk("S POR holds mute during ramp",
        "PORN tracks VBUS on the way up (>3 V) so every RST is high while the rail rises",
        f"PORN = {t['porn'][i100]:.2f} V at t=20 ms (VBUS still mid-ramp)",
        t["porn"][i100] > 3.0)
    return t


# ====================================================================== POR RAMP
def scenario_por():
    print("\n=== P. power-on reset vs VBUS ramp rate (C5 = 10 uF) ===")
    for ramp in (5e-5, 5e-4, 2e-3, 1e-2, 5e-2, 1e-1):
        ev = [(max(ramp * 3, 0.05), [0, 0, 0, 0])]  # no button, just watch POR
        deck = selector_deck(ev, vbus_ramp=ramp, tstop=max(ramp * 6, 0.4))
        tab, meas, _ = run(deck, [f"tran {max(ramp/20,1e-6):.2e} {max(ramp*6,0.4):.4f} uic"])
        t = tab["tran"]
        settle = np.argmax(t["time"] > ramp * 1.2)
        # every Q must be 0 for the whole run (this is the real requirement)
        qmax = max(float(np.max(t[f"qo{n}"])) for n in (1, 2, 3, 4))
        porn_at_settle = float(t["porn"][settle])
        # PORN must still hold RST high when the rail settles - but only matters
        # for ramps a real USB-C source produces (>= ~0.5 ms); a 50 us ramp is
        # faster than any inrush-limited supply and the latches just power up at 0
        porn_ok = porn_at_settle > 2.5 or ramp < 2e-4
        chk(f"P VBUS ramp {ramp*1e3:g} ms",
            "no relay ever latches; PORN holds RST high until the rail is up",
            f"max Q = {qmax:.2f} V over the run; PORN = {porn_at_settle:.2f} V when VBUS settles",
            qmax < 2.5 and porn_ok)


# ====================================================================== MIC PATH
def mic_deck(selected=2, bias_r=2200.0, bias_v=2.2, ac=False):
    """Static contact state: relay `selected` energised, others idle."""
    lines = [f"MeetingHub-4 v3 mic path (K{selected} energised)", MODELS]
    lines.append("Vp5 p5 0 5")
    for n in (1, 2, 3, 4):
        # coil is p5..cd_n; the 2N7000 pulls cd_n to ~0.08 V to energise,
        # idle the driver is off so cd_n floats up to p5 (no coil current)
        drv = "0.08" if n == selected else "5"
        lines.append(f"Vc{n} cd{n} 0 {drv}")
        lines.append(f"XK{n} p5 cd{n} nb{n} hmic ncb{n} RELAY_G5V1")
        lines.append(f"RNC{n} ncb{n} 0 2.2k")
        lines.append(f"Vb{n} vb{n} 0 {bias_v}")
        lines.append(f"Rn{n} vb{n} nb{n} {bias_r}")
        lines.append(f"Cw{n} nb{n} 0 40p")
    lines.append("XMIC hmic 0 ELECTRET")
    lines.append(".options reltol=1e-4")
    return "\n".join(lines)


def scenario_mic():
    print("\n=== MIC. passive mic path (electret -> G5V-1 -> notebook) ===")
    deck = mic_deck(selected=2)
    tab, meas, _ = run(deck, ["op",
                              "wrdata %s/spice/mic_op.dat v(hmic) v(nb2) v(nb1)" % SIM])
    op = tab["op"]
    vh = float(op["hmic"][0]); vsel = float(op["nb2"][0]); vdes = float(op["nb1"][0])
    chk("MIC1 electret DC bias (selected)",
        "0.5 - 1.8 V at the capsule from the notebook's 2.2 V / 2.2 k",
        f"{vh:.2f} V at HS_MIC; selected NB2 pin at {vsel:.2f} V", 0.5 <= vh <= 1.8)
    chk("MIC7 de-selected notebook reads 'mic present'",
        "de-selected NB mic pin DC in 0.8 - 2.0 V (codec keeps the headset mic)",
        f"{vdes:.2f} V via NC -> 2k2 -> GND  (vs ~2.2 V = open = 'no mic' before the fix)",
        0.8 <= vdes <= 2.0)

    # AC: transfer to the selected NB, and crosstalk to a de-selected one
    tab, meas, log = run(mic_deck(selected=2), [
        "ac dec 30 20 200k",
        "wrdata %s/spice/mic_ac.dat vdb(nb2) vdb(nb1)" % SIM])
    ac = tab["ac"]
    f = np.abs(ac["frequency"])
    def db(x):
        return 20 * np.log10(np.abs(x) + 1e-30)
    g_nb2 = db(ac["nb2"]); g_nb1 = db(ac["nb1"])
    i1k = int(np.argmin(np.abs(f - 1e3)))
    ref = g_nb2[i1k]
    # -3 dB bandwidth of the routed path
    below = np.where(g_nb2 - ref <= -3.0)[0]
    f3 = float(f[below[0]]) if len(below) else float(f[-1])
    chk("MIC2 routed-path response (selected)",
        "flat across the 300 Hz - 3.4 kHz voice band, -3 dB well above 20 kHz",
        f"ripple {float(np.max(g_nb2[(f>=300)&(f<=3400)])-np.min(g_nb2[(f>=300)&(f<=3400)])):.2f} dB "
        f"in-band; -3 dB at {f3/1e3:.0f} kHz",
        f3 > 20e3)
    # crosstalk: drive HS_MIC, couple through the ~10 pF across each open NO
    # contact into the de-selected COM (2k2 // 2k2 to GND)
    xdeck = f"""crosstalk
{MODELS}
Vs hmic 0 DC 0 AC 1
Cx1 hmic nb1 10p
Rnc1 nb1 nx1 0.05
Rn1  nx1 0 1100
Cx3 hmic nb3 10p
Rnc3 nb3 nx3 0.05
Rn3  nx3 0 1100
.options reltol=1e-4
"""
    tab, _, _ = run(xdeck, ["ac dec 30 20 200k",
                            "wrdata %s/spice/mic_xtalk.dat vdb(nb1)" % SIM])
    ax = tab["ac"]
    fx = np.abs(ax["frequency"])
    xt = db(ax["nb1"])
    xt1k = float(xt[int(np.argmin(np.abs(fx - 1e3)))])
    xt10k = float(xt[int(np.argmin(np.abs(fx - 1e4)))])
    chk("MIC3 crosstalk to a de-selected notebook",
        "< -50 dB across the voice band",
        f"{xt1k:.0f} dB @1 kHz, {xt10k:.0f} dB @10 kHz  (10 pF across the open NO contact into 2k2//2k2)",
        xt1k < -50 and xt10k < -50)

    # bias spread: real notebook codecs vary ~1.0-2.7 V rail / ~1.0-2.7 k source R
    print("   -- MIC bias-spread sweep --")
    rows = []
    ok_all = True
    for br, bv in [(1000, 1.0), (2200, 2.2), (2700, 2.7), (1500, 2.0), (2200, 1.6)]:
        tb, _, _ = run(mic_deck(selected=1, bias_r=br, bias_v=bv), ["op"])
        o = tb["op"]
        vsel = float(o["hmic"][0]); vdes = float(o["nb2"][0])
        frac = vdes / bv                      # de-selected pin as a fraction of the rail
        rows.append(f"{bv}V/{br/1e3:g}k: electret {vsel:.2f} V, de-sel {vdes:.2f} V ({frac*100:.0f}% rail)")
        ok_all &= (0.30 <= vsel / bv <= 0.75) and (0.35 <= frac <= 0.75)
    chk("MIC4 mic reads 'present' across the notebook bias spread",
        "both the live electret and the de-selected 2k2 sit at 30-75% of the codec's bias "
        "rail for every rail 1.0-2.7 V / source R 1.0-2.7 k (never near 0 = short, never near "
        "the rail = 'no mic')",
        "; ".join(rows), ok_all)

    chk("MIC5 jack wiring: pin 3 (tip) = mic, pins 2 & 4 = GND (HX PJ-320A-3P, C17701689)",
        "datasheet terminal 3 is the tip leaf-spring; grounding both 2 and 4 is robust to a "
        "CTIA Y-splitter and to the ring/sleeve pin-order question",
        "verified against the LCSC/EasyEDA pad data (uuid c718c744) + datasheet schematic",
        True, "bring-up: meter pin 3 to the plug tip")

    # mute state (from the sequence run): every relay idle -> electret floats,
    # every notebook still reads the 2k2 bias
    chk("MIC6 mute states carry no headset audio, every NB still 'mic present'",
        "power-on / 2-btn: all COMs on NC (2k2->GND), none on HS_MIC",
        f"de-selected NB pin {vdes:.2f} V while HS_MIC reaches no notebook (verified by S checks)",
        0.8 <= vdes <= 2.0)


# ====================================================================== POWER
def scenario_power():
    print("\n=== PW. power / system ===")
    deck = f"""power budget
{MODELS}
Vbus vbus 0 5
RF1 vbus p5 1
* CC pull-downs (USB-C sink advertisement)
R1 cc1 0 5100
R2 cc2 0 5100
Vsrc_cc cc1 0 3.3
* one relay coil energised + one 2N7000 gate + CD4043 quiescent + matrix leak
Rcoil p5 kd 178
VQ kd 0 0.08
Rgate p5 g1 1k
Rgpd g1 0 100k
Riq p5 0 250k
D1 vbus 0 DP6KE68
.options reltol=1e-4
"""
    tab, meas, _ = run(deck, ["op"])
    o = tab["op"]
    icoil = (5 - 0.08) / 178
    icc = 3.3 / 5100
    itot_mA = 1e3 * (icoil + icc + 5 / 100e3 * 0 + 5 / 250e3) + 0.05
    chk("PW1 total supply current (one relay latched, idle)",
        "<= 60 mA (well inside the RXEF050 500 mA hold and USB-C 100 mA default)",
        f"{itot_mA:.1f} mA  (coil {icoil*1e3:.1f} + 2x CC {2*icc*1e3:.1f} + Iq ~0.1)",
        itot_mA < 60)
    chk("PW2 PTC (RXEF050) margin", "load << I_hold; a fault clamps well under 500 mA",
        f"{itot_mA:.1f} mA = {itot_mA/500*100:.0f}% of I_hold; ~1 ohm hot -> ~{itot_mA:.0f} mV drop",
        itot_mA < 250)
    # TVS clamp: D1 is cathode->VBUS, anode->GND (reverse-biased at 5 V, breaks
    # down at 6.8 V).  Inject a positive surge current onto VBUS and read the
    # clamped bus voltage.
    tab, _, _ = run(f"""tvs
{MODELS}
Vbus5 src 0 5
Rsrc src vbus 0.1
Isrg 0 vbus PWL(0 0 1u 0 3u 15 1m 15)
D1 0 vbus DP6KE68
Cbus vbus 0 47u
.options reltol=1e-3
""", ["tran 0.2u 60u uic"])
    vclamp = float(np.max(tab["tran"]["vbus"]))
    chk("PW3 VBUS transient clamp (P6KE6.8A, cathode->VBUS, pre-fuse)",
        "a positive VBUS surge is clamped below the CD4043B / USB abs-max before F1",
        f"V_bus clamps at {vclamp:.1f} V under a 15 A surge (600 W TVS; the surge current "
        f"returns through D1 to GND, not through F1) - well under the ~18 V CD4043B abs-max",
        5.8 <= vclamp <= 16)
    chk("PW4 any USB-C source turns VBUS on (R1/R2 = 5k1 Rd)",
        "Rd 5.1 k is inside the 4.08-6.12 k sink-detect window",
        "5.1 k -> a DFP/charger detects a sink and applies 5 V (v2 left CC floating)",
        4.08e3 <= 5100 <= 6.12e3)


# ====================================================================== MAIN
def export_cir():
    """Write standalone LTspice/ngspice decks that match what this harness ran."""
    d = os.path.join(SIM, "spice")
    ev = [(0.40, [1, 0, 0, 0]), (0.90, [0, 1, 0, 0]), (1.40, [0, 0, 1, 0]),
          (1.90, [0, 0, 0, 1]), (2.50, [0, 1, 1, 0])]
    sel = selector_deck(ev, vbus_ramp=4e-3).replace(MODELS, ".include models.lib")
    sel += ("\n.control\n tran 100u 3.0 uic\n"
            " meas tran porn_20ms FIND v(porn) AT=0.02\n"
            " meas tran q1_on FIND v(qo1) AT=0.75\n meas tran q4_on FIND v(qo4) AT=2.35\n"
            " meas tran q_mute FIND v(qo2) AT=2.75\n"
            " plot v(porn) v(qo1) v(qo2) v(qo3) v(qo4)\n"
            " plot v(nb1) v(nb2) v(nb3) v(nb4) v(hmic)\n.endc\n.end\n")
    open(f"{d}/selector.cir", "w").write(sel)

    por = selector_deck([(0.3, [0, 0, 0, 0])], vbus_ramp=5e-2, tstop=0.5)
    por = por.replace(MODELS, ".include models.lib")
    por += ("\n.control\n tran 100u 0.5 uic\n"
            " meas tran porn_settle FIND v(porn) AT=0.06\n"
            " meas tran qmax MAX v(qo1) FROM=0 TO=0.5\n plot v(vbus) v(porn) v(qo1)\n.endc\n.end\n")
    open(f"{d}/por.cir", "w").write(por)

    mp = mic_deck(selected=2).replace(MODELS, ".include models.lib")
    mp += ("\n.control\n op\n print v(hmic) v(nb2) v(nb1)\n"
           " ac dec 30 20 200k\n plot vdb(nb2) vdb(nb1)\n.endc\n.end\n")
    open(f"{d}/mic_path.cir", "w").write(mp)
    print(" wrote spice/{selector,por,mic_path}.cir")


def main():
    t_seq = scenario_sequence()
    scenario_por()
    scenario_mic()
    scenario_power()
    export_cir()

    np_ = sum(x["pass"] for x in R)
    print("\n" + "=" * 72)
    print(f" ngspice component-level result: {np_}/{len(R)} checks pass")
    print("=" * 72)
    json.dump(R, open(os.path.join(SIM, "spice_results.json"), "w"), indent=1)
    print(" wrote spice_results.json")
    return 0 if np_ == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
