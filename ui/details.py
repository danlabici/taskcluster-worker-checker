from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
import os
from datetime import timedelta
from ui.modules import open_json, Machine, TrayIcon

class MachineDetails(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        file_path = os.path.abspath('ui/details.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Machine Details", "Load Complete.", 1)
        self.close_btn.pressed.connect(self.close)
        self.objects = []
        self.add_lista()

    def add_lista(self):
        self.objects.clear()
        machine_data = open_json("google_dict.json")
        idle_data = open_json("heroku_dict.json")
        for machine, _idle in zip(machine_data, idle_data):
            try:
                ilo = machine_data.get(machine)["ilo"]
            except KeyError:
                ilo = "N/A"
            t = Machine(machine)
            t.insert_data(machine_data.get(machine)["ignore"],
                          machine_data.get(machine)["notes"],
                          machine_data.get(machine)["serial"],
                          machine_data.get(machine)["owner"],
                          machine_data.get(machine)["reason"],
                          ilo)
            self.objects.append(t)

    @pyqtSlot(str)
    def display_info(self, filter):
        for member in self.objects:
            if filter in member.hostname:
                try:
                    ilo = member.ilo
                except KeyError:
                    ilo = "-"
                self.key_line.setText(member.hostname)
                self.idle_line.setText(str(timedelta(seconds=member.idle)))
                self.ilo_line.setText(ilo)
                self.sn_line.setText(member.serial)
                self.owner_line.setText(member.owner)
                self.reason_line.setText(member.reason)
                self.notes_line.setText(member.notes)
                self.ignore_line.setText(member.ignore)