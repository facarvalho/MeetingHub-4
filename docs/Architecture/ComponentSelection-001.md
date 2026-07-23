# Phase 3 — Component Selection (Preliminary BOM)

Before drawing the schematic, we need to choose real components. The rule will be:

* components available on the market;
* good durability;
* reasonable cost;
* easy replacement;
* simple assembly.

We will create:

```text
hardware/BOM/BOM-001.xlsx
```

and also a document:

```text
docs/Architecture/ComponentSelection-001.md
```

---

## Main Components — Initial Proposal

### 1) Panel-mount TRRS Connectors

Requirement:

* 3.5 mm female P2
* metallic
* panel mounting
* CTIA standard

Quantity:

* 5 units

  * 4 laptops
  * 1 headset

Criteria:

* plated contact
* mechanical fixation via nut
* high service life

---

### 2) Volume Potentiometers

Quantity:

* 5 units

Functions:

* Laptop 1 Volume
* Laptop 2 Volume
* Laptop 3 Volume
* Laptop 4 Volume
* Master Volume

Type:

* stereo
* 10 kΩ logarithmic
* metal shaft

---

### 3) Active Mixer

Initial proposal:

**NE5532**

Quantity:

* 2 units

Use:

* left channel
* right channel

Reasons:

* excellent for audio;
* inexpensive;
* well known;
* easy to find.

---

### 4) Headphone Amplifier

Options under consideration:

**NJM4556A**

or

**TPA6120A2**

Criteria:

* low distortion;
* capability for 16–64 Ω headsets;
* stability.

For V1 I would lean toward the **NJM4556A**, for being simple and robust.

---

### 5) Microphone Selection

Main requirement:

The laptop must continue to "see" a headset.

Proposal:

Signal relay.

Candidate model:

* Omron G6K
* Panasonic TQ2

Quantity:

* 1 selection set

---

### 6) MUTE

Button:

* industrial;
* normally closed (NC).

Why?

If the button breaks, the safe default is to keep working.

---

### 7) Power Supply

Input:

USB-C 5 V

Blocks:

```text
USB-C
  |
Protection
  |
Filter
  |
5V Analog
```

---

# Next Document

Now we will create:

```
docs/Architecture/ComponentSelection-001.md
```

In it we will record:

* chosen component;
* alternatives;
* reason for the choice;
* datasheet;
* supplier.

---

After that comes the most important step:

## Electrical Schematic Rev A

We will draw the blocks:

1. TRRS Input.
2. L/R/MIC Separation.
3. Volume control.
4. Stereo mixer.
5. Headphone amplifier.
6. Microphone circuit.
7. Power supply.
