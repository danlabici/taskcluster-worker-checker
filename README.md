# taskcluster-worker-checker [![Build Status](https://travis-ci.com/Akhliskun/taskcluster-worker-checker.svg?branch=master)](https://travis-ci.com/Akhliskun/taskcluster-worker-checker)

This utility will check [TaskCluster](https://github.com/taskcluster) provisioner for [RelEng](https://github.com/mozilla-releng) hardware and will output in the terminal if any machine are missing.

# How to run the script:
## Instalation:
1) Make sure you have PrettyTable installed on your system, by running:

    `pip install prettytable` - Works on Linux, Mac, Windows (if python is installed).

2) Clone the repository and run client.py

## Running Client.py
| Windows  | Linux/Mac OSX |
| ------------- | ------------- |
| `python3 client.py -w linux` | `python3 client.py -w linux` |
| `python3 client.py -w win`  | `python3 client.py -w win`  |
| `python3 client.py -w osx`  | `python3 client.py -w osx`  |

If you preffer the output to be saved in a file, you can run the following command:

`python client.py -w WORKER_TYPE -u LDAP_USERNAME > missing.txt`

To get an output like this:
```
Servers that WE know  of: 200
Servers that TC knows of: 197
Total of missing server: 3
ssh LDAP@WORKER_TYPE.releng.DATACENTER.mozilla.com
ssh LDAP@WORKER_TYPE.releng.DATACENTER.mozilla.com
ssh LDAP@WORKER_TYPE.releng.DATACENTER.mozilla.com
```

You can also add the `-v True` or `--verbose True` to get extra information such as loaned machines and machines that have known issues. 
Output example with -v/--verbose:
```
Linux Loaners:
+------------------+---------------------------------------------------------------------+----------+
|   Machine Name   |                                BUG ID                               |  Owner   |
+------------------+---------------------------------------------------------------------+----------+
| t-linux64-ms-240 |                        Staging Pool - No Bug                        | :dragrom |
| t-linux64-ms-280 | Staging Pool - https://bugzilla.mozilla.org/show_bug.cgi?id=1464070 | :dragrom |
| t-linux64-ms-394 |                        Staging Pool - No Bug                        | :dragrom |
| t-linux64-ms-395 |                        Staging Pool - No Bug                        | :dragrom |
| t-linux64-ms-580 |         https://bugzilla.mozilla.org/show_bug.cgi?id=1474573        | :dev-env |
+------------------+---------------------------------------------------------------------+----------+
PXE Issues:
+--------------+--------+---------+-----------+
| Machine Name | BUG ID |   Date  |   Update  |
+--------------+--------+---------+-----------+
|   No Issue   | No BUG | No Date | No Update |
+--------------+--------+---------+-----------+
HDD Issues:
+--------------+--------+---------+-----------+
| Machine Name | BUG ID |   Date  |   Update  |
+--------------+--------+---------+-----------+
|   No Issue   | No BUG | No Date | No Update |
+--------------+--------+---------+-----------+
Other Issues:
+--------------+--------+---------+-----------+
| Machine Name | BUG ID |   Date  |   Update  |
+--------------+--------+---------+-----------+
|   No Issue   | No BUG | No Date | No Update |
+--------------+--------+---------+-----------+
Servers that WE know  of: 200
Servers that TC knows of: 195
Total of missing server : 0
```
Also, if you want to generate for all machines you can run:

`python3 client.py -w win && python3 client.py -w linux && python3 client.py -w osx`

or verbose (Attention, this will generate a lot of output):

`python3 client.py -w win -v True && python3 client.py -w linux -v True && python3 client.py -w osx -v True`

## How does it work?
1) Script will ask the user which worker-type he's interested into. Via run arguments.
    
    1.a) We also give the option to add his own Mozilla LDAP username. Making MacOSX workflow faster, by prefilling the ssh command with the needed information. 
2) We generate a **CONTROL** list of names in a set `hard-coded` range. [ISSUE - Grab machines from ServiceNow](https://github.com/Akhliskun/taskcluster-worker-checker/issues/2)
3) We get/parse the TC JSON for chosen worker-type. [ISSUE - Fix Failed JSON Responses](https://github.com/Akhliskun/taskcluster-worker-checker/issues/3)
4) We print the diff between ListA and ListB
4.1) We print the missing machines and ssh command, including your LDAP if offered.

## Can I contribute?
Yes! We have a couple of [Issues Open](https://github.com/Akhliskun/taskcluster-worker-checker/issues). 
Pick whichever you find fancy and make a PullRequest.
**PLEASE** don't forget to select "`Allow edits from maintainers`" so we can have quicker merges!

## Did I break anything?
This repository is running TravisCI to check each commit and pull request to make sure every change added to the script is playing nice. If you wanna check the status of a build, you can check our TravisCI repository page:

[LAST BUILD](https://travis-ci.com/Akhliskun/taskcluster-worker-checker) for live logs or [BUILD HISTORY](https://travis-ci.com/Akhliskun/taskcluster-worker-checker/builds) page.

## The code Explained:
`machines_to_ignore = {}` - Will be used to remove entries from the generated output. We don't want to see those!

`parse_taskcluster_json(workertype)` - Function that will parse the json data from from TC based on the worker-type which you choose. Will return the formated data. (eg: t-linux64-ms-280)

`generate_machine_lists(workertype)` - Function that will generate the control list. Better said, it will generate the machines which we know we should have in TC.

`main()` - Will ask for arguments + return the data to you in a readable format.


**PS**: We only look at MDC1/MDC2, even if TC JSON comes with SCL3, we ignore the "extra items". 
