# REWORK-002 — Re-roteamento do PCB no KiCad

Versão: 1.0 · Data: 2026-08-28
Complementa `REWORK-001` (que é o conserto manual das placas já fabricadas).
Este documento é para gerar **gerbers corrigidos** para um novo lote.

---

## 0. Estado atual do arquivo

O `MeetingHub-4-v1.kicad_pcb` **já foi todo pré-preparado** por script — inclusive
o "F8" e a limpeza de duplicados. O que já está feito:

- **Bug latente do repo corrigido:** 14 footprints (RV1–RV5, C1, C4, C21, D1,
  SW2–SW5) nunca tiveram link com o esquemático → qualquer *Update PCB from
  Schematic* duplicava eles. Agora todos têm `path` correto; só MH1–MH4 e TP2
  ficam sem link (não têm símbolo, é normal).
- Redes dos pads reatribuídas ao esquemático corrigido (RV1–RV5 pinos 1/3/4/6;
  K1–K4 pinos 1/9/10; D2–D5 pinos 1/2; SW2–SW5).
- **SW1 removido** da placa; `Net-(SW1-B)` fundida em `HEADSET_MIC` (+ um jumper
  curto no lugar do antigo SW1).
- **SW2–SW5** trocados para `SW_PushLock_PS-22F03` e postos na fileira frontal
  (x≈88/107/126/145, y≈213, rot 180). **Posição é aproximada** — ajuste fino é
  o GRUPO F.
- Trilhas antigas em rede errada / órfãs **apagadas** (pot row, relés, chaves).
- Zonas **não** repreenchidas → aperte `B` no KiCad.
- Sem footprints duplicados, sem footprint fora da placa.

Ao abrir no Pcbnew: **~42 linhas de ratsnest**, nas regiões da fileira RV1–RV4
(+RV5) e relés/diodos/chaves. O resto da placa intacto.

> **Não** precisa mais rodar o F8 — já foi feito por script. Se rodar mesmo
> assim, deve ser quase um no-op (no máximo renomeia alguma rede local tipo
> `Net-(D2-A)`→`Net-(D2-K)`). Para começar do zero: `git checkout` o `.kicad_pcb`
> e o `.pretty/SW_PushLock_PS-22F03.kicad_mod` — mas aí você reencontra o bug
> dos duplicados.

---

## 1. Preparação (2 min)

1. Abra `MeetingHub-4-v1.kicad_pro` no KiCad, abra o Pcbnew. `B` para repreencher
   zonas.
2. (Opcional) **Tools → Update PCB from Schematic (F8)** só para conferir —
   deve dizer "no changes" ou quase. Se listar "Add footprint SWx" ou
   duplicados, **cancele** e me avise (algo saiu do lugar).
3. Ative a exibição de ratsnest e o DRC em tempo real.
3. Ative a exibição de ratsnest (ícone "show ratsnest" na barra lateral direita).
4. Regras de trilha: use as mesmas larguras já usadas na placa
   (**Inspect → Net Inspector** mostra; provavelmente 0,25 mm sinal / 0,3–0,4 mm
   VBIAS). Vias: as default do projeto.
5. Deixe o **DRC em tempo real** ligado (Route → menu, ou o padrão do KiCad 7).

Faça na ordem abaixo. Depois de cada grupo, `B` para repreencher zonas e
confira o ratsnest sumindo.

---

## 2. GRUPO A — Sinais dos potenciômetros (10 trilhas)

O cursor (pino 2 / pino 5) fica **entre** os dois pinos de ponta, então a
trilha de sinal precisa contornar o pino do cursor. São desvios curtos (~7 mm).

Cada capacitor de entrada `Cx` já tem trilha chegando a ~1 mm do **pino 1/4
antigo**; leve essa ponta para o **pino 3/6**:

