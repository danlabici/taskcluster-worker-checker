"""
This script will check for missing moonshots in TaskCluster.
github repo: https://github.com/Akhliskun/taskcluster-worker-checker
"""

from argparse import ArgumentParser
import urllib.request, json

# Define machines that SHOULDN'T appear.
# Example: Machine is dev-env, loaner, or has known problems etc.
machines_to_ignore = {
    "linux": {
        "loaner": {
            "t-linux64-ms-280": {
                "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1464070", 
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
                "date": "No Owner", 
                "update": "No Owner"
            },
        },

        "hdd_issues": {
            "No Issue": {
                "bug": "No BUG", 
                "date": "No Owner", 
                "update": "No Owner"
            },
        },
        "other_issues": {
            "No Issue": {"bug": "No BUG", "date": "No Owner", "update": "No Owner"}
        },
    },
    "windows": {
        "loaner": {
        },
        "pxe_issues": {
            "T-W1064-MS-281": ["https://bugzilla.mozilla.org/show_bug.cgi?id=1465753", "13.07.2018",
                               "https://bugzilla.mozilla.org/show_bug.cgi?id=1465753#c6"],
            "T-W1064-MS-338": ["", "15.07.2018", "New bug, no updates yet."]  # TODO: Make bug!
        },
        "hdd_issues": {
            "T-W1064-MS-071": ["https://bugzilla.mozilla.org/show_bug.cgi?id=1475905", "15.07.2018",
                               "New bug, no updates yet."],
            "T-W1064-MS-261": ["https://bugzilla.mozilla.org/show_bug.cgi?id=1475906", "15.07.2018",
                               "New bug, no updates yet."],
            "T-W1064-MS-291": ["https://bugzilla.mozilla.org/show_bug.cgi?id=1475908", "15.07.2018",
                               "New bug, no updates yet."]
        },
        "other_issues": {
            "T-W1064-MS-072": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "T-W1064-MS-130": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "T-W1064-MS-177": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "T-W1064-MS-178": ["", "15.07.2018", "New bug, no updates yet."]  # TODO: Make bug!
        },
    },
    "osx": {
        "loaner": {
            "t-yosemite-r7-380": ["Forever-Loaned", ":dragrom"]
        },
        "ssh_stdio": {
            "t-yosemite-r7-055": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-061": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-151": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-186": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-322": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-356": ["", "15.07.2018", "New bug, no updates yet."]  # TODO: Make bug!
        },
        "ssh_unresponsive": {
            "t-yosemite-r7-078": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-124": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-130": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-263": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-267": ["", "15.07.2018", "New bug, no updates yet."],  # TODO: Make bug!
            "t-yosemite-r7-357": ["", "15.07.2018", "New bug, no updates yet."]  # TODO: Make bug!
        },
        "other_issues": {
            "t-yosemite-r7-442": ["", "15.07.2018", "New bug, no updates yet."]  # TODO: Make bug!
        },
    },
}


def build_host_info(hostnames, **kwargs):
    all_hosts = {}
    for hostname in hostnames:
        all_hosts.update({hostname: dict(kwargs)})
    return all_hosts

# Insert Windows 10 to 60 into the dictionary.
machines_to_ignore['windows']['loaner'].update(
    build_host_info(["T-W1064-MS-0{}".format(i) for i in range(10, 61)], bug="Dev-Environment", date="No date",
                    update="Find Bug Comment"))

workersList = []

