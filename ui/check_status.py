from PyQt5 import QtWidgets, uic
import os
from datetime import datetime, timedelta
from ui.messaging_module import TrayIcon
from ui.modules import get_heroku_last_seen, get_google_spreadsheet_data, add_idle_to_google_dict, open_json, save_json, remove_fqdn_from_machine_name
from twc_modules.configuration import *

class CheckStatusWindow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        file_path = os.path.abspath('ui/check_status.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Status", "Tray opened", 1)
        self.all_btn.pressed.connect(self.all_workers)
        self.win_btn.pressed.connect(self.windows_workers)
        self.linux_btn.pressed.connect(self.linux_workers)
        self.mac_btn.pressed.connect(self.mac_workers)
        self.lazy_spin.setEnabled(False)
        self.lazy_check.stateChanged.connect(self.change_lazy_input_state)

    def change_lazy_input_state(self):
        if self.lazy_check.isChecked():
            self.lazy_spin.setEnabled(True)
        else:
            self.lazy_spin.setEnabled(False)

    def message_board_history(self, text):
        read1 = self.status_browser.toPlainText()
        self.status_browser.setText(text + " \n" + read1 + " ")

    def all_workers(self):
        self.get_all_machines()
        self.tableWidget.setRowCount(0)
        self.output_problem_machines("All")

    def windows_workers(self):
        self.get_all_machines()
        self.tableWidget.setRowCount(0)
        self.output_problem_machines("w1064")

    def linux_workers(self):
        self.get_all_machines()
        self.tableWidget.setRowCount(0)
        self.output_problem_machines("linux64")

    def mac_workers(self):
        self.get_all_machines()
        self.tableWidget.setRowCount(0)
        self.output_problem_machines("yosemite")

    def get_all_machines(self):
        option = QtWidgets.QMessageBox.information(None, "Import new data", "Do you want to import new data or work on existing data?\n"
                                                                            "Working on existing data improves app performance!", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if option == QtWidgets.QMessageBox.Yes:
            get_heroku_last_seen()
            self.message_board_history("Getting Heroku data...")
            get_google_spreadsheet_data()
            self.message_board_history("Getting Google spreadsheet data...")
            add_idle_to_google_dict()
            self.message_board_history("Adding 'idle' to google dict data...")
        else:
            pass

    def output_problem_machines(self, workerVal):
        self.tableWidget.setColumnCount(5)
        lazy_time = LAZY
        machine_data = open_json("google_dict.json")
        idle_data = open_json("heroku_dict.json")
        for machine, idle in zip(machine_data, idle_data):
            if self.details_check.isChecked():
                hostname = machine
            else:
                hostname = machine.partition(".")[0]
            ignore = machine_data.get(machine)["ignore"]
            notes = machine_data.get(machine)["notes"]
            serial = machine_data.get(machine)["serial"]
            owner = machine_data.get(machine)["owner"]
            reason = machine_data.get(machine)["reason"]
            idle = str(timedelta(seconds=idle_data.get(idle)["idle"]))
            # idle = 0
            try:
                ilo = machine_data.get(machine)["ilo"]
            except KeyError:
                ilo = "-"

            if workerVal in machine:
                list_row = [hostname, idle, ilo, serial, notes]
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(list_row[0]))
                self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(list_row[1]))
                self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(list_row[2]))
                self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(list_row[3]))
                self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(list_row[4]))
            elif workerVal not in machine:
                list_row = [hostname, idle, ilo, serial, notes]
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(list_row[0]))
                self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(list_row[1]))
                self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(list_row[2]))
                self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(list_row[3]))
                self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(list_row[4]))