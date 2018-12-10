from PyQt5 import QtWidgets, uic, QtCore
from ui.check_status import CheckStatusWindow
import os
import sys
from ui.messaging_module import TrayIcon


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        file_path = os.path.abspath('ui/main.ui')
        uic.loadUi(file_path, self)
        self.move(QtWidgets.QApplication.desktop().screen().rect().center() - self.rect().center())
        self.menubar.setNativeMenuBar(False)
        # self.showMaximized()
        self.actionCheck_Machine_Status.triggered.connect(self.show_check_status_widget)
        self.actionExit.triggered.connect(self.close)
        self.actionLight.triggered.connect(self.theme_selector_light)
        self.actionDark.triggered.connect(self.theme_selector_dark)
        self.actionVS_Dark.triggered.connect(self.theme_selector_vs)

    def show_check_status_widget(self):
        self.qdock = CheckStatusWindow()
        self.anim = QtCore.QPropertyAnimation(self.qdock, b"geometry")
        self.anim.setDuration(200)
        self.anim.setStartValue(QtCore.QRect(0, 0, 0, 0))
        self.anim.setEndValue(QtCore.QRect(self.qdock.geometry()))
        self.mdiArea.addSubWindow(self.qdock)
        self.anim.start()
        self.qdock.showMaximized()

    def theme_selector_light(self):
        self.actionDark.setChecked(False)
        self.actionVS_Dark.setChecked(False)

    def theme_selector_dark(self):
        self.actionLight.setChecked(False)
        self.actionVS_Dark.setChecked(False)

    def theme_selector_vs(self):
        self.actionDark.setChecked(False)
        self.actionLight.setChecked(False)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec_())

