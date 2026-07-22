# SCH-002 - Schematic Design Plan

Version: 0.1
Status: Draft

---

# 1. Objetivo

Definir a organização do esquemático elétrico antes da implementação no KiCad.

---

# 2. Folhas do esquemático

O projeto será dividido em blocos:

## Sheet 1 - Power Supply

Responsável por:

- entrada USB-C 5V;
- proteção;
- filtragem;
- distribuição das tensões.


## Sheet 2 - TRRS Inputs

Responsável por:

- conectores dos notebooks;
- separação dos sinais:
  - Audio Left
  - Audio Right
  - Ground
  - Microphone


## Sheet 3 - Audio Mixer

Responsável por:

- volumes individuais;
- somador estéreo;
- pré-amplificação.


## Sheet 4 - Headphone Amplifier

Responsável por:

- amplificação final;
- saída headset.


## Sheet 5 - Microphone Switching

Responsável por:

- seleção notebook 1-4;
- mute;
- relés de sinal.


# 3. Regras de projeto

- manter linha de microfone transparente;
- separar áudio analógico de alimentação;
- minimizar loops de terra;
- utilizar componentes de alta disponibilidade.

