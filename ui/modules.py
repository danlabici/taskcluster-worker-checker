import json
from datetime import datetime, timedelta
from twc_modules.configuration import *
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

twc_version = VERSION
timenow = datetime.utcnow()


def open_json(file_name):
    with open("json_data/{}".format(file_name)) as f:
        data = json.load(f)
        print("open file")
    return data


def save_json(file_name, data):
    with open("json_data/{}".format(file_name), 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.close()

def get_heroku_last_seen():
    start = datetime.now()
    # verbose = configuration.VERBOSE
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
    # if verbose:
    #     print("Heroku Data Processing took:", end - start)
    return heroku_machines

def get_google_spreadsheet_data():
    start = datetime.now()
    # verbose = configuration.VERBOSE
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
    # if verbose:
    #     save_json('verbose_google_dict.json', all_google_machine_data)
    #     print("Google Data Processing took:", end - start)
    return all_google_machine_data

def add_idle_to_google_dict():
    start = datetime.now()
    # verbose = configuration.VERSION
    heroku_data = open_json("heroku_dict.json")
    google_data = open_json("google_dict.json")

    shared_keys = set(heroku_data).intersection(google_data)
    for key in shared_keys:
        machine_idle = {"idle": heroku_data.get(key)["idle"]}
        google_data[key].update(machine_idle)

    save_json("google_dict.json", google_data)
    end = datetime.now()
    # if verbose:
    #     print("Adding IDLE times to Google Data took:", end - start)

def remove_fqdn_from_machine_name(hostname):
    if len(hostname) > 1:
        if "t-linux64-ms-" in hostname:
            return hostname[:16]
        elif "t-w1064-ms-" in hostname:
            return hostname[:14]
        else:
            return hostname[:17]