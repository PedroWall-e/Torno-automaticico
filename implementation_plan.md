# Torno Automático — Plano de Implementação

Sistema integrado de torno com ELS/CNC + Visão Computacional com câmera e tela de assistência ao operador.

## Visão Geral do Sistema

O sistema é composto por **2 módulos principais** que se comunicam entre si:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        TORNO AUTOMÁTICO                              │
│                                                                      │
│   ┌─────────────────────────────┐    ┌────────────────────────────┐  │
│   │   MÓDULO VISÃO (Raspberry)  │    │  MÓDULO CONTROLE (ESP32)   │  │
│   │                             │    │                            │  │
│   │  📷 Câmera (acima torno)    │    │  🔄 Encoder do mandril     │  │
│   │  🖥️ Tela touch 7"          │◄──►│  ⚙️ Stepper Z (vite)      │  │
│   │  🧠 OpenCV + TF Lite       │UART│  ⚙️ Stepper X (transv.)   │  │
│   │  🎯 Guias visuais          │WiFi│  🎮 Controles manuais      │  │
│   │  👁️ Detecção de objetos    │    │  📟 Display Nextion (opc.) │  │
│   │  ⚠️ Alerta de erros        │    │  🔧 ELS / CNC modes       │  │
│   │  🔮 Pré-visualização 3D    │    │                            │  │
│   └─────────────────────────────┘    └────────────────────────────┘  │
│                                                                      │
│   Comunicação: UART serial + WiFi/MQTT backup                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## User Review Required

> [!IMPORTANT]
> ### Decisões que precisam da sua aprovação:
> 1. **Raspberry Pi 4 ou 5?** — O Pi 5 é ~2x mais rápido para OpenCV, mas custa mais (~80€ vs ~45€)
> 2. **Tela:** 7" touch oficial do Raspberry (~70€) ou alternativa HDMI genérica (~30€)?
> 3. **Controlador ELS:** ESP32-S3 (como NanoEls H5) ou Arduino Mega (como MegaEls)?
> 4. **Câmera:** Módulo Camera Pi HQ (~50€, melhor qualidade) ou Camera Module 3 (~25€, suficiente)?
> 5. **Comunicação Pi ↔ ESP:** UART serial (simples, confiável) ou WiFi/WebSocket (mais flexível)?
> 6. **Interface do operador:** Qt/PyQt (nativa, rápida) ou Web (Flask + browser, mais bonita)?

---

## Arquitetura de Software

### Módulo 1: Controlador ELS/CNC (ESP32-S3)

Firmware C++ rodando no ESP32. Responsável pelo controle de tempo real dos motores.

#### Modos de Operação

| Modo | Descrição | Sincronização |
|---|---|---|
| **ELS Gearbox** | Vite madre segue mandril | Encoder → Stepper (tempo real) |
| **ELS Threading** | Rosqueamento automático | Encoder → Stepper (sincronizado) |
| **ELS Turning** | Torneamento multi-passe | Encoder → Stepper + limites |
| **ELS Facing** | Faceamento automático | Encoder → Stepper + limites |
| **CNC Manual** | Movimentos manuais via tela | Raspberry → ESP32 (comandos) |
| **CNC GCode** | Execução de programa GCode | Raspberry envia blocos G → ESP32 |

#### Protocolo de Comunicação (ESP32 ↔ Raspberry Pi)

```
UART Serial 115200 baud, mensagens JSON terminadas em \n

── Raspberry → ESP32 (Comandos) ──────────────────────
{"cmd":"move","axis":"Z","dist":1.5,"speed":100}
{"cmd":"move","axis":"X","dist":-0.5,"speed":50}
{"cmd":"mode","value":"thread","pitch":1.5}
{"cmd":"start"}
{"cmd":"stop"}
{"cmd":"zero","axis":"Z"}
{"cmd":"zero","axis":"X"}
{"cmd":"gcode","line":"G01 X-2.0 Z-50.0 F0.1"}
{"cmd":"set","param":"backlash_z","value":0.05}

── ESP32 → Raspberry (Status, 10Hz) ──────────────────
{"pos_z":25.430,"pos_x":-3.200,"rpm":450,"angle":127.5,
 "mode":"thread","state":"running","pitch":1.5,
 "limit_zl":true,"limit_zr":false,"limit_xu":false,"limit_xd":true}
```

---

### Módulo 2: Sistema de Visão + Interface (Raspberry Pi)

Aplicação Python rodando no Raspberry Pi. Responsável pela câmera, tela e comunicação.

#### Estrutura de Arquivos do Software

