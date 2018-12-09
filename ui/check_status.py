from PyQt5 import QtWidgets, uic, QtCore
import os
from datetime import datetime, timedelta
from ui.messaging_module import TrayIcon
from ui.details import MachineDetails
from ui.modules import GetDataThread, open_json, VmMachine


class CheckStatusWindow(QtWidgets.QFrame):
    filterData = QtCore.pyqtSignal(str)
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        file_path = os.path.abspath('ui/check_status.ui')
        uic.loadUi(file_path, self)
        TrayIcon().messageInfo("Status", "Tray opened", 1)
        self.thread1 = GetDataThread()
        self.thread1.newValue.connect(self.message_board_history)
        self.thread1.finished.connect(self.start_processing_no_lazy)
        self.process_btn.pressed.connect(self.get_all_machines)
        self.thread1.addList.connect(self.add_lista)
        self.lazy_spin.setEnabled(False)
        self.filter_btn.setEnabled(False)
        self.filter_line.setEnabled(False)
        self.filter_combo.setEnabled(False)
        self.ignore_combo.setEnabled(False)
        self.lazy_check.stateChanged.connect(self.change_lazy_input_state)
        self.owner_check.stateChanged.connect(self.change_owner_input_state)
        self.ignore_check.stateChanged.connect(self.change_ignore_input_state)
        self.tableWidget.doubleClicked.connect(self.display_more_info)
        # self.filter_btn.pressed.connect(self.filter_by_field)
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
            t = VmMachine(machine)
            t.insert_data(machine_data.get(machine)["ignore"],
                          machine_data.get(machine)["notes"],
                          machine_data.get(machine)["serial"],
                          machine_data.get(machine)["owner"],
                          machine_data.get(machine)["reason"],
                          idle_data.get(_idle)["idle"],
                          ilo)
            self.objects.append(t)
        self.message_board_history("Machines updated and loaded in memory.")

    def start_processing_no_lazy(self):
        self.tableWidget.setRowCount(0)
        _name_filter = str(self.machine_combo.currentText()).partition("-")[0]
        _lazy_time = self.lazy_spin.value() * 3600
        _owner_name = self.filter_line.displayText()
        _ignore = self.ignore_combo.currentText()
        for member in self.objects:
            if (_name_filter in member.hostname) and (self.ignore_check.isChecked() is False) and (self.lazy_check.isChecked() is False) and (self.owner_check.isChecked() is False):
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_ignore in member.ignore) and self.ignore_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_ignore in member.ignore) and (_lazy_time > member.idle) and self.ignore_check.isChecked() and self.lazy_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_ignore in member.ignore) and (_lazy_time > member.idle) and (_owner_name in member.owner) and self.ignore_check.isChecked() and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_ignore in member.ignore) and (_lazy_time > member.idle) and (_owner_name in member.notes) and self.ignore_check.isChecked() and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_ignore in member.ignore) and (_owner_name in member.owner) and self.ignore_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_ignore in member.ignore) and (_owner_name in member.notes) and self.ignore_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_lazy_time > member.idle) and (_owner_name in member.owner) and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_lazy_time > member.idle) and (_owner_name in member.notes) and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_name_filter in member.hostname) and (_lazy_time > member.idle) and self.lazy_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif _name_filter == "All" and (self.ignore_check.isChecked() is False) and (self.lazy_check.isChecked() is False) and (self.owner_check.isChecked() is False):
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_ignore in member.ignore) and self.ignore_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_ignore in member.ignore) and (_lazy_time > member.idle) and self.ignore_check.isChecked() and self.lazy_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_ignore in member.ignore) and (_lazy_time > member.idle) and (_owner_name in member.owner) and self.ignore_check.isChecked() and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_ignore in member.ignore) and (_lazy_time > member.idle) and (_owner_name in member.notes) and self.ignore_check.isChecked() and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_ignore in member.ignore) and (_owner_name in member.owner) and self.ignore_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_ignore in member.ignore) and (_owner_name in member.notes) and self.ignore_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_lazy_time > member.idle) and (_owner_name in member.owner) and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_lazy_time > member.idle) and (_owner_name in member.notes) and self.lazy_check.isChecked() and self.owner_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif (_lazy_time > member.idle) and self.lazy_check.isChecked():
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            else:
                pass

        self.message_board_history("Showing list of machines based on name filter.")

    def get_all_machines(self):
        option = QtWidgets.QMessageBox.information(None, "Import new data", "Do you want to import new data or work on existing data?\n"
                                                                            "Working on existing data improves app performance!", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if option == QtWidgets.QMessageBox.Yes:
            self.thread1.start(1)
        else:
            self.start_processing_no_lazy()
    
    def list_objects_on_table(self, host, idle, ilo, serial, notes):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['Machine(Hostname)', 'Idle Time', 'Ilo', 'Serial Number', 'Notes'])
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(host.partition(".")[0]))
        self.tableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(timedelta(seconds=idle))))
        self.tableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(ilo))
        self.tableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(serial))
        self.tableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(notes))
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

    def message_board_history(self, text):
        read1 = self.status_browser.toPlainText()
        self.status_browser.setText("[{}]---{} \n {} ".format(datetime.now(), text, read1))

    def change_lazy_input_state(self):
        if self.lazy_check.isChecked():
            self.lazy_spin.setEnabled(True)
        else:
            self.lazy_spin.setEnabled(False)

    def change_ignore_input_state(self):
        if self.ignore_check.isChecked():
            self.ignore_combo.setEnabled(True)
        else:
            self.ignore_combo.setEnabled(False)

    def change_owner_input_state(self):
        if self.owner_check.isChecked():
            self.filter_btn.setEnabled(True)
            self.filter_line.setEnabled(True)
            self.filter_combo.setEnabled(True)
        else:
            self.filter_btn.setEnabled(False)
            self.filter_line.setEnabled(False)
            self.filter_combo.setEnabled(False)

    def display_more_info(self):
        row_id = self.select_row_table()
        dialog1 = MachineDetails()
        self.filterData.connect(dialog1.display_info)
        self.filterData.emit(row_id)
        dialog1.exec()

    def select_row_table(self):
        index = self.tableWidget.selectionModel().selectedRows()[0]
        id_us = self.tableWidget.model().data(index)
        return id_us

    def filter_by_field(self):
        elf.tableWidget.setRowCount(0)
        _name_filter = str(self.machine_combo.currentText()).partition("-")[0]
        _lazy = self.lazy_spin.value() * 3600
        for member in self.objects:
            if (_name_filter in member.hostname) and (_lazy > int(member.idle)):
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
            elif _lazy > int(member.idle):
                self.list_objects_on_table(member.hostname, member.idle, member.ilo, member.serial, member.notes)
        self.message_board_history("Showing list of machines based on name filter "
                                   "and idle time. Limit set to: {}h".format(self.lazy_spin.value()))
