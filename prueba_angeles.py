import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget, QMessageBox, QLabel, QDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage

class PrevisualizacionImagen(QDialog):
    def __init__(self, ruta_imagen):
        super().__init__()
        self.setWindowTitle('Previsualización de la Imagen')
        self.layout = QVBoxLayout()

        # Mostrar imagen original
        self.imagen_original = QLabel(self)
        self.mostrar_imagen(self.imagen_original, ruta_imagen)
        self.layout.addWidget(self.imagen_original)

        # Botón para eliminar sombras
        self.boton_eliminar_sombras = QPushButton("Eliminar sombras")
        self.boton_eliminar_sombras.clicked.connect(lambda: self.eliminar_sombras(ruta_imagen))
        self.layout.addWidget(self.boton_eliminar_sombras)

        # Mostrar imagen sin sombras
        self.imagen_sin_sombras = QLabel(self)
        self.layout.addWidget(self.imagen_sin_sombras)

        self.setLayout(self.layout)

    def mostrar_imagen(self, label, ruta_imagen):
        image = cv2.imread(ruta_imagen)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        label.setPixmap(pixmap)

    def eliminar_sombras(self, ruta_imagen):
        image = cv2.imread(ruta_imagen)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        corrected = cv2.divide(gray, background, scale=255)
        _, binary = cv2.threshold(corrected, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        denoised = cv2.medianBlur(binary, 5)
        result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

        height, width, channel = result.shape
        bytes_per_line = 3 * width
        q_img = QImage(result.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.imagen_sin_sombras.setPixmap(pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplicación de Previsualización de Imágenes')
        self.setGeometry(100, 100, 800, 600)

        self.imagenes_cargadas = [
            './img/def1.jpg',
            './img/def2.jpg',
            './img/def3.jpg',
            './img/def4.jpg'
        ]

        layout = QVBoxLayout()

        self.lista_imagenes = QListWidget(self)
        for imagen in self.imagenes_cargadas:
            self.lista_imagenes.addItem(imagen)
        self.lista_imagenes.clicked.connect(self.previsualizar_imagen)

        layout.addWidget(self.lista_imagenes)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def previsualizar_imagen(self, index):
        indice_seleccionado = index.row()
        if indice_seleccionado >= 0:
            ruta_imagen = self.imagenes_cargadas[indice_seleccionado]
            print("La ruta de la imagen es: ", ruta_imagen)
            ventana_previsualizacion = PrevisualizacionImagen(ruta_imagen)
            ventana_previsualizacion.exec_()
        else:
            QMessageBox.information(self, "Información", "No se ha seleccionado ninguna imagen.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())