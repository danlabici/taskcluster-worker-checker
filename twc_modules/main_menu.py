from twc_modules import configuration
from client import run_logic, output_single_machine, output_loaned_machines, output_machines_with_notes

windows = configuration.WINDOWS
linux = configuration.LINUX
yosemite = configuration.YOSEMITE
all = configuration.ALLWORKERS

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
          "TWC version: {} || Github: https://github.com/Akhliskun/taskcluster-worker-checker\n".format(configuration.VERSION))
    if configuration.LAZY != 6:
        print("==== Custom Lazy Time of:", configuration.LAZY, " ====")
    if configuration.VERBOSE:
        print("==== Verbose Mode Activated  ====\n")

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
        if choice_menu1 == 1:
            run_logic(all)
            exit(0)
        if choice_menu1 == 2:
            run_logic(windows)
            exit(0)
        if choice_menu1 == 3:
            run_logic(linux)
            exit(0)
        if choice_menu1 == 4:
            run_logic(yosemite)
            exit(0)
        if choice_menu1 == 0:
            run_menu()

    if choice == 11:
        run_logic(all)
        exit(0)

    if choice == 12:
        run_logic(windows)
        exit(0)

    if choice == 13:
        run_logic(linux)
        exit(0)

    if choice == 14:
        run_logic(yosemite)
        exit(0)

    if choice == 2:
        print("Type the HostName to search for a specific machine.\n"
              "Example: t-yosemite-r7-240")
        single_machine = str(input())
        output_single_machine(single_machine)
        exit(0)

    if choice == 3:
        print("Loaned machines has two distinct options to run:\n"
              "With a name provided. Example: Q or davehouse\n"
              "Or you can simple press enter (don't input anything) and will list all the machines that are loaned")
        output_loaned_machines(loaner=input().lower())
        exit(0)

    if choice == 4:
        print("This function will print ALL machines with notes.\n"
              "Press ENTER to continue.")
        input()
        output_machines_with_notes()
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
