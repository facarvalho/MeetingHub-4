# SCH-007 - Microphone Switching Design

Version: 0.1
Status: Draft


# 1. Objective

Define the circuit responsible for routing the headset microphone to one of the four laptops.


# 2. Main Requirement

The microphone line must remain electrically transparent.

The laptop must see:

```

Laptop

```
|
```

Headset MIC

```

with no significant difference compared to a direct connection.


# 3. Constraints

Do not use:

- microphone amplifier;
- digital converter;
- processing;
- alteration of microphone bias/polarization.


# 4. Architecture

Flow:

```

Headset MIC

```
  |

 MUTE

  |
```

MIC Selection

```
  |
```

+-----+-----+-----+-----+

|     |     |     |     |

NB1   NB2   NB3   NB4

```


# 5. Switching Method

Initial method:

Signal relays.

Desired characteristics:

- low contact resistance;
- gold-plated contact;
- low capacitance;
- long service life.


# 6. Operation

Only one laptop must receive the microphone at a time.

States:

```

Selected:
NB1
NB2
NB3
NB4

or

None (MUTE)

```


# 7. MUTE

Mute must interrupt the microphone line.

Characteristics:

- physical action;
- immediate response;
- no software.


# 8. Considerations

The circuit must be validated with different laptops due to variations in headset detection implementation.


# 9. Required Tests

Validate:

- headset recognition;
- microphone operation;
- switching between laptops;
- absence of noise;
- absence of interference.
```

