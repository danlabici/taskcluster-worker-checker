from pynput.mouse import Listener


def on_click(*args):
    print("You have clicked at x:{}  y:{}".format(args[0], args[1]))
    return False


def mouse_listener():
    with Listener(on_click=on_click)as listener:
        listener.join()


mouse_listener()