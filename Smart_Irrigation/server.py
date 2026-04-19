from flask import Flask, request
import csv
import os

app = Flask(__name__)

# créer CSV s'il n'existe pas
if not os.path.exists("data.csv"):
    with open("data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Temp", "Soil"])

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json

    temp = data.get("temp")
    soil = data.get("soil")

    with open("data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([temp, soil])

    print("Reçu :", temp, soil)

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)