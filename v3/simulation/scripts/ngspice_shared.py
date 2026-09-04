#!/usr/bin/env python3
"""Minimal ctypes binding to libngspice (the shared-library API).

The box has no `ngspice` binary and PySpice 1.5 rejects ngspice 42, so this
drives /usr/lib/.../libngspice.so.0 directly.  Enough of the API to:
  * load a netlist string
  * run an analysis
  * pull result vectors back as numpy arrays
  * capture the console text (so `.meas` / `.print` lines are available)

API ref: https://ngspice.sourceforge.io/shared.html
"""
import ctypes as C
import glob
import os
import numpy as np

def _find_lib():
    for p in ("/usr/lib/x86_64-linux-gnu/libngspice.so.0",
              "/usr/lib/x86_64-linux-gnu/libngspice.so",
              "/usr/lib/libngspice.so.0"):
        if os.path.exists(p):
            return p
    hits = glob.glob("/usr/lib/**/libngspice.so*", recursive=True)
    if hits:
        return sorted(hits)[-1]
    raise RuntimeError("libngspice not found")

_LIB = _find_lib()


class _Complex(C.Structure):
    _fields_ = [("cx_real", C.c_double), ("cx_imag", C.c_double)]


class _VecInfo(C.Structure):
    _fields_ = [("v_name", C.c_char_p), ("v_type", C.c_int),
                ("v_flags", C.c_short),
                ("v_realdata", C.POINTER(C.c_double)),
                ("v_compdata", C.POINTER(_Complex)), ("v_length", C.c_int)]


_VF_REAL = 1 << 0     # ngspice dvec.h: VF_REAL
_VF_COMPLEX = 1 << 1  # VF_COMPLEX


SendChar    = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
SendStat    = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
ControlExit = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)
SendData    = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.c_int, C.c_void_p)
SendInit    = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.c_void_p)
BGRunning   = C.CFUNCTYPE(C.c_int, C.c_bool, C.c_int, C.c_void_p)


class NgSpice:
    def __init__(self):
        self.lib = C.CDLL(_LIB)
        self.log = []
        self._exit = None

        def _sc(msg, _id, _u):
            try:
                self.log.append(msg.decode("latin-1", "replace"))
            except Exception:
                pass
            return 0

        def _ss(msg, _id, _u):
            return 0

        def _ce(status, unload, quit_, _id, _u):
            self._exit = status
            return 0

        def _sd(d, n, _id, _u):
            return 0

        def _si(d, _id, _u):
            return 0

        def _bg(running, _id, _u):
            return 0

        self._cb = (SendChar(_sc), SendStat(_ss), ControlExit(_ce),
                    SendData(_sd), SendInit(_si), BGRunning(_bg))
        self.lib.ngSpice_Init.restype = C.c_int
        self.lib.ngSpice_Init(self._cb[0], self._cb[1], self._cb[2],
                              self._cb[3], self._cb[4], self._cb[5], None)
        self.lib.ngGet_Vec_Info.restype = C.POINTER(_VecInfo)
        self.lib.ngSpice_CurPlot.restype = C.c_char_p
        self.lib.ngSpice_AllVecs.restype = C.POINTER(C.c_char_p)
        self.lib.ngSpice_AllPlots.restype = C.POINTER(C.c_char_p)

    def cmd(self, s):
        self.log.append("ngspice-> " + s)
        return self.lib.ngSpice_Command(s.encode())

    def source(self, netlist_text):
        lines = [ln for ln in netlist_text.splitlines()]
        arr = (C.c_char_p * (len(lines) + 1))()
        for i, ln in enumerate(lines):
            arr[i] = ln.encode()
        arr[len(lines)] = None
        self.lib.ngSpice_Circ.restype = C.c_int
        return self.lib.ngSpice_Circ(arr)

    def run(self):
        return self.cmd("run")

    def cur_plot(self):
        p = self.lib.ngSpice_CurPlot()
        return p.decode() if p else ""

    def plots(self):
        pp = self.lib.ngSpice_AllPlots()
        out = []
        i = 0
        while pp[i]:
            out.append(pp[i].decode())
            i += 1
        return out

    def vec_names(self, plot=None):
        pp = self.lib.ngSpice_AllVecs((plot or self.cur_plot()).encode())
        out = []
        i = 0
        while pp[i]:
            out.append(pp[i].decode())
            i += 1
        return out

    def vec(self, name, plot=None):
        key = name if plot is None else f"{plot}.{name}"
        vi = self.lib.ngGet_Vec_Info(key.encode())
        if not vi or not vi[0].v_length:
            return None
        n = vi[0].v_length
        if vi[0].v_compdata and not (vi[0].v_flags & _VF_REAL):
            raw = np.ctypeslib.as_array(
                C.cast(vi[0].v_compdata, C.POINTER(C.c_double)), shape=(2 * n,))
            return (raw[0::2] + 1j * raw[1::2]).copy()
        if vi[0].v_realdata:
            return np.ctypeslib.as_array(vi[0].v_realdata, shape=(n,)).copy()
        return None

    def table(self, plot=None):
        """All real vectors of a plot as {name: ndarray}."""
        plot = plot or self.cur_plot()
        d = {}
        for nm in self.vec_names(plot):
            v = self.vec(nm, plot)
            if v is not None:
                d[nm] = v
        return d

    def meas_lines(self):
        """Console lines that look like `.meas` results: 'name = value'."""
        out = {}
        for ln in self.log:
            s = ln.strip()
            if "=" in s and not s.startswith("ngspice->"):
                left, _, right = s.partition("=")
                left = left.strip().lower()
                try:
                    out[left] = float(right.strip().split()[0])
                except (ValueError, IndexError):
                    pass
        return out

    def reset(self):
        self.cmd("reset")
        self.cmd("destroy all")


_INST = None
def instance():
    global _INST
    if _INST is None:
        _INST = NgSpice()
    return _INST


if __name__ == "__main__":
    ng = instance()
    ng.source("""rc test
V1 in 0 5
R1 in out 1k
C1 out 0 1u
.tran 2u 5m uic
.end""")
    ng.run()
    t = ng.table()
    print("vectors:", list(t))
    print("v(out) @5ms =", round(float(t["out"][-1]), 4), " (expect ~4.97)")
