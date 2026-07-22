# PCB-001 - Guia de Layout (Fases 2-10)

Version: 0.1
Status: Draft

Guia prático para as fases que dependem da interface gráfica do KiCad e de
componentes físicos - trabalho que só você pode executar. Este documento
existe para você seguir passo a passo enquanto monta a PCB.


# Fase 2 - Criar a PCB

1. Abra o projeto `MeetingHub-4.kicad_pro` no KiCad.
2. Abra o **PCB Editor** (ícone da placa, ou duplo clique em
   `MeetingHub-4.kicad_pcb` na árvore do projeto).
3. Menu **Tools → Update PCB from Schematic** (atalho não muda entre
   versões recentes; se não achar no menu Tools, procure no ícone da barra
   de ferramentas com um raio ⚡ sobre uma placa).
4. Vai abrir um diálogo listando as mudanças. Você deve ver **66 footprints
   novos** (todos os componentes das 5 folhas, exceto os GND). Confira que
   não aparece nenhum "Footprint not found" - se aparecer, é sinal de que
   algum footprint que atribuí não existe na sua instalação do KiCad
   (verifique se as bibliotecas padrão estão instaladas).
5. Clique em **Update PCB**. Os 66 footprints vão aparecer empilhados perto
   da origem, uns em cima dos outros - isso é normal, ninguém posiciona
   nada ainda.
6. Salve o `.kicad_pcb` imediatamente (Ctrl+S) para garantir que a
   associação schematic↔PCB ficou gravada.

**Não roteie nada nesta fase.** O objetivo é só ter os 66 footprints
carregados na placa.


# Fase 3 - Definir a mecânica

Esta é a fase mais importante segundo sua própria avaliação, e eu concordo:
decisão errada aqui obriga a refazer o posicionamento inteiro depois.

Responda antes de tocar em qualquer footprint:

## 3.1 Quais componentes precisam tocar o painel do gabinete

Baseado no esquemático, estes **11 componentes têm função de painel** (o
usuário precisa alcançá-los de fora):

| Componente | Função | Onde no painel |
|---|---|---|
| J1 (USB-C) | entrada de alimentação | traseira/lateral |
| J2-J5 (TRRS) | 4 notebooks | frente |
| J6 (TRRS) | headset do operador | frente |
| RV1-RV5 (potenciômetro duplo) | volume individual + master | frente |
| SW1-SW5 (via JST-XH + fio) | mute + seleção de notebook | frente (chave física fora da placa, ligada por fio ao conector JST) |

Todo o resto (U1, U2, K1-K4, R1-R20, C1-C21, F1, D1-D5, TP1) fica **interno**,
sem restrição de painel.

## 3.2 Dimensão da placa

- Meça o espaço interno do gabinete (ou defina o gabinete primeiro, se
  ainda não escolheu um).
- Regra prática: a placa deve ter **pelo menos a largura necessária para
  alinhar 5 jacks TRRS (J2-J6) + espaço de aperto de porca de painel**.
  Jack de painel 3.5mm (tipo PJ320D) normalmente precisa de ~12-15mm de
  centro a centro para a porca não esbarrar na vizinha - para 5 jacks em
  linha isso já são ~60-75mm só de frente de jacks.
- Se os 5 potenciômetros (RV1-RV5) também forem ficar na mesma face frontal,
  são mais 5 furos de eixo, cada um precisando de ~20-25mm de centro a
  centro (RK097 tem corpo maior que o jack). Se não couber tudo numa linha
  só, planeje duas fileiras (jacks embaixo, potes em cima, por exemplo).
- Desenhe esse arranjo no papel ou num editor vetorial **antes** de definir
  o contorno da placa no KiCad - o contorno da placa (`Edge.Cuts`) deve
  nascer do desenho do painel, não o contrário.

## 3.3 Desenhar o contorno da placa

No KiCad: selecione a camada **Edge.Cuts** na lista de camadas, use a
ferramenta de linha/retângulo para desenhar o contorno com as dimensões
decididas acima.


# Fase 4 - Posicionamento

Siga a ordem que você já propôs - ela está certa porque prioriza quem tem
restrição mecânica (painel) antes de quem só tem restrição elétrica:

1. **J1 (USB-C)** - fixe primeiro no canto/borda onde vai encostar no
   painel traseiro.
2. **J2-J6 (TRRS)** - alinhe em linha reta na borda frontal, respeitando o
   espaçamento decidido na Fase 3.
3. **RV1-RV5 (potenciômetros)** - alinhe acima ou ao lado dos jacks,
   também na borda frontal.
