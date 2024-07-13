# The above code is a Python script that imports various modules from PyQt5 library for creating a GUI
# application. It also imports modules like numpy, matplotlib, imageio, sys, os, and PIL for handling
# image processing tasks. The script defines a class that inherits from QMainWindow and sets up a GUI
# window with various widgets like labels, layouts, file dialogs, progress dialogs, etc. It also
# includes functionality for displaying images using QPixmap, plotting graphs using matplotlib, and
# working with image files using PIL and imageio. Overall, the script seems to be a template for an
# image processing application with a graphical user
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, QDialog, QLabel, QVBoxLayout, QAbstractItemView, QMessageBox, QProgressDialog, QWidget, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QStringListModel
import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from PIL import Image

# This Python class creates a QDialog window to display an image scaled to fit 80% of the screen
# width.
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
        
class GraphWindow(QMainWindow):
    def __init__(self, wrapped_phase, parent=None):
        super(GraphWindow, self).__init__(parent)
        
        self.setWindowTitle("Gráficos")
        self.setGeometry(100, 100, 1200, 800)
        
        # Calculate the necessary values
        self.wrapped_phase = wrapped_phase
        self.calculate_graphs()
        
        # Create a QWidget as a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create a vertical layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create matplotlib figures
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(self.canvas)
        
        # Plot the graphs
        self.plot_graphs()
        
    def calculate_graphs(self):
        # Calculate gradient of the wrapped phase
        self.gx, self.gy = np.gradient(self.wrapped_phase)

        # Compute the Laplacian of the gradient
        self.laplacian = np.gradient(self.gx)[0] + np.gradient(self.gy)[1]

        # Compute the 2D unwrapped phase using Fourier transform
        self.unwrapped_phase = np.real(np.fft.ifft2(-self.laplacian))
    
    def plot_graphs(self):
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(131)
        ax1.imshow(self.gx, cmap='gray')
        ax1.set_title('Gradient gx')

        ax2 = self.figure.add_subplot(132)
        ax2.imshow(self.laplacian, cmap='gray')
        ax2.set_title('Laplacian')

        ax3 = self.figure.add_subplot(133)
        ax3.imshow(self.unwrapped_phase, cmap='gray')
        ax3.set_title('Unwrapped Phase')

        self.canvas.draw()
        
        
class ImagePickerWidget(QWidget):
    def __init__(self, parent, widget_name, label_name, boton_name):
        super().__init__(parent)
        
        self.parentM = parent
        self.widget_name = widget_name
        self.label_name = label_name
        self.boton_name = boton_name

        self.w_drop = self.parentM.findChild(QWidget, self.widget_name)
        self.image_label = self.parentM.findChild(QLabel, self.label_name)

        if self.w_drop:
            self.w_drop.setAcceptDrops(True)
            self.w_drop.dragEnterEvent = self.dragEnterEvent
            self.w_drop.dropEvent = self.dropEvent
        else:
            print(f"Error: '{self.widget_name}' widget no encontrado.")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            #print("El URL es: ", file_path)
            self.parentM.imagenes_cargadas[self.boton_name] = file_path
            self.parentM.actualizar_lista_imagenes()
            self.display_image(file_path)
            
    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()
        
        
