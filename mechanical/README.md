# Gabinete do MeetingHub-4 - v0.1 (rascunho)

Status: **rascunho não verificado visualmente** - eu não tenho nenhuma
ferramenta de CAD 3D disponível neste ambiente (sem OpenSCAD, FreeCAD, e
sem acesso para instalar), então nunca vi este modelo renderizado. Você
precisa abrir no OpenSCAD e conferir antes de mandar imprimir.

Arquivo: [`MeetingHub-4-Case.scad`](MeetingHub-4-Case.scad)


# O que é fato do projeto vs. o que é estimativa minha

**Vem direto do `.kicad_pcb` real (confiável)**:
- Dimensão da placa: 265.1 x 160.1mm
- Posição dos 4 furos de fixação M3 (MH1-4)
- Posição de J1 (USB-C), J2-J5 (TRRS notebooks), J6 (TRRS headset),
  RV1-5 (potenciômetros), SW1-5 (âncoras JST)
- Qual face de gabinete cada componente usa (atrás/frente/em cima) -
  isso já estava decidido e documentado em
  [PCB-001 Fase 3.1](../docs/Architecture/PCB-001-LayoutGuide.md)
  desde o projeto do layout da placa, não é invenção nova.

**São estimativas minhas, sem fonte no projeto (confira antes de
imprimir)**:
- **Altura dos componentes** (`component_clearance` no arquivo,
  20mm): usei valores típicos de datasheet para relé G5V-1 (~15.7mm),
  soquete DIP-8 (~10mm) e capacitor eletrolítico 220µF radial (~16mm) -
  não tenho os datasheets reais abertos, então é uma estimativa de
  "família de peça", não medida exata. Se algum componente for mais
  alto que isso, a tampa não fecha.
- **Tamanho dos recortes dos conectores** (`trrs_cut_*`, `usb_cut_*`):
  fiz recortes **generosos** (tipo janela, não furo justo) porque o
  quanto cada conector realmente projeta para fora da borda da placa
  não está documentado em nenhum arquivo - não dá pra confiar em
  medida de sub-milímetro aqui. Contra-parte: pode sobrar folga
  visível ao redor do conector depois de montado.
- **Diâmetro do furo do eixo do potenciômetro** (`pot_hole_d`, 7mm) e
  **furo das chaves** (`sw_hole_d`, 7mm): valores típicos para
  RK097 e uma mini chave alavanca/pushbutton comum - **as chaves
  físicas (SW1-5) você ainda não escolheu** (elas são ligadas por fio
  via JST, não têm posição fixa na placa), então esse furo é só um
  placeholder até você decidir qual chave física vai usar e me passar
  o diâmetro real do furo dela.


# Como conferir e gerar o arquivo para impressão

1. Instale o [OpenSCAD](https://openscad.org/downloads.html) (gratuito,
   Windows/Mac/Linux).
2. Abra `MeetingHub-4-Case.scad`.
3. Aperte **F5** (preview) para ver o modelo rapidamente, ou **F6**
   (render completo, mais lento mas mais preciso) antes de exportar.
4. O arquivo mostra a base do gabinete e a tampa lado a lado. Gire a
   câmera e confira:
   - Os 4 furos de fixação da placa (postes menores, mais internos)
     batem com os cantos da sua placa real.
   - Os recortes traseiros (J1 + J2-J5) e frontal (J6) parecem na
     posição/tamanho certos.
   - Os 5 furos da tampa (RV1-5) alinham com os potenciômetros.
5. Depois de conferir - **e só depois** - exporte cada peça
   separadamente como STL: no arquivo, comente a linha da peça que não
   quer exportar (adicione `//` na frente) e use **File → Export →
   Export as STL**. Exporte a base e a tampa como dois arquivos STL
   separados (você vai precisar imprimir e enviar os dois).


# Ajustando antes de imprimir

Os parâmetros mais importantes ficam no topo do arquivo, com
comentário explicando cada um:

- `component_clearance`: aumente se algum componente for mais alto que
  o estimado (meça o componente real mais alto acima da placa, mão na
  régua, e use esse valor + uns 2-3mm de folga).
- `sw_hole_d`: troque pelo diâmetro real da chave física que você
  comprar para SW1-5.
- `trrs_cut_*` / `usb_cut_*`: se quiser um recorte mais justo (menos
  folga visível), pode reduzir - mas eu recomendo testar primeiro com
  a folga generosa do rascunho, é mais fácil garantir que encaixa.

Depois de editar qualquer parâmetro, aperte F5/F6 de novo para ver o
efeito antes de reexportar.


# Antes de imprimir o lote inteiro

Como eu não consegui verificar isso visualmente, o mais seguro é:

1. **Imprima só a tampa primeiro** (é a peça mais barata e rápida) e
   confira se os 5 furos de potenciômetro alinham com a placa real
   montada.
2. Se bater, imprima a base e faça um encaixe seco (sem parafusar)
   com a placa de verdade antes de finalizar/pintar/parafusar tudo.
3. Só depois disso pedir a impressão em produção (via PCBWay ou outro
   serviço de impressão 3D) - eles aceitam STL diretamente.

Qualquer ajuste de medida, me avise a medida real que você tirou e eu
atualizo o `.scad`.
