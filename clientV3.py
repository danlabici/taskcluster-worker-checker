from PyQt5 import QtWidgets, uic
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
        self.actionCheck_Machine_Status.triggered.connect(self.show_check_status_widget)

    def show_check_status_widget(self):
        self.qdock = CheckStatusWindow()
        self.mdiArea.addSubWindow(self.qdock)
        self.qdock.showMaximized()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec_())

