# DR-002 - Electrical Architecture Review

Version: 0.1
Status: Review


# 1. Objetivo

Revisar a arquitetura elétrica definida antes do início do desenvolvimento do esquemático no KiCad.


# 2. Escopo Revisado

Foram avaliados:

- interface TRRS CTIA;
- caminho de áudio;
- mixer estéreo;
- amplificador de headphone;
- seleção de microfone;
- alimentação;
- controle de ruído.


# 3. Decisões Aprovadas


## Interface

Aprovado:

- TRRS CTIA;
- conectores metálicos de painel;
- compatibilidade nativa com notebooks.


## Áudio

Aprovado:

- quatro entradas independentes;
- mixer estéreo ativo;
- controle individual de volume;
- volume master.


## Microfone

Aprovado:

- chaveamento por relé;
- ausência de eletrônica ativa na linha MIC;
- seleção de um notebook por vez.


## Alimentação

Aprovado:

- USB-C 5V;
- filtragem;
- proteção;
- separação de áudio e alimentação.


## Ruído

Aprovado:

- aterramento em estrela;
- atenção ao layout da PCB;
- testes com diferentes carregadores.


# 4. Pontos de Atenção

Durante o desenvolvimento do protótipo deverão ser avaliados:

- ruído entre notebooks;
- compatibilidade com diferentes codecs de áudio;
- comportamento da detecção de headset;
- qualidade do chaveamento do microfone.


# 5. Status

Arquitetura aprovada para desenvolvimento do esquemático.


