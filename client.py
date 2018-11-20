#!/usr/bin/python3
import sys
import json
from datetime import datetime, timedelta

try:
    import gspread
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

def get_heroku_last_seen():
    start = datetime.now()
    verbose = configuration.VERBOSE
    url = "http://releng-hardware.herokuapp.com/machines"
    headers = {"user-agent": "ciduty-twc/{}".format(twc_version)}
    data = json.loads(requests.get(url, headers=headers).text)
    heroku_machines = {}
    for value in data:
        idle = timenow - datetime.strptime(value["lastseen"], "%Y-%m-%dT%H:%M:%S.%f")
        _idle = int(idle.total_seconds())
        heroku_machines.update(
            {value["machine"].lower(): {"lastseen": value["lastseen"], "idle": _idle,
                                        "datacenter": value["datacenter"]}})

    save_json("heroku_dict.json", heroku_machines)
    end = datetime.now()
    if verbose:
        print("Heroku Data Processing took:", end - start)
    return heroku_machines


def get_google_spreadsheet_data():
    start = datetime.now()
    verbose = configuration.VERBOSE
    # Define READONLY scopes needed for the CLI
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]

    # Setup Credentials
    ENV_CREDS = "ciduty-twc.json"
    login_info = ServiceAccountCredentials.from_json_keyfile_name(ENV_CREDS, scopes)

    # Authenticate / Login
    auth_token = gspread.authorize(login_info)

    # Choose which sheets from the SpreadSheet we will work with.
    moonshots_sheet_mdc1 = auth_token.open("Moonshot Master Inventory").get_worksheet(0)
    moonshots_sheet_mdc2 = auth_token.open("Moonshot Master Inventory").get_worksheet(1)
    osx_sheet_all_mdc = auth_token.open("Moonshot Master Inventory").get_worksheet(2)

    # Read the Data from the sheets
    moonshots_mdc1 = moonshots_sheet_mdc1.get_all_records()
    moonshots_mdc2 = moonshots_sheet_mdc2.get_all_records()
    osx_all_mdc = osx_sheet_all_mdc.get_all_records()

    # Construct dictionaries with all data that we need.
    moonshots_google_data_mdc1 = {entry["Hostname"]:
        {
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

    moonshots_google_data_mdc2 = {entry["Hostname"]:
        {
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

    osx_google_data = {entry["Hostname"]:
        {
            "serial": entry["Serial"],
            "warranty": entry["Warranty End Date"],
            "owner": entry["Ownership"],
            "reason": entry["Ownership Reason"],
            "notes": entry["Notes"],
            "ignore": entry["CiDuty CLI Ignore"]
        } for entry in osx_all_mdc}

    all_google_machine_data = {**moonshots_google_data_mdc1, **moonshots_google_data_mdc2, **osx_google_data}
    save_json('google_dict.json', all_google_machine_data)
    end = datetime.now()
    if verbose:
        save_json('vebose_google_dict.json', all_google_machine_data)
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


def add_idle_to_google_dict():
    start = datetime.now()
    verbose = configuration.VERSION
    heroku_data = open_json("heroku_dict.json")
    google_data = open_json("google_dict.json")

    shared_keys = set(heroku_data).intersection(google_data)
    for key in shared_keys:
        machine_idle = {"idle": heroku_data.get(key)["idle"]}
        google_data[key].update(machine_idle)

    save_json("google_dict.json", google_data)
    end = datetime.now()
    if verbose:
        print("Adding IDLE times to Google Data took:", end - start)


def output_problem_machines(workerType):
    start = datetime.now()
    verbose = configuration.VERBOSE
    lazy_time = configuration.LAZY
    machine_data = open_json("google_dict.json")
    if not verbose:
        table = PrettyTable()
        table.field_names = ["Hostname", "IDLE Time ( >{} hours)".format(lazy_time), "ILO", "Serial", "Other Notes"]
    else:
        table = PrettyTable()
        table.field_names = ["Hostname", "IDLE Time ( >{} hours)".format(lazy_time), "ILO", "Serial", "Owner",
                             "Ownership Notes", " Other Notes", "Ignored?"]

    for machine in machine_data:
        hostname = machine
        ignore = machine_data.get(machine)["ignore"]
        notes = machine_data.get(machine)["notes"]
        serial = machine_data.get(machine)["serial"]
        owner = machine_data.get(machine)["owner"]
        reason = machine_data.get(machine)["reason"]

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
            if idle > timedelta(hours=lazy_time) and ignore == "No":
                if workerType == "ALL":
                    if not verbose:
                        table.add_row([hostname, idle, ilo, serial, notes])
                    else:
                        _verbose_google_dict = open_json("vebose_google_dict.json")
                        for key in _verbose_google_dict:
                            if machine in str(key):
                                table.add_row([key, idle, ilo, serial, owner, reason, notes, ignore])

                if workerType == "t-w1064-ms" and workerType in str(machine):
                        if not verbose:
                            table.add_row([hostname, idle, ilo, serial, notes])
                        else:
                            _verbose_google_dict = open_json("vebose_google_dict.json")
                            for key in _verbose_google_dict:
                                if machine in str(key):
                                    table.add_row([key, idle, ilo, serial, owner, reason, notes, ignore])

                if workerType == "t-linux64-ms" and workerType in str(machine):
                        if not verbose:
                            table.add_row([hostname, idle, ilo, serial, notes])
                        else:
                            _verbose_google_dict = open_json("vebose_google_dict.json")
                            for key in _verbose_google_dict:
                                if machine in str(key):
                                    table.add_row([key, idle, ilo, serial, owner, reason, notes, ignore])

                if workerType == "t-yosemite-r7" and workerType in machine:
                        if not verbose:
                            table.add_row([hostname, idle, ilo, serial, notes])
                        else:
                            _verbose_google_dict = open_json("vebose_google_dict.json")
                            for key in _verbose_google_dict:
                                if machine in str(key):
                                    table.add_row([key, idle, ilo, serial, owner, reason, notes, ignore])

    print(table)
    end = datetime.now()

    if verbose:
        print("Printing the missing machines took:", end - start)


def write_html_data():
    pass


def push_html_to_git():
    pass


def run_logic(workerType):
    """
    This is the main order in which the tool will run all the functions needed to return the result.
      - If new features are added, which needs to run WITHOUT a parameter, it needs to be added here.
    """
    get_heroku_last_seen()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_idle_to_google_dict()
    output_problem_machines(workerType=workerType)


def dev_run_logic():
    """
    When debugging and you change how data is stored/manipulated, use this function to always recreate the files.
    This will also skip the MainMenu of the CLI application
    :return: Fresh data.
    """
    get_heroku_last_seen()
    get_google_spreadsheet_data()
    remove_fqdn_from_machine_name()
    add_idle_to_google_dict()
    output_problem_machines(workerType=workerType)


if __name__ == "__main__":
    if "-v" in sys.argv:
        configuration.VERBOSE = True

    if "-l" in sys.argv:
        lazy_time_index = sys.argv.index("-l") + 1
        lazy_time = sys.argv[lazy_time_index]
        try:
            configuration.LAZY = int(lazy_time)
        except ValueError as e:
            print("Expecting integer for the Lazy Time value, but got:\n", e)
            exit(-1)

    if "-tc" in sys.argv:
        configuration.TRAVISCI = True
        print("TravisCI Testing Begins!")
        dev_run_logic()
    else:
        main_menu.run_menu()
