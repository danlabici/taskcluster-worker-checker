from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
import os
from datetime import timedelta
from ui.messaging_module import TrayIcon
from ui.modules import open_json

class MachineDetails(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        file_path = os.path.abspath('ui/details.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Machine Details", "Load Complete.", 1)
        self.close_btn.pressed.connect(self.close)

    @pyqtSlot(str)
    def display_info(self, filter):
        machine_data = open_json("google_dict.json")
        idle_data = open_json("heroku_dict.json")
        for machine, idle in zip(machine_data, idle_data):
            if filter in machine:
                hostname = machine
                ignore = machine_data.get(machine)["ignore"]
                notes = machine_data.get(machine)["notes"]
                serial = machine_data.get(machine)["serial"]
                owner = machine_data.get(machine)["owner"]
                reason = machine_data.get(machine)["reason"]
                idle = str(timedelta(seconds=idle_data.get(idle)["idle"]))
                try:
                    ilo = machine_data.get(machine)["ilo"]
                except KeyError:
                    ilo = "-"
                self.key_line.setText(hostname)
                self.idle_line.setText(idle)
                self.ilo_line.setText(ilo)
                self.sn_line.setText(serial)
                self.owner_line.setText(owner)
                self.reason_line.setText(reason)
                self.notes_line.setText(notes)
                self.ignore_line.setText(ignore)
