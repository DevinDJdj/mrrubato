
import json
import os
#allow to edit just the JSON file if this eventually gets packaged in some way eventually.  

if os.path.isfile("../config.json"):
    cfg = json.load(open("../config.json"))
#    print(cfg)
else:
    with open("config.json") as json_data_file:
        cfg = json.load(json_data_file)
    