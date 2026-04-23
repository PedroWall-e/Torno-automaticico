#include <Arduino.h>
#include "protocol.h"
#include "spindle.h"
#include "stepper_control.h"

unsigned long last_status_time = 0;
const int STATUS_INTERVAL_MS = 100; // Envia Status para a Tela 10x por segundo

void setup() {
    Serial.begin(115200);   // Mesmo canal e velocidade que pusemos no Python
    
    Spindle::init();        // Prepara os Relés Pro Bumafer
    StepperControl::init(); // Prepara Steppers Nema
    Protocol::init();       // Memória RAM Json
    
    // Dá um fôlego para bootloaders largarem o cabo DTR serial do ESP
    delay(500); 
}

void loop() {
    // 1. Tentar engolir ordens do Cérebro (Respberry) via Cabo de forma veloz
    Protocol::process_incoming_serial();

    // 2. TAREFA CRÍTICA: Manter o laço dos Motores sem engasgos 
    StepperControl::run_loop();

    // 3. Controle suave / Pwm do Mandril pra não esbarrar nada
    Spindle::run_loop();

    // 4. Bateu 100 milisegundos? Dispara um Status do Eixo pra Pintar a Tela do Pi.
    if (millis() - last_status_time >= STATUS_INTERVAL_MS) {
        last_status_time = millis();
        Protocol::send_status();
    }
}
