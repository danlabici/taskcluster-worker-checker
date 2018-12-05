from argparse import ArgumentParser
import urllib.request, json

workersList = []

class CheckWorkers():
    def __init__(self, param):
        self.param = param
        self.linux = "gecko-t-linux-talos"
        self.windows = "gecko-t-win10-64-hw"
        self.macosx = "gecko-t-osx-1010"
        self.gen_machine_list = self.generate_machine_lists(self.param)
        self.missing_machines(self.param)
        
    def get_workers_list(self, val1):
        api = urllib.request.urlopen("https://queue.taskcluster.net/v1/provisioners/releng-hardware/worker-types/{}/workers".format(val1))
        data = json.loads(api.read().decode())
        if data['workers'] == []:
            print('Retrying....')
            self.get_workers_list(self.param)
        for workers in data['workers']:
            workersList.append(workers['workerId'])
        return workersList

    def generate_machine_lists(self, val1):
        try:
            if val1 == self.linux:
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
            if val1 == self.windows:
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
            if val1 == self.macosx:
                range_ms_osx = list(range(20, 237)) + list(range(237, 473))  # ToDo: Add real MacOS range.
                ms_osx_name = "t-yosemite-r7-{}"
                osx_machines = []
                for i in range_ms_osx:
                    digit_constructor = str(i).zfill(3)  # Generate numbers in 3 digits form, like: 001, 002, 003
                    osx_machines.append(ms_osx_name.format(digit_constructor))   # Mac Name + Number
                return osx_machines
        except val1 != LINUX or WINDOWS or MACOSX:
            print('Invalid worker type')
            exit(0)

    def missing_machines(self, input1):
        a = set(self.get_workers_list(input1))
        missing_machines = [x for x in self.generate_machine_lists(input1) if x not in a]
        print("\nControl Number: {}".format(len(self.generate_machine_lists(input1))))
        print("Number from TC JSON: {}\n".format(len(self.generate_machine_lists(input1)) - len(missing_machines)))
        print(missing_machines, "\n")

if __name__ == '__main__':
    parser = ArgumentParser(
        description="Utility to check missing moonshots form TC.")
    parser.add_argument('-w', '--worker-type',
                        dest="worker_type",
                        help='Available options: gecko-t-osx-1010, gecko-t-linux-talos, gecko-t-win10-64-hw',
                        default='gecko-t-linux-talos',
                        required=True)

    args = parser.parse_args()
    _wrkType = args.worker_type
    wrkList = _wrkType.split(",")
    for item in wrkList:
        CheckWorkers(item)