```
torno-automatico/
├── raspberry/
│   ├── main.py                    # Ponto de entrada
│   ├── config.py                  # Configurações (calibração, hardware)
│   │
│   ├── vision/
│   │   ├── camera.py              # Captura e pré-processamento
│   │   ├── calibration.py         # Calibração câmera ↔ coordenadas reais
│   │   ├── object_detector.py     # Detecção de peça, ferramenta, castanha
│   │   ├── measurement.py         # Medição de diâmetro, comprimento
│   │   ├── error_detector.py      # Detecção de anomalias (chatter, rebarbas)
│   │   ├── guide_overlay.py       # Desenha guias visuais sobre a imagem
│   │   └── preview_renderer.py    # Pré-visualização do objeto final
│   │
│   ├── communication/
│   │   ├── serial_comm.py         # Comunicação UART com ESP32
│   │   └── protocol.py            # Encode/decode do protocolo JSON
│   │
│   ├── ui/
│   │   ├── app.py                 # Aplicação principal Qt
│   │   ├── main_screen.py         # Tela principal com câmera + dados
│   │   ├── setup_screen.py        # Tela de configuração/calibração
│   │   ├── gcode_screen.py        # Tela de carregamento/execução GCode
│   │   ├── manual_screen.py       # Controle manual dos eixos
│   │   └── widgets/
│   │       ├── camera_view.py     # Widget de vídeo com overlays
│   │       ├── dro_display.py     # DRO (Digital Readout) Z e X
│   │       ├── mode_selector.py   # Seletor ELS/CNC/Manual
│   │       └── jog_controls.py    # Botões de movimento
│   │
│   ├── gcode/
│   │   ├── parser.py              # Parser de GCode
│   │   ├── simulator.py           # Simulador visual de GCode
│   │   └── sender.py              # Envia GCode linha a linha ao ESP32
│   │
│   └── models/
│       ├── tool_wear.tflite       # Modelo de desgaste de ferramenta
│       └── object_detect.tflite   # Modelo de detecção de objetos
│
├── esp32/
│   ├── els_controller.ino         # Firmware principal ESP32
│   ├── encoder.h                  # Leitura de encoder
│   ├── stepper.h                  # Controle de steppers
│   ├── threading.h                # Lógica de rosqueamento
│   ├── feeding.h                  # Lógica de avanço
│   ├── serial_protocol.h          # Comunicação com Raspberry
│   └── config.h                   # Constantes de hardware
│
└── docs/
    ├── wiring_diagram.md
    ├── calibration_guide.md
    └── user_manual.md
```

---

## Proposed Changes

### Componente 1: Sistema de Visão (Câmera)

A câmera fica **acima do torno**, olhando para baixo, com vista da peça, castanha e ferramenta.

#### Funções da Câmera

##### 1.1 Detecção de Objetos
- Identifica: **peça** (cilindro no mandril), **ferramenta** (inserto), **castanha** (chuck)
- Usa OpenCV para detecção por contornos + cor + forma
- Opcional: modelo TensorFlow Lite para detecção mais robusta

##### 1.2 Medição Dimensional
- Calibração: um padrão de referência (checkerboard) define pixels → mm
- Mede **diâmetro** da peça em tempo real pela silhueta vista de cima
- Mede **comprimento** visível da peça fora da castanha
- Exibe medidas como overlay na tela

##### 1.3 Detecção de Erros
- **Peça solta:** detecta deslocamento inesperado da peça
- **Ferramenta quebrada:** mudança brusca no contorno da ferramenta
- **Chatter/vibração:** análise de variação de frames (blur/tremor)
- **Cavaco enrolado:** acúmulo excessivo de material no mandril
- Em caso de anomalia: **alerta sonoro + visual + comando de pausa ao ESP32**

##### 1.4 Guias Visuais para o Operador
Linhas e formas desenhadas sobre a imagem da câmera em tempo real:

```python
# Exemplos de overlays na tela do operador:

# 1. Linha central do mandril (referência de centro)
cv2.line(frame, center_top, center_bottom, GREEN, 2)

# 2. Linha de posição atual da ferramenta
cv2.line(frame, tool_pos, tool_pos_end, CYAN, 2)

# 3. Retângulo do perfil final desejado (do GCode/LatheCode)
cv2.polylines(frame, [profile_points], True, YELLOW, 2)

# 4. Zonas de limite (soft limits) — áreas vermelhas semitransparentes
cv2.rectangle(frame, limit_area, RED_TRANSPARENT)

# 5. Diâmetro atual medido
cv2.putText(frame, f"Ø {diameter:.2f}mm", pos, font, GREEN)

# 6. Seta indicando direção de avanço
cv2.arrowedLine(frame, start, end, BLUE, 2)

# 7. Contorno da peça detectada 
cv2.drawContours(frame, [workpiece_contour], -1, GREEN, 2)

# 8. Contorno do perfil final desejado sobre a peça
cv2.drawContours(frame, [target_profile], -1, YELLOW, 1, cv2.LINE_AA)
```

