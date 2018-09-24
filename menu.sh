#!/bin/sh
choice=""

while [ "$choice" != "q" ]
do
        cat Automation/banner.txt
        echo
        echo
        echo "Please choose an option:"
        echo
        echo "1) Update Checker"
        echo "2) Run Checker"
        echo "3) Run Checker verbose mode"
        echo "q) Quit"
        echo

        read choice

        case $choice in
            '1') git pull;;
            '2') clear
                Automation/./scanner.sh;;
            '3') clear
                Automation/./scanner-v.sh;;
            'q') echo "quiting!";;
            *)   echo "menu item is not available; try again!";;
        esac
done
