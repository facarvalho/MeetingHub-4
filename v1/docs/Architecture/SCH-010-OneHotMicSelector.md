# SCH-010 — Seleção exclusiva de microfone (one-hot, só hardware)

Versão: 1.0 · Data: 2026-08-28
Opção **C2** decidida com o usuário: botões **momentâneos** (sem trava mecânica)
+ **trava eletrônica** feita com um CD4043 e uma matriz de diodos. Comportamento
de KVM: aperto NB2 → NB2 liga e o que estava selecionado **desarma sozinho**.

Serve tanto para reworkar a placa fabricada (`b86a034`) quanto para o respin.

> **IMPORTANTE:** na placa fabricada **não existe footprint** para o CD4043 nem
> para os MOSFETs — e nem precisa. Todo esse circuito é montado numa
> **plaquinha separada** (perfboard ~5×7 cm) que fica **solta dentro da caixa**
> e se liga à placa principal por ~12 fios (§5). Na placa principal só se faz
> corte de trilha, jumper e levantar pino — **nenhum componente novo é soldado
> nela**.
>
> Se você não quer plaquinha nenhuma, veja as opções **sem eletrônica** no
> REWORK-001 Parte D (chave rotativa, ou régua de botões intertravados).

---

## 1. Comportamento

- 4 botões momentâneos, um por notebook (NB1..NB4 = relés K1..K4).
- Apertar o botão X: **liga K_X e desliga os outros 3.**
- Soltar o botão: o estado **fica** (trava eletrônica).
- Ligar a placa: **nenhum** selecionado → microfone não vai a ninguém = mudo.
- Apertar 2 ao mesmo tempo: enquanto os dois estão apertados, **ambos ficam
  desligados**; ao soltar, vence o **último a ser solto** (na prática, imite
  não apertar dois de propósito).
- Bounce de contato: imune (o latch RS re-afirma o mesmo estado).

---

## 2. Princípio — CD4043B (quad latch RS tipo NOR) + matriz de diodos

Um latch RS por canal. Latch tipo NOR:

| S | R | Q |
|---|---|---|
| 0 | 0 | mantém |
| 1 | 0 | 1 |
| 0 | 1 | 0 |
| 1 | 1 | 0 |

**Regra da matriz:** o botão X leva +5 V para **`S_X`** e para **`R`** dos
outros três. Nunca leva S e R do mesmo latch → sem conflito.

- Botão X apertado → `S_X=1,R_X=0` → `Q_X=1`; nos outros `S=0,R=1` → `Q=0`.
- Botão solto → todas as linhas S/R caem (pull-down) → todos os latches mantêm.

### Pinagem do CD4043BE (DIP-16, vista de cima)

```
        ┌────┬─┬────┐
  Q4  1 ┤    └─┘    ├ 16  VDD (+5V)
  Q1  2 ┤           ├ 15  R4
  R1  3 ┤           ├ 14  S4
  S1  4 ┤  CD4043B  ├ 13  NC
ENABLE 5├┤           ├ 12  S3
  S2  6 ┤           ├ 11  R3
  R2  7 ┤           ├ 10  Q3
 VSS  8 ┤           ├  9  Q2
        └───────────┘
```

- **VDD (16) → +5 V**, **VSS (8) → GND**, **ENABLE (5) → +5 V** (liga as saídas).
- 100 nF entre 16 e 8, colado no CI.
- Latch A (NB1): S1=4, R1=3, Q1=2
- Latch B (NB2): S2=6, R2=7, Q2=9
- Latch C (NB3): S3=12, R3=11, Q3=10
- Latch D (NB4): S4=14, R4=15, Q4=1

---

## 3. Esquema

### 3.1 Entrada de botão + matriz de diodos (todos os diodos = 1N4148)

