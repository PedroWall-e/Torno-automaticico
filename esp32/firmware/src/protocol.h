#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include "spindle.h"
#include "stepper_control.h"

namespace Protocol {
    StaticJsonDocument<256> doc_in;
    StaticJsonDocument<256> doc_out;
    String input_buffer = "";

    void init() {
        input_buffer.reserve(256); // Prevenir fragmentação da memória no ESP32
    }

    void handle_command(String& json_str) {
        DeserializationError error = deserializeJson(doc_in, json_str);
        
        if (error) return; // Se for ruído elétrico no cabo, só ignora.

        const char* cmd = doc_in["cmd"];
        if (!cmd) return;
        
        // Cérebro quer saber se estamos vivos
        if (strcmp(cmd, "ping") == 0) {
            // Emite resposta instantânea
        } 
        // Recebemos um pacote com diretrizes para o Fuso
        else if (strcmp(cmd, "spindle") == 0) {
            const char* state = doc_in["state"];
            int rpm_target = doc_in["rpm"] | 0;
            
            if (state) {
                if (strcmp(state, "fwd") == 0)      Spindle::set_state(1, rpm_target);
                else if (strcmp(state, "rev") == 0) Spindle::set_state(-1, rpm_target);
                else if (strcmp(state, "stop") == 0)Spindle::set_state(0, 0);
            } else {
                Spindle::set_target_rpm(rpm_target);
            }
        }
    }

    void process_incoming_serial() {
        // Leitura "Não Bloqueante". Lê apenas os pingos que chegaram 
        // e volta pro motor focar no que importa.
        while (Serial.available() > 0) {
            char c = Serial.read();
            if (c == '\n') {
                handle_command(input_buffer);
                input_buffer = "";
            } else {
                input_buffer += c;
                // Timeout de Segurança (Buffer overflow) pra travar lixo no cabo
                if(input_buffer.length() > 255) input_buffer = "";
            }
        }
    }

    void send_status() {
        doc_out.clear();
        doc_out["pos_z"] = StepperControl::pos_z_mm; 
        doc_out["pos_x"] = StepperControl::pos_x_mm; 
        
        doc_out["rpm"] = Spindle::get_current_rpm(); 
        doc_out["state"] = Spindle::get_state_str(); 

        serializeJson(doc_out, Serial);
        Serial.println(); // O \n é nosso terminador
    }
}
