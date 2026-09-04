# MeetingHub-4 v2 — compra dos componentes no Brasil + placa nua importada

Data: 2026-09-03 · preços **aproximados** de set/2026, confira no link antes de comprar · câmbio usado: US$ 1 ≈ R$ 5,40

> **Objetivo:** decidir se compensa importar só a **placa nua** (barata, leve, imposto
> baixo) e comprar os **componentes no Brasil**, em vez de pagar a placa montada pela
> JLCPCB (US$ 108 + US$ 87 frete + ~104 % imposto ≈ **US$ 398 / ~R$ 2.150** por lote de 5).

---

## 1. Resumo da decisão

| | Placa montada JLCPCB (5 un) | Placa nua importada + peças no Brasil |
|---|---|---|
| Placa | US$ 108 | ~US$ 30–45 / 5 un (nua) |
| Frete | US$ 87 (expresso) | ~US$ 12–25 (linha econômica) |
| Imposto | ~104 % sobre (placa+frete) | ~37 % se o pedido ≤ US$ 50 (Remessa Conforme); ~92 % acima |
| Componentes | inclusos | **~R$ 180–260 por placa** (ver tabela) |
| Montagem | pronta | você solda, ou ~R$ 100–150 com um técnico |
| **Custo por 1 placa funcionando** | ~R$ 430 | **~R$ 450–650** |
| **Custo pelas 5 placas** | ~R$ 2.150 | **~R$ 1.400–1.900** + solda |

**Conclusão:** compensa **se você for montar as 5** (ou pelo menos 3), ou se você mesmo
solda. Para **1 placa só** o ganho é pequeno, porque a JLCPCB obriga a comprar 5 placas
nuas e o frete/imposto é fixo. O maior risco **não é preço, é footprint** (item 3).

---

## 2. Tabela de componentes — onde comprar no Brasil

Designadores conforme [`BOM-PCBA-MeetingHub-4-v2.csv`](../hardware/BOM/BOM-PCBA-MeetingHub-4-v2.csv).
Preço = **por placa** (1 unidade de cada valor). "Comprar em quantidade" (kit) quase sempre sai mais barato.

### 2.1 Circuitos integrados

