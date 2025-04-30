from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QStackedWidget
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer
import sys
import cv2


class EnrollScreen(QWidget):
    def __init__(self, stacked_widget,appParams:dict):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.appParams = appParams
        self.cap = None
        self.timer = QTimer()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.image_label = QLabel("Iniciando cámara...")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.captureBtn = QPushButton("CAPTURAR IMAGEN")
        self.cancelBtn = QPushButton("CANCELAR")

        self.captureBtn.clicked.connect(self.capturar_imagen)
        self.cancelBtn.clicked.connect(self.regresar_a_primera_ventana)

        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.captureBtn)
        self.layout.addWidget(self.cancelBtn)

        self.setLayout(self.layout)

        self.iniciar_camara()

    def iniciar_camara(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.image_label.setText("No se pudo acceder a la cámara.")
            return

        self.timer.timeout.connect(self.mostrar_frame)
        self.timer.start(30)  # Aproximadamente 33 fps

    def mostrar_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(), self.image_label.height(),
                Qt.KeepAspectRatio
            ))

    def capturar_imagen(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.timer.stop()
                self.cap.release()
                self.cap = None

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame_rgb.shape
                bytes_per_line = 3 * width
                q_image = QImage(
                    frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888
                )
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.width(), self.image_label.height(),
                    Qt.KeepAspectRatio
                ))
            else:
                self.image_label.setText("Error al capturar la imagen.")

    def regresar_a_primera_ventana(self):
        if self.cap and self.cap.isOpened():
            self.timer.stop()
            self.cap.release()
            self.cap = None
        self.stacked_widget.setCurrentIndex(0)