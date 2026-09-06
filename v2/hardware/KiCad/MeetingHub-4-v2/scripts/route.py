#!/usr/bin/env python3
"""Route MeetingHub-4-v2 (2-layer) with Freerouting 2.2.4, headless.

KiCad 7.0.11 has no CLI DSN/SES, so ExportSpecctraDSN via the pcbnew API, run
freerouting, write /tmp/mh4v2.ses.  Then scripts/ses_import.py + scripts/post.py.
2-layer board: F.Cu / B.Cu both signal + GND pour, no inner planes to patch.
"""
import os, re, shutil, subprocess, sys, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB  = os.path.abspath(os.path.join(HERE, "..", "MeetingHub-4-v2.kicad_pcb"))
DSN  = "/tmp/mh4v2.dsn"
SES  = "/tmp/mh4v2.ses"
JAR  = os.path.abspath(os.path.join(HERE, "..", "freerouting-2.2.4.jar"))

board = pcbnew.LoadBoard(PCB)
if not pcbnew.ExportSpecctraDSN(board, DSN):
    sys.exit("ExportSpecctraDSN failed")
print("DSN exported")

STRATS = [[], ["-is", "random"], ["-us", "global"],
          ["-is", "random", "-us", "global"], ["-mp", "40"]]
best_unrouted, best_ses = 1 << 30, SES + ".best"
for i, extra in enumerate(STRATS):
    out = subprocess.run(["java", "-jar", JAR, "-de", DSN, "-do", SES,
                          "-mp", "20", "-mt", "1"] + extra,
                         capture_output=True, text=True)
    log = out.stdout + out.stderr
    m = re.search(r'final score: [\d.]+(?: \((\d+) unrouted\))?', log)
    unrouted = int(m.group(1)) if (m and m.group(1)) else (0 if m else 999)
    print(f"  try {i} {extra or '(default)'}: rc={out.returncode} unrouted={unrouted}")
    if out.returncode == 0 and unrouted < best_unrouted and os.path.exists(SES):
        best_unrouted = unrouted
        shutil.copy(SES, best_ses)
    if out.returncode == 0 and unrouted == 0:
        break
if os.path.exists(best_ses):
    shutil.copy(best_ses, SES)
print(f"best: {best_unrouted} unrouted -> {SES}")