| Ligar | de (trilha existente termina em ~) | até o pino | camada sugerida |
|---|---|---|---|
| C5.2 → **RV1.3** | (75,4 , 161,6) | RV1 pino 3 (74,3 , 167,6) | B.Cu |
| C6.2 → **RV1.6** | trilha vem do norte p/ RV1 pino 4 | RV1 pino 6 (76,8 , 167,6) | B.Cu |
| C7.2 → **RV2.3** | ~(94,6 , 162,6) | RV2 pino 3 (94,6 , 167,6) | B.Cu |
| C8.2 → **RV2.6** | ~(97,1 , 162,6) | RV2 pino 6 (97,1 , 167,6) | B.Cu |
| C9.2 → **RV3.3** | ~(114,9 , 162,6) F.Cu | RV3 pino 3 (114,9 , 167,6) | F.Cu |
| C10.2 → **RV3.6** | ~(117,4 , 162,6) F.Cu | RV3 pino 6 (117,4 , 167,6) | F.Cu |
| C11.2 → **RV4.3** | ~(121,8 , 149,1) F.Cu | RV4 pino 3 (135,3 , 167,6) | F.Cu |
| C12.2 → **RV4.6** | ~(118,6 , 143,5) F.Cu | RV4 pino 6 (137,8 , 167,6) | F.Cu |
| C13.2 → **RV5.3** | ~(117,0 , 142,6) | RV5 pino 3 (162,5 , 213,5) | B.Cu |
| C14.2 → **RV5.6** | ~(108,5 , 141,5) | RV5 pino 6 (162,5 , 211,0) | B.Cu |

**Como desviar do cursor:** saia da ponta da trilha, ande ~1,3 mm para o lado de
fora da coluna de pinos (afastando de x do pino 2/5), desça passando o pino do
cursor, e entre no pino 3/6. Se a camada estiver congestionada, um via + hop
pela outra camada resolve.

---

## 3. GRUPO B — VBIAS para os potenciômetros (~11 trilhas)

Agora os pinos **1 e 4** de RV1–RV5 precisam de VBIAS. A rede VBIAS
(fonte: divisor R1/R2 + C3, e os pinos + dos amp-ops) **está intacta**.

**Recomendado — criar um barramento novo na fileira y ≈ 162,6** (que agora está
livre de sinal):

1. Dentro de cada pot, ligue **pino 1 ↔ pino 4** (2,5 mm, reto): RV1, RV2, RV3,
   RV4.
2. Ligue os pots entre si nessa fileira: RV1.4 → RV2.1 → RV2.4 → RV3.1 →
   RV3.4 → RV4.1 (trechos de ~15–18 mm em F.Cu ou B.Cu, ao longo de y≈162,3,
   logo acima dos furos).
3. **Um alimentador** desse barramento até a fonte de VBIAS: o ponto mais
   perto é **C3 pino 1 (118,5 , 127,3)** ou a trilha VBIAS em F.Cu por volta de
   (115,2 , 127,3). Roteie descendo entre os capacitores C7–C10 até o
   barramento (caminho parecido com o do alimentador antigo, que descia por
   ali). ~35 mm.
4. **RV5** (pino 1 e 4, lá no painel frontal): ligue RV5.1 ↔ RV5.4 (2,5 mm) e
   puxe um ramo de VBIAS até lá. Opções de origem:
   - da trilha VBIAS em F.Cu perto de (170 , 122,9), descendo pela borda
     direita; **ou**
   - do barramento novo em RV4.4, contornando por baixo (y ≈ 205, mesma faixa
     de SW/RV5). Cuidado com o trunk `HEADSET_MIC` que corre a largura toda em
     y ≈ 209,5 — passe por baixo dele com via se precisar.

Confira no fim: `pino 1` e `pino 4` de todos os RV com continuidade até C3
pino 1.

---

## 4. GRUPO C — Acionamento dos relés `Net-(Dx-A)` (4 redes)

Cada rede tem 3 pads: **Kx.9** (bobina, lado do +5V), **Dx.1** (catodo do
diodo), **SWx.2** (chave "Select"). Hoje: Dx e Kx.9 isolados; SWx.2 tem um
coto que sobrou apontando para o lugar errado (perto de Dx pino 2).

Por relé (K1/D2/SW2; repita K2/D3/SW3, K3/D4/SW4, K4/D5/SW5):

1. **Apague** qualquer coto solto de `Net-(Dx-A)` que tenha ficado perto do
   **pino 2 do diodo** (ele é GND agora).
2. Trilha nova **Kx.9 → Dx.1**:
   - K1.9 (79,0 , 186,1) → D2.1 (73,5 , 199,8). B.Cu, ~14 mm, área livre.
   - K2.9 (89,4 , 186,1) → D3.1 (85,7 , 199,8).
   - K3.9 (99,8 , 186,1) → D4.1 (97,9 , 199,8).
   - K4.9 (110,2 , 186,1) → D5.1 (110,2 , 199,8).
3. Trilha **Dx.1 → SWx.2** (ou SWx.2 → Kx.9; qualquer topologia que una os 3):
   - SW2.2 (95,6 , 212,0) já tem trilha descendo até ~(95,5 , 207) / (82,2 ,
     199,8). Leve essa ponta até **D2.1 (73,5 , 199,8)** (passando por baixo
     do corpo do diodo, ou por F.Cu ao longo de y ≈ 205 e sobe).
   - Idem para SW3–SW5.

