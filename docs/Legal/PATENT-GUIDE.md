# Guia de Registro de Patente Internacional — MeetingHub-4

**Versão: 0.1 — Documento educacional, não é aconselhamento jurídico**

---

## Leia isto primeiro: avaliação honesta de patenteabilidade

Antes de qualquer procedimento, é importante avaliar com realismo se este projeto tem chance real de receber uma patente. Baseado na documentação técnica deste repositório (ERS-001, HAD-001, SCH-001 a SCH-009, PCB-001):

O MeetingHub-4 combina blocos de circuito **bem conhecidos e amplamente publicados** — um estágio somador com amplificador operacional para mixagem de áudio, relés para chaveamento de sinal de microfone, um amplificador de fone de ouvido, interfaces TRRS passivas, e alimentação via USB-C — montados de forma direta para atender a uma necessidade específica (gerenciar áudio de 4 notebooks com um headset).

Para que uma **patente de invenção (utility patent)** seja concedida, a maioria dos sistemas de patente no mundo (incluindo o brasileiro, via INPI, e o sistema PCT) exige três critérios cumulativos:

1. **Novidade** — a solução não pode já existir, publicada ou em uso, em nenhum lugar do mundo, antes da data de depósito.
2. **Atividade inventiva / não-obviedade** — a solução não pode ser um passo óbvio para um técnico no assunto, a partir do que já é conhecido.
3. **Aplicação industrial** — a solução precisa ser fabricável/utilizável industrialmente (este critério, isoladamente, o MeetingHub-4 atende sem problema).

**O risco real aqui está nos critérios 1 e 2.** Circuitos somadores com op-amp, chaveamento por relé, e interfaces TRRS são técnicas de eletrônica analógica ensinadas em qualquer curso básico de eletrônica e usadas em produtos comerciais há décadas. Um exame de patente (ou uma busca de anterioridade feita antes do depósito) muito provavelmente encontraria "prior art" (técnica anterior) cobrindo os elementos individuais e, possivelmente, a própria combinação — mixers de áudio multi-fonte com seleção de microfone por relé não são um conceito novo no mercado de áudio profissional/broadcast.

**Isso não significa que não há nada a proteger** — só significa que a proteção mais adequada provavelmente não é uma patente de invenção. Ver seção "Alternativas" abaixo antes de decidir gastar tempo e dinheiro com depósito internacional.

**Recomendação concreta**: antes de gastar qualquer valor com depósito, contrate uma **busca de anterioridade profissional** (patent search) feita por um agente de propriedade industrial registrado. Custa uma fração do valor de um depósito internacional e responde a pergunta central com base em evidência real, não em suposição — inclusive a minha, escrita aqui sem acesso a bases de patentes.

---

## Alternativas de proteção mais adequadas a este tipo de projeto

| Proteção | O que cobre | Custo relativo | Já coberto neste projeto? |
|---|---|---|---|
| **Segredo de negócio (trade secret)** | O próprio arquivo de projeto (esquemático, PCB) mantido confidencial | Baixo (cláusula contratual) | Sim — cláusula 7 do [LICENSE.md](../../LICENSE.md) |
| **Direito autoral (copyright)** | Os arquivos de esquemático/PCB como desenho técnico, e a documentação escrita | Baixo/nenhum (proteção automática na maioria dos países; registro formal reforça a prova de autoria) | Automático desde a criação; considerar registro formal se for comercializar internacionalmente |
| **Marca (trademark)** | O nome comercial do produto ("MeetingHub-4" ou nome de marca real de venda) e/ou logotipo | Médio, por país/classe | Não feito - avaliar antes do lançamento comercial |
| **Desenho industrial (design patent)** | A aparência visual do gabinete/painel, se tiver design próprio e distintivo | Médio | Não aplicável ainda - depende do design do gabinete, que não faz parte deste projeto de hardware eletrônico |
| **Patente de invenção (utility patent)** | Uma solução técnica nova e não-óbvia | Alto (ver abaixo) | Avaliar via busca de anterioridade antes de decidir |

Para a maioria dos produtos de hardware de nicho como este, a combinação **segredo de negócio (proteger os arquivos de projeto) + marca (proteger o nome comercial) + contrato de licença bem redigido** oferece proteção prática mais rápida e barata do que perseguir uma patente com risco real de indeferimento.

