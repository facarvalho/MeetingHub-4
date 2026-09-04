#!/usr/bin/env python3
"""Export the v3 fab package: gerbers + drill + zip, schematic PDF, netlist copy,
then the BOMs / CPL."""
import subprocess, os, zipfile, glob, shutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB  = f"{HERE}/MeetingHub-4-v3.kicad_pcb"
SCH  = f"{HERE}/MeetingHub-4-v3.kicad_sch"
PRJ  = "/home/fac/MeetingHub-4/v3"
GERB = f"{PRJ}/hardware/Gerbers"
os.environ.setdefault("KICAD7_FOOTPRINT_DIR", "/usr/share/kicad/footprints")

def run(*a): subprocess.run(list(a), check=True)

run("kicad-cli", "pcb", "export", "gerbers", "--output", GERB + "/",
    "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,"
                "F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
    "--no-protel-ext", PCB)
run("kicad-cli", "pcb", "export", "drill", "--output", GERB + "/",
    "--format", "excellon", "--excellon-oval-format", "route", PCB)

zpath = f"{GERB}/MeetingHub-4-v3-Gerbers.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(glob.glob(f"{GERB}/*.gbr") + glob.glob(f"{GERB}/*.drl")
                    + glob.glob(f"{GERB}/*.gbrjob")):
        z.write(f, os.path.basename(f))
print("zip:", zpath)

run("kicad-cli", "sch", "export", "pdf", "--output",
    f"{PRJ}/hardware/Schematics/MeetingHub-4-v3-Schematic.pdf", SCH)
if os.path.exists("/tmp/v3.net"):
    shutil.copy("/tmp/v3.net", f"{PRJ}/hardware/PCB/MeetingHub-4-v3.net")
run("python3", f"{HERE}/scripts/bomcpl.py")
print("fab package done")
