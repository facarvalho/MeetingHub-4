# SCH-007 - Microphone Switching Design

Version: 0.1
Status: Draft


# 1. Objetivo

Definir o circuito responsável por direcionar o microfone do headset para um dos quatro notebooks.


# 2. Requisito Principal

A linha de microfone deverá permanecer eletricamente transparente.

O notebook deverá enxergar:

```

Notebook

```
|
```

Headset MIC

```

sem diferença significativa em relação a uma conexão direta.


# 3. Restrições

Não utilizar:

- amplificador de microfone;
- conversor digital;
- processamento;
- alteração da polarização do microfone.


# 4. Arquitetura

Fluxo:

```

Headset MIC

```
  |

 MUTE

  |
```

Seleção MIC

```
  |
```

+-----+-----+-----+-----+

|     |     |     |     |

NB1   NB2   NB3   NB4

```


# 5. Método de Chaveamento

Método inicial:

Relés de sinal.

Características desejadas:

- baixa resistência de contato;
- contato dourado;
- baixa capacitância;
- alta vida útil.


# 6. Operação

Somente um notebook deverá receber o microfone por vez.

Estados:

```

Selecionado:
NB1
NB2
NB3
NB4

ou

Nenhum (MUTE)

```


# 7. MUTE

O mute deverá interromper a linha do microfone.

Características:

- ação física;
- resposta imediata;
- sem software.


# 8. Considerações

O circuito deverá ser validado com diferentes notebooks devido às variações de implementação de detecção de headset.


# 9. Testes Necessários

Validar:

- reconhecimento do headset;
- funcionamento do microfone;
- troca entre notebooks;
- ausência de ruído;
- ausência de interferência.
```

