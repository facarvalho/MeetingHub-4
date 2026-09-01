# BOM-003 - Lista de Compras (MeetingHub-4)

Verificado em estoque na LCSC/JLCPCB em 2026-08-06. SW1-SW5 e RV1-RV4 atualizados em 2026-08-07; C2/C3/C16/C19 atualizado em 2026-08-08 (ver notas abaixo).

| Componente | Referência | Código | Link | Quantidade |
|---|---|---|---|---|
| Capacitor cerâmico 100nF SMD 0603 | C1, C4, C21 | LCSC C14663 | https://www.lcsc.com/product-detail/C14663.html | 3 |
| Capacitor eletrolítico 10uF THT D5xL11mm (CX KM106M016D11RR0VH2FP0) — substitui UD2E100M1010 (era SMD D10x10.2mm, colidia com vizinhos no footprint THT da placa) | C2, C3, C16, C19 | LCSC C43799 | https://www.lcsc.com/product-detail/C43799.html | 4 |
| Capacitor cerâmico X7R 1uF THT | C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C18 | LCSC C2167638 | https://www.lcsc.com/product-detail/C2167638.html | 12 |
| Capacitor eletrolítico 220uF | C17, C20 | LCSC C2063 | https://www.lcsc.com/product-detail/C2063.html | 2 |
| Diodo TVS 5V unidirecional SMD SOD-323 | D1 | LCSC C553448 | https://www.lcsc.com/product-detail/C553448.html | 1 |
| Diodo 1N4148 | D2, D3, D4, D5 | LCSC C402212 | https://www.lcsc.com/product-detail/C402212.html | 4 |
| Fusível PTC 500mA | F1 | LCSC C1562150 | https://www.lcsc.com/product-detail/C1562150.html | 1 |
| Conector USB-C | J1 | LCSC C7095263 | https://www.lcsc.com/product-detail/C7095263.html | 1 |
| Conector TRRS 3.5mm | J2, J3, J4, J5, J6 | LCSC C22459515 | https://www.lcsc.com/product-detail/C22459515.html | 5 |
| Relé SPDT 5V | K1, K2, K3, K4 | LCSC C28695 | https://www.lcsc.com/product-detail/C28695.html | 4 |
| Resistor 10k | R1-R12 | LCSC C5618323 | https://www.lcsc.com/product-detail/C5618323.html | 12 |
| Resistor 100k | R13, R17 | LCSC C1364475 | https://www.lcsc.com/product-detail/C1364475.html | 2 |
| Resistor 1k | R14, R15, R18, R19 | LCSC C120055 | https://www.lcsc.com/product-detail/C120055.html | 4 |
| Resistor 47R | R16, R20 | LCSC C2896824 | https://www.lcsc.com/product-detail/C2896824.html | 2 |
| Potenciômetro duplo 10k audio (Alps RK09L1240A12) — corpo compacto/quadrado (14.5x17.9mm), montagem vertical | RV1, RV2, RV3, RV4 | LCSC C380211 | https://www.lcsc.com/product-detail/C380211.html | 4 |
| Potenciômetro duplo 10k audio (Alps RK09712200HA) — corpo largo (29.6x9.5mm), montagem horizontal (90°, painel frontal, master) | RV5 | LCSC C470545 | https://www.lcsc.com/product-detail/C470545.html | 1 |
| Chave push com retenção (push-on/push-off / self-locking), THT ângulo reto, DPDT — PS-22F03 / A03 — usada como SW2-SW5 (seletoras). **2026-08-28**: trocada de momentânea (TS665ZJ) para latching, para não precisar "segurar" o botão. **SW1 (MUTE) removido**: sem seletora travada = todos os relés desligados = mic mudo (o próprio "nenhum selecionado" é o mute). Footprint `SW_PushLock_PS-22F03` é RASCUNHO — conferir dimensões do corpo/atuador e a posição dos pinos COM/NO no datasheet C2848947 antes de encomendar. MPN alt: HOOYA PS-22F03-N-B (C19190927) | SW2, SW3, SW4, SW5 | LCSC C2848947 | https://www.lcsc.com/product-detail/C2848947.html | 4 |
| Amplificador operacional duplo NE5532 | U1 | LCSC C2987282 | https://www.lcsc.com/product-detail/C2987282.html | 1 |
| Amplificador operacional duplo NJM4556A | U2 | LCSC C2838125 | https://www.lcsc.com/product-detail/C2838125.html | 1 |
| Knobs para RV1-RV5 (eixo chato 6mm) — **compatibilidade confirmada 2026-08-11**: conferi os desenhos mecânicos oficiais Alps de ambas as peças — RK09L1240A12 (RV1-4) e RK09712200HA (RV5) usam o mesmo eixo padrão Alps "平轴" (flat shaft), ø6mm com corte plano de 4.5mm, 12mm de eixo exposto. Mesmo tipo/diâmetro nas duas, esse knob serve pros 5 | RV1-RV5 | RS Online | https://ie.rs-online.com/web/p/potentiometer-knobs/7777353 | 5 |
| Capa/botão para SW2-SW5 (seletoras) — a PS-22F03/A03 costuma vir com uma capa vermelha; capas coloridas avulsas ("A03 switch cap") existem na LCSC/AliExpress se quiser diferenciar as 4 | SW2-SW5 | — | — | 4 (opcional) |
| Pés de borracha (base da placa) | — | genérico, loja local/AliExpress | — | 4 |
