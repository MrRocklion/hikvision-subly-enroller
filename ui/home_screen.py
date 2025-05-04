import logging
from datetime import datetime, timezone

import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit,
    QTextBrowser, QLabel, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class HomeScreen(QWidget):
    datos_obtenidos = Signal(dict)

    def __init__(self, stacked_widget, appParams: dict):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.appParams = appParams
        self.userInfo = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Buscar Información de Cédula")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)

        titulo = QLabel("Formulario de Búsqueda")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignCenter)

        self.input_cedula = QLineEdit()
        self.input_cedula.setPlaceholderText("Ingrese la cédula...")
        self.input_cedula.setFixedWidth(250)

        self.boton_buscar = QPushButton("Buscar")
        self.boton_buscar.setFixedWidth(100)
        self.boton_buscar.clicked.connect(self.buscar_info)

        form_container = QHBoxLayout()
        form_container.addWidget(self.input_cedula)
        form_container.addWidget(self.boton_buscar)
        form_container.setAlignment(Qt.AlignCenter)

        form_layout.addRow(form_container)
        main_layout.addLayout(form_layout)

        self.boton_enrollar = QPushButton("Enrrollar")
        self.boton_enrollar.setFixedWidth(100)
        self.boton_enrollar.clicked.connect(self.ir_a_segunda_ventana)
        self.boton_enrollar.setDisabled(True)

        self.resultado_html = QTextBrowser()
        self.resultado_html.setOpenExternalLinks(True)
        self.resultado_html.setStyleSheet("background-color: #212f3d; border: 1px solid #ccc;")
        main_layout.addWidget(self.resultado_html)
        main_layout.addWidget(self.boton_enrollar, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setMinimumSize(500, 400)

    def buscar_info(self):
        self.boton_buscar.setDisabled(True)
        cedula = self.input_cedula.text().strip()
        if not cedula:
            self.resultado_html.setHtml("<p style='color: red;'>Por favor, ingrese una cédula válida.</p>")
            logging.warning("Intento de búsqueda con cédula vacía.")
            return

        logging.info(f"Buscando información para cédula: {cedula}")
        try:

            info = self.search_by_dni(cedula)
        except Exception as e:
            self.resultado_html.setHtml("<p style='color: red;'>Error al buscar la información. Intente nuevamente.</p>")
            logging.error(f"Error en búsqueda de cédula {cedula}: {e}")
            self.boton_buscar.setDisabled(False)
            return

        if info["status"]:
            html = f"""
            <div style="background-color: #212f3d; padding: 20px; border-radius: 10px; 
                        border: 1px solid #ccc; max-width: 400px; margin: auto;">
                <h2 style="color: #2E86C1; text-align: center;">Datos Encontrados</h2>
                <p><b>Nombre:</b> {info['nombre']}</p>
                <p><b>Dirección:</b> {info['direccion']}</p>
                <p><b>Teléfono:</b> {info['telefono']}</p>
                <p><b>Correo:</b> {info['email']}</p>
                <p><b>Subscripción Activa:</b> {info['status_subscription']}</p>
                <p><b>Fecha de Inicio:</b> {info['sub_start_date']}</p>
                <p><b>Fecha de Finalización:</b> {info['sub_end_date']}</p>
            </div>
            """
            self.boton_enrollar.setDisabled(False)
            self.userInfo = info
        else:
            html = """
            <div style="padding: 20px; border-radius: 10px; 
                        border: 1px solid #ff9999; max-width: 400px; margin: auto;">
                <h2 style="color: red; text-align: center;">Usuario sin subscripción activa</h2>
                <p style="text-align: center;">Este sistema es solo para clientes con subscripción activa.</p>
            </div>
            """
            self.boton_enrollar.setDisabled(True)
        self.boton_buscar.setDisabled(False)
        self.resultado_html.setHtml(html)

    def search_by_dni(self, dni):
        self.boton_enrollar.setDisabled(False)
        url = f"{self.appParams['base_url']}/api/users/validate?dni={dni}"
        headers = {
            'x-tenant-id': self.appParams['tenant_id'],
            'Authorization': f"Bearer {self.appParams['token']}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

        info = {
            "id": "0", "status": False, "nombre": "", "direccion": "",
            "telefono": "", "email": "", "sub_start_date": "",
            "sub_end_date": "", "status_subscription": ""
        }

        if result.get("result") is None:
            logging.info(f"Cédula {dni} no encontrada en sistema.")
            return info

        user = result["result"]
        subs = user.get("user_subscriptions", [])
        if not subs:
            logging.info(f"Usuario {dni} sin subscripciones registradas.")
            return info

        current_sub = subs[-1]
        now = datetime.now(timezone.utc)
        start_date = datetime.strptime(current_sub['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(current_sub['end_date'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

        estado = 'ACTIVA' if now <= end_date else 'INACTIVA'
        gender = "male" if user.get("gender") == "MASCULINO" else "female"

        info.update({
            "id": str(user['id']),
            "status": True if estado == 'ACTIVA' else False,
            "nombre": f"{user['name']} {user['lastname']}",
            "direccion": user['address'],
            "telefono": user['phone'],
            "email": user['email'],
            "sub_start_date": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "sub_end_date": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "status_subscription": estado
        })

        user_data = {
            "id": str(user['id']),
            "enroll_data": {
                "UserInfo": {
                    "employeeNo": str(user['id']),
                    "name": info['nombre'].upper(),
                    "userType": "normal",
                    "Valid": {
                        "enable": True,
                        "beginTime": info['sub_start_date'],
                        "endTime": info['sub_end_date'],
                        "timeType": "local"
                    },
                    "doorRight": "1",
                    "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                    "gender": gender,
                    "localUIRight": False,
                    "maxOpenDoorTime": 0,
                    "userVerifyMode": "",
                    "groupId": 3,
                    "userLevel": "Employee",
                    "localPassword": ""
                }
            },
            "face_data": {
                "FaceDataRecord": f'{{"faceLibType":"blackFD","FDID":"1","FPID":"{user["id"]}"}}'
            }
        }

        self.datos_obtenidos.emit(user_data)
        logging.info(f"Datos obtenidos correctamente para cédula {dni}.")
        return info

    def ir_a_segunda_ventana(self):
        logging.info("Navegando a la pantalla de enrolamiento.")
        self.stacked_widget.setCurrentIndex(1)

    def getUser(self, token):
        logging.info("Solicitando datos de usuario por defecto para testing.")
        url = f"{self.appParams['base_url']}/api/users/validate?dni=1108595682"
        headers = {
            'x-tenant-id': 'bbd38caf-8c63-4bd3-9ea5-4a73379f555f',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return "Suscripción activa hasta el 31/12/2023"
        except requests.RequestException as e:
            logging.error(f"Error obteniendo datos del usuario de prueba: {e}")
            return "Error al obtener datos del usuario"
