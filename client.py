import requests
import time
import random
import csv
import os
import numpy as np

CSV_FILE = "data.csv"

def generate_score(temp, humidity, fertility):
    score = 0
    if 20 <= temp <= 30:       score += 35
    elif 15 <= temp <= 35:     score += 20
    elif 10 <= temp <= 38:     score += 10

    if 40 <= humidity <= 70:   score += 35
    elif 30 <= humidity <= 80: score += 20
    elif 20 <= humidity <= 90: score += 10

    score += int(fertility * 0.30)
    score += random.gauss(0, 2)
    return round(float(np.clip(score, 0, 100)), 1)

# Init CSV
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Temp", "Humidity", "Fertility", "Score"])

print("🚀 Sender démarré — envoi toutes les 2 secondes...\n")

while True:
    temp      = round(random.uniform(10, 45), 1)
    humidity  = round(random.uniform(10, 100), 1)
    fertility = round(random.uniform(0, 100), 1)
    score     = generate_score(temp, humidity, fertility)

    # Sauvegarde CSV locale
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([temp, humidity, fertility, score])

    # Envoi Flask
    try:
        res = requests.post("http://127.0.0.1:5000/data", json={
            "temp": temp,
            "humidity": humidity,
            "fertility": fertility,
            "score": score
        }, timeout=3)
        status = "✅" if res.status_code == 200 else "⚠️"
        print(f"{status} Temp:{temp}°C | Humidity:{humidity}% | Fertility:{fertility}% | Score:{score}%")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    time.sleep(2)