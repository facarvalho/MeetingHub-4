# SCH-005 - Audio Mixer Design

Version: 0.1
Status: Draft


# 1. Objective

Define the circuit responsible for mixing the stereo audio of the four laptops.

The system shall allow:

- listening to four sources simultaneously;
- controlling the volume of each source;
- maintaining separation between left and right channels;
- providing a signal suitable for the headphone amplifier.


# 2. Architecture

Each laptop has two channels:

- Audio Left
- Audio Right


Flow:

```

Laptop 1 L/R
|
v
Volume 1

Laptop 2 L/R
|
v
Volume 2

Laptop 3 L/R
|
v
Volume 3

Laptop 4 L/R
|
v
Volume 4

```
    |
    v
```

Active Stereo Mixer

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


# 3. Mixer Topology

An active mixer using operational amplifiers will be used.

Characteristics:

- low noise;
- high input impedance;
- low interference between sources.


# 4. Volume Control

Each laptop will have:

- stereo potentiometer;
- independent volume adjustment.


Quantity:

- 4 individual controls.


# 5. Stereo Channel

The design shall maintain:

Left channel:

```

NB1_L
NB2_L
NB3_L
NB4_L

```
  |
  v
```

Mixer_L

```


Right channel:

```

NB1_R
NB2_R
NB3_R
NB4_R

```
  |
  v
```

Mixer_R

```


# 6. Requirements

The mixer shall:

- prevent one laptop output from loading another;
- maintain low distortion;
- preserve the audio frequency range;
- work with laptop output signals.


# 7. Candidate Components

Operational amplifier:

- NE5532
- OPA1652
- audio equivalent


# 8. Notes

The final circuit will be validated considering:

- noise;
- gain;
- maximum output level;
- compatibility with the headphone amplifier.
```
