# TEST-001 - Guia de Teste e Bring-Up da Placa

Version: 1.0
Status: Final

Guia prático para testar a placa montada, na ordem certa - dos testes mais
seguros (sem energizar) até o funcionamento completo com os 4 notebooks.
**Siga a ordem**: cada fase só deve começar depois que a anterior passar
limpa - é assim que se evita queimar componente por um erro de montagem
que passaria despercebido se você ligasse tudo de uma vez.


# Fase 1 - Inspeção visual (antes de qualquer energia)

Com a placa montada e **nada conectado na alimentação**, confira com uma
lupa/boa luz:

1. **Solda**: sem pontos frios (aspecto fosco/rachado), sem bolhas de
   estanho encostando em pad vizinho (curto), sem falta de solda em nenhum
   pino.
2. **Polaridade dos componentes polarizados** - o mais importante desta
   fase, porque inverter qualquer um destes **queima o componente ou o
   resto da placa** ao ligar:
   - **C17, C20** (220µF, eletrolíticos): a faixa/traço no corpo do
     capacitor marca o **negativo** - confira contra a serigrafia da
     placa antes de energizar.
   - **C2, C3, C16, C19** (10µF, eletrolíticos): mesma lógica.
   - **D1** (TVS, proteção): tem polaridade - confira orientação da faixa
     catodo contra a serigrafia.
   - **D2-D5** (1N4148): a faixa no corpo marca o catodo - confira contra
     a marcação "K" na serigrafia (ver PCB-001 Fase 8, essas marcações
     foram reposicionadas para não ficarem cortadas).
   - **U1, U2** (DIP-8): o entalhe/ponto no corpo do CI marca o pino 1 -
     confira contra o desenho na serigrafia antes de encaixar no soquete
     (se estiver usando soquete, como recomendado no BOM-002 para
     protótipo).
   - **J1** (USB-C): conector é mecanicamente "chaveado", só encaixa de um
     jeito - mas confira que a solda dos terminais SMD/THT do conector
     está firme, ele recebe estresse mecânico toda vez que um cabo é
     plugado.
3. **Sem curto visível** entre trilhas/pads adjacentes, principalmente na
   área do U1 (grade densa do mixer) e do J1 (USB-C, pinos finos).


# Fase 2 - Teste de continuidade (multímetro, ainda sem energia)

Com o multímetro em modo **continuidade/resistência**, placa ainda **sem
USB conectado**:

1. Meça entre **TP1** (+5V_AUDIO) e **TP2** (GND). Deve mostrar
   **circuito aberto** (sem continuidade, resistência alta/infinita, não
   um bipe de curto). Se der continuidade direta (0Ω ou bipe de curto),
   **não conecte a alimentação** - há um curto entre alimentação e terra
   que precisa ser encontrado e corrigido primeiro (revise solda perto de
   J1, D1, F1, C1).
2. Confira continuidade do fusível **F1** isoladamente (as duas pontas do
   próprio fusível) - deve haver continuidade (fusível bom, ainda não
   queimado).

Só avance para a Fase 3 depois que os dois itens acima estiverem OK.


# Fase 3 - Primeira energização

1. Conecte um cabo USB-C **de dados/energia simples** (não um carregador
   de notebook com Power Delivery em voltagem alta - o ideal é uma fonte
   USB-A→C ou um carregador de celular simples, 5V) na entrada J1.
   **Não conecte nenhum notebook ou headset ainda.**
2. **Cheire e observe** nos primeiros segundos - se sentir cheiro de
   queimado ou ver fumaça, **desconecte imediatamente** e revise a Fase 1
   e 2 antes de tentar de novo.
3. Com o multímetro em modo tensão DC, meça **TP1 em relação a TP2**:
   deve ler próximo de **5V** (tipicamente 4.8-5.2V, já que não há
   regulador nesta placa - a tensão de +5V_AUDIO é a própria tensão de
   entrada do USB, só protegida por fusível e TVS, ver DR-003).
4. Toque de leve no corpo do **U1** e **U2** (os dois CIs DIP-8) depois
   de uns 30 segundos ligado - devem estar em temperatura ambiente/mornos
   no máximo. Se algum estiver **quente a ponto de incomodar o dedo**,
   desligue e revise a orientação do CI (pino 1) e a tensão de
   alimentação dele.
