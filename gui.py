import sys
import os
from PyQt5.QtWidgets import QMainWindow, QPushButton,\
    QApplication, QInputDialog, QLineEdit, QLabel, \
    QFileDialog, QTextEdit, QSpinBox, QVBoxLayout,\
    QComboBox, QGroupBox, QFormLayout, QMessageBox
from PyQt5.QtCore import pyqtSlot, QByteArray, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
import client
from final import image_parser


global_user_email = ""
global_image_name = []
global_selected_name = ""
global_process_type = ""
global_image_dict = {}


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'BME 590 Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.init_gui()
        self.next = None

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(204, 204, 255))
        self.setPalette(p)
        self.statusBar().showMessage('Welcome!')
        self.display_text()
        self.button_new_user()
        self.button_existing_user()
        self.show()

    def display_text(self):
        label = QLabel('Author: Sarah Putney, '
                       'Erica Skerrett, Roujia Wang', self)
        label.setAlignment(Qt.AlignCenter)
        label.move(150, 300)
        label.setMinimumSize(350, 40)

    def button_new_user(self):
        button = QPushButton('Create New User', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(100, 200)
        button.clicked.connect(self.create_user)

    def button_existing_user(self):
        button = QPushButton('Existing User', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(320, 200)
        button.clicked.connect(self.get_user)

    @pyqtSlot()
    def create_user(self):
        user_email, ok_pressed = QInputDialog.getText(
            self, "Account Information", "User Email:", QLineEdit.Normal, "")
        if ok_pressed and user_email != '':
            global global_user_email
            global_user_email = user_email
            client.post_create_user(global_user_email)
            self.next = App2()
            self.close()

    @pyqtSlot()
    def get_user(self):
        user_email, ok_pressed = QInputDialog.getText(
            self, "Account Information", "User Email:", QLineEdit.Normal, "")
        if ok_pressed and user_email != '':
            global global_user_email
            global_user_email = user_email
            email = client.get_returning_user(global_user_email)
            if email.get("error_message") == 'None':
                self.next = App2()
                self.close()
            else:
                print(email)
                button_reply = QMessageBox.question(
                    self, 'Error Message', email.get("error_message"),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if button_reply == QMessageBox.Yes:
                    self.next = App()
                    self.close()
                else:
                    self.close()

    def close_event(self, event):
        reply = QMessageBox.question(
            self, 'Message', "Are you sure you want to quit the processor?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class App2(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.label = QLabel()
        self.next = None
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(204, 204, 255))
        self.setPalette(p)
        self.statusBar().showMessage('Step 1: Choose Images!')
        self.button_choose()
        self.show()

    def button_choose(self):
        button = QPushButton('Choose Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(220, 200)
        button.clicked.connect(self.image_dialog)

    def image_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "",
            "All Files (*)", options=options)
        if file_name:
            global global_image_name
            global global_user_email
            global global_image_dict
            global_image_name = file_name
            global_image_dict = image_parser(global_image_name)
            client.post_uploaded_images(global_user_email, global_image_dict)
            self.close()
            self.next = App3()
        else:
            button_reply = QMessageBox.question(
                self, 'Error Message', 'Please Choose Image(s) to Proceed',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if button_reply == QMessageBox.Yes:
                self.next = App2()
                self.close()
            else:
                self.close()

    def close_event(self, event):
        reply = QMessageBox.question(
            self, 'Message', "Are you sure you want to quit the processor?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class App3(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.next = None
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(204, 204, 255))
        self.setPalette(p)
        self.statusBar().showMessage('Step 2: Upload Image(s)!')
        self.display_text()
        self.scroll_down_menu()  # user define unzipped images
        self.button_upload()
        self.show()

    def display_text(self):
        label = QLabel('Please Select From Following Options', self)
        label.setAlignment(Qt.AlignCenter)
        label.move(180, 100)
        label.setMinimumSize(250, 40)

    def scroll_down_menu(self):
        global global_image_dict
        global global_user_email
        label = QLabel("List of Images", self)
        combo = QComboBox(self)
        for i in global_image_name:
            combo.addItem(i)
        combo.move(250, 150)
        label.setGeometry(150, 20, 640, 280)
        combo.activated[str].connect(self.on_activated)

    def on_activated(self, name):
        global global_user_email
        global global_selected_name
        global_selected_name = name
        print(global_selected_name)

    def button_upload(self):
        button = QPushButton('Upload Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(220, 300)
        button.clicked.connect(self.next_window)

    def next_window(self):
        self.close()
        self.next = App4()

    def close_event(self, event):
        reply = QMessageBox.question(
            self, 'Message', "Are you sure you want to quit the processor?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class App4(QMainWindow):

    def __init__(self):
        super().__init__()
        global global_selected_name
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.next = None
        self.path, self.filename = os.path.split(global_selected_name)
        self.init_gui()
        print(global_selected_name)

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(204, 204, 255))
        self.setPalette(p)
        self.statusBar().showMessage('Step 3: Process Image(s)!')
        self.display_image()
        self.button1()
        self.button2()
        self.button3()
        self.button4()
        self.show()

    def display_image(self):
        label = QLabel(self)
        pixmap = QPixmap(os.path.join(self.path, self.filename))
        pixmap2 = pixmap.scaledToWidth(250)
        label.setPixmap(pixmap2)
        label.setGeometry(50, 20, 640, 280)

    def button1(self):
        button = QPushButton('Histogram Equalization', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(360, 60)
        button.clicked.connect(self.histogram)

    def button2(self):
        button = QPushButton('Contrast Stretching', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(360, 120)
        button.clicked.connect(self.contrast)

    def button3(self):
        button = QPushButton('Log Compression', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(360, 180)
        button.clicked.connect(self.compression)

    def button4(self):
        button = QPushButton('Reverse Video', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(360, 240)
        button.clicked.connect(self.reverse)

    @pyqtSlot()
    def histogram(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        image_strip = global_selected_namegi.split('/')[-1]
        image_name = image_strip.split('.')[0]
        global_process_type = "HistogramEqualization"
        print(global_user_email)
        print(image_name)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    image_name, global_process_type)
        self.close()
        self.next = App5()

    @pyqtSlot()
    def contrast(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "ContrastStretching"
        image_strip = global_selected_name.split('/')[-1]
        image_name = image_strip.split('.')[0]
        print(global_user_email)
        print(image_name)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    image_name, global_process_type)
        self.close()
        self.next = App5()

    @pyqtSlot()
    def compression(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "LogCompression"
        image_strip = global_selected_name.split('/')[-1]
        image_name = image_strip.split('.')[0]
        print(global_user_email)
        print(image_name)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    image_name, global_process_type)
        self.close()
        self.next = App5()

    @pyqtSlot()
    def reverse(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "ReverseVideo"
        image_strip = global_selected_name.split('/')[-1]
        image_name = image_strip.split('.')[0]
        print(global_user_email)
        print(image_name)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    image_name, global_process_type)
        self.close()
        self.next = App5()

    def close_event(self, event):
        reply = QMessageBox.question(
            self, 'Message', "Are you sure you want to quit the processor?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class App5(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.next = None
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(204, 204, 255))
        self.setPalette(p)
        self.statusBar().showMessage('Step 4: Download Processed Image(s)!')
        self.display_images()
        self.display_images_info()
        self.button_download()
        self.upload_new_images()
        self.show()

    def display_images(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        image_strip = global_process_type.split('/')[-1]
        image_name = image_strip.split('.')[0]
        processed_images = client.get_processed_image(
            global_user_email, image_name, global_process_type)
        label = QLabel(self)
        data = QByteArray.fromBase64(
            processed_images.get(global_selected_name))
        pixmap = QPixmap()
        if pixmap.loadFromData(data, "PNG"):
            self.label.setPixmap(pixmap)
            pixmap2 = pixmap.scaledToWidth(400)
            label.setPixmap(pixmap2)
            label.setGeometry(120, 20, 640, 280)

    def display_images_info(self):
        global global_user_email
        info = client.get_user_metrics(global_user_email)
        label = QLabel(info, self)  # need to elaborate more
        label.move(180, 250)

    def button_download(self):
        button = QPushButton('Download Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(220, 300)
        button.clicked.connect(self.download)

    def upload_new_images(self):
        button = QPushButton('Upload New Image(s)', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(220, 330)
        button.clicked.connect(self.new_upload)

    @pyqtSlot()
    def download(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()",
            "", "JPEG Files (*.jpg);; JPEG Files(*jpeg);; "
                "TIFF Files(*.tif);; TIFF Files(*.tiff);; "
                "PNG Files(*.png)", options=options)
        if fileName:
            print(fileName)
            # place holder for saving file command

    @pyqtSlot()
    def new_upload(self):
        print('Upload New Images')
        self.close()
        self.next = App2()

    def close_event(self, event):
        reply = QMessageBox.question(
            self, 'Message', "Are you sure you want to quit the processor?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
