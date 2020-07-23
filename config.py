#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

loads = json.loads
load = json.load
dumps = json.dumps
dump = json.dump

config_file = ""

CONFIG = {}

def load_config():
    global CONFIG
    with open(config_file, 'r') as configfile:
        CONFIG = load( configfile )
    return CONFIG

def save_config():
    with open(config_file, 'w') as configfile:
        dump(CONFIG, configfile, indent=4)

def setdefault():
    CONFIG.setdefault("Feedback",False)
    CONFIG.setdefault("Update_shell","")
    CONFIG.setdefault("Restart_shell","")
    save_config()