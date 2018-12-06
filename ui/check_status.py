from PyQt5 import QtWidgets, uic, QtCore
import os
from datetime import datetime, timedelta
from ui.messaging_module import TrayIcon
from ui.details import MachineDetails
from ui.modules import GetDataThread, open_json, save_json
from twc_modules.configuration import *


class CheckStatusWindow(QtWidgets.QFrame):
    filterData = QtCore.pyqtSignal(str)
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        file_path = os.path.abspath('ui/check_status.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Status", "Tray opened", 1)
        self.thread1 = GetDataThread()
        self.thread1.newValue.connect(self.message_board_history)
        self.thread1.finished.connect(self.start_processing)
        self.process_btn.pressed.connect(self.get_all_machines)
        self.lazy_spin.setEnabled(False)
        self.lazy_check.stateChanged.connect(self.change_lazy_input_state)
        self.tableWidget.doubleClicked.connect(self.display_more_info)
        self.filter_btn.pressed.connect(self.filter_by_field)

    def select_row_table(self):
        index = self.tableWidget.selectionModel().selectedRows()[0]
        id_us = self.tableWidget.model().data(index)
        return id_us

    def display_more_info(self):
        row_id = self.select_row_table()
        dialog1 = MachineDetails()
        self.filterData.connect(dialog1.display_info)
        self.filterData.emit(row_id)
        dialog1.exec()

    def change_lazy_input_state(self):
        if self.lazy_check.isChecked():
            self.lazy_spin.setEnabled(True)
        else:
            self.lazy_spin.setEnabled(False)

    def message_board_history(self, text):
        read1 = self.status_browser.toPlainText()
        # self.status_browser.setText(text + " \n" + read1 + " ")
        self.status_browser.setText("[{}]---{} \n {} ".format(datetime.now(), text, read1))

    def start_processing(self):
        if self.lazy_check.isChecked():
            self.output_problem_machines(str(self.machine_combo.currentText()).partition("-")[0], (self.lazy_spin.value() * 3600))
            self.message_board_history("Filtering list using value: {}h".format(self.lazy_spin.value()))
        else:
            self.output_problem_machines(str(self.machine_combo.currentText()).partition("-")[0], 0)

    def get_all_machines(self):
        option = QtWidgets.QMessageBox.information(None, "Import new data", "Do you want to import new data or work on existing data?\n"
                                                                            "Working on existing data improves app performance!", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if option == QtWidgets.QMessageBox.Yes:
            self.thread1.start(1)
        else:
            self.start_processing()

    def filter_by_field(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['Machine(Hostname)', 'Idle Time', 'Ilo', 'Serial Number', 'Notes'])
        machine_data = open_json("google_dict.json")
        idle_data = open_json("heroku_dict.json")
        if self.filter_combo.currentText() == "Owner":
            compare = "owner"
        elif self.filter_combo.currentText() == "Notes":
            compare = "notes"
        else:
            compare = None
        for machine, idle in zip(machine_data, idle_data):
            if (self.filter_line.text() in machine_data.get(machine)[compare]):
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
                try:
                    ilo = machine_data.get(machine)["ilo"]
                except KeyError:
                    ilo = "-"
                list_row = [hostname, idle, ilo, serial, notes]
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(list_row[0]))
                self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(list_row[1]))
                self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(list_row[2]))
                self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(list_row[3]))
                self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(list_row[4]))

    def output_problem_machines(self, workerVal, lazyH):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['Machine(Hostname)', 'Idle Time', 'Ilo', 'Serial Number', 'Notes'])
        machine_data = open_json("google_dict.json")
        idle_data = open_json("heroku_dict.json")
        for machine, idle in zip(machine_data, idle_data):
            if (workerVal in machine) and (lazyH < idle_data.get(idle)["idle"]):
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
                try:
                    ilo = machine_data.get(machine)["ilo"]
                except KeyError:
                    ilo = "-"
                list_row = [hostname, idle, ilo, serial, notes]
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(list_row[0]))
                self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(list_row[1]))
                self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(list_row[2]))
                self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(list_row[3]))
                self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(list_row[4]))
            elif (workerVal == "All") and (lazyH < idle_data.get(idle)["idle"]):
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
                try:
                    ilo = machine_data.get(machine)["ilo"]
                except KeyError:
                    ilo = "-"
                list_row = [hostname, idle, ilo, serial, notes]
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(list_row[0]))
                self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(list_row[1]))
                self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(list_row[2]))
                self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(list_row[3]))
                self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(list_row[4]))
            else:
                pass
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)