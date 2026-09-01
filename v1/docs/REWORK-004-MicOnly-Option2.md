# REWORK-004 — Consertar SÓ o microfone (Opção 2), sem comprar nada

Versão: 1.0 · Data: 2026-08-31
Placa física de referência = commit **`b86a034`** (o lote JLCPCB `W2026080810364558`).
Guia visual (artefato HTML): <https://claude.ai/code/artifact/b2020ecc-38f1-42e4-a727-40a2e051e617>

---

## 1. O que este guia faz (e o que NÃO faz)

| | |
|---|---|
| **Objetivo** | Deixar o **microfone do headset funcionando nos 4 notebooks** na placa que já chegou. |
| **Como fica o uso** | "Aperte para falar": você **segura** o botão *Select* (SW2…SW5) do notebook enquanto fala. Soltou = mudo. |
| **Custo** | **R$ 0.** Só solda + ~30 cm de fio fino. Reaproveita relés, diodos e botões que já estão na placa. |
| **Tempo** | ~1h30–2h para a **primeira** placa (faça 1 relé inteiro, teste, depois os outros 3). ~1h por placa depois. |
| **NÃO cobre** | Potenciômetros invertidos → `REWORK-001` Parte B. Acabar de vez com o "segurar botão" → seção 11. |

> Este é o caminho **mais barato e simples** que ainda mantém a seleção dos 4
> notebooks. Se você só usa 1 notebook, a "Opção 1" (2 soldas) está na
> `REWORK-001 §1b` / resposta do chat.

---

## 2. Ferramentas e materiais

### Obrigatório

| Item | Detalhe |
|---|---|
| Ferro de solda ponta fina | 15–30 W, ponta de 1 mm ou menor, ~330 °C. Ponta limpa e estanhada. |
| Solda fina | 0,5–0,8 mm, **com fluxo (rosin core)**. Sn63/Pb37 é o mais fácil; sem chumbo também serve. |
| Caneta / seringa de **fluxo** | Essencial para não fazer "solda fria" ao levantar pino e ao soldar fio fino. |
| **Sugador de solda** OU **malha dessoldadora** 1,5–2 mm | Para limpar os furos. Tenha os dois se puder. |
| **Fio fino AWG 30** isolado (Kynar/wire-wrap) | ~30 cm. Alternativa: perna cortada de resistor + espaguete fino. Evite fio esmaltado (o verniz descasca e dá curto). |
| Alicate de bico fino + alicate de corte | |
| Pinça | Para segurar o pino do relé enquanto aquece. |
| **Multímetro** | Com bip de continuidade, tensão DC **e** teste de diodo. É o que garante que deu certo. |
| Lupa / óculos de aumento / câmera do celular no zoom | Os furos têm ~1 mm. |
| Fita Kapton **ou** termo-retrátil 1 mm | Para isolar o pino 1 levantado. |
| Álcool isopropílico + escova/cotonete | Limpar o fluxo no fim (fluxo velho fica condutivo). |

### Recomendado

- "Terceira mão" ou morsa de PCB, e **luz boa**.
- Multímetro com pontas de agulha (as garras não entram nos furos).
- Cola quente (uma gota para ancorar os fios no fim).
- Bobininha de solda de sobra e um pino/agulha para desentupir furo.

### Comprar: **nada.** 

Não troque os botões, não compre CI, não compre relé. Tudo que o conserto usa
já está na placa.

---

## 3. Por que o microfone não funciona (o defeito)

Os relés **K1–K4** são Omron **G5V-1** (SPDT). No projeto fabricado, a fábrica
soldou exatamente o que estava no arquivo — e o arquivo tinha os pinos da
**bobina trocados com os do contato**:

