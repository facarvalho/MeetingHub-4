# SCH-004 - TRRS Interface Design

Version: 0.1
Status: Draft


# 1. Objetivo

Definir a interface elétrica entre os notebooks e o MeetingHub-4 utilizando conectores TRRS padrão CTIA.


# 2. Padrão Utilizado

Interface:

- TRRS 3,5 mm
- CTIA / AHJ


Pinagem:

| Contato | Função |
|---|---|
| Tip | Audio Left |
| Ring 1 | Audio Right |
| Ring 2 | Ground |
| Sleeve | Microphone |


# 3. Entradas

Quantidade:

4 entradas independentes.

Identificação:

- J1 - Notebook 1
- J2 - Notebook 2
- J3 - Notebook 3
- J4 - Notebook 4


# 4. Requisito de Transparência

O notebook deverá interpretar a conexão como um headset TRRS conectado diretamente.

A linha de microfone deverá:

- manter a polarização fornecida pelo notebook;
- não possuir amplificação;
- não possuir conversão;
- não alterar a impedância percebida.


# 5. Caminho do Áudio

Cada entrada será dividida:

```

TRRS

L  ---------> Controle Volume L
R  ---------> Controle Volume R
GND --------> Referência comum
MIC --------> Seletor de microfone

```


# 6. Caminho do Microfone

```

Headset MIC

```
  |
```

Circuito MUTE

```
  |
```

Seleção Notebook

```
  |
```

MIC Notebook selecionado

```


# 7. Proteção

Serão avaliadas:

- proteção ESD;
- filtragem EMI;
- proteção contra descargas nos conectores.

