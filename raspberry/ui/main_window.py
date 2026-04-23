from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QSlider, QFrame, QGridLayout)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QPixmap, QImage
from vision.camera_canvas import CameraCanvas
from gcode.gcode_worker import GCodeWorker

class TornoMainWindow(QMainWindow):
    def __init__(self, serial_worker, camera_worker):
        super().__init__()
        self.setWindowTitle("Torno CNC/ELS - Bumafer 600mm")
        
        # Ponteiros pros motores de background
        self.serial = serial_worker
        self.camera = camera_worker
        
        self.setStyleSheet("""
            QMainWindow { background-color: #0d0d0d; }
            QLabel { color: #E0E0E0; font-family: Arial; }
            QFrame { background-color: #1a1a1a; border-radius: 8px; }
            QPushButton { 
                background-color: #333333; color: white; border-radius: 4px; padding: 15px; font-weight: bold; border: 1px solid #444;
            }
            QPushButton:pressed { background-color: #555555; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # =========================================================
        # ZONA 1 (ESQUERDA): Câmera (Com Sinal conectado)
        # =========================================================
        camera_frame = QFrame()
        camera_layout = QVBoxLayout(camera_frame)
        self.camera_label = CameraCanvas()
        camera_layout.addWidget(self.camera_label)
        
        main_layout.addWidget(camera_frame, stretch=60)

        # =========================================================
        # ZONA 2 (DIREITA): Músculos, DRO e Infos
        # =========================================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # DRO
        dro_frame = QFrame()
        dro_layout = QGridLayout(dro_frame)
        font_dro = QFont("Courier New", 36, QFont.Bold)
        
        self.label_z_val = QLabel("+000.000")
        self.label_z_val.setFont(font_dro)
        self.label_z_val.setStyleSheet("color: #00FF55;")
        
        self.label_x_val = QLabel("-000.000")
        self.label_x_val.setFont(font_dro)
        self.label_x_val.setStyleSheet("color: #FFaa00;")
        
        dro_layout.addWidget(QLabel("EIXO Z (mm):"), 0, 0)
        dro_layout.addWidget(self.label_z_val, 1, 0)
        dro_layout.addWidget(QLabel("EIXO X (mm):"), 2, 0)
        dro_layout.addWidget(self.label_x_val, 3, 0)
        
        right_panel.addWidget(dro_frame, stretch=2)

        # SPINDLE (Com Sinais Conectados)
        spindle_frame = QFrame()
        spindle_layout = QVBoxLayout(spindle_frame)
        
        spindle_bar = QHBoxLayout()
        self.label_rpm = QLabel("0 RPM")
        self.label_rpm.setFont(QFont("Courier New", 26, QFont.Bold))
        self.label_rpm.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_rpm.setStyleSheet("color: #00AAFF;")
        
        spindle_bar.addWidget(QLabel("FUSO:"))
        spindle_bar.addWidget(self.label_rpm)
        spindle_layout.addLayout(spindle_bar)
        
        btn_layout = QHBoxLayout()
        
        # ======= MAGIC HAS HAPPENED (OPÇÃO A: LIGAÇÃO) =======
        btn_ccw = QPushButton("⏪ REV")
        btn_ccw.clicked.connect(lambda: self.serial.send_command({"cmd": "spindle", "state": "rev"}))
        
        btn_stop = QPushButton("🛑 STOP")
        btn_stop.setStyleSheet("background-color: #AA0000; color: white;") 
        btn_stop.clicked.connect(lambda: self.serial.send_command({"cmd": "spindle", "state": "stop"}))
        
        btn_cw = QPushButton("FWD ⏩")
        btn_cw.clicked.connect(lambda: self.serial.send_command({"cmd": "spindle", "state": "fwd"}))
        
        btn_layout.addWidget(btn_ccw)
        btn_layout.addWidget(btn_stop)
        btn_layout.addWidget(btn_cw)
        
        slider_rpm = QSlider(Qt.Horizontal)
        slider_rpm.setRange(0, 2500)
        slider_rpm.setTickInterval(500)
        # Quando soltar o drag, envia pro ESP32
        slider_rpm.sliderReleased.connect(lambda: self.serial.send_command({"cmd": "spindle", "rpm": slider_rpm.value()}))
        # ========================================================
        
        spindle_layout.addLayout(btn_layout)
        spindle_layout.addSpacing(10)
        spindle_layout.addWidget(slider_rpm)
        right_panel.addWidget(spindle_frame, stretch=2)

        sys_frame = QFrame()
        sys_layout = QHBoxLayout(sys_frame)
        sys_layout.addWidget(QPushButton("ELS"))
        btn_gcode = QPushButton("▶ GCode")
        sys_layout.addWidget(btn_gcode)
        sys_layout.addStretch()
        sys_layout.addWidget(QPushButton("⚙"))
        sys_frame.setStyleSheet("background-color: transparent;")
        right_panel.addWidget(sys_frame, stretch=1)
        
        # =========================================================
        # MÁQUINA DE GCODE / AUTOMOCÃO
        # =========================================================
        self.gcode_worker = GCodeWorker(self.serial)
        # Código estático de teste embutido para provas de conceito
        codigo_teste = """\n        G00 X0 Z0\n        G01 X-2.5 Z-10.0 F150\n        G76 P1.5 Z-30\n        """
        self.gcode_worker.load_file_content(codigo_teste)
        # Ativa nosso maquinário de disparo de JSON
        btn_gcode.clicked.connect(self.gcode_worker.start)
        
        main_layout.addLayout(right_panel, stretch=40)
        
        # LIGAS DE RECEBIMENTO (Quando os Cães dão retorno)
        self.serial.status_received.connect(self.update_telemetry)
        self.camera.frame_ready.connect(self.update_video)

    @Slot(dict)
    def update_telemetry(self, data):
        """Disparado 10x por seg qd o ESP32 manda o StatusJSON"""
        if 'pos_z' in data:
            self.label_z_val.setText(f"{data['pos_z']:+08.3f}")
        if 'pos_x' in data:
            self.label_x_val.setText(f"{data['pos_x']:+08.3f}")
        if 'rpm' in data:
            self.label_rpm.setText(f"{data['rpm']} RPM")

    @Slot(QImage)
    def update_video(self, image):
        """Disparado a 30fps copiando a OpenCV de forma crua pra Tela"""
        # Redimensiona mantendo aspecto
        pixmap = QPixmap.fromImage(image).scaled(
            self.camera_label.width(), 
            self.camera_label.height(), 
            Qt.KeepAspectRatio
        )
        self.camera_label.setPixmap(pixmap)
