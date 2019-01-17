from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
import os
from datetime import timedelta
from ui.modules import open_json, Machine, TrayIcon

class MachineDetails(QtWidgets.QDialog):
    def __init__(self,hostname, idle, ilo, serial, notes, owner, reason, ignore):
        QtWidgets.QDialog.__init__(self)
        file_path = os.path.abspath('ui/details.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Machine Details", "Load Complete.", 1)
        self.close_btn.pressed.connect(self.close)
        self.key_line.setText(hostname)
        self.idle_line.setText(str(timedelta(seconds=idle)))
        self.ilo_line.setText(ilo)
        self.sn_line.setText(serial)
        self.owner_line.setText(owner)
        self.reason_line.setText(reason)
        self.notes_line.setText(notes)
        self.ignore_line.setText(ignore)
