from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QStackedWidget,QMessageBox
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer
import sys
import cv2
import requests
from requests.auth import HTTPDigestAuth
import json
from PIL import Image
import os
import time
class EnrollScreen(QWidget):
    def __init__(self, stacked_widget,appParams:dict = {
            "base_url":'',
            "email": '',
            "password": '',
            "tenant_id": '',
            "isapi_url":'',
            "isapi_user":'',
            "isapi_password":'',
            "token": ''
        }):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.appParams = appParams
        self.cap = None
        self.timer = QTimer()
        self.userData = {'id':"0"}
        self.image_io = ""
        self.init_ui()
     

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.image_label = QLabel("Iniciando cámara...")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.captureBtn = QPushButton("TOMAR FOTO")
        self.retryBtn = QPushButton("VOLVER A TOMAR FOTO")
        self.registerBtn = QPushButton("REGISTRAR")
        self.cancelBtn = QPushButton("CANCELAR")

        self.captureBtn.clicked.connect(self.capturar_imagen)
        self.retryBtn.clicked.connect(self.volver_a_tomar_foto)
        self.cancelBtn.clicked.connect(self.regresar_a_primera_ventana)
        self.registerBtn.clicked.connect(self.isapi_load_face)

        self.layout.addWidget(self.captureBtn)
        self.layout.addWidget(self.retryBtn)
        self.layout.addWidget(self.registerBtn)
        self.layout.addWidget(self.cancelBtn)
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)
        self.iniciar_camara()
        #valores iniciales por defecto
        

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start(30)
        self.captureBtn.setDisabled(False)
        self.retryBtn.setDisabled(True)
        self.registerBtn.setDisabled(True)
        

    def volver_a_tomar_foto(self):
        self.captureBtn.setDisabled(False)
        self.retryBtn.setDisabled(True)
        self.registerBtn.setDisabled(True)
        if self.cap and not self.timer.isActive():
            self.timer.start(30)  # Vu
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
    def crop_to_portrait(self,image, aspect_ratio=(4, 5)):
        height, width, _ = image.shape
        target_ratio = aspect_ratio[0] / aspect_ratio[1]
        current_ratio = width / height

        if current_ratio > target_ratio:
            # Imagen es más ancha de lo necesario, recortar en ancho
            new_width = int(height * target_ratio)
            x1 = (width - new_width) // 2
            image_cropped = image[:, x1:x1 + new_width]
        else:
            # Imagen es más alta de lo necesario, recortar en alto
            new_height = int(width / target_ratio)
            y1 = (height - new_height) // 2
            image_cropped = image[y1:y1 + new_height, :]

        return image_cropped
    def capturar_imagen(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = self.crop_to_portrait(frame, aspect_ratio=(4, 5))

                # Ruta relativa al directorio del proyecto
                base_dir = os.path.dirname(os.path.abspath(__file__))
                src_dir = os.path.abspath(os.path.join(base_dir, ".."))
                data_dir = os.path.join(src_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                name_img = str(self.userData['id'])
                ruta_guardado = os.path.join(data_dir, name_img+'.jpg')
                cv2.imwrite(ruta_guardado, frame)

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
                self.captureBtn.setDisabled(True)
                self.timer.stop()
                self.retryBtn.setDisabled(False)
                self.registerBtn.setDisabled(False)
    def isapi_load_face(self):
        # Enrolamos inicialmente al usuario:
        url_enroll = f"{self.appParams['isapi_url']}/ISAPI/AccessControl/UserInfo/Record?format=json"
        url_face_id = f"{self.appParams['isapi_url']}/ISAPI/Intelligent/FDLib/FDSetUp?format=json"
        headers = {
        }
        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(base_dir, ".."))
        data_dir = os.path.join(src_dir, "data")
        image_name = str(self.userData['id']) +".jpg"
        total_path = os.path.join(data_dir, image_name)
        files= [('img',(image_name,open(total_path,'rb'),'image/jpeg'))]
        try:
            response_enroller = requests.post(
                url_enroll,
                headers=headers,
                data= json.dumps(self.userData['enroll_data']),
                auth=HTTPDigestAuth(self.appParams['isapi_user'], self.appParams['isapi_password']),
                verify=False
            )
            if response_enroller.status_code == 200:
                time.sleep(2)
                requests.put(
                    url_face_id,
                    headers=headers,
                    files=files,
                    data = self.userData['face_data'],
                    auth=HTTPDigestAuth(self.appParams['isapi_user'], self.appParams['isapi_password']),
                    verify=False
                )
                self.stacked_widget.setCurrentIndex(0)
            elif response_enroller.status_code == 400:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Subly Info")
                msg_box.setText("Usuario ya registrado!")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.addButton("Cerrar", QMessageBox.AcceptRole)
                msg_box.exec()

        except requests.exceptions.RequestException as e:
            print("Ocurrió un error al intentar registrar al usuario:")
            print(str(e))


    def recibir_datos(self, datos):
        self.userData = datos
    def regresar_a_primera_ventana(self):
        self.stacked_widget.setCurrentIndex(0)