```
 +5V ─┬─[BTN1]─┬─►|─ S1        (►| = 1N4148, anodo no botão, catodo na linha)
      │        ├─►|─ R2
      │        ├─►|─ R3
      │        └─►|─ R4
      │
      ├─[BTN2]─┬─►|─ S2
      │        ├─►|─ R1
      │        ├─►|─ R3
      │        └─►|─ R4
      │
      ├─[BTN3]─┬─►|─ S3
      │        ├─►|─ R1
      │        ├─►|─ R2
      │        └─►|─ R4
      │
      └─[BTN4]─┬─►|─ S4
               ├─►|─ R1
               ├─►|─ R2
               └─►|─ R3

 S1,S2,S3,S4 ── cada uma: 100k → GND
 R1,R2,R3,R4 ── cada uma: 100k → GND
```

16 diodos de matriz. `BTNn` = botão momentâneo NA (normalmente aberto), um lado
no +5 V.

### 3.2 Reset ao ligar (power-on = mudo)

```
 +5V ──┤ 1µF ├──┬──►|─ R1
                ├──►|─ R2
                ├──►|─ R3
                ├──►|─ R4
                │
               100k
                │
               GND
```

No instante que liga, o degrau de +5 V passa pelo capacitor → as 4 linhas R
sobem por ~20 ms → todos os `Q=0` → nenhum relé → mudo. Depois o nó cai a 0 V
e os diodos ficam reversos. (4 diodos + 1µF + 100k.)

### 3.3 Driver de bobina — 1 por canal (Q → MOSFET → bobina)

```
        +5V
         │
     ┌───┴───┐              Dx (1N4148)
     │ bobina│  pino 2 ──┬──────|◄──┐   (catodo p/ +5V)
     │  K_n  │           │          │
     └───┬───┘  pino 9 ──┴──────────┴──┬─── dreno
         │                             │
       (contatos: COM=5/6, NO=10, NC=1)│
                                     [2N7000]
                                       │ fonte
                                      GND

  Q_n ──[470Ω]──┬── gate
                │
              100k
                │
               GND
```

- `Q_n = 1` → MOSFET conduz → puxa o pino 9 da bobina para GND → **relé liga**.
- `Q_n = 0` → MOSFET corta → bobina desenergiza; `Dx` corta o pico indutivo.
- **A bobina do relé passa a ficar entre +5 V (pino 2) e o MOSFET (pino 9).**
  `Dx` (o antigo D2–D5) fica em paralelo com a bobina, **catodo para o lado do
  pino 2 (+5 V)**.
- Só **1 relé ligado por vez** → consumo ~30 mA (não 120 mA). Folgado no F1.

### 3.4 (Opcional) LED indicador por canal

```
 Q_n ──[2k2]──►|──(LED)── GND
```
Acende fraco (~1 mA) mas visível. 4 LED + 4 × 2k2.

### 3.5 (Opcional) botão MUTE / OFF

Um 5º botão momentâneo que **reseta todos os latches**:

```
 +5V ──[BTN_MUTE]─┬─►|─ R1
                  ├─►|─ R2
                  ├─►|─ R3
                  └─►|─ R4
```
+4 diodos. Apertar → todos `Q=0` → todos os relés soltam → COM fica no NC
(aberto) → microfone não vai a ninguém = mudo.

---

## 4. Lista de materiais (placa auxiliar)

| Qtd | Item | Obs |
|---|---|---|
| 1 | **CD4043BE** DIP-16 + soquete | quad latch RS NOR, 3-state |
| 1 | 100 nF cerâmico | desacople VDD |
| 16 (+4 se MUTE) | 1N4148 | matriz de diodos |
| 4 | 1N4148 | reset de power-on |
| 8 | resistor 100 k | pull-down de S1–S4, R1–R4 |
| 1 | capacitor 1 µF | reset de power-on |
| 1 | resistor 100 k | reset de power-on |
| 4 | **2N7000** (ou 2N7002 SMD) | driver de bobina (N-MOSFET nível lógico) |
| 4 | resistor 470 Ω a 1 k | série no gate (não é crítico; 1 k serve) |
| 4 | resistor 100 k | pull-down de gate |
| 1 | capacitor 100 µF / ≥10 V | bulk de +5 V na placa auxiliar |
| — | 4 (ou 5) botões táteis momentâneos NA | pode reusar SW2–SW5 da placa |
| — | perfboard ~5×7 cm, fio fino | |
| 4 | LED + 4 × 2k2 | *opcional*, indicador |