| Pino do relé | Função real (G5V-1) | Está ligado hoje a | Efeito |
|---|---|---|---|
| **2** | bobina | GND | — |
| **9** | bobina | **`NBx_MIC`** (linha de microfone do notebook) | a bobina (~167 Ω) fica **pendurada na linha de mic** → "puxa" a polarização do mic do notebook para GND → **mic morto**, só um chiado ao plugar o P2 |
| **1** | contato NF | +5 V do botão *Select* (via diodo Dx) | o acionamento vai para um **contato**, não para a bobina → **o relé nunca liga** |
| **10** | contato NA | *nada* | é aqui que o mic do notebook **deveria** entrar |
| **5 / 6** | COM | mic do headset (via SW1) | ok |
| **Dx** | (1N4148) | catodo→GND, anodo→acionamento | orientação errada para roda-livre |

Além disso, **SW1** (o primeiro botão, rotulado *MUTE*) é um botão **momentâneo
em série** com a linha do mic: normalmente **aberto** → o mic só passa enquanto
você segura o SW1. Na prática é um "aperte para falar", não um mudo.

### O conserto, em uma frase

Para cada relé: mandar o **acionamento para a bobina (pino 9)**, mandar o **mic
do notebook para o contato NA (pino 10)**, **soltar o pino 1**, e **virar o
diodo**. E dar uma **ponte no SW1** para o mic passar sempre.

Depois disso: segurou SW2 → relé K1 fecha → mic do headset → notebook 1.
Soltou → mudo.

---

## 4. Achando as peças na placa

Fileira, de trás para frente (a borda com os potenciômetros/botões é a **frente**):

```
   J2  J3  J4  J5              <- conectores TRRS dos notebooks 1..4 (atrás)
   ...
   K1  K2  K3  K4              <- relés Omron G5V-1  (y ~ 184 mm)
   D2  D3  D4  D5              <- diodos 1N4148 deitados (y ~ 200 mm)
   SW1 RV5 SW2 SW3 SW4 SW5     <- botões e master, no painel frontal (y ~ 213 mm)
```

- **K1** é o relé mais à esquerda (alinhado com o J do notebook 1). Depois K2, K3, K4.
- **D2 → K1**, D3 → K2, D4 → K3, D5 → K4. O diodo fica logo **à frente** do seu relé.
- **SW1** é o primeiro botão da fileira frontal, à esquerda do potenciômetro grande (RV5).

### Pinos do Omron G5V-1 (olhando por cima, componentes virados para você)

```
        coluna A            coluna B
  fundo  [ 1 ] NF           [ 10 ] NA        <- [1] = furo quadrado no serigrafia
         [ 2 ] BOBINA       [  9 ] BOBINA
         
         [ 5 ] COM  · · · · [  6 ] COM        <- par afastado, mais para a frente
```

- Passo entre pinos: 2,54 mm na vertical, 5,08 mm entre as colunas.
- **2 e 9 = bobina** · **1 = NF** (normalmente fechado) · **10 = NA** (normalmente
  aberto) · **5 e 6 = COM** (ligados entre si).
- Desenho oficial: datasheet Omron G5V-1 (seção 12).

### Diodos D2–D5 (1N4148, corpo de vidro ~7 mm, deitado)

- A **faixa** marca o **catodo**.
- **Hoje a faixa aponta para a ESQUERDA** (para o furo que é GND).
- Depois do conserto a faixa vai apontar para a **DIREITA** (para o furo que vai
  ao relé / botão).

---

## 5. Coordenadas dos furos (para **achar**, não para medir com régua)

Valores em mm, sistema do KiCad (X cresce para a direita, Y para "baixo" =
frente da placa). **Sempre confirme cada furo com o multímetro** antes de soldar
— a serigrafia + o bip valem mais que estas coordenadas.

### Relés — furos que vamos usar

