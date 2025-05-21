#Importa los componentes que necesitamos
from PySide6.QtWidgets import QApplication, QWidget

#Este módulo permite el procesamiento de argumentos de la línea de comandos
import sys

app = QApplication(sys.argv)

window = QWidget()
window.show()

app.exec()