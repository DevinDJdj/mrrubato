
import sys
import json
import os
#allow to edit just the JSON file if this eventually gets packaged in some way eventually.  
#not great mechanism, but cant be bothered.  
global cfg
global cfg_path


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