| Relé | furo **1** (acionamento: vai p/ SWn + Dn) | furo **9** (`NBx_MIC`) | furo **10** (vazio) |
|---|---|---|---|
| K1 | (73,90 ; 183,60) | (78,98 ; 186,14) | (78,98 ; 183,60) |
| K2 | (84,30 ; 183,60) | (89,38 ; 186,14) | (89,38 ; 183,60) |
| K3 | (94,70 ; 183,60) | (99,78 ; 186,14) | (99,78 ; 183,60) |
| K4 | (105,10 ; 183,60) | (110,18 ; 186,14) | (110,18 ; 183,60) |

Pino **2** (GND, **não mexer**): mesmo X do furo 1, Y = 186,14.
Pinos **5 / 6** (COM, **não mexer**): Y = 193,76.

### Diodos

| Diodo | pad da **esquerda** (GND) | pad da **direita** (vai ao relé) | para o relé |
|---|---|---|---|
| D2 | (73,50 ; 199,80) | (81,12 ; 199,80) | K1 |
| D3 | (85,72 ; 199,80) | (93,34 ; 199,80) | K2 |
| D4 | (97,94 ; 199,80) | (105,56 ; 199,80) | K3 |
| D5 | (110,16 ; 199,80) | (117,78 ; 199,80) | K4 |

### SW1 (ponte)

- Furo **A** = (73,15 ; 214,51) — `HEADSET_MIC` (vem do J6)
- Furo **B** = (71,90 ; 212,01) — vai para os COM dos relés
- São os **dois furos da esquerda** do SW1. Os dois da direita não têm cobre.

### Botões *Select* (só para conferência — **não** vamos mexer neles)

| Botão | furo com **+5 V** (frente) | furo que vai ao **relé** (trás) | comanda |
|---|---|---|---|
| SW2 | (96,81 ; 214,51) | (95,56 ; 212,01) | K1 / NB1 |
| SW3 | (109,51 ; 214,51) | (108,26 ; 212,01) | K2 / NB2 |
| SW4 | (123,79 ; 214,51) | (122,54 ; 212,01) | K3 / NB3 |
| SW5 | (135,87 ; 214,51) | (134,62 ; 212,01) | K4 / NB4 |

### Contato de mic de cada notebook (para a conferência do pino 10)

Sleeve (anel do fundo) do TRRS: **J2** = NB1 (80,70 ; 88,81) · **J3** = NB2
(93,70 ; 88,81) · **J4** = NB3 (106,70 ; 88,81) · **J5** = NB4 (119,70 ; 88,81).

---

## 6. Fase 0 — Preparação

1. Tire a placa da caixa, desligue **tudo** (sem USB conectado).
2. **Fotografe** os relés e os diodos antes de mexer (para conferir a faixa do
   diodo depois).
3. Prenda a placa na terceira mão / morsa, com boa luz.
4. Estanhe a ponta do ferro e tenha a malha/sugador à mão.
5. **Regra de ouro:** faça o **K1 + D2 inteiros**, rode o teste da seção 9 no
   notebook 1, e **só então** repita em K2/K3/K4.

---

## 7. Fase 1 — Ponte no SW1 (tira o "segura o mute")

O SW1 tem 4 furos; **só os 2 da esquerda têm trilha**. Ligue esses 2
permanentemente:

1. Passe um tiquinho de fluxo nos furos A (73,15 ; 214,51) e B (71,90 ; 212,01).
2. Ou pingue solda até unir os dois, ou solde um pedacinho de fio de ~3 mm
   entre eles. O **corpo do botão pode ficar** no lugar.
3. **Confira (multímetro, continuidade):**
   - furo A do SW1 ↔ **pino 5 de qualquer relé** → deve **apitar**.
   - furo A do SW1 ↔ sleeve do **J6** (headset) → deve **apitar**.

Resultado: o mic do headset chega **sempre** aos COM dos relés. O "mudo" passa a
ser *nenhum botão Select apertado*.

---

## 8. Fase 2 — Reparar cada relé (comece pelo K1)

Faça na ordem: **K1 → K2 → K3 → K4**. Para cada um, D**n** é o diodo dele
(D2↔K1, D3↔K2, D4↔K3, D5↔K4).

