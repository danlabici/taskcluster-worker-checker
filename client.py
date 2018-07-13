"""
This script will check for missing moonshots in TaskCluster.
github repo: https://github.com/Akhliskun/taskcluster-worker-checker
"""

from argparse import ArgumentParser
import urllib.request, json

# Define machines that SHOULDN'T appear.
# Example: Machine is dev-env, loaner, etc.
# ToDo: Implement a function that checks if we have machines loaned.

ignore_ms_linux = ["t-linux64-ms-280",  # :dragrom
                   "t-linux64-ms-580"]  # :dev machine for relops

ignore_ms_windows = ["T-W1064-MS-010", "T-W1064-MS-011", "T-W1064-MS-012", "T-W1064-MS-013", "T-W1064-MS-014",  # GW10 testing
                     "T-W1064-MS-015", "T-W1064-MS-016", "T-W1064-MS-017", "T-W1064-MS-018", "T-W1064-MS-019",  # GW10 testing
                     "T-W1064-MS-020", "T-W1064-MS-021", "T-W1064-MS-022", "T-W1064-MS-023", "T-W1064-MS-024",  # GW10 testing
                     "T-W1064-MS-025", "T-W1064-MS-026", "T-W1064-MS-027", "T-W1064-MS-028", "T-W1064-MS-029",  # GW10 testing
                     "T-W1064-MS-030", "T-W1064-MS-031", "T-W1064-MS-032", "T-W1064-MS-033", "T-W1064-MS-034",  # GW10 testing
                     "T-W1064-MS-035", "T-W1064-MS-036", "T-W1064-MS-037", "T-W1064-MS-038", "T-W1064-MS-039",  # GW10 testing
                     "T-W1064-MS-040", "T-W1064-MS-041", "T-W1064-MS-042", "T-W1064-MS-043", "T-W1064-MS-044",  # GW10 testing
                     "T-W1064-MS-045", "T-W1064-MS-046", "T-W1064-MS-047", "T-W1064-MS-048", "T-W1064-MS-049",  # GW10 testing
                     "T-W1064-MS-050", "T-W1064-MS-051", "T-W1064-MS-052", "T-W1064-MS-053", "T-W1064-MS-054",  # GW10 testing
                     "T-W1064-MS-055", "T-W1064-MS-056", "T-W1064-MS-057", "T-W1064-MS-058", "T-W1064-MS-050",  # GW10 testing
                     "T-W1064-MS-060"]  # GW10 testing

ignore_ms_osx = ["t-yosemite-r7-380"]  # :dragrom
workersList = []

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
    if (workertype == LINUX) or (workertype == "linux"):
        global mdc1_range, mdc2_range  # We need them global so we can use them to generate the ssh command.
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

    args = parser.parse_args()
    workertype = args.worker_type
    ldap = args.ldap_username

    parse_taskcluster_json(workertype)

    # Remove loaners from generated list
    if (workertype == LINUX) or (workertype == "linux"):
        if not ignore_ms_linux:
            a = set(ignore_ms_linux)  # Mark workerlist to be compared to our list.
            workerlist_without_loaners = [x for x in generate_machine_lists(workertype) if x not in a]
            print("\nNo loaners for LINUX machines\n")
        else:
            a = set(ignore_ms_linux)  # Mark workerlist to be compared to our list.
            workerlist_without_loaners = [x for x in generate_machine_lists(workertype) if x not in a]
            print("\nTotal of loaned machines: {} \nName of machines loaned: {}\n".format(len(ignore_ms_linux), ignore_ms_linux))

    if (workertype == WINDOWS) or (workertype == "win"):
        if not ignore_ms_windows:
            a = set(ignore_ms_windows)  # Mark workerlist to be compared to our list.
            workerlist_without_loaners = [x for x in generate_machine_lists(workertype) if x not in a]
            print("\nNo loaners for WINDOWS machines\n")
        else:
            a = set(ignore_ms_windows)  # Mark workerlist to be compared to our list.
            workerlist_without_loaners = [x for x in generate_machine_lists(workertype) if x not in a]
            print("\nTotal of loaned machines: {} \nName of machines loaned: {}\n".format(len(ignore_ms_windows), ignore_ms_windows))

    if (workertype == MACOSX) or (workertype == "osx"):
        if not ignore_ms_osx:
            a = set(ignore_ms_osx)  # Mark workerlist to be compared to our list.
            workerlist_without_loaners = [x for x in generate_machine_lists(workertype) if x not in a]
            print("\nNo loaners for WINDOWS machines\n")
        else:
            a = set(ignore_ms_osx)  # Mark workerlist to be compared to our list.
            workerlist_without_loaners = [x for x in generate_machine_lists(workertype) if x not in a]
            print("\nTotal of loaned machines: {} \nName of machines loaned: {}\n".format(len(ignore_ms_osx), ignore_ms_osx))

    # Get the TC List of workers WITHOUT the loaners and make the diff.
    b = set(workersList)
    missing_machines = [x for x in workerlist_without_loaners if x not in b]
    print("Servers that WE know  of: {}".format(len(generate_machine_lists(workertype))))
    print("Servers that TC knows of: {}".format(len(workersList)))
    print("Total of missing server : {}".format(len(missing_machines)))

    if len(workersList) > len(generate_machine_lists(workertype)):
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
