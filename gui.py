import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction
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
        button = QPushButton('Register', self)
        button.setToolTip('This is an example button')
        button.move(280, 300)
        button.clicked.connect(self.create_user)

        self.show()

    @pyqtSlot()
    def create_user(self):
        print('Register to database')
        # place holder for a post function


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
