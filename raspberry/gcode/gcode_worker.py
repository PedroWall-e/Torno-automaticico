import time
from PySide6.QtCore import QThread, Signal
from gcode.parser import parse_gcode

class GCodeWorker(QThread):
    """
    A Fila de Execução (Fase 6).
    Envia arquivos de GCode passo-a-passo. É a verdadeira mente do CNC.
    """
    gcode_finished = Signal()
    progress_update = Signal(int, int) # Linha X de Linha Y (Para barrinha de % na tela)
    gcode_error = Signal(str)

    def __init__(self, serial_worker):
        super().__init__()
        self.serial = serial_worker
        self.is_running = False
        self.commands = []
        
    def load_file_content(self, raw_text):
        try:
            self.commands = parse_gcode(raw_text)
            return len(self.commands)
        except Exception as e:
            self.gcode_error.emit(str(e))
            return 0

    def run(self):
        self.is_running = True
        total = len(self.commands)
        current = 0
        
        while self.is_running and current < total:
            cmd = self.commands[current]
            
            # Formata comandos Padrão (Linear e Rapio)
            if cmd.command[0] == 'G' and cmd.command[1] in [0, 1]:
                json_cmd = {"cmd": "move"}
                if 'X' in cmd.params: json_cmd['x'] = cmd.params['X']
                if 'Z' in cmd.params: json_cmd['z'] = cmd.params['Z']
                if 'F' in cmd.params: json_cmd['f'] = cmd.params['F']
                
                self.serial.send_command(json_cmd)
                
                # IMPORTANTE: Aqui, no software "full", precisariamos aguardar
                # um status_dict dizendo "Cheguei no Z 0!". Como prova de conceito,
                # daremos 1.5s entre movimentos de Gcode
                time.sleep(1.5) 
                
            # ROSCAS E THREADS (O Câncer dos Tornos!)
            elif cmd.command[0] == 'G' and cmd.command[1] == 76:
                # Transforma G76 (Complexooo) em JSON atômico pra ativar o Modulo NanoEls (Fácil!)
                json_cmd = {
                    "cmd": "thread",
                    "pitch": cmd.params.get('P', 1.0),
                    "depth": cmd.params.get('K', 1.0),
                    "end_z": cmd.params.get('Z', 0.0)
                }
                self.serial.send_command(json_cmd)
                time.sleep(3.0) # Roscas demoram mais
                
            current += 1
            self.progress_update.emit(current, total)
            
        self.is_running = False
        self.gcode_finished.emit()

    def stop(self):
        self.is_running = False
