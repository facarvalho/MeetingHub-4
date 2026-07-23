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
- ⚠️ **ERC (Electrical Rules Checker) do esquemático ainda não foi
  confirmado.** Esta versão do KiCad (7.0.11) não expõe ERC por linha de
  comando nem por script Python (diferente do DRC de PCB, para o qual foi
  encontrado um caminho via `pcbnew.WriteDRCReport` - ver PCB-001) - só
  roda pela interface gráfica. **Rode antes de fabricar**: no Schematic
  Editor, **Inspect → Electrical Rules Checker → Run ERC**, revise
  qualquer erro/aviso e me envie o relatório se quiser ajuda para
  interpretar.

**Pendente real, fora do escopo deste BOM**: conferência mecânica final
dos footprints acima (J1-J6, K1-K4, RV1-RV5) contra os datasheets das
peças efetivamente compradas, no momento da compra/recebimento -
recomendado mesmo com o layout validado, já que pequenas variações entre
fornecedores do mesmo componente podem existir.
