# REWORK-001 — Correção manual das placas já fabricadas

Versão: 1.0 · Data: 2026-08-28
Aplica-se às 5 placas do lote JLCPCB `W2026080810364558` (gerbers v10.0).

---

## 1. Resumo

A análise do projeto identificou **3 erros de projeto** (confirmados no
esquemático **e** na netlist do PCB — por isso as 5 placas se comportam igual;
não é defeito de fabricação):

| # | Sintoma relatado | Causa | Onde se corrige |
|---|---|---|---|
| 1 | Potenciômetro aumenta para a esquerda, diminui para a direita | Terminais externos (1↔3 / 4↔6) trocados em RV1–RV5 | Parte B |
| 2 | No mínimo ainda sai áudio | Mesma troca: pot log ligado ao contrário → só corta no fim do curso; + VBIAS sem buffer | Parte B (+ Parte C opcional) |
| 3 | Microfone não funciona em nenhum PC, só um ruído ao plugar o P2 | Bobina e contatos dos relés K1–K4 trocados (a linha de mic do notebook está ligada na bobina; o acionamento está no contato) | Parte A |

**Observação adicional (não é erro de ligação, mas afeta o uso):** SW1–SW5
são botões **momentâneos** (SHOU HAN TS665ZJ). Ver Parte D.

### O que já foi alterado no repositório

O **esquemático** já foi corrigido nos itens 1 e 3:

- `hardware/KiCad/MeetingHub-4/MIXER.kicad_sch` — RV1–RV5: sinal e VBIAS
  trocados de terminal (netlist conferida: pino 1/4 = VBIAS, pino 3/6 = sinal,
  pino 2/5 = cursor).
- `hardware/KiCad/MeetingHub-4/MICSW.kicad_sch` — K1–K4: bobina nos pinos 2 e 9
  (2 = GND, 9 = acionamento), COM nos pinos 5/6 (mic do headset), `NBx_MIC` no
  pino 10 (contato NA), pino 1 (NF) livre; diodos D2–D5 reorientados como
  roda-livre correto (catodo no lado do acionamento).

O **layout do PCB (`MeetingHub-4.kicad_pcb`) NÃO foi re-roteado** — fazer isso à
mão sem o KiCad aberto é arriscado. Para gerar gerbers corrigidos e um novo lote:

1. Abrir o projeto no KiCad, rodar **ERC** (deve passar).
2. No Pcbnew: **Tools → Update PCB from Schematic (F8)**.
3. Re-rotear as ligações que ficarão vermelhas (pinos externos de RV1–RV5;
   pinos 1/9/10 de K1–K4; D2–D5). O restante da placa não muda.
4. Rodar DRC, refazer preenchimento de zonas, regenerar gerbers.

Enquanto isso, este documento descreve como consertar **na mão** as placas que
já chegaram, para validar as correções antes de encomendar o novo lote.

---

## 2. Ferramentas e materiais

- Ferro de solda ponta fina + solda fina (0,5–0,8 mm) + fluxo.
- Malha dessoldadora (pavio) e/ou sugador.
- Fio esmaltado/wire-wrap fino (AWG 30) ou fio flexível fino isolado — uns 60 cm.
- Estilete / bisturi (só se optar pelo método de corte de trilha — ver B.4).
- Multímetro com bipe de continuidade **e** medição de tensão DC.
- Lupa / microscópio, boa iluminação.
- Álcool isopropílico para limpar o fluxo no final.
- (Opcional Parte C) 1 capacitor eletrolítico 100–470 µF / ≥10 V por placa.

**Antes de começar:** faça a Parte A e a Parte B em **uma placa só**, teste tudo
(seção 6), e só depois replique nas outras 4.

---

## 3. Como identificar os pinos

- **Potenciômetros RV1–RV4** (corpo quadrado, vertical): 6 pinos em 2 colunas de
  3. O **pino 1 é o furo quadrado**. Na mesma coluna do pino 1, descendo:
  1 → 2 → 3. Na outra coluna: 4 → 5 → 6.
  - Coluna do pino 1: **1** (sinal L), **2** (cursor L), **3** (VBIAS).
  - Outra coluna: **4** (sinal R), **5** (cursor R), **6** (VBIAS).
