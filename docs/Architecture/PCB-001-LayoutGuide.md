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
usuário precisa alcançá-los de fora). A decisão final sobre **qual face**
de cada um segue a lógica de uso (o que o operador toca com mais
frequência fica na frente; conexões permanentes/raras ficam atrás):

| Componente | Função | Face do gabinete |
|---|---|---|
| J6 (TRRS) | headset do operador | **frente** |
| SW1-SW5 (via JST-XH + fio) | mute + seleção de notebook | **frente** (chave física fora da placa, ligada por fio ao conector JST; ficam perto do J6, é o que o operador mais mexe) |
| RV1-RV5 (potenciômetro duplo) | volume individual + master | **em cima** (eixo do RK097 aponta pra cima, acessível pelo painel superior) |
| J2-J5 (TRRS) | 4 notebooks (P2) | **atrás** (cabo fica ligado o tempo todo, não precisa ser acessível durante o uso) |
| J1 (USB-C) | entrada de alimentação | **atrás**, junto dos P2 |

Todo o resto (U1, U2, K1-K4, R1-R20, C1-C21, F1, D1-D5, TP1) fica **interno**,
sem restrição de painel.

**Por que essa divisão:** o operador interage com o headset e os seletores
de microfone o tempo todo (frente) e ajusta o volume ocasionalmente (em
cima) - essas ficam nas faces de fácil acesso. Os cabos dos notebooks e a
alimentação são plugados uma vez e raramente mexidos de novo - vão para
trás, fora do caminho.

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

### 3.3.1 Antes de desenhar

- Decida qual caminho de gabinete você vai seguir (ver discussão anterior:
  pronto de catálogo vs. sob medida via PCBWay/JLC3D/JLCMC/sanduíche de
  acrílico). Isso muda o que "certo" significa aqui:
  - **Gabinete pronto**: o contorno precisa bater **exatamente** com as
    dimensões internas do datasheet do gabinete escolhido, incluindo folga
    para nervuras/trilhos internos (ribs) que muitos cases plásticos têm
    perto das bordas - meça ou confira o desenho técnico do fabricante do
    case, não confie só na medida externa.
  - **Gabinete sob medida (depois)**: o contorno pode ser um retângulo
    simples, do tamanho que sobrar depois de posicionar os componentes de
    painel (Fase 3.2) mais uma margem de ~3-5mm em cada lado. O case vai
    ser cortado/impresso sob medida em cima do STEP/Gerber que você
    exportar depois - não precisa acertar de primeira.
- Ajuste o **grid** antes de desenhar: `Ver → Grid Properties` (ou ícone de
  grade na barra lateral), defina 1mm (ou 0.5mm se quiser mais precisão nos
  cantos). Desenhar "a olho" sem grid é a causa mais comum de contorno
  com gaps.

### 3.3.2 Passo a passo no KiCad

1. Na lista de camadas (lado direito, por padrão), clique em **Edge.Cuts**
   para selecioná-la como camada ativa - ela costuma aparecer em amarelo.
2. Use a ferramenta **Add Rectangle** (ícone de retângulo na barra de
   ferramentas da direita, ou tecla de atalho `R`) se o contorno for um
   retângulo simples. Clique num canto, arraste até o canto oposto, clique
   de novo para fechar.
3. Se o contorno **não** for um retângulo simples (ex.: um recorte para os
   jacks ficarem mais pra fora, ou canto chanfrado), use **Add Line**
   (atalho `Alt+L` ou ícone de linha) segmento por segmento, sempre
   fechando no ponto onde começou.
4. **Não confie no clique do mouse para a medida exata.** Depois de
   desenhar aproximadamente, clique com o botão direito em cada segmento
   → **Properties** (ou tecla `E`) e digite os valores exatos de
   **Start X/Y** e **End X/Y** manualmente. É assim que se garante que o
   contorno tem, por exemplo, exatamente 90mm x 60mm, e não "89.7mm porque
   a mão tremeu".
