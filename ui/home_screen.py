from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, 
    QTextBrowser, QLabel, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt , Signal
from PySide6.QtGui import QFont
from datetime import datetime,timezone
import requests

class HomeScreen(QWidget):
    datos_obtenidos = Signal(dict)
    def __init__(self, stacked_widget,appParams:dict):
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

        # Título
        titulo = QLabel("Formulario de Búsqueda")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Formulario
        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignCenter)

        self.input_cedula = QLineEdit()
        self.input_cedula.setPlaceholderText("Ingrese la cédula...")
        self.input_cedula.setFixedWidth(250)

        # Botón Buscar
        self.boton_buscar = QPushButton("Buscar")
        self.boton_buscar.setFixedWidth(100)
        self.boton_buscar.clicked.connect(self.buscar_info)

        form_container = QHBoxLayout()
        form_container.addWidget(self.input_cedula)
        form_container.addWidget(self.boton_buscar)
        form_container.setAlignment(Qt.AlignCenter)

        form_layout.addRow(form_container)
        main_layout.addLayout(form_layout)

        #Boton Enrrollar
        self.boton_enrollar = QPushButton("Enrrollar")
        self.boton_enrollar.setFixedWidth(100)
        self.boton_enrollar.clicked.connect(self.ir_a_segunda_ventana)
        

        # Visualización de resultados en HTML
        self.resultado_html = QTextBrowser()
        self.resultado_html.setOpenExternalLinks(True)
        self.resultado_html.setStyleSheet("background-color: #212f3d; border: 1px solid #ccc;")
        main_layout.addWidget(self.resultado_html)
        main_layout.addWidget(self.boton_enrollar, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setMinimumSize(500, 400)

    def buscar_info(self):
        cedula = self.input_cedula.text().strip()
        info = self.search_by_dni(cedula)
        if not cedula:
            self.resultado_html.setHtml("<p style='color: red;'>Por favor, ingrese una cédula válida.</p>")
            return

        if info['status']:
            html = f"""
            <body style="font-family: Arial, sans-serif; background-color: #212f3d;">
            <div style="background-color: #212f3d; padding: 20px; border-radius: 10px; 
                        border: 1px solid #ccc; max-width: 400px; margin: auto; font-family: Arial, sans-serif;">
                <h2 style="color: #2E86C1; text-align: center; margin-bottom: 20px;">Datos Encontrados</h2>
                <p><b>Nombre:</b> {info['nombre']}</p>
                <p><b>Dirección:</b> {info['direccion']}</p>
                <p><b>Teléfono:</b> {info['telefono']}</p>
                <p><b>Correo:</b> {info['email']}</p>
                <p><b>Subscripcion Activa:</b> {info['status_subscription']}</p>
                <p><b>Fecha de Inicio:</b> {info['sub_start_date']}</p>
                <p><b>Fecha de finalizacion:</b> {info['sub_end_date']}</p>
            </div>
            </body>
            """
            self.userInfo = info
        else:
            html = """
            <div style="padding: 20px; border-radius: 10px; 
                        border: 1px solid #ff9999; max-width: 400px; margin: auto; font-family: Arial, sans-serif;">
                <h2 style="color: red; text-align: center;">El usuario No tiene una suscripcion Activa</h2>
                <p style="text-align: center;">Este Sistema es solo para clientes con suscripcion Activa</p>
            </div>
            """

        self.resultado_html.setHtml(html)
    def search_by_dni(self,dni):
        url = f"{self.appParams['base_url']}/api/users/validate?dni={dni}"
        payload = {}
        headers = {
        'x-tenant-id': self.appParams['tenant_id'],
        'Authorization': f'Bearer {self.appParams["token"]}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        result = response.json()
        
        user_subscriptions = result['result']['user_subscriptions']
        current_sub = None

        info = {}
        if len(user_subscriptions)>=1:
            current_sub = user_subscriptions[-1]
            now = datetime.now(timezone.utc)
            end_date = datetime.strptime(current_sub['end_date'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            start_date = datetime.strptime(current_sub['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            estado = 'inactiva'
            if now > end_date:
                estado = 'inactiva'
            info = {
                "status":True,
                "nombre": result['result']['name'] + " " + result['result']['lastname'],
                "direccion": result['result']['address'],
                "telefono": result['result']['phone'],
                "email": result['result']['email'],
                "sub_start_date": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "sub_end_date":end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                'status_subscription':estado
            }
            gender = "female"
            if result['result']['gender'] == "MASCULINO":
                gender = "male"
                user_data={
                        "id":str(result['result']['id']),
                        "enroll_data":{"UserInfo":{
                            "employeeNo":str(result['result']['id']),
                            "name":str(info['nombre']).upper(),
                            "userType":"normal",
                            "Valid":{"enable":True,"beginTime":info['sub_start_date'],"endTime":info['sub_end_date'],"timeType":"local"},
                            "doorRight":"1","RightPlan":[{"doorNo":1,"planTemplateNo":"1"}],
                            "gender":gender,
                            "localUIRight":False,
                            "maxOpenDoorTime":0,
                            "userVerifyMode":"",
                            "groupId":3,
                            "userLevel":"Employee",
                            "localPassword":""
                        }
                        },
                        "face_data":{"FaceDataRecord":'{"faceLibType":"blackFD","FDID":"1","FPID":'+'"'+f"{str(result['result']['id'])}"+'"'+'}'}
                }
                self.datos_obtenidos.emit(user_data)
        else:
            info = {
                "status":False,
                "nombre": '',
                "direccion":'',
                "telefono":'',
                "email":'',
                "sub_start_date":'',
                "sub_end_date":'',
                'status_subscription':''
                }
            
        return info

    def ir_a_segunda_ventana(self):
        self.stacked_widget.setCurrentIndex(1)
    
    def getUser(self,token):
        url = f"{self.appParams['base_url']}/api/users/validate?dni=1108595682"
        payload = {}
        headers = {
        'x-tenant-id': 'bbd38caf-8c63-4bd3-9ea5-4a73379f555f',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return "Suscripción activa hasta el 31/12/2023"

