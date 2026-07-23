# Guia PCBWay - Como pedir a fabricação da placa (para iniciante)

Version: 1.0
Status: Final

Guia passo a passo para pedir a fabricação da PCB do MeetingHub-4 no
PCBWay (pcbway.com), escrito para quem nunca fez isso antes. Os valores
técnicos abaixo (tamanho, camadas, espessura) são os valores **reais**
extraídos do projeto final - use-os para conferir se o site detectou
tudo certo, não precisa saber o que significam para seguir o guia.

**Arquivo a enviar**: [`hardware/Gerbers/MeetingHub-4-Gerbers-v1.0.zip`](../hardware/Gerbers/MeetingHub-4-Gerbers-v1.0.zip)
(já contém gerbers de todas as camadas + furação, pronto para upload).


# Ficha técnica da placa (para conferir contra o que o site detectar)

| Item | Valor |
|---|---|
| Dimensões | 265.1 x 160.1 mm |
| Camadas | **4** |
| Espessura final | 1.6 mm |
| Material | FR-4 (padrão) |
| Furo mínimo | 0.6 mm (dentro do padrão, não precisa de opção especial) |
| Cor da máscara de solda | à sua escolha (verde é o padrão mais barato/rápido) |
| Cor da serigrafia | branco (padrão) |
| Acabamento de superfície | HASL (com chumbo) recomendado - mais barato, e a placa é 100% THT (solda manual), não precisa de ENIG |
| Peso do cobre | 1oz (padrão) |
| Quantidade sugerida | 5 unidades (mínimo comum do PCBWay para protótipo; sobra placa para erro de montagem) |


# Passo a passo

## 1. Criar conta

Acesse [pcbway.com](https://www.pcbway.com) e crie uma conta (e-mail +
senha, ou login via Google). Não precisa de CNPJ nem nada de empresa -
conta pessoal serve.

## 2. Abrir o orçamento instantâneo de PCB

No menu superior, procure **"PCB Instant Quote"** (ou "Quote Now" na
página inicial, seção PCB). Isso abre o formulário de configuração da
placa.

## 3. Enviar o arquivo de gerbers

No formulário, tem um botão **"Add Gerber File"** (ou "Upload
Gerber"). Envie o arquivo `MeetingHub-4-Gerbers-v1.0.zip` (não precisa
descompactar, o site aceita o zip direto).

O PCBWay tenta detectar automaticamente tamanho e número de camadas a
partir do arquivo. **Confira**:
- **Dimension**: deve aparecer algo próximo de `265.1 x 160.1 mm`. Se
  aparecer um valor bem diferente, o upload provavelmente falhou -
  tente reenviar antes de continuar.
- **Layer**: deve estar em **4**. Se aparecer 2, o site não leu as
  camadas internas direito - não prossiga, me avise.

Se por algum motivo o site não detectar automaticamente, preencha
manualmente com os valores da tabela acima.

## 4. Conferir/ajustar as opções de fabricação

Na mesma tela (ou na aba "Specification"), confira cada campo contra a
tabela técnica acima. Os campos mais importantes:

- **Layers**: 4
- **Material**: FR-4
- **Thickness**: 1.6mm
- **Min Track/Spacing**: pode deixar no padrão do site (6/6mil) - o
  projeto não usa nada mais fino que isso.
- **Min Hole Size**: pode deixar no padrão (0.3mm) - o menor furo do
  projeto é 0.6mm, folgado.
- **Solder Mask**: escolha a cor que preferir (verde é o padrão, mais
  barato e rápido; outras cores podem custar um pouco mais/demorar
  mais).
- **Silkscreen**: branco (padrão).
- **Surface Finish**: **HASL(with lead)** - mais barato, funciona bem
  para solda manual (que é como este protótipo foi projetado para ser
  montado, com soquete nos CIs U1/U2).
- **Via Process**: **Tenting vias** (padrão, mais barato).
- **Board Outline Tolerance**: pode deixar padrão.
- Todo o resto (Panelization, Castellated Holes, Edge Plating,
  etc.): **não marque nenhuma opção extra** - este projeto não precisa
  de nenhuma delas.

## 5. Quantidade

Escolha a quantidade (sugestão: **5 unidades** - é o mínimo comum do
PCBWay para essa faixa de tamanho, e é bom ter placas sobrando caso
algo dê errado na primeira montagem/solda).

## 6. Montagem (PCBA) - **não contrate**

O PCBWay vai oferecer, na mesma tela ou logo depois, um serviço de
**montagem automática dos componentes (PCBA)**. **Não é necessário
para este projeto**: todos os 75 componentes são THT (through-hole),
pensados para montagem manual (o BOM inclusive recomenda usar soquete
nos CIs U1/U2 - ver [BOM-002-AsBuilt](../hardware/BOM/BOM-002-AsBuilt.md)),
e contratar montagem automática custaria bem mais caro sem necessidade.
Peça só a **placa nua (bare PCB)**.

## 7. Adicionar ao carrinho e revisar o preço

Depois de confirmar as opções, clique em **"Add to Cart"** (ou
similar) e revise o preço final antes de continuar - ele muda conforme
cor da máscara, acabamento e quantidade escolhidos.

## 8. Pagamento e frete

Escolha a forma de envio (o PCBWay geralmente oferece algumas opções
de transportadora com preço/prazo diferentes - a mais barata costuma
levar bem mais tempo para chegar ao Brasil). Finalize o pagamento
(cartão de crédito internacional costuma ser aceito diretamente).

**Atenção a impostos de importação**: por vir de fora do Brasil, pode
haver retenção na alfândega e cobrança de imposto (ICMS + taxas) na
entrega, dependendo do valor declarado e da transportadora escolhida -
isso é uma questão de importação, não do PCBWay em si; se nunca
importou nada, vale pesquisar como funciona antes de finalizar (ex.:
o programa Remessa Conforme, se a loja estiver cadastrada).

## 9. Acompanhar o pedido

O PCBWay envia atualizações por e-mail em cada etapa (produção,
inspeção, envio, código de rastreio). O prazo de fabricação padrão
costuma ser alguns dias úteis (varia com a fila de produção); frete
internacional costuma ser o item mais demorado do processo todo.


# Quando a placa chegar

1. Confira visualmente contra a Fase 1 do [TEST-001](../docs/Architecture/TEST-001-BringUpGuide.md)
   antes de montar qualquer componente (checando também se a
   serigrafia/furos batem com o esperado).
2. Siga o [TEST-001](../docs/Architecture/TEST-001-BringUpGuide.md) na
   ordem (inspeção visual → continuidade → primeira energização →
   teste funcional) para montar e validar a placa com segurança.


# Nota sobre este guia

A interface do site do PCBWay muda de tempos em tempos (nomes de botão,
posição de campo). Se algum passo não bater exatamente com o que você
vê na tela, **confira sempre contra a ficha técnica no topo deste
documento** (esses valores são os reais, extraídos do arquivo final do
projeto) em vez do texto do passo a passo, e me avise se algo parecer
estranho antes de finalizar o pedido.
