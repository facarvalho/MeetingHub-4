# SCH-003 - Power Supply Design

Version: 0.1
Status: Draft


# 1. Objetivo

Definir a arquitetura da alimentação elétrica do MeetingHub-4.


# 2. Entrada

Fonte:

USB-C

Tensão:

5V DC


# 3. Requisitos

A alimentação deverá:

- possuir proteção contra sobrecorrente;
- possuir filtragem contra ruído;
- separar alimentação digital e analógica;
- minimizar interferência no áudio.


# 4. Arquitetura

```

USB-C 5V

```
|
v
```

Proteção entrada

```
|
v
```

Filtro EMI

```
|
v
```

Barramento +5V_AUDIO

```
|
+----------------+
|                |
v                v
```

Mixer            Amplificador
de áudio         Headphone

```


# 5. Proteções

Previstas:

- fusível resetável;
- proteção contra surtos;
- capacitores de desacoplamento.


# 6. Observações

O circuito deverá priorizar baixo ruído.

A alimentação não deverá interferir na linha de microfone ou nas entradas TRRS.
```

