# DR-003 - Schematic Implementation Review

Version: 1.0
Status: Review


# 1. Objetivo

Documentar o que foi de fato implementado e validado durante a construção do
esquemático KiCad do MeetingHub-4 (SCH-001 a SCH-009), e deixar explícito o
que essa validação cobre e o que **não** cobre, para orientar a revisão
técnica completa antes da fabricação.


# 2. O que foi implementado

Cinco folhas hierárquicas em `hardware/KiCad/MeetingHub-4/`:

| Folha | Arquivo | Conteúdo |
|---|---|---|
| POWER | POWER.kicad_sch | J1 (USB-C, só VBUS/GND), F1 (fusível 500mA), D1 (TVS 5V), C1/C2 (filtro), TP1 (test point) |
| TRRS_INPUTS | TRRS.kicad_sch | J2-J5, 4 entradas TRRS CTIA (notebooks 1-4) |
| AUDIO_MIXER | MIXER.kicad_sch | RV1-RV4 (volume individual), U1 NE5532 (somador L/R), RV5 (master) |
| HEADPHONE_AMP | HPAMP.kicad_sch | U2 NJM4556A (ganho ~2x por canal), J6 (jack do headset do usuário) |
| MIC_SWITCHING | MICSW.kicad_sch | SW1 (mute) + K1-K4 (relé G5V-1) + D2-D5 (flyback) |

Todos os 70 componentes (66 ativos/passivos + GND) têm footprint THT
atribuído. BOM gerada em `hardware/BOM/BOM-MeetingHub-4.csv` e PDF do
esquemático em `hardware/Schematics/MeetingHub-4-Schematic.pdf`.


# 3. O que foi validado, e como

- **Conectividade estrutural**: `kicad-cli sch export netlist` rodado
  repetidamente (múltiplas vezes, de forma determinística) sobre o projeto
  completo, sem erro. As redes nomeadas (`+5V_AUDIO`, `VBIAS`, `NB1-4_L/R/MIC`,
  `MIX_L/R`, `HEADSET_MIC`, `GND`) aparecem corretamente na netlist exportada,
  ligando as 5 folhas entre si como esperado.
- **Renderização visual**: `kicad-cli sch export pdf` gerado e inspecionado
  página a página (todas as 6 páginas), confirmando que os componentes
  aparecem nas folhas certas com os rótulos esperados.
- **Footprints**: script de pós-processamento conferiu que 100% dos
  componentes (exceto símbolos de GND, que não usam footprint) têm um
  footprint não-vazio atribuído.

**Isso equivale a uma checagem de integridade estrutural do arquivo, não a
um ERC.** Nenhuma dessas verificações substitui o ERC completo do KiCad
(conflito de tipo de pino, entrada flutuante, pino de alimentação sem
fonte, etc.), que só roda pela interface gráfica nesta versão do
`kicad-cli` (7.0.11 - os subcomandos `sch erc` e `pcb drc` só existem a
partir do KiCad 8).


# 4. Limitação importante da revisão

A validação acima foi feita **sobre o projeto completo** (todas as 5 folhas
+ raiz), não sobre fragmentos isolados. Ainda assim, a revisão foi
predominantemente automatizada (parsing/exportação via `kicad-cli`) e
visual (inspeção do PDF renderizado). Não substitui:

- ERC completo na interface gráfica do KiCad;
- conferência manual, folha por folha, de cada junção/rótulo contra a
  intenção elétrica (especialmente linha de microfone e aterramento);
- revisão de valores de ganho, impedância e ruído por alguém que possa
  simular ou bancar o circuito fisicamente.


# 5. Decisões técnicas tomadas durante a implementação

Pontos que exigem confirmação humana antes de rotear a PCB:

- **VBIAS**: gerado por divisor resistivo passivo (10k/10k + 10uF), sem
  buffer ativo. Funciona porque a impedância de entrada dos op-amps é alta,
  mas é a escolha mais simples possível - se houver ruído de fundo audível
  no protótipo, esse é o primeiro ponto a revisar (trocar por um buffer
  ativo dedicado).
- **Ganhos**: mixer somador com ganho unitário por fonte (Rf = Rin = 10k);
  estágio de headphone com ganho ~2x (Rf/Rg = 1k/1k). Não foram validados
  contra nível de saída real de notebooks nem contra a sensibilidade de
  fones de 16-64 ohms - valores de partida razoáveis, não calibrados.
- **Seleção de microfone**: implementada com chaves SPST manuais (SW2-SW5)
  alimentando cada bobina de relé independentemente. Não há intertravamento
  elétrico - é responsabilidade do usuário final acionar apenas uma seleção
  por vez, como já previsto em SCH-007.
- **Contorno de bug do kicad-cli**: símbolos com `(extends "Base")` (ex.
  NE5532/NJM4556A a partir de LM2904, TVS a partir de ZPYxx) e nomes de
  símbolo em cache sem o prefixo da biblioteca causavam segfault
  determinístico no `kicad-cli sch export netlist` (KiCad 7.0.11). Os
  símbolos foram embutidos usando o símbolo-base diretamente com o campo
  Value sobrescrito, e os nomes em cache foram prefixados
  (`Device:R`, `Diode:ZPYxx`, etc.). Isso é apenas uma peculiaridade de
  arquivo/ferramenta - não afeta a elétrica, mas fica registrado caso
  outro símbolo com `extends` seja adicionado no futuro.


# 6. Pendências antes da fabricação

Confirmadas nesta revisão, ainda em aberto:

- ERC completo via KiCad (GUI).
- Layout da PCB (posicionamento de jacks/potenciômetros/relés, separação
  áudio x alimentação, plano de terra) e DRC da fabricante escolhida.
- Conferência mecânica de pinout/footprint contra os datasheets das peças
  efetivamente compradas: USB-C, jacks TRRS (PJ320D), G5V-1, potenciômetros
  duplos (RK097).
- Conferência dimensional contra o gabinete.
- Geração de Gerbers, arquivos de furação (Excellon), BOM final e
  Pick & Place (se houver montagem automática).
- Revisão técnica manual completa (alimentação, aterramento analógico,
  níveis/impedância de áudio, relés, USB-C, op-amps, mixer, seleção de
  microfone, possíveis loops de terra) antes de gerar os arquivos de
  fabricação.


# 7. Status

Esquemático estruturalmente válido e pronto para a etapa de layout de PCB.
Não aprovado para fabricação - depende das pendências da seção 6.
