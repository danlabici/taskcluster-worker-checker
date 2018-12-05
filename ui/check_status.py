from PyQt5 import QtWidgets, uic
import os
from datetime import datetime, timedelta
from ui.messaging_module import TrayIcon
from ui.modules import get_heroku_last_seen, get_google_spreadsheet_data, add_idle_to_google_dict, open_json, save_json
from twc_modules.configuration import *

class CheckStatusWindow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        file_path = os.path.abspath('ui/check_status.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Status", "Tray opened", 1)
        self.all_btn.pressed.connect(self.all_workers)

    def all_workers(self):
        self.get_all_machines()
        self.output_problem_machines("t-w1064-ms")

    def get_all_machines(self):
        get_heroku_last_seen()
        get_google_spreadsheet_data()
        add_idle_to_google_dict()

    def output_problem_machines(self, workerVal):
        # start = datetime.now()
        self.tableWidget.setColumnCount(5)
        lazy_time = LAZY
        machine_data = open_json("google_dict.json")
        for machine in machine_data:
            hostname = machine
            ignore = machine_data.get(machine)["ignore"]
            notes = machine_data.get(machine)["notes"]
            serial = machine_data.get(machine)["serial"]
            owner = machine_data.get(machine)["owner"]
            reason = machine_data.get(machine)["reason"]
            try:
                idle = timedelta(seconds=machine_data.get(machine)["idle"])
                ilo = machine_data.get(machine)["ilo"]
            except KeyError:
                ilo = "-"
                idle = "-"

            if workerVal in str(machine):
                list_row = [hostname, idle, ilo, serial, notes]
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(list_row[0]))
                self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(list_row[1]))
                self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(list_row[2]))
                self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(list_row[3]))
                self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(list_row[4]))