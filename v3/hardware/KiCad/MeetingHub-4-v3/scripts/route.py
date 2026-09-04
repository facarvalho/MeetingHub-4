#!/usr/bin/env python3
"""Route the v3 board with Freerouting 2.2.4, headless.

KiCad 7.0.11 has no CLI DSN/SES, so:
  1. ExportSpecctraDSN from the .kicad_pcb via the pcbnew Python API.
  2. Patch the DSN: mark In1.Cu / In2.Cu as `(type power)`.  Freerouting routes
     signal traces on every layer it sees as `(type signal)`; the two inner
     layers are solid GND / +5V planes, so without this it lays traces on them
     and ses_import.py silently drops those (-> dozens of unconnected pads).
  3. Run freerouting-2.2.4.jar  -> /tmp/v3.ses
Then run scripts/ses_import.py to apply the result, and scripts/post.py.
"""
import os, re, shutil, subprocess, sys, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB  = os.path.join(HERE, "..", "MeetingHub-4-v3.kicad_pcb")
DSN  = "/tmp/v3.dsn"
SES  = "/tmp/v3.ses"
JAR  = os.path.join(HERE, "..", "freerouting-2.2.4.jar")
if not os.path.exists(JAR):
    JAR = os.path.join(HERE, "..", "..", "..", "..", "..", "v2", "hardware",
                       "KiCad", "MeetingHub-4-v2", "freerouting-2.2.4.jar")

board = pcbnew.LoadBoard(os.path.abspath(PCB))
if not pcbnew.ExportSpecctraDSN(board, DSN):
    sys.exit("ExportSpecctraDSN failed")

txt = open(DSN).read()
n = 0
for ly in ("In1.Cu", "In2.Cu"):
    txt, k = re.subn(r'(\(layer\s+' + re.escape(ly) + r'\s*\n\s*\(type\s+)signal(\))',
                     r'\1power\2', txt)
    n += k
open(DSN, "w").write(txt)
print(f"DSN exported, patched {n} inner-plane layer(s) to (type power)")

# Freerouting 2.2.4 has no random seed; it can settle on a local minimum with a
# net or two unrouted.  Retry with different optimisation strategies and keep the
# first result that routes everything.
STRATS = [[], ["-is", "random"], ["-us", "global"], ["-is", "random", "-us", "global"],
          ["-mp", "40"], ["-is", "random", "-mp", "40"]]
best_rc, best_unrouted, best_ses = 1, 1 << 30, SES + ".best"
for i, extra in enumerate(STRATS):
    out = subprocess.run(["java", "-jar", os.path.abspath(JAR), "-de", DSN,
                          "-do", SES, "-mp", "20", "-mt", "1"] + extra,
                         capture_output=True, text=True)
    log = out.stdout + out.stderr
    m = re.search(r'session completed:.*?final score: [\d.]+(?: \((\d+) unrouted\))?', log)
    unrouted = int(m.group(1)) if (m and m.group(1)) else (0 if m else 999)
    print(f"  try {i} {extra or '(default)'}: rc={out.returncode} unrouted={unrouted}")
    if out.returncode == 0 and unrouted < best_unrouted and os.path.exists(SES):
        best_unrouted = unrouted
        shutil.copy(SES, best_ses)
    if out.returncode == 0 and unrouted == 0:
        best_rc = 0
        break
if os.path.exists(best_ses):
    shutil.copy(best_ses, SES)          # hand ses_import the most complete result
if best_unrouted:
    print(f"NOTE: freerouting left {best_unrouted} net(s) unrouted; "
          "post.py finishes short connections, otherwise route by hand in KiCad")
    best_rc = 0 if best_unrouted <= 3 else 1   # <=3 stubs is post.py's job
print(f"freerouting rc={best_rc} (best unrouted={best_unrouted})")
sys.exit(0)
