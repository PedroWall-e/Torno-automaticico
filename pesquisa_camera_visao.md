# Pesquisa: Câmera e Visão Computacional em Tornos

## Resposta Curta

> [!IMPORTANT]
> **Não existe nenhum projeto open-source "pronto para usar"** que integre câmera diretamente com um ELS (Electronic Lead Screw) para torno. Porém, existem **projetos separados** de visão computacional para usinagem que podem ser integrados ao nosso torno automático como módulo adicional.

---

## Projetos Open-Source Encontrados

### 1. 🔬 Haimer Probe — Visão + LinuxCNC

📎 https://github.com/kentavv/haimer_probe  
⭐ 28 stars | 🐍 Python + OpenCV | 📄 GPL-3.0

**O que faz:**
- Usa **2 webcams** para automatizar LinuxCNC
- **Câmera 1:** Lê o mostrador analógico de um sensor Haimer 3D via visão computacional
- **Câmera 2:** Voltada para baixo, detecta e estima dimensões de furos na peça
- Combina visão com probing automático — a câmera encontra os furos e o probe Haimer os mede com precisão

**Hardware:**
- Microsoft LifeCam Cinema (webcam USB)
- Haimer 3D Sensor (probe mecânico)
- Suporte 3D printável para fixar câmera no probe
- PC rodando LinuxCNC

**Relevância:** ⭐⭐⭐⭐ — É o projeto mais próximo do que você descreveu. Usa câmera para ajudar o operador a posicionar e medir peças. Pode ser adaptado para torno.

---

### 2. 🏭 CNC Tool Wear Detection — ML para Desgaste de Ferramenta

📎 https://github.com/MAAykanat/CNC-Tool-Wear-Detection  
⭐ 10 stars | 🐍 Python | 📄 MIT

**O que faz:**
- Classifica desgaste de ferramenta CNC usando **machine learning**
- Usa dados de sensores (não câmera diretamente — feed rate, corrente, voltagem, aceleração)
- Algoritmos: KNN, Decision Tree, Random Forest, XGBoost, LightGBM
- Dataset da Universidade de Michigan (SMART lab)

**Relevância:** ⭐⭐ — Conceito de prevenção de erros, mas baseado em sensores, não câmera.

---

### 3. 📐 Computer Vision Workpieces — Inspeção Visual de Peças Usinadas

📎 https://github.com/uleroboticsgroup/computer_vision_workpieces  
🐍 Jupyter Notebook | 📄 Apache-2.0

**O que faz:**
- Inspeção automática de peças usinadas por visão computacional
- Detecção de **rebarbas (burrs)** em peças acabadas
- Usa técnicas de OpenCV: binarização, detecção de contornos, GLCM (textura), LBP
- Parte de um livro acadêmico sobre inteligência computacional

**Relevância:** ⭐⭐⭐ — Pode ser usado para inspeção pós-usinagem no torno.

---

## Abordagens que NÃO são projetos completos, mas são caminhos viáveis

### 4. 📷 ESP32-CAM + Edge Impulse — Classificação de Desgaste por Imagem

**Conceito:**
- ESP32-CAM (~5€) captura imagens da ferramenta de corte
- Edge Impulse (plataforma gratuita) treina modelo de classificação de imagens
- O modelo roda **diretamente no ESP32** (TinyML)
- Classifica: "Ferramenta boa" vs "Ferramenta desgastada" vs "Trocar agora"

**Stack:**
| Componente | Função | Custo |
|---|---|---|
| ESP32-CAM | Captura + inferência | ~5€ |
| Edge Impulse | Treinamento do modelo | Grátis |
| LED Ring | Iluminação consistente | ~3€ |
| Suporte 3D | Fixação no torno | ~1€ |

**Prós:** Barato, roda on-device, fácil de integrar com ESP32-S3 do NanoEls  
**Contras:** Resolução limitada, precisa treinamento com muitas imagens

---

