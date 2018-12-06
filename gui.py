import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, \
    QApplication, QInputDialog, QLineEdit, QLabel,\
    QFileDialog
from PyQt5.QtCore import pyqtSlot


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.label = QLabel()
        self.init_gui()
        self.next = None

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Welcome!')
        self.button_new_user()
        self.button_existing_user()
        self.show()

    def button_new_user(self):
        button = QPushButton('Create New User', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(100, 200)
        button.clicked.connect(self.get_text)

    def button_existing_user(self):
        button = QPushButton('Existing User', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(320, 200)
        button.clicked.connect(self.get_text)

    def get_text(self):
        text, ok_pressed = QInputDialog.getText(
            self, "Account Information", "Username:", QLineEdit.Normal, "")
        if ok_pressed and text != '':
            self.create_user(text)
            self.close()
            self.next = App2()

    @pyqtSlot()
    def create_user(self, text):
        print(text)
        # place holder for a post function


class App2(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.label = QLabel()
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Step 1: Upload Images!')
        self.button_upload()
        self.show()

    def button_upload(self):
        button = QPushButton('Upload Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(220, 200)
        button.clicked.connect(self.image_upload_dialog)

    def image_upload_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "",
            "All Files (*)", options=options)
        if file_name:
            print(file_name)
        else:
            print("Warning: Empty")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