Diodos D2–D5 **continuam na placa principal** como roda-livre (reorientados —
ver §5).

### 4.1 Compra — para reparar 1 placa (5 placas entre parênteses)

**Peças que TÊM que ser exatamente essas (LCSC — códigos conferidos):**

| Item | LCSC | Link | Qtd |
|---|---|---|---|
| **CD4043BE** DIP-16 (TI) | **C39537** | https://www.lcsc.com/product-detail/C39537.html | 1 (5) |
| — ou clone mais barato | C22390239 | https://www.lcsc.com/product-detail/C22390239.html | |
| **2N7000** N-MOSFET TO-92 | **C9114** | https://www.lcsc.com/product-detail/C9114.html | 4 (20) |
| **1N4148** DO-35 THT (o mesmo dos D2–D5) | **C402212** | https://www.lcsc.com/product-detail/C402212.html | 20 · +4 se MUTE (120) |

**Passivos genéricos — reaproveite os códigos que já estão na BOM do projeto:**

| Item | LCSC (já na BOM-003) | Qtd |
|---|---|---|
| Resistor 100 k 1/4 W THT (= R13/R17) — 8 pull-down S/R + 4 pull-down gate + 1 power-on | **C1364475** | 13 (70) |
| Resistor 1 k 1/4 W THT (= R14/R15…) — série no gate do MOSFET | **C120055** | 4 (20) |
| Capacitor 1 µF THT X7R (= C5–C14) — serve no reset de power-on | **C2167638** | 1 (5) |

**Passivos comuns — de kit ou loja local (não vale a pena link específico):**

| Item | Qtd |
|---|---|
| Soquete DIP-16 (2,54 mm) | 1 (5) |
| Capacitor 100 nF cerâmico THT (desacople do CI) | 1 (5) |
| Capacitor 100 µF / ≥16 V eletrolítico THT (bulk +5 V) | 1 (5) |
| *(opcional)* LED 3 mm difuso + resistor 2k2 1/4 W THT | 4 + 4 (20 + 20) |
| Perfboard ~5×7 cm + fio fino | 1 (5) |

> Um **kit sortido de resistores 1/4 W THT** + um **kit de capacitores cerâmicos
> THT** cobrem os genéricos e sobra muito.
>
> **NÃO precisa comprar:** relés K1–K4, diodos D2–D5 (ficam na placa),
> potenciômetros, botões seletores (reusa SW2–SW5). O SW1 só leva uma ponte de
> solda.

---

## 5. Ligação à placa fabricada (`b86a034`) — junto com o conserto do microfone

> Este procedimento **substitui** a Parte A + Parte D do REWORK-001 (faz o
> conserto do mic e a seleção one-hot de uma vez). Faça **1 canal (K1) primeiro**
> e teste.

### 5.1 Por relé (K1..K4) + diodo (D2..D5)

1. **Levante os pinos 1, 2, 9 e 10** do relé (deixe 5 e 6 soldados + um ponto de
   cola quente para segurar).
2. Ligações novas nos pinos levantados:
   - **pino 2 → barramento +5 V** (fio novo — ver §5.2).
   - **pino 9 → saída de dreno do MOSFET** do canal (fio até a placa auxiliar).
   - **pino 10 → furo 9** (o furo que ficou vazio, que tem a trilha `NBx_MIC`).
   - **pino 1 → nada** (isolado).
3. **Diodo Dx (D2→K1, D3→K2, D4→K3, D5→K4):** dessolde e ressolde **em paralelo
   com a bobina, entre os pinos 2 e 9 do relé**, com a **faixa (catodo) para o
   lado do pino 2 (+5 V)**. Se ficar mais fácil, solde-o direto nas pernas
   levantadas 2 e 9.