- **RV5** (master, corpo largo, deitado, no painel frontal): mesma lógica, 2
  fileiras de 3. Pino **1** é o furo levemente quadrado; **1/2/3** numa fileira,
  **4/5/6** na outra; **2 e 5** são os cursores (centro).
- **Relés K1–K4** (Omron G5V-1): 6 pinos.
  ```
     [1]  ......  [10]        <- [1] é o furo quadrado
     [2]  ......  [ 9]        <- pinos 2 e 9 = BOBINA
     [5] ........ [ 6]        <- pinos 5/6 = COM (comum), afastados
  ```
  Contatos: **1** = NF (normalmente fechado), **10** = NA (normalmente aberto),
  **5/6** = COM.
- **Diodos D2–D5** (1N4148, deitados, ~7,6 mm): a **faixa** marca o catodo.

---

## 4. PARTE A — Relés K1–K4 (conserta o microfone)

### A.1 O que está errado

| Pino do relé | Ligado hoje a | Deveria estar em |
|---|---|---|
| 2 (bobina) | GND | GND ✔ (não mexer) |
| 9 (bobina) | `NBx_MIC` (mic do notebook) | acionamento (+5V da chave "Select") |
| 1 (contato NF) | chave "Select" + diodo Dx | nada (livre) |
| 5/6 (COM) | mic do headset (após MUTE) | mic do headset ✔ (não mexer) |
| 10 (contato NA) | nada | `NBx_MIC` |
| Dx | catodo→GND, anodo→acionamento | catodo→acionamento, anodo→GND |

Resultado do erro: a bobina fica entre GND e a linha de mic do notebook (nunca
liga, e "curto-circuita" a polarização de mic do notebook com ~167 Ω); o mic do
headset fica preso ao contato NF → diodo → GND.

### A.2 Passo a passo (repetir para K1, K2, K3, K4)

Tabela de referência — a "rede" de cada furo (não muda; só levantamos os pinos):

| Relé | furo 1 = | furo 9 = | diodo |
|---|---|---|---|
| K1 | acionamento NB1 (vai p/ SW2 e D2) | NB1_MIC | D2 |
| K2 | acionamento NB2 (SW3, D3) | NB2_MIC | D3 |
| K3 | acionamento NB3 (SW4, D4) | NB3_MIC | D4 |
| K4 | acionamento NB4 (SW5, D5) | NB4_MIC | D5 |

**Passo 1 — Levantar 3 pinos do relé.**
Aqueça e puxe delicadamente para cima ~1,5 mm os pinos **1, 9 e 10**, até que
saiam do furo e não encostem mais no anel de cobre. **Não** mexa nos pinos 2, 5,
6 nem nas abas metálicas de fixação — o relé continua preso.

**Passo 2 — Dois jumpers.**
Com fio fino isolado:
- **pino 9 (levantado) → furo 1** (o furo que sobrou vazio, ainda ligado ao
  acionamento). Agora a bobina recebe o +5V da chave.
- **pino 10 (levantado) → furo 9** (furo vazio, ainda ligado a `NBx_MIC`). Agora
  o contato NA leva o mic ao notebook quando o relé fecha.

**Passo 3 — Isolar o pino 1.**
O pino 1 (contato NF) fica **sem ligação**. Deixe-o levantado e, de preferência,
cubra a ponta com um pedacinho de termo-retrátil ou fita Kapton para não
encostar em nada.

**Passo 4 — Inverter o diodo Dx.**
Dessolde o diodo (D2 para K1, D3 para K2, etc.), gire **180°** e ressolde, de
forma que a **faixa (catodo) fique voltada para o lado oposto ao de hoje** — ou
seja, para o lado do pino da rede de acionamento (`Net-(Dx-A)`), e o anodo para
o lado do GND. Regra simples: hoje a faixa aponta para o relé; depois da
inversão ela aponta para **longe** do relé.

