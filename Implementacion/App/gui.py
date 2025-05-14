import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Mi Primera App con PySide")
window.setGeometry(100, 100, 400, 200)  # x, y, ancho, alto

label = QLabel("¡Hola Mundo!", parent=window)
label.move(150, 80)

window.show()
sys.exit(app.exec())
