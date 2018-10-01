
import subprocess

file = open("../banner.txt","r")
for line in file:
    print(line)
file.close()

def menu():       #the menu. 8 options
    print("\n1. Update checker. ")
    print("2. Search for Linux. ")
    print("3. Search for Linux-TW. ")
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
        subprocess.call(['python', '../../client.py', '-w', 'linux', '-v', 'true'])
    elif option == 3:
        subprocess.call(['python', '../../client.py', '-w', 'linuxtw', '-v', 'true'])
    elif option == 4:
        subprocess.call(['python', '../../client.py', '-w', 'win', '-v', 'true'])
    elif option == 5:
        subprocess.call(['python', '../../client.py', '-w', 'osx', '-v', 'true'])
    elif option == 6:
        subprocess.call(['python', '../../client.py', '-w', 'linux'])
        subprocess.call(['python', '../../client.py', '-w', 'linuxtw'])
        subprocess.call(['python', '../../client.py', '-w', 'win'])
        subprocess.call(['python', '../../client.py', '-w', 'osx'])
    elif option == 7:
        subprocess.call("nano ../../client.py")
    elif option == 8:
        break
    else:
        print("Wrong option !")
    menu()
    

'''A basic version of the TWC menu. I'll improve it in the next shifts.'''