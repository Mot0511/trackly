import time
import requests
import random
from utils.send_message import send_message

snapshots = {}

def worker(site):
    try:
        data = requests.get(site.url, headers={'Referer': site.url})
        
        if site.id in snapshots and not data.text == snapshots[site.id]:
            print('Отправка сообщения')
            send_message(site)

        snapshots[site.id] = data.text

    except Exception as e:
        print(e)
