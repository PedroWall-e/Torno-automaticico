import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class CameraWorker(QThread):
    """
    Captura de vídeo em Thead separada. 
    Lê o feed do OpenCV 30 vezes por segundo, aplica OpenCV (Miras, Overlay), 
    e manda a imagem empacotada em QImage pro PyQt desenhar sem atrasar o GCode.
    """
    frame_ready = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.is_running = True

    def run(self):
        # Tenta abrir driver default de câmera do linux (/dev/video0)
        # Em alguns Raspberry Pi OS pode precisar de argumentos extras (GStreamer/libcamera)
        # O "Canhão" do Gstreamer moderno para raptar os quadros do libcamera no OS Novo
        pipeline = "libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! appsink"
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        
        while self.is_running:
            ret, frame = cap.read()
            if ret:
                h, w, _ = frame.shape
                
                # --- VISÃO COMPUTACIONAL (OVERLAYS) ---
                # Exemplo: Mira Central do Torno Fixa (Eixo da Placa)
                cv2.line(frame, (w//2, 0), (w//2, h), (0, 255, 0), 1) # Linha Verde
                cv2.line(frame, (0, h//2), (w, h//2), (0, 255, 0), 1) # Cruzamento
                
                # Círculo alvo
                cv2.circle(frame, (w//2, h//2), 50, (0, 255, 255), 1) # Amarelo

                # Conversão ultrarrápida OpenCV BGR -> Qt RGB
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Atira pra tela principal
                self.frame_ready.emit(qt_image)
                
            # Limita à 30fps para não queimar cpu térmica do Pi atoa
            self.msleep(33)
            
        cap.release()

    def stop(self):
        self.is_running = False