---

## Se, mesmo assim, decidir seguir com depósito de patente internacional

### Visão geral do sistema PCT (Patent Cooperation Treaty)

O caminho padrão para buscar proteção em múltiplos países a partir de um único depósito inicial é o **Tratado de Cooperação em Matéria de Patentes (PCT)**, administrado pela OMPI/WIPO. Ele **não concede uma "patente internacional"** (isso não existe como conceito jurídico único) — ele permite reservar prioridade e adiar decisões país-a-país enquanto se avalia o mérito.

**Etapas típicas:**

1. **Depósito prioritário nacional** (opcional, mas comum): depósito inicial no país de origem do requerente (ex.: INPI no Brasil) para estabelecer data de prioridade. A partir daqui, você tem **12 meses** para decidir entrar no PCT reivindicando essa prioridade.
2. **Depósito internacional PCT**: um único pedido, num único idioma, depositado num escritório receptor (ex.: INPI, ou diretamente na OMPI), reivindicando a prioridade do depósito nacional (se houver).
3. **Busca internacional (International Search Report)**: uma autoridade de busca (ex.: INPI, EPO, USPTO, dependendo de onde o pedido foi feito) emite um relatório indicando técnica anterior relevante encontrada — **é aqui que problemas de novidade/atividade inventiva tendem a aparecer publicamente pela primeira vez**.
4. **Publicação internacional**: o pedido é publicado (tornado público) aos 18 meses contados da prioridade mais antiga.
5. **Exame preliminar internacional** (opcional): uma opinião preliminar sobre patenteabilidade, útil para decidir se vale a pena prosseguir.
6. **Entrada em fase nacional**: até **30-31 meses** contados da data de prioridade (o prazo varia por país), o requerente decide em **quais países específicos** quer efetivamente prosseguir com o exame e eventual concessão — cada país então examina e decide independentemente, segundo sua própria lei. **É nesta fase que a maior parte do custo real acontece** (tradução, agentes locais, taxas de exame país a país).

### Prazos-chave (resumo)

| Marco | Prazo a partir da prioridade |
|---|---|
| Depósito PCT reivindicando prioridade nacional | até 12 meses |
| Publicação internacional | 18 meses |
| Entrada em fase nacional (varia por país, ex.: Europa ~31 meses, EUA ~30 meses) | 30-31 meses |

### Custos (ordem de grandeza, **não são valores fixos** — variam por escritório, número de países, e câmbio; consulte um agente para orçamento real)

- Depósito nacional prioritário: baixo a moderado.
- Depósito PCT + busca internacional: moderado (tipicamente alguns milhares de dólares/euros).
- **Fase nacional em cada país** (tradução obrigatória + agente local + taxas): este é o item que mais pesa — cada país escolhido pode custar de forma independente, e escolher 5-10 países pode multiplicar o custo total várias vezes em relação ao depósito PCT inicial.
- Manutenção (anuidades) em cada país concedido, por todo o prazo de vigência.

### Quem procurar

- **Agente de Propriedade Industrial registrado** (no Brasil, credenciado junto ao INPI) para o depósito nacional e orientação sobre PCT.
- **Advogado de patentes (patent attorney)** com atuação internacional, ou uma firma com correspondentes em cada país-alvo, para a fase nacional.
- A própria **OMPI/WIPO** disponibiliza material educacional gratuito sobre o sistema PCT (pesquise "WIPO PCT applicant's guide" diretamente no site oficial da OMPI).

---

## Resumo executivo

1. **Não deposite nada antes de uma busca de anterioridade profissional.** O risco de indeferimento por falta de novidade/atividade inventiva é real e concreto para este tipo de projeto.
2. **Considere se segredo de negócio + marca não resolve melhor e mais barato** o problema de negócio real (impedir cópia direta, proteger o nome comercial).
3. **Se a busca indicar chance real**, o caminho é: depósito nacional prioritário → PCT → entrada em fase nacional nos países de interesse comercial real (não em todos os países do mundo — escolha por onde pretende vender).
4. **Todo esse processo deve ser conduzido por um agente/advogado de patentes habilitado.** Este documento é só um mapa do território, não um substituto para orientação profissional.
