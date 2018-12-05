from PyQt5 import QtWidgets, uic
import os


class CheckStatusWindow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        file_path = os.path.abspath('ui/check_status.ui')
        uic.loadUi(file_path, self)