class Ventana3D(QMainWindow):
    def __init__(self, d_phi, point_cloud, imagen_def1, umbral_menor, umbral_mayor, operador_umbral_menor, operador_umbral_mayor, parent=None):
        super(Ventana3D, self).__init__(parent)
        self.setWindowTitle("Visualización 3D")
        self.setGeometry(100, 100, 1200, 600)

        # Crear una figura con dos subplots
        self.figura = plt.figure(figsize=(10, 5))

        # Primer subplot: la figura 3D
        ax1 = self.figura.add_subplot(121, projection='3d')

        # Obtener las dimensiones de la imagen def1
        def1_image = Image.open(imagen_def1)
        def1_width, def1_height = def1_image.size
        
        # Establecer el tamaño de la gráfica 3D
        ax1.set_xlim(0, def1_width)
        ax1.set_ylim(0, def1_height)

        # Crear la malla para el gráfico
        x, y = np.meshgrid(np.arange(d_phi.shape[1]), np.arange(d_phi.shape[0]))
        
        # Aplicar el umbral a la matriz d_phi
        if operador_umbral_menor is not None and operador_umbral_mayor is not None:
            d_phi_masked = np.ma.masked_where(
                (eval(f'd_phi {operador_umbral_menor} umbral_menor')) |
                (eval(f'd_phi {operador_umbral_mayor} umbral_mayor')), 
                d_phi
            )
        else:
            d_phi_masked = np.ma.masked_where((d_phi < umbral_menor) | (d_phi > umbral_mayor), d_phi)
            
        # Guardar coordenadas en el parent
        parent.coordenadas = {
            'x': x.flatten(),
            'y': y.flatten(),
            'd_phi_masked': d_phi_masked.flatten()
        }
        
        # Graficar la nueva superficie 3D
        surf = ax1.plot_surface(x, y, d_phi_masked, cmap='viridis')
        
        # Configurar título y etiquetas de los ejes
        ax1.set_title('Visualización en 3D')
        ax1.set_xlabel('Columna')
        ax1.set_ylabel('Fila')
        ax1.set_zlabel('Fase')
        
        # Añadir una barra de color
        self.figura.colorbar(surf, ax=ax1)
        
        parent.figura_3d = self.figura

        # Segundo subplot: la nube de puntos
        ax2 = self.figura.add_subplot(122, projection='3d')
        ax2.scatter(point_cloud[:, 0], point_cloud[:, 1], point_cloud[:, 2], c=point_cloud[:, 2], cmap='gray')
        ax2.set_title('Point Cloud')
        ax2.set_xlabel('Columna')
        ax2.set_ylabel('Fila')
        ax2.set_zlabel('Altura')

        # Crear un canvas para la figura con ambos subplots
        canvas = FigureCanvas(self.figura)

        # Crear un layout y agregar el canvas
        layout = QVBoxLayout()
        layout.addWidget(canvas)

        # Crear un widget central y establecer el layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Botón para guardar imagen
        self.btn_guardar_imagen = QPushButton('Guardar Imagen', self)
        self.btn_guardar_imagen.clicked.connect(self.guardar_imagen)
        layout.addWidget(self.btn_guardar_imagen)
        
    def guardar_imagen(self):
        """
        The function `guardar_imagen` allows the user to save the 3D visualization image.
        """
        # Obtener el nombre de archivo para guardar
        ruta_guardar, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen 3D", "", "Archivos de imagen (*.png)")

        if ruta_guardar:
            # Guardar la figura actual en el archivo especificado
            self.figura.savefig(ruta_guardar)
            QMessageBox.information(self, "Información", f"¡Imagen 3D guardada con éxito en: {ruta_guardar}")

    def closeEvent(self, event):
        """
        Override closeEvent para limpiar recursos al cerrar la ventana.
        """
        # Eliminar imágenes temporales u otros recursos si es necesario
        super().closeEvent(event)

