from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt
import math

class CameraCanvas(QLabel):
    """
    Substituto inteligente da QLabel padrão. 
    Serve como a "Prancheta" transparente por cima do nosso vídeo OpenCV.
    Permite cliques e arrastos p/ medição e calibração de bits, ferramentas e peças.
    """
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.points = []
        
        # Padrão: 1 pixel = 1 milímetro.
        # No software completo isso será ajustável (Calibrar Câmera)
        self.pixel_to_mm_ratio = 1.0 

    def mousePressEvent(self, event):
        """Ao tocar na tela do Raspberry, guardamos coordenadas"""
        # Se já tiver os 2 pontos, apaga tudo p/ começar uma nova régua
        if len(self.points) >= 2:
            self.points.clear()
            
        self.points.append(event.position().toPoint())
        self.update() # Manda o Qt redesenhar o Overlay na hora

    def paintEvent(self, event):
        """Sempre que um novo frame do OpenCV ou um click chega, isso desenha por cima"""
        super().paintEvent(event) # Desenha o pixmap (imagem) do OpenCV no fundo primeiro
        
        if len(self.points) > 0:
            painter = QPainter(self)
            
            # Anti-serrilhado para as linhas ficarem bonitas mesmo no painel LCD
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Caneta Amarelo Néon Industrial
            pen = QPen(QColor(255, 255, 0), 2)
            painter.setPen(pen)
            
            # 1. Pinta bolinhas onde o Dedo/Mouse clicou
            for p in self.points:
                painter.drawEllipse(p, 5, 5)
                
            # 2. Se temos 2 bolinhas, traça a Régua e faz a matemática
            if len(self.points) == 2:
                p1 = self.points[0]
                p2 = self.points[1]
                
                painter.drawLine(p1, p2)
                
                # Pitágoras para calcular o vetor exato de medição de pixel na câmera
                dx = p2.x() - p1.x()
                dy = p2.y() - p1.y()
                dist_pixels = math.sqrt(dx*dx + dy*dy)
                
                medida_mm = dist_pixels * self.pixel_to_mm_ratio
                
                # Põe um retângulo preto atrás do texto para dar contraste
                mid_x = (p1.x() + p2.x()) // 2
                mid_y = (p1.y() + p2.y()) // 2 - 15
                
                texto = f"{dist_pixels:.0f} Px | ~ {medida_mm:.2f} mm"
                
                painter.setPen(QColor(0, 0, 0)) # Contorno
                painter.drawText(mid_x + 1, mid_y + 1, texto) 
                painter.setPen(QColor(255, 100, 100)) # Vermelhão pro texto
                painter.drawText(mid_x, mid_y, texto)
