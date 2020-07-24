#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os

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
    (filepath,filename) = os.path.split(config_file)
    folder = os.path.exists(filepath)
    if not folder:
        os.makedirs(filepath)
        
    with open(config_file, 'w') as configfile:
        dump(CONFIG, configfile, indent=4,ensure_ascii=False)

def setdefault():
    CONFIG.setdefault("Feedback",False)
    CONFIG.setdefault("Update_shell","")
    CONFIG.setdefault("Restart_shell","")
    CONFIG.setdefault("Feedback_alert",False)
    CONFIG.setdefault("Feedback_text","")
    CONFIG.setdefault("Feedback_answer","")
    save_config()

def get_json():
    return dumps(CONFIG,indent=4,ensure_ascii=False)