5. Meça a tensão de **VBIAS**: essa é a referência de meio-sinal do
   mixer, gerada por um divisor resistivo R1/R2 (10k/10k) na folha
   MIXER - meça no ponto de junção entre R1 e R2 (ou direto nos pinos 3/5
   do U1, que recebem VBIAS). Deve ler aproximadamente **metade da
   tensão de TP1** (≈2.5V se TP1 leu 5V). Se ler muito diferente disso
   (perto de 0V ou perto de 5V), há um problema no divisor R1/R2 ou em
   uma solda fria num deles.

Se os 3 pontos de tensão (TP1 ≈5V, VBIAS ≈ metade de TP1, GND=0V de
referência) baterem, a alimentação está saudável - prossiga.


# Fase 4 - Teste funcional (com notebooks e headset)

Agora sim, com a placa energizada e validada eletricamente:

1. **Um notebook por vez primeiro** - conecte o cabo do notebook 1 em
   **J2**, e o headset em **J6**. Toque um áudio de teste no notebook
   (ex.: um vídeo qualquer) e confirme que ouve no headset.
2. Repita isoladamente para **J3** (notebook 2), **J4** (notebook 3),
   **J5** (notebook 4) - cada um sozinho primeiro, antes de testar todos
   juntos.
3. **Volume individual**: gire cada potenciômetro **RV1** (NB1), **RV2**
   (NB2), **RV3** (NB3), **RV4** (NB4) e confirme que controla o volume
   daquele notebook especificamente, sem afetar os outros.
4. **Volume geral**: gire **RV5** (master) e confirme que afeta o volume
   de todos simultaneamente.
5. **Monitoramento simultâneo**: com os 4 notebooks tocando áudio ao
   mesmo tempo, confirme que ouve a mistura dos 4 no headset (esse é o
   critério de aprovação RF-003 do ERS-001).
6. **Seleção de microfone**: acione as chaves **SW2** (seleciona NB1),
   **SW3** (NB2), **SW4** (NB3), **SW5** (NB4) uma de cada vez - fale no
   microfone do headset e confirme, no software de chamada/gravação de
   cada notebook, que **apenas o notebook selecionado** recebe o áudio do
   microfone. Você deve ouvir o relé correspondente (**K1-K4**) fazer um
   pequeno "clique" mecânico ao trocar de seleção - isso é esperado e
   normal.
7. **MUTE**: acione **SW1** e confirme que o microfone é cortado
   independente de qual notebook estava selecionado.
8. **Reconhecimento sem driver**: em cada notebook, confirme que o
   sistema operacional reconhece a conexão como um headset TRRS comum
   (ícone de fone/microfone padrão), sem pedir instalação de driver nem
   abrir nenhum aviso - este é o critério RF-008/Seção 3 do ERS-001.


# Fase 5 - Teste de durabilidade (opcional, mas recomendado antes de uso intenso)

O ERS-001 define meta de **>1 milhão de operações** do seletor de
microfone. Não é viável testar isso manualmente antes do uso normal, mas
vale, antes de considerar o protótipo aprovado para uso diário:

- Acionar cada chave de seleção (SW2-SW5) umas 50-100 vezes seguidas,
  confirmando que o relé correspondente continua comutando de forma
  limpa (sem áudio "chiando" ou cortando de forma intermitente no
  meio da troca).
- Deixar a placa ligada por algumas horas contínuas, revisitando a Fase 3
  passo 4 (temperatura de U1/U2) periodicamente.


# O que fazer se algo falhar

| Sintoma | Onde olhar primeiro |
|---|---|
| TP1 não mostra ~5V | Fusível F1 (queimado?), solda do J1 (USB-C), curto detectado na Fase 2 |
| VBIAS muito longe de TP1/2 | Solda fria em R1 ou R2 (folha MIXER) |
| Um notebook específico não toca áudio | Solda do jack correspondente (J2-J5), continuidade do cabo TRRS usado |
| Áudio de um notebook vaza pros outros / mixagem estranha | Revisar U1 (orientação, solda), esse é o CI que faz a soma dos 4 sinais |
| Fone não toca nada | U2 (amplificador de headphone) - orientação, solda, ou VBIAS incorreto chegando nele |
| Seleção de microfone não troca | Relé correspondente (K1-K4) - solda, ou chave física ligada no JST errado (confira SW2→K1, SW3→K2, SW4→K3, SW5→K4) |
| MUTE não corta | SW1, revisar fiação até o JST |
| Notebook pede driver / não reconhece como headset | Confira pinagem do plugue TRRS do headset real contra o padrão CTIA (ponta=L, anel1=R, anel2=MIC, base=GND) - um plugue fora do padrão CTIA (ex.: OMTP) engana o notebook |
