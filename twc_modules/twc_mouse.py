from pynput.mouse import Listener


def on_click(*args):
    print("You have clicked at x:{}  y:{}".format(args[0], args[1]))
    return False


def mouse_listener(*args):
    print("Please click on {}".format(args))
    with Listener(on_click=on_click)as listener:
        listener.join()
        save_question(args)


def save_question(*args):
    print("Do you want to save current location for {}?\n"
          "1. Yes\n"
          "2. No".format(args))
    choise = int(input())
    if choise == 1:
        print("Location of '{}' saved.".format(args[0][0]))
        return False
    else:
        mouse_listener(*args)


mouse_listener()