LINUX = "gecko-t-linux-talos"
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

    elif (workertype == WINDOWS) or (workertype == "win"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-win10-64-hw/workers"

    elif (workertype == MACOSX) or (workertype == "osx"):
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-osx-1010/workers"

    else:
        print("ERROR: Unknown worker-type!")
        print("Please run the script with the [client.py -h] to see the help docs!")
        exit(0)

    with urllib.request.urlopen(apiUrl) as api:
        try:
            data = json.loads(api.read().decode())
        except:
            print("ERROR: Couldn't read and/or decode the JSON!")

        if not data["workers"]:
            # Not sure why but TC kinda fails at responding or I'm doing something wrong
            # Anyways if you keep at it, it will respond with the JSON data :D
            print("JSON Response Failed. Retrying...")
            parse_taskcluster_json(workertype)

        else:
            for workers in data['workers']:
                workersList.append(workers['workerId'])

    return workersList


def generate_machine_lists(workertype):
    global mdc1_range, mdc2_range  # We need them global so we can use them to generate the ssh command.
    if (workertype == LINUX) or (workertype == "linux"):
        mdc1_range = list(range(1, 16)) + list(range(46, 61)) + \
                     list(range(91, 106)) + list(range(136, 151)) + \
                     list(range(181, 196)) + list(range(226, 241)) + \
                     list(range(271, 281))

        mdc2_range = list(range(301, 316)) + list(range(346, 361)) + \
                     list(range(391, 406)) + list(range(436, 451)) + \
                     list(range(481, 496)) + list(range(526, 541)) + \
                     list(range(571, 581))

        range_ms_linux = mdc1_range + mdc2_range
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

        range_ms_windows = mdc1_range  # Ignoring MDC2 for now. ToDo: Do we have a BUG for mdc2 Win10?

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
                        required=True)
    parser.add_argument("-u", "--ldap-username",
                        dest="ldap_username",
                        help="Example: -u dlabici -- Don't include @mozilla.com!!",
                        default="LDAP",
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
        loaners = machines_to_ignore["linux"]["loaner"]
        pxe_issues = machines_to_ignore["linux"]["pxe_issues"]
        hdd_issues = machines_to_ignore["linux"]["hdd_issues"]
        other_issues = machines_to_ignore["linux"]["other_issues"]
        ignore_all = list(get_all_keys(loaners, pxe_issues, hdd_issues, other_issues))

        if verbose:
            print("Linux Loaners:")
            if not loaners:
                print("No Linux Loaners")
            else:
                for machine in sorted(loaners.keys()):
                    print("Name: {} \t BUG: {} \t Owner: {}".format(machine, loaners[machine]['bug'], loaners[machine]['owner']))

            print("\nPXE Issues:")
            if not pxe_issues:
                print("No PXE Issues")
            else:
                for pxe in sorted(pxe_issues.keys()):
                    print("Name: {} \t BUG: {} \t Date: {} \t Last Update: {}".format(pxe, pxe_issues[pxe]['bug'],
                                                                                          pxe_issues[pxe]['date'],
                                                                                          pxe_issues[pxe]['update']))

            print("\nHDD Issues:")
            if not hdd_issues:
                print("No Linux with HDD Issues")
            else:
                for hdd in sorted(hdd_issues.keys()):
                    print("Name: {} \t BUG: {} \t Date: {} \t Last Update: {}".format(hdd, hdd_issues[hdd]['bug'],
                                                                                      hdd_issues[hdd]['date'],
                                                                                      hdd_issues[hdd]['update']))

            print("\nOther Issues:")
            if not other_issues:
                print("No Linux under Other Issues")
            else:
                for issue in sorted(other_issues.keys()):
                    print("Name: {} \t BUG: {} \t Date: {} \t Last Update: {}".format(issue, other_issues[issue]['bug'],
                                                                                      other_issues[issue]['date'],
                                                                                      other_issues[issue]['update']))
        a = set(ignore_all)
        workers = [x for x in generate_machine_lists(workertype) if x not in a]

    # if (workertype == WINDOWS) or (workertype == "win"):
    #     if not ignore_ms_windows:
    #         a = set(ignore_ms_windows)
    #         workers = [x for x in generate_machine_lists(workertype) if x not in a]
    #         if verbose:
    #             print("\nNo loaners for WINDOWS machines\n")
    #     else:
    #         a = set(ignore_ms_windows)
    #         workers = [x for x in generate_machine_lists(workertype) if x not in a]
    #         if verbose:
    #             print("\nTotal of loaned machines: {} \nName of machines loaned:\n{}\n".format(len(ignore_ms_windows),
    #                                                                                            ignore_ms_windows))
    #
    # if (workertype == MACOSX) or (workertype == "osx"):
    #     if not ignore_ms_osx:
    #         a = set(ignore_ms_osx)
    #         workers = [x for x in generate_machine_lists(workertype) if x not in a]
    #         if verbose:
    #             print("\nNo loaners for WINDOWS machines\n")
    #     else:
    #         a = set(ignore_ms_osx)
    #         workers = [x for x in generate_machine_lists(workertype) if x not in a]
    #         if verbose:
    #             print("\nTotal of loaned machines: {} \nName of machines loaned:\n{}\n".format(len(ignore_ms_osx),
    #                                                                                            ignore_ms_osx))

    c = set(workersList)
    missing_machines = [x for x in workers if x not in c]
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
            print("{}".format(machine))

        if (workertype == WINDOWS) or (workertype == "win"):
            print("{}".format(machine))

        if (workertype == MACOSX) or (workertype == "osx"):
            if int(machine[-3:]) <= int(mdc2_range[-1]):
                print("ssh {}@{}.test.releng.mdc2.mozilla.com".format(ldap, machine))
            else:
                print("ssh {}@{}.test.releng.mdc1.mozilla.com".format(ldap, machine))


if __name__ == '__main__':
    main()
