# BOM-002 - As-Built Bill of Materials

Version: 1.0
Status: Draft (gerado a partir do esquemático, pendente de layout de PCB)

Supersede: BOM-001 (lista conceitual, anterior ao esquemático real)


# 1. Objetivo

Registrar a lista de materiais real, extraída diretamente do esquemático KiCad
(5 folhas: POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP, MIC_SWITCHING),
com referência, valor e footprint de cada componente.

Arquivo bruto: [BOM-MeetingHub-4.csv](BOM-MeetingHub-4.csv)


# 2. Resumo

- 70 componentes distintos (34 linhas após agrupar por valor+footprint)
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


# 4. Pendências antes da fabricação

- ERC completo via KiCad (interface gráfica).
- Layout da PCB (posicionamento de jacks, potenciômetros, relés; separação
  áudio/alimentação).
- DRC da fabricante escolhida.
- Conferência mecânica dos footprints acima contra os datasheets das peças
  efetivamente compradas.
