# SCH-002 - Schematic Design Plan

Version: 0.1
Status: Draft

---

# 1. Objective

Define the organization of the electrical schematic before implementation in KiCad.

---

# 2. Schematic sheets

The project will be divided into blocks:

## Sheet 1 - Power Supply

Responsible for:

- USB-C 5V input;
- protection;
- filtering;
- voltage distribution.


## Sheet 2 - TRRS Inputs

Responsible for:

- laptop connectors;
- signal separation:
  - Audio Left
  - Audio Right
  - Ground
  - Microphone


## Sheet 3 - Audio Mixer

Responsible for:

- individual volumes;
- stereo summing;
- pre-amplification.


## Sheet 4 - Headphone Amplifier

Responsible for:

- final amplification;
- headset output.


## Sheet 5 - Microphone Switching

Responsible for:

- laptop 1-4 selection;
- mute;
- signal relays.


# 3. Design rules

- keep the microphone line transparent;
- separate analog audio from power supply;
- minimize ground loops;
- use high-availability components.
