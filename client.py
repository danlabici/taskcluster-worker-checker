"""
This script will check for missing moonshots in TaskCluster.
github repo: https://github.com/Akhliskun/taskcluster-worker-checker
"""
import os

try:
    from argparse import ArgumentParser
    import urllib.request, json
    import prettytable
except ImportError:
    print("Detected Missing Dependences! \n Trying Automated Installation.")
    print("If installation fails, please run: pip install prettytable")
    os.system("python -m pip install prettytable")

# Define machines that SHOULDN'T appear.
# Example: Machine is dev-env, loaner, or has known problems etc.
machines_to_ignore = {
    "linux": {
        "loaner": {

            "t-linux64-ms-394": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },

            "t-linux64-ms-395": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },

            "t-linux64-ms-580": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1474573",
                "owner": ":dev-env"
            },
        },
        "pxe_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
        "hdd_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
        "ssh_stdio": {
            "t-linux64-ms-308": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1491566",
                "date": "28.09.2018",
                "update": "https://bugzilla.mozilla.org/show_bug.cgi?id=1491567"
            },
            "t-linux64-ms-358": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1492808",
                "date": "20.09.2018",
                "update": "New bug. No update"
            },
        },
        "other_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
    },
    "linuxtw": {
        "loaner": {

            "t-linux64-ms-240": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },
            "t-linux64-ms-280": {
                "bug": "Staging Pool - https://bugzilla.mozilla.org/show_bug.cgi?id=1464070",
                "owner": ":dragrom"
            },
        },
        "pxe_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
        "hdd_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
        "ssh_stdio": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
        "other_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
    },
    "windows": {
        "loaner": {
            "T-W1064-MS-581": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1499223",
                "owner": ":markco"
            },
            "T-W1064-MS-582": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1499223",
                "owner": ":markco"
            },
        },
        "pxe_issues": {
            "T-W1064-MS-262": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1498851",
                "date": "13.10.2018",
                "update": "New bug. No updates"
            },
        },
        "hdd_issues": {
            "No Issue": {
                "bug": "No BUG",
                "date": "No Date",
                "update": "No Update"
            },
        },
        "other_issues": {
            "T-W1064-MS-116": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1485213",
                "date": "16.10.2018",
                "update": "machine not picking up tasks even after reimage"
            },
            "T-W1064-MS-125": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1490314",
                "date": "26.09.2018",
                "update": "powered off after green task. Food for markco"
            },
            "T-W1064-MS-258": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1493240#c2",
                "date": "30.09.2018",
                "update": "do not touch"
            },
            "T-W1064-MS-284": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1491466",
                "date": "16.10.2018",
                "update": "worker is dead"
            },
            "T-W1064-MS-318": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1495255",
                "date": "30.09.2018",
                "update": "New bug. No update"
            },
            "T-W1064-MS-320": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1495257",
                "date": "30.09.2018",
                "update": "New bug. No update"
            },
            "T-W1064-MS-321": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1482758",
                "date": "30.09.2018",
                "update": "New bug. No update"
            },
            "T-W1064-MS-322": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1480216",
                "date": "30.09.2018",
                "update": "New bug. No update"
            },
            "T-W1064-MS-323": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1495263",
                "date": "30.09.2018",
                "update": "New bug. No update"
            },
            "T-W1064-MS-324": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1480778",
                "date": "30.09.2018",
                "update": "New bug. No update"
            },
            "T-W1064-MS-345": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1482776",
                "date": "30.09.2018",
                "update": "https://bugzilla.mozilla.org/show_bug.cgi?id=1482776#c2"
            },
            "T-W1064-MS-465": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494810",
                "date": "28.09.2018",
                "update": "pxe network boot problems"
            },
            "T-W1064-MS-470": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494867",
                "date": "28.09.2018",
                "update": "No video on ILO. Asked Van to re-seat."
            },
            "T-W1064-MS-474": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494017",
                "date": "26.09.2018",
                "update": "pxe network boot problems"
            },
            "T-W1064-MS-599": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494010",
                "date": "26.09.2018",
                "update": "pxe network boot problems"
            },
            "T-W1064-MS-600": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494013",
                "date": "26.09.2018",
                "update": "pxe network boot problems"
            },
        },
    },
    "osx": {
        "loaner": {
            "t-yosemite-r7-100": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },

            "t-yosemite-r7-101": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },

            "t-yosemite-r7-246": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1492703",
                "owner": ":dhouse"
            },

            "t-yosemite-r7-253": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1452773",
                "owner": ":bwc"
            },

            "t-yosemite-r7-266": {
                "bug": "1487818",
                "owner": ":dividehex"
            },

            "t-yosemite-r7-276": {
                "bug": "1487818",
                "owner": ":dividehex"
            },

            "t-yosemite-r7-380": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },

            "t-yosemite-r7-394": {
                "bug": "Staging Pool - No Bug",
                "owner": ":dragrom"
            },
        },
        "ssh_stdio": {
            "t-yosemite-r7-068": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1486195",
                "date": "13.10.2018",
                "update": "https://bugzilla.mozilla.org/show_bug.cgi?id=1486195#c2"
            },
            "t-yosemite-r7-109": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1476837",
                "date": "13.10.2018",
                "update": "New Bug. No updates"
            },
            "t-yosemite-r7-144": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1498015",
                "date": "13.10.2018",
                "update": "New Bug. No updates"
            },
            "t-yosemite-r7-150": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1498025",
                "date": "13.10.2018",
                "update": "New Bug. No updates"
            },
        },
        "ssh_unresponsive": {
            "t-yosemite-r7-189": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1472682",
                "date": "16.08.2018",
                "update": "New bug, no updates yet."
            },
            "t-yosemite-r7-223": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1482741",
                "date": "28.09.2018",
                "update": "New bug, no updates yet"
            },
            "t-yosemite-r7-229": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1477779",
                "date": "17.08.2018",
                "update": "Van to check it next DC visit"
            },
            "t-yosemite-r7-239": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1473791",
                "date": "06.08.2018",
                "update": "Taken to the apple store"
            },
        },
        "other_issues": {
            "t-yosemite-r7-072": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1478526",
                "date": "01.08.2018",
                "update": "requires on site visit"
            },
            "t-yosemite-r7-119": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1499119",
                "date": "16.10.2018",
                "update": "van will check it"
            },
            "t-yosemite-r7-175": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1485271",
                "date": "04.09.2018",
                "update": "van will check it next DC visit"
            },
            "t-yosemite-r7-201": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1477150",
                "date": "26.08.2018",
                "update": "host was renamed and repurposed"
            },
            "t-yosemite-r7-272": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1472845",
                "date": "27.07.2018",
                "update": "brought to the apple store"
            },
            "t-yosemite-r7-273": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494112",
                "date": "26.07.2018",
                "update": "https://bugzilla.mozilla.org/show_bug.cgi?id=1494112#c2"
            },
            "t-yosemite-r7-384": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1493101",
                "date": "23.09.2018",
                "update": "Van will check on his next DC visit"
            },
            "t-yosemite-r7-393": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1476396",
                "date": "05.10.2018",
                "update": "the machine has been repurposed"
            },
        },
    },
}


