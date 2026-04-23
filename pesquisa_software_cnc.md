# Pesquisa: Software CNC para Torno — O que já existe?

## Resumo Rápido

> [!IMPORTANT]
> Existem **3 caminhos** para o nosso projeto. A recomendação é um **sistema híbrido**:
> usar o **grblHAL** ou firmware próprio (baseado no NanoEls) no ESP32 para controle
> de tempo real, e o **Raspberry Pi** rodando uma interface própria inspirada no
> GMOCCAPY/LinuxCNC para visão, GUI e GCode.

---

## Softwares CNC Existentes para Torno

### ⚙️ Nível 1 — Controladores Completos (Software = Firmware + GUI)

Estes são sistemas que controlam a máquina inteira. O software roda em um PC/Pi
e gera os pulsos para os motores diretamente.

---

#### 1. 🏆 LinuxCNC — O Padrão da Indústria

📎 https://linuxcnc.org  
📄 GPL | 🐧 Linux (Debian) | 💻 PC x86 ou Raspberry Pi

**O que é:** Sistema completo de controle CNC (não é "gcode sender", é o
controlador inteiro). Roda em Linux com kernel tempo real.

**Funcionalidades para Torno:**
| Feature | Suporte |
|---|---|
| Threading (G33, G76) | ✅ Nativo, robusto |
| Constant Surface Speed (CSS) | ✅ G96/G97 |
| Multi-pass threading | ✅ G76 com spring passes |
| Facing, turning, contouring | ✅ Completo |
| Encoder spindle sync | ✅ Nativo com index pulse |
| Soft limits | ✅ |
| Backlash compensation | ✅ |
| Tool table com offsets | ✅ Nativo |
| Canned cycles (G70-G76) | ✅ |
| Custom M-codes (Python) | ✅ |

**GUIs para Torno (touchscreen):**

| GUI | Detalhe | Touch? |
|---|---|---|
| **GMOCCAPY** | Interface moderna, botões grandes, modo torno nativo | ✅ Projetada para touch |
| **Touchy** | Minimalista, feita para usar SEM mouse/teclado | ✅ Otimizada |
| **AXIS** | Interface clássica, mais completa mas requer mouse | ⚠️ Parcial |
| **Probe Basic** | Interface mais bonita (QtPyVCP), mas precisa x86 | ✅ Mas NÃO roda em RPi |

**Raspberry Pi:**
- ✅ Roda no Pi 4 e Pi 5 com imagem oficial
- ⚠️ Para melhor performance: usar placa Mesa Ethernet (7i96S ~100€) que gera os pulsos em hardware dedicado
- ⚠️ Sem placa Mesa: pode gerar pulsos via GPIO mas com limitações de velocidade

**Prós:**
- Sistema mais completo e testado do mundo para CNC
- Suporte nativo a torno com threading perfeito
- Enorme comunidade e documentação
- Extensível com Python e HAL

**Contras:**
- **Complexo de configurar** (HAL files, INI files)
- **NÃO é um firmware de microcontrolador** — precisa de Linux completo rodando
- Adicionar câmera/visão requer desenvolvimento customizado
- Sem interface web nativa

> [!TIP]
> **Veredicto:** Se fosse APENAS um torno CNC, LinuxCNC seria a escolha óbvia. 
> Mas como queremos integrar câmera + visão + ELS + CNC, usar LinuxCNC completo 
> pode ser excessivo — seria melhor usar partes da sua filosofia.

---

#### 2. 🔧 grblHAL — GRBL Moderno para ESP32/ARM

📎 https://github.com/grblHAL  
📄 GPL | 💾 ESP32 / STM32 / Teensy / RP2040

**O que é:** Evolução do GRBL para processadores 32-bit. É um **firmware** que
roda diretamente no microcontrolador e interpreta GCode.

**Funcionalidades para Torno:**
| Feature | Suporte |
|---|---|
| Threading (G33, G76) | ⚠️ Experimental (depende do driver) |
| Feed per revolution (G95) | ⚠️ Experimental |
| Encoder spindle sync | ⚠️ Requer configuração específica |
| Standard GCode (G0, G1, G2, G3) | ✅ Completo |
| Soft limits | ✅ |
| Backlash compensation | ✅ |
| Homing | ✅ |
| Tool changes | ✅ |
| WebUI | ✅ (com plugin ESP32) |

**Prós:**
- Roda direto no ESP32 (sem PC/Pi necessário para controle)
- Protocolo bem documentado e universal
- Vários GCode senders compatíveis
- Ativo desenvolvimento

**Contras:**
- **Threading em torno é experimental** no ESP32
- Não foi projetado originalmente para torno
- Configuração de encoder spindle é complexa
- Menos features de torno que LinuxCNC