### 5.2 Barramento +5 V para as bobinas

Um fio ligando **pino 2 de K1, K2, K3, K4** entre si e a um ponto de +5 V:
**TP1** (`+5V_AUDIO`, ~(215,1 , 101,8)) ou o pino 2 de F1 (~(165,6 , 106,2)).

### 5.3 Botões

Reusando **SW2–SW5** (já são momentâneos e já têm +5 V no pad 1):

1. Em cada SW, **corte a trilha do pad 2** (o pad de trás, ~(95,6 , 212,0) etc.)
   para soltá-lo do relé.
2. Fio: **SW2 pad 2 → BTN1** da matriz · SW3 pad 2 → BTN2 · SW4 pad 2 → BTN3 ·
   SW5 pad 2 → BTN4.  (o pad 1 continua no +5 V; apertar leva +5 V ao pad 2 → à
   matriz.)

### 5.4 MUTE (SW1)

Você já autorizou tirar o mudo dedicado. Duas opções:

- **Sem botão de mudo:** ponte de solda ligando os 2 furos com trilha do SW1
  (`HEADSET_MIC` ↔ furo dos COM dos relés). O microfone sempre chega aos relés;
  "mudo" = nenhum botão apertado desde que ligou (ou aperte o botão do canal
  atual… não, isso não desliga — então nesse modo, uma vez selecionado, sempre
  há um ativo).
- **Com botão de mudo (recomendado):** dê a ponte no SW1 (mic passa direto) e
  **adicione um 5º botão** (novo, no painel) ligado a `BTN_MUTE` (§3.5).
  Apertar = volta ao mudo.

### 5.5 Alimentação da placa auxiliar

`+5 V` e `GND` da placa principal (TP1 / qualquer GND). 100 µF de bulk na
entrada da placa auxiliar.

### 5.6 Conferência (multímetro / bancada)

1. Ligar: nenhum LED / nenhum relé clicado. Multímetro em `NBx_MIC`: sem
   continuidade com o headset. **Mudo.** ✔
2. Apertar BTN2 (NB2): K2 clica, LED2 acende. `NB2_MIC` ↔ headset com
   continuidade; `NB1/3/4_MIC` não. ✔
3. Apertar BTN4: K2 solta, K4 clica. Só NB4 ativo. ✔
4. Apertar BTN2 e BTN3 juntos: nenhum fica ligado. ✔
5. (Se tiver MUTE) apertar MUTE: todos soltam. ✔

---

## 6. Para o respin (KiCad)

Nova folha `SELECT_LOGIC.kicad_sch`:

- `U3 = CD4043B` (símbolo `4xxx:CD4043B`), footprint SOIC-16 ou DIP-16.
- Matriz de 16 (ou 20) diodos `D_Small` + 8 pull-downs 100 k.
- RC de power-on-reset (1 µF + 100 k + 4 diodos).
- 4 × `Q_ATtiny`… não — 4 × `2N7000` + 470 Ω + 100 k.
- SW2–SW5 continuam `Switch:SW_SPST` (momentâneos), mas o pad "sinal" vai à
  matriz, não mais direto ao relé.
- Relés K1–K4: **pino 2 → +5V_AUDIO**, **pino 9 → dreno do MOSFET do canal**,
  pino 10 → `NBx_MIC`, pino 1 NC, COM 5/6 → `HEADSET_MIC`.
- D2–D5: catodo → +5V (pino 2), anodo → pino 9.
- SW1 removido (ou vira `BTN_MUTE` → 4 diodos → R1..R4). LEDs opcionais.
- No PCB: a placa toda passa a caber melhor porque some o barramento de +5 V
  chaveado pelos botões (agora os botões são sinal lógico, corrente ~0).

> Isto é uma folha nova inteira — quando você decidir fechar o respin, eu monto
> o `.kicad_sch` dessa lógica e ligo aos sinais existentes.
