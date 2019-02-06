#!/usr/bin/python3
import os
import sys
import json
import time
import ctypes
import signal
from datetime import datetime, timedelta
import platform
import subprocess

try:
    import gspread

    if (sys.platform == "linux") or (sys.platform == "linux2"):
        pass
    else:
        import win32gui, win32con, win32com.client
        from pynput.keyboard import Key, Controller
        import pyautogui as pyautogui
    import requests
    from prettytable import PrettyTable
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("Detected missing modules!\n"
          "Please Run and Restart the application:\n"
          "pip3 install -r requirements.txt")
    exit(0)

from twc_modules import configuration, main_menu

timenow = datetime.utcnow()
twc_version = configuration.VERSION
workerType = configuration.WORKERTYPE
windows = configuration.WINDOWS
linux = configuration.LINUX
yosemite = configuration.YOSEMITE

number_of_machines = 0
number_of_windows = 0
number_of_linux = 0
number_of_osx = 0
machines_to_reboot = []


def get_heroku_data():
    start = datetime.now()
    verbose = configuration.VERBOSE

    url = "http://releng-hardware.herokuapp.com/machines"
    headers = {"user-agent": "ciduty-twc/{}".format(twc_version)}
    if configuration.DEVMODE:
        data = open_json("machines.json")
    else:
        data = json.loads(requests.get(url, headers=headers).text)
    heroku_machines = {}
    for value in data:
        try:
            idle = timenow - datetime.strptime(value["lastseen"], "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            idle = timenow - datetime.strptime(value["lastseen"], "%Y-%m-%dT%H:%M:%S")
            print(value["machine"], " - Has Time Issues")
        _idle = int(idle.total_seconds())
        heroku_machines.update({value["machine"].lower(): {
            "lastseen": value["lastseen"], "idle": _idle, "datacenter": value["datacenter"],
            "status": value["machines-last-status"], "taskid": value["machines-last-taskid"]}})

    save_json("heroku_dict.json", heroku_machines)
    end = datetime.now()
    if verbose:
        print("Heroku Data Processing took:", end - start)
    return heroku_machines


def get_google_spreadsheet_data():
    start = datetime.now()
    verbose = configuration.VERBOSE
    # Define READONLY scopes needed for the CLI
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly",
              "https://www.googleapis.com/auth/drive.readonly"]

    # Setup Credentials
    ENV_CREDS = "ciduty-twc.json"
    login_info = ServiceAccountCredentials.from_json_keyfile_name(ENV_CREDS, scopes)

    # Authenticate / Login
    auth_token = gspread.authorize(login_info)

    # Choose which sheets from the SpreadSheet we will work with.
    moonshots_sheet_mdc1 = auth_token.open("Moonshot Master Inventory").worksheet("MDC_1")
    moonshots_sheet_mdc2 = auth_token.open("Moonshot Master Inventory").worksheet("MDC_2")
    osx_sheet_all_mdc = auth_token.open("Moonshot Master Inventory").worksheet("OSX")

    # Read the Data from the sheets
    moonshots_mdc1 = moonshots_sheet_mdc1.get_all_records()
    moonshots_mdc2 = moonshots_sheet_mdc2.get_all_records()
    osx_all_mdc = osx_sheet_all_mdc.get_all_records()

    # Construct dictionaries with all data that we need.
    moonshots_google_data_mdc1 = {entry["Hostname"]: {
        "prefix": entry["Hostname prefix"],
        "chassis": entry["Chassis"],
        "serial": entry["Cartridge Serial"],
        "cartridge": entry["Cartridge #"],
        "ilo": entry["ilo ip:port"],
        "owner": entry["Ownership"],
        "reason": entry["Ownership Reason"],
        "notes": entry["NOTES"],
        "ignore": entry["CiDuty CLI Ignore"]
    } for entry in moonshots_mdc1}

    moonshots_google_data_mdc2 = {entry["Hostname"]: {
        "prefix": entry["Hostname prefix"],
        "chassis": entry["Chassis"],
        "serial": entry["Cartridge Serial"],
        "cartridge": entry["Cartridge #"],
        "ilo": entry["ilo ip:port"],
        "owner": entry["Ownership"],
        "reason": entry["Ownership Reason"],
        "notes": entry["NOTES"],
        "ignore": entry["CiDuty CLI Ignore"]
    } for entry in moonshots_mdc2}

    osx_google_data = {entry["Hostname"]: {
        "serial": entry["Serial"],
        "warranty": entry["Warranty End Date"],
        "owner": entry["Ownership"],
        "reason": entry["Ownership Reason"],
        "notes": entry["Notes"],
        "ignore": entry["CiDuty CLI Ignore"]
    } for entry in osx_all_mdc}

    all_google_machine_data = {**moonshots_google_data_mdc1, **moonshots_google_data_mdc2,
                               **osx_google_data}
    save_json('google_dict.json', all_google_machine_data)
    end = datetime.now()
    if verbose:
        save_json('verbose_google_dict.json', all_google_machine_data)
        print("Google Data Processing took:", end - start)
    return all_google_machine_data