**Passo 5 — Conferência (multímetro, placa sem alimentação):**
- Continuidade **pino 9 do relé ↔ pino 2 da chave "Select" correspondente**: deve
  apitar.
- Continuidade **pino 10 do relé ↔ conector TRRS do notebook correspondente,
  contato do cabo (Sleeve/mic)**: deve apitar.
- Continuidade **pino 1 do relé ↔ qualquer coisa**: **não** deve apitar (isolado).
- Continuidade **pino 2 do relé ↔ GND**: deve apitar.
- Diodo Dx: no modo diodo, ponta vermelha no lado do acionamento (faixa) e preta
  no GND → deve indicar ~0,55–0,7 V (conduz); invertido → aberto.

---

## 5. PARTE B — Potenciômetros RV1–RV5 (conserta direção e "não zera")

### B.1 O que está errado

Cada gang do pot é um divisor: **entrada de sinal → trilha → VBIAS**, cursor →
saída. Hoje a entrada de sinal está no terminal que deveria ir ao VBIAS e
vice-versa. Isso (a) inverte o sentido e (b), como o pot é logarítmico ligado ao
contrário, faz o volume ficar quase no máximo em quase todo o curso e só cair no
finzinho.

Correção: **trocar os terminais 1↔3 e 4↔6**. O cursor (2 e 5) não muda.

### B.2 Redes de cada furo (não mudam; só levantamos os pinos)

| Pot | furo 1 | furo 3 | furo 4 | furo 6 |
|---|---|---|---|---|
| RV1 | sinal NB1-L (C5) | VBIAS | sinal NB1-R (C6) | VBIAS |
| RV2 | sinal NB2-L (C7) | VBIAS | sinal NB2-R (C8) | VBIAS |
| RV3 | sinal NB3-L (C9) | VBIAS | sinal NB3-R (C10) | VBIAS |
| RV4 | sinal NB4-L (C11) | VBIAS | sinal NB4-R (C12) | VBIAS |
| RV5 | sinal mix L (C13) | VBIAS | sinal mix R (C14) | VBIAS |

### B.3 Passo a passo (método recomendado — sem cortar trilha)

Repetir para RV1, RV2, RV3, RV4 e RV5.

**Passo 1 — Levantar 4 pinos.**
Aqueça e puxe para cima ~1,5 mm os pinos **1, 3, 4 e 6**. Deixe **2 e 5**
(cursores) e as abas de fixação soldados — o pot continua no lugar e alinhado.

**Passo 2 — Quatro jumpers cruzados** (fio fino; são só ~5 mm cada):
- pino **1** (levantado) → **furo 3**
- pino **3** (levantado) → **furo 1**
- pino **4** (levantado) → **furo 6**
- pino **6** (levantado) → **furo 4**

Pronto: o terminal 1 do pot passa a ver VBIAS, o terminal 3 passa a ver o sinal;
idem 4/6. Nenhuma trilha foi cortada, o barramento de VBIAS que liga RV1–RV4
continua intacto.

**Passo 3 — Conferência (multímetro):**
- Continuidade **terminal 1 do pot ↔ terminal 3 (antigo furo de VBIAS)** →
  agora o terminal 1 deve ter continuidade com o VBIAS / com o furo 3 de outro
  pot. Terminal 3 do pot deve ter continuidade com o capacitor de entrada
  (C5/C7/…).
- Com a placa ligada e um PC tocando música: girando o knob **no sentido
  horário o volume deve AUMENTAR**; no fim do curso anti-horário deve **zerar**.

### B.4 Método alternativo (se preferir não levantar pinos)

Para cada gang: cortar a trilha no furo 1 e no furo 3, e soldar dois jumpers
"cruzados" (furo 1 → ponta da trilha do furo 3; furo 3 → ponta da trilha do furo
1). Idem 4/6. É mais invasivo e exige recompor o barramento de VBIAS em RV2/RV3
(que passa "de dentro"); por isso o método B.3 (levantar pinos) é preferível.

---

