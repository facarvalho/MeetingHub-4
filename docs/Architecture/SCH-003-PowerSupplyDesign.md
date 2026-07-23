# SCH-003 - Power Supply Design

Version: 0.1
Status: Draft


# 1. Objective

Define the architecture of the MeetingHub-4 power supply.


# 2. Input

Source:

USB-C

Voltage:

5V DC


# 3. Requirements

The power supply shall:

- have overcurrent protection;
- have noise filtering;
- separate digital and analog power supply;
- minimize audio interference.


# 4. Architecture

```

USB-C 5V

```
|
v
```

Input protection

```
|
v
```

EMI Filter

```
|
v
```

+5V_AUDIO Bus

```
|
+----------------+
|                |
v                v
```

Audio             Headphone
Mixer             Amplifier

```


# 5. Protections

Planned:

- resettable fuse;
- surge protection;
- decoupling capacitors.


# 6. Notes

The circuit shall prioritize low noise.

The power supply shall not interfere with the microphone line or the TRRS inputs.
```
