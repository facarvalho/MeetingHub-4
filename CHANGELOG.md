# Changelog

Histórico de marcos do projeto MeetingHub-4, por fase. Para o histórico linha-a-linha, ver `git log`.

## v1.0 — Hardware completo (fabricação-pronto)

### Definição de requisitos e arquitetura
- Especificação de requisitos (ERS-001) e documento de arquitetura de hardware (HAD-001).
- Diagrama de blocos elétrico (SCH-001) e plano de projeto do esquemático (SCH-002).
- Projeto elétrico detalhado por bloco: fonte (SCH-003), interface TRRS (SCH-004), mixer de áudio (SCH-005), amplificador de headphone (SCH-006), chaveamento de microfone (SCH-007), aterramento e controle de ruído (SCH-008), plano de implementação no KiCad (SCH-009).
- Revisões de arquitetura (DR-001, DR-002) antes da implementação do esquemático.

### Esquemático
- Esquemático completo implementado em 5 folhas (POWER, TRRS_INPUTS, AUDIO_MIXER, HEADPHONE_AMP, MIC_SWITCHING) com footprints atribuídos.
- Revisão de implementação (DR-003), com correções de fidelidade ao projeto elétrico original.
- Esquemático congelado como v1.0 (netlist e PDF gerados).

### Layout de PCB
- Guia de layout completo (PCB-001), cobrindo posicionamento mecânico, zoneamento, plano de terra, roteamento, DRC e preparação para fabricação.
- Posicionamento dos 66 componentes com restrições físicas reais (painel frontal/traseiro/superior).
- Roteamento completo via Freerouting (autorroteador), com ajustes manuais de largura de trilha para as redes de potência.
- Furos de fixação para o gabinete.
- Ground plane e, posteriormente, migração para **placa de 4 camadas** com planos internos dedicados de GND e +5V_AUDIO, eliminando um problema estrutural de conectividade de terra que sobrevivia a duas rodadas de re-layout em 2 camadas.
- Validação final: 0 pads não conectados, 0 erros de DRC (confirmado via relatório de DRC real), silkscreen sem sobreposições, gerbers de 4 camadas exportados e validados.

### Documentação e licenciamento
- Reorganização profissional de toda a documentação do projeto.
- Licença comercial de uso com royalty ([LICENSE.md](LICENSE.md)).
- Guia de registro de patente internacional ([docs/Legal/PATENT-GUIDE.md](docs/Legal/PATENT-GUIDE.md)).