## 6. PARTE C — VBIAS (opcional, recomendado)

O VBIAS é gerado só por um divisor 10k/10k + C3 de 10 µF, sem buffer. Com os
pots no mínimo, o sinal de todas as fontes é injetado nesse nó e vaza um
pouquinho para a saída. Se, **depois da Parte B**, ainda houver um resíduo baixo
audível no mínimo:

- **Solução rápida:** soldar um eletrolítico de **100–470 µF / ≥10 V** em
  paralelo com **C3** (perto do divisor R1/R2, região superior-esquerda do
  bloco do mixer). Polaridade: **+ no lado do VBIAS (pino 1 de C3)**, **− no GND
  (pino 2 de C3)**.
- **Solução boa (respin):** bufferizar o VBIAS com um seguidor de tensão
  (usar meio CI extra) e/ou baixar o divisor para 2×2,2 kΩ.

---

## 7. PARTE D — Seleção e MUTE (tirar o "segurar botão")

### D.1 Por que hoje tem que segurar

SW1–SW5 são táteis **momentâneos** (fecham só enquanto pressionados) e estão
ligados "direto", sem trava:

- **SW1 (MUTE)** fica em **série** com a linha do microfone → normalmente
  **aberto** → o mic só passa enquanto você aperta ("aperte para falar", ao
  contrário de um mute).
- **SW2–SW5 (Select)** alimentam a bobina do relé direto → o relé só fica ligado
  enquanto o botão está apertado.

Isso é um 4º defeito de projeto. Para **validar o rework** (Partes A/B) não
precisa resolver — é só segurar os botões durante o teste. Mas se você quer usar
a placa de verdade, escolha uma das opções abaixo.

### D.2 Opção mínima — sem peça nova (bom p/ teste e uso de 1 PC fixo)

- **Ponte permanente nos 2 polos do SW1** (uma gota de solda ou um pedacinho de
  fio entre `SW1 furo 1` e `SW1 furo 2`) → o microfone passa sempre.
- **Ponte permanente nos 2 polos de UM dos "Select"** (ex.: SW2) → aquele
  notebook fica selecionado direto.
- Perde o mute e a troca de PC, mas zero peça e zero "segurar".

### D.3 Opção recomendada — 1 chave rotativa (seleção + mute juntos)

