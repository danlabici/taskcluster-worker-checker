# taskcluster-worker-checker [![Build Status](https://travis-ci.com/Akhliskun/taskcluster-worker-checker.svg?branch=master)](https://travis-ci.com/Akhliskun/taskcluster-worker-checker)

This utility will check [TaskCluster](https://github.com/taskcluster) provisioner for [RelEng](https://github.com/mozilla-releng) hardware and will output in the terminal if any machine are missing.

## How to run the script:

`python3 client.py -w linux` or `python3 client.py -w gecko-t-linux-talos`

`python3 client.py -w win` or `python3 client.py -w gecko-t-win10-64-hw`

`python3 client.py -w osx` or `python3 client.py -w gecko-t-osx-1010`

Or you can run this:
`python3 client.py -w WORKER_TYPE -u LDAP_USERNAME | cat >> missing.txt`
To get an output like this:
```
Total of loaned machines: 2
Name of machines loaned: [list_of_loaned_machines]

Servers that WE know  of: 200
Servers that TC knows of: 197
Total of missing server: 3
ssh LDAP@WORKER_TYPE.releng.DATACENTER.mozilla.com
ssh LDAP@WORKER_TYPE.releng.DATACENTER.mozilla.com
ssh LDAP@WORKER_TYPE.releng.DATACENTER.mozilla.com
```


## How does it work?
1) We ask the user which worker-type he's interested into.
1.a) We also give him the option to add his own Mozilla LDAP username.
2) We generate a **CONTROL** list of names in a set `hard-coded` range. [ISSUE - Grab machines from ServiceNow](https://github.com/Akhliskun/taskcluster-worker-checker/issues/2)
3) We get/parse the TC JSON for chosen worker-type. [ISSUE - Fix Failed JSON Responses](https://github.com/Akhliskun/taskcluster-worker-checker/issues/3)
4) We print the diff between ListA and ListB
4.1) We print the ssh command, including your LDAP if offered.

## Can I contribute?
Yes! We have a couple of [Issues Open](https://github.com/Akhliskun/taskcluster-worker-checker/issues). 
Pick whichever you find fancy and make a PullRequest.
**PLEASE** don't forget to select "`Allow edits from maintainers`" so we can have quicker merges!

## Did I break anything?
This repository is running TravisCI to check each commit and pull request to make sure every change added to the script is playing nice. If you wanna check the status of a build, you can check our TravisCI repository page:

[LAST BUILD](https://travis-ci.com/Akhliskun/taskcluster-worker-checker) for live logs or [BUILD HISTORY](https://travis-ci.com/Akhliskun/taskcluster-worker-checker/builds) page.

## The code Explained:
`ignore_ms_{linux,windows,osx}` - Will be used to remove entries from the generated output. We don't want to see those!

`parse_taskcluster_json(workertype)` - Function that will parse the json data from from TC based on the worker-type which you choose. Will return the formated data. (eg: t-linux64-ms-280)

`generate_machine_lists(workertype)` - Function that will generate the control list. Better said, it will generate the machines which we know we should have in TC.

`main()` - Will ask for arguments + return the data to you in a readable format.



**PS**: We only look at MDC1/MDC2, even if TC JSON comes with SCL3, we ignore the "extra items". 

You gotta love `set()` :D