##### 1.5 Pré-visualização do Objeto
- O operador carrega um perfil (LatheCode ou GCode)
- O sistema renderiza o perfil final **sobre a imagem real da peça**
- Mostra em amarelo/transparente o material que será removido
- Mostra em verde o perfil final esperado
- Permite ao operador verificar alinhamento **antes** de iniciar o corte

---

### Componente 2: Interface do Operador (Tela do Raspberry)

#### Layout da Tela Principal (7" touch 800×480)

```
┌──────────────────────────────────────────────────────────┐
│ [ELS ▼] [Thread ▼]  P: 1.50mm   RPM: 450   ⚠️ OK      │ ← Barra de status
├────────────────────────────────────┬─────────────────────┤
│                                    │  Z:  +025.430 mm   │
│                                    │  X:  -003.200 mm   │
│         CÂMERA AO VIVO             │                     │
│      (com overlays/guias)          │  Ø  32.15 mm       │
│                                    │  L  45.00 mm       │
│    ┌──── perfil amarelo ────┐      │                     │
│    │    (material a remover)│      │  [◄][▲][▼][►]      │
│    └────────────────────────┘      │  Step: 0.1mm       │
│                                    │                     │
│         ● peça detectada           │  [▶ START]          │
│         ◆ ferramenta               │  [■ STOP ]          │
│                                    │  [⌂ ZERO Z]         │
│                                    │  [⌂ ZERO X]         │
├────────────────────────────────────┴─────────────────────┤
│ [Calibrar] [GCode] [Config] [Manual]    Spindle: ⟳ FWD  │ ← Barra inferior
└──────────────────────────────────────────────────────────┘
```

#### Telas Disponíveis

| Tela | Função |
|---|---|
| **Principal** | Câmera + DRO + controles básicos |
| **GCode** | Carregar, simular e executar programas GCode |
| **Calibração** | Calibrar câmera (checkerboard), medir referência |
| **Configuração** | Passos/volta, passo vite, backlash, micro-step |
| **Manual** | Controle manual dos eixos com jog |
| **Perfil** | Editor de perfil (LatheCode) com pré-visualização |

---

### Componente 3: Controlador ELS/CNC (ESP32-S3)

Baseado na arquitetura do **NanoEls**, simplificado para nosso uso:

#### Hardware do ESP32

| Componente | Conexão ESP32 |
|---|---|
| Encoder (600ppr) | GPIO com interrupção |
| Stepper Z (STEP/DIR/ENA) | GPIO direto ou via SN74HCT245N |
| Stepper X (STEP/DIR/ENA) | GPIO direto ou via SN74HCT245N |
| Raspberry Pi | UART TX/RX (115200) |
| Botão E-STOP | GPIO com interrupção (prioridade máxima) |
| Handwheel/MPG (opcional) | GPIO com interrupção |

#### Modos no ESP32

```cpp
enum OperationMode {
    MODE_IDLE,          // Parado, aceita comandos manuais
    MODE_ELS_GEARBOX,   // ELS: avanço síncrono com mandril
    MODE_ELS_THREAD,    // ELS: rosqueamento sincronizado
    MODE_ELS_TURN,      // ELS: torneamento automático multi-passe
    MODE_ELS_FACE,      // ELS: faceamento automático
    MODE_ELS_CONE,      // ELS: cone com razão X/Z constante
    MODE_CNC_MANUAL,    // CNC: movimentos manuais via Raspberry
    MODE_CNC_GCODE,     // CNC: execução de GCode via Raspberry
};
```

---

### Componente 4: Comunicação Raspberry ↔ ESP32

#### Fluxo de Dados

```
Raspberry Pi                          ESP32-S3
    │                                     │
    │───── {"cmd":"mode","value":"thread"} ──►│  Comando
    │                                     │
    │◄──── {"pos_z":25.4,"rpm":450,...} ──│  Status (10Hz)
    │                                     │
    │───── {"cmd":"start"} ───────────────►│  Iniciar
    │                                     │
    │◄──── {"event":"limit_hit","axis":"Z"} ─│  Evento
    │                                     │
    │───── {"cmd":"stop"} ────────────────►│  Parar (ou E-STOP)
    │                                     │
    │───── {"cmd":"gcode","line":"G01..."} ►│  Bloco GCode
    │◄──── {"event":"gcode_done"} ────────│  Bloco concluído
```

#### Prioridades

| Prioridade | Tipo | Exemplo |
|---|---|---|
| 🔴 Máxima | E-STOP | Botão físico → para tudo imediatamente |
| 🟠 Alta | Pausa por erro | Câmera detecta anomalia → pause |
| 🟡 Normal | Comandos | Iniciar, parar, mudar modo |
| 🔵 Baixa | Status | Posição, RPM, ângulo (periódico) |

---

## Lista de Hardware Completa

