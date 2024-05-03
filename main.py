from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, QDialog, QLabel, QVBoxLayout, QAbstractItemView, QMessageBox, QProgressDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QStringListModel
import numpy as np
import matplotlib.pyplot as plt
import imageio
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
from PIL import Image

class PrevisualizacionImagen(QDialog):
    
    def __init__(self, ruta_imagen):
        
        super().__init__()

        # Configurar la ventana modal
        self.setWindowTitle("Previsualización de la imagen " + ruta_imagen)

        # Obtener el tamaño de la pantalla
        pantalla = QApplication.desktop().screenGeometry()
        pantalla_ancho = pantalla.width()

        # Cargar la imagen desde la ruta
        pixmap = QPixmap(ruta_imagen)

        # Escalar la imagen para ajustarse al ancho de la pantalla
        pixmap = pixmap.scaledToWidth(round(pantalla_ancho * 0.8))

        # Crear un QLabel para mostrar la imagen
        label_imagen = QLabel()
        label_imagen.setPixmap(pixmap)

        # Crear un layout vertical y agregar el QLabel
        layout = QVBoxLayout()
        layout.addWidget(label_imagen)

        # Establecer el layout en la ventana modal
        self.setLayout(layout)

class Ventana(QMainWindow):
    
    def __init__(self):
        
        super(Ventana, self).__init__()
        self.setGeometry(0, 0, 800, 480)
        uic.loadUi("./ui/main.ui", self)
        self.btn_cargar_img.clicked.connect(self.abrir_explorador)
        self.btn_exportar_txt.clicked.connect(self.exportar_coordenadas)
        self.mostrar_grafico3D.clicked.connect(self.mostrar_en_3d)
        self.btn_procesar_img.clicked.connect(self.fase_final)
        self.btn_limpiar_area.clicked.connect(self.limpiar_area_trabajo)
        self.btn_quitarimg.clicked.connect(self.quitar_imagen)
        self.list_img.doubleClicked.connect(self.previsualizar_imagen)
        self.btn_exportar_imagen.clicked.connect(self.exportar_imagen)
        self.imagenes_cargadas = []  # Lista para almacenar las rutas de las imágenes cargadas
        self.center()  # Centrar la ventana al iniciar
        # Deshabilitar la edición en el QListView
        self.list_img.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.visualizacion_3d_creada = False
        self.operador_umbral_menor = '<'  # Inicialmente establecido en <=
        self.operador_umbral_mayor = '>'  # Inicialmente establecido en >=
        self.btn_umbral_menor.clicked.connect(self.set_operador_umbral_menor)
        self.btn_umbral_mayor.clicked.connect(self.set_operador_umbral_mayor)
        
    def set_operador_umbral_menor(self):
        if self.operador_umbral_menor == '<=':
            self.operador_umbral_menor = '<'
            self.btn_umbral_menor.setText('<')
        else:
            self.operador_umbral_menor = '<='
            self.btn_umbral_menor.setText('<=')
        self.set_button_style(self.btn_umbral_menor)

    def set_operador_umbral_mayor(self):
        if self.operador_umbral_mayor == '>=':
            self.operador_umbral_mayor = '>'
            self.btn_umbral_mayor.setText('<')
        else:
            self.operador_umbral_mayor = '>='
            self.btn_umbral_mayor.setText('<=')
        self.set_button_style(self.btn_umbral_mayor)
        
    def set_button_style(self, button):
        # Establecer el estilo del botón según el operador actual
        if button.text() == '<':
            button.setStyleSheet("""
                QPushButton {
                    background-color: #F2AD55; /* Color de fondo */
                    border: 2px solid #DA7C04; /* Borde */
                    border-radius: 5px; /* Bordes redondeados */
                    color: #000; /* Color del texto */
                    padding: 5px 10px; /* Espaciado interno (vertical horizontal) */
                    font: 8pt "Verdana";
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #F2DD55; /* Color de fondo */
                    border: 2px solid #DA7C04; /* Borde */
                    border-radius: 5px; /* Bordes redondeados */
                    color: #000; /* Color del texto */
                    padding: 5px 10px; /* Espaciado interno (vertical horizontal) */
                    font: 8pt "Verdana";
                }
            """)
        
    def previsualizar_imagen(self, index):
        # Obtener el índice de la imagen seleccionada
        indice_seleccionado = index.row()

        # Verificar si se seleccionó una imagen
        if indice_seleccionado >= 0:
            # Obtener la ruta de la imagen
            ruta_imagen = self.imagenes_cargadas[indice_seleccionado]

            # Crear una ventana de previsualización de la imagen
            ventana_previsualizacion = PrevisualizacionImagen(ruta_imagen)
            ventana_previsualizacion.exec_()
        else:
            QMessageBox.information(self, "Información", "No se ha seleccionado ninguna imagen.")
        
    def quitar_imagen(self):
        # Obtener el índice de la imagen seleccionada en la lista
        indice_seleccionado = self.list_img.currentIndex().row()

        # Verificar si se seleccionó una imagen
        if indice_seleccionado >= 0:
            # Eliminar la imagen de la lista de imágenes cargadas
            del self.imagenes_cargadas[indice_seleccionado]
            # Actualizar la lista de imágenes en la interfaz
            self.actualizar_lista_imagenes()
            QMessageBox.information(self, "Información", "Imagen eliminada correctamente.")
        else:
            QMessageBox.information(self, "Información", "No se ha seleccionado ninguna imagen.")
        
    def center(self):
        # Obtener la geometría de la pantalla
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def abrir_explorador(self):
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.DontUseNativeDialog
        archivos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar imágenes", "", "Archivos de imagen (*.jpg *.png *.bmp *.gif)", options=opciones)
        if archivos:
            self.imagenes_cargadas.extend(archivos)  # Agregar las rutas de las imágenes seleccionadas a la lista
            self.actualizar_lista_imagenes()
            
    def actualizar_lista_imagenes(self):
        # Mostrar los nombres de las imágenes en el listView
        modelo = QStringListModel()
        modelo.setStringList([archivo.split('/')[-1] for archivo in self.imagenes_cargadas])
        self.list_img.setModel(modelo)
        
    def fase_final(self):
        
        if hasattr(self, 'figura_3d'):
            del self.figura_3d
        
        # Verificar si hay imágenes cargadas
        if not self.imagenes_cargadas:
            QMessageBox.information(self, "Información", "No hay imágenes cargadas.")
            return
        
        # Filtrar las imágenes de referencia y deformación
        ref_images = [image for image in self.imagenes_cargadas if 'ref' in image]
        def_images = [image for image in self.imagenes_cargadas if 'def' in image]
        
        if len(ref_images) != 4 or len(def_images) != 4:
            QMessageBox.information(self, "Información", "Faltan imágenes de referencia o deformación.")
            return
        
        # Ordenar las imágenes según su número de referencia o deformación en el nombre de archivo
        ref_images_sorted = sorted(ref_images, key=lambda x: int(x.split('/')[-1].split('ref')[1].split('.')[0]))
        def_images_sorted = sorted(def_images, key=lambda x: int(x.split('/')[-1].split('def')[1].split('.')[0]))
        
        # Leer las imágenes de referencia
        R_images = [imageio.imread(image).astype(float) for image in ref_images_sorted]
        
        # Leer las imágenes de deformación
        D_images = [imageio.imread(image).astype(float) for image in def_images_sorted]
        
        # Asignar las imágenes a las variables correspondientes
        R1, R2, R3, R4 = R_images
        D1, D2, D3, D4 = D_images

        # Obtener las expresiones de los QLineEdit
        NR_expresion = self.lineEdit_NR.text()
        DR_expresion = self.lineEdit_DR.text()
        ND_expresion = self.lineEdit_ND.text()
        DD_expresion = self.lineEdit_DD.text()
        
        try:
            # Evaluar las expresiones para obtener los valores
            NR = eval(NR_expresion)
            DR = eval(DR_expresion)
            ND = eval(ND_expresion)
            DD = eval(DD_expresion)
        except Exception as e:
            QMessageBox.information(self, "Error", f"Error al evaluar las expresiones: {e}")
            return

        # Obtener las expresiones de los QLineEdit
        expresiones_fase_dif = self.lineEdit_fase_dif.text().split(',')

        # Verificar si se ingresaron dos expresiones
        if len(expresiones_fase_dif) != 2:
            QMessageBox.information(self, "Información", "Se deben ingresar exactamente dos expresiones separadas por coma.")
            return
        
        try:
            # Evaluar las expresiones para obtener los valores
            self.d_phi = np.arctan2(eval(expresiones_fase_dif[0]), eval(expresiones_fase_dif[1]))
            d_phi2 = self.d_phi
        except Exception as e:
            QMessageBox.information(self, "Error", f"Error al evaluar las expresiones: {e}")
            return

        # Visualización de la fase diferencial en 2D y 3D en la misma ventana
        fig, ax = plt.subplots(figsize=(6, 6))

        # Visualización en 2D
        fase2D = ax.imshow(d_phi2, cmap='gray')
        ax.set_title('Matriz de datos')
        ax.set_xlabel('Columna')
        ax.set_ylabel('Fila')
        plt.colorbar(fase2D, ax=ax)

        # Convertir el gráfico a una imagen para mostrarlo en la interfaz PyQt5
        fig.canvas.draw()
        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img = QImage(data, data.shape[1], data.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        
        self.img_graficos.setPixmap(pixmap)
        
        # Actualizar la visualización 3D si ya existe una
        if self.visualizacion_3d_creada == True:
            self.plotear_en_3d(self.d_phi)
            self.mostrar_en_3d()
        else:
            # Guardar el gráfico 3D en una variable de instancia
            self.figura_3d = self.plotear_en_3d(self.d_phi)
            # No llamar a mostrar_en_3d() aquí, ya que se llamará después de actualizar la figura 3D
        
    def plotear_en_3d(self, d_phi):
        
        #print("El valor de d_phi es: ", d_phi)
        # Obtener los umbrales de los lineEdit
        umbral_menor_text = self.lineEdit_umbral_menor.text()
        umbral_mayor_text = self.lineEdit_umbral_mayor.text()
        
        # Determinar los valores predeterminados si no se ingresan valores en los lineEdit
        if not umbral_menor_text:
            umbral_menor = np.min(d_phi)
            self.lineEdit_umbral_menor.setText(str(umbral_menor))  # Establecer el valor predeterminado en el lineEdit
        else:
            umbral_menor = float(umbral_menor_text)
            
        if not umbral_mayor_text:
            umbral_mayor = np.max(d_phi)
            self.lineEdit_umbral_mayor.setText(str(umbral_mayor))  # Establecer el valor predeterminado en el lineEdit
        else:
            umbral_mayor = float(umbral_mayor_text)
            
        # Establecer el cursor al principio del texto en los lineEdit
        self.lineEdit_umbral_menor.setCursorPosition(0)
        self.lineEdit_umbral_mayor.setCursorPosition(0)
        
        # Limpiar el gráfico 3D si ya existe
        if hasattr(self, 'figura_3d'):
            plt.clf()
        else:
            # Crear una nueva figura solo si no existe
            self.figura_3d = plt.figure()
            
        # Obtener el subplot 3D
        ax = self.figura_3d.add_subplot(111, projection='3d')
        
        # Obtener las dimensiones de la imagen def1
        def1_path = self.imagenes_cargadas[0]  # Suponiendo que la imagen def1 es la primera en la lista
        def1_image = Image.open(def1_path)
        def1_width, def1_height = def1_image.size
        
        #print("def1_width: ", def1_width)
        #print("def1_height: ", def1_height)

        # Establecer el tamaño de la gráfica 3D
        ax.set_xlim(0, def1_width)
        ax.set_ylim(0, def1_height)
        
        # Crear la malla para el gráfico
        x, y = np.meshgrid(np.arange(d_phi.shape[1]), np.arange(d_phi.shape[0]))
        
        # Aplicar el umbral a la matriz d_phi
        if self.operador_umbral_menor is not None and self.operador_umbral_mayor is not None:
            d_phi_masked = np.ma.masked_where(
                (eval(f'd_phi {self.operador_umbral_menor} umbral_menor')) |
                (eval(f'd_phi {self.operador_umbral_mayor} umbral_mayor')), 
                d_phi
            )
        else:
            # Si no se ha establecido un operador, usar un umbral estándar
            d_phi_masked = np.ma.masked_where((d_phi < umbral_menor) | (d_phi > umbral_mayor), d_phi)
        
        # Limpiar el subplot 3D si ya tiene una superficie
        ax.clear()
        
        # Graficar la nueva superficie 3D
        surf = ax.plot_surface(x, y, d_phi_masked, cmap='viridis')
        
        # Configurar título y etiquetas de los ejes
        ax.set_title('Visualización en 3D')
        ax.set_xlabel('Columna')
        ax.set_ylabel('Fila')
        ax.set_zlabel('Fase')
        
        # Añadir una barra de color
        self.figura_3d.colorbar(surf, ax=ax)
        
        return self.figura_3d
        
    def mostrar_en_3d(self):
        
        # Verificar si ya hay una previsualización 3D en la ventana
        if hasattr(self, 'widget') and self.widget.layout():
            # Eliminar todos los widgets del layout
            for i in reversed(range(self.layoutv.count())):
                widget = self.layoutv.itemAt(i).widget()
                self.layoutv.removeWidget(widget)
                widget.deleteLater()

        # Obtener el canvas de la figura 3D
        canvas = FigureCanvas(self.figura_3d)
        
        self.layoutv.addWidget(canvas)
        
        # Crear un nuevo widget para la nueva ventana
        self.widget.setLayout(self.layoutv)
        
        self.visualizacion_3d_creada = True
        
        # Mostrar la nueva ventana con la visualización 3D
        self.widget.show()
        
    def limpiar_area_trabajo(self):
        # Limpiar la lista de imágenes cargadas
        self.imagenes_cargadas = []
        # Limpiar la visualización de la imagen en el QLabel
        self.img_graficos.clear()
        # Limpiar el modelo de la lista de imágenes
        modelo_vacio = QStringListModel()
        self.list_img.setModel(modelo_vacio)
        # Limpiar la figura 3D si está cargada
        if hasattr(self, 'figura_3d'):
            plt.close(self.figura_3d)
            del self.figura_3d 
            # Eliminar todos los widgets del layout
            for i in reversed(range(self.layoutv.count())):
                widget = self.layoutv.itemAt(i).widget()
                self.layoutv.removeWidget(widget)
                widget.deleteLater()
        
        self.visualizacion_3d_creada = False
        
    def exportar_imagen(self):
        # Exportar imagen 2D
        pixmap_img_graficos = self.img_graficos.pixmap()
        img_graficos_pil = pixmap_img_graficos.toImage()
        img_graficos_pil.save("imagen_2D.png")

        # Exportar imagen 3D
        self.figura_3d.savefig("imagen_3D.png")

        # Combinar imágenes
        imagen_2D = Image.open("imagen_2D.png")
        imagen_3D = Image.open("imagen_3D.png")
        
        # Ajustar tamaño si es necesario
        imagen_2D = imagen_2D.resize(imagen_3D.size)
        
        # Crear una nueva imagen combinando ambas
        imagen_combinada = Image.new("RGB", (imagen_2D.width + imagen_3D.width, max(imagen_2D.height, imagen_3D.height)))
        imagen_combinada.paste(imagen_2D, (0, 0))
        imagen_combinada.paste(imagen_3D, (imagen_2D.width, 0))

        # Guardar la imagen combinada
        ruta_guardar, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen", "", "Archivos de imagen (*.png)")
        if ruta_guardar:
            imagen_combinada.save(ruta_guardar)
            QMessageBox.information(self, "Información", f"¡Imagen guardada con éxito en: {ruta_guardar}")

        # Eliminar imágenes temporales
        os.remove("imagen_2D.png")
        os.remove("imagen_3D.png")
        
    def exportar_coordenadas(self):
        if hasattr(self, 'figura_3d') and hasattr(self.figura_3d, 'axes'):
            # Obtener el subplot 3D
            ax = self.figura_3d.axes[0]

            # Obtener las dimensiones de la matriz de fase
            n_rows, n_cols = self.d_phi.shape

            # Crear un arreglo de coordenadas z usando la matriz de fase d_phi
            z = self.d_phi.flatten()  # Aplanamos la matriz de fase

            # Crear arreglos de coordenadas x e y
            x, y = np.meshgrid(np.arange(n_cols), np.arange(n_rows))
            x = x.flatten()  # Aplanamos las matrices x e y
            y = y.flatten()

            # Aplicar el umbral a la matriz d_phi
            umbral_menor = float(self.lineEdit_umbral_menor.text())
            umbral_mayor = float(self.lineEdit_umbral_mayor.text())
            d_phi_masked = np.ma.masked_where(
                (self.d_phi < umbral_menor) | (self.d_phi > umbral_mayor), 
                self.d_phi
            )

            # Crear un archivo de texto para guardar las coordenadas con el umbral aplicado
            ruta_guardar, _ = QFileDialog.getSaveFileName(self, "Guardar Coordenadas", "", "Archivos de texto (*.txt)")
            if ruta_guardar:
                # Mostrar ventana de progreso
                progress = QProgressDialog("Exportando coordenadas...", None, 0, 100, self)
                progress.setWindowModality(QtCore.Qt.WindowModal)
                progress.setWindowTitle("Exportando...")
                progress.show()

                with open(ruta_guardar, 'w') as file:
                    file.write("Coordenadas de la superficie 3D con umbral aplicado:\n")
                    file.write("Coordenadas X, Y, Z:\n")
                    for i in range(len(x)):
                        if not np.ma.is_masked(d_phi_masked.flat[i]):
                            file.write(f"{x[i]}, {y[i]}, {z[i]}\n")
                        # Actualizar ventana de progreso
                        progress.setValue(int(i * 100 / len(x)))

                progress.setValue(100)  # Completa el progreso
                QMessageBox.information(self, "Información", f"¡Coordenadas con umbral aplicado guardadas con éxito en: {ruta_guardar}")
        else:
            QMessageBox.warning(self, "Advertencia", "No hay gráfica 3D para exportar coordenadas.")
        
if __name__ == '__main__':
    print("\x1b[1;32m"+"Iniciando...")
    app = QApplication(['a'])
    GUI = Ventana()
    GUI.showMaximized()
    GUI.setWindowTitle("Dra. Angeles Mtz. Rmz.")
    GUI.show()
    sys.exit(app.exec())