# SCH-008 - Grounding and Noise Control

Version: 0.1
Status: Draft


# 1. Objetivo

Definir a estratégia de aterramento, alimentação e controle de ruído do MeetingHub-4.

O equipamento possui múltiplas fontes de áudio analógico conectadas simultaneamente, portanto o controle de interferência é requisito crítico.


# 2. Fontes potenciais de ruído

Possíveis fontes:

- quatro notebooks conectados simultaneamente;
- diferentes carregadores de fonte;
- loops de terra;
- alimentação USB;
- interferência digital externa.


# 3. Estratégia de aterramento

Será utilizado aterramento em estrela.

Arquitetura:

```

Entradas TRRS

```
  |
```

GND_AUDIO

```
  |
```

Ponto estrela

```
  |
```

Alimentação

```

Objetivos:

- evitar correntes circulando pelo terra de áudio;
- reduzir ruído de fundo;
- melhorar estabilidade.


# 4. Separação dos domínios

O projeto deverá separar:

## Áudio analógico

- entradas TRRS;
- mixer;
- amplificador headphone.


## Alimentação

- USB-C;
- filtros;
- proteção.


A união será feita em ponto controlado.


# 5. Layout da PCB

Requisitos:

- manter trilhas de áudio afastadas da alimentação;
- evitar paralelismo entre sinais sensíveis e alimentação;
- utilizar plano de terra quando aplicável;
- posicionar conectores próximos às bordas da placa.


# 6. Desacoplamento

Cada circuito integrado deverá possuir:

- capacitor cerâmico próximo aos pinos de alimentação;
- capacitores de reserva na alimentação principal.


# 7. Considerações sobre notebooks

O projeto deverá ser testado com:

- notebook ligado na bateria;
- notebook conectado ao carregador;
- diferentes marcas de computador.


# 8. Testes

Validar:

- ruído sem sinal;
- ruído com quatro notebooks conectados;
- troca do microfone;
- operação com carregadores diferentes.


# 9. Critério de aprovação

O equipamento deverá operar sem ruído perceptível em uso normal.
```

