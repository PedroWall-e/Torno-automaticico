# Resumo dos Projetos de Referência — Torno Automático

Análise dos 4 projetos encontrados em `Referencia/`:

---

## 1. ELS — Electronic Lead Screw (by McMax)

📁 `ELS---Electronic-Lead-Screw-main/`

### Plataforma
- **Microcontrolador:** Arduino UNO (ATmega328P)
- **Linguagem:** C++ (Arduino IDE)
- **Display:** LCD 20×4 caracteres

### Hardware
| Componente | Detalhe |
|---|---|
| Encoder | Incremental com saída em quadratura (A, B) — sem suporte a índice Z |
| Motor | Stepper com driver externo |
| Controle | Joystick analógico (2 eixos) + 3 botões (ESC, SEL, RESET) |
| Alimentação | 12V para Arduino + fonte separada para stepper |

### Funcionalidades
- **Filettatura (rosqueamento):** Passos métricos e imperiais (0.1mm a 2× passo da vite, resolução de 0.05mm), roscas por módulo
- **Avanzamento (avanço):** Modos cent/giro e mm/min
- **Movimento livre** do stepper
- **Leitura de RPM** do mandril
- **Posição angular** do mandril (resolução depende do encoder)
- **Rosca direita/esquerda**
- **Rosca com comprimento definido**
- **Configurações salvas em EEPROM** (passos/volta, passo da vite, caixa norton)

### Arquitetura de Software
- Controle PWM via Timer1 do ATmega328P com `Fast PWM` e `ICR1` como TOP
- Encoder lido por interrupções de hardware (INT0, INT1)
- Array de sequência pré-calculado (até 800 posições) para sincronizar encoder↔stepper
- Aceleração/desaceleração por rampa em software
- Código modular em múltiplos `.ino`: `Avanzamento`, `Filettatura`, `Impostazioni`, `MenuPrincipale`, `MovimentoLibero`, `PosizioneMandrino`, `VelocitaMandrino`, `EEPROM`

### Complexidade
⭐⭐ **Média-baixa** — Projeto mais simples e acessível, bom para entender os fundamentos.

---

## 2. LatheCode

📁 `lathecode-main/`

### Plataforma
- **Ambiente:** Web (TypeScript + Vite)
- **Uso:** Editor online — **não é firmware de controlador**

### O que é
Formato de texto para descrever peças com simetria circular (peças de torno). Define dimensões do material bruto e operações de subtração da direita para a esquerda. Suporta conversão para **GCode** e **STL**.

### Capacidades da Linguagem LatheCode
| Feature | Exemplo |
|---|---|
| Cilindros | `L7 D6` |
| Batentes/ombros | `L2 D4 L7 D6` |
| Cones | `DS14.9 DE17.78` |
| Esferas | `CONV` / `CONC` |
| Elipses | Curvas côncavas e convexas |
| Ferramenta | `TOOL RECT R0.2 L2`, `TOOL ROUND R5`, `TOOL ANG` |
| Profundidade de corte | `DEPTH CUT1 FINISH0.2` |
| Velocidades | `FEED MOVE200 PASS50 PART10` |
| Lotes | Múltiplas peças em sequência |
| Direção dos eixos | `AXES RIGHT DOWN` |
| Modo torneamento | `MODE TURN` / `MODE FACE` |

### Relevância para o Projeto
> [!IMPORTANT]
> LatheCode não é um firmware de ELS — é uma **linguagem de descrição de peças** e um editor web. Porém, é extremamente relevante se o projeto futuro incluir **execução de GCode** ou interface de **planejamento de peças**. O NanoEls H5 já usa LatheCode para gerar GCode via WiFi.

### Complexidade
⭐⭐ **Média** — Projeto web, não embarcado.

---

## 3. MegaEls (DigitalFeed v7e2)

📁 `megaels-main/`

