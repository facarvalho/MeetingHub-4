# SCH-001 - Electrical Block Diagram

Version: 0.1  
Status: Draft

---

# 1. Objective

This document describes the functional block diagram of the MeetingHub-4 hardware.

The objective is to define the electrical architecture before developing the detailed schematic.

---

# 2. Overview

MeetingHub-4 is an analog device that allows connecting four laptops simultaneously using TRRS CTIA headset interfaces.

Main functions:

- receive audio from four laptops;
- mix the audio signals in stereo;
- provide monitoring on a single headset;
- select which laptop will receive the microphone signal;
- maintain native compatibility with the laptops' headset detection.

---

# 3. General Diagram

```text
                 AUDIO

+------------+
| Laptop 1   |
+------------+
      |
      |
+------------+
| Laptop 2   |
+------------+
      |
      |
+------------+
| Laptop 3   |
+------------+
      |
      |
+------------+
| Laptop 4   |
+------------+
      |
      |
      v

+---------------------------+
| TRRS CTIA Inputs          |
| L / R / MIC Separation    |
+---------------------------+

      |
      |
      v

+---------------------------+
| Individual Volume Control |
| VOL1 VOL2 VOL3 VOL4       |
+---------------------------+

      |
      |
      v

+---------------------------+
| Active Stereo Mixer       |
| L Channel + R Channel     |
+---------------------------+

      |
      |
      v

+---------------------------+
| Master Volume             |
+---------------------------+

      |
      |
      v

+---------------------------+
| Headphone Amplifier       |
+---------------------------+

      |
      |
      v

+---------------------------+
| Headset TRRS CTIA         |
+---------------------------+
````

---

# 4. Microphone Path

The microphone path shall remain transparent to the laptop.

No active processing will be used on the microphone line.

```text
+----------------+
| Headset MIC    |
+----------------+
        |
        |
        v

+----------------+
| MUTE           |
+----------------+
        |
        |
        v

+----------------+
| MIC Selection  |
| Laptop 1-4     |
+----------------+
        |
        |
        v

+----------------+
| Selected       |
| Laptop         |
+----------------+
```

---

# 5. Microphone Selection

Microphone selection will be performed via signal switching.

Requirements:

* low contact resistance;
* minimal interference;
* preservation of the microphone bias voltage;
* reliable operation under heavy use.

Initial solution:

* high-durability signal relays.

---

# 6. Power Supply

External source:

```text
USB-C 5V

     |
     v

+----------------+
| Protection     |
+----------------+

     |
     v

+----------------+
| Filtering      |
+----------------+

     |
     v

+----------------+
| Audio Circuits |
| Power Supply   |
+----------------+
```

---

# 7. Grounding

The design will use a star grounding strategy.

Objectives:

* minimize noise;
* reduce ground loops;
* improve interference immunity.

Structure:

```text
Audio Inputs
      |
      |
      v
GND_AUDIO

      |
      |
Star point

      |
      |
Power Supply
```

---

# 8. Subsystems

## 8.1 TRRS Inputs

Quantity:

* 4 laptop inputs;
* 1 headset output.

Standard:

* CTIA;
* 3.5 mm;
* TRRS.

---

## 8.2 Audio Mixer

Characteristics:

* stereo;
* active;
* low noise;
* individual control per input.

---

## 8.3 Headphone Amplifier

Responsible for:

* supplying adequate current to the headset;
* maintaining audio quality;
* preventing overload of the laptops' outputs.

---

## 8.4 Microphone

Characteristics:

* direct connection to the selected laptop;
* no digital conversion;
* no processing;
* compatibility with native headset detection.
