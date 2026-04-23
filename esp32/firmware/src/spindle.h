#pragma once
#include <Arduino.h>

namespace Spindle {
    // Configuração de Pinos para o Bumafer 600mm
    const int PIN_RELAY_FWD = 25;
    const int PIN_RELAY_REV = 26;
    const int PIN_PWM_OUT = 27; // Pode alimentar um filtro RC (0-10V)
    
    int current_rpm = 0;
    int target_rpm = 0;
    int direction = 0; // 0 = Stop, 1 = FWD, -1 = REV

    void init() {
        pinMode(PIN_RELAY_FWD, OUTPUT);
        pinMode(PIN_RELAY_REV, OUTPUT);
        digitalWrite(PIN_RELAY_FWD, LOW); // Garante relé desligado no boot
        digitalWrite(PIN_RELAY_REV, LOW);
        
        // Em um ESP32 usaríamos o ledcSetup para alta resolução PWM,
        // que controlará a placa inversora original do Torno.
    }

    void set_state(int dir, int rpm) {
        direction = dir;
        target_rpm = rpm;
        
        if (dir == 0) { // PARADA
            digitalWrite(PIN_RELAY_FWD, LOW);
            digitalWrite(PIN_RELAY_REV, LOW);
            // TODO: Zera PWM
            
        } else if (dir == 1) { // FRENTE
            digitalWrite(PIN_RELAY_REV, LOW); // Desarma reverso antes
            delay(50); // Segurança física do relé
            digitalWrite(PIN_RELAY_FWD, HIGH);
            
        } else if (dir == -1) { // TRÁS
            digitalWrite(PIN_RELAY_FWD, LOW); // Desarma frente antes
            delay(50);
            digitalWrite(PIN_RELAY_REV, HIGH);
        }
    }
    
    void set_target_rpm(int rpm) {
        target_rpm = rpm;
        // FUTURO: Atualizar o duty cycle do PWM instantaneamente
    }

    int get_current_rpm() {
        return current_rpm; // FUTURO: Lerá os pulsos de hardware do Encoder
    }
    
    const char* get_state_str() {
        if(direction == 0) return "idle";
        return direction > 0 ? "fwd" : "rev";
    }

    void run_loop() {
        // Lógica de rampa de aceleração suave para não derrubar o disjuntor
        // de casa ao pedir 2500 RPM instantâneos no Bumafer 1100W.
    }
}
