from PyQt5 import QtWidgets, uic, QtCore
import os
from ui.messaging_module import TrayIcon
from ui.modules import BackendProperties, UiProperties, Settings

class SettingsWindow(QtWidgets.QDialog):
    filterData = QtCore.pyqtSignal(str)
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        file_path = os.path.abspath('ui/settings_ui.ui')
        uic.loadUi(file_path, self)
        self.save_btn.pressed.connect(self.save_all)
        self.discard_btn.pressed.connect(self.close)
        self.work_btn.pressed.connect(self.get_wdir_folder)
        self.google_btn.pressed.connect(self.get_google_creds_file)
        self.get_working_dir_json()
        self.get_google_creds_json()
        self.get_notification_display()

    def get_wdir_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Workdir Folder', '/path/to/default/*')
        self.workingDir_txtField.setText(folder_name)

    def get_google_creds_file(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Google Creds File', '/path/to/default/*')
        self.credentials_txtField.setText(file_name[0])

    def save_working_dir(self):
        wdir_path = self.workingDir_txtField.displayText()
        t = BackendProperties(name='WDir', value=wdir_path, active="Yes")
        t.update_property()

    def save_google_creds(self):
        creds_path = self.credentials_txtField.displayText()
        t = BackendProperties(name='GCreds', value=creds_path, active="Yes")
        t.update_property()

    def save_notification_display(self):
        status = self.showNotification_chkBox.isChecked()
        t = UiProperties(name='Notifier', value=status, active="Yes")
        t.update_property()

    def get_working_dir_json(self):
        t = Settings()
        data = t.get_property('backend', 'WDir')
        self.workingDir_txtField.setText(data['value'])

    def get_google_creds_json(self):
        t = Settings()
        data = t.get_property('backend', 'GCreds')
        self.credentials_txtField.setText(data['value'])

    def get_notification_display(self):
        t = Settings()
        data = t.get_property('ui_properties', 'Notifier')
        if data['value'] is True:
            self.showNotification_chkBox.setChecked(True)
        else:
            self.showNotification_chkBox.setChecked(False)

    def save_all(self):
        self.save_google_creds()
        self.save_notification_display()
        self.save_working_dir()
        TrayIcon().messageInfo("Settings", "Settings saved.", 1)
        self.close()