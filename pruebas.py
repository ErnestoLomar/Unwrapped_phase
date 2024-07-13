import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImagePickerWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        self.label = QLabel("Drag and drop an image here or click the button to choose an image.")
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Choose Image")
        self.button.clicked.connect(self.open_image_dialog)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.image_label)

        self.setLayout(layout)

    def open_image_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_path:
            self.display_image(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.display_image(file_path)

    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Picker")
        self.setGeometry(100, 100, 800, 600)

        self.image_picker = ImagePickerWidget()
        self.setCentralWidget(self.image_picker)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())