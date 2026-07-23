# MeetingHub-4

Hub analógico de áudio para 4 notebooks, com headset TRRS único e seleção de microfone — sem drivers, sem firmware, sem software.

| | |
|---|---|
| **Status** | Hardware completo — esquemático congelado v1.0, PCB roteada e validada, pronta para fabricação |
| **Versão** | v1.0 |
| **Camadas da PCB** | 4 (F.Cu / In1.Cu GND / In2.Cu +5V_AUDIO / B.Cu) |
| **Licença** | Comercial, com royalty de uso — ver [LICENSE.md](LICENSE.md) |

## O que é

O MeetingHub-4 conecta até 4 notebooks simultaneamente via entrada TRRS 3.5mm (P2), permitindo que o usuário:

- **monitore o áudio das quatro fontes ao mesmo tempo**, com volume individual por notebook e um volume geral;
- **fale em apenas um notebook por vez**, selecionando o microfone do headset com uma chave física;
- **use um único headset TRRS CTIA** (o mesmo do celular), sem adaptador;
- **funcione sem instalar nada** — cada notebook enxerga o equipamento como um headset comum conectado direto no P2.

É um projeto **100% analógico**: sem Bluetooth, sem áudio USB, sem firmware, sem processamento digital. Ver [ERS-001](docs/ERS/ERS-001.md) para a especificação completa de requisitos.

## Estrutura do repositório

```
docs/
  ERS/                    Especificação de requisitos (o que o produto precisa fazer)
  Architecture/           Arquitetura de hardware e projeto do esquemático (HAD, SCH-001 a SCH-009, PCB-001)
  DesignReviews/          Revisões de projeto (DR-001 a DR-003)
  Legal/                  Guia de registro de patente internacional

hardware/
  KiCad/MeetingHub-4/     Projeto KiCad completo (esquemático + PCB, fonte de verdade)
  Schematics/             PDF do esquemático exportado
  BOM/                    Lista de materiais (conceitual e as-built)
  PCB/                    Netlist exportada
  Gerbers/                Gerbers + furação prontos para fabricação (zip pronto para upload)

mechanical/                Modelo 3D do gabinete (OpenSCAD, rascunho v0.1)

production/                Guias de como pedir a fabricação (PCB, gabinete)

LICENSE.md                Licença comercial de uso (com royalty)
CHANGELOG.md              Histórico de marcos do projeto
```

## Por onde começar a ler

1. **[ERS-001](docs/ERS/ERS-001.md)** — o que o equipamento precisa fazer, e por quê.
2. **[HAD-001](docs/Architecture/HAD-001.md)** — como a arquitetura de hardware atende os requisitos.
3. **SCH-001 a SCH-009** (em `docs/Architecture/`) — decisões de projeto elétrico, bloco por bloco (fonte, TRRS, mixer, amplificador de fone, chaveamento de microfone, aterramento).
4. **[DR-001](docs/DesignReviews/DR-001-ArchitectureReview.md), [DR-002](docs/DesignReviews/DR-002-ElectricalArchitectureReview.md), [DR-003](docs/DesignReviews/DR-003-SchematicImplementationReview.md)** — revisões críticas do projeto antes de cada etapa seguinte.
5. **[PCB-001](docs/Architecture/PCB-001-LayoutGuide.md)** — guia completo de layout de PCB (fases 2 a 10), incluindo todas as decisões e correções aplicadas até o estado final.
6. **[BOM-002-AsBuilt](hardware/BOM/BOM-002-AsBuilt.md)** — lista de materiais real, extraída do projeto final.
7. **[TEST-001](docs/Architecture/TEST-001-BringUpGuide.md)** — guia de teste da placa montada, da inspeção visual ao funcionamento completo com os 4 notebooks.
8. **[PCBWay-OrderGuide](production/PCBWay-OrderGuide.md)** — passo a passo para pedir a fabricação da placa no PCBWay.

## Estado do hardware

- Esquemático: 5 folhas (POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP, MIC_SWITCHING), congelado como v1.0.
- PCB: 66 componentes, todos THT, roteada em 4 camadas (planos dedicados de GND e +5V_AUDIO nas camadas internas — ver Fase 6 do PCB-001 para o porquê).
- Validação: 0 pads não conectados, 0 erros de DRC. Único aviso restante é cosmético e documentado (divergência de biblioteca dos potenciômetros RV1-RV5 — ver Fase 8 do PCB-001).
- Arquivos de fabricação: gerados e validados (`kicad-cli pcb export gerbers` limpo). **Ao pedir fabricação, selecione explicitamente placa de 4 camadas.**

## Licenciamento e propriedade intelectual

Este projeto é distribuído sob uma **licença comercial com pagamento de royalty de uso** — ver [LICENSE.md](LICENSE.md) para os termos completos. Não é um projeto de hardware aberto (open source hardware); uso comercial requer licença paga do titular.

Para quem pretende buscar proteção por patente antes de comercializar, ver o **[Guia de Registro de Patente Internacional](docs/Legal/PATENT-GUIDE.md)** — inclui um alerta importante sobre patenteabilidade que deve ser lido antes de iniciar qualquer depósito.

**Nenhum documento deste repositório constitui aconselhamento jurídico.** Tanto a licença quanto o guia de patente são pontos de partida redigidos para revisão por um advogado/agente de propriedade industrial habilitado antes de qualquer uso comercial ou depósito real.
