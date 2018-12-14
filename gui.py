import sys
import os
from PyQt5.QtWidgets import QMainWindow, QPushButton,\
    QApplication, QInputDialog, QLineEdit, QLabel, \
    QFileDialog, QComboBox, QAction, QMessageBox
from PyQt5.QtCore import pyqtSlot, QByteArray, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
import client
from final import image_parser, make_hist, decode
import skimage
from skimage.viewer import ImageViewer
from PIL import Image
from matplotlib import pyplot as plt
import io


global_user_email = ""
global_image_name = []
global_selected_name = ""
global_process_type = ""
global_image_dict = {}
global_process_image = ""


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'BME 590 Image Processor'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 480
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
        label.move(160, 300)
        label.setMinimumSize(400, 40)

    def button_new_user(self):
        button = QPushButton('Create New User', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(150, 200)
        button.clicked.connect(self.create_user)

    def button_existing_user(self):
        button = QPushButton('Existing User', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(360, 200)
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


class App2(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 480
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
        self.display_image()
        self.button_choose()
        self.show()

    def display_image(self):
        label = QLabel(self)
        pixmap = QPixmap('christmas.jpg')
        pixmap2 = pixmap.scaledToWidth(400)
        label.setPixmap(pixmap2)
        label.setGeometry(160, 50, 640, 280)

    def button_choose(self):
        button = QPushButton('Choose Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(250, 320)
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


class App3(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 480
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
        self.scroll_down_menu()
        self.button_upload()
        self.show()

    def display_text(self):
        label = QLabel('Please Select From Following Options'
                       ' by Clicking the Image Name:', self)
        label.setAlignment(Qt.AlignCenter)
        label.move(20, 150)
        label.setMinimumSize(640, 40)

    def scroll_down_menu(self):
        global global_user_email
        global global_image_name
        uploaded_images = global_image_name
        combo = QComboBox(self)
        for i in uploaded_images:
            combo.addItem(i)
        combo.move(120, 200)
        combo.setMinimumSize(440, 40)
        combo.activated[str].connect(self.on_activated)

    def on_activated(self, name):
        global global_image_name
        global global_selected_name
        for i in global_image_name:
            if name in i:
                global_selected_name = name
        print(global_selected_name)

    def button_upload(self):
        button = QPushButton('Upload Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(250, 320)
        button.clicked.connect(self.next_window)

    def next_window(self):
        global global_selected_name
        if global_selected_name == '':
            button_reply = QMessageBox.question(
                self, 'Error Message', 'You must click on the image to'
                                       ' select it!',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if button_reply == QMessageBox.Yes:
                self.next = App3()
                self.close()
            else:
                self.close()
        else:
            self.close()
            self.next = App4()


class App4(QMainWindow):

    def __init__(self):
        super().__init__()
        global global_selected_name
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 480
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
        pixmap2 = pixmap.scaledToWidth(350)
        label.setPixmap(pixmap2)
        label.setGeometry(50, 20, 640, 350)

    def button1(self):
        button = QPushButton('Histogram Equalization', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(400, 120)
        button.clicked.connect(self.histogram)

    def button2(self):
        button = QPushButton('Contrast Stretching', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(400, 170)
        button.clicked.connect(self.contrast)

    def button3(self):
        button = QPushButton('Log Compression', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(400, 220)
        button.clicked.connect(self.compression)

    def button4(self):
        button = QPushButton('Reverse Video', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(400, 270)
        button.clicked.connect(self.reverse)

    @pyqtSlot()
    def histogram(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "HistogramEqualization"
        print(global_user_email)
        print(global_selected_name)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    global_selected_name, global_process_type)
        print('posted')
        print(global_selected_name)
        self.close()
        self.next = App5()

    @pyqtSlot()
    def contrast(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "ContrastStretching"
        print(global_user_email)
        print(global_selected_name)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    global_selected_name, global_process_type)
        self.close()
        self.next = App5()

    @pyqtSlot()
    def compression(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "LogCompression"
        print(global_user_email)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    global_selected_name, global_process_type)
        self.close()
        self.next = App5()

    @pyqtSlot()
    def reverse(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global_process_type = "ReverseVideo"
        print(global_user_email)
        print(global_process_type)
        client.post_processed_image(global_user_email,
                                    global_selected_name, global_process_type)
        self.close()
        self.next = App5()


class App5(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 480
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
        self.button_histogram()
        self.show()

    def display_images(self):
        global global_user_email
        global global_process_type
        global global_selected_name
        global global_process_image
        image_strip = global_selected_name.split('/')[-1]
        image_name = image_strip.split('.')[0]
        processed_images = client.get_processed_image(
            global_user_email, image_name, global_process_type)
        print(processed_images.keys())
        label = QLabel(self)
        s = processed_images[image_name]
        global_process_image = s
        data = QByteArray.fromBase64(s.encode())
        image_type = image_strip.split('.')[1]
        upload_sizes = client.get_upload_sizes(global_user_email)
        upload_size = upload_sizes[image_name]
        size_string = "Upload Size: " + str(upload_size)
        upload_times = client.get_upload_time(global_user_email)
        upload_time = upload_times[image_name]
        print(upload_time)
        time_string = "Upload Time: " + upload_time
        pixmap = QPixmap()
        if pixmap.loadFromData(data, image_type):
            pixmap2 = pixmap.scaledToWidth(250)
            label.setPixmap(pixmap2)
            label.setGeometry(380, 20, 640, 320)
        label1 = QLabel(size_string, self)
        label1.move(350, 30)
        label1.setMinimumSize(200, 40)
        label2 = QLabel(time_string, self)
        label2.move(350, 50)
        label2.setMinimumSize(300, 40)

    def display_images_info(self):
        global global_user_email
        info = client.get_user_metrics(global_user_email)
        user_metrics = list(info.keys())
        user_metrics_info = list(info.values())
        for i, n in enumerate(user_metrics):
            label1 = QLabel(str(n), self)
            label1.move(30, 50 + i * 20)
            label1.setMinimumSize(220, 40)
        for i, n in enumerate(user_metrics_info):
            label2 = QLabel(str(n), self)
            label2.move(260, 50 + i * 20)
            label2.setMinimumSize(200, 40)

    def button_download(self):
        button = QPushButton('Download Image', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(250, 330)
        button.clicked.connect(self.download)

    def upload_new_images(self):
        button = QPushButton('Upload New Image(s)', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(250, 360)
        button.clicked.connect(self.new_upload)

    def button_histogram(self):
        button = QPushButton('View Histogram(s)', self)
        button.setMinimumSize(200, 40)
        button.setToolTip('This is an example button')
        button.move(250, 300)
        button.clicked.connect(self.histogram_window)

    @pyqtSlot()
    def download(self):
        global global_process_image
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, options = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()",
            "", "JPEG Files(*.jpeg);; "
                "TIFF Files(*.tiff);; "
                "PNG Files(*.png)", options=options)
        if file_name:
            options = options.split('.')[-1]
            options = options.strip(')')
            img_buf = decode(global_process_image)
            img_array = skimage.io.imread(img_buf)
            plt.imsave(file_name + '.' + options,
                       img_array)

    @pyqtSlot()
    def new_upload(self):
        print('Upload New Images')
        self.close()
        self.next = App2()

    @pyqtSlot()
    def histogram_window(self):
        global global_selected_name
        global global_image_dict
        image_strip = global_selected_name.split('/')[-1]
        image_key = image_strip.split('.')[0]
        image_data = global_image_dict[image_key]
        make_hist(image_data)
        self.close()
        self.next = App6()


class App6(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 480
        self.next = None
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(204, 204, 255))
        self.setPalette(p)
        self.statusBar().showMessage('Step 5: View Histogram(s)!')
        self.upload_new_images()
        self.histogram_original()
        self.histogram_processed()
        self.show()

    def upload_new_images(self):
        button = QPushButton('Upload New Image(s)', self)
        button.setMinimumSize(200, 30)
        button.setToolTip('This is an example button')
        button.move(220, 320)
        button.clicked.connect(self.new_upload)

    def histogram_original(self):
        label_text = QLabel('Original Image', self)
        label_text.move(100, 50)
        label_text.setMinimumSize(150, 40)
        label = QLabel('Original Image', self)
        pixmap = QPixmap('hist.jpeg')
        pixmap2 = pixmap.scaledToWidth(230)
        label.setPixmap(pixmap2)
        label.setGeometry(80, 80, 640, 200)

    def histogram_processed(self):
        global global_process_image
        vals = make_hist(global_process_image)
        label_text = QLabel('Processed Image', self)
        label_text.move(350, 50)
        label_text.setMinimumSize(150, 40)
        label = QLabel('Processed Image', self)
        pixmap = QPixmap('hist.jpeg')
        pixmap2 = pixmap.scaledToWidth(230)
        label.setPixmap(pixmap2)
        label.setGeometry(320, 80, 640, 200)

    @pyqtSlot()
    def new_upload(self):
        self.close()
        self.next = App2()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