def open_json(file_name):
    with open("json_data/{}".format(file_name)) as f:
        data = json.load(f)
    return data


def save_json(file_name, data):
    with open("json_data/{}".format(file_name), 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.close()


def remove_fqdn_from_machine_name():
    start = datetime.now()
    verbose = configuration.VERBOSE
    # Update Machine-Key from FQDN to Hostname
    _google_dict = open_json('google_dict.json')
    for key in list(_google_dict):
        if len(key) > 1:
            if "t-linux64-ms-" in key:
                _google_dict[key[:16]] = _google_dict.pop(key)
            elif "t-w1064-ms-" in key:
                _google_dict[key[:14]] = _google_dict.pop(key)
            else:
                _google_dict[key[:17]] = _google_dict.pop(key)
    save_json('google_dict.json', _google_dict)
    end = datetime.now()
    if verbose:
        print("Removing the FQDN took:", end - start)


def add_heroku_data_to_google_dict():
    start = datetime.now()
    verbose = configuration.VERBOSE
    heroku_data = open_json("heroku_dict.json")
    google_data = open_json("google_dict.json")

    shared_keys = set(heroku_data).intersection(google_data)
    for key in shared_keys:
        machine_idle = {"idle": heroku_data.get(key)["idle"],
                        "status": heroku_data.get(key)["status"],
                        "taskid": heroku_data.get(key)["taskid"]}
        google_data[key].update(machine_idle)

    save_json("google_dict.json", google_data)
    end = datetime.now()
    if verbose:
        print("Adding IDLE times to Google Data took:", end - start)


def taskId(machine_data, machine):
    try:
        taskid = machine_data.get(machine)["taskid"]
    except KeyError:
        taskid = "-"
    return taskid


def status_cleaner(machine_data, machine):
    try:
        status = machine_data.get(machine)["status"]
    except KeyError:
        status = "-"
    if status is not None:
        if "completed_completed" in status:
            status = "Completed"
        elif "running_unresolved" in status:
            status = "Running"
        elif "failed_failed" in status:
            status = "Failed"
        else:
            pass
    else:
        pass
    return status


def twc_table_header(verbose, lazy_time):
    if not verbose:
        table = PrettyTable()
        table.field_names = ["Hostname", "IDLE Time ( >{} hours)".format(lazy_time),
                             "Machine Status", "ILO",
                             "Serial", "Other Notes"]
    else:
        table = PrettyTable()
        table.field_names = ["Hostname", "IDLE Time ( >{} hours)".format(lazy_time),
                             "Machine Status", "Last Task",
                             "ILO", "Serial", "Owner", "Ownership Notes", " Other Notes",
                             "Ignored?"]
    return table


def count_up_all(print_machine_numbers, machine):
    global number_of_machines, number_of_windows, number_of_linux, number_of_osx

    if "t-w1064-ms" in str(machine):
        number_of_windows += 1
    elif "t-linux64-ms" in str(machine):
        number_of_linux += 1
    elif "t-yosemite-r7" in str(machine):
        number_of_osx += 1
    else:
        pass

    if print_machine_numbers:
        print("Total Lazy Workers:", number_of_windows + number_of_linux + number_of_osx)
        print("Windows   Machines:", number_of_windows)
        print("Linux     Machines:", number_of_linux)
        print("OSX       Machines:", number_of_osx)


def twc_insert_table_row(**kwargs):
    verbose = kwargs.get("verbose")
    table = kwargs.get("table")
    workerType = kwargs.get("workerType")
    machine = kwargs.get("machine")
    hostname = machine
    idle = kwargs.get("idle")
    status = kwargs.get("status")
    taskid = kwargs.get("taskid")
    ilo = kwargs.get("ilo")
    serial = kwargs.get("serial")
    owner = kwargs.get("owner")
    reason = kwargs.get("reason")
    notes = kwargs.get("notes")
    ignore = kwargs.get("ignore")

    if workerType == "ALL":
        _verbose_google_dict = open_json("verbose_google_dict.json")
        for key in _verbose_google_dict:
            if machine in str(key):
                if not verbose:
                    if "t-yosemite-r7" in str(machine):
                        table.add_row([hostname, idle, status, ilo, serial, notes])
                        count_up_all(print_machine_numbers=False, machine=machine)

                    if configuration.PING and not ping_host(key):
                        table.add_row([hostname, idle, status, ilo, serial, notes])
                        count_up_all(print_machine_numbers=False, machine=machine)
                        machines_to_reboot.append((hostname, ilo))

                    if (not configuration.PING) and ("t-yosemite-r7" not in str(machine)):
                        table.add_row([hostname, idle, status, ilo, serial, notes])
                        count_up_all(print_machine_numbers=False, machine=machine)
                        machines_to_reboot.append((hostname, ilo))
                else:
                    if machine in str(key):
                        if configuration.PING:
                            print("Trying to ping:", key)
                            result = ping_host(key)
                            print("Ping {}: {}".format(("Failed" if not result else "Succeeded"),
                                                       key))
                            if not result:
                                table.add_row(
                                    [key, idle, status, taskid, ilo, serial, owner, reason, notes,
                                     ignore])
                                count_up_all(print_machine_numbers=False, machine=machine)
                                machines_to_reboot.append((hostname, ilo))
                        if not configuration.PING:
                            table.add_row(
                                [key, idle, status, taskid, ilo, serial, owner, reason, notes,
                                 ignore])
                            count_up_all(print_machine_numbers=False, machine=machine)
                            machines_to_reboot.append((hostname, ilo))

    if workerType == "t-w1064-ms" and workerType in str(machine):
        _verbose_google_dict = open_json("verbose_google_dict.json")
        for key in _verbose_google_dict:
            if machine in str(key):
                if not verbose:
                    if configuration.PING:
                        result = ping_host(key)
                        if not result:
                            table.add_row([hostname, idle, status, ilo, serial, notes])
                            count_up_all(print_machine_numbers=False, machine=machine)
                            machines_to_reboot.append((hostname, ilo))
                    else:
                        table.add_row([hostname, idle, status, ilo, serial, notes])
                        count_up_all(print_machine_numbers=False, machine=machine)
                        machines_to_reboot.append((hostname, ilo))
                else:
                    if machine in str(key):
                        if configuration.PING:
                            print("Trying to ping:" + key)
                            result = ping_host(key)

                            if not result:
                                table.add_row(
                                    [key, idle, status, taskid, ilo, serial, owner, reason, notes,
                                     ignore])
                                count_up_all(print_machine_numbers=False, machine=machine)
                                machines_to_reboot.append((hostname, ilo))
                        if not configuration.PING:
                            table.add_row(
                                [key, idle, status, taskid, ilo, serial, owner, reason, notes,
                                 ignore])
                            count_up_all(print_machine_numbers=False, machine=machine)
                            machines_to_reboot.append((hostname, ilo))

    if workerType == "t-linux64-ms" and workerType in str(machine):
        _verbose_google_dict = open_json("verbose_google_dict.json")
        for key in _verbose_google_dict:
            if machine in str(key):
                if not verbose:
                    if configuration.PING:
                        result = ping_host(key)
                        if not result:
                            table.add_row([hostname, idle, status, ilo, serial, notes])
                            count_up_all(print_machine_numbers=False, machine=machine)
                            machines_to_reboot.append((hostname, ilo))
                    else:
                        table.add_row([hostname, idle, status, ilo, serial, notes])
                        count_up_all(print_machine_numbers=False, machine=machine)
                        machines_to_reboot.append((hostname, ilo))
                else:
                    if machine in str(key):
                        if configuration.PING:
                            print("Trying to ping:", key)
                            result = ping_host(key)

                            if not result:
                                table.add_row([key, idle, status, taskid, ilo, serial,
                                               owner, reason, notes, ignore])
                                count_up_all(print_machine_numbers=False, machine=machine)
                                machines_to_reboot.append((hostname, ilo))
                        if not configuration.PING:
                            table.add_row([key, idle, status, taskid, ilo, serial,
                                           owner, reason, notes, ignore])
                            count_up_all(print_machine_numbers=False, machine=machine)
                            machines_to_reboot.append((hostname, ilo))

    if workerType == "t-yosemite-r7" and workerType in str(machine):
        if not verbose:
            table.add_row([hostname, idle, status, ilo, serial, notes])
            count_up_all(print_machine_numbers=False, machine=machine)
        else:
            _verbose_google_dict = open_json("verbose_google_dict.json")
            for key in _verbose_google_dict:
                if machine in str(key):
                    table.add_row(
                        [key, idle, status, taskid, ilo, serial, owner, reason, notes, ignore])
                    count_up_all(print_machine_numbers=False, machine=machine)

    return table


def output_problem_machines(workerType):
    verbose = configuration.VERBOSE
    lazy_time = configuration.LAZY
    machine_data = open_json("google_dict.json")

    table = twc_table_header(verbose, lazy_time)

    for machine in machine_data:
        ignore = machine_data.get(machine)["ignore"]
        notes = machine_data.get(machine)["notes"]
        serial = machine_data.get(machine)["serial"]
        owner = machine_data.get(machine)["owner"]
        reason = machine_data.get(machine)["reason"]

        taskid = taskId(machine_data, machine)
        status = status_cleaner(machine_data, machine)

        if notes == "":
            notes = "No notes available."
        else:
            pass

        try:
            idle = timedelta(seconds=machine_data.get(machine)["idle"])
            ilo = machine_data.get(machine)["ilo"]
        except KeyError:
            ilo = "-"

        if machine:
            key_data = {"workerType": workerType,
                        "machine": machine,
                        "verbose": verbose,
                        "table": table,
                        "idle": idle,
                        "status": status,
                        "taskid": taskid,
                        "ilo": ilo,
                        "serial": serial,
                        "owner": owner,
                        "reason": reason,
                        "notes": notes,
                        "ignore": ignore,
                        }

            if idle > timedelta(hours=lazy_time) and ignore == "No":
                twc_insert_table_row(**key_data)

    print(table)
    count_up_all(print_machine_numbers=True, machine=None)
    if configuration.OUTPUTFILE:
        write_html_data(table)

    print("Last Completed Run: " + str(datetime.strftime(datetime.now(), "%H:%M  %d-%b-%Y")))

    if configuration.AUTOREBOOT:
        auto_reboot()


def output_single_machine(single_machine):
    start = datetime.now()
    verbose = configuration.VERBOSE
    lazy_time = configuration.LAZY
    get_heroku_data()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_heroku_data_to_google_dict()
    machine_data = open_json("google_dict.json")

    table = twc_table_header(verbose=True, lazy_time=lazy_time)

    for machine in machine_data:
        hostname = machine
        notes = machine_data.get(machine)["notes"]
        serial = machine_data.get(machine)["serial"]
        owner = machine_data.get(machine)["owner"]
        reason = machine_data.get(machine)["reason"]
        ignore = machine_data.get(machine)["ignore"]

        taskid = taskId(machine_data, machine)
        status = status_cleaner(machine_data, machine)

        if notes == "":
            notes = "No notes available."
        else:
            pass

        try:
            idle = timedelta(seconds=machine_data.get(machine)["idle"])
            ilo = machine_data.get(machine)["ilo"]
        except KeyError:
            ilo = "-"

        if machine:
            if single_machine in str(machine):
                table.add_row(
                    [hostname, idle, status, taskid, ilo, serial, owner, reason, notes, ignore])

    print(table)

    if configuration.OUTPUTFILE:
        write_html_data(table)

    end = datetime.now()

    if verbose:
        print("Printing the missing machines took:", end - start)


def output_loaned_machines(**loaner):
    start = datetime.now()
    number_of_machines = 0
    verbose = configuration.VERBOSE
    lazy_time = configuration.LAZY
    get_heroku_data()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_heroku_data_to_google_dict()
    machine_data = open_json("google_dict.json")

    table = twc_table_header(verbose, lazy_time)

    for machine in machine_data:
        hostname = machine
        ignore = machine_data.get(machine)["ignore"]
        notes = machine_data.get(machine)["notes"]
        serial = machine_data.get(machine)["serial"]
        owner = machine_data.get(machine)["owner"]
        reason = machine_data.get(machine)["reason"]

        taskid = taskId(machine_data, machine)
        status = status_cleaner(machine_data, machine)

        if notes == "":
            notes = "No notes available."
        else:
            pass

        try:
            idle = timedelta(seconds=machine_data.get(machine)["idle"])
            ilo = machine_data.get(machine)["ilo"]
        except KeyError:
            ilo = "-"

        if machine:
            for value in loaner:
                if owner:
                    if loaner.get(value) == "":
                        if not verbose:
                            table.add_row([hostname, idle, status, ilo, serial, notes, ignore])
                            number_of_machines += 1
                        else:
                            table.add_row(
                                [hostname, idle, status, taskid, ilo, serial, owner, reason, notes,
                                 ignore])
                            number_of_machines += 1

                    else:
                        if str(loaner.get(value)).lower() == str(owner).lower():
                            if not verbose:
                                table.add_row([hostname, idle, status, ilo, serial, notes, ignore])
                                number_of_machines += 1
                            else:
                                table.add_row(
                                    [hostname, idle, status, taskid, ilo, serial, owner, reason,
                                     notes, ignore])
                                number_of_machines += 1

    print(table)
    print("Total number of loaned machines:", number_of_machines)

    if configuration.OUTPUTFILE:
        write_html_data(table)

    end = datetime.now()

    if verbose:
        print("Printing the loaned machines took:", end - start)


def output_machines_with_notes():
    start = datetime.now()
    number_of_machines = 0
    verbose = configuration.VERBOSE
    lazy_time = configuration.LAZY
    get_heroku_data()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_heroku_data_to_google_dict()
    machine_data = open_json("google_dict.json")

    table = twc_table_header(verbose=True, lazy_time=lazy_time)

    for machine in machine_data:
        hostname = machine
        ignore = machine_data.get(machine)["ignore"]
        notes = machine_data.get(machine)["notes"]
        serial = machine_data.get(machine)["serial"]
        owner = machine_data.get(machine)["owner"]
        reason = machine_data.get(machine)["reason"]

        taskid = taskId(machine_data, machine)
        status = status_cleaner(machine_data, machine)

        if notes == "":
            notes = "No notes available."
        else:
            pass

        try:
            idle = timedelta(seconds=machine_data.get(machine)["idle"])
            ilo = machine_data.get(machine)["ilo"]
        except KeyError:
            ilo = "-"

        if machine:
            if notes is not "No notes available.":
                table.add_row(
                    [hostname, idle, status, taskid, ilo, serial, owner, reason, notes, ignore])
                number_of_machines += 1
            else:
                pass

    print(table)
    print("Total number of machines with notes:", number_of_machines)

    if configuration.OUTPUTFILE:
        write_html_data(table)

    end = datetime.now()

    if verbose:
        print("Printing the loaned machines took:", end - start)


def write_html_data(*args):
    x = args[0]
    default_html = """
    <head>
        <style type="text/css">
            table {border-collapse:collapse;border-spacing:0;border-color:#aabcfe;}
            table td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#aabcfe;color:#669;background-color:#e8edff;}
            table th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#aabcfe;color:#039;background-color:#b9c9fe;}
            table .tg-hmp3{background-color:#D2E4FC;text-align:left;vertical-align:top}
            table .tg-baqh{text-align:center;vertical-align:top}
            table .tg-mb3i{background-color:#D2E4FC;text-align:right;vertical-align:top}
            table .tg-lqy6{text-align:right;vertical-align:top}
            table .tg-0lax{text-align:left;vertical-align:top}
        </style>
    </head>
    """

    # Delete old data and insert the styling.
    with open("index.html", "w+") as f:
        f.write(default_html)

    # Append the table.
    with open("index.html", "a") as f:
        f.write(x.get_html_string())
        f.close()

    if configuration.OPENHTML:
        os.system("start" + " index.html")


def force_ilo_active_window(focus_ilo):
    toplist = []
    winlist = []
    shell = win32com.client.Dispatch("WScript.Shell")

    def enum_callback(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_callback, toplist)
    focused_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    restore_app = [(hwnd, title) for hwnd, title in winlist if focused_app.lower() in title.lower()]
    ilo_app = [(hwnd, title) for hwnd, title in winlist if
               'iLO Integrated Remote Console'.lower() in title.lower()]
    ilo_app = ilo_app[0]
    restore_app = restore_app[0]

    shell.SendKeys('%')
    win32gui.SetForegroundWindow(ilo_app[0])

    if focus_ilo:
        if restore_app == ilo_app:
            pass
        else:
            shell.SendKeys('%')
            win32gui.ShowWindow(ilo_app[0], win32con.SW_RESTORE)
            time.sleep(1)

    if not focus_ilo:
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(restore_app[0])
    return True


def ping_host(host):
    """
    Returns True if host responds to a ping request
    """
    # Ping parameters as function of OS
    ping_retries = "-n 3" if platform.system().lower() == "windows" else "-c 3"
    ping_wait_time = "-w 5" if platform.system().lower() == "windows" else "-W 5"
    args = "ping " + " " + ping_retries + " " + ping_wait_time + " " + host
    need_sh = False if platform.system().lower() == "windows" else True

    return subprocess.call(args=args, shell=need_sh, stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT) == 0


def auto_reboot():
    ilo_location = configuration.ILO
    if machines_to_reboot:
        cursor = ctypes.windll.user32
        keyboard = Controller()
        for entry in machines_to_reboot:
            if entry[1] is not "-":
                x, y = pyautogui.position()
                if x < 1980:  # Main Screen Coordinates
                    ilo = (1080, 475)
                    password = (1080, 525)
                    connect_btn = (855, 620)
                    power_dropdown = (610, 260)
                    cold_boot = (610, 325)
                else:  # Second Screen Coordinates
                    ilo = (2957, 475)
                    password = (2993, 531)
                    connect_btn = (2779, 620)
                    power_dropdown = (2530, 260)
                    cold_boot = (2530, 325)

                proc_id = []
                hp_app = subprocess.Popen(ilo_location)
                time.sleep(1)
                proc_id.append(hp_app.pid)

                # IP:Port Position
                # force_ilo_active_window(focus_ilo=True)
                x, y = pyautogui.position()
                cursor.SetCursorPos(ilo[0], ilo[1])
                pyautogui.click()
                with keyboard.pressed(Key.ctrl):
                    keyboard.press('a')
                    keyboard.release('a')
                keyboard.press(Key.backspace)
                # Insert ILO IP:PORT
                keyboard.type(entry[1])
                cursor.SetCursorPos(x, y)

                # Password Position
                x, y = pyautogui.position()
                cursor.SetCursorPos(password[0], password[1])
                pyautogui.click()
                cursor.SetCursorPos(x, y)
                # Insert Password
                keyboard.type(str(configuration.PASSWORD))

                # Connect Button Position
                x, y = pyautogui.position()
                cursor.SetCursorPos(connect_btn[0], connect_btn[1])
                pyautogui.click()
                cursor.SetCursorPos(x, y)
                # force_ilo_active_window(focus_ilo=False)

                # Power Dropdown
                time.sleep(5)
                x, y = pyautogui.position()
                cursor.SetCursorPos(power_dropdown[0], power_dropdown[1])
                force_ilo_active_window(focus_ilo=True)
                pyautogui.click()
                cursor.SetCursorPos(x, y)

                # Cold Reboot
                x, y = pyautogui.position()
                cursor.SetCursorPos(cold_boot[0], cold_boot[1])
                pyautogui.click()
                force_ilo_active_window(focus_ilo=False)
                cursor.SetCursorPos(x, y)

                # Close the process
                os.kill(int(proc_id[0]), signal.SIGTERM)
                if configuration.VERBOSE:
                    print("Restart Process for " + str(entry[0]) + " finished.")
    else:
        print("No machines to reboot! Closing application.")
        exit(0)


def push_to_git():
    pass


def run_logic(workerType):
    """
    This is the main order in which the tool will run all the functions needed to return the result.
      - If new features are added, which needs to run WITHOUT a parameter, it needs to be added here
    """
    get_heroku_data()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_heroku_data_to_google_dict()
    output_problem_machines(workerType=workerType)


def dev_run_logic():
    """
    When debugging and you change how data is stored/manipulated, use this function to always
    recreate the files. This will also skip the MainMenu of the CLI application
    :return: Fresh data.
    """
    get_heroku_data()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_heroku_data_to_google_dict()
    output_problem_machines(workerType=workerType)


if __name__ == "__main__":
    try:
        if "-v" in sys.argv:
            configuration.VERBOSE = True

        if "-l" in sys.argv:
            lazy_time_index = sys.argv.index("-l") + 1
            lazy_time = sys.argv[lazy_time_index]
            try:
                configuration.LAZY = int(lazy_time)
            except ValueError as err:
                print("Expecting integer for the Lazy Time value, but got:\n", err)
                exit(-1)

        if "-m" in sys.argv:
            choise_index = sys.argv.index("-m") + 1
            choise = sys.argv[choise_index]
            try:
                configuration.CHOICE = int(choise)
            except ValueError as err:
                print("Expecting integer for the Lazy Time value, but got:\n", err)
                exit(-1)

        if "-o" in sys.argv:
            configuration.OUTPUTFILE = True

        if "-o" and "-a" in sys.argv:
            configuration.OPENHTML = True

        if "-p" in sys.argv:
            configuration.PERSISTENT = True
            main_menu.menu_persistent()

        if len(sys.argv) > int(1):
            configuration.ARGLEN = len(
                sys.argv) - 1  # We subtract 1 as that's the client.py argument.

        if "-rb" in sys.argv:
            if (sys.platform == "linux") or (sys.platform == "linux2"):
                print("Call HP and ask for iLO on Linux. \n"
                      "Till that point, auto-reboot only works on Windows.")
                configuration.AUTOREBOOT = False
            if "-v" not in sys.argv:
                print("To autoreboot, you need `-v` in arguments.")
                exit(0)
            else:
                configuration.AUTOREBOOT = True

        if "-ping" in sys.argv:
            print("Testing for VPN connection")
            RESULT = ping_host("rejh1.srv.releng.mdc1.mozilla.com")
            if RESULT:
                print("Connection Successful!")
                configuration.PING = True
            else:
                print("VPN seems to be off \n"
                      "Script Stopped from running!")
                exit(0)

        if "-dev" in sys.argv:
            try:
                open_json("machines.json")
                configuration.DEVMODE = True
            except FileNotFoundError:
                configuration.DEVMODE = False

        if "-tc" in sys.argv:
            configuration.TRAVISCI = True
            print("TravisCI Testing Begins!")
            dev_run_logic()
        else:
            main_menu.run_menu()
    except (KeyboardInterrupt, SystemExit):
        exit(0)
