# SCH-008 - Grounding and Noise Control

Version: 0.1
Status: Draft


# 1. Objective

Define the grounding, power supply, and noise control strategy of the MeetingHub-4.

The equipment has multiple analog audio sources connected simultaneously, so interference control is a critical requirement.


# 2. Potential Noise Sources

Possible sources:

- four laptops connected simultaneously;
- different power supply chargers;
- ground loops;
- USB power supply;
- external digital interference.


# 3. Grounding Strategy

Star grounding will be used.

Architecture:

```

TRRS Inputs

```
  |
```

GND_AUDIO

```
  |
```

Star Point

```
  |
```

Power Supply

```

Objectives:

- avoid currents circulating through the audio ground;
- reduce background noise;
- improve stability.


# 4. Domain Separation

The design must separate:

## Analog Audio

- TRRS inputs;
- mixer;
- headphone amplifier.


## Power Supply

- USB-C;
- filters;
- protection.


The union will be made at a controlled point.


# 5. PCB Layout

Requirements:

- keep audio traces away from the power supply;
- avoid parallel routing between sensitive signals and power supply traces;
- use a ground plane where applicable;
- position connectors near the board edges.


# 6. Decoupling

Each integrated circuit must have:

- a ceramic capacitor near the power supply pins;
- reserve capacitors on the main power supply.


# 7. Laptop Considerations

The design must be tested with:

- laptop running on battery;
- laptop connected to the charger;
- different computer brands.


# 8. Tests

Validate:

- noise with no signal;
- noise with four laptops connected;
- microphone switching;
- operation with different chargers.


# 9. Approval Criteria

The equipment must operate with no perceptible noise under normal use.
```

