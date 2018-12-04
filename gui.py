import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, \
    QApplication, QInputDialog, QLineEdit
from PyQt5.QtCore import pyqtSlot


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Processor'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Welcome!')
        # first button for new users
        self.button_new_user()
        # second button for existing users
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

    @pyqtSlot()
    def create_user(self, text):
        print(text)
        # place holder for a post function


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
