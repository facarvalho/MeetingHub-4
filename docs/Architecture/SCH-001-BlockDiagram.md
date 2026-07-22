# SCH-001 - Electrical Block Diagram

Version: 0.1  
Status: Draft

---

# 1. Objetivo

Este documento descreve o diagrama funcional de blocos do hardware do MeetingHub-4.

O objetivo é definir a arquitetura elétrica antes do desenvolvimento do esquemático detalhado.

---

# 2. Visão Geral

O MeetingHub-4 é um equipamento analógico que permite conectar quatro notebooks simultaneamente utilizando interfaces headset TRRS CTIA.

Funções principais:

- receber áudio de quatro notebooks;
- misturar os sinais de áudio em estéreo;
- disponibilizar monitoramento em um único headset;
- selecionar qual notebook receberá o sinal do microfone;
- manter compatibilidade nativa com a detecção de headset dos notebooks.

---

# 3. Diagrama Geral

```text
                 ÁUDIO

+------------+
| Notebook 1 |
+------------+
      |
      |
+------------+
| Notebook 2 |
+------------+
      |
      |
+------------+
| Notebook 3 |
+------------+
      |
      |
+------------+
| Notebook 4 |
+------------+
      |
      |
      v

+---------------------------+
| Entradas TRRS CTIA        |
| Separação L / R / MIC     |
+---------------------------+

      |
      |
      v

+---------------------------+
| Controle Volume Individual|
| VOL1 VOL2 VOL3 VOL4       |
+---------------------------+

      |
      |
      v

+---------------------------+
| Mixer Estéreo Ativo       |
| Canal L + Canal R         |
+---------------------------+

      |
      |
      v

+---------------------------+
| Volume Master             |
+---------------------------+

      |
      |
      v

+---------------------------+
| Amplificador Headphone    |
+---------------------------+

      |
      |
      v

+---------------------------+
| Headset TRRS CTIA         |
+---------------------------+
````

---

# 4. Caminho do Microfone

O caminho do microfone deverá permanecer transparente para o notebook.

Não será utilizado processamento ativo na linha do microfone.

```text
+----------------+
| Headset MIC    |
+----------------+
        |
        |
        v

+----------------+
| MUTE           |
+----------------+
        |
        |
        v

+----------------+
| Seleção MIC    |
| Notebook 1-4   |
+----------------+
        |
        |
        v

+----------------+
| Notebook       |
| Selecionado    |
+----------------+
```

---

# 5. Seleção do Microfone

A seleção do microfone será realizada através de chaveamento de sinal.

Requisitos:

* baixa resistência de contato;
* mínima interferência;
* preservação da polarização do microfone;
* operação confiável em uso intenso.

Solução inicial:

* relés de sinal de alta durabilidade.

---

# 6. Alimentação

Fonte externa:

```text
USB-C 5V

     |
     v

+----------------+
| Proteção       |
+----------------+

     |
     v

+----------------+
| Filtragem      |
+----------------+

     |
     v

+----------------+
| Alimentação    |
| Circuitos Áudio|
+----------------+
```

---

# 7. Aterramento

O projeto utilizará uma estratégia de aterramento em estrela.

Objetivos:

* minimizar ruído;
* reduzir loops de terra;
* melhorar imunidade a interferências.

Estrutura:

```text
Entradas Áudio
      |
      |
      v
GND_AUDIO

      |
      |
Ponto estrela

      |
      |
Alimentação
```

---

# 8. Subsistemas

## 8.1 Entradas TRRS

Quantidade:

* 4 entradas notebook;
* 1 saída headset.

Padrão:

* CTIA;
* 3,5 mm;
* TRRS.

---

## 8.2 Mixer de Áudio

Características:

* estéreo;
* ativo;
* baixo ruído;
* controle individual por entrada.

---

## 8.3 Amplificador de Headphone

Responsável por:

* fornecer corrente adequada ao headset;
* manter qualidade de áudio;
* evitar sobrecarga das saídas dos notebooks.

---

## 8.4 Microfone

Características:

* conexão direta ao notebook selecionado;
* sem conversão digital;
* sem processamento;
* compatibilidade com detecção nativa de headset.

