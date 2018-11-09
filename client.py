"""
This script will check for missing moonshots in TaskCluster.
github repo: https://github.com/Akhliskun/taskcluster-worker-checker
"""
try:
    import os
    import json
    import gspread
    import prettytable

    import urllib.request
    from argparse import ArgumentParser
    from collections import namedtuple
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("Detected Missing Dependences! \n Please run the following, based on your OS type.")
    print("Windows: \npip install prettytable gspread oauth2client pyopenssl")
    print("Linux/OSX: \npip3 install prettytable gspread oauth2client pyopenssl")
    exit(0)


workersList = []  # Used by TaskCluster API Logic

all_osx_machines = []
all_linux_machines = []
all_windows_machines = []
all_google_machines = []
machines_to_ignore = []

LINUX = "gecko-t-linux-talos"
WINDOWS = "gecko-t-win10-64-hw"
MACOSX = "gecko-t-osx-1010"


def parse_taskcluster_json(workertype):
    '''
    We need this incase Auth fails.
    :param workertype: gecko-t-linux-talos, gecko-t-win10-64-hw, gecko-t-osx-1010.
    :return: A JSON file containing all workers for a workertype selected at runtime.
    '''

    # Setup API URLs
    if (workertype == LINUX) or (workertype == "linux"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-linux-talos/workers"

    elif (workertype == WINDOWS) or (workertype == "win"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-win10-64-hw/workers"

    elif (workertype == MACOSX) or (workertype == "osx"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-osx-1010/workers"

    else:
        print("ERROR: Unknown worker-type!")
        print("Please run the script with the [client.py -h] to see the help docs!")
        exit(0)

    with urllib.request.urlopen(apiUrl, timeout=10) as api:
        try:
            data = json.loads(api.read().decode())

        except:
            print("TIMEOUT: JSON response didn't arive in 10 seconds!")
            exit(0)

        try:
            if not data["workers"]:
                # TaskCluster has an issue with RelEng hardware. BUG 1497560
                print("Empty Worker List. Retrying...")
                parse_taskcluster_json(workertype)
            else:
                for workers in data['workers']:
                    workersList.append(workers['workerId'].lower())

        except KeyboardInterrupt:
            print("Application stopped via Keyboard Shortcut.")
            exit(0)

    return workersList

def google_auth():
    # Define READONLY scopes needed for the CLI
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]

    # Setup Credentials
    ENV_CREDS = "ciduty-twc.json"
    login_info = ServiceAccountCredentials.from_json_keyfile_name(ENV_CREDS, scopes)

    # Authenticate / Login
    auth_token = gspread.authorize(login_info)
    return auth_token

def get_moonshot_spreadsheet_data():
    moonshots_sheet_mdc1 = google_auth().open("Moonshot Master Inventory").get_worksheet(0)
    moonshots_sheet_mdc2 = google_auth().open("Moonshot Master Inventory").get_worksheet(1)

    moonshots_mdc1 = moonshots_sheet_mdc1.get_all_records()
    moonshots_mdc2 = moonshots_sheet_mdc2.get_all_records()

    moonshots_google_data_mdc1 = [(entry["Hostname prefix"], entry["Hostname"], entry["Chassis"], entry["Cartridge #"],
                                   entry["ilo ip:port"], entry["Ownership"], entry["Ownership Reason"], entry["NOTES"],
                                   entry["CiDuty CLI Ignore"]) for entry in moonshots_mdc1]
    moonshots_google_data_mdc2 = [(entry["Hostname prefix"], entry["Hostname"], entry["Chassis"], entry["Cartridge #"],
                                   entry["ilo ip:port"], entry["Ownership"], entry["Ownership Reason"], entry["NOTES"],
                                   entry["CiDuty CLI Ignore"]) for entry in moonshots_mdc2]

    all_moonshots_data = moonshots_google_data_mdc1 + moonshots_google_data_mdc2
    return all_moonshots_data

def get_osx_spreadsheet_data():
    osx_sheet_all_mdc = google_auth().open("Moonshot Master Inventory").get_worksheet(2)
    osx_all_mdc = osx_sheet_all_mdc.get_all_records()

    osx_google_data = [(entry["Hostname"], entry["Serial"], entry["Warranty End Date"],entry["Ownership"],
                        entry["Ownership Reason"], entry["Notes"], entry["CiDuty CLI Ignore"]) for entry in osx_all_mdc]

    return osx_google_data

def name_touple_values():
    moonshot_field_names = namedtuple("Moonshots", ["prefix", "hostname", "chassis", "cartridge", "ilo", "owner", "reason", "note", "ignore"])
    osx_field_names = namedtuple("OSX", ["hostname", "serial", "warranty", "owner", "reason", "note", "ignore"])

    # Generate List of all machines.
    for entry in get_moonshot_spreadsheet_data():
        row = moonshot_field_names._make(entry)
        all_google_machines.append(row)

        # Generate Moonshot list of machines to ignore.
        if row.ignore == "Yes":
            machines_to_ignore.append(row)

    for entry in get_osx_spreadsheet_data():
        row = osx_field_names._make(entry)
        all_google_machines.append(row)

        # Generate OSX list of machines to ignore.
        if row.ignore == "Yes":
            machines_to_ignore.append(row)

    for row in all_google_machines[:600]:
        if row.prefix == "t-w1064-ms":
            all_windows_machines.append(row.hostname)
        elif row.prefix == "t-linux64-ms":
            all_linux_machines.append(row.hostname)
        elif row.prefix == "":
            pass
        else:
            print("Something went wrong with the Google Machines Generator")

    for row in all_google_machines[-int(len(all_google_machines) - 600):]:
        all_osx_machines.append(row.hostname)

    return all_google_machines, machines_to_ignore, all_linux_machines, all_windows_machines, all_osx_machines


def main():
    # Get/Set Arguments
    parser = ArgumentParser(description="Utility to check missing moonshots form TC.")
    parser.add_argument("-w", "--worker-type",
                        dest="worker_type",
                        help="Available options: gecko-t-linux-talos, linux, gecko-t-win10-64-hw, win, gecko-t-osx-1010, mac",
                        default=LINUX,
                        required=False)
    parser.add_argument("-u", "--ldap-username",
                        dest="ldap_username",
                        help="Example: -u dlabici -- Don't include @mozilla.com!!",
                        default="root",
                        required=False)

    parser.add_argument("-v", "--verbose",
                        dest="verbose_enabler",
                        help="Example: -v True",
                        default=False,
                        required=False)

    args = parser.parse_args()
    workertype = args.worker_type
    ldap = args.ldap_username
    verbose = args.verbose_enabler

    parse_taskcluster_json(workertype)

        # Remove machines from generated list
    if (workertype == LINUX) or (workertype == "linux"):
        to_ignore = []
        for machine in all_google_machines[:600]:
            if machine.prefix == "t-linux64-ms" and machine.ignore == "Yes":
                to_ignore.append(machine.hostname)

        a = set(to_ignore)
        workers = [x for x in all_linux_machines if x not in a]


    if (workertype == WINDOWS) or (workertype == "win"):
        to_ignore = []
        for machine in all_google_machines[:600]:
            if machine.prefix == "t-w1064-ms" and machine.ignore == "Yes":
                to_ignore.append(machine.hostname)

        a = set(to_ignore)
        workers = [x for x in all_windows_machines if x not in a]


    if (workertype == MACOSX) or (workertype == "osx"):
        to_ignore = []
        for machine in all_google_machines[-int(len(all_google_machines) - 600):]:  # Pick only OSX machines (last 450 entries)
            if machine.ignore == "Yes":
                to_ignore.append(machine.hostname)

        a = set(to_ignore)
        workers = [x for x in all_osx_machines if x not in a]


    b = set(workersList)
    worker_list = []

    if (workertype == WINDOWS) or (workertype == "win"):
        for machine in workers:
            worker_list.append(machine[:14])
        missing_machines = [x for x in worker_list if x not in b]
        print("Total Missing Machines: ",len(missing_machines))
        for machine in missing_machines:
            print(machine)

    if (workertype == LINUX) or (workertype == "linux"):
        for machine in workers:
            worker_list.append(machine[:16])
        missing_machines = [x for x in worker_list if x not in b]
        print("Total Missing Machines: ", len(missing_machines))
        for machine in missing_machines:
            print(machine)

    if (workertype == MACOSX) or (workertype == "osx"):
        for machine in workers:
            worker_list.append(machine[:17])
        missing_machines = [x for x in worker_list if x not in b]
        print("Total Missing Machines: ", len(missing_machines))
        for machine in missing_machines:
            print(machine)



if __name__ == '__main__':
    name_touple_values()
    main()