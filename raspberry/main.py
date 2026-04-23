import sys
import os
from PySide6.QtWidgets import QApplication

from ui.main_window import TornoMainWindow
from comm.serial_worker import SerialWorker
from vision.camera_worker import CameraWorker

def main():
    # os.environ["QT_QPA_PLATFORM"] = "eglfs" 
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 1. Iniciamos os motores de fundo (Músculos do Pi)
    serial_worker = SerialWorker(port="COM3", baudrate=115200) # Editar p/ /dev/ttyUSB0 depois
    camera_worker = CameraWorker()
    
    # 2. Injetamos eles na UI pra ela poder conectar os 'click' nos gatilhos
    window = TornoMainWindow(serial_worker, camera_worker)
    
    if os.environ.get("QT_QPA_PLATFORM") == "eglfs":
        window.showFullScreen()
    else:
        window.resize(1024, 600)
        window.show()
        
    # 3. Dá partida (RUN) na Serial e na Câmera no background
    serial_worker.start()
    camera_worker.start()
        
    exit_code = app.exec()
    
    # 4. Desliga limpo ao fechar
    serial_worker.stop()
    camera_worker.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