### Plataforma
- **Microcontrolador:** Arduino Mega 2560 (ATmega2560)
- **Linguagem:** C/C++ (Arduino IDE)
- **Display:** LCD 16×2 caracteres
- **Origem:** Projeto russo (ChipMaker.ru), fork por kachurovskiy

### Hardware
| Componente | Detalhe |
|---|---|
| Encoder | 600 linhas/rev (1200 pulsos em quadratura) |
| Motores | 2 steppers (eixo Z = vite madre, eixo X = carro transversal) |
| Controle | 9 botões, joystick de 4 posições com trava, 2 potenciômetros, handwheel MPG (100 pulsos), switch de 8 posições para modo |
| LEDs | 4 indicadores de limites |
| Buzzer | 5V |
| PCB | PCB dedicada com Gerber disponível (JLCPCB ~20€) |
| Case | Case 3D printável (STL + F3D) |

### Funcionalidades
- **2 eixos** (Z longitudinal + X transversal)
- **Rosqueamento:** Tabela pré-calculada com passos métricos (0.25mm–4mm) e imperiais (6–80 TPI), multi-start
- **Avanço síncrono:** mm/rev, controlado por potenciômetro
- **Avanço assíncrono:** mm/min (para retífica)
- **Cones:** Tabela com Morse Taper 0–6, ângulos comuns (1:4 a 1:50, 8° a 45°)
- **Esferas**
- **Divisor angular**
- **Limites suaves** (soft limits) nos 4 lados com LEDs indicadores
- **Rosqueamento automático** (com limites configurados)
- **Compensação de backlash** (folga) em X e Z
- **Controle de aceleração/desaceleração** configurável
- **Sub-modos:** Interno, Manual e Externo para cada modo

### Arquitetura de Software
- Manipulação direta de registradores AVR (PORTL, PIND, etc.) para máxima velocidade
- Múltiplos timers do Mega2560 usados simultaneamente:
  - Timer2: Movimento rápido (rapid)
  - Timer3: Handwheel (MPG)
  - Timer4: Avanço assíncrono
  - Timer5: Avanço síncrono
- Interrupções de hardware (INT0) para leitura do encoder do mandril
- Interrupção separada (INT2) para handwheel
- Tabelas pré-calculadas para roscas e cones (recalcular com `tables.html` ao mudar hardware)
- Flags via registradores GPIO do AVR para performance
- Código modular: `Thread.ino`, `Feed.ino`, `aFeed.ino`, `Cone.ino`, `Sphere.ino`, `HandCoder.ino`, `Menu.ino`, `ADC.ino`, `Beeper.ino`, `Print.ino`

### Complexidade
⭐⭐⭐⭐ **Alta** — Código denso com manipulação direta de hardware, múltiplos timers e interrupções.

---

## 4. NanoEls (H2 / H4 / H5)

📁 `nanoels-main/`

### Plataforma
Projeto com **3 gerações de hardware**:

| Versão | MCU | Display | Eixos |
|---|---|---|---|
| **H2** | Arduino Nano (ATmega328P) | — | 1 (Z) |
| **H4** | ESP32-S3 | — | Até 4 |
| **H5** | ESP32-S3 (N16R8) | Nextion 5" Touch | Até 3 |

### Hardware (H5 — versão mais avançada)
| Componente | Custo | Detalhe |
|---|---|---|
| Display | 67€ | Nextion NX8048P050 — 5" touchscreen colorido |
| MCU | 5€ | ESP32-S3 N16R8 |
| Level Shifter | 2€ | 2× SN74HCT245N |
| Terminais | 6€ | KF2EDG 3.5mm |
| PCB | 5€ | Personalizada (JLCPCB) |
| Teclado | 19€ (opcional) | Mini PS2 |
| **Total** | ~100€ | |

### Funcionalidades (H5)
- **Modos completos:**
  - 🔧 Gearbox (ELS clássico)
  - 🔩 Torneamento automático multi-passe
  - 🔩 Faceamento automático multi-passe
  - 📐 Cones (razão constante X/Z)
  - ✂️ Corte (parting) automático
  - 🧵 Rosqueamento automático multi-passe (inclusive multi-start e cônico)
  - 🔴 Semi-esferas e semi-elipses automáticas
  - ⚡ Modo assíncrono (velocidade constante, independente do mandril)
  - 📄 **GCode via WiFi** — upload via navegador web!
- **Controle sofisticado:**
  - Tela touch + teclado PS2
  - Handwheels (MPG) para Z e X
  - Limites suaves configuráveis nos 4 sentidos
  - Compensação de backlash
  - Sistema métrico, imperial e TPI
  - Zeragem de eixos com offset
  - Micro-stepping fino
  - Passes de acabamento mais rasos automaticamente
- **Conectividade:** WiFi para upload de GCode + interface web
- **Firmware:** Arquivo único `h5.ino` com ~130KB (≈3500+ linhas)

### Complexidade
⭐⭐⭐⭐⭐ **Muito alta** — Projeto mais completo e sofisticado. Referência principal.

---

## Tabela Comparativa

| Característica | ELS (McMax) | LatheCode | MegaEls | NanoEls H5 |
|---|---|---|---|---|
| **MCU** | Arduino UNO | Web (TS) | Arduino Mega | ESP32-S3 |
| **Eixos** | 1 (Z) | N/A | 2 (Z+X) | 3 (Z+X+Y) |
| **Display** | LCD 20×4 | Browser | LCD 16×2 | Nextion 5" Touch |
| **Roscas** | Métrica+Imperial+Módulo | N/A | Métrica+Imperial | Métrica+Imperial+TPI |
| **Avanço sync** | ✅ | N/A | ✅ | ✅ |
| **Avanço async** | ❌ | N/A | ✅ | ✅ |
| **Cones** | ❌ | ✅ (desc.) | ✅ | ✅ |
| **Esferas** | ❌ | ✅ (desc.) | ✅ | ✅ |
| **GCode** | ❌ | ✅ (gerador) | ❌ | ✅ (WiFi) |
| **Automação multi-passe** | ❌ | N/A | ✅ (parcial) | ✅ (completa) |
| **Rosca multi-start** | ❌ | N/A | ✅ | ✅ |
| **Soft limits** | ❌ | N/A | ✅ | ✅ |
| **Backlash comp.** | ❌ | N/A | ✅ | ✅ |
| **WiFi** | ❌ | N/A | ❌ | ✅ |
| **Handwheel (MPG)** | ❌ | N/A | ✅ | ✅ |
| **PCB dedicada** | ❌ | N/A | ✅ | ✅ |
| **Case 3D** | ❌ | N/A | ✅ | ✅ |
| **Custo estimado** | ~30€ | Grátis | ~80€ | ~100€ |

---

## Lições e Padrões Relevantes

> [!TIP]
> ### Padrões comuns entre os projetos:
> 1. **Encoder em quadratura** para sincronizar mandril ↔ vite madre
> 2. **Tabelas pré-calculadas** para roscas e cones (evitar divisão float em tempo real)
> 3. **Interrupções de hardware** para leitura de encoder (não usar polling!)
> 4. **Timer PWM dedicado** para gerar pulsos STEP do stepper
> 5. **Aceleração por rampa** no stepper para evitar perda de passo
> 6. **Compensação de backlash** essencial para precisão em troca de direção

> [!IMPORTANT]
> ### Decisões de arquitetura para o nosso projeto:
> - **Se 1 eixo e simples:** ELS (Arduino UNO) é suficiente como base
> - **Se 2 eixos sem WiFi:** MegaEls (Arduino Mega) é a melhor referência
> - **Se solução completa e moderna:** NanoEls H5 (ESP32-S3) é o caminho — WiFi, touch, GCode, 3 eixos
> - **Se quiser interface de planejamento de peças:** Integrar LatheCode para geração de GCode
