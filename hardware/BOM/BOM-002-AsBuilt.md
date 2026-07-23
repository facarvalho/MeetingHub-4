# BOM-002 - As-Built Bill of Materials

Version: 1.0
Status: Final — confere com a PCB final de 4 camadas (layout completo e validado)

Supersede: BOM-001 (lista conceitual, anterior ao esquemático real)


# 1. Objetivo

Registrar a lista de materiais real, extraída diretamente do esquemático KiCad
(5 folhas: POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP, MIC_SWITCHING),
com referência, valor e footprint de cada componente, mais os itens
adicionados diretamente na PCB durante o layout (furos de fixação e ponto de
teste de GND).

Arquivo bruto: [BOM-MeetingHub-4.csv](BOM-MeetingHub-4.csv)


# 2. Resumo

- 75 itens físicos distintos (36 linhas após agrupar por valor+footprint):
  70 componentes do esquemático + TP2 (ponto de teste de GND) + MH1-4
  (furos de fixação M3) - estes últimos 5 não têm símbolo no esquemático
  por serem só-mecânicos, adicionados direto na PCB (ver PCB-001 Fases
  3.3.3 e 8).
- 100% dos componentes possuem footprint atribuído (exceto símbolos de GND)
- Todos os componentes ativos e passivos em THT, favorecendo montagem manual


# 3. Notas de escolha de footprint

- **J1** (USB-C): `Connector_USB:USB_C_Receptacle_GCT_USB4085` - peça comum,
  usada em diversos projetos open-hardware.
- **J2-J6** (TRRS 3.5mm, 4 polos): `Connector_Audio:Jack_3.5mm_PJ320D_Horizontal`
  - jack metálico de painel. Confirmar mecanicamente contra a peça real comprada
  antes de rotear a PCB.
- **K1-K4** (relé): `Relay_THT:Relay_SPDT_Omron_G5V-1` - footprint oficial do
  G5V-1 real.
- **RV1-RV5** (potenciômetro duplo): `Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal`
  - conferir alinhamento com os furos do painel frontal.
- **SW1-SW5** (MUTE + seleção de notebook): `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`
  - chaves ficam no painel, ligadas por fio até a placa (não são botões de PCB).
- **U1, U2** (NE5532 / NJM4556A): `Package_DIP:DIP-8_W7.62mm` - DIP-8 para
  facilitar montagem manual do protótipo (usar soquete). Migrar para SOIC-8
  em produção seriada, se necessário reduzir a área da placa.
- **D1** (proteção TVS): footprint `Diode_THT:D_DO-41_SOD81`; valor real de
  compra é PTVS5V0Z1USK (o símbolo usado na biblioteca é o genérico ZPYxx,
  sem alterar pinagem/geometria).
- **TP1, TP2** (pontos de teste): `TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm`
  - TP1 no net +5V_AUDIO (folha POWER), TP2 no net GND, perto do U1. TP2 é
    um footprint só-mecânico, adicionado direto na PCB (sem símbolo no
    esquemático) - ver PCB-001 Fase 8 para o histórico de por que ele
    existe (ponto de teste genérico de GND, útil para medição).
- **MH1-MH4** (furos de fixação do gabinete): `MountingHole:MountingHole_3.2mm_M3`
  - furo não-plaqueado 3.2mm para parafuso M3, um em cada canto da placa,
    6mm de margem da borda. Só-mecânicos, sem símbolo no esquemático - ver
    PCB-001 Fase 3.3.3 para as posições exatas.


# 4. Status de fabricação

- ✅ Layout de PCB completo (posicionamento de jacks, potenciômetros,
  relés; separação áudio/alimentação por face do gabinete - ver PCB-001
  Fases 3-5).
- ✅ DRC real (via KiCad) limpo: 0 pads não conectados, 0 erros. Único
  aviso remanescente é cosmético e aceito (divergência de biblioteca dos
  potenciômetros RV1-RV5 - ver PCB-001 Fase 8).
- ✅ Placa migrada para 4 camadas (planos dedicados de GND e +5V_AUDIO nas
  camadas internas - ver PCB-001 Fase 6).
- ✅ Gerbers, furação (Excellon) e posições de montagem exportados e
  validados via `kicad-cli` (sem erro de exportação).
- ✅ ERC rodado (via KiCad, pelo usuário), em duas rodadas, e todos os
  erros reais foram corrigidos - ver PCB-001 Fase 11 para o detalhe de
  cada um:
  - **TP1 nunca esteve realmente ligado a +5V_AUDIO** (nem no esquemático,
    nem na PCB) - o pino ficava visualmente sobre um fio existente sem
    junção elétrica. Corrigido em ambos os arquivos.
  - **TP2 também não estava ligado a GND na PCB** (footprint só-mecânico,
    adicionado sem net). Corrigido - agora no net GND de fato.
  - `power_pin_not_driven` no U1 (pinos V+/V-): corrigido com dois símbolos
    `power:PWR_FLAG` em POWER.kicad_sch. Na primeira tentativa o flag de
    +5V_AUDIO foi ligado no lado errado do fusível F1 (ainda resolveu o
    lado GND, mas não o V+) - corrigido na segunda rodada, movendo o flag
    para o mesmo nó que já alimenta o TP1 e o rótulo global +5V_AUDIO.
  - `lib_symbol_issues` em J2-J6 (AudioJack4): o símbolo estava referenciado
    como `Connector:AudioJack4`, biblioteca que não existe mais nessa
    posição no KiCad atual (o símbolo foi movido para `Connector_Audio`).
    Corrigido o `lib_id` para `Connector_Audio:AudioJack4` em TRRS.kicad_sch
    (J2-J5) e HPAMP.kicad_sch (J6) - geometria e pinos conferidos byte a
    byte contra a biblioteca do sistema antes da troca.
  - `pin_not_connected` (erro, não aviso) nos 9 pinos de dados/CC/SBU/shield
    do J1 (USB-C: D+, D-, CC1, CC2, SBU1, SBU2, SHIELD) e no pino 10 dos
    relés K1-K4 (pino duplicado do contato reverso do G5V-1, não usado
    nesta topologia SPDT): ambos os casos são intencionais (J1 só é usado
    como entrada de alimentação - ver DR-002/DR-003), mas ficavam listados
    como **erro** de qualquer forma. Corrigido adicionando marcadores
    "no connect" explícitos em cada pino, a forma padrão do KiCad de dizer
    "sei que este pino está solto de propósito".
  - Não corrigido, por ser cosmético: ~233 `endpoint_off_grid` (pinos/fios
    fora da grade de verificação do ERC, não afeta conectividade real).
  - **Recomendado**: rode o ERC de novo depois de puxar essas mudanças,
    para confirmar 0 erros restantes (só os avisos de grade, que são
    estéticos).

**Pendente real, fora do escopo deste BOM**: conferência mecânica final
dos footprints acima (J1-J6, K1-K4, RV1-RV5) contra os datasheets das
peças efetivamente compradas, no momento da compra/recebimento -
recomendado mesmo com o layout validado, já que pequenas variações entre
fornecedores do mesmo componente podem existir.
