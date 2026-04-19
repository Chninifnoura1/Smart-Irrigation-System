import requests
import time
import random

while True:
    temp = random.randint(20, 40)
    soil = random.randint(0, 100)

    data = {
        "temp": temp,
        "soil": soil
    }

    requests.post("http://127.0.0.1:5000/data", json=data)

    print("Envoyé:", data)

    time.sleep(2)