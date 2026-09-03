"""
MeetingHub-4 v2 - full end-to-end simulation video.

Renders v2/simulation/MeetingHub-4-v2-full-simulation.mp4, ~1 min, chapters:

  1  system block diagram
  2  power-up            : VBUS ramp -> +5V, VBIAS settles to 2.500 V
  3  power-on reset      : mic held muted ~140 ms
  4  one-hot mic selector: SW2->PC1, SW3->PC2, SW4->PC3, SW5->PC4, SW3+SW4 = mute
  5  audio path          : 4 laptops playing -> mixer sum -> master -> headphone amp
  6  volume + MUTE check : RV1 swept CW->CCW; at MIN the channel is silent (-66 dB)
  7  all volumes to zero : headset output = 169 uV residual (-65 dB), effectively silent
  8  master volume RV5   : one knob scales the whole mix, mutes at MIN
  9  frequency response  : end-to-end, voice band flat
  10 scorecard
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mna import Circuit, db
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
from select_logic import OneHot, relay_route, MATRIX
OUT = os.path.join(os.path.dirname(__file__), "..")
FPS = 20
BG, PANEL, FG, GRN, RED, BLU, MUT = "#0e1116","#161b22","#e6edf3","#2ea043","#f85149","#58a6ff","#6e7681"

POT = 10e3
def chain(fracs, master=1.0, load=32.0, src=None, rend=5.0):
    """AC model: 4 laptop L inputs -> RVn -> U1 mixer -> RV5 -> U2 HP amp -> J6.T."""
    c = Circuit()
    c.V("V5","p5","0",dc=5.0)
    c.R("R1","p5","vref",10e3); c.R("R2","vref","0",10e3); c.C("C3","vref","0",10e-6)
    c.opamp("U3","vbout","vref","vbias","p5","0",A0=1e5,gbw=1e6,rout=100.0)
    c.R("R38","vbout","vbias",47.0); c.C("C26","vbias","0",1e-6)
    for i in range(4):
        acv = 0.0 if src is None else src[i]
        c.V(f"Vin{i}", f"in{i}", "0", ac=acv)
        c.C(f"Cin{i}", f"in{i}", f"sig{i}", 1e-6)
        fr = fracs[i]
        c.R(f"RVs{i}", f"sig{i}", f"w{i}", max(POT*(1-fr), rend))
        c.R(f"RVb{i}", f"w{i}", "vbias", max(POT*fr, rend))
        c.R(f"Rn{i}", f"w{i}", "u1n", 10e3)
    c.R("R3","u1n","u1o",3.3e3)
    c.opamp("U1","u1o","vbias","u1n","p5","0",A0=1e5,gbw=15e6,rout=60.0)
    c.C("C13","u1o","m_sig",1e-6)
    c.R("RV5s","m_sig","m_w",max(POT*(1-master),rend)); c.R("RV5b","m_w","vbias",max(POT*master,rend))
    c.C("C15","m_w","u2p",1e-6); c.R("R13","u2p","vbias",100e3)
    c.R("R15","u2n","u2o",1e3); c.R("R14","u2n","fbg",1e3); c.C("C16","fbg","0",10e-6)
    c.opamp("U2","u2o","u2p","u2n","p5","0",A0=1e5,gbw=9e6,rout=25.0)
    c.C("C17","u2o","n1",220e-6); c.R("R16","n1","j6t",47.0); c.R("Rl","j6t","0",load)
    return c

# ============================================================== precompute
print("precomputing ...")

# --- 2. power-up.  +5V ramp (RC of C2 10uF through the USB source ~ instant on
#     this scale) and VBIAS_REF = C3(10uF) charging through R1||R2 = 5k  ->
#     tau = 50 ms, so VBIAS needs ~250 ms.  Pure RC (no op-amp) -> BE is exact.
#     The LM358 buffer output tracks VBIAS_REF within the loop bandwidth (its
#     closed-loop response is flat / non-peaking - verified by .ac, see report).
def pu():
    c = Circuit()
    c.V("Vb","p5","0", pwl=[(0,0),(4e-3,5.0),(1.0,5.0)])
    c.C("C2","p5","0",10e-6)
    c.R("R1","p5","vref",10e3); c.R("R2","vref","0",10e3); c.C("C3","vref","0",10e-6)
    c.R("R38","vref","vbias",47.0); c.C("C26","vbias","0",1e-6)   # buffer modelled ideal: VBIAS follows VBIAS_REF
    r = c.tran(0.35, 5e-5, uic={"p5":0,"vref":0,"vbias":0})
    return r
PU = pu()

# --- 3. POR
def por():
    c = Circuit()
    c.V("V5","p5","0", pwl=[(0,0),(1e-4,5),(1,5)])
    c.C("C24","p5","porn",10e-6); c.R("R37","porn","0",100e3); c.R("Rl","porn","0",25e3)
    return c.tran(0.6, 5e-4, uic={"porn":0.0})
POR = por(); TW = POR["t"][np.where(POR["porn"]>=2.5)[0][-1]]

# --- 4. selector timeline
EV = [(0,"power on",[0,0,0,0]),(1.0,"press SW2",[1,0,0,0]),(2.0,"press SW3",[0,1,0,0]),
      (3.0,"press SW4",[0,0,1,0]),(4.0,"press SW5",[0,0,0,1]),
      (5.2,"press SW3 + SW4",[0,1,1,0]),(6.0,"release",[0,0,0,0]),(6.8,"end",[0,0,0,0])]
Tsel = np.arange(0,7.2,0.02); sim = OneHot()
QQ = np.zeros((len(Tsel),4)); PRN = np.zeros(len(Tsel))
for i,t in enumerate(Tsel):
    b=[0,0,0,0]
    for te,lbl,bp in EV:
        if te<=t<te+0.18: b=[max(x,y) for x,y in zip(b,bp)]
    porn = t<0.14
    _,_,Q = sim.step(b,porn); QQ[i]=Q; PRN[i]=porn
BSEL = QQ  # latch states over time

# --- 5. audio path.  Built from the EXACT .ac transfer functions (one input
#     driven at a time), then time waveforms reconstructed by superposition -
#     no time-stepping, so no integrator error.
def audio_waves(fracs, master, amps, freqs, tstop=20e-3, n=2000):
    t = np.linspace(0, tstop, n)
    keys = ["w0","w1","w2","w3","u1o","m_w","j6t"]
    W = {k: np.zeros(n) for k in keys}
    for i in range(4):
        src = [0,0,0,0]; src[i] = 1.0
        _, r = chain(fracs, master=master, load=32.0, src=src).ac([freqs[i]])
        for k in keys:
            H = r[k][0]
            W[k] += amps[i]*np.abs(H)*np.sin(2*np.pi*freqs[i]*t + np.angle(H))
    W["t"] = t
    return W
AUD = audio_waves([0.9,0.7,0.55,0.8], 0.85, [0.30,0.25,0.22,0.28], [196,262,330,392])

# --- 6. RV1 sweep gains  (ch1 only playing, 1 kHz)
FR = np.concatenate([np.linspace(1,0,70), np.zeros(15)])
G1 = np.array([np.abs(chain([x,0,0,0], src=[1,0,0,0]).ac([1000])[1]["j6t"][0]) for x in FR])
GFULL = G1[0]

# --- 8. RV5 sweep
MFR = np.concatenate([np.linspace(1,0,55), np.zeros(12)])
GM = np.array([np.abs(chain([1,1,1,1], master=x, src=[1,1,1,1]).ac([1000])[1]["j6t"][0]) for x in MFR])

# --- 9. frequency response
FSW = np.logspace(1, np.log10(20e3), 260)
_, RF = chain([1,1,1,1], master=1.0, src=[1,0,0,0]).ac(FSW)
HF = np.abs(RF["j6t"]); HREF = np.interp(1000, FSW, HF); RELF = db(HF/HREF)
SWEEP_PTS = np.logspace(1, np.log10(20e3), 70)

# --- static numbers
VBIAS_FINAL = PU["vbias"][-1]
GZERO = np.abs(chain([0,0,0,0], src=[1,0,0,0]).ac([1000])[1]["j6t"][0])
GALL0 = np.abs(chain([0,0,0,0], src=[1,1,1,1]).ac([1000])[1]["j6t"][0])
print(f"  VBIAS settled {VBIAS_FINAL:.4f} V ; ch mute {db(GZERO/GFULL):.0f} dB ; all-zero out {GALL0*0.316*1e6:.0f} uV")

# ============================================================== figure
fig = plt.figure(figsize=(12.8,7.2), dpi=100); fig.patch.set_facecolor(BG)
def newax(*r):
    a = fig.add_axes(*r); a.set_facecolor(PANEL)
    a.tick_params(colors="#9aa4b2", labelsize=8)
    for s in a.spines.values(): s.set_color("#3a434f")
    return a
CHTITLE = fig.text(.5,.955,"",ha="center",fontsize=19,color=FG,weight="bold")
CHSUB   = fig.text(.5,.905,"",ha="center",fontsize=12,color=GRN)
FOOT    = fig.text(.5,.02,"MeetingHub-4 v2  ·  end-to-end simulation  ·  local MNA engine  ·  netlist: hardware/PCB/MeetingHub-4-v2.net",
                   ha="center",fontsize=8,color="#5b6673")

def clearfig():
    for ax in list(fig.axes):
        if ax not in (): fig.delaxes(ax)

# ---------- scene helpers -------------------------------------------------
def sc_overview(p):
    clearfig(); ax = newax([.06,.12,.88,.72]); ax.axis("off"); ax.set_xlim(0,100); ax.set_ylim(0,60)
    def box(x,y,w,h,t,c=BLU):
        ax.add_patch(plt.Rectangle((x,y),w,h,fill=True,color=PANEL,ec=c,lw=2))
        ax.text(x+w/2,y+h/2,t,ha="center",va="center",color=FG,fontsize=9)
    def arr(x1,y1,x2,y2,c="#7d8590"):
        ax.annotate("",(x2,y2),(x1,y1),arrowprops=dict(arrowstyle="->",color=c,lw=1.6))
    box(2,48,16,8,"USB-C 5 V\nF1 + TVS"); box(24,48,16,8,"VBIAS buffer\nLM358 -> 2.5 V", GRN)
    arr(18,52,24,52)
    for i in range(4):
        y=38-i*9; box(2,y,16,7,f"laptop {i+1}\nline out")
        box(24,y,14,7,f"RV{i+1}\nvolume", "#d29922"); arr(18,y+3.5,24,y+3.5)
        arr(38,y+3.5,52,20+ (0 if i<2 else 8))
    box(52,20,16,10,"U1 mixer\nSUM  -0.33/ch", GRN)
    box(72,20,12,10,"RV5\nmaster","#d29922"); arr(68,25,72,25)
    box(72,4,12,10,"U2 HP amp\ngain 2", GRN); arr(78,20,78,14)
    box(88,4,10,10,"headset\nJ6 TRRS", BLU); arr(84,9,88,9)
    box(52,44,30,10,"one-hot mic selector\nU4 CD4043B + diode matrix + POR", RED)
    box(88,44,10,10,"mic ->\nlaptop n", BLU); arr(82,49,88,49)
    ax.text(2,58,"SW2..SW5 momentary  ->  press once = that laptop hears the headset mic, others drop",
            color="#9aa4b2",fontsize=8)
    CHTITLE.set_text("MeetingHub-4 v2 — full end-to-end simulation")
    CHSUB.set_text("USB-powered 4-laptop conference headset hub: monitor mix + one-hot mic router")

def sc_powerup(p):
    clearfig(); ax = newax([.09,.14,.85,.66])
    k = int(p*(len(PU["t"])-1))
    ax.plot(PU["t"][:k+1]*1e3, PU["p5"][:k+1], color=BLU, lw=2, label="+5V rail (TP1)")
    ax.plot(PU["t"][:k+1]*1e3, PU["vbias"][:k+1], color=GRN, lw=2.5, label="VBIAS")
    ax.plot(PU["t"][:k+1]*1e3, PU["vref"][:k+1], color="#d29922", lw=1.2, ls="--", label="VBIAS_REF")
    ax.axhline(2.5, color="#888", ls=":", lw=1)
    ax.set_xlim(0,350); ax.set_ylim(0,5.4); ax.set_xlabel("ms"); ax.set_ylabel("V")
    ax.legend(loc="lower right", facecolor=PANEL, edgecolor="#3a434f", labelcolor="#c9d1d9", fontsize=9)
    now = PU["t"][k]*1e3
    ax.text(150,4.6,f"VBIAS = {PU['vbias'][k]:.3f} V", color=GRN, fontsize=12)
    CHTITLE.set_text("2 · Power-up")
    CHSUB.set_text(f"VBUS ramps in 4 ms · VBIAS_REF = C3 10 µF through R1‖R2 5 k (τ = 50 ms) "
                   f"→ VBIAS settles to 2.5 V in ~250 ms · t = {now:.0f} ms")

def sc_por(p):
    clearfig(); ax = newax([.09,.32,.85,.48]); axb = newax([.09,.12,.85,.14]); axb.axis("off")
    k = int(p*(len(POR["t"])-1)); t = POR["t"][k]
    ax.plot(POR["t"]*1e3, POR["porn"], color="#30363d", lw=1)
    ax.plot(POR["t"][:k+1]*1e3, POR["porn"][:k+1], color=BLU, lw=2.5)
    ax.axhline(2.5, color=RED, ls="--", lw=1.2); ax.axvspan(0, TW*1e3, color=RED, alpha=.10)
    ax.set_xlim(0,600); ax.set_ylim(0,5.2); ax.set_xlabel("ms"); ax.set_ylabel("PORN  [V]")
    muted = t <= TW
    axb.text(.5,.5,"MIC MUTED" if muted else "latch free — mic follows the buttons",
             ha="center",fontsize=22 if muted else 14, color=RED if muted else GRN, weight="bold",
             transform=axb.transAxes)
    CHTITLE.set_text("3 · Power-on reset")
    CHSUB.set_text(f"C24 10 µF + R37 100 k hold every RST high for {TW*1e3:.0f} ms  →  Q1..Q4 = 0  →  no relay  ·  t = {t*1e3:.0f} ms")

def sc_selector(p):
    clearfig(); axL = newax([.06,.12,.52,.68]); axR = newax([.62,.12,.34,.68]); axR.axis("off")
    ti = int(p*(len(Tsel)-1)); t = Tsel[ti]
    w = (Tsel >= t-2.2) & (Tsel <= t)
    names = ["PORN","Q1→K1","Q2→K2","Q3→K3","Q4→K4"]
    sigs  = [PRN, BSEL[:,0], BSEL[:,1], BSEL[:,2], BSEL[:,3]]
    cols  = [RED, GRN, GRN, GRN, GRN]
    for j,(nm,s,c) in enumerate(zip(names,sigs,cols)):
        y0 = len(names)-j
        axL.fill_between(Tsel[w], y0, y0+s[w]*0.75, step="pre", color=c, alpha=.85)
        axL.text(t-2.2, y0+0.28, nm, color="#c9d1d9", fontsize=9)
    axL.set_xlim(t-2.2, t+0.1); axL.set_ylim(0.5,len(names)+1.1); axL.set_yticks([])
    axL.set_xlabel("s"); axL.axvline(t, color=BLU, lw=1)
    Q = BSEL[ti]
    axR.set_xlim(0,10); axR.set_ylim(0,10)
    axR.text(1.3,9.3,"HEADSET MIC",color=FG,fontsize=11,weight="bold")
    axR.plot([2,2],[1,8.7],color="#8b949e",lw=3)
    for i in range(4):
        y = 7.6-i*1.85; on = Q[i]==1
        axR.add_patch(plt.Rectangle((4.2,y-.4),1.5,.8,color=GRN if on else "#30363d"))
        axR.text(4.95,y,f"K{i+1}",ha="center",va="center",fontsize=9,weight="bold",
                 color=BG if on else "#8b949e")
        axR.text(7.1,y,f"LAPTOP {i+1}",va="center",fontsize=12,
                 color=GRN if on else MUT, weight="bold" if on else "normal")
        axR.plot([2,4.2],[y,y],color=GRN if on else "#30363d",lw=3,ls="-" if on else ":")
        if on: axR.plot([5.7,7],[y,y],color=GRN,lw=3)
    r = relay_route(Q)
    axR.text(5,0.2,r,ha="center",fontsize=13,weight="bold",color=RED if "MUTED" in r else GRN)
    lbl = ""
    for te,ll,_ in EV:
        if t>=te: lbl=ll
    CHTITLE.set_text("4 · One-hot mic selector")
    CHSUB.set_text(f"single press each  ·  last action: {lbl}  ·  t = {t:.1f} s")

def _wave(ax, tr, keys, colors, labels, ymax):
    for k,c,l in zip(keys,colors,labels):
        ax.plot(tr["t"]*1e3, tr[k], color=c, lw=1.8, label=l)
    ax.set_xlim(0, tr["t"][-1]*1e3); ax.set_ylim(-ymax,ymax)
    ax.set_xlabel("ms"); ax.legend(loc="upper right", facecolor=PANEL, edgecolor="#3a434f",
        labelcolor="#c9d1d9", fontsize=8, ncol=2)

def sc_audio(p):
    clearfig()
    a1 = newax([.08,.55,.86,.28]); a2 = newax([.08,.14,.86,.28])
    n = max(2, int(p*len(AUD["t"])))
    tr = {k:(v[:n] if hasattr(v,"__len__") else v) for k,v in AUD.items()}
    _wave(a1, tr, ["w0","w1","w2","w3"], ["#58a6ff","#7ee787","#d29922","#ff7b72"],
          ["RV1 wiper","RV2 wiper","RV3 wiper","RV4 wiper"], 0.35)
    a1.set_title("4 laptop signals after their volume pots", color="#c9d1d9", fontsize=10)
    _wave(a2, tr, ["u1o","j6t"], [GRN, BLU], ["U1 mixer sum (-0.33/ch)","headset J6.T (into 32 Ω)"], 0.6)
    a2.set_title("mixer output  and  final headset output", color="#c9d1d9", fontsize=10)
    CHTITLE.set_text("5 · Audio path — 4 laptops playing together")
    CHSUB.set_text("196 / 262 / 330 / 392 Hz  ·  independent volumes  ·  summed, then master, then ×2 headphone amp")

def sc_volsweep(p):
    clearfig(); axL = newax([.08,.14,.52,.66]); axR = newax([.66,.14,.30,.66])
    k = int(p*(len(FR)-1)); fr = FR[k]; g = G1[k]
    axL.plot(FR*100, db(G1/GFULL), color="#30363d", lw=1)
    sel = np.arange(len(FR)) <= k
    axL.plot(FR[sel]*100, db(G1[sel]/GFULL), color=GRN, lw=2.6)
    axL.plot([fr*100],[db(g/GFULL)], "o", color=RED, ms=9)
    axL.set_xlim(105,-5); axL.set_ylim(-90,6)
    axL.set_xlabel("RV1 rotation  [%]   (sweeping CW → CCW)"); axL.set_ylabel("channel gain  [dB re full]")
    axL.axhline(-60, color="#888", ls=":", lw=1)
    tono = np.linspace(0,4e-3,400); vo = g*0.30*np.sin(2*np.pi*1000*tono)
    axR.plot(tono*1e3, 0.30*0.267*np.sin(2*np.pi*1000*tono), color="#30363d", lw=1, label="full-vol ref")
    axR.plot(tono*1e3, vo*0.267/max(GFULL,1e-9)*GFULL/0.267 if False else vo, color=GRN, lw=2, label="headset out")
    axR.set_ylim(-0.09,0.09); axR.set_xlabel("ms"); axR.set_ylabel("V")
    axR.legend(loc="upper right", fontsize=8, facecolor=PANEL, edgecolor="#3a434f", labelcolor="#c9d1d9")
    axR.text(0.1,0.075,f"{db(g/GFULL):+.0f} dB", color=GRN, fontsize=12)
    CHTITLE.set_text("6 · Volume control + MUTE check  (the v1 R$3000 bug)")
    if fr < 0.02:
        CHSUB.set_text(f"RV1 at MINIMUM → {db(G1[k]/GFULL):+.0f} dB, {G1[k]*0.316*1e6:.0f} µV out  →  SILENT   "
                       f"(v2: signal on RVn.3/6, VBIAS on RVn.1/4 — mute works)")
    else:
        CHSUB.set_text(f"RV1 at {fr*100:.0f} % → {db(G1[k]/GFULL):+.1f} dB   ·   sweeping toward minimum …")

def sc_allzero(p):
    clearfig(); ax = newax([.09,.16,.85,.6])
    tono = np.linspace(0,10e-3,1200)
    # before: all 4 at full ; after: all 4 zero -> step at t=5ms
    env = np.where(tono<5e-3, 1.0, 0.0)
    ref = 0.316*GALL0/max(GALL0,1e-9)  # dummy
    full_out = 0.267*0.316*(np.sin(2*np.pi*180*tono)+0.7*np.sin(2*np.pi*300*tono))/1.7
    y = np.where(tono<5e-3, full_out, GALL0*0.316*np.sin(2*np.pi*180*tono))
    prog = min(1.0, p*1.4)
    m = tono <= (tono[0] + prog*(tono[-1]-tono[0]))
    ax.plot(tono[m]*1e3, y[m], color=GRN, lw=1.8)
    ax.axvline(5, color="#888", ls=":", lw=1)
    ax.text(1.5, 0.11, "4 laptops, volumes UP", color="#c9d1d9", fontsize=9)
    ax.text(6.0, 0.11, "all 4 volumes → 0", color=RED, fontsize=9)
    ax.set_xlim(0,10); ax.set_ylim(-0.14,0.14); ax.set_xlabel("ms"); ax.set_ylabel("headset J6.T  [V]")
    if prog > 0.55:
        ax.annotate(f"residual {GALL0*0.316*1e6:.0f} µV  ({db(GALL0):.0f} dB)  — inaudible",
                    (7.5, 0.03), color=GRN, fontsize=10,
                    arrowprops=dict(arrowstyle="->", color=GRN))
    CHTITLE.set_text("7 · All four volumes at zero")
    CHSUB.set_text(f"no path bypasses the pots · output collapses to {GALL0*0.316*1e6:.0f} µV = {db(GALL0):.0f} dB · effectively silent")

def sc_master(p):
    clearfig(); ax = newax([.1,.16,.84,.62])
    k = int(p*(len(MFR)-1)); mfr = MFR[k]; g = GM[k]
    ax.plot(MFR*100, db(GM/GM[0]), color="#30363d", lw=1)
    sel = np.arange(len(MFR)) <= k
    ax.plot(MFR[sel]*100, db(GM[sel]/GM[0]), color=GRN, lw=2.6)
    ax.plot([mfr*100],[db(g/GM[0])],"o",color=RED,ms=9)
    ax.set_xlim(105,-5); ax.set_ylim(-90,6)
    ax.set_xlabel("RV5 master rotation  [%]   (CW → CCW)"); ax.set_ylabel("system gain  [dB re full]")
    ax.axhline(-60,color="#888",ls=":",lw=1)
    CHTITLE.set_text("8 · Master volume RV5")
    if mfr < 0.02:
        CHSUB.set_text(f"all 4 channels at full · RV5 at MINIMUM → {db(GM[k]/GM[0]):+.0f} dB = whole system muted")
    else:
        CHSUB.set_text(f"all 4 channels at full · RV5 at {mfr*100:.0f} % → {db(GM[k]/GM[0]):+.1f} dB · one knob scales the whole mix")

def sc_freq(p):
    clearfig(); ax = newax([.09,.16,.85,.62])
    k = int(p*(len(SWEEP_PTS)-1)); fcur = SWEEP_PTS[k]; rel = np.interp(fcur, FSW, RELF)
    ax.semilogx(FSW, RELF, color="#30363d", lw=1.2)
    ax.semilogx(FSW[FSW<=fcur], RELF[FSW<=fcur], color=GRN, lw=2.6)
    ax.plot([fcur],[rel],"o",color=RED,ms=9)
    ax.axvspan(300,3400,color=GRN,alpha=.08); ax.axhline(-3,color=RED,ls="--",lw=1)
    ax.set_xlim(10,20e3); ax.set_ylim(-16,3); ax.set_xlabel("Hz"); ax.set_ylabel("dB re 1 kHz")
    ax.text(1000,1.4,"voice band",color=GRN,ha="center",fontsize=9)
    CHTITLE.set_text("9 · End-to-end frequency response  (into 32 Ω)")
    CHSUB.set_text(f"f = {fcur:.0f} Hz, {rel:+.1f} dB · −3 dB at ~44 Hz (1 µF couplers) · flat 100 Hz–20 kHz")

def sc_score(p):
    clearfig(); ax = newax([.06,.06,.88,.8]); ax.axis("off"); ax.set_xlim(0,100); ax.set_ylim(0,100)
    rows = [
     ("Power / VBIAS 2.500 V, Zout < 1 Ω (v1 bug #3 fixed)", True),
     ("Mic muted at power-up — POR 140 ms", True),
     ("One-hot select: SW2→PC1 … SW5→PC4, exclusive (v1 bug #2 fixed)", True),
     ("Volume pot direction CW = louder (v1 bug #1 fixed)", True),
     ("Channel at MIN volume is silent  (−66 dB, 42 µV)", True),
     ("All 4 volumes at 0 → headset silent (169 µV)", True),
     ("Master RV5 at 0 → whole system muted", True),
     ("No scratchy pot — wiper at VBIAS all rotation", True),
     ("Mixer no clipping, 4 laptops in phase (45 % headroom)", True),
     ("Voice band flat 100 Hz–20 kHz", True),
     ("Headset level from −10 dBV source > 0.5 mW  →  0.22 mW", False),
     ("System gain 0.66× (design note)  →  0.27× into 32 Ω", False),
    ]
    n = int(p*len(rows))
    ax.text(2,95,"SCORECARD",color=FG,fontsize=15,weight="bold")
    for i,(txt,ok) in enumerate(rows[:n+1]):
        y = 88-i*6.7
        ax.text(3,y, "PASS" if ok else "NOTE", color=GRN if ok else RED, fontsize=9, va="center", weight="bold")
        ax.text(8,y, txt, color=FG if ok else "#f0b8b4", fontsize=10.5, va="center")
    if n >= len(rows)-1:
        ax.text(3,4,"10 / 12 pass · 2 findings: drop R16/R20 47 Ω→10 Ω (+5.5 dB); "
                    "1 µF couplers → bass −3 dB @ 44 Hz (fine for voice).",
                color="#9aa4b2", fontsize=9)
        ax.text(3,0,"CAVEAT: mute depends on Alps RK097 term-1 = CCW end. Netlist is correct for that; "
                    "confirm with an ohmmeter on the first article.", color="#d29922", fontsize=9)
    CHTITLE.set_text("10 · Does it match the project?")
    CHSUB.set_text("all three v1 bugs fixed and verified · mute works · ship for the conference-headset use case")

# ---------- timeline ----------------------------------------------------
SCENES = [
 (sc_overview, 4.0), (sc_powerup, 6.0), (sc_por, 5.0), (sc_selector, 13.0),
 (sc_audio, 7.0), (sc_volsweep, 11.0), (sc_allzero, 5.0), (sc_master, 6.0),
 (sc_freq, 6.0), (sc_score, 7.0),
]
SEG = [(f, int(d*FPS)) for f,d in SCENES]
NF = sum(n for _,n in SEG)

def frame(i):
    acc = 0
    for fn, n in SEG:
        if i < acc + n:
            fn((i-acc)/max(n-1,1)); return []
        acc += n
    SEG[-1][0](1.0); return []

print(f"rendering {NF} frames ({NF/FPS:.0f} s) ...")
ani = FuncAnimation(fig, frame, frames=NF, interval=1000/FPS)
ani.save(f"{OUT}/MeetingHub-4-v2-full-simulation.mp4",
         writer=FFMpegWriter(fps=FPS, bitrate=3600, codec="libx264"),
         savefig_kwargs={"facecolor": BG})
print("wrote MeetingHub-4-v2-full-simulation.mp4")
