# SCH-006 - Headphone Amplifier Design

Version: 0.1
Status: Draft


# 1. Objective

Define the stage responsible for providing sufficient power to the TRRS headset connected to the equipment.

The amplifier must receive the signal from the stereo mixer and provide adequate output for low- and medium-impedance headphones.


# 2. Architecture

Flow:

```

Stereo Mixer

```
  |
  v
```

Master Volume

```
  |
  v
```

Headphone Amplifier

```
  |
  v
```

TRRS Headset

```


# 3. Requirements

The amplifier must:

- operate with a 5V power supply;
- have low noise;
- support professional-use headsets;
- avoid distortion at high volume;
- have short-circuit protection on the output.


# 4. Compatibility

Expected range:

- 16 ohms;
- 32 ohms;
- 64 ohms.


# 5. Candidate Components

Initial options:

## NJM4556A

Characteristics:

- developed for headphone amplification;
- high current capability;
- simple;
- reliable.


## TPA6132A2

Characteristics:

- low voltage;
- low power consumption;
- dedicated headphone output.


The final selection will be made after analysis of:

- availability;
- cost;
- audio quality.


# 6. Output

The output must maintain the standard:

TRRS CTIA:

- Left
- Right
- Ground
- Microphone


The amplifier will be responsible only for the channels:

- Left
- Right


# 7. Protections

Planned:

- output resistor;
- decoupling;
- short-circuit protection;
- power supply filtering.


# 8. Notes

The microphone line remains independent.

The headphone amplifier must not interfere with headset detection by the laptops.
```