def build_host_info(hostnames, **kwargs):
    all_hosts = {}
    for hostname in hostnames:
        all_hosts.update({hostname: dict(kwargs)})
    return all_hosts


# Insert Linux from chassis 14 into the loan dictionary
machines_to_ignore['linux']['loaner'].update(
    build_host_info(["t-linux64-ms-{}".format(i) for i in range(571, 580)], bug="Loaner for Relops", owner="No Owner"))

workersList = []

LINUX = "gecko-t-linux-talos"
LINUXTW = "gecko-t-linux-talos-tw"
WINDOWS = "gecko-t-win10-64-hw"
MACOSX = "gecko-t-osx-1010"


def get_all_keys(*args):
    """Given a list of dictionaries, return a list of dictionary keys"""
    all_keys = []
    for d in args:
        all_keys.extend(list(d.keys()))
    return all_keys


def parse_taskcluster_json(workertype):
    '''
    We need this incase Auth fails.
    :param workertype: gecko-t-linux-talos, gecko-t-win10-64-hw, gecko-t-osx-1010.
    :return: A JSON file containing all workers for a workertype selected at runtime.
    '''

    # Setup API URLs
    if (workertype == LINUX) or (workertype == "linux"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-linux-talos/workers"


    elif (workertype == LINUXTW) or (workertype == "linuxtw"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-linux-talos-tw/workers"

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
                # Not sure why but TC kinda fails at responding or I'm doing something wrong
                # Anyways if you keep at it, it will respond with the JSON data :D
                print("Empty Worker List. Retrying...")
                parse_taskcluster_json(workertype)
            else:
                for workers in data['workers']:
                    workersList.append(workers['workerId'])

        except KeyboardInterrupt:
            print("Application stopped via Keyboard Shortcut.")
            exit(0)

    return workersList


def generate_machine_lists(workertype):
    global mdc1_range, mdc2_range  # We need them global so we can use them to generate the ssh command.
    if (workertype == LINUX) or (workertype == "linux"):
        mdc2_range = list(range(301, 316)) + list(range(346, 361)) + \
                     list(range(391, 406)) + list(range(436, 451)) + \
                     list(range(481, 496)) + list(range(526, 541)) + \
                     list(range(571, 581))

        #   list(range(301, 316)) + list(range(346, 361)) + \   All linux chassis (except 13) moved to talos-TW
        #          list(range(391, 406)) + list(range(436, 451)) + \
        #          list(range(481, 496)) +

        range_ms_linux = mdc2_range
        ms_linux_name = "t-linux64-ms-{}"
        linux_machines = []

        for i in range_ms_linux:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            linux_machines.append(ms_linux_name.format(digit_constructor))

        return linux_machines

    if (workertype == LINUXTW) or (workertype == "linuxtw"):
        mdc1_range = list(range(1, 16)) + list(range(46, 61)) + \
                     list(range(91, 106)) + list(range(136, 151)) + \
                     list(range(181, 196)) + list(range(226, 241)) + \
                     list(range(271, 280))

        range_ms_linux = mdc1_range  # when the machines from mdc2 category linux-tw will be re-added add here + mdc2_range_linuxtw
        ms_linux_name = "t-linux64-ms-{}"
        linux_machines = []

        for i in range_ms_linux:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            linux_machines.append(ms_linux_name.format(digit_constructor))

        return linux_machines

    if (workertype == WINDOWS) or (workertype == "win"):
        mdc1_range = list(range(16, 46)) + list(range(61, 91)) + \
                     list(range(106, 136)) + list(range(151, 181)) + \
                     list(range(196, 226)) + list(range(241, 271)) + \
                     list(range(281, 299))
        mdc2_range = list(range(316, 346)) + \
                     list(range(361, 391)) + list(range(406, 436)) + \
                     list(range(451, 481)) + list(range(496, 526)) + \
                     list(range(541, 571)) + list(range(581, 601))

        range_ms_windows = mdc1_range + mdc2_range

        ms_windows_name = "T-W1064-MS-{}"
        windows_machines = []

        for i in range_ms_windows:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            windows_machines.append(ms_windows_name.format(digit_constructor))
        return windows_machines

    if (workertype == MACOSX) or (workertype == "osx"):

        mdc2_range = list(range(21, 237))
        mdc1_range = list(range(237, 473))

        range_ms_osx = mdc2_range + mdc1_range  # No idea why macs MDC2 starts with the lower numbers.
        ms_osx_name = "t-yosemite-r7-{}"
        osx_machines = []

        for i in range_ms_osx:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            osx_machines.append(ms_osx_name.format(digit_constructor))
        return osx_machines

    else:
        print("Invalid Worker-Type!")
        exit(0)


def main():
    # Get/Set Arguments
    parser = ArgumentParser(description="Utility to check missing moonshots form TC.")
    parser.add_argument("-w", "--worker-type",
                        dest="worker_type",
                        help="Available options: gecko-t-linux-talos, linux, gecko-t-win10-64-hw, win, gecko-t-osx-1010, mac",
                        default=WINDOWS,
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

    if verbose:
        from prettytable import PrettyTable

    # Remove machines from generated list
    if (workertype == LINUX) or (workertype == "linux"):
        loaners = machines_to_ignore["linux"]["loaner"]
        pxe_issues = machines_to_ignore["linux"]["pxe_issues"]
        hdd_issues = machines_to_ignore["linux"]["hdd_issues"]
        ssh_stdio = machines_to_ignore["linux"]["ssh_stdio"]
        other_issues = machines_to_ignore["linux"]["other_issues"]
        ignore_all = list(get_all_keys(loaners, pxe_issues, hdd_issues, ssh_stdio, other_issues))

        if verbose:
            print("\nLinux Loaners:")
            if not loaners:
                print("No Linux Loaners")
            else:
                table = PrettyTable()
                table.field_names = ["Machine Name", "BUG ID", "Owner"]
                for machine in sorted(loaners.keys()):
                    table.add_row([machine, loaners[machine]['bug'], loaners[machine]['owner']])
                print(table)

            print("\nPXE Issues:")
            if not pxe_issues:
                print("No PXE Issues")
            else:
                pxe_table = PrettyTable()
                pxe_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for pxe in sorted(pxe_issues.keys()):
                    pxe_table.add_row([pxe, pxe_issues[pxe]['bug'], pxe_issues[pxe]['date'], pxe_issues[pxe]['update']])
                print(pxe_table)

            print("\nHDD Issues:")
            if not hdd_issues:
                print("No Linux with HDD Issues")
            else:
                hdd_table = PrettyTable()
                hdd_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for hdd in sorted(hdd_issues.keys()):
                    hdd_table.add_row([hdd, hdd_issues[hdd]['bug'], hdd_issues[hdd]['date'], hdd_issues[hdd]['update']])
                print(hdd_table)

            print("\nSSH-STDIO Issues:")
            if not ssh_stdio:
                print("No SSH-STDIO Issues")
            else:
                stdio_table = PrettyTable()
                stdio_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for stdio in sorted(ssh_stdio.keys()):
                    stdio_table.add_row(
                        [stdio, ssh_stdio[stdio]['bug'], ssh_stdio[stdio]['date'], ssh_stdio[stdio]['update']])
                print(stdio_table)

            print("\nOther Issues:")
            if not other_issues:
                print("No Linux under Other Issues")
            else:
                otherissues_table = PrettyTable()
                otherissues_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for issue in sorted(other_issues.keys()):
                    otherissues_table.add_row(
                        [issue, other_issues[issue]['bug'], other_issues[issue]['date'], other_issues[issue]['update']])
                print(otherissues_table)

        a = set(ignore_all)
        workers = [x for x in generate_machine_lists(workertype) if x not in a]

    if (workertype == LINUXTW) or (workertype == "linuxtw"):
        loaners = machines_to_ignore["linuxtw"]["loaner"]
        pxe_issues = machines_to_ignore["linuxtw"]["pxe_issues"]
        hdd_issues = machines_to_ignore["linuxtw"]["hdd_issues"]
        ssh_stdio = machines_to_ignore["linuxtw"]["ssh_stdio"]
        other_issues = machines_to_ignore["linuxtw"]["other_issues"]
        ignore_all = list(get_all_keys(loaners, pxe_issues, hdd_issues, ssh_stdio, other_issues))

        if verbose:
            print("\nLinux Loaners-TW:")
            if not loaners:
                print("No Linux Loaners-TW")
            else:
                table = PrettyTable()
                table.field_names = ["Machine Name", "BUG ID", "Owner"]
                for machine in sorted(loaners.keys()):
                    table.add_row([machine, loaners[machine]['bug'], loaners[machine]['owner']])
                print(table)

            print("\nPXE Issues-TW:")
            if not pxe_issues:
                print("No PXE Issues-TW")
            else:
                pxe_table = PrettyTable()
                pxe_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for pxe in sorted(pxe_issues.keys()):
                    pxe_table.add_row([pxe, pxe_issues[pxe]['bug'], pxe_issues[pxe]['date'], pxe_issues[pxe]['update']])
                print(pxe_table)

            print("\nHDD Issues-TW:")
            if not hdd_issues:
                print("No Linux with HDD Issues-TW")
            else:
                hdd_table = PrettyTable()
                hdd_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for hdd in sorted(hdd_issues.keys()):
                    hdd_table.add_row([hdd, hdd_issues[hdd]['bug'], hdd_issues[hdd]['date'], hdd_issues[hdd]['update']])
                print(hdd_table)

            print("\nSSH-STDIO Issues-TW:")
            if not ssh_stdio:
                print("No SSH-STDIO Issues-TW")
            else:
                stdio_table = PrettyTable()
                stdio_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for stdio in sorted(ssh_stdio.keys()):
                    stdio_table.add_row(
                        [stdio, ssh_stdio[stdio]['bug'], ssh_stdio[stdio]['date'], ssh_stdio[stdio]['update']])
                print(stdio_table)

            print("\nOther Issues-TW:")
            if not other_issues:
                print("No Linux under Other Issues-TW")
            else:
                otherissues_table = PrettyTable()
                otherissues_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for issue in sorted(other_issues.keys()):
                    otherissues_table.add_row(
                        [issue, other_issues[issue]['bug'], other_issues[issue]['date'], other_issues[issue]['update']])
                print(otherissues_table)

        a = set(ignore_all)
        workers = [x for x in generate_machine_lists(workertype) if x not in a]

    if (workertype == WINDOWS) or (workertype == "win"):
        loaners = machines_to_ignore["windows"]["loaner"]
        pxe_issues = machines_to_ignore["windows"]["pxe_issues"]
        hdd_issues = machines_to_ignore["windows"]["hdd_issues"]
        other_issues = machines_to_ignore["windows"]["other_issues"]
        ignore_all = list(get_all_keys(loaners, pxe_issues, hdd_issues, other_issues))

        if verbose:
            print("\nWindows Loaners:")
            if not loaners:
                print("No Windows Loaners")
            else:
                table = PrettyTable()
                table.field_names = ["Machine Name", "BUG ID", "Owner"]
                for machine in sorted(loaners.keys()):
                    table.add_row([machine, loaners[machine]['bug'], loaners[machine]['owner']])
                print(table)

            print("\nPXE Issues:")
            if not pxe_issues:
                print("No PXE Issues")
            else:
                pxe_table = PrettyTable()
                pxe_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for pxe in sorted(pxe_issues.keys()):
                    pxe_table.add_row([pxe, pxe_issues[pxe]['bug'], pxe_issues[pxe]['date'], pxe_issues[pxe]['update']])
                print(pxe_table)

            print("\nHDD Issues:")
            if not hdd_issues:
                print("No Windows with HDD Issues")
            else:
                hdd_table = PrettyTable()
                hdd_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for hdd in sorted(hdd_issues.keys()):
                    hdd_table.add_row([hdd, hdd_issues[hdd]['bug'], hdd_issues[hdd]['date'], hdd_issues[hdd]['update']])
                print(hdd_table)

            print("\nOther Issues:")
            if not other_issues:
                print("No Windows under Other Issues")
            else:
                otherissues_table = PrettyTable()
                otherissues_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for issue in sorted(other_issues.keys()):
                    otherissues_table.add_row(
                        [issue, other_issues[issue]['bug'], other_issues[issue]['date'], other_issues[issue]['update']])
                print(otherissues_table)

        a = set(ignore_all)
        workers = [x for x in generate_machine_lists(workertype) if x not in a]

    if (workertype == MACOSX) or (workertype == "osx"):
        loaners = machines_to_ignore["osx"]["loaner"]
        ssh_stdio = machines_to_ignore["osx"]["ssh_stdio"]
        ssh_unresponsive = machines_to_ignore["osx"]["ssh_unresponsive"]
        other_issues = machines_to_ignore["osx"]["other_issues"]
        ignore_all = list(get_all_keys(loaners, ssh_stdio, ssh_unresponsive, other_issues))

        if verbose:
            print("\nYosemite Loaners:")
            if not loaners:
                print("No Yosemite Loaners")
            else:
                table = PrettyTable()
                table.field_names = ["Machine Name", "BUG ID", "Owner"]
                for machine in sorted(loaners.keys()):
                    table.add_row([machine, loaners[machine]['bug'], loaners[machine]['owner']])
                print(table)

            print("\nSSH-STDIO Issues:")
            if not ssh_stdio:
                print("No SSH-STDIO Issues")
            else:
                stdio_table = PrettyTable()
                stdio_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for stdio in sorted(ssh_stdio.keys()):
                    stdio_table.add_row(
                        [stdio, ssh_stdio[stdio]['bug'], ssh_stdio[stdio]['date'], ssh_stdio[stdio]['update']])
                print(stdio_table)

            print("\nSSH-Unresponsive Issues:")
            if not ssh_unresponsive:
                print("No Yosemite with SSH Issues")
            else:
                unresponsive_table = PrettyTable()
                unresponsive_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for unresponsite in sorted(ssh_unresponsive.keys()):
                    unresponsive_table.add_row(
                        [unresponsite, ssh_unresponsive[unresponsite]['bug'], ssh_unresponsive[unresponsite]['date'],
                         ssh_unresponsive[unresponsite]['update']])
                print(unresponsive_table)

            print("\nOther Issues:")
            if not other_issues:
                print("No yosemite under Other Issues")
            else:
                otherissues_table = PrettyTable()
                otherissues_table.field_names = ["Machine Name", "BUG ID", "Date", "Update"]
                for issue in sorted(other_issues.keys()):
                    otherissues_table.add_row(
                        [issue, other_issues[issue]['bug'], other_issues[issue]['date'], other_issues[issue]['update']])
                print(otherissues_table)

        a = set(ignore_all)
        workers = [x for x in generate_machine_lists(workertype) if x not in a]

    b = set(workersList)
    missing_machines = [x for x in workers if x not in b]
    print("\n")
    print("Servers that WE know  of: {}".format(len(generate_machine_lists(workertype))))
    print("Servers that TC knows of: {}".format(len(workersList)))

    print("Total of missing server : {}".format(len(missing_machines)))

    if verbose:
        if len(workers) > len(generate_machine_lists(workertype)):
            print("!!! We got SCL3 Machines in the JSON body!!!! \n"
                  "!!! Ignoring all SCL3, Only MDC{1-2} machines are shown!!!!")

    # Print each machine on a new line.
    for machine in missing_machines:
        if (workertype == LINUX) or (workertype == "linux"):
            if verbose == "short":
                print(machine)
            else:
                if int(machine[-3:]) >= int(mdc2_range[0]):
                    print("ssh {}@{}.test.releng.mdc2.mozilla.com".format('root', machine))
                else:
                    print("ssh {}@{}.test.releng.mdc1.mozilla.com".format('root', machine))

        if (workertype == LINUXTW) or (workertype == "linuxtw"):
            if verbose == "short":
                print(machine)
            else:
                if int(machine[-3:]) >= int(mdc1_range[0]):
                    print("ssh {}@{}.test.releng.mdc1.mozilla.com".format('root', machine))

        if (workertype == WINDOWS) or (workertype == "win"):
            if verbose == "short":
                print(machine)
            else:
                if int(machine[-3:]) >= int(mdc2_range[0]):
                    print("ssh {}@{}.wintest.releng.mdc2.mozilla.com".format('Administrator', machine))
                else:
                    print("ssh {}@{}.wintest.releng.mdc1.mozilla.com".format('Administrator', machine))

        if (workertype == MACOSX) or (workertype == "osx"):
            if verbose == "short":
                print(machine)
            else:
                if int(machine[-3:]) <= int(mdc2_range[-1]):
                    print("ssh {}@{}.test.releng.mdc2.mozilla.com".format(ldap, machine))
                else:
                    print("ssh {}@{}.test.releng.mdc1.mozilla.com".format(ldap, machine))


if __name__ == '__main__':
    main()
