# DR-002 - Electrical Architecture Review

Version: 0.1
Status: Review


# 1. Objective

Review the electrical architecture defined before starting development of the schematic in KiCad.


# 2. Scope Reviewed

The following were evaluated:

- TRRS CTIA interface;
- audio path;
- stereo mixer;
- headphone amplifier;
- microphone selection;
- power supply;
- noise control.


# 3. Approved Decisions


## Interface

Approved:

- TRRS CTIA;
- metal panel connectors;
- native compatibility with laptops.


## Audio

Approved:

- four independent inputs;
- active stereo mixer;
- individual volume control;
- master volume.


## Microphone

Approved:

- relay-based switching;
- absence of active electronics on the MIC line;
- selection of one laptop at a time.


## Power supply

Approved:

- USB-C 5V;
- filtering;
- protection;
- separation of audio and power supply.


## Noise

Approved:

- star grounding;
- attention to PCB layout;
- tests with different chargers.


# 4. Points of Attention

During prototype development, the following must be evaluated:

- noise between laptops;
- compatibility with different audio codecs;
- headset detection behavior;
- quality of microphone switching.


# 5. Status

Architecture approved for schematic development.