### 8.1 Levantar os pinos 1, 9 e 10 do relé

Um pino de cada vez:

1. Fluxo no pino.
2. Encoste o ferro no pino **pelo lado de baixo** (lado da solda) e, com a
   pinça por cima, **puxe o pino ~1,5 mm para fora** assim que a solda derreter.
3. O pino tem que **sair do furo e não encostar mais no anel de cobre**.
4. Se sobrar solda tampando o furo, limpe com a malha (você vai precisar do
   furo **1** e do furo **9** abertos).
5. **NÃO** toque nos pinos **2, 5, 6** nem nas duas **abas metálicas** de
   fixação — o relé continua preso e alinhado por elas.

> Se o pino não subir fácil: **pare**, ponha mais fluxo, reaqueça, tire a solda
> com a malha e tente de novo. Forçar **arranca o anel de cobre**.

### 8.2 Jumper A — pino **9** (levantado) → furo **1**

- ~6 mm de fio AWG 30. Descasque ~2 mm de cada ponta, estanhe as pontas.
- Uma ponta no **pino 9** levantado; a outra **dentro do furo 1** (que ficou
  vazio e ainda está ligado ao botão SW*n* + D*n*).
- Agora a **bobina** recebe o +5 V quando você aperta o botão.

### 8.3 Jumper B — pino **10** (levantado) → furo **9**

- ~3 mm de fio (os dois ficam na mesma coluna, quase encostados).
- Pino **10** → **dentro do furo 9** (vazio, ainda ligado à trilha `NBx_MIC`).
- Agora o **contato NA** leva o mic ao notebook quando o relé fecha.

### 8.4 Isolar o pino **1**

- Deixe o pino 1 levantado e **sem nada ligado**.
- Cubra a ponta com um pedacinho de termo-retrátil ou uma dobra de fita Kapton,
  para não encostar em nada.

### 8.5 Virar o diodo D*n*

1. Dessolde as **duas** pernas e tire o diodo.
2. Gire **180°** e recoloque: a **faixa (catodo) agora aponta para a DIREITA**,
   ou seja, para o pad que vai ao relé/botão — e **para longe** do pad de GND.
3. Solde as duas pernas, corte as sobras.

**Por quê:** depois do conserto, quando você aperta o botão, o furo 1 (e o pad
direito do diodo) fica em **+5 V**. Com o diodo **como está hoje** ele conduziria
+5 V direto para o GND = **curto**. Virado, ele fica **bloqueado** no uso normal
e só conduz o "pico" da bobina quando você **solta** o botão — que é a função de
roda-livre (flyback), protegendo o contato do botão.

### 8.6 Conferência do relé (multímetro, **placa sem alimentação**)

| Medir | Esperado |
|---|---|
| pino **9** ↔ furo de trás do **SW*n*** (o que vai ao relé) | **apita** (continuidade) |
| pino **9** ↔ pino **2** | ~**140–180 Ω** (é a bobina; num bipador com limiar baixo **não** apita) |
| pino **10** ↔ **sleeve do TRRS** daquele notebook (J2/J3/J4/J5) | **apita** |
| pino **10** ↔ pino **5** ou **6** | **não apita** (contato NA aberto com relé desligado) |
| pino **1** ↔ qualquer coisa | **não apita** (isolado) |
| pino **2** ↔ GND | **apita** |
| **Teste de diodo**: ponta **vermelha** no pad **esquerdo (GND)** do D*n*, **preta** no pad **direito** | ~**0,55–0,70 V** (conduz) |
| Teste de diodo invertido (vermelha na direita) | **OL / aberto** |

### 8.7 Repetir em K2 (D3), K3 (D4), K4 (D5)

Mesmíssimos passos, só mudam as coordenadas (seção 5). Faça só depois que o K1
passar no teste funcional (seção 9).

---

## 9. Fase 3 — Teste funcional

