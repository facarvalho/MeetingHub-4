# SCH-005 - Audio Mixer Design

Version: 0.1
Status: Draft


# 1. Objetivo

Definir o circuito responsável por misturar o áudio estéreo dos quatro notebooks.

O sistema deverá permitir:

- ouvir quatro fontes simultaneamente;
- controlar o volume de cada fonte;
- manter separação entre canais esquerdo e direito;
- fornecer sinal adequado ao amplificador de headphone.


# 2. Arquitetura

Cada notebook possui dois canais:

- Audio Left
- Audio Right


Fluxo:

```

Notebook 1 L/R
|
v
Volume 1

Notebook 2 L/R
|
v
Volume 2

Notebook 3 L/R
|
v
Volume 3

Notebook 4 L/R
|
v
Volume 4

```
    |
    v
```

Mixer Estéreo Ativo

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


# 3. Topologia do Mixer

Será utilizado mixer ativo utilizando amplificadores operacionais.

Características:

- baixo ruído;
- impedância de entrada elevada;
- baixa interferência entre fontes.


# 4. Controle de Volume

Cada notebook terá:

- potenciômetro estéreo;
- ajuste independente de volume.


Quantidade:

- 4 controles individuais.


# 5. Canal Estéreo

O projeto deverá manter:

Canal esquerdo:

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


Canal direito:

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


# 6. Requisitos

O mixer deverá:

- evitar que uma saída de notebook carregue outra;
- manter baixa distorção;
- preservar faixa de frequência de áudio;
- funcionar com sinais de saída de notebook.


# 7. Componentes candidatos

Amplificador operacional:

- NE5532
- OPA1652
- equivalente de áudio


# 8. Observações

O circuito final será validado considerando:

- ruído;
- ganho;
- nível máximo de saída;
- compatibilidade com amplificador de headphone.
```
