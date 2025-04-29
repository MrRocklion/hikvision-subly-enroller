from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, 
    QTextBrowser, QLabel, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sys
import requests

# Diccionario simulado
datos_personas = {
    "1234567890": {
        "nombre": "Juan Pérez",
        "edad": 30,
        "direccion": "Av. Siempre Viva 742",
        "telefono": "0987654321"
    },
    "0987654321": {
        "nombre": "María García",
        "edad": 25,
        "direccion": "Calle Falsa 123",
        "telefono": "0912345678"
    }
}

class HomeScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
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
        info = datos_personas.get(cedula)

        if info:
            html = f"""
            <body style="font-family: Arial, sans-serif; background-color: #212f3d;">
            <div style="background-color: #212f3d; padding: 20px; border-radius: 10px; 
                        border: 1px solid #ccc; max-width: 400px; margin: auto; font-family: Arial, sans-serif;">
                <h2 style="color: #2E86C1; text-align: center; margin-bottom: 20px;">Datos Encontrados</h2>
                <p><b>Nombre:</b> {info['nombre']}</p>
                <p><b>Edad:</b> {info['edad']} años</p>
                <p><b>Dirección:</b> {info['direccion']}</p>
                <p><b>Teléfono:</b> {info['telefono']}</p>
            </div>
            </body>
            """
        else:
            html = """
            <div style="background-color: #ffe6e6; padding: 20px; border-radius: 10px; 
                        border: 1px solid #ff9999; max-width: 400px; margin: auto; font-family: Arial, sans-serif;">
                <h2 style="color: red; text-align: center;">No se encontró información</h2>
                <p style="text-align: center;">Por favor verifique la cédula ingresada.</p>
            </div>
            """

        self.resultado_html.setHtml(html)

    def ir_a_segunda_ventana(self):
        self.stacked_widget.setCurrentIndex(1)