| # | Componente | Estimativa | Notas |
|---|---|---|---|
| 1 | Raspberry Pi 4 (4GB) | ~45€ | Ou Pi 5 por ~80€ |
| 2 | Tela touch 7" | ~30-70€ | Oficial ou genérica |
| 3 | Camera Module 3 | ~25€ | Ou HQ Camera ~50€ |
| 4 | ESP32-S3 N16R8 | ~5€ | Para o controlador ELS |
| 5 | 2× SN74HCT245N | ~2€ | Level shifter 3V3→5V |
| 6 | Encoder óptico 600ppr | ~15€ | Para mandril |
| 7 | Stepper NEMA23 + driver (Z) | ~40€ | CL57T closed-loop recomendado |
| 8 | Stepper NEMA17 + driver (X) | ~25€ | Para carro transversal |
| 9 | Fonte 48V (ou 24V) | ~20€ | Para motores |
| 10 | Fonte 5V 3A | ~10€ | Para Pi + ESP32 |
| 11 | PCB personalizada (ESP32) | ~5€ | JLCPCB |
| 12 | LED ring para iluminação | ~5€ | Consistência da câmera |
| 13 | Suporte câmera + case 3D | ~5€ | Filamento PLA |
| 14 | Conectores, cabos, terminais | ~15€ | Diversos |
| 15 | Botão E-STOP | ~5€ | Segurança obrigatória |
| | **TOTAL ESTIMADO** | **~250-310€** | |

---

## Fases de Desenvolvimento

### Fase 1 — Fundação (Semanas 1-3)
- [ ] Firmware ESP32: leitura encoder + controle stepper Z
- [ ] Firmware ESP32: protocolo serial JSON
- [ ] Raspberry: app Python básica com tela
- [ ] Raspberry: comunicação serial com ESP32
- [ ] Raspberry: DRO (posição Z, X, RPM) na tela
- [ ] Testar movimentos manuais via tela do Raspberry

### Fase 2 — ELS Básico (Semanas 4-6)
- [ ] Firmware ESP32: modo ELS Gearbox (avanço síncrono)
- [ ] Firmware ESP32: modo Threading (rosqueamento)
- [ ] Firmware ESP32: stepper X + backlash
- [ ] Raspberry: seletor de modo na interface
- [ ] Raspberry: configuração de passos via tela

### Fase 3 — Câmera e Visão (Semanas 7-10)
- [ ] Raspberry: captura de câmera + exibição na tela
- [ ] Raspberry: calibração câmera → coordenadas reais
- [ ] Raspberry: detecção de contorno da peça
- [ ] Raspberry: medição de diâmetro via visão
- [ ] Raspberry: guias visuais (linhas de referência, limites)
- [ ] Raspberry: detecção de anomalias básica

### Fase 4 — CNC e Pré-visualização (Semanas 11-14)
- [ ] Raspberry: parser de GCode
- [ ] Raspberry: simulador visual de GCode
- [ ] Raspberry: envio de GCode ao ESP32
- [ ] Raspberry: overlay do perfil final sobre imagem da câmera
- [ ] Firmware ESP32: execução de blocos GCode
- [ ] Integrar LatheCode para geração de perfil

### Fase 5 — Polimento (Semanas 15-16)
- [ ] Detecção de desgaste de ferramenta (TF Lite)
- [ ] Alerta automático + pausa de segurança
- [ ] Melhorias de interface
- [ ] Documentação e manual do usuário
- [ ] Testes extensivos de integração

---

## Open Questions

> [!IMPORTANT]
> ### Perguntas para definir antes de começar:
>
> 1. **Qual torno você vai usar?** Preciso saber o modelo para dimensionar motores e montagem do encoder
> 2. **Você já tem o Raspberry Pi e a câmera?** Se sim, quais modelos?
> 3. **O ESP32 controlará o motor do mandril (spindle) também ou apenas os eixos?** A maioria dos ELS assume que o mandril é ligado/desligado manualmente
> 4. **Budget máximo para hardware?** Posso ajustar a especificação
> 5. **Prefere interface nativa (Qt/PyQt) ou web (Flask+browser)?** Qt é mais suave mas mais complexo; web é mais bonita e fácil de iterar
> 6. **Quer começar pelo firmware ESP32 ou pela interface do Raspberry?**

---

## Verification Plan

### Testes Automatizados
- Teste unitário do protocolo serial (JSON encode/decode)
- Teste do parser de GCode com programas de exemplo
- Teste da calibração de câmera com checkerboard

### Testes Manuais
- Fase 1: Mover eixos via tela e confirmar DRO
- Fase 2: Cortar rosca de teste (M10×1.5) e medir com paquímetro
- Fase 3: Comparar diâmetro medido pela câmera vs paquímetro (erro < 0.5mm)
- Fase 4: Executar GCode simples (cilindro escalonado) e validar dimensões
