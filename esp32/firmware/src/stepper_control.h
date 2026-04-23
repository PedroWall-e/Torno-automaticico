#pragma once
#include <Arduino.h>
#include <driver/pcnt.h>

namespace StepperControl {
    
    // Pinos de Músculo X e Z (Mapeamento original do NanoEls H5 ESP32-S3)
    const int Z_ENA = 41;
    const int Z_DIR = 42;
    const int Z_STEP = 35;

    const int X_ENA = 16;
    const int X_DIR = 15;
    const int X_STEP = 7;

    // Pinos do Encoder de Vidro/Óptico do Mandril
    const int ENC_A = 13;
    const int ENC_B = 14;

    volatile float pos_z_mm = 0.0;
    volatile float pos_x_mm = 0.0;
    volatile int spindle_pulse_count = 0;

    // Timer de hardware puro (Isolado do Arduino loop)
    hw_timer_t * timer = NULL;
    portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

    void IRAM_ATTR onTimer() {
        // ====================================================================
        // ZONA DE RISCO DE MORTE: INTERRUPÇÃO DE HARDWARE (MICROSEGUNDOS)
        // Nenhuma lentidão, print ou delay é permitido aqui dentro.
        // ====================================================================
        portENTER_CRITICAL_ISR(&timerMux);
        
        // FUTURO: É aqui que a lógica de Bresenham de pulsar o Z_STEP
        // baseada na contagem exata de leitura do Encoder via PCNT ocorrerá.
        
        portEXIT_CRITICAL_ISR(&timerMux);
    }

    void init() {
        // 1. Setup Pinos Stepper
        pinMode(Z_ENA, OUTPUT);
        pinMode(Z_DIR, OUTPUT);
        pinMode(Z_STEP, OUTPUT);
        pinMode(X_ENA, OUTPUT);
        pinMode(X_DIR, OUTPUT);
        pinMode(X_STEP, OUTPUT);
        
        // 2. Setup Especializado: PCNT (Contador de Pulsos do ESP32)
        // Faz a leitura "Quadrature" dos sinais A e B até 40MHz em Background.
        // É isso que dá a estabilidade perfeita para o Threading no Torno!
        pcnt_config_t pcnt_config = {
            .pulse_gpio_num = ENC_A,
            .ctrl_gpio_num = ENC_B,
            .lctrl_mode = PCNT_MODE_REVERSE,
            .hctrl_mode = PCNT_MODE_KEEP,
            .pos_mode = PCNT_COUNT_INC,
            .neg_mode = PCNT_COUNT_DEC,
            .counter_h_lim = 30000,
            .counter_l_lim = -30000,
            .unit = PCNT_UNIT_0,
            .channel = PCNT_CHANNEL_0,
        };
        pcnt_unit_config(&pcnt_config);
        pcnt_counter_pause(PCNT_UNIT_0);
        pcnt_counter_clear(PCNT_UNIT_0);
        pcnt_counter_resume(PCNT_UNIT_0);

        // 3. Setup Timer ISR (Clock de 1 microsegundo por tick)
        timer = timerBegin(0, 80, true);
        timerAttachInterrupt(timer, &onTimer, true);
        // Interrompe a CPU inteira a cada 50us p/ gerar pulsos motores se preciso
        timerAlarmWrite(timer, 50, true); 
        timerAlarmEnable(timer);
    }
    
    void run_loop() {
        // Puxamos silenciosamente a contagem óptica atual do mandril
        int16_t count;
        pcnt_get_counter_value(PCNT_UNIT_0, &count);
        spindle_pulse_count = count;
        
        // Cálculo de rampas de aceleração e envio de metas p/ o onTimer..
    }
}
