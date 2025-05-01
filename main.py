from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHBoxLayout, QStackedWidget, QHeaderView
)

import sys
from ui.home_screen import HomeScreen  
from ui.enroll_screen import EnrollScreen  
from dotenv import load_dotenv
import os
import json
import requests
load_dotenv(dotenv_path=".env", override=True)

BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TENANT_ID = os.getenv("TENANT_ID")
ISAPI_URL = os.getenv("ISAPI_URL")
ISAPI_USER = os.getenv("ISAPI_USER")
ISAPI_PASSWORD = os.getenv("ISAPI_PASSWORD")

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.appParams = {
            "base_url": BASE_URL,
            "email": EMAIL,
            "password": PASSWORD,
            "tenant_id": TENANT_ID,
            "isapi_url":ISAPI_URL,
            "isapi_user":ISAPI_USER,
            "isapi_password":ISAPI_PASSWORD,
            "token": ''
        }
        self.authenticate()
        self.init_ui()

    def init_ui(self):
        
        layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()

        self.primera_ventana = HomeScreen(self.stacked_widget,appParams=self.appParams)
        self.segunda_ventana = EnrollScreen(self.stacked_widget,appParams=self.appParams)
        self.primera_ventana.datos_obtenidos.connect(self.segunda_ventana.recibir_datos)
        self.stacked_widget.addWidget(self.primera_ventana)
        self.stacked_widget.addWidget(self.segunda_ventana)

        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.setWindowTitle("Subbly Face Enrollment")
        
    def authenticate(self):
        url = f"{BASE_URL}/api/auth/login"
        headers = {
            'x-tenant-id': TENANT_ID,
            'Content-Type': 'application/json'
            }
        payload = json.dumps({
        "email": EMAIL,
        "password": PASSWORD
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        result = response.json()
        if response.status_code == 201:
            auxToken = result['result']['token']
            self.appParams['token'] = auxToken
        else:
            print("Error en la autenticación:", response.status_code, response.text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.resize(400, 300)
    ventana.show()
    sys.exit(app.exec())