### 5. 🖥️ Raspberry Pi + OpenCV — Sistema Completo de Monitoramento

**Conceito:**
- Raspberry Pi 4/5 com câmera HQ como processador de visão
- OpenCV para processamento de imagem em tempo real
- TensorFlow Lite ou PyTorch para modelos mais complexos
- MQTT para comunicação com o controlador ELS (ESP32)

**Funções possíveis:**
| Função | Técnica | Dificuldade |
|---|---|---|
| Medir diâmetro da peça | Detecção de bordas + calibração | ⭐⭐⭐ |
| Detectar desgaste de ferramenta | Classificação de imagem (CNN) | ⭐⭐⭐⭐ |
| Detectar rebarbas/acabamento | Análise de textura (GLCM/LBP) | ⭐⭐⭐ |
| Detectar chatter/vibração | FFT de vídeo ou acelerômetro | ⭐⭐⭐⭐ |
| Auxiliar posicionamento | Overlay com guias visuais na tela | ⭐⭐ |
| Dashboard remoto | Flask/Streamlit + streaming | ⭐⭐ |

---

## Arquitetura Proposta para Integração com o Nosso Projeto

```
┌─────────────────────────────────────────────────────┐
│                 TORNO AUTOMÁTICO                     │
│                                                     │
│  ┌──────────────┐          ┌──────────────────────┐ │
│  │  ESP32-S3    │◄──MQTT──►│  Raspberry Pi 4/5    │ │
│  │  (NanoEls)   │          │  + Câmera HQ         │ │
│  │              │          │  + OpenCV             │ │
│  │ • Encoder    │          │  + TF Lite            │ │
│  │ • Stepper Z  │          │                       │ │
│  │ • Stepper X  │          │ Funções:              │ │
│  │ • Display    │          │ • Medir diâmetro      │ │
│  │ • WiFi       │          │ • Detectar desgaste   │ │
│  └──────┬───────┘          │ • Guia posicionamento │ │
│         │                  │ • Alerta de erros     │ │
│    Controle                │ • Dashboard web       │ │
│    de Eixos                └──────────────────────┘ │
│                                                     │
│  ┌──────────────┐   alternativa barata              │
│  │  ESP32-CAM   │──────────────────────────────────┐│
│  │  (TinyML)    │   Classificação on-device        ││
│  │  Edge Impulse│   Ferramenta OK / Desgastada     ││
│  └──────────────┘──────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

---

## Desafios Práticos em Ambiente de Torno

> [!WARNING]
> ### Problemas reais que precisam ser resolvidos:
> 1. **Cavacos e fluido de corte** — sujam a lente constantemente
> 2. **Vibração** — a câmera precisa de montagem rígida anti-vibração
> 3. **Iluminação** — reflexos do metal dificultam análise de imagem, precisa de iluminação LED difusa controlada
> 4. **Velocidade** — processamento precisa ser rápido o suficiente para operar durante o corte
> 5. **Segurança** — a câmera NÃO deve substituir paradas de emergência mecânicas

---

## Recomendação

> [!TIP]
> ### Para o nosso projeto, sugiro uma abordagem em fases:
> 
> **Fase 1 (junto com o ELS):** Adicionar uma **ESP32-CAM** apontada para a peça/ferramenta como "olho remoto" — apenas streaming de vídeo para o operador ver remotamente via WiFi. Custo: ~5€. Sem ML por enquanto.
> 
> **Fase 2 (após ELS estável):** Adicionar um **Raspberry Pi** com câmera HQ para:
> - Medir diâmetro da peça em tempo real (overlay visual)
> - Detectar quando a ferramenta está desgastada
> - Dashboard web com streaming + dados dos eixos
> 
> **Fase 3 (avançado):** Integrar com o controlador ELS para:
> - Pausa automática se detectar anomalia
> - Correção automática de offset baseada em medição visual
> - Previsão de desgaste e planejamento de troca de ferramenta