1. Ligue a placa pela **USB-C**. Headset **com microfone** no **J6**.
2. Meça: **+5V_AUDIO ≈ 5 V** no TP1.
3. No **notebook 1**, abra o **Gravador de Voz** (ou Meet / Zoom "testar mic")
   e selecione o headset como entrada.
4. **Segure o SW2.** Você deve **ouvir o "clique" do K1** e o notebook 1 deve
   **captar sua voz**. Solte o SW2 → o mic **para**.
5. Confirme que o **notebook 1 reconhece o mic do headset** (aparece como
   dispositivo de entrada, não some / não fica "sem sinal"). Isso prova que a
   bobina não está mais carregando a linha.
6. Repita: **SW3 → notebook 2**, **SW4 → notebook 3**, **SW5 → notebook 4**.
7. **Nenhum botão apertado** → nenhum notebook capta (mudo). ✔
8. Apertar **dois** botões ao mesmo tempo → **dois** notebooks recebem o mic.
   Isso é **esperado** (não há intertravamento). Para resolver, ver seção 11.

Passou nos itens 4–7 no K1? Faça K2/K3/K4 e repita 4–7 em cada notebook.

---

## 10. Fase 4 — Acabamento

1. Limpe **todo o fluxo** com álcool isopropílico + escova. Fluxo velho conduz
   e dá "mic fantasma".
2. Confira sob lupa: **nenhum respingo** ligando trilhas, nenhuma "barba" de
   solda.
3. Uma gota de **cola quente** ancorando os jumpers de cada relé e o pino 1
   isolado (evita que vibrem e quebrem).
4. Preencha o checklist (seção 13).

### Se não funcionar

| Sintoma | Provável causa | O que checar |
|---|---|---|
| K*n* clica, mas o notebook não capta | Jumper B frio, ou no furo errado | continuidade pino 10 ↔ sleeve do TRRS daquele notebook |
| K*n* não clica | Jumper A frio; diodo ainda invertido (curto); botão não fecha | segure o botão e meça: pino 9 recebe +5 V? pino 2 = GND? |
| Notebook capta mesmo sem botão | pino 1 não isolado; ponte do SW1 encostando em algo | pino 1 ↔ tudo = sem apito; revisar a ponte |
| Mic ainda fraco no notebook | bobina ainda carregando a linha | pino 9 **realmente** fora do furo, sem tocar o anel; furo 9 só com o jumper B |
| Chiado / ruído de fundo | fluxo não limpo; jumper AWG30 sem isolação passando perto de trilha de áudio | limpar com IPA; reposicionar/encurtar o fio |

---

## 11. Depois: acabar com o "segurar botão" (opcional, barato)

O conserto acima mantém os botões **momentâneos**. Para não ter que segurar,
sem eletrônica:

- **1 chave rotativa 1 polo × 5 posições** (OFF / NB1 / NB2 / NB3 / NB4):
  comum → +5 V (furo da frente do SW2, ou TP1); cada posição → o **furo de
  trás** de SW2…SW5. OFF já é o mudo. Detalhes em **`REWORK-001 §D.3`**.
  Custo: ~R$ 5–15, 1 peça, e ainda força "um notebook de cada vez".

Para seleção estilo **KVM** (aperta NB2 → NB1 desarma sozinho) mantendo botões:
placa auxiliar **CD4043 + matriz de diodos** — **`docs/Architecture/SCH-010-OneHotMicSelector.md`**
(mais caro/complexo; é a última opção).

E os **potenciômetros** invertidos: **`REWORK-001` Parte B** (levantar pinos
1, 3, 4, 6 e cruzar 1↔3 e 4↔6).

Para o **respin** (novo lote de PCB já correto): `REWORK-002`.

---

## 12. Referências reais (fotos, datasheets, técnica)

- **Omron G5V-1 — datasheet oficial (desenho dos terminais / pinagem PCB):**
  <https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v_1.pdf> ·
  <https://components.omron.com/us-en/products/relays/G5V-1>
