from argparse import ArgumentParser
import urllib.request, json

workersList = []

LINUX = "gecko-t-linux-talos"
WINDOWS = "gecko-t-win10-64-hw"
MACOSX = "gecko-t-osx-1010"

def linux_api():
    try:
        api = urllib.request.urlopen("https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-linux-talos/workers")
        data = json.loads(api.read().decode())
    except data['workers'] == []:
        print('Retrying....')
        linux_api()
    return data

def windows_api():
    try:
        api = urllib.request.urlopen("https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-win10-64-hw/workers")
        data = json.loads(api.read().decode())
    except data['workers'] == []:
        print('Retrying....')
        linux_api()
    return data

def mac_api():
    try:
        api =urllib.request.urlopen("https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/gecko-t-osx-1010/workers")
        data = json.loads(api.read().decode())
    except data['workers'] == []:
        print('Retrying....')
        linux_api()
    return data

def build_TC_worker_list(inputVal):
    for workers in inputVal['workers']:
        workersList.append(workers['workerId'])
    return workersList

def generate_machine_lists(workertype):
    try:
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
            for i in range_ms_linux:
                digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
                linux_machines.append(ms_linux_name.format(digit_constructor))  # Linux Name + Number
            return linux_machines
        if workertype == WINDOWS:
            range_ms_windows = list(range(16, 46)) + list(range(61, 91)) + \
                             list(range(106, 136)) + list(range(151, 181)) + \
                             list(range(196, 226)) + list(range(241, 271)) + \
                             list(range(281, 299)) + list(range(316, 346)) + \
                             list(range(361, 391)) + list(range(406, 436)) + \
                             list(range(451, 481)) + list(range(496, 526)) + \
                             list(range(541, 571)) + list(range(581, 601))
            ms_windows_name = "T-W1064-MS-{}"
            windows_machines = []
            for i in range_ms_windows:
                digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
                windows_machines.append(ms_windows_name.format(digit_constructor))  # Windows Name + Number
            return windows_machines
        if workertype == MACOSX:
            range_ms_osx = list(range(20, 237)) + list(range(237, 473))  # ToDo: Add real MacOS range.
            ms_osx_name = "t-yosemite-r7-{}"
            osx_machines = []
            for i in range_ms_osx:
                digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
                osx_machines.append(ms_osx_name.format(digit_constructor))   # Mac Name + Number
            return osx_machines
    except workertype != LINUX or WINDOWS or MACOSX:
        print('Invalid worker type')
        exit(0)

def missing_machines(input1, input2):
    if input1 == 'LINUX':
        a = set(linux_api())
    if input1 == 'WINDOWS':
        a = set(windows_api())
    if input1 == 'MACOSX':
        a = set(mac_api())
    missing_machines = [x for x in generate_machine_lists(input2) if x not in a]
    return missing_machines

if __name__ == '__main__':
    parser = ArgumentParser(
        description="Utility to check missing moonshots form TC.")
    parser.add_argument('-w', '--worker-type',
                        dest="worker_type",
                        help='Available options: gecko-t-osx-1010, gecko-t-linux-talos, gecko-t-win10-64-hw',
                        default='gecko-t-linux-talos',
                        required=False)

    parser.add_argument('-o', '--os-type', dest='os_type',
                        default='LINUX',
                        required=False)

    args = parser.parse_args()
    _wrkType = args.worker_type
    _os_type = args.os_type

    _missing_machines = missing_machines(_os_type, _wrkType)
    _generate_machine_list = generate_machine_lists(_wrkType)
    print("Control Number: {}".format(len(_generate_machine_list)))
    print("Number from TC JSON: {}".format(len(_missing_machines)))
    print(_missing_machines)
