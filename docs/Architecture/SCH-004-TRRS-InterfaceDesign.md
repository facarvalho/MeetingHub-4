# SCH-004 - TRRS Interface Design

Version: 0.1
Status: Draft


# 1. Objective

Define the electrical interface between the laptops and the MeetingHub-4 using standard CTIA TRRS connectors.


# 2. Standard Used

Interface:

- TRRS 3.5 mm
- CTIA / AHJ


Pinout:

| Contact | Function |
|---|---|
| Tip | Audio Left |
| Ring 1 | Audio Right |
| Ring 2 | Ground |
| Sleeve | Microphone |


# 3. Inputs

Quantity:

4 independent inputs.

Identification:

- J1 - Laptop 1
- J2 - Laptop 2
- J3 - Laptop 3
- J4 - Laptop 4


# 4. Transparency Requirement

The laptop shall interpret the connection as a TRRS headset connected directly.

The microphone line shall:

- maintain the polarization supplied by the laptop;
- have no amplification;
- have no conversion;
- not alter the perceived impedance.


# 5. Audio Path

Each input will be split:

```

TRRS

L  ---------> Volume Control L
R  ---------> Volume Control R
GND --------> Common reference
MIC --------> Microphone selector

```


# 6. Microphone Path

```

Headset MIC

```
  |
```

MUTE Circuit

```
  |
```

Laptop Selection

```
  |
```

MIC of selected laptop

```


# 7. Protection

The following will be evaluated:

- ESD protection;
- EMI filtering;
- discharge protection on the connectors.
