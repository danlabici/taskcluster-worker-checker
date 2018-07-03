# taskcluster-worker-checker
## Ugly and rough script.

This is still being developed and will be getting clearner and easier to read.
If anything of value could be found here, maybe it would be the ranges for all OS types.

## How to run:

`python client.py -w gecko-t-osx-1010`

`python client.py -w gecko-t-linux-talos`

`python client.py -w gecko-t-win10-64-hw`


## How does it work?
1) We ask the user which worker-type hes interested into.
2) We generate a **CONTROL** list of names in a set range (eg: t-linux64-ms-280)
3) We get/parse the TC JSON for chosen worker-type
4) We print the diff between ListA and ListB