4. **K1-K4 (relés G5V-1)** - posicione **longe** dos jacks/potes de áudio e,
   se possível, próximos ao SW2-SW5/JST correspondente (K1 perto de SW2,
   K2 perto de SW3, etc. - facilita rastrear o roteamento depois).
5. **SW1-SW5 (conectores JST)** - perto da borda onde os fios vão sair
   para as chaves de painel reais.
6. **U1, U2 (op-amps DIP-8)** - U1 perto do grupo RV1-RV5 (ele é quem
   recebe os sinais delas), U2 perto de J6 (ele é quem alimenta o jack do
   headset). Deixe espaço ao redor de cada um para os resistores/capacitores
   da própria malha de realimentação.
7. **Capacitores** - os de desacoplamento (C4, C14, C21 - 100nF) devem
   ficar a poucos milímetros dos pinos de alimentação de U1/U2, sem exceção.
   Os demais (acoplamento, bias) ficam próximos ao op-amp/potenciômetro a
   que pertencem.
8. **Resistores** - por último, preenchendo o espaço entre os componentes
   que eles conectam.

**Ainda não pense em trilhas nesta fase** - só posição e rotação dos
footprints.


# Fase 5 - Planejamento do layout (regiões)

Zoneamento sugerido, seguindo a própria separação das folhas do
esquemático (isso não é coincidência - a hierarquia já foi pensada com
isolamento de ruído em mente, ver SCH-008):

```text
┌─────────────────────────────────────────┐
│  POWER (J1, F1, D1, C1, C2, TP1)         │  <- canto/borda de entrada
│                                           │
│  MIC_SWITCHING (K1-K4, D2-D5, SW1-SW5)   │  <- afastado de TRRS_INPUTS/MIXER
│                                           │
│  TRRS_INPUTS (J2-J5)   AUDIO_MIXER       │  <- lado a lado, sinal flui
│                          (RV1-RV4, U1)   │     de um pro outro
│                              │            │
│                        HEADPHONE_AMP     │
│                        (U2, J6)          │
└─────────────────────────────────────────┘
```

Ideia central: **potência (POWER) e sinal fraco de microfone
(MIC_SWITCHING) ficam nas pontas opostas**, com o caminho de áudio
(TRRS → MIXER → HPAMP) atravessando o meio em linha reta, sem cruzar de
volta. Isso evita que uma trilha de áudio tenha que passar perto de um
relé ou da entrada de alimentação.


# Fase 6 - Plano de terra

- Plano de GND cobrindo toda a placa na camada **Bottom** (B.Cu).
- Sinal na camada **Top** (F.Cu), usando o plano de baixo como retorno.
- Cada capacitor de desacoplamento (C4/C14/C21) deve ter a via de GND o
  mais curta possível - idealmente o próprio pad encostando numa via para
  o plano, sem trilha longa entre o capacitor e o plano.
- **Aterramento em estrela** (já decidido em SCH-008/DR-002): o retorno de
  GND de POWER e o retorno de GND do bloco analógico (TRRS/MIXER/HPAMP)
  devem se encontrar em um único ponto físico - não deixe o plano de GND
  "livre" sem pensar em onde a corrente de retorno da alimentação
  efetivamente entra no plano analógico.
- Cuidado especial com **K1-K4**: a corrente de acionamento da bobina do
  relé (vindo de +5V_AUDIO, passando por SW2-SW5) não deve compartilhar o
  mesmo trecho de plano de GND que a linha de retorno de MIC/áudio -
  prefira que a corrente da bobina "entre e saia" pela região de POWER,
  não atravessando por baixo de TRRS_INPUTS/MIXER.


# Fase 7 - Roteamento

Siga a ordem que você propôs. Larguras de trilha sugeridas para esta
placa (alimentação via USB, ~500mA no fusível):

| Tipo de sinal | Largura sugerida |
|---|---|
| +5V_AUDIO, GND (potência) | 0.6-0.8mm |
| Sinal de áudio (NB*_L/R, MIX_L/R) | 0.25-0.3mm |
| Linha de microfone (NB*_MIC, HEADSET_MIC) | 0.25-0.3mm, **evitar correr paralela e colada em trilha de +5V_AUDIO ou bobina de relé** - se cruzar, cruze perpendicular, nunca paralelo por mais que uns poucos mm |
| Controle de relé (bobina, +5V_AUDIO→SWx→K) | 0.4-0.5mm |

Ordem de roteamento (a sua está correta):

