'''A basic version of the TWC menu. I'll improve it in the next shifts.'''

import subprocess

file = open("banner.txt","r")
for line in file:
    print(line)
file.close()

def menu():       #the menu. 8 options
    print("\n1. Check for updates. ")
    print("2. Search for Linux. ")
    print("4. Search for Windows. ")
    print("5. Search for OSX. ")
    print("6. Search for all types of workers. ")
    print("7. Edit the script. ")
    print("8. Exit.\n")

menu()

while True:     #the 'switch:case' method to choose an option
    option = int(input("Choose an option: "))
    if option == 1:
        subprocess.call("git pull")
    elif option == 2:
        subprocess.call(['python', '../client.py', '-w', 'linux', '-v', 'true'])
    elif option == 3:
        subprocess.call(['python', '../client.py', '-w', 'win', '-v', 'true'])
    elif option == 4:
        subprocess.call(['python', '../client.py', '-w', 'osx', '-v', 'true'])
    elif option == 5:
        print("\n\n\nLinux: ")
        subprocess.call(['python', '../client.py', '-w', 'linux'])
        print("\n\n\nWindows: ")
        subprocess.call(['python', '../client.py', '-w', 'win'])
        print("\n\n\nOSX: ")
        subprocess.call(['python', '../client.py', '-w', 'osx'])
    elif option == 6:
        subprocess.call("nano ../client.py")
    elif option == 7:
        break
    else:
        print("Wrong option !")
    menu()


