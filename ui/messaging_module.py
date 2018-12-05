from PyQt5 import QtWidgets, QtGui
import sys


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self):
        QtWidgets.QSystemTrayIcon.__init__(self)
        self.tray = QtWidgets.QSystemTrayIcon()
        icon = QtGui.QIcon("DevOps-Gear.png")
        self.tray.setIcon(icon)
        menu = QtWidgets.QMenu()
        exit_action = menu.addAction("Exit")
        settings_action = menu.addAction("Settings")
        self.tray.setContextMenu(menu)
        exit_action.triggered.connect(sys.exit)
        # settings_action.triggered.connect(self.run_settings)
        self.tray.show()

    def messageInfo(self, title, line, option):
        """System tray messageInfo system showing Informative icon and Informative level"""
        if option == 1:
            self.tray.showMessage(title, line, QtWidgets.QSystemTrayIcon.Information)
        if option == 0:
            QtWidgets.QMessageBox.information(None, title, line, QtWidgets.QMessageBox.Yes)

    def messageWarning(self, title, line, option):
        """System tray messageInfo system showing Warning icon and Warning level"""
        if option == 1:
            self.tray.showMessage(title, line, QtWidgets.QSystemTrayIcon.Warning)
        if option == 0:
            QtWidgets.QMessageBox.warning(None, title, line, QtWidgets.QMessageBox.Yes)

    def messageCritical(self, title, line, option):
        """System tray messageInfo system showing Critical icon and Critical level"""
        if option == 1:
            self.tray.showMessage(title, line, QtWidgets.QSystemTrayIcon.Critical)
        if option == 0:
            QtWidgets.QMessageBox.critical(None, title, line, QtWidgets.QMessageBox.Yes)
