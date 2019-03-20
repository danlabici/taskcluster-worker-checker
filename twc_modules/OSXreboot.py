import subprocess
import os
import sys
from selenium import webdriver
import time
from selenium.webdriver.support.color import Color


class OSXreboot():
    def __init__(self, worker):
        self.w = worker
        self.link = "https://tools.taskcluster.net/provisioners/releng-hardware/worker-types/gecko-t-osx-1010/workers/"

    def create_link(self):
        if int(self.w[-3:]) < 237:
            dc = "mdc2"
        else:
            dc = "mdc1"
        self.link += dc + "/" + self.w
        return self.link

    def launch_browser(self):
        if sys.platform == 'win32':
            os.startfile(self.w)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', self.w])
        else:
            try:
                subprocess.Popen(['xdg-open', self.w])
            except OSError:
                print('Please open a browser on: ' + self.w)

    def click_reboot(self):
        driver = webdriver.Firefox(executable_path='./geckodriver')
        driver.get(self.w)
        time.sleep(5)
        last_task = driver.find_element_by_css_selector\
            ('div.table-responsive:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > '
             'tr:nth-child(1) > td:nth-child(1) > span:nth-child(1)')\
            .value_of_css_property('background-color')
        last_task_color = Color.from_string(last_task).hex
        if last_task_color == '#f0ad4e':
            reboot = driver.find_element_by_css_selector('button._1_IlPzDfcdYSoXO4c8oXdA:nth-child(3)')
            reboot.click()
            time.sleep(5)
            driver.close()
        else:
            time.sleep(5)
            driver.close()

    def close_firefox(self):
        pass
