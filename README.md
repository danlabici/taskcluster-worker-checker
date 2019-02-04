# taskcluster-worker-checker [![Build Status](https://travis-ci.com/Akhliskun/taskcluster-worker-checker.svg?branch=master)](https://travis-ci.com/Akhliskun/taskcluster-worker-checker)

This utility will check [TaskCluster](https://github.com/taskcluster) provisioner for [RelEng](https://github.com/mozilla-releng) hardware and will output in the terminal if any machine are missing.

# How to run the script:
## Instalation:
1) Run the following command to install all missing dependencies:

`pip install -r requirements.txt`

2) Since `30 October 2018` the script will require you to manually add a json file which holds the credentials needed to connect to Google Drive.
The file is inside the `"secret repo/passwords/ciduty-twc.json"`.

If you don't know how to get access to this file, please ping anyone in **CiDuty** using **#ci**

3) Clone the repository and run client.py

## Running Client.py
| Windows                         | Linux/Mac OSX                  |   
| --------------------------------|--------------------------------|
|           `python client.py`    | `python3 client.py`            |


## Other Run Options:
Script doesn't mind the order in which you set the options/arguments.

`-v`  - Used to activate verbose mode. Script will output runtimes and vew extra columns in the end output.

`-l`  - Used to set custom Lazy timer. Default Lazy Timer is set to 6 hours. Usage: `-l 10` or `-l 2`

`-m`  - Used to skip the menu. For example `-m 14` will check OSX workers. `-m 2` will go to check a specific machine.

`-p`  - Used to set persistent menu.

`-o`  - Used to output the resulting table in a HTML file, called index.html

`-a`  - If `-o` is provided, the file will automatically open in your default browser.

`-rb` - Automatically reboots the Moonshots (Windows/Linux). You will need iLO to present on the PC. __**Works only on WINDOWS host machines!**__

`-ct` - Used to set flag for TravisCI testing.



## How does it work?
1) Script will ask the user which worker-type he's interested into.
2) We get the machine data from [RelEnd-Hardware](https://releng-hardware.herokuapp.com/machines)
3) We parse the information from Moonshots Master Inventory spreadsheet (visible only to select people, but all data from it is saved inside TWC and you can use it freely)
4) We print the machines which, by default, are IDLE/Lazy for `6 hours` or longer.
5) And finally, Output the data.

## Can I contribute?
Yes! We have a couple of [Issues Open](https://github.com/Akhliskun/taskcluster-worker-checker/issues).
Pick whichever you find fancy and make a PullRequest.

## Did I break anything?
This repository is running TravisCI to check each commit and pull request to make sure every change added to the script is playing nice. If you wanna check the status of a build, you can check our TravisCI repository page:

[LAST BUILD](https://travis-ci.com/Akhliskun/taskcluster-worker-checker) for live logs or [BUILD HISTORY](https://travis-ci.com/Akhliskun/taskcluster-worker-checker/builds) page.

`NOTE:` If you work on a fork, `for security reasons` TravisCI will not have access to the encrypted credentials stored inside `ciduty-twc.json.enc`
