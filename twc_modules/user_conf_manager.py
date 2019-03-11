import json
import requests


def load_conf():
    try:
        with open("../user_settings.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        with requests.get("https://raw.githubusercontent.com/Akhliskun/taskcluster-worker-checker/master/user_settings.json") as file:
            return json.load(file.decode())



def write_conf(data):
    with open("../user_settings.json", "w+") as file:
        return json.dump(data, file, indent=2)


def ilo_path():
    data = load_conf()
    data.update({"reboot":
        {
            "ilo_app_location": "labici"
        }
    })
    return write_conf(data)


ilo_path()
