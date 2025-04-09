import time
import requests
import random
from utils.send_message import send_message
import keyboard

snapshots = {}

def worker(site):
    try:
        data = requests.get(site.url)
        
        if site.id in snapshots and not data.text == snapshots[site.id]:
            send_message(site)

        snapshots[site.id] = data.text

    except Exception as e:
        print(e)