Uma **chave rotativa 1 polo, 5 posições** (não-curto-circuitante / "break before
make"), com fios volantes:

| Posição | Ligar o terminal da posição a | Efeito |
|---|---|---|
| 1 — OFF | (nada) | todos os relés desligados → **mic mudo** |
| 2 — NB1 | `SW2 furo pad-2` (rede do acionamento de K1) | mic → notebook 1 |
| 3 — NB2 | `SW3 furo pad-2` | mic → notebook 2 |
| 4 — NB3 | `SW4 furo pad-2` | mic → notebook 3 |
| 5 — NB4 | `SW5 furo pad-2` | mic → notebook 4 |

- **Comum da rotativa** → **+5 V**: o ponto mais fácil é `SW2 furo pad-1`
  (já é `+5V_AUDIO`), ou o test point **TP1**.
- Como a posição OFF já é o mute, **dê a ponte permanente no SW1** (D.2) e não
  precisa de botão de mute separado.
- SW2–SW5 podem **sair da placa** ou **ficar no lugar sem uso** (são
  normalmente abertos; não atrapalham — no máximo funcionam como um "override"
  momentâneo em paralelo com a rotativa).
- A rotativa força **um PC de cada vez** mecanicamente — resolve também a
  falta de intertravamento do projeto original.

Furos de referência (vistos por cima, fileira frontal, y ≈ 212–214,5):
`SW1` à esquerda, depois `RV5`, depois `SW2, SW3, SW4, SW5`. O `furo pad-2` de
cada "Select" é o de **trás** (mais longe da borda), que carrega a trilha
`Net-(Dx-A)` para o relé.

### D.4 Opção alternativa — botões com retenção

Trocar SW1–SW5 por botões **push-on/push-off** (com trava). Provavelmente muda o
footprint (o TS665ZJ é só momentâneo), então é mais trabalho de adaptar furos.
E os 4 "Select" continuam sem intertravamento: se travar 2, dois PCs recebem o
mic (erro do usuário — já assumido no SCH-007). Por isso a rotativa (D.3) é
melhor.

> Para o respin, a recomendação é: **rotativa 1P5T para o Select + 1 botão
> latching só para o MUTE** (ou manter só a rotativa com posição OFF).

---

## 8. Teste de verificação (após reworkar 1 placa)

Alimente pela USB-C. Com um multímetro:

1. **VBIAS** ≈ 2,4–2,6 V (medir no pino 1 de C3 ou no terminal 1 de qualquer RV).
2. **+5V_AUDIO** ≈ 5 V no test point TP1.

Áudio (1 notebook por vez, com fone no J6):

3. Toque música no notebook 1 (cabo TRRS em J1... *no J do notebook 1*).
   Gire **RV1 no horário → volume sobe**; anti-horário até o fim → **silêncio
   total**. Repita RV2–RV4 e o master RV5.
4. Duas ou mais fontes ao mesmo tempo: devem somar sem uma "puxar" a outra.

Microfone:

5. Fone com microfone no J6. Selecione o notebook 1 — **segurando SW1 + SW2**,
   ou (se já fez a Parte D) pela ponte do SW1 + rotativa na posição NB1.
   Fale: o notebook 1 deve captar o microfone normalmente (testar em
   Gravador de Voz / Meet).
6. Troque para o notebook 2 (segurar SW3 / rotativa em NB2). Etc.
7. Nada selecionado (rotativa em OFF, ou nenhum "Select" apertado): nenhum
   notebook capta (mudo).
8. Confirme que o notebook **reconhece o headset** (aparece microfone externo) —
   isso valida que a linha de mic não está mais carregada pela bobina.

Se 3, 5 e 7 passarem, as três correções estão boas → replicar nas outras 4
placas e seguir para o respin do PCB.

---

## 9. Checklist por placa

```
Placa nº ____

RELÉS
[ ] K1: pinos 1,9,10 levantados · jumper 9→furo1 · jumper 10→furo9 · pino1 isolado · D2 invertido
[ ] K2: idem · D3 invertido
[ ] K3: idem · D4 invertido
[ ] K4: idem · D5 invertido
[ ] continuidade conferida (A.2 passo 5) nos 4 relés

POTENCIÔMETROS
[ ] RV1: pinos 1,3,4,6 levantados · jumpers 1↔3 e 4↔6
[ ] RV2: idem
[ ] RV3: idem
[ ] RV4: idem
[ ] RV5: idem
[ ] direção conferida (horário = mais alto) nos 5

SELEÇÃO / MUTE (Parte D — escolher uma)
[ ] D.2 pontes em SW1 + um Select   (uso fixo de 1 PC)
[ ] D.3 chave rotativa 1P5T: comum→+5V, pos NB1..NB4→SW2..SW5 pad-2, ponte no SW1
[ ] (ou deixar momentâneo e segurar botão só no teste)

OPCIONAL
[ ] C3 reforçado com eletrolítico ___ µF

TESTE
[ ] VBIAS ~2,5 V   [ ] +5V TP1
[ ] RV1..RV5 sobem no horário e zeram no fim
[ ] mic NB1..NB4 OK (segurando SW1 + Select)
[ ] headset reconhecido pelo notebook
[ ] limpeza do fluxo
```

---

## 10. Depois de validar

1. No KiCad: ERC → Update PCB from Schematic → re-rotear RV1–RV5 (pinos externos)
   e K1–K4 (pinos 1/9/10) e D2–D5 → DRC → zonas → gerbers.
2. Avaliar no respin: chave rotativa 1P5T (OFF/NB1–NB4) para a seleção de mic
   + botão latching (ou a própria posição OFF) para o MUTE; buffer de VBIAS.
3. Encomendar novo lote e descartar/aposentar as placas reworkadas (ou mantê-las
   como protótipos).
