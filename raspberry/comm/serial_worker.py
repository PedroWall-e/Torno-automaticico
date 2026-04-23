import json
import time
import serial
from PySide6.QtCore import QThread, Signal

class SerialWorker(QThread):
    """
    O "Coração" da ponte Raspberry <-> ESP32.
    Rodar num QThread é obrigatório: se lêssemos a porta USB na mesma área do
    código da interface, a nossa tela congelaria enquanto espera os dados.
    Aqui, o Worker respira solto no background e empurra as atualizações na tela!
    """
    
    # Tubos de Comunicação direta com a interface (Signals do Qt)
    # Entrega um dicionário pronto para uso. Ex: {"z": 1.5, "rpm": 400}
    status_received = Signal(dict)
    
    # Avisa a tela se o cabo se soltou ou se o ESP32 queimou/desligou
    connection_error = Signal(str)

    def __init__(self, port="COM3", baudrate=115200): # /dev/ttyUSB0 no Raspberry final
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.is_running = True
        self.serial_conn = None
        
        # Nossa bacia de comandos do Pi para o ESP32
        self.command_queue = []

    def send_command(self, cmd_dict):
        """
        Função pública que a nossa "main_window" vai chamar pra enviar algo.
        Ex: serial_worker.send_command({"cmd": "spin_stop"})
        """
        self.command_queue.append(cmd_dict)

    def connect_serial(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=0.05)
            # Acabou de conectar, manda um ping dizendo que o cérebro ta online
            self.send_command({"cmd": "ping", "sender": "PI4"})
            return True
        except Exception as e:
            self.connection_error.emit(f"FALHA SERIAL: Cabo ESP32 Ausente na porta {self.port}")
            return False

    def run(self):
        """O Loop real que acontece em total isolamento nas costas da Tela"""
        while self.is_running:
            # 1. Tentar conectar caso falte
            if self.serial_conn is None or not self.serial_conn.is_open:
                if not self.connect_serial():
                    time.sleep(1) # Dorme 1 segundo antes de metralhar o sistema de novo
                    continue

            try:
                # 2. Despachar a Pilha de Comandos pendentes na garganta pro ESP32
                while len(self.command_queue) > 0:
                    cmd_to_send = self.command_queue.pop(0) # Pega exato o primeiro q chegou
                    json_str = json.dumps(cmd_to_send) + "\n"
                    # Transforma o Texto em Bytes e Manda
                    self.serial_conn.write(json_str.encode('utf-8'))
                    self.serial_conn.flush()

                # 3. Ouvir os reportes do ESP32 (Telemetria, DRO, Posição Atual)
                if self.serial_conn.in_waiting > 0:
                    # Tenta ler até o "/n" enter.
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        try:
                            # Converte o status cru num dicionário python 
                            status_dict = json.loads(line)
                            
                            # DISPARA A GRANADA! Quem assinou esse sinal
                            # (nossa Interface), pegará o dicionário e jogará na tela!
                            self.status_received.emit(status_dict)
                            
                        except json.JSONDecodeError:
                            # Pode acontecer no primeiro segundo em que o ESP32 ligar,
                            # enviando sujeira ou bootlogs na serial. Ignoramos até limpar.
                            pass
                            
            except serial.SerialException:
                # Se o cabo foi arrancado bruscamente:
                self.connection_error.emit("CONEXÃO PERDIDA! O ESP32 Desapareceu!")
                self.serial_conn.close()
            
            # Repouso micro do processador pra essa thread não estourar 100% de CPU
            time.sleep(0.01)

    def stop(self):
        """Para limpo e fecha a porta de comunicação quando o programa desligar"""
        self.is_running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
