# SCH-006 - Headphone Amplifier Design

Version: 0.1
Status: Draft


# 1. Objetivo

Definir o estágio responsável por fornecer potência suficiente ao headset TRRS conectado ao equipamento.

O amplificador deverá receber o sinal do mixer estéreo e fornecer saída adequada para fones de baixa e média impedância.


# 2. Arquitetura

Fluxo:

```

Mixer Estéreo

```
  |
  v
```

Volume Master

```
  |
  v
```

Amplificador Headphone

```
  |
  v
```

Headset TRRS

```


# 3. Requisitos

O amplificador deverá:

- operar com alimentação de 5V;
- possuir baixo ruído;
- suportar headset de uso profissional;
- evitar distorção em volume elevado;
- possuir proteção contra curto na saída.


# 4. Compatibilidade

Faixa esperada:

- 16 ohms;
- 32 ohms;
- 64 ohms.


# 5. Componentes candidatos

Opções iniciais:

## NJM4556A

Características:

- desenvolvido para amplificação de headphone;
- alta capacidade de corrente;
- simples;
- confiável.


## TPA6132A2

Características:

- baixa tensão;
- baixo consumo;
- saída dedicada para fones.


A seleção final será feita após análise de:

- disponibilidade;
- custo;
- qualidade de áudio.


# 6. Saída

A saída deverá manter padrão:

TRRS CTIA:

- Left
- Right
- Ground
- Microphone


O amplificador será responsável apenas pelos canais:

- Left
- Right


# 7. Proteções

Previstas:

- resistor de saída;
- desacoplamento;
- proteção contra curto;
- filtragem de alimentação.


# 8. Observações

A linha de microfone permanece independente.

O amplificador de headphone não deverá interferir na detecção do headset pelos notebooks.
```
