# DR-003 - Schematic Implementation Review

Version: 1.0
Status: Review


# 1. Objetivo

Documentar o que foi de fato implementado e validado durante a construção do
esquemático KiCad do MeetingHub-4 (SCH-001 a SCH-009), e deixar explícito o
que essa validação cobre e o que **não** cobre, para orientar a revisão
técnica completa antes da fabricação.


# 2. O que foi construído

O projeto foi organizado em cinco folhas hierárquicas em
`hardware/KiCad/MeetingHub-4/`:

## POWER (POWER.kicad_sch)

- Conector USB-C de alimentação (J1)
- Fusível de proteção (F1, 500mA)
- Diodo TVS de proteção (D1)
- Filtragem da alimentação +5V_AUDIO (C1/C2)
- Ponto de teste (TP1)

**Observação:** esta folha **não possui regulador de tensão**. A alimentação
`+5V_AUDIO` corresponde ao VBUS do USB-C, protegido e filtrado, sem
regulação ativa.

## TRRS_INPUTS (TRRS.kicad_sch)

- Quatro conectores TRRS para os notebooks (J2-J5)
- Distribuição dos sinais de áudio provenientes dos notebooks

## AUDIO_MIXER (MIXER.kicad_sch)

- Potenciômetros de ajuste individual dos canais (RV1-RV4) + master (RV5)
- Mixer estéreo **ativo** baseado em amplificador operacional NE5532 (U1)
- Rede de realimentação do somador
- Geração da referência **VBIAS** por divisor resistivo (10 kΩ / 10 kΩ) com
  capacitor de desacoplamento

**Observação:** o VBIAS é utilizado como referência de meia tensão para os
amplificadores operacionais (U1 e U2). Ele **não** fornece polarização aos
microfones, que permanecem utilizando a alimentação fornecida pelo notebook,
conforme os requisitos de transparência do SCH-004/SCH-007.

## HEADPHONE_AMP (HPAMP.kicad_sch)

- Amplificador para fones de ouvido baseado em NJM4556A (U2)
- Acoplamento de entrada/saída por capacitor
- Desacoplamento da alimentação
- Conector TRRS do headset do operador (J6)

## MIC_SWITCHING (MICSW.kicad_sch)

- Chave de mute (SW1)
- Quatro relés Omron G5V-1 (K1-K4)
- Diodos flyback (D2-D5)
- Seleção individual dos quatro microfones
- Conectores JST-XH para botões externos (SW1-SW5)

Ao final, o projeto contém **66 componentes**, todos com footprints
atribuídos (exceto símbolos globais de alimentação). BOM gerada em
`hardware/BOM/BOM-MeetingHub-4.csv` e PDF do esquemático em
`hardware/Schematics/MeetingHub-4-Schematic.pdf`.


# 3. Diagramas de bloco

Diagrama único de topologia mista tende a confundir alimentação com sinal.
Por isso, três diagramas separados:

## 3.1 Distribuição de alimentação

```text
USB-C (J1)
   │
 POWER
   │ +5V_AUDIO
   ├──► AUDIO_MIXER    (U1 NE5532)
   ├──► HEADPHONE_AMP  (U2 NJM4556A)
   └──► MIC_SWITCHING  (bobinas dos relés K1-K4, via SW2-SW5)
```

## 3.2 Caminho de áudio (Notebook -> Headset)

```text
TRRS_INPUTS                 AUDIO_MIXER                HEADPHONE_AMP
J2 NB1_L/R ──┐
J3 NB2_L/R ──┤   volume            soma            MIX_L/R    ganho     J6
J4 NB3_L/R ──┼──► individual ──► ativa (U1) ───────────────► (U2) ──► Headset
J5 NB4_L/R ──┘   (RV1-RV4)                                             (L/R)
```

## 3.3 Caminho do microfone (Headset -> Notebook selecionado)

```text
Headset (J6, sleeve)
   │ HEADSET_MIC
 MIC_SWITCHING (SW1 mute + K1-K4 seleção)
   │
   ├──► NB1_MIC ──► J2 (TRRS_INPUTS)
   ├──► NB2_MIC ──► J3
   ├──► NB3_MIC ──► J4
   └──► NB4_MIC ──► J5      (apenas um relé deve ficar energizado por vez)
```


# 4. O que foi validado, e como

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


# 5. Limitação importante da revisão

A validação acima foi feita **sobre o projeto completo** (todas as 5 folhas
+ raiz), não sobre fragmentos isolados. Ainda assim, a revisão foi
predominantemente automatizada (parsing/exportação via `kicad-cli`) e
visual (inspeção do PDF renderizado). Não substitui:

- ERC completo na interface gráfica do KiCad;
- conferência manual, folha por folha, de cada junção/rótulo contra a
  intenção elétrica (especialmente linha de microfone e aterramento);
- revisão de valores de ganho, impedância e ruído por alguém que possa
  simular ou bancar o circuito fisicamente.


# 6. Decisões técnicas tomadas durante a implementação

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


# 7. Pendências antes da fabricação

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


# 8. Status

Esquemático estruturalmente válido e pronto para a etapa de layout de PCB.
Não aprovado para fabricação - depende das pendências da seção 7.
