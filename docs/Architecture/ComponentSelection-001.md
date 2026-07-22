# Fase 3 — Seleção de componentes (BOM preliminar)

Antes de desenhar o esquemático, precisamos escolher componentes reais. A regra será:

* componentes disponíveis no mercado;
* boa durabilidade;
* custo razoável;
* fácil reposição;
* montagem simples.

Vamos criar:

```text
hardware/BOM/BOM-001.xlsx
```

e também um documento:

```text
docs/Architecture/ComponentSelection-001.md
```

---

## Componentes principais — proposta inicial

### 1) Conectores TRRS de painel

Requisito:

* P2 fêmea 3,5 mm
* metálico
* montagem em painel
* padrão CTIA

Quantidade:

* 5 unidades

  * 4 notebooks
  * 1 headset

Critérios:

* contato banhado
* fixação mecânica por porca
* vida útil alta

---

### 2) Potenciômetros de volume

Quantidade:

* 5 unidades

Funções:

* Volume Notebook 1
* Volume Notebook 2
* Volume Notebook 3
* Volume Notebook 4
* Volume Master

Tipo:

* estéreo
* 10 kΩ logarítmico
* eixo metálico

---

### 3) Mixer ativo

Proposta inicial:

**NE5532**

Quantidade:

* 2 unidades

Uso:

* canal esquerdo
* canal direito

Motivos:

* excelente para áudio;
* barato;
* muito conhecido;
* fácil de encontrar.

---

### 4) Amplificador de headphone

Opções em análise:

**NJM4556A**

ou

**TPA6120A2**

Critérios:

* baixa distorção;
* capacidade para headset 16–64 Ω;
* estabilidade.

Para a V1 eu tenderia ao **NJM4556A**, por ser simples e robusto.

---

### 5) Seleção do microfone

Requisito principal:

O notebook deve continuar "vendo" um headset.

Proposta:

Relé de sinal.

Modelo candidato:

* Omron G6K
* Panasonic TQ2

Quantidade:

* 1 conjunto de seleção

---

### 6) MUTE

Botão:

* industrial;
* normalmente fechado (NC).

Por quê?

Se o botão quebrar, o padrão seguro é continuar funcionando.

---

### 7) Alimentação

Entrada:

USB-C 5 V

Blocos:

```text
USB-C
  |
Proteção
  |
Filtro
  |
5V Analógico
```

---

# Próximo documento

Agora vamos criar:

```
docs/Architecture/ComponentSelection-001.md
```

Nele vamos registrar:

* componente escolhido;
* alternativas;
* motivo da escolha;
* datasheet;
* fornecedor.

---

Depois disso vem a etapa mais importante:

## Esquemático elétrico Rev A

Vamos desenhar os blocos:

1. Entrada TRRS.
2. Separação L/R/MIC.
3. Controle de volume.
4. Mixer estéreo.
5. Amplificador de headphone.
6. Circuito de microfone.
7. Alimentação.