1. Alimentação (+5V_AUDIO, do J1 até POWER, depois até MIXER/HPAMP/MICSW)
2. GND (plano, mais os poucos casos que não dá pra resolver só com plano)
3. Sinais dos op-amps (malha de realimentação de U1 e U2 - mantenha essas
   trilhas curtas, são as mais sensíveis a captar ruído)
4. Microfones (NB1-4_MIC, HEADSET_MIC - linha "transparente", sem
   amplificação, então qualquer ruído captado aqui vai direto pro
   notebook)
5. Fones (MIX_L/R, saída de J6)
6. Controle (bobinas dos relés, SW1-SW5)
7. USB-C por último, como você sugeriu - os 4 pinos de dados (D+/D-/CC1/CC2)
   estão **intencionalmente sem uso** neste projeto (só VBUS+GND importam),
   então nem precisam de trilha nenhuma - ignore os "unconnected" que o
   KiCad avisar para esses pinos.


# Fase 8 - DRC

1. No PCB Editor: **Inspect → Design Rules Checker** (ou o ícone de
   "bug"/lupa na barra de ferramentas).
2. Antes de rodar, confira **File → Board Setup → Design Rules** - ajuste
   a largura mínima de trilha e o espaçamento mínimo para os valores da
   fabricante que você for usar (ex.: JLCPCB padrão é 0.153mm de trilha e
   0.127mm de espaçamento mínimos - use algo folgado tipo 0.25mm/0.2mm já
   que esta placa não é densa).
3. Clique em **Run DRC**. Corrija um erro de cada vez, rodando de novo
   depois de cada correção - não tente corrigir tudo de uma vez e rodar
   só no final.
4. Erros mais prováveis nesta placa: clearance entre os pads grandes do
   G5V-1/USB-C e trilhas vizinhas, e trilhas não roteadas (net não
   conectada) se algum footprint ficar sem toda trilha ligada.
5. Só considere a Fase 8 concluída com **zero erros e zero warnings não
   justificados** (um warning de "trilha curta" ou similar pode ser
   aceitável, mas documente por quê).


# Fase 9 - Revisão mecânica em escala 1:1

1. No PCB Editor: **File → Print**.
2. Marque a opção de escala **1:1** (às vezes chamada "Scale 1" ou "No
   scaling" dependendo da versão) - **nunca use "fit to page"**, isso
   distorce a escala.
3. Antes de confiar na impressão, meça com uma régua uma medida conhecida
   no papel (ex.: a distância entre dois furos de montagem) para confirmar
   que a impressora não escalou nada.
4. Com a folha impressa, sobreponha fisicamente:
   - um relé G5V-1 (ou o footprint desenhado dele) sobre os pads de K1-K4;
   - um jack TRRS (o modelo real que você comprar) sobre J2-J6;
   - um potenciômetro RK097 sobre RV1-RV5;
   - o conector USB-C sobre J1.
5. Confira se os furos de fixação do painel (se houver) coincidem com a
   posição real dos componentes, e se não há dois componentes tentando
   ocupar o mesmo espaço físico (ex.: corpo do potenciômetro encostando no
   relé vizinho).


# Fase 10 - Fabricação

Arquivos a gerar (via **File → Fabrication Outputs** no PCB Editor, ou
`kicad-cli pcb export` linha de comando):

- **Gerbers** (todas as camadas de cobre + máscara + silk + Edge.Cuts)
- **Excellon** (arquivo de furação)
- **BOM final** - já temos uma gerada em `hardware/BOM/BOM-MeetingHub-4.csv`;
  confirme que ela ainda bate com o `.kicad_pcb` final antes de enviar.
- **PDF de montagem** (posição dos componentes, útil pra você mesmo na
  hora de soldar)
- **PDF do esquemático** - já temos em `hardware/Schematics/`

**Observação sobre Pick & Place**: todos os 66 componentes deste projeto
têm footprint **THT** (nenhum SMD). Isso significa que, a rigor, você **não
precisa gerar arquivo de Pick & Place** para este lote, a menos que decida
contratar montagem automática por onda/solda seletiva de alguma fabricante
que peça esse arquivo mesmo para THT. Para montagem manual, Gerbers +
Excellon + BOM + PDF de montagem já são suficientes.

Depois de gerado tudo, me chame de volta e eu confiro:
- se os arquivos abrem e são consistentes entre si (via `kicad-cli`);
- se a BOM final bate com o `.kicad_pcb`;
- se sobrou algum footprint sem valor/referência antes de fechar o pacote
  de fabricação.