# This class represents a QMainWindow in a Python application with various functionalities related to
# image processing and visualization.
class Ventana(QMainWindow):
    
    def __init__(self):
        """
        The function initializes a PyQt5 window with various UI elements and connects them to different
        functions.
        """
        
        super(Ventana, self).__init__()
        self.setGeometry(0, 0, 800, 480)
        uic.loadUi("./ui/main.ui", self)
        
        # Conectar los botones a la función abrir_explorador
        self.def1.clicked.connect(self.abrir_explorador)
        self.def2.clicked.connect(self.abrir_explorador)
        self.def3.clicked.connect(self.abrir_explorador)
        self.def4.clicked.connect(self.abrir_explorador)
        self.ref1.clicked.connect(self.abrir_explorador)
        self.ref2.clicked.connect(self.abrir_explorador)
        self.ref3.clicked.connect(self.abrir_explorador)
        self.ref4.clicked.connect(self.abrir_explorador)
        
        self.w_drop1 = ImagePickerWidget(self, "w_drop1", "lbl_def1", "def1")
        self.w_drop1 = ImagePickerWidget(self, "w_drop2", "lbl_def2", "def2")
        self.w_drop1 = ImagePickerWidget(self, "w_drop3", "lbl_def3", "def3")
        self.w_drop1 = ImagePickerWidget(self, "w_drop4", "lbl_def4", "def4")
        self.w_drop1 = ImagePickerWidget(self, "w_drop5", "lbl_ref1", "ref1")
        self.w_drop1 = ImagePickerWidget(self, "w_drop6", "lbl_ref2", "ref2")
        self.w_drop1 = ImagePickerWidget(self, "w_drop7", "lbl_ref3", "ref3")
        self.w_drop1 = ImagePickerWidget(self, "w_drop8", "lbl_ref4", "ref4")
        
        # Asignar identificadores únicos a cada botón
        self.def1.setObjectName("def1")
        self.def2.setObjectName("def2")
        self.def3.setObjectName("def3")
        self.def4.setObjectName("def4")
        self.ref1.setObjectName("ref1")
        self.ref2.setObjectName("ref2")
        self.ref3.setObjectName("ref3")
        self.ref4.setObjectName("ref4")
        
        self.btn_show_graphs.clicked.connect(self.mostrar_graficos)
        
        self.btn_exportar_txt.clicked.connect(self.exportar_coordenadas)
        self.mostrar_grafico3D.clicked.connect(self.mostrar_en_3d)
        self.btn_procesar_img.clicked.connect(self.fase_final)
        self.btn_limpiar_area.clicked.connect(self.limpiar_area_trabajo)
        self.btn_quitarimg.clicked.connect(self.quitar_imagen)
        self.list_img.doubleClicked.connect(self.previsualizar_imagen)
        self.btn_exportar_imagen.clicked.connect(self.exportar_imagen)
        
        self.imagenes_cargadas = {
            "def1": None,
            "def2": None,
            "def3": None,
            "def4": None,
            "ref1": None,
            "ref2": None,
            "ref3": None,
            "ref4": None
        }
        
        self.coordenadas = None  # Inicializamos coordenadas como None al principio
        
        self.center()  # Centrar la ventana al iniciar
        # Deshabilitar la edición en el QListView
        self.list_img.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.visualizacion_3d_creada = False
        self.operador_umbral_menor = '<'  # Inicialmente establecido en <=
        self.operador_umbral_mayor = '>'  # Inicialmente establecido en >=
        self.btn_umbral_menor.clicked.connect(self.set_operador_umbral_menor)
        self.btn_umbral_mayor.clicked.connect(self.set_operador_umbral_mayor)
        
        self.unwrapped_phase_goldstein_unwrap = np.array([])
        self.height_map = ""
        self.point_cloud = ""
        
    def mostrar_graficos(self):
        if self.unwrapped_phase_goldstein_unwrap.size > 0:
            self.graph_window = GraphWindow(self.unwrapped_phase_goldstein_unwrap)
            self.graph_window.show()
        else:
            QMessageBox.information(self, "Información", "No existe gráficos para mostrar.")
        
    def set_operador_umbral_menor(self):
        """
        This function toggles between '<' and '<=' for a threshold operator and updates a button text
        accordingly.
        """
        if self.operador_umbral_menor == '<=':
            self.operador_umbral_menor = '<'
            self.btn_umbral_menor.setText('<')
        else:
            self.operador_umbral_menor = '<='
            self.btn_umbral_menor.setText('<=')
        self.set_button_style(self.btn_umbral_menor)

    def set_operador_umbral_mayor(self):
        """
        This Python function toggles between two comparison operators and updates a button text
        accordingly.
        """
        if self.operador_umbral_mayor == '>=':
            self.operador_umbral_mayor = '>'
            self.btn_umbral_mayor.setText('<')
        else:
            self.operador_umbral_mayor = '>='
            self.btn_umbral_mayor.setText('<=')
        self.set_button_style(self.btn_umbral_mayor)
        
    def set_button_style(self, button):
        """
        The function `set_button_style` sets the style of a button based on its text value.
        
        :param button: The `button` parameter in the `set_button_style` method is a QPushButton widget
        that you want to style based on its text value. The method checks if the text of the button is
        `'<'`, and if it is, it sets a specific style for that button. Otherwise, it sets a
        """
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
        """
        This function previews an image selected from a list of loaded images in a separate window.
        
        :param index: The `index` parameter is typically an index object that represents the location
        of an item within a model. In this context, it is used to determine the selected image from a
        list of loaded images.
        """
        # Obtener el nombre del botón asociado al índice de la imagen seleccionada
        sender_names = list(self.imagenes_cargadas.keys())
        if index.row() < len(sender_names):
            sender_name = sender_names[index.row()]
            
            # Obtener la ruta de la imagen
            ruta_imagen = self.imagenes_cargadas.get(sender_name)

            # Verificar si se seleccionó una imagen
            if ruta_imagen:
                # Crear una ventana de previsualización de la imagen
                ventana_previsualizacion = PrevisualizacionImagen(ruta_imagen)
                ventana_previsualizacion.exec_()
            else:
                QMessageBox.information(self, "Información", "No se ha seleccionado ninguna imagen.")
        else:
            QMessageBox.information(self, "Información", "Índice de imagen seleccionado no válido.")
            
    def goldstein_unwrap(self, phase_map):
        
        try:
            rows, cols = phase_map.shape

            # Initialize the unwrapped phase map
            unwrapped_phase = np.zeros((rows, cols))

            # Phase difference thresholds
            threshold = np.pi

            # Loop through each pixel in the phase map
            for r in range(rows):
                for c in range(cols):
                    # Calculate differences between neighboring pixels
                    delta_r = 0
                    delta_c = 0
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr != 0 or dc != 0:
                                r_neighbor = r + dr
                                c_neighbor = c + dc
                                if 0 <= r_neighbor < rows and 0 <= c_neighbor < cols:
                                    delta_r += np.sin(phase_map[r_neighbor, c_neighbor] - phase_map[r, c])
                                    delta_c += np.cos(phase_map[r_neighbor, c_neighbor] - phase_map[r, c])

                    # Calculate the unwrapped phase value
                    unwrapped_phase[r, c] = phase_map[r, c] + np.arctan2(delta_r, delta_c)

                    # Perform 2π jumps corrections
                    while (unwrapped_phase[r, c] - phase_map[r, c]) > threshold:
                        unwrapped_phase[r, c] -= 2 * np.pi

                    while (unwrapped_phase[r, c] - phase_map[r, c]) < -threshold:
                        unwrapped_phase[r, c] += 2 * np.pi
            
            self.unwrapped_phase_goldstein_unwrap = unwrapped_phase
            
            return unwrapped_phase
        except Exception as e:
            print("Fallo goldstein_unwrap: ", e)
            QMessageBox.information(self, "Error", f"Fallo goldstein_unwrap: {e}")

    def takeda_phase_unwrap(self, wrapped_phase):
        
        try:
            # Calculate gradient of the wrapped phase
            gx, gy = np.gradient(wrapped_phase)

            # Compute the Laplacian of the gradient
            laplacian = np.gradient(gx)[0] + np.gradient(gy)[1]#np.del2(gx + 1j * gy)

            # Compute the 2D unwrapped phase using Fourier transform
            unwrapped_phase = np.real(np.fft.ifft2(-laplacian))

            # Adjust the phase to be in the range [-pi, pi]
            unwrapped_phase = np.mod(unwrapped_phase + np.pi, 2 * np.pi) - np.pi

            return unwrapped_phase
        except Exception as e:
            print("Fallo takeda_phase_unwrap: ", e)
            QMessageBox.information(self, "Error", f"Fallo takeda_phase_unwrap: {e}")

    def phase_to_height(self, data, distance_reference_plane, distance_CCD_projector, period):
        
        try:
            distance_reference_plane = int(distance_reference_plane)
            distance_CCD_projector = int(distance_CCD_projector)
            period = int(period)
            # Unwrap the phase using Takeda's algorithm
            unwrapped_phase_map = self.takeda_phase_unwrap(data)

            # Convert unwrapped phase to height distribution
            height_map = (unwrapped_phase_map * period) / (2 * np.pi)

            # Convert height to real-world coordinates (in meters)
            height_map = (height_map * distance_reference_plane) / distance_CCD_projector

            # Reconstruct the 3D object
            rows, cols = height_map.shape
            X, Y = np.meshgrid(np.arange(1, cols+1), np.arange(1, rows+1))
            X = X - (cols + 1) / 2  # Centering X and Y coordinates
            Y = Y - (rows + 1) / 2
            point_cloud = np.vstack((X.ravel(), Y.ravel(), height_map.ravel())).T

            return height_map, point_cloud
        except Exception as e:
            print("Fallo phase_to_height: ", e)
            QMessageBox.information(self, "Error", f"Fallo phase_to_height: {e}")
    
    def nuevo_procesamiento(self, d_phi2):
        try:
            distance_reference_plane = self.lineEdit_distancia_plano.text()
            distance_CCD_projector = self.lineEdit_distancis_ccd.text()
            period = self.lineEdit_periodo.text()

            # Unwrap phase using Goldstein algorithm
            fase_desenvuelta = self.goldstein_unwrap(d_phi2)

            # Perform phase-to-height conversion and get the point cloud
            self.height_map, self.point_cloud = self.phase_to_height(fase_desenvuelta, distance_reference_plane, distance_CCD_projector, period)
            
            #print("El valor de height_map: ", self.height_map)
            #print("El valor de point_cloud: ", self.point_cloud)
            
            return self.height_map, self.point_cloud
        except Exception as e:
            print("Fallo el nuevo procesamiento: ", e)
            QMessageBox.information(self, "Error", f"Fallo el nuevo procesamiento: : {e}")
        
    def quitar_imagen(self):
        """
        This function removes a selected image from a list of loaded images and updates the
        interface accordingly, displaying a message to inform the user of the outcome.
        """
        # Obtener el índice de la imagen seleccionada en la lista
        indice_seleccionado = self.list_img.currentIndex().row()

        # Obtener el nombre del botón asociado al índice de la imagen seleccionada
        sender_names = list(self.imagenes_cargadas.keys())
        if indice_seleccionado >= 0 and indice_seleccionado < len(sender_names):
            sender_name = sender_names[indice_seleccionado]

            #print("Sender name: ", sender_name)
            
            #print("Imagenes cargadas: ", self.imagenes_cargadas)
            # Eliminar la imagen del diccionario de imágenes cargadas
            self.imagenes_cargadas[sender_name] = None
            
            #print("Imagenes cargadas2: ", self.imagenes_cargadas)
            
            lbl_name = "lbl_" + sender_name
            self.label = self.findChild(QLabel, lbl_name)
            
            self.label.clear()
            self.label.setText(f"Arrastra {sender_name}")
            
            # Actualizar la lista de imágenes en la interfaz
            self.actualizar_lista_imagenes()
            
            QMessageBox.information(self, "Información", "Imagen eliminada correctamente.")
        else:
            QMessageBox.information(self, "Información", "No se ha seleccionado ninguna imagen.")
        
    def center(self):
        """
        The `center` function in Python centers a window on the screen using PyQt.
        """
        # Obtener la geometría de la pantalla
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def abrir_explorador(self):
        """
        The function "abrir_explorador" opens a file dialog to select image files and adds the selected
        file paths to a list.
        """
        
        sender = self.sender()
        sender_name = sender.objectName()
        
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.DontUseNativeDialog
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Archivos de imagen (*.jpg *.png *.bmp *.gif)", options=opciones)
        if archivo:
            self.imagenes_cargadas[sender_name] = archivo
            self.actualizar_lista_imagenes()
            self.display_image(archivo, sender_name)
            
    def display_image(self, file_path, btn_name):
        pixmap = QPixmap(file_path)
        lbl_name = "lbl_" + btn_name
        self.image_label = self.findChild(QLabel, lbl_name)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()
            
    def actualizar_lista_imagenes(self):
        """
        The function updates a list view with the names of images loaded in the program.
        """
        # Mostrar los nombres de las imágenes en el listView
        modelo = QStringListModel()
        
        # Filtrar las imágenes que tienen valores (no vacías)
        imagenes_con_valores = [archivo.split('/')[-1] for archivo in self.imagenes_cargadas.values() if archivo]
        
        modelo.setStringList(imagenes_con_valores)
        self.list_img.setModel(modelo)
        
    def fase_final(self):
        """
        The function `fase_final` processes loaded images, evaluates expressions, and visualizes data in
        2D and 3D, updating the interface accordingly.
        :return: The `fase_final` method returns different messages using `QMessageBox.information` to
        inform the user about certain conditions or errors in the code. If all the conditions are met
        and no exceptions are raised during the evaluation of expressions, the method will display
        visualizations of the phase differential in 2D and 3D in the same window. The 2D visualization
        will be displayed as an
        """
        
        if hasattr(self, 'figura_3d'):
            del self.figura_3d
        
        # Verificar si hay imágenes cargadas
        if not self.imagenes_cargadas:
            QMessageBox.information(self, "Información", "No hay imágenes cargadas.")
            return
        
        # Filtrar las imágenes de referencia y deformación
        ref_images = [self.imagenes_cargadas[key] for key in self.imagenes_cargadas if 'ref' in key and self.imagenes_cargadas[key]]
        def_images = [self.imagenes_cargadas[key] for key in self.imagenes_cargadas if 'def' in key and self.imagenes_cargadas[key]]
        
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
            self.nuevo_procesamiento(d_phi2)
            print("El valor de phi2: ", d_phi2)
        except Exception as e:
            QMessageBox.information(self, "Error", f"Error al evaluar las expresiones: {e}")
            return

        # Visualización de la fase diferencial en 2D y 3D en la misma ventana
        #fig, ax = plt.subplots(figsize=(6, 6))
        fig, ax = plt.subplots(1, 2, figsize=(18, 6))
        
        # Visualización en 2D
        fase2D = ax[0].imshow(d_phi2, cmap='gray')
        ax[0].set_title('Matriz de datos')
        ax[0].set_xlabel('Columna')
        ax[0].set_ylabel('Fila')
        plt.colorbar(fase2D, ax=ax[0])
        
        # Visualización en 2D del mapa de altura
        ax[1].imshow(self.height_map, cmap='gray')
        ax[1].set_title('Height Map')
        ax[1].set_xlabel('Columna')
        ax[1].set_ylabel('Fila')
        plt.colorbar(ax[1].imshow(self.height_map, cmap='gray'), ax=ax[1])

        # Convertir el gráfico a una imagen para mostrarlo en la interfaz PyQt5
        fig.canvas.draw()
        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img = QImage(data, data.shape[1], data.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        
        self.img_graficos.setPixmap(pixmap)
        
        umbral_menor_text = self.lineEdit_umbral_mayor.text()
        umbral_mayor_text = self.lineEdit_umbral_menor.text()
        
        # Determinar los valores predeterminados si no se ingresan valores en los lineEdit
        if not umbral_menor_text:
            umbral_menor = np.min(self.d_phi)
            self.lineEdit_umbral_mayor.setText(str(umbral_menor))  # Establecer el valor predeterminado en el lineEdit
        else:
            umbral_menor = float(umbral_menor_text)
            
        if not umbral_mayor_text:
            umbral_mayor = np.max(self.d_phi)
            self.lineEdit_umbral_menor.setText(str(umbral_mayor))  # Establecer el valor predeterminado en el lineEdit
        else:
            umbral_mayor = float(umbral_mayor_text)
            
        # Establecer el cursor al principio del texto en los lineEdit
        self.lineEdit_umbral_menor.setCursorPosition(0)
        self.lineEdit_umbral_mayor.setCursorPosition(0)
        
        # # Actualizar la visualización 3D si ya existe una
        # if self.visualizacion_3d_creada == True:
        #     self.mostrar_en_3d()
        
    def mostrar_en_3d(self):
        """
        The function `mostrar_en_3d` is used to display a 3D visualization in a new window.
        """
        
        umbral_menor_text = self.lineEdit_umbral_mayor.text()
        umbral_mayor_text = self.lineEdit_umbral_menor.text()
        
        # Determinar los valores predeterminados si no se ingresan valores en los lineEdit
        if not umbral_menor_text:
            umbral_menor = np.min(self.d_phi)
            self.lineEdit_umbral_mayor.setText(str(umbral_menor))  # Establecer el valor predeterminado en el lineEdit
        else:
            umbral_menor = float(umbral_menor_text)
            
        if not umbral_mayor_text:
            umbral_mayor = np.max(self.d_phi)
            self.lineEdit_umbral_menor.setText(str(umbral_mayor))  # Establecer el valor predeterminado en el lineEdit
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
        
        # Obtener las dimensiones de la imagen def1
        def1_path = self.imagenes_cargadas["def1"]  # Suponiendo que la imagen def1 es la primera en la lista
        
        # Crear una nueva ventana para la visualización 3D con los parámetros necesarios
        self.ventana_3d = Ventana3D(
            self.d_phi,
            self.point_cloud,
            def1_path,
            umbral_menor,
            umbral_mayor,
            self.operador_umbral_menor,
            self.operador_umbral_mayor,
            self
        )
        
        # Mostrar la nueva ventana con la visualización 3D
        self.ventana_3d.show()
        
    def limpiar_area_trabajo(self):
        """
        The function `limpiar_area_trabajo` clears various elements such as loaded images, image
        display, image list model, 3D figure, and layout widgets in a Python GUI application.
        """
        # Limpiar la lista de imágenes cargadas
        self.imagenes_cargadas = {
            "def1": None,
            "def2": None,
            "def3": None,
            "def4": None,
            "ref1": None,
            "ref2": None,
            "ref3": None,
            "ref4": None
        }
        
        self.lbl_def1.clear()
        self.lbl_def1.setText("Arrastra def1")
        self.lbl_def2.clear()
        self.lbl_def2.setText("Arrastra def2")
        self.lbl_def3.clear()
        self.lbl_def3.setText("Arrastra def3")
        self.lbl_def4.clear()
        self.lbl_def4.setText("Arrastra def4")
        
        self.lbl_ref1.clear()
        self.lbl_ref1.setText("Arrastra ref1")
        self.lbl_ref2.clear()
        self.lbl_ref2.setText("Arrastra ref2")
        self.lbl_ref3.clear()
        self.lbl_ref3.setText("Arrastra ref3")
        self.lbl_ref4.clear()
        self.lbl_ref4.setText("Arrastra ref4")
        
        self.unwrapped_phase_goldstein_unwrap = np.array([])
        
        # Limpiar la visualización de la imagen en el QLabel
        self.img_graficos.clear()
        # Limpiar el modelo de la lista de imágenes
        modelo_vacio = QStringListModel()
        self.list_img.setModel(modelo_vacio)
        # Limpiar la figura 3D si está cargada
        if hasattr(self, 'figura_3d'):
            plt.close(self.figura_3d)
            del self.figura_3d 
        
        self.visualizacion_3d_creada = False
        
    def exportar_imagen(self):
        """
        The function `exportar_imagen` saves a 2D image, allows the user to save the image,
        and then deletes the temporary image.
        """
        # Exportar imagen 2D
        pixmap_img_graficos = self.img_graficos.pixmap()
        img_graficos_pil = pixmap_img_graficos.toImage()
        img_graficos_pil.save("imagen_2D.png")

        # Abrir la imagen guardada
        imagen_2D = Image.open("imagen_2D.png")

        # Guardar la imagen
        ruta_guardar, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen", "", "Archivos de imagen (*.png)")
        if ruta_guardar:
            imagen_2D.save(ruta_guardar)
            QMessageBox.information(self, "Información", f"¡Imagen guardada con éxito en: {ruta_guardar}")

        # Eliminar la imagen temporal
        os.remove("imagen_2D.png")
        
    def exportar_coordenadas(self):
        """
        Exporta las coordenadas de la gráfica 3D con umbral aplicado.
        """
        if hasattr(self, 'coordenadas'):
            coordenadas = self.coordenadas

            # Extraer coordenadas
            x = coordenadas['x']
            y = coordenadas['y']
            d_phi_masked = coordenadas['d_phi_masked']

            # Obtener las dimensiones de la matriz de fase
            n_rows, n_cols = self.d_phi.shape

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
                            file.write(f"{x[i]}, {y[i]}, {d_phi_masked.flat[i]}\n")
                        # Actualizar ventana de progreso
                        progress.setValue(int(i * 100 / len(x)))

                progress.setValue(100)  # Completa el progreso
                QMessageBox.information(self, "Información", f"¡Coordenadas con umbral aplicado guardadas con éxito en: {ruta_guardar}")
        else:
            QMessageBox.warning(self, "Advertencia", "No hay coordenadas disponibles para exportar.")

        
# The above code is a Python script that appears to be creating a GUI application using PyQt. Here is
# a breakdown of what the code is doing:
if __name__ == '__main__':
    print("\x1b[1;32m"+"Iniciando...")
    app = QApplication(['a'])
    GUI = Ventana()
    GUI.showMaximized()
    GUI.setWindowTitle("Dra. Angeles Mtz. Rmz.")
    GUI.show()
    sys.exit(app.exec())