| Ref | Peça | Qtd | Onde comprar | Preço aprox. (un) | Linha |
|---|---|---|---|---|---|
| U1 | NJM4580DD (op-amp áudio, DIP-8) | 1 | [Toni Eletrônica](https://tonieletronica.com/ci-njm4580dd-amplificador-operacional-jrc-4580dd-dip-8/) · [Mercado Livre](https://lista.mercadolivre.com.br/njm4580) | R$ 6–12 | R$ 9 |
| U2 | NJM4556AD (op-amp alta corrente, DIP-8) | 1 | [Mercado Livre "NJM4556"](https://eletronicos.mercadolivre.com.br/ci-njm4556-jrc-amplificador-operacional) — **conferir se é DIP-8**, a maioria é SIP-8 | R$ 15–35 | R$ 25 |
| U3 | LM358P (op-amp, DIP-8) | 1 | [SmartProjects](https://www.smartprojectsbrasil.com.br/circuito-integrado-amplificador-operacional-lm358) · [Mercado Livre](https://lista.mercadolivre.com.br/lm358) | R$ 1–3 | R$ 2 |
| U4 | CD4043BE (quad latch NOR, DIP-16) | 1 | [Achei Componentes](https://www.acheicomponentes.com.br/circuito-integrado-cd4043be-dip-16-texas) · [Proesi](https://www.proesi.com.br/cd4043-circuito-integrado-dip-16) · [Mercado Livre](https://produto.mercadolivre.com.br/MLB-1580401361-1-peca-circuito-integrado-cd4043be-dip-16-cd4043-_JM) | R$ 3–7 | R$ 5 |
| — | Soquete DIP-8 (3×) + DIP-16 (1×) — recomendado | 4 | Baú da Eletrônica / SmartProjects / Mercado Livre | R$ 0,50–1 | R$ 3 |

> **U2 é o ponto de atenção dos CIs:** o NJM4556A**D** (DIP-8) é raro no varejo BR; o que
> se acha é o NJM4556A**L** (SIP-8), footprint diferente. Se não achar o DIP, importe
> este junto com a placa (item 4) ou troque por 2× NJM4580 em paralelo (exige revisão do circuito).

### 2.2 Potenciômetros e chaves

| Ref | Peça | Qtd | Onde comprar | Preço aprox. (un) | Linha |
|---|---|---|---|---|---|
| RV1–RV5 | Pot. duplo 10 k **log (A10K)**, PCI horizontal tipo RK09 | 5 | [Casa do Resistor "mini duplo A10K L15 PCI"](https://www.casadoresistor.com.br/potenciometro-logaritmico-mini-duplo-a-10k-l15-estriado-o16mm-pci) · [Duque Eletrônica](https://www.duqueeletronica.com.br/produto/potenciometro-10ka-l15-a10k-duplo-schave-6t-180o-stereo-logaritmo-006972-0103hd781o) · [Mercado Livre](https://lista.mercadolivre.com.br/potenciometro-duplo-10k-10k-log) | R$ 4–9 | R$ 30 (5×) |
| SW2–SW5 | Chave tátil 6 mm **90° / horizontal**, 4 term. | 4 | [Baú da Eletrônica KFC-A06-W6](https://www.baudaeletronica.com.br/produto/chave-tactil-kfc-a06-w6-6mm-4-terminais-90-graus.html) · [Soldafria](https://www.soldafria.com.br/chave-tactil-kfc-a06-w6-6mm-4-terminais-90-graus-p-4456.html) | R$ 0,50–1,50 | R$ 4 (4×) |

> Verificar footprint (item 3). O pot v2 é **Alps RK097 horizontal**; o "mini duplo L15
> PCI" nacional costuma ser compatível com o footprint RK09, mas **confira o passo dos
> pinos** contra o desenho no KiCad.

### 2.3 Relés, conectores, semicondutores de potência

| Ref | Peça | Qtd | Onde comprar | Preço aprox. (un) | Linha |
|---|---|---|---|---|---|
| K1–K4 | Relé de sinal **Omron G5V-1 5 VDC SPDT** | 4 | [Ecotron Componentes](https://www.ecotroncomponentes.com.br/automacao/reles/rele-5vdc-g5v-1-dc5-omron-g5v1dc5) · [DigiKey Brasil](https://www.digikey.com.br/pt/products/detail/omron-electronics-inc-emc-div/G5V-1-T90-DC12/6650356) | R$ 9–14 | R$ 45 (4×) |
| J2–J6 | Jack P2 3,5 mm **4 polos (TRRS)** fêmea PCI | 5 | [SmartProjects "P2 estéreo 4 term. placa"](https://www.smartprojectsbrasil.com.br/conector-jack-p2-estereo-femea-aberto-4-terminais-para-placa) · [Mercado Livre "jack P2 4 polos"](https://lista.mercadolivre.com.br/jack-p2-4-polos) | R$ 1,50–4 | R$ 15 (5×) |
| J1 | Conector **USB-C fêmea PCI** (compatível c/ footprint GCT USB4085) | 1 | [Mamute SMD 24 pinos 180°](https://www.mamuteeletronica.com.br/conector-usb-tipo-c-3-1-femea-24-pinos-smd-smt-180-graus-22746) · [Mercado Livre](https://lista.mercadolivre.com.br/conector-usb-c-femea) | R$ 3–10 | R$ 8 |
| Q1–Q4 | 2N7000 (MOSFET TO-92) | 4 | [Mercado Livre](https://lista.mercadolivre.com.br/2n7000) · Baú da Eletrônica | R$ 0,50–1 | R$ 3 (4×) |
| D1 | P6KE6.8A (TVS 6,8 V, DO-15) | 1 | [Mercado Livre "P6KE 6.8"](https://lista.mercadolivre.com.br/diodo-p6ke-6.8) · Mixtrônica | R$ 1–4 | R$ 3 |
| F1 | Fusível PTC resetável **500 mA radial THT** (MF-R050) | 1 | [Loja da Fábrica de Bolso](https://loja.fabricadebolso.com.br/produto/fusivel-auto-restauravel-self-restoring-fuse-500maptc-reset-fuse.html) · Mercado Livre | R$ 1–4 | R$ 3 |

> **J1 (USB-C) é o segundo ponto de atenção:** o v2 usa o footprint do GCT USB4085
> (recept. 16 pinos, power-only). Os conectores "2 pinos para alimentação" nacionais
> **não** encaixam. Ou usa um USB-C 16/24 pinos com o mesmo padrão, ou importa o GCT
> junto com a placa (item 4).

### 2.4 Resistores 1/4 W (axial THT) e capacitores

| Ref | Valor | Qtd | Onde comprar | Linha |
|---|---|---|---|---|
| R1,R2,R5–R12 | 10 k | 10 | qualquer loja; **kit 1/4 W** (600 pç, ~R$ 30) resolve todos os valores | — |
| R3,R4 | 3k3 (metal film 1 %) | 2 | idem | — |
| R13,R17,R21–R28,R33–R37 | 100 k | 15 | idem | — |
| R14,R15,R18,R19,R29–R32 | 1 k | 8 | idem | — |
| R16,R20,R38 | 47 R (47 Ω) | 3 | idem | — |
| — | **Resistores (avulsos ou kit)** | 38 | [Baú da Eletrônica](https://www.baudaeletronica.com.br/) · [SmartProjects](https://www.smartprojectsbrasil.com.br/) · Mercado Livre | R$ 5 avulso / R$ 30 kit |
| C1,C4,C21,C22,C25 | 100 nF cerâmico 5 mm | 5 | qualquer loja | R$ 1,50 |
| C5–C15,C18,C26 | 1 µF cerâmico/poliéster 5 mm | 13 | qualquer loja | R$ 5 |
| C2,C3,C16,C19,C24 | 10 µF eletrolítico 16 V | 5 | qualquer loja | R$ 1 |
| C17,C20 | 220 µF eletrolítico 16 V | 2 | qualquer loja | R$ 1 |
| C23 | 100 µF eletrolítico 16 V | 1 | qualquer loja | R$ 0,50 |
| D2–D5,D10–D29 | 1N4148 (DO-35) | 24 | Mercado Livre / Baú (kit 100 pç ~R$ 10) | R$ 3 |

### 2.5 Total estimado dos componentes (por placa)

| Grupo | R$ / placa |
|---|---|
| CIs + soquetes | ~R$ 44 |
| Potenciômetros (5×) | ~R$ 30 |
| Chaves táteis (4×) | ~R$ 4 |
| Relés (4×) | ~R$ 45 |
| Jacks P2 (5×) + USB-C | ~R$ 23 |
| 2N7000 + TVS + PTC | ~R$ 9 |
| Resistores + capacitores + 1N4148 | ~R$ 16 |
| **Subtotal peças** | **~R$ 171** |
| Fretes (2–3 lojas × ~R$ 15–25) | ~R$ 50 |
| **Total peças, 1 placa** | **~R$ 220** |
| **Total peças, 5 placas** | **~R$ 750–900** (fretes diluídos, kits) |

Item mais caro: **relés (R$ 45)** e **pots (R$ 30)**. Juntos = 44 % do custo de peças.

---

## 3. Risco real: footprint (leia antes de comprar a placa nua)

A placa v2 foi desenhada em torno de **peças específicas da JLCPCB**. Três footprints são
**locais, feitos sob medida** — se a peça nacional tiver pinagem/passo diferente, **não encaixa**:

| Footprint no v2 | Peça original | Peça BR equivalente | Encaixa? |
|---|---|---|---|
| `Potentiometer_Alps_RK097_Dual_Horizontal` | Alps RK09712200HA | pot. duplo "mini L15 PCI" | **provável, confirmar passo dos pinos** |
| `Jack_3.5mm_PJ-3200B-4A_Horizontal` | HRO PJ-3200B-4A | jack P2 4 polos nacional | **confirmar** — pinagem T/R1/R2/S varia por fabricante |
| `USB_C_Receptacle_GCT_USB4085` | GCT USB4085 | — | **improvável** com conector "2 pinos"; precisa do GCT ou equivalente 16 pinos |
| `Relay_SPDT_Omron_G5V-1` (padrão KiCad) | Omron G5V-1 | Omron G5V-1 (mesma peça) | **sim** |
| `SW_Tactile_...PTS645Vx39-2LFS` | C&K PTS645 90° | KFC-A06-W6 90° | **provável, confirmar** |

**Antes de mandar fazer a placa nua:** abrir o projeto no KiCad, e para cada peça
nacional que você for usar, comparar o footprint do v2 com o datasheet da peça comprada.
Ajustar os footprints locais se necessário e **regerar os Gerbers**.

---

## 4. Recomendação: sourcing híbrido

O melhor custo/risco:

1. **Importe da LCSC, junto no mesmo pacote da placa nua**, só as 3 peças críticas de footprint
   (custo somado ~US$ 3–6, peso ~zero, não muda a faixa de imposto):
   - J1 — GCT USB4085 (`C7095263`)
   - J2–J6 — HRO PJ-3200B-4A ×5 (`C136687`)
   - RV1–RV5 — Alps RK09712200HA ×5 (`C470545`) *(ou confirme o pot nacional e compre aqui)*
2. **Compre no Brasil** todo o resto (CIs, relés, resistores, capacitores, diodos,
   2N7000, chaves, fusível) — item 2.
3. **Placa nua:** peça 5 un, 2 camadas, 192 × 156 mm, 1,6 mm, HASL, na JLCPCB com
   **frete econômico** (mantém o pedido ≤ US$ 50 → imposto ~37 %). Alternativa nacional
   com nota fiscal: [PCB Brasil](https://pcbbrasil.com.br) / [FastPCB](https://fastpcb.com.br).

Custo desse caminho: **placa ~R$ 350–450 (5 un) + peças ~R$ 750–900 (5 un) ≈ R$ 1.100–1.350
pelas 5**, contra ~R$ 2.150 da JLCPCB montada. Economia ~40 %, e você fica com a
experiência de bancada para a fase de bring-up (`v2-DESIGN.md` §7).

---

## 5. Lojas BR usadas nesta pesquisa

| Loja | Site | Forte em |
|---|---|---|
| Baú da Eletrônica | baudaeletronica.com.br | catálogo amplo, kits |
| SmartProjects Brasil | smartprojectsbrasil.com.br | CIs, conectores, jacks |
| Mercado Livre | mercadolivre.com.br | tudo, preço, frete grátis |
| Casa do Resistor | casadoresistor.com.br | potenciômetros |
| Duque Eletrônica | duqueeletronica.com.br | potenciômetros |
| Ecotron Componentes | ecotroncomponentes.com.br | relés Omron |
| Achei Componentes | acheicomponentes.com.br | CIs (São Paulo) |
| Proesi | proesi.com.br | CIs série 4000 |
| Toni Eletrônica | tonieletronica.com | op-amps de áudio |
| Soldafria | soldafria.com.br | chaves, ferramentas |
| Mixtrônica | mixtronica.com | diodos, fusíveis |
| DigiKey Brasil | digikey.com.br | peças originais (importa, mas cota em BRL) |

Preços e disponibilidade mudam — sempre confira no link antes de fechar o pedido.
