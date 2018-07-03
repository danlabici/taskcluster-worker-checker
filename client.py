"""
This script will check for missing moonshots in TaskCluster.
"""

from argparse import ArgumentParser
import urllib.request, json, pdb

# Define machines that SHOULDN'T appear.
# Example: Machine is dev-env, loaner, etc.
# ToDo: Implement a function that checks if we have machines loaned.
ignore_ms_linux = None
ignore_ms_windows = None
ignore_ms_osx = None
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
    global apiUrl, data
    if workertype == LINUX:
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-linux-talos/workers"

    elif workertype == WINDOWS:
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-win10-64-hw/workers"

    elif workertype == MACOSX:
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-osx-1010/workers"

    else:
        print("Unknown workertype!")
        exit(0)

    with urllib.request.urlopen(apiUrl) as api:
        try:
            data = json.loads(api.read().decode())
        except:
            print('Error found. Aborting ship!')

        if data["workers"] == []:
            # Not sure why but TC kinda fails at responding or I'm doing something wrong
            # Anyways if you keep at it, it will respond with the JSON data :D
            print("Auth Failed")
            parse_taskcluster_json(workertype)

        else:
            for workers in data['workers']:
                workersList.append(workers['workerId'])

    return workersList


def generate_machine_lists(workertype):
    if workertype == LINUX:

        range_ms_linux = list(range(1, 16)) + list(range(46, 61)) + \
                         list(range(91, 106)) + list(range(136, 151)) + \
                         list(range(181, 196)) + list(range(226, 241)) + \
                         list(range(271, 281)) + list(range(301, 316)) + \
                         list(range(346, 361)) + list(range(391, 406)) + \
                         list(range(436, 451)) + list(range(481, 496)) + \
                         list(range(526, 541)) + list(range(571, 581))
        ms_linux_name = "t-linux64-ms-{}"
        linux_machines = []

        # Construct Linux Machine names.
        for i in range_ms_linux:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            linux_machines.append(ms_linux_name.format(digit_constructor))  # Linux Name + Number

        return linux_machines

    elif workertype == WINDOWS:

        range_ms_windows = list(range(16, 46)) + list(range(61, 91)) + \
                         list(range(106, 136)) + list(range(151, 181)) + \
                         list(range(196, 226)) + list(range(241, 271)) + \
                         list(range(281, 299)) + list(range(316, 346)) + \
                         list(range(361, 391)) + list(range(406, 436)) + \
                         list(range(451, 481)) + list(range(496, 526)) + \
                         list(range(541, 571)) + list(range(581, 601))
        ms_windows_name = "T-W1064-MS-{}"
        windows_machines = []

        # Construct Windows Machine names.
        for i in range_ms_windows:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            windows_machines.append(ms_windows_name.format(digit_constructor))  # Windows Name + Number
        return windows_machines

    elif workertype == MACOSX:

        range_ms_osx = list(range(20, 237)) + list(range(237, 473))  # ToDo: Add real MacOS range.
        ms_osx_name = "t-yosemite-r7-{}"
        osx_machines = []

        # Construct OSX Machine names.
        for i in range_ms_osx:
            digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
            osx_machines.append(ms_osx_name.format(digit_constructor))   # Mac Name + Number
        return osx_machines

    else:
        print("Invalid Worker-Type!")
        exit(0)


def main():
    # Get/Set Arguments
    global apiUrl, data
    parser = ArgumentParser(
        description="Utility to check missing moonshots form TC.")
    parser.add_argument('-w', '--worker-type',
                        dest="worker_type",
                        help='Available options: gecko-t-osx-1010, gecko-t-linux-talos, gecko-t-win10-64-hw',
                        required=True)

    args = parser.parse_args()
    workertype = args.worker_type

    # Generate API URL
    if workertype == LINUX:
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-linux-talos/workers"
    elif workertype == WINDOWS:
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-win10-64-hw/workers"
    elif workertype == MACOSX:
        apiUrl = "https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-osx-1010/workers"
    else:
        print("Wrong workertype!")
        exit(1)

    with urllib.request.urlopen(apiUrl) as api:
        try:
            data = json.loads(api.read().decode())
        except:
            print('Error found. Aborting ship!')
        # Retry to Auth problems
        if data["workers"] == []:
            print("Auth Failed")
            parse_taskcluster_json(workertype)
        else:
            for workers in data['workers']:
                workersList.append(workers['workerId'])

    a = set(workersList)  # Mark workerlist to be compared to our list.
    missing_machines = [x for x in generate_machine_lists(workertype) if x not in a]
    print("Control Number: {}".format(len(generate_machine_lists(workertype))))
    print("Number from TC JSON: {}".format(len(workersList)))
    print(missing_machines)
    return workertype


if __name__ == '__main__':
    main()
