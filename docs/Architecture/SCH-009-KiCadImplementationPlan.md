# Next Step: Create the KiCad Project

Enter the directory:

```bash
cd ~/MeetingHub-4/hardware/KiCad
```

Create the folder:

```bash
mkdir MeetingHub-4
cd MeetingHub-4
```

Open KiCad and create the project:

Name:

```text
MeetingHub-4
```

Location:

```text
~/MeetingHub-4/hardware/KiCad/MeetingHub-4/
```

---

After it's created, your tree should look similar to:

```text
hardware
└── KiCad
    └── MeetingHub-4
        ├── MeetingHub-4.kicad_pro
        ├── MeetingHub-4.kicad_sch
        └── MeetingHub-4.kicad_pcb
```

---

# First Schematic Sheet

Let's start with the power supply.

In KiCad we will create:

```
Sheet: Power Supply
```

Initial components:

| Reference | Component         | Function    |
| --------- | ------------------ | ----------- |
| J1        | USB-C               | 5V input    |
| F1        | Resettable fuse     | Protection  |
| D1        | TVS/Protection       | Surge       |
| C1        | 100nF               | Filter      |
| C2        | 10uF                 | Reserve     |
| J2        | Test Point           | Measurement |

Buses:

```
+5V_USB
    |
    |
Protection
    |
    |
+5V_AUDIO
    |
    |
Circuits
```

---

# Before Placing Components

An important decision:

In your case, I **would not use USB-C with PD negotiation**.

We will use USB-C only as a power input:

* VBUS = 5V
* GND = return

Reason:

* simpler;
* cheaper;
* fewer points of failure.

---

# Next Step in KiCad

When you open the schematic:

1. Create a hierarchical sheet called:

```
POWER
```

2. Place the first symbol:

```
USB_C_Receptacle_USB2.0_16P
```

3. Then we will do the protection.

---

When you create the KiCad project, just send me the result of:

```bash
tree hardware/KiCad
```

or a screenshot of KiCad.

Then we'll proceed component by component. Now we begin the real construction of the MeetingHub-4. 🔧
