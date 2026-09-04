"""
Compact Modified-Nodal-Analysis circuit engine for the MeetingHub-4 v3 review (mic selector).

Purpose-built (not a general SPICE): linear R / C / L, independent V and I
sources (DC / AC / SIN / PWL), VCVS (E), VCCS (G), and a one-pole op-amp macro
with output saturation.  Analyses: .op, .ac (complex sweep), .tran (trapezoidal
with Newton for the op-amp saturation term).

Node "0" / "gnd" is ground.  Everything SI.
"""
import numpy as np

class Circuit:
    def __init__(self):
        self.nodes = {"0": 0}
        self.elems = []          # (kind, args...)
        self.vsrc = []           # names of current-carrying branches (V, E, L)
        self._name = set()

    def n(self, name):
        name = str(name)
        if name in ("0", "gnd", "GND"):
            return 0
        if name not in self.nodes:
            self.nodes[name] = len(self.nodes)
        return self.nodes[name]

    def _uni(self, nm):
        assert nm not in self._name, f"duplicate element {nm}"
        self._name.add(nm)

    # ---- element stamps (stored, realised per-analysis) -------------------
    def R(self, nm, a, b, val):
        self._uni(nm); self.elems.append(("R", nm, self.n(a), self.n(b), float(val)))
    def C(self, nm, a, b, val, ic=0.0):
        self._uni(nm); self.elems.append(("C", nm, self.n(a), self.n(b), float(val), float(ic)))
    def L(self, nm, a, b, val, ic=0.0):
        self._uni(nm); k = len(self.vsrc); self.vsrc.append(nm)
        self.elems.append(("L", nm, self.n(a), self.n(b), float(val), float(ic), k))
    def V(self, nm, a, b, dc=0.0, ac=0.0, sin=None, pwl=None):
        self._uni(nm); k = len(self.vsrc); self.vsrc.append(nm)
        self.elems.append(("V", nm, self.n(a), self.n(b), float(dc), complex(ac), sin, pwl, k))
    def I(self, nm, a, b, dc=0.0, ac=0.0, sin=None, pwl=None):
        self._uni(nm); self.elems.append(("I", nm, self.n(a), self.n(b), float(dc), complex(ac), sin, pwl))
    def E(self, nm, op, on, cp, cn, gain):          # VCVS  v(op,on) = gain*v(cp,cn)
        self._uni(nm); k = len(self.vsrc); self.vsrc.append(nm)
        self.elems.append(("E", nm, self.n(op), self.n(on), self.n(cp), self.n(cn), float(gain), k))
    def G(self, nm, op, on, cp, cn, gm):            # VCCS  i(op->on) = gm*v(cp,cn)
        self._uni(nm); self.elems.append(("G", nm, self.n(op), self.n(on), self.n(cp), self.n(cn), float(gm)))

    def opamp(self, nm, outp, inp, inn, vpos, vneg, A0=1e5, gbw=10e6, rout=50.0):
        """One-pole op-amp: internal node 'nm_x' holds A0-scaled error behind a
        pole at gbw/A0; output VCVS (unity) drives the pin through rout.  Rails
        vpos/vneg clamp the internal node (soft) in .tran."""
        gm = A0 / rout                              # gm*rout = A0 (open-loop DC gain)
        cx = A0 / (rout * 2 * np.pi * gbw)          # pole = 1/(2π rout cx) = gbw/A0
        xn = f"{nm}_x"
        self.G(f"{nm}_gm", xn, "0", inp, inn, gm)   # error current
        self.R(f"{nm}_ro", xn, "0", rout)           # ×gm×rout = A0
        self.C(f"{nm}_cx", xn, "0", cx)
        self.E(f"{nm}_bo", f"{nm}_o", "0", xn, "0", 1.0)
        self.R(f"{nm}_os", f"{nm}_o", outp, 1.0)    # 1Ω output series (kept tiny)
        self.elems.append(("CLAMP", nm, self.n(xn), self.n(vpos), self.n(vneg)))

    # ---- helpers --------------------------------------------------------
    GMIN = 1e-9

    @property
    def N(self):  return len(self.nodes) - 1
    @property
    def M(self):  return len(self.vsrc)

    def _src_val(self, e, t=None, ac=False):
        dc, acmag, sinspec, pwl = e[4], e[5], e[6], e[7]
        if ac:   return acmag
        if t is None: return dc
        if sinspec is not None:
            off, amp, freq = sinspec[:3]
            td = sinspec[3] if len(sinspec) > 3 else 0.0
            return off + (amp*np.sin(2*np.pi*freq*(t-td)) if t >= td else 0.0)
        if pwl is not None:
            ts = [p[0] for p in pwl]; vs = [p[1] for p in pwl]
            return float(np.interp(t, ts, vs))
        return dc

    # ---- DC operating point (linear; op-amp = linear one-pole DC) --------
    def op(self):
        N, M = self.N, self.M
        A = np.zeros((N+M, N+M)); z = np.zeros(N+M)
        def gstamp(i, j, g):
            if i: A[i-1, i-1] += g
            if j: A[j-1, j-1] += g
            if i and j: A[i-1, j-1] -= g; A[j-1, i-1] -= g
        for e in self.elems:
            k = e[0]
            if k == "R": gstamp(e[2], e[3], 1.0/e[4])
            elif k == "C": pass
            elif k == "G":
                _, nm, op_, on, cp, cn, gm = e
                for (r, s) in ((op_, cp), (op_, cn, ), (on, cp), (on, cn)):
                    pass
                if op_ and cp: A[op_-1, cp-1] += gm
                if op_ and cn: A[op_-1, cn-1] -= gm
                if on and cp: A[on-1, cp-1] -= gm
                if on and cn: A[on-1, cn-1] += gm
            elif k in ("V", "L", "E"):
                pass
        # branch equations
        for e in self.elems:
            k = e[0]
            if k == "V":
                _, nm, a, b, dc, acm, sinspec, pwl, br = e
                row = N + br
                if a: A[row, a-1] += 1; A[a-1, row] += 1
                if b: A[row, b-1] -= 1; A[b-1, row] -= 1
                z[row] = self._src_val(e, t=None)
            elif k == "L":
                _, nm, a, b, val, ic, br = e
                row = N + br
                if a: A[row, a-1] += 1; A[a-1, row] += 1
                if b: A[row, b-1] -= 1; A[b-1, row] -= 1
                z[row] = 0.0
            elif k == "E":
                _, nm, op_, on, cp, cn, g, br = e
                row = N + br
                if op_: A[row, op_-1] += 1; A[op_-1, row] += 1
                if on: A[row, on-1] -= 1; A[on-1, row] -= 1
                if cp: A[row, cp-1] -= g
                if cn: A[row, cn-1] += g
            elif k == "I":
                _, nm, a, b, dc, acm, sinspec, pwl = e
                val = self._src_val(e, t=None)
                if a: z[a-1] -= val
                if b: z[b-1] += val
        for i in range(N): A[i, i] += self.GMIN
        x = np.linalg.solve(A, z)
        return self._pack(x)

    def _pack(self, x):
        out = {"0": 0.0}
        for name, idx in self.nodes.items():
            if idx == 0: continue
            out[name] = x[idx-1]
        for j, nm in enumerate(self.vsrc):
            out[f"i({nm})"] = x[self.N + j]
        return out

    # ---- AC sweep ------------------------------------------------------
    def ac(self, freqs, ref=None):
        freqs = np.asarray(freqs, float)
        N, M = self.N, self.M
        res = {name: np.zeros(len(freqs), complex) for name in self.nodes if name != "0"}
        for fi, f in enumerate(freqs):
            s = 2j*np.pi*f
            A = np.zeros((N+M, N+M), complex); z = np.zeros(N+M, complex)
            def gstamp(i, j, g):
                if i: A[i-1, i-1] += g
                if j: A[j-1, j-1] += g
                if i and j: A[i-1, j-1] -= g; A[j-1, i-1] -= g
            for e in self.elems:
                k = e[0]
                if k == "R": gstamp(e[2], e[3], 1.0/e[4])
                elif k == "C": gstamp(e[2], e[3], s*e[4])
                elif k == "G":
                    _, nm, op_, on, cp, cn, gm = e
                    if op_ and cp: A[op_-1, cp-1] += gm
                    if op_ and cn: A[op_-1, cn-1] -= gm
                    if on and cp: A[on-1, cp-1] -= gm
                    if on and cn: A[on-1, cn-1] += gm
            for e in self.elems:
                k = e[0]
                if k == "V":
                    _, nm, a, b, dc, acm, sinspec, pwl, br = e
                    row = N + br
                    if a: A[row, a-1] += 1; A[a-1, row] += 1
                    if b: A[row, b-1] -= 1; A[b-1, row] -= 1
                    z[row] = acm
                elif k == "L":
                    _, nm, a, b, val, ic, br = e
                    row = N + br
                    if a: A[row, a-1] += 1; A[a-1, row] += 1
                    if b: A[row, b-1] -= 1; A[b-1, row] -= 1
                    A[row, row] -= s*val
                elif k == "E":
                    _, nm, op_, on, cp, cn, g, br = e
                    row = N + br
                    if op_: A[row, op_-1] += 1; A[op_-1, row] += 1
                    if on: A[row, on-1] -= 1; A[on-1, row] -= 1
                    if cp: A[row, cp-1] -= g
                    if cn: A[row, cn-1] += g
                elif k == "I":
                    _, nm, a, b, dc, acm, sinspec, pwl = e
                    if a: z[a-1] -= acm
                    if b: z[b-1] += acm
            for i in range(N): A[i, i] += self.GMIN
            x = np.linalg.solve(A, z)
            for name, idx in self.nodes.items():
                if idx == 0: continue
                res[name][fi] = x[idx-1]
        if ref is not None:
            r = res[ref]
            res = {k: v/r for k, v in res.items()}
        return freqs, res

    # ---- transient (backward Euler, fully linear) --------------------
    def tran(self, tstop, dt, uic=None):
        """uic: optional dict {node: V0} initial condition; default = .op()."""
        N, M = self.N, self.M
        ts = np.arange(0.0, tstop+dt/2, dt)
        X = np.zeros((len(ts), N+M))
        if uic is None:
            ic = self.op()
            x0 = np.zeros(N+M)
            for name, idx in self.nodes.items():
                if idx: x0[idx-1] = ic[name]
            for j, nm in enumerate(self.vsrc):
                x0[N+j] = ic[f"i({nm})"]
        else:
            x0 = np.zeros(N+M)
            for name, v in uic.items():
                if name in self.nodes and self.nodes[name]:
                    x0[self.nodes[name]-1] = v
        X[0] = x0
        for ti, t in enumerate(ts):
            if ti == 0: continue
            xp = X[ti-1]
            A = np.zeros((N+M, N+M)); z = np.zeros(N+M)
            def gstamp(i, j, g):
                if i: A[i-1, i-1] += g
                if j: A[j-1, j-1] += g
                if i and j: A[i-1, j-1] -= g; A[j-1, i-1] -= g
            for e in self.elems:
                k = e[0]
                if k == "R": gstamp(e[2], e[3], 1.0/e[4])
                elif k == "C":
                    _, nm, a, b, val, icc = e
                    g = val/dt
                    gstamp(a, b, g)
                    jeq = g*((xp[a-1] if a else 0.0) - (xp[b-1] if b else 0.0))
                    if a: z[a-1] += jeq
                    if b: z[b-1] -= jeq
                elif k == "G":
                    _, nm, op_, on, cp, cn, gm = e
                    if op_ and cp: A[op_-1, cp-1] += gm
                    if op_ and cn: A[op_-1, cn-1] -= gm
                    if on and cp: A[on-1, cp-1] -= gm
                    if on and cn: A[on-1, cn-1] += gm
            for e in self.elems:
                k = e[0]
                if k == "V":
                    _, nm, a, b, dc, acm, sinspec, pwl, br = e
                    row = N + br
                    if a: A[row, a-1] += 1; A[a-1, row] += 1
                    if b: A[row, b-1] -= 1; A[b-1, row] -= 1
                    z[row] = self._src_val(e, t=t)
                elif k == "L":
                    _, nm, a, b, val, icc, br = e
                    row = N + br; g = val/dt
                    if a: A[row, a-1] += 1; A[a-1, row] += 1
                    if b: A[row, b-1] -= 1; A[b-1, row] -= 1
                    A[row, row] -= g
                    z[row] = -g*xp[row]
                elif k == "E":
                    _, nm, op_, on, cp, cn, gg, br = e
                    row = N + br
                    if op_: A[row, op_-1] += 1; A[op_-1, row] += 1
                    if on: A[row, on-1] -= 1; A[on-1, row] -= 1
                    if cp: A[row, cp-1] -= gg
                    if cn: A[row, cn-1] += gg
                elif k == "I":
                    _, nm, a, b, dc, acm, sinspec, pwl = e
                    val = self._src_val(e, t=t)
                    if a: z[a-1] -= val
                    if b: z[b-1] += val
            for i in range(N): A[i, i] += self.GMIN
            X[ti] = np.linalg.solve(A, z)
        out = {"t": ts}
        for name, idx in self.nodes.items():
            if idx == 0: continue
            out[name] = X[:, idx-1]
        for j, nm in enumerate(self.vsrc):
            out[f"i({nm})"] = X[:, N+j]
        return out


def db(x):  return 20*np.log10(np.abs(x))
