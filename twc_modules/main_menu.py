from twc_modules.configuration import VERSION
from client import run_all_machines, run_windows_machines, run_linux_machines, run_yosemite_machines


def run_menu(*arg):
    """
    - Check Machine(s) Status
    |-- Check ALL WorkerTypes.
    |-- Check Only Windows machines
    |-- Check Only Linux machines
    |-- Check Only Yosemite machines

    - Check a Specific Machine

    - Check machines Loaned by user
    -- input(ldap)

    - List all Machines with added Notes.
    """
    print("Welcome to CiDuty's TaskCluster Worker Checker.\n"
          "You can use the options below to investigate the machines which you want.\n"
          "TWC version: {} || Github: https://github.com/Akhliskun/taskcluster-worker-checker\n".format(VERSION))
    print("1. Check Machine(s) Status\n"
          "2. Check a Specific Machine\n"
          "3. List Machines Loaned by User\n"
          "4. List Machines with Added Notes\n"
          "5. TaskCluster Worker Checker HELP Docs\n\n"
          "0. Exit application.")
    try:
        choice = int(input())
    except ValueError:
        print("\n\nInvalid Choice!\n"
              "Restarting script!\n\n")
        run_menu()

    if choice == 1:
        print("1. Check ALL WorkerTypes\n"
              "2. Check ONLY Windows Machines\n"
              "3. Check ONLY Linux Machines\n"
              "4. Check ONLY Yosemite Machines\n\n"
              "0. Go Back.")
        try:
            choice_menu1 = int(input())
        except ValueError:
            print("\n\nInvalid Choice!\n")
            run_menu()
        if choice == 1:
            run_all_machines()
            exit(0)
        if choice_menu1 == 2:
            run_windows_machines()
        if choice_menu1 == 3:
            run_linux_machines()
        if choice_menu1 == 4:
            run_yosemite_machines()
        if choice_menu1 == 0:
            run_menu()

    if choice == 11:
        run_all_machines()
    if choice in range(12, 16):
        print("Logic not implemented yet!")
        exit(0)

    if choice == 2:
        print("Logic not implemented yet!")
        exit(0)

    if choice == 3:
        print("Logic not implemented yet!")
        exit(0)

    if choice == 4:
        print("Logic not implemented yet!")
        exit(0)

    if choice == 5:
        print("Logic not implemented yet!")
        exit(0)

    if choice == 0:
        print("Closing CLI application.\n")
        exit()
    else:
        print("\n\nInvalid Choice!\n"
              "Restarting script!\n\n")
        run_menu()