- **1N4148 — identificar a faixa do catodo:**
  SparkFun, *Discrete Semiconductor Kit Identification Guide — Diodes*
  <https://learn.sparkfun.com/tutorials/discrete-semiconductor-kit-identification-guide/diodes> ·
  datasheet: <https://www.diodes.com/assets/Datasheets/ds12019.pdf>
- **Levantar pino / rework de furo passante:**
  AllPCB, *Through-Hole Component Replacement — A Detailed Guide for Beginners*
  <https://www.allpcb.com/blog/pcb-manufacturing/through-hole-component-replacement-a-detailed-guide-for-beginners.html>
- **Soldar fio de jumper / "bodge wire" (AWG30 Kynar):**
  SparkFun, *How to Work with Jumper Pads and PCB Traces*
  <https://learn.sparkfun.com/tutorials/how-to-work-with-jumper-pads-and-pcb-traces/all> ·
  Chemtronics, *PCB Trace Repair With a Wire Jumper*
  <https://www.chemtronics.com/how-to-pcb-trace-repair-with-a-wire-jumper> ·
  vídeo: *Bodging PCBs to Fix Mistakes with Magnet Wire* <https://www.youtube.com/watch?v=8Iroei0a1lY>
- **Guia visual deste rework (artefato HTML):**
  <https://claude.ai/code/artifact/b2020ecc-38f1-42e4-a727-40a2e051e617>

---

## 13. Checklist por placa

```
Placa nº ____   data ____

FASE 1
[ ] ponte no SW1 (furos A e B)
[ ] confere: SW1-A <-> pino 5 de um relé apita
[ ] confere: SW1-A <-> sleeve do J6 apita

FASE 2 — por relé (marcar cada coluna)                K1   K2   K3   K4
[ ] pinos 1, 9, 10 levantados (fora do cobre)         [ ]  [ ]  [ ]  [ ]
[ ] jumper A: pino 9 -> furo 1                         [ ]  [ ]  [ ]  [ ]
[ ] jumper B: pino 10 -> furo 9                        [ ]  [ ]  [ ]  [ ]
[ ] pino 1 isolado (kapton/termo)                      [ ]  [ ]  [ ]  [ ]
[ ] diodo Dn virado (faixa p/ a direita)               [ ]  [ ]  [ ]  [ ]
[ ] conferencia 8.6 OK                                 [ ]  [ ]  [ ]  [ ]

FASE 3 — teste
[ ] +5V no TP1 ~ 5 V
[ ] segura SW2 -> K1 clica -> NB1 capta o mic; solta -> para
[ ] segura SW3 -> NB2 capta
[ ] segura SW4 -> NB3 capta
[ ] segura SW5 -> NB4 capta
[ ] nada apertado -> mudo
[ ] cada notebook reconhece o mic do headset

FASE 4
[ ] fluxo limpo com IPA
[ ] sem respingos (conferido na lupa)
[ ] jumpers e pino 1 ancorados com cola quente
```

---

## 14. Resumo das ligações (antes → depois)

Por relé K*n* (n = 1..4):

| Furo / pino | Antes (fabricado) | Depois (Opção 2) |
|---|---|---|
| pino 2 | GND | GND *(igual)* |
| pino 9 | `NBx_MIC` | **acionamento** (via jumper A ao furo 1) |
| pino 10 | — | **`NBx_MIC`** (via jumper B ao furo 9) |
| pino 1 | acionamento (SW*n* + D*n*) | **isolado** |
| pinos 5/6 | mic do headset (via SW1) | mic do headset *(igual; SW1 agora em ponte)* |
| D*n* | faixa → esquerda (GND) | **faixa → direita** (roda-livre da bobina) |
| SW1 | momentâneo em série | **em ponte** (mic passa sempre) |
| SW2–SW5 | momentâneos | **momentâneos** *(não mexer — "aperte para falar")* |