> Observação: `Dx.1` é agora o **catodo** (faixa) do diodo. Na montagem do novo
> lote o diodo já entra na orientação certa pelo símbolo corrigido — nada a
> fazer aqui além de rotear.

---

## 5. GRUPO D — GND dos diodos `Dx.2` (4 vias)

`D2.2 / D3.2 / D4.2 / D5.2` são **GND** agora. Cada um precisa alcançar a zona
GND (camada interna In1.Cu):

- Coloque **um via em cima (ou colado) do pino 2** de cada diodo. A zona GND
  faz a conexão térmica sozinha quando você repreenche (`B`).
- Alternativa: trilha curta do pino 2 até um via/pad GND vizinho.

---

## 6. GRUPO E — `NBx_MIC` para o contato NA dos relés (4 trilhas)

A linha de microfone de cada notebook agora vai no **pino 10** do relé (era o
pino 9).

A trilha `NBx_MIC` que vinha do conector TRRS já chega perto do relé (terminava
no antigo pino 9). Leve a ponta dela para o **pino 10**:

| Ligar | ponta da trilha existente ~ | até | obs |
|---|---|---|---|
| J2.S → **K1.10** | (72,1 , 179,2) B.Cu | K1 pino 10 (79,0 , 183,6) | contornar pinos 1/2 do K1 |
| J3.S → **K2.10** | perto de K2 | K2 pino 10 (89,4 , 183,6) | |
| J4.S → **K3.10** | (93,4 , 179,8) B.Cu | K3 pino 10 (99,8 , 183,6) | |
| J5.S → **K4.10** | perto de K4 | K4 pino 10 (110,2 , 183,6) | |

Pino 9 e pino 10 são vizinhos (2,54 mm na mesma coluna), então é literalmente
mover a ponta um furo para cima.

---

## 6b. GRUPO F — Chaves (SW1 removido, SW2–SW5 já trocadas)

Decisão do projeto ajustado: **botões com retenção** (push-on/push-off) e
**sem botão de MUTE separado** (sem seletora travada → todos os relés desligados
→ mic mudo).

**Já feito por script:** SW1 apagado; `Net-(SW1-B)` fundida em `HEADSET_MIC`
(+ jumper curto no lugar); SW2–SW5 trocadas para `SW_PushLock_PS-22F03`,
colocadas em x≈88/107/126/145 y≈213 rot 180, com as redes certas
(`SWx.1`→+5V_AUDIO, `SWx.2`→`Net-(Dx-K)`).

**Falta você fazer:**

1. **Posição final da fileira frontal.** A posição atual das 4 chaves é
   aproximada e pode encostar no courtyard dos diodos D2–D5 / do MH3 / do RV5.
   Reposicione `SW2 SW3 SW4 SW5` (e confira `RV5`) com folga real entre
   courtyards, atuadores para a borda frontal (+Y), ≥10 mm livres à frente de
   cada atuador (capa + curso de 2,5 mm). Espaço útil: x ≈ 76 (à direita do
   MH3) até ≈ 152 (à esquerda do RV5).

2. **Rotear cada chave (2 redes):**
   - `SWx.1` → **+5V_AUDIO** — um via no pad 1 pega a zona In2.Cu, ou trilha
     curta ao barramento +5V.
   - `SWx.2` → **`Net-(Dx-K)`** — mesma rede do GRUPO C (`SWx.2` ↔ `Kx.9` ↔
     `Dx.1`); a ponta mais perto costuma ser o `Dx.1`.

3. **Confira `HEADSET_MIC`**: de J6 deve chegar aos 4 COM dos relés (pinos 5/6).
   O jumper que o script colocou no lugar do SW1 (B.Cu, ~(73,71)) fecha o vão;
   se o *highlight net* mostrar o barramento partido, roteie o trecho que faltar.

4. **Footprint `SW_PushLock_PS-22F03` é RASCUNHO.** Antes de gerar gerbers:
   - conferir dimensões do corpo/atuador no datasheet **C2848947** (G-Switch
     PS-22F03NC) — ajustar `F.Fab`/`F.CrtYd` se necessário;
   - **confirmar qual pino é COM e qual é NO** (assumi pad 1 = COM, pad 2 = NO,
     fecha quando travado). Se o datasheet disser outra posição, mover os
     pads "1"/"2"/"" (mecânico) no footprint.
   - Se, no protótipo, a seletora "seleciona quando solta" em vez de "quando
     apertada", é porque peguei NC no lugar de NO → trocar pad 2 de furo.

