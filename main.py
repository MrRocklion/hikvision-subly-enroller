from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHBoxLayout, QStackedWidget, QHeaderView
)
import sys
from ui.home_screen import HomeScreen  
from ui.enroll_screen import EnrollScreen  


class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()

        self.primera_ventana = HomeScreen(self.stacked_widget)
        self.segunda_ventana = EnrollScreen(self.stacked_widget)

        self.stacked_widget.addWidget(self.primera_ventana)
        self.stacked_widget.addWidget(self.segunda_ventana)

        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.setWindowTitle("Programa con QStackedWidget")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.resize(400, 300)
    ventana.show()
    sys.exit(app.exec())
