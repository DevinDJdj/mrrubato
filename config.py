
import sys
import json
import os
#allow to edit just the JSON file if this eventually gets packaged in some way eventually.  
#not great mechanism, but cant be bothered.  
global cfg
global cfg_path
global custom_settings

if os.path.isfile(sys.path[0] + "/config.json"):
    cfg = json.load(open(sys.path[0] + "/config.json"))

elif os.path.isfile("../../config.json"):
    cfg = json.load(open("../../config.json"))
#    print(cfg)
elif os.path.isfile("../config.json"):
    cfg = json.load(open("../config.json"))
#    print(cfg)
else:
    with open("config.json") as json_data_file:
        cfg = json.load(json_data_file)


def init(fname):
    if os.path.isfile(fname):
        cfg = json.load(open(fname))
        print("config loaded from " + fname)
        return cfg

def load_custom_settings():
    global custom_settings
    if os.path.isfile(sys.path[0] + "/custom_settings.json"):
        custom_settings = json.load(open(sys.path[0] + "/custom_settings.json"))
    else:
        custom_settings = {}

def save_custom_settings():
    global custom_settings
    with open(sys.path[0] + "/custom_settings.json", "w") as json_file:
        json.dump(custom_settings, json_file, indent=4)

def get_data_folder():
    if sys.platform == "win32":
        return os.path.join(os.getenv('APPDATA'), 'Trey')
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Trey')
    else:
        return os.path.join(os.path.expanduser('~'), '.trey')