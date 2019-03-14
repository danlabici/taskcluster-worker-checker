import json
import uuid
import base64
import binascii
import os


try:
    import win32api  # Only works on Windows.
    import pyautogui  # Only works on Windows.
except ImportError:
    pass


class Cryptograph():
    def __init__(self):
        self._mac_addr = str(uuid.getnode())

    def _encode(self, clear):
        """Encode a string based on a key, in this case mac address"""
        enc = []
        for i in range(len(clear)):
            self._mac_addr_c = self._mac_addr[i % len(self._mac_addr)]
            enc_c = chr((ord(clear[i]) + ord(self._mac_addr_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()

    def _decode(self, enc):
        """Decode a string based on a key, in this case mac address"""
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            self._mac_addr_c = self._mac_addr[i % len(self._mac_addr)]
            dec_c = chr((256 + ord(enc[i]) - ord(self._mac_addr_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

    def _encoding(self, value):
        """Returns encoded string"""
        return self._encode(value)

    def _decoding(self, value):
        """Returns decoded string"""
        return self._decode(value)


class FileHandler(Cryptograph):
    def __init__(self):
        Cryptograph.__init__(self)

        # For some reason try/except FileNotFound doesn't work, so we do it manually.
        check_file = os.path.isfile("user_settings.json")
        if check_file:
            self._filename = "user_settings.json"
        else:
            self._filename = os.path.join(os.pardir, "user_settings.json")

        self._data = self._read_conf()

    def _read_conf(self):
        with open(self._filename, "r") as file:
            self._data = json.load(file)
            return self._data

    def _write_conf(self, data):
        with open(self._filename, "w") as file:
            json.dump(data, file, indent=2)

    def save_ilo_path(self, path):
        self._data["reboot"]["ilo_location"] = self._encoding(path)
        self._write_conf(self._data)

    def read_ilo_path(self):
        try:
            return str(self._decoding(self._data["reboot"]["ilo_location"]))
        except binascii.Error:
            print("Encoding iLO Installation Path is invalid!\n"
                  "Please provide it again for re-encryption.")
            self.save_ilo_path(input())

    def save_ilo_password(self, pwd):
        self._data["reboot"]["password"] = self._encoding(pwd)
        self._write_conf(self._data)

    def read_ilo_password(self):
        try:
            return str(self._decoding(self._data["reboot"]["password"]))
        except binascii.Error:
            print("Invalid Password encoding!\n"
                  "Please provide it again for re-encryption.")
            self.save_ilo_password(input())


class SleepTimers(FileHandler):
    def __init__(self):
        FileHandler.__init__(self)
        self._data = self._read_conf()

    def save_sleep_timer(self, key, value):
        self._data["reboot"]["sleep_timers"][key] = int(value)
        self._write_conf(self._data)

    def read_sleep_timer(self, key):
        return int(self._data["reboot"]["sleep_timers"][key])


class GetDisplayData:
    def __init__(self):
        self._display_count = int()
        self._primary_display_x, self._primary_display_y = self._get_primary_display_size

    @property
    def get_display_count(self):
        self._display_count = len(win32api.EnumDisplayMonitors())
        return self._display_count

    @property
    def _get_primary_display_size(self):
        return pyautogui.size()


class ClickCords(FileHandler, GetDisplayData):
    def __init__(self):
        FileHandler.__init__(self)
        GetDisplayData.__init__(self)
        self._data = self._read_conf()

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
            if cursor_x > self._primary_display_x:
                return "display2"
            elif cursor_x < int(0):
                return "display2"
            elif 0 < cursor_x <= self._primary_display_x:
                return "display1"

    def save_click_cords(self, display, key, value):
        self._data["reboot"]["click_cords"][display][key] = value
        self._write_conf(self._data)

    def read_click_cords(self, display, key):
        return self._data["reboot"]["click_cords"][display][key]


class UserConfigurator(SleepTimers, ClickCords):
    def __init__(self):
        SleepTimers.__init__(self)
        ClickCords.__init__(self)