5. Para cantos arredondados (comum em gabinetes sob medida, fica mais
   fácil de imprimir/cortar): no KiCad 7, selecione os dois segmentos que
   formam o canto e use **Edit → Fillet Lines** - digite o raio desejado
   (ex.: 3mm) e ele substitui o canto vivo por um arco automaticamente, já
   com a geometria fechada corretamente.

### 3.3.3 Furos de fixação (mounting holes)

**Aplicado diretamente no `.kicad_pcb`**: 4 footprints `MountingHole_3.2mm_M3`
(furo não-plaqueado 3.2mm, sem net, próprio para parafuso M3), um em cada
canto, com 6mm de margem da borda (dentro da faixa 5-6mm recomendada, sem
colidir com nenhum componente - os 4 cantos estavam livres):

| Referência | Posição (X, Y) | Canto |
|---|---|---|
| MH1 | 66.0mm, 91.0mm | superior esquerdo |
| MH2 | 319.0mm, 91.0mm | superior direito |
| MH3 | 66.0mm, 239.0mm | inferior esquerdo |
| MH4 | 319.0mm, 239.0mm | inferior direito |

(Placa vai de x=60-325mm, y=85-245mm; margem de 6mm em cada eixo a partir
da borda.)

- Se o gabinete já está escolhido, confira se essa posição bate com os
  furos/trilhos de fixação do case antes de fabricar - se não bater, é só
  mover os 4 footprints no KiCad (Properties → X/Y) para a posição certa,
  a geometria do furo em si não muda.
- Se o gabinete é sob medida (depois), essas posições viram a referência
  para o fabricante do case alinhar os furos dele.
- Validado: paren balance do arquivo, nenhuma colisão com footprints
  vizinhos (nenhum outro componente a menos de 20mm de qualquer canto), e
  `kicad-cli pcb export gerbers` limpo.

### 3.3.4 Conferir se o contorno fechou corretamente

Um contorno com gap (não fechado) é o erro mais comum nesta fase, e só
aparece na hora de gerar Gerbers/fabricar se você não checar antes:

1. Rode o DRC (adiantando um pouco a Fase 8, só para o contorno): **Inspect
   → Design Rules Checker → Run DRC**. Um contorno aberto aparece como
   erro do tipo *"board outline"* ou *"Unclosed board outline"*.
2. Alternativa visual: abra a **visualização 3D** (`View → 3D Viewer`, ou
   `Alt+3`) - se o contorno não fechou, a placa aparece "furada" ou com
   formato estranho em vez de uma peça sólida.
3. Só depois de confirmar o contorno fechado e sem erros é que vale a pena
   seguir para a Fase 4 (posicionamento definitivo) com confiança de que a
   geometria da placa está correta.


# Fase 4 - Posicionamento

A ordem abaixo prioriza quem tem restrição mecânica (painel) antes de quem
só tem restrição elétrica - e já foi **aplicada diretamente no
`.kicad_pcb`** (posições exatas por referência, validadas por script:
sem par de componentes com âncoras a menos de 6mm, contorno fechado,
`kicad-cli pcb export gerbers` limpo). Ainda falta a conferência visual
na tela e a Fase 9 (mockup 1:1) antes de considerar definitivo.

1. **J2-J5 (P2) + J1 (USB-C)** - fileira traseira (y=100mm), pitch de
   40mm entre os 4 jacks de notebook; J1 isolado ao lado (x=290mm),
   cluster de POWER (F1, D1, C1, C2, TP1) colado nele.
2. **RV1-RV5 (potenciômetros)** - fileira "em cima" (y=170mm), cada um
   alinhado na mesma coluna X do jack de notebook correspondente
   (RV1 sobre J2, RV2 sobre J3, etc.); RV5 (master) na quinta coluna.
3. **J6 (headset) + SW1-SW5** - fileira frontal: J6 na borda (y=230mm),
   SW1-SW5 logo atrás dele (y=218mm, pitch 15mm) - ficam perto de quem
   eles servem.