5. **Enclosure**: os furos do painel frontal passam de ~6 mm (tátil) para
   ~9,5 mm + rasgo do atuador da PS-22F03, e some 1 furo (SW1). Atualizar o
   modelo OpenSCAD / plano de corte do acrílico.

---

## 6c. O que o DRC mostra AGORA (antes de rotear)

Rodando o DRC no estado pré-preparado dá ~130 avisos. É esperado — quase tudo
some sozinho:

| Categoria | Qtd | O que é | Ação |
|---|---|---|---|
| `unconnected_items` | ~33 | **o ratsnest** — nets ainda não roteadas | rotear (GRUPOS A–F) |
| `track_dangling` | ~17 | pontas de trilha esperando ligação | somem ao rotear |
| `lib_footprint_issues` | ~70 | artefato de caminho de biblioteca local | **ignorar** (some no KiCad instalado; ver HANDOFF) |
| `silk_over_copper` | ~34 | silk sobre pad em J2–J6 / D3–D5 | **ignorar** (pré-existente, cosmético) |
| `silk_edge_clearance` | 6 | texto de referência de SW2–SW5 perto da borda | some ao reposicionar as chaves (GRUPO F pt.1) |
| `via_dangling` | 1 | via de VBIAS do RV5 sobrou | liga ao rotear RV5 (GRUPO B) ou apague |

**Não há violação de `clearance` nem `hole_clearance` de verdade** — se aparecer
alguma, é zona desatualizada: aperte **`B`**.

## 7. Fechamento

1. `B` — repreencher todas as zonas (já vem preenchido, mas confirme).
2. **Inspect → Design Rules Checker** → *Run DRC*. Meta: **0 `unconnected_items`
   e 0 `track_dangling`** (ignore `lib_footprint_issues` / `silk_over_copper`).
   - Se sobrar "unconnected items", falta rotear algo — o DRC lista qual pad.
3. Confira visualmente cada RV e cada K com a ferramenta de *highlight net*
   (clique numa trilha → realça a rede toda): VBIAS nos pinos 1/4 dos pots,
   sinal nos 3/6; nos relés, bobina 2–9, COM 5/6, `NBx_MIC` no 10, pino 1 solto.
4. **File → Fabrication Outputs → Gerbers** + **Drill Files** (ou
   `kicad-cli pcb export gerbers` / `drill` — ver `production/PCBWay-OrderGuide.md`).
5. Zipar, atualizar `hardware/Gerbers/` e o guia de pedido, e submeter cotação.

---

## 8. Checklist

```
[ ] B (repreencher zonas) ao abrir
[ ] (opcional) F8 confere "no changes" — se listar Add/duplicados, PARAR
[ ] DRC: só sobra unconnected_items + track_dangling + cosméticos (esperado)
GRUPO A - sinais dos pots
[ ] RV1.3←C5  [ ] RV1.6←C6  [ ] RV2.3←C7  [ ] RV2.6←C8
[ ] RV3.3←C9  [ ] RV3.6←C10 [ ] RV4.3←C11 [ ] RV4.6←C12
[ ] RV5.3←C13 [ ] RV5.6←C14
GRUPO B - VBIAS
[ ] pino1↔pino4 em RV1,RV2,RV3,RV4,RV5
[ ] barramento y≈162 unindo RV1..RV4
[ ] alimentador do barramento até C3.1
[ ] ramo VBIAS até RV5
GRUPO C - acionamento relés
[ ] K1.9-D2.1-SW2.2   [ ] K2.9-D3.1-SW3.2
[ ] K3.9-D4.1-SW4.2   [ ] K4.9-D5.1-SW5.2
GRUPO D - GND diodos
[ ] via GND em D2.2 D3.2 D4.2 D5.2
GRUPO E - NBx_MIC
[ ] J2.S→K1.10  [ ] J3.S→K2.10  [ ] J4.S→K3.10  [ ] J5.S→K4.10
GRUPO F - chaves (SW1 removido + SW2-5 trocadas já feito por script)
[ ] fileira frontal reposicionada (RV5 + SW2..SW5), folga de courtyard OK
[ ] SWx.1→+5V, SWx.2→Net-(Dx-K) roteados
[ ] HEADSET_MIC de J6 chega aos 4 COM (highlight net)
[ ] footprint PS-22F03 conferido vs datasheet C2848947 (dims + COM/NO)
[ ] enclosure: furos do painel atualizados
FECHAMENTO
[ ] B (zonas)   [ ] DRC 0 erros   [ ] highlight-net conferido
[ ] gerbers + drill regenerados e zipados
```
