import json
import uuid
import base64
import binascii
import os
import win32api
import pyautogui


class Cryptograph():
    def __init__(self):
        self.mac_addr = str(uuid.getnode())

    def encode(self, clear):
        """Encode a string based on a key, in this case mac address"""
        enc = []
        for i in range(len(clear)):
            self.mac_addr_c = self.mac_addr[i % len(self.mac_addr)]
            enc_c = chr((ord(clear[i]) + ord(self.mac_addr_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()

    def decode(self, enc):
        """Decode a string based on a key, in this case mac address"""
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            self.mac_addr_c = self.mac_addr[i % len(self.mac_addr)]
            dec_c = chr((256 + ord(enc[i]) - ord(self.mac_addr_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

    def encoding(self, value):
        """Returns encoded string"""
        return self.encode(value)

    def decoding(self, value):
        """Returns decoded string"""
        return self.decode(value)


class FileHandler(Cryptograph):
    def __init__(self):
        Cryptograph.__init__(self)
        try:
            if os.path.isfile(os.path.join(os.pardir, "user_settings.json")):
                self.filename = os.path.join(os.pardir, "user_settings.json")
        except FileNotFoundError:
            self.filename = os.path.join("user_settings.json")

        self.data = self.read_conf()

    def read_conf(self):
        with open(self.filename, "r") as file:
            self.data = json.load(file)
            return self.data

    def write_conf(self, data):
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=2)

    def enc_ilo_path(self, path):
        self.data["reboot"]["ilo_location"] = self.encoding(path)
        self.write_conf(self.data)

    def dec_ilo_path(self):
        try:
            return str(self.decoding(self.data["reboot"]["ilo_location"]))
        except binascii.Error:
            print("Encoding iLO Installation Path is invalid!\n"
                  "Please provide it again for re-encryption.")
            self.enc_ilo_path(input())

    def enc_ilo_password(self, pwd):
        self.data["reboot"]["password"] = self.encoding(pwd)
        self.write_conf(self.data)

    def dec_ilo_password(self):
        try:
            return str(self.decoding(self.data["reboot"]["password"]))
        except binascii.Error:
            print("Invalid Password encoding!\n"
                  "Please provide it again for re-encryption.")
            self.enc_ilo_password(input())


class SleepTimers(FileHandler):
    def __init__(self):
        FileHandler.__init__(self)
        self.data = self.read_conf()

    def set_timer(self, key, value):
        self.data["reboot"]["sleep_timers"][key] = value
        self.write_conf(self.data)

    def get_timer(self, key):
        return int(self.data["reboot"]["sleep_timers"][key])


class GetDisplayData:
    def __init__(self):
        self.display_count = int()
        self.primary_display_x, self.primary_display_y = self.get_primary_display_size

    @property
    def get_display_count(self):
        self.display_count = len(win32api.EnumDisplayMonitors())
        return self.display_count

    @property
    def get_primary_display_size(self):
        return pyautogui.size()


class ClickCords(FileHandler, GetDisplayData):
    def __init__(self):
        FileHandler.__init__(self)
        GetDisplayData.__init__(self)
        self.data = self.read_conf()

    def which_display(self, cursor_x):
        """
        This function tries to figure out the setup of the dual display setup of a PC.
        Should a PC use more than 3 screens, default everything to display 1.

        Challenges:
            - We only know screen resolution of screen 1 (Primary).
            - We can't figure out layouts of 3 ore more displays.
            - No way to get all screen sizes or zoom level.

        Logic Implementation:
        LOGIC 1: Cursor X-pos smaller than Primary Xsize
        LOGIC 2: Cursor X-pos smaller than x=0
        What We know:
            - Primary Display will always start from tuple(x=0, y=0)
            - If Secondary is on LEFT side of Primary, it's x and y will always be negative.
            - If Secondary is on RIGHT side of Primary, it's x and y will always be greater than Primary X and Y
        DIAGRAM(s):
        Display SETUP: Primary | Secondary
        0,0               Primary max(X)         Secondary max(x)
         |----------------------|----------------------|>
                   ^                         ^
                   |                         |
            We know this            We don't know this.


        Display SETUP: Secondary | Primary
        Secondary max(-x)            (0, 0)             Primary max(x)
               <|----------------------|----------------------|>
                           ^                         ^
                           |                         |
                    We don't know this.         We know this

        :param cursor_x: Current Cursor X-position.
        :return: String of display1 or display2.
        """
        if self.get_display_count > 2:
            return "display1"
        else:
            if cursor_x > self.primary_display_x:
                return "display2"
            elif cursor_x < int(0):
                return "display2"
            elif 0 < cursor_x <= self.primary_display_x:
                return "display1"

    def set_click_cords(self, display, key, value):
        self.data["reboot"]["click_cords"][display][key] = value
        self.write_conf(self.data)

    def get_click_cords(self, display, key):
        return self.data["reboot"]["click_cords"][display][key]


class UserConfigurator(SleepTimers, ClickCords):
    def __init__(self):
        SleepTimers.__init__(self)
        ClickCords.__init__(self)


a = UserConfigurator()
print(a.dec_ilo_path())