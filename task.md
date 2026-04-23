# Tarefas de Execução — Torno Automático CNC/ELS

## Fase 1: Estrutura Base
- `[/]` Criar estrutura de pastas do projeto (Pi e ESP32).
- `[x]` Implementar `parser.py` de GCode customizado sem licença GPL.

## Fase 2: Interface PyQt (Módulo Raspberry)
- `[x]` Inicializar tela principal (`main_window.py`) no formato tela-cheia (Kiosk).
- `[x]` Criar painéis de Layout: Área de Câmera, DRO, Controles Manuais de Fuso.
- `[x]` Criar os Widgets de leitura numérica gigantes para DRO e RPM.
- `[x]` Criar botões lógicos do Spindle (Start, Stop, Reverso, Slider de Velocidade).

## Fase 3: Comunicação (A Ponte Pi ↔ ESP32)
- `[x]` Python: `serial_worker.py` (Thread independente para leitura e envio assíncrono).
- `[x]` Python: Empacotar status e comandos em JSON.

## Fase 4: Controladores do ESP32 (Módulo Músculo)
- `[x]` Setup C++ inicial com suporte Serial de 115200 baud mínimo e envio constante de status ("heartbeat").
- `[x]` Extrair núcleo de processamento do Enconder e Stepper do código `NanoEls H5`.
- `[x]` Construir o tradutor serial JSON em C++ (usar biblioteca rápida e compacta como ArduinoJson).
- `[x]` Lógica de Controle do Motor Spindle: Receber alvo de RPM/Estado e acionar Relés / Potenciômetro digital (ou gerador PWM).

## Fase 5: Visão Computacional (Módulo Raspberry)
- `[x]` Integrar fluxo da `picamera2` e exibi-lo como Widget principal na interface PyQt.
- `[x]` Configurar "Canvas" transparente no PyQt sobre o vídeo para desenho de linhas de escala em milímetros.
- `[ ]` Rotina de Calibração: Clicar em 2 pontos na imagem e setar DÍAMETRO conhecido para conversão (Pixels -> MM).

## Fase 6: Movimento Complexo e GCode
- `[ ]` GUI de carregamento de arquivo e exibição da fila de Gcode.
- `[ ]` Rotina de processamento assíncrono do Gcode: Enviar comando -> ESP executa -> Confirma "OK" -> Envia próximo Gcode.
- `[ ]` Ciclos fixos base: Converter ciclo G76 de Rosca num "Macro" que despacha comandos únicos configurando o Stepper Tracker do NanoEls.
