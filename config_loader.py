import os, json
import pickle

CONFIG_FILE = 'config.json'

def get(key):
    return json.loads(open(CONFIG_FILE).read())[key]