> [!WARNING]
> **Veredicto:** grblHAL é promissor mas o suporte a threading/torno no ESP32 
> ainda não é confiável. Para um ELS puro, o NanoEls é muito melhor.

---

#### 3. 🌊 FluidNC — Fork do GRBL para ESP32

📎 https://github.com/bdring/FluidNC  
📄 GPL | 💾 ESP32

**O que é:** Fork moderno do GRBL especificamente para ESP32. Configuração via
arquivo YAML ao invés de compilação.

**Funcionalidades para Torno:**
| Feature | Suporte |
|---|---|
| Threading (G33, G76) | ❌ Não suportado |
| Spindle sync motion | ❌ Não suportado |
| Standard GCode | ✅ |
| WebUI bonita | ✅ Excelente |
| Config via YAML | ✅ Fácil |
| WiFi | ✅ |

**Prós:**
- Configuração mais fácil que grblHAL
- WebUI excelente embutida
- Grande comunidade

**Contras:**
- **NÃO suporta threading de torno** — projetado para fresadoras
- Não serve como ELS

> [!CAUTION]
> **Veredicto:** FluidNC NÃO serve para nosso projeto. Sem threading/spindle sync.

---

### ⚙️ Nível 2 — ELS Dedicados (Firmware Específico para Torno)

Estes são firmwares específicos para Electronic Lead Screw, focados em
sincronização encoder↔stepper.

---

#### 4. 🚀 NanoEls H5 — O Que Já Temos como Referência

📎 https://github.com/kachurovskiy/nanoels  
📄 MIT | 💾 ESP32-S3

*Já analisado em detalhe no `resumo_referencias.md`*

**Resumo:** É o projeto de ELS mais completo que existe. Suporta threading, 
turning, facing, cones, esferas, GCode via WiFi, touch screen Nextion, 
teclado PS2, MPG.

**Para nosso projeto:** ⭐⭐⭐⭐⭐ — **Melhor base para o firmware do ESP32**

---

#### 5. 💡 ESPels — ELS com Interface Web React

📎 https://github.com/jschoch/ESPels  
📄 MIT | 💾 ESP32

**O que é:** ELS baseado em ESP32 com interface web feita em React.js
via WebSocket.

**Funcionalidades:**
| Feature | Suporte |
|---|---|
| Threading (métrico + imperial) | ✅ |
| Feed mode (avanço contínuo) | ✅ |
| MoveSync (avanço com distância) | ✅ |
| Bounce mode (ida e volta) | ✅ |
| Interface Web (React) | ✅ Via WiFi |
| Touch screen nativa | ❌ |

**Prós:**
- Interface web moderna — pode controlar do celular/tablet
- WebSocket para comunicação tempo real
- Código mais simples que NanoEls

**Contras:**
- Menos features que NanoEls (sem cones, esferas, faceamento auto)
- Projeto em estado "beta"
- Sem display/tela nativa embutida

> [!TIP]
> **Veredicto:** Interessante pela interface web React + WebSocket.
> Pode inspirar a comunicação Raspberry ↔ ESP32 via WebSocket ao invés de UART.

---

### ⚙️ Nível 3 — GCode Senders (Apenas Interface, não controlam diretamente)

Estes são softwares que enviam GCode para um controlador (GRBL/grblHAL)
mas NÃO fazem o controle de motor diretamente.

---

#### 6. CNCjs — Sender Web

📎 https://cnc.js.org  
🌐 Web (Node.js) | Roda no Pi

- Interface web bonita, funciona bem em touchscreen
- **NÃO tem modo torno** — projetado para fresadora 3 eixos
- Pode ser usado se tivermos grblHAL no ESP32
- Suporta macros customizadas

#### 7. Universal Gcode Sender (UGS)

📎 https://winder.github.io/ugs_website  
☕ Java | Multiplataforma

- Interface desktop Java, funcional mas não moderna
- **NÃO tem modo torno** nativo
- Suporta GRBL e grblHAL

#### 8. bCNC

📎 https://github.com/vlachoudis/bCNC  
🐍 Python/Tkinter

- Interface desktop Python, com CAM básico embutido
- **NÃO tem modo torno** — pedido aberto no GitHub há anos
- Útil para debug de GRBL

> [!NOTE]
> **Veredicto GCode Senders:** Nenhum deles tem modo torno nativo.
> Para nosso projeto, faremos nossa própria interface no Raspberry Pi.

---

## Tabela Comparativa Final

| Software | Tipo | Torno? | Threading? | Roda em | Touch? | Câmera? | Para nós? |
|---|---|---|---|---|---|---|---|
| **LinuxCNC** | Controlador completo | ✅ | ✅ Nativo | Pi / PC | ✅ GMOCCAPY | ❌ | ⚠️ Complexo demais |
| **grblHAL** | Firmware MCU | ⚠️ | ⚠️ Experimental | ESP32 | ❌ | ❌ | ⚠️ Threading fraco |
| **FluidNC** | Firmware ESP32 | ❌ | ❌ | ESP32 | ✅ WebUI | ❌ | ❌ Não serve |
| **NanoEls H5** | ELS dedicado | ✅ | ✅ Robusto | ESP32-S3 | ✅ Nextion | ❌ | ✅ **Melhor base** |
| **ESPels** | ELS com Web | ✅ | ✅ | ESP32 | ✅ Web | ❌ | ✅ Inspira WebSocket |
| **CNCjs** | GCode sender | ❌ | N/A | Pi / PC | ✅ | ❌ | ❌ Sem torno |
| **UGS** | GCode sender | ❌ | N/A | PC | ⚠️ | ❌ | ❌ |
| **bCNC** | GCode sender | ❌ | N/A | PC | ❌ | ❌ | ❌ |

---

## Recomendação para o Nosso Projeto

> [!IMPORTANT]
> ### Arquitetura Recomendada: Sistema Híbrido
>
> Ao invés de usar UM software existente, vamos pegar **o melhor de cada um**:
>
> | De onde | O que pegar | Para que |
> |---|---|---|
> | **NanoEls H5** | Lógica de ELS (encoder↔stepper sync, threading, feeding) | Firmware do ESP32 |
> | **ESPels** | Conceito de comunicação WebSocket | Comunicação Pi ↔ ESP32 |
> | **LinuxCNC (GMOCCAPY)** | Inspiração de layout de interface touchscreen para torno | Design da GUI no Raspberry |
> | **LinuxCNC** | Protocolo GCode (G33, G76, G0, G1, G2, G3) | Interpretação de GCode |
> | **LatheCode** | Linguagem de descrição de peças → GCode | Gerador de programas |
> | **Haimer Probe** | Conceitos de visão computacional para posicionamento | Módulo de câmera |

### Por que NÃO usar LinuxCNC direto?

1. **Threading do NanoEls é melhor** — sincronização direta encoder↔stepper no ESP32 é mais determinística que via Linux
2. **LinuxCNC não tem câmera/visão** — teríamos que desenvolver do zero de qualquer jeito
3. **Complexidade** — configurar HAL/INI do LinuxCNC é muito mais complexo que firmware dedicado
4. **Flexibilidade** — com sistema próprio, podemos ter modo ELS (sem PC) + modo CNC (com Pi)
5. **O ESP32 funciona sozinho** — se o Raspberry travar, o ELS continua funcionando

### Por que NÃO usar grblHAL/FluidNC?

1. **Threading é experimental/inexistente** — não confiável para rosqueamento
2. **Não foram projetados para torno** — são firmware de fresadora adaptados
3. **NanoEls é superior** para operações de torno

---

## Fluxo do Sistema Final

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   RASPBERRY PI (Python + Qt/Web)                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Inspirado em:                                       │   │
│   │  • GMOCCAPY (layout touch para torno)               │   │
│   │  • CNCjs (interface web moderna)                    │   │
│   │  • Haimer Probe (visão computacional)               │   │
│   │                                                      │   │
│   │  Funções:                                            │   │
│   │  📷 Câmera com overlays                              │   │
│   │  🖥️ Interface touch com DRO                         │   │
│   │  📄 Parser + simulador GCode                        │   │
│   │  🔮 Pré-visualização da peça                        │   │
│   │  ⚠️ Detecção de erros                               │   │
│   │  📐 Medição por visão                                │   │
│   └────────────────────┬────────────────────────────────┘   │
│                        │ UART / WebSocket                    │
│   ┌────────────────────▼────────────────────────────────┐   │
│   │  ESP32-S3 (Firmware C++)                             │   │
│   │  Baseado em: NanoEls H5 + ESPels                    │   │
│   │                                                      │   │
│   │  Funções:                                            │   │
│   │  🔄 Leitura encoder (interrupções HW)               │   │
│   │  ⚙️ Geração pulsos stepper (timer HW)              │   │
│   │  🔩 Threading sincronizado                          │   │
│   │  📏 Avanço síncrono/assíncrono                      │   │
│   │  📐 Cones, esferas, multi-passe                     │   │
│   │  🛑 E-STOP (interrupção prioritária)                │   │
│   │  📡 Protocolo JSON serial + WiFi backup             │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```