4. **K1-K4 + D2-D5 (mic switching)** - perto do grupo SW, mas numa faixa
   própria (y=190/203mm) pra não colidir com eles; K1 alinhado com SW2,
   K2 com SW3, etc.
5. **U1 (mixer) + R1-R12 + C3-C14** - grade 5x5 entre a fileira de trás e
   a fileira de cima (x=75mm, y=118mm em diante, **pitch 15x11mm** - o
   pitch X foi alargado de 13 para 15mm numa segunda rodada, pelo mesmo
   motivo do HPAMP: dava congestionamento demais pro plano de GND
   conectar 2 pads específicos sem violar clearance - ver nota no fim
   desta fase) - é literalmente o meio do caminho do sinal (P2 → volume
   → mixer).
6. **U2 (headphone amp) + R13-R20 + C15-C21** - grade 4x4 perto do J6
   (x=215mm, y=182mm em diante, pitch 12x11mm).

**Coordenadas exatas por referência** estão no `.kicad_pcb` - não há uma
cópia separada aqui porque ela ficaria desatualizada a cada ajuste fino
que você fizer na tela. Se precisar conferir um valor específico, abra o
KiCad e selecione o componente (painel de propriedades mostra X/Y).

**Nota sobre o re-layout do grid do mixer (pitch 13→15mm)**: depois do
primeiro roteamento (Fase 7), o plano de GND ficava com pads presos em
bolsões de cobre isolados do plano principal - a causa era falta de
espaço para o preenchedor de zona (zone filler) colocar um "spoke" legal
até esses pads sem violar clearance com trilhas de sinal vizinhas.
Alargar o pitch X do grid, reposicionar os 25 componentes, e rodar o
Freerouting do zero resolveu C4, R2, C1 e C3 (via stitch manual de GND
+ pequenos desvios em trilhas de sinal vizinhas - NB2_L/NB3_L/NB2_R -
para abrir espaço de verdade, e conexão sólida em vez de solda térmica
para C1/C3). Validado por script (paren balance, contagem de itens não
conectados via `pcbnew`, clearance pad-a-pad e trilha-a-pad por camada,
`kicad-cli pcb export gerbers` limpo) e confirmado por DRC real na tela
a cada rodada.

**Limitação conhecida e aceita: pino 4 do U1 (GND)**. Esse pino
especificamente não tem caminho de cobre disponível para o plano
principal de GND, dentro da folga mínima de fabricação (0.15mm) - só a
via direta no próprio pad, sem conexão ao plano. Causa raiz: num
encapsulamento DIP-8, o pino 4 fica fisicamente entre o pino 3 e o pino
5 (é assim que a numeração do encapsulamento dá a volta), então esse
aperto local é inerente à pinagem do chip, não ao layout ao redor -
confirmado tentando: (a) alargar o pitch X e depois também o Y do grid
do mixer (2 rodadas completas de re-layout + reroteamento), (b) girar o
U1 90° (mesma pinagem, mesmo aperto, só muda a direção), (c) busca
exaustiva por script (A*, bulge de trilha vizinha) não encontrando
nenhum caminho com folga confiável, e (d) tentativa manual na tela pelo
usuário, mesma conclusão. **Solução prática**: jumper manual (fio curto
soldado) do pino 4 do U1 (ou da via já presente ali) até um ponto
acessível do plano de GND, na placa já montada - resolve eletricamente
sem precisar de mais trilha na PCB. O DRC real vai continuar acusando
esse único item; é esperado e esta é a explicação registrada.

**Pendente**: os 6mm de folga usados na validação são só entre âncoras
(centro do footprint), não entre corpos reais - potenciômetro RK097,
relé G5V-1 e jack PJ320D têm corpo maior que isso. Confirme visualmente
antes de rotear.


# Fase 5 - Planejamento do layout (regiões)

Zoneamento **efetivamente aplicado** (Fase 4), organizado por face do
gabinete em vez de por folha do esquemático - mas o princípio de
isolamento de ruído do SCH-008 continua valendo, só que expresso em
frente/trás em vez de lado a lado:

```text
                    ATRÁS (y=100-135)
┌───────────────────────────────────────────────────┐
│  J2 J3 J4 J5        J1          F1 D1 C1 C2 TP1     │  <- P2 + USB-C + POWER
│                                                     │
│  ┌──────────────┐              ┌─────────────┐     │
│  │ AUDIO_MIXER  │              │             │     │
│  │ U1,R1-12,     │              │             │     │
│  │ C3-14         │              │             │     │
│  └──────────────┘              │             │     │
│                                                     │
│  RV1 RV2 RV3 RV4 RV5                                │  <- EM CIMA (y=170)
│                                                     │
│  ┌──────┐                      ┌──────────────┐    │
│  │MIC_SW│                      │ HEADPHONE_AMP│    │
│  │K1-4  │                      │ U2,R13-20,   │    │
│  │D2-5  │                      │ C15-21       │    │
│  └──────┘                      └──────────────┘    │
│  SW1 SW2 SW3 SW4 SW5              J6                │  <- FRENTE (y=218-230)
└───────────────────────────────────────────────────┘
                    FRENTE (usuário)
```

Ideia central, adaptada: **alimentação (POWER) e P2 ficam atrás, longe do
operador; a linha de microfone (MIC_SWITCHING) fica na frente**, perto de
onde ela termina (SW1-SW5) e longe de onde a alimentação entra (atrás).
O caminho de áudio (P2 → volume → mixer → headphone amp → J6) atravessa a
placa de trás pra frente em linha reta, sem cruzar de volta - mesma lógica
de antes (SCH-008), só que a "frente" do gabinete faz o papel de ponta
oposta à alimentação, em vez de uma folha de esquemático específica.


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
  prefira que a corrente da bobina "entre e saia" pela região de POWER
  (atrás), não atravessando por baixo da fileira de P2/pots/mixer no meio
  da placa.


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
2. Antes de rodar, confira **File → Board Setup → Design Rules →
   Constraints** e ajuste **Minimum track width** e **Minimum clearance**
   para um piso de segurança acima do mínimo de fábrica (JLCPCB padrão é
   0.153mm de trilha e 0.127mm de espaçamento).
   **Correção em relação à sugestão original deste guia**: com a placa já
   roteada (Fase 7, via Freerouting), a maioria das trilhas de sinal usa
   0.2mm e o clearance validado a sessão inteira é 0.15mm - usar 0.25mm/
   0.2mm (a sugestão original, escrita antes do roteamento existir) criaria
   ~400 falsos "erro de largura de trilha" em trilhas que já estão
   corretas. Use **0.2mm de trilha mínima e 0.15mm de clearance mínimo**
   em vez disso - ainda folgado acima do mínimo da JLCPCB, mas compatível
   com o que já foi roteado.
3. Clique em **Run DRC**. Corrija um erro de cada vez, rodando de novo
   depois de cada correção - não tente corrigir tudo de uma vez e rodar
   só no final.
4. Erros mais prováveis nesta placa: clearance entre os pads grandes do
   G5V-1/USB-C e trilhas vizinhas, e trilhas não roteadas (net não
   conectada) se algum footprint ficar sem toda trilha ligada.
5. Só considere a Fase 8 concluída com **zero erros e zero warnings não
   justificados** (um warning de "trilha curta" ou similar pode ser
   aceitável, mas documente por quê).

**Warning aceito e documentado**: os 4 furos de fixação (MH1-MH4, Fase
3.3.3) disparam `[extra_footprint]` (severidade warning) porque são
footprints só-mecânicos, adicionados direto no `.kicad_pcb` e sem símbolo
correspondente no esquemático - isso é esperado e seguro para
`MountingHole`, que não tem função elétrica e por isso normalmente não
entra no esquemático. Pode ignorar esse warning específico (@MH1, MH2,
MH3, MH4) sem se preocupar.


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
