# Torno Automático — Plano de Implementação

Sistema integrado de torno com controle CNC/ELS e Visão Computacional de assistência.

## Especificações da Máquina e Hardware Final
Este plano foi adaptado especificamente para o seguinte conjunto:

*   **Torno Máquina:** Bumafer 600mm (Distância entre centros), Motor Brushless 1100W (220V), Furo do eixo 38mm, Velocidade 0-2500 RPM.
*   **Módulo Cérebro (Visão/UI):** Raspberry Pi 4 + Raspberry Pi Camera V2 + Tela Oficial Touchscreen 7".
*   **Sistema Operacional:** Raspberry Pi OS Lite (Sem ambiente de área de trabalho para economizar recursos e dar sensação de painel industrial).
*   **Módulo Músculo (Tempo Real):** ESP32-S3.

---

## Arquitetura de Software

### Módulo 1: Controlador ELS/CNC (ESP32-S3)

Firmware C++ rodando no ESP32. Responsável pelo controle de tempo real. Além dos eixos X e Z, ele agora controla ativamente o mandril.

#### Funções Adicionadas ao ESP32
- **Controle de Rotação (Mandril):** Saída para um Potenciômetro Digital (ex: MCP4151 via SPI) ou Módulo PWM-Tensão (0-10V) para simular o giro do controlador do Bumafer.
- **Relés de Direção:** Pinos de saída para acionar relés (Forward, Reverse, Stop) do mandril.
- **Sincronização Ativa:** Em modos CNC, o ESP32 pode acelerar/desacelerar o próprio mandril automaticamente (G96 - Constant Surface Speed).

#### Modos de Operação
| Modo | Descrição |
|---|---|
| **Manual/Analógico** | Operador usa a tela, ESP32 apenas ajusta relés/potenciômetro do fuso |
| **ELS Gearbox** | Vite madre segue encoder do mandril rigorosamente |
| **ELS Threading** | Rosqueamento automático sincronizado |
| **ELS Automação** | Torneamento, Faceamento, Esferas e Cones (Multi-passe) |
| **CNC GCode** | Execução de programa GCode com comandos vindos do Raspberry |

#### Protocolo de Comunicação (ESP32 ↔ Raspberry Pi)
UART Serial 115200 baud, mensagens JSON. Adicionados comandos de spindle:
- `{"cmd":"spindle","state":"fwd","rpm":1200}`
- Resposta de status incluirá RPM medido do encoder para validar a potência injetada.

---

### Módulo 2: Sistema de Visão e Interface Kiosk (Raspberry Pi 4)

A aplicação será construída em Python usando **PySide6 (Qt)**.

#### Desafio do OS Lite resolvido:
Como estamos no Raspberry Pi OS Lite (sem X11 ou Wayland), rodaremos o PySide6 em modo **Kiosk** industrial. O Qt usará o plugin `eglfs` ou `linuxfb` para desenhar os gráficos de alta performance direto na memória de vídeo (DRM/KMS), pulando a necessidade de uma área de trabalho. O tempo de boot é curtíssimo (vai direto pro nosso app).

#### Estrutura do App no Raspberry
- **GCode Parser:** Nosso próprio parser GCode (sem licença GPL).
- **Visão OpenCV:** Captura via `picamera2`. Medição de diâmetros, guias virtuais projetadas sobre a câmera.
- **Thread Serial:** Fila isolada e robusta enviando JSON para o ESP32.

---

### Representação do Painel

A interface de 7 polegadas terá este layout de prioridade visual:
1. **Vídeo ao vivo da Camera V2 + Overlays de medição e eixo**
2. **DRO Enorme (Z e X) e RPM do mandril**
3. **Controle Eletrônico de Fuso (Lig/Desl/Rev/Slider de Velocidade)**
4. **Painel de Modos e Carregador Mestre de GCode/LatheCode**

---

## Lista de Hardware de Aquisição
*(Componentes ainda necessários para integrar na máquina)*

1.  **ESP32-S3:** Módulo controlador (como o N16R8).
2.  **Transmissores 3V3→5V:** SN74HCT245N ou similar para sinais de motor limpos.
3.  **Encoder Rotativo (600+ ppr):** Ligado ao eixo árvore MT5 do torno Bumafer para sincronia ELS perfeita.
4.  **Motores de Passo:** NEMA 23 (Closed Loop recomendado) para Z, NEMA 17 para X.
5.  **Controle de Fuso:** Potenciômetro digital SPI (MCP4151) ou conversor PWM→Tensão para hackear a placa do motor Brushless do Bumafer.
6.  **Módulos de Relé (5V/3.3V):** Para direção do motor Brushless (Se necessário pela placa do torno).

---

## User Review Required

> [!IMPORTANT]
> ### Estamos prontos para Executar!
> O plano final reflete todas as suas configurações de hardware. 
> 
> **Próximo passo na aprovação deste plano:**
> Criarei a lista de tarefas (`task.md`) e começaremos pela **Fase 1**: Programar a tela Kiosk no Raspberry (App PySide6 base) simulando envio serial de comandos de fuso/motores para provar que a interface e comunicação base operam 100% no OS Lite.
> 
> **Posso dar largada para execução do código?**
