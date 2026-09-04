# MeetingHub-4 v2 — Painéis FRONTAL e TRASEIRO (elevação, X real / Z estimado)

X = posição real (`MeetingHub-4-v2.kicad_pcb`). Z = altura acima da base do gabinete, **ESTIMADA** — ver tabela.

> ⚠ **ESTA FOLHA NÃO É GABARITO DE CORTE.** As alturas (Z) são estimativas de mercado ou herdadas da folha equivalente da v1, não medidas reais do componente físico na v2. Confirme com paquímetro antes de furar qualquer painel lateral. Mesmo aviso que a v1 usava para este mesmo tipo de folha — nunca foi um gabarito de corte lá, também não é aqui.
>
> Além disso: por design (`v2/CLAUDE.md`), o gabinete da v2 é **"top+bottom acrílico, lados abertos"** — ou seja, painéis frontal/traseiro fechados **não fazem parte do plano atual**, de propósito (RV1-5/SW2-5/J6 ficam expostos na borda frontal, J1+J2-5 na borda traseira, sem chapa cobrindo). Esta folha é só uma referência opcional para quem futuramente quiser fechar as laterais.

A v2 muda a distribuição de componentes de borda em relação à v1: em vez de 4 potenciômetros verticais no topo + 1 horizontal na borda, **todos os 5 potenciômetros (RV1–RV5) são horizontais** e saem pela borda inferior da placa, ao lado dos 4 botões seletores de microfone. A lógica de painel frontal/traseiro da v1 foi mantida: entradas + alimentação atrás, controles + saída na frente.

## Painel TRASEIRO (borda superior da placa: alimentação + entradas de microfone)

| Ref. | X (mm) | Z estimado (mm, da base) | Função | Origem da estimativa |
|---|---|---|---|---|
| J1 | 30.00 | — | USB-C · alimentação 5V | mesma pegada GCT USB4085 da v1 (J1 lá: 3,9 mm lidos no desenho do fabricante, Seção A-A) |
| J2 | 102.00 | — | jack 3,5mm · NB1 | `Jack_3.5mm_PJ-3200B-4A_Horizontal` — footprint novo na v2 (v1 usava PJ320D); altura não conferida em datasheet específico |
| J3 | 125.00 | — | jack 3,5mm · NB2 | idem J2 |
| J4 | 148.00 | — | jack 3,5mm · NB3 | idem J2 |
| J5 | 171.00 | — | jack 3,5mm · NB4 | idem J2 |

## Painel FRONTAL (borda inferior da placa: controles de volume, seleção de mic, saída de headset)

| Ref. | X (mm) | Z estimado (mm, da base) | Função | Origem da estimativa |
|---|---|---|---|---|
| RV1 | 20.00 | — | volume NB1 | Alps RK09712200HA horizontal (LCSC C470545) — mesma família do RV5 da v1; v1 marcou 10 mm de saliência como "a estimativa menos confiável da folha" (palpite, não veio de datasheet) |
| RV2 | 35.00 | — | volume NB2 | idem RV1 |
| RV3 | 50.00 | — | volume NB3 | idem RV1 |
| RV4 | 65.00 | — | volume NB4 | idem RV1 |
| RV5 | 80.00 | — | volume master (`10k Master`, confirmado em MIXER.kicad_sch) | idem RV1 |
| SW2 | 114.00 | — | seletor mic | C&K PTS645 right-angle THT (LCSC C285519) — peça diferente do push-lock PS-22F03 usado na v1; altura de atuador não conferida em datasheet específico |
| SW3 | 128.00 | — | seletor mic | idem SW2 |
| SW4 | 142.00 | — | seletor mic | idem SW2 |
| SW5 | 156.00 | — | seletor mic | idem SW2 |
| J6 | 172.00 | — | headset / monitor | `Jack_3.5mm_PJ-3200B-4A_Horizontal` — mesma observação de J2–J5 |

## Notas

- Coluna Z deixada em branco de propósito: os valores de Z herdados da folha da v1 (ex.: 17,10 mm para os botões, 24,60 mm para o pot, 20,60 mm para os jacks P3, 18,50 mm para o USB-C) foram medidos/estimados para **outros componentes físicos** (PS-22F03, PJ320D) que a v2 não usa mais. Reutilizar esses números sem reconferência seria mais arriscado do que não informar — meça com paquímetro os componentes reais da v2 (PTS645 C285519, PJ-3200B-4A C136687, RK09712200HA C470545) antes de projetar o corte definitivo dos painéis.
- Envelope do gabinete e altura da superfície da PCB acima da base dependem dos espaçadores escolhidos (ver `mh4-plano-de-corte.md` → calço inferior/superior); ainda não fixados fisicamente para a v2.
- Como na v1, este documento cobre apenas **elevação** (posição X real + Z a confirmar). O desenho de corte dos painéis frontal/traseiro (larguras dos furos de cada conector, folgas de kerf) não foi gerado — não existia como gabarito de corte confiável nem na v1.

---
MeetingHub-4 v2 · painéis frontal/traseiro · gerado a partir do MeetingHub-4-v2.kicad_pcb · baseado na folha equivalente da v1 (`v1/box/mh4-paineis-frontal-traseiro.pdf`)
