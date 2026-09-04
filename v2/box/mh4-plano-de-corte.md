# MeetingHub-4 v2 — Plano de Corte e Furação — Acrílico

Corte a laser · acrílico (PMMA) 3 mm · origem das coordenadas: `MeetingHub-4-v2.kicad_pcb` · datum (0,0) = canto superior esquerdo de cada chapa

> Gerado a partir do plano equivalente da v1 (`v1/box/mh4-plano-de-corte.pdf`), adaptado à placa v2 (192 × 156 mm, cantos R6, 6 pontos de fixação). Diferente da v1, a v2 **não tem nenhum potenciômetro montado no topo** — todos os RV1–RV5 são horizontais e saem pela borda inferior da placa, então a chapa TOPO não precisa de furo de trimmer. Isso torna TOPO e BASE geometricamente idênticas nesta revisão.

## Quantidade para produção

| Peça | Por unidade | 5 unidades |
|---|---|---|
| Chapa TOPO (só furos de fixação) | 1 | 5 |
| Chapa BASE (só furos de fixação) | 1 | 5 |
| **Total de peças a cortar** | **2** | **10** |

## Material

Acrílico (PMMA) **3 mm**, transparente ou na cor desejada. Corte a laser CO₂ padrão. Tolerância de kerf (0,1–0,2 mm) já embutida nos diâmetros de furo especificados.

Chapa por peça: **192,00 × 156,00 mm**, cantos com raio de 6 mm.

## Arquivos desta entrega

| Arquivo | Conteúdo | Uso |
|---|---|---|
| `mh4-acrilico-topo.dxf` | contorno + 6 furos M3 | enviar direto para a máquina de corte |
| `mh4-acrilico-base.dxf` | contorno + 6 furos M3 (idêntico ao topo) | enviar direto para a máquina de corte |
| `mh4-acrilico-topo.svg` / `-base.svg` | mesmas geometrias, formato vetorial alternativo | conferência visual / oficinas que preferem SVG |
| `mh4-plano-de-corte.md` | este documento — desenho cotado + tabela de furos + lista de material + kit de fixação | conferência humana e pedido de orçamento |
| `mh4-paineis-frontal-traseiro.md` | folha de elevação (X real / Z estimado) dos painéis laterais | referência para furar os painéis frontal/traseiro (NÃO é gabarito de corte) |

## Chapa TOPO / BASE — furos (idênticos)

Datum (0,0) no canto superior esquerdo da chapa. Dimensões conferem com `mh4-acrilico-*.dxf`.

| Furo | X (mm, esq.) | Y (mm, topo) | Ø | Observação |
|---|---|---|---|---|
| MH1 | 8.00 | 8.00 | Ø3.5 | fixação M3, 6x em ambas as chapas |
| MH2 | 184.00 | 8.00 | Ø3.5 | fixação M3, 6x em ambas as chapas |
| MH3 | 8.00 | 126.00 | Ø3.5 | fixação M3, 6x em ambas as chapas |
| MH4 | 184.00 | 126.00 | Ø3.5 | fixação M3, 6x em ambas as chapas |
| MH5 | 9.00 | 144.00 | Ø3.5 | fixação M3, 6x em ambas as chapas — próximo ao cluster RV/SW da borda inferior |
| MH6 | 183.00 | 144.00 | Ø3.5 | fixação M3, 6x em ambas as chapas — próximo ao cluster RV/SW da borda inferior |

Cantos R6 (4x).

## Observação — RV1 a RV5

Todos os potenciômetros principais são montados horizontalmente (`Potentiometer_Alps_RK097_Dual_Horizontal`) — o eixo sai pela borda da placa, direto no painel frontal do gabinete, igual ao RV5 fazia na v1. **Nenhum** dos cinco tem furo nestas duas chapas de acrílico (topo/base); a furação deles pertence ao desenho do painel frontal (ver `mh4-paineis-frontal-traseiro.md`), ainda não coberto por este plano como gabarito de corte definitivo.

## Ferragem de montagem — por unidade

A v2 tem 6 pontos de fixação (não 4) e nenhum trimmer no topo, então o kit de fixação da v1 muda: mais um par de espaçadores/parafusos, e **sem** porca de barril / arruela / porca M9 (esses eram exclusivos do trimmer RK09L vertical, que não existe na v2).

| Item | Por unidade | 5 unidades | Observação |
|---|---|---|---|
| Parafuso M3 cabeça chata, ~20–25 mm | 6 | 30 | cobre base + calço inferior + PCB + calço superior + porca no topo |
| Espaçador de nylon M3, furo passante, 10 mm | 6 | 30 | calço inferior — ajustar conforme conector mais alto sob a placa |
| Espaçador de nylon M3, furo passante, 3 mm | 6 | 30 | calço superior — só precisa vencer a espessura da chapa topo |
| Porca M3 (ou porca de embutir M3) | 6 | 30 | trava no topo; substitui a porca de barril usada nos furos de trimmer da v1 |

## Ordem de montagem

1. Parafuso M3 pelo lado de baixo da chapa base → calço inferior (10 mm) → placa PCB → calço superior (3 mm) → chapa topo → porca M3 nos 6 pontos (MH1–MH6).
2. Nunca rosqueie parafuso direto no acrílico — sempre furo passante + espaçador/porca fazendo o aperto.
3. Confirme a altura real do calço inferior contra o conector mais alto sob a placa (USB-C J1, jacks) antes de cortar/comprar os espaçadores em quantidade — os valores acima são os mesmos usados como ponto de partida na v1 e ainda não foram reconferidos fisicamente para a v2.

---
MeetingHub-4 v2 · plano de corte gerado a partir do MeetingHub-4-v2.kicad_pcb · baseado no plano da v1 (`v1/box/mh4-plano-de-corte.pdf`)
