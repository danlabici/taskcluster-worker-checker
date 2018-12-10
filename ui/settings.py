from PyQt5 import QtWidgets, uic, QtCore
import os
from ui.messaging_module import TrayIcon

class SettingsWindow(QtWidgets.QDialog):
    filterData = QtCore.pyqtSignal(str)
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        file_path = os.path.abspath('ui/settings_ui.ui')
        uic.loadUi(file_path, self)