# Próxima etapa: criar o projeto KiCad

Entre no diretório:

```bash
cd ~/MeetingHub-4/hardware/KiCad
```

Crie a pasta:

```bash
mkdir MeetingHub-4
cd MeetingHub-4
```

Abra o KiCad e crie o projeto:

Nome:

```text
MeetingHub-4
```

Local:

```text
~/MeetingHub-4/hardware/KiCad/MeetingHub-4/
```

---

Depois de criado, sua árvore deverá ficar parecida com:

```text
hardware
└── KiCad
    └── MeetingHub-4
        ├── MeetingHub-4.kicad_pro
        ├── MeetingHub-4.kicad_sch
        └── MeetingHub-4.kicad_pcb
```

---

# Primeira folha do esquemático

Vamos começar pela alimentação.

No KiCad vamos criar:

```
Sheet: Power Supply
```

Componentes iniciais:

| Referência | Componente        | Função     |
| ---------- | ----------------- | ---------- |
| J1         | USB-C             | Entrada 5V |
| F1         | Fusível resetável | Proteção   |
| D1         | TVS/Proteção      | Surto      |
| C1         | 100nF             | Filtro     |
| C2         | 10uF              | Reserva    |
| J2         | Test Point        | Medição    |

Barramentos:

```
+5V_USB
    |
    |
Proteção
    |
    |
+5V_AUDIO
    |
    |
Circuitos
```

---

# Antes de colocar componentes

Uma decisão importante:

No seu caso, eu **não usaria USB-C com negociação PD**.

Usaremos USB-C apenas como entrada de energia:

* VBUS = 5V
* GND = retorno

Motivo:

* mais simples;
* mais barato;
* menos pontos de falha.

---

# Próximo passo no KiCad

Quando abrir o esquemático:

1. Crie uma folha hierárquica chamada:

```
POWER
```

2. Coloque o primeiro símbolo:

```
USB_C_Receptacle_USB2.0_16P
```

3. Depois faremos a proteção.

---

Quando você criar o projeto KiCad, me envie apenas o resultado do:

```bash
tree hardware/KiCad
```

ou uma captura da tela do KiCad.

Aí seguimos componente por componente. Agora começamos a construção real do MeetingHub-4. 🔧
