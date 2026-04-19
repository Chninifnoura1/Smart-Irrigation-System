from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import csv
import os
import pickle
import numpy as np
import json   
app = Flask(__name__)
app.secret_key = "cle_secrete_dyal_projet"

pump = "OFF"
mode = "AUTO"

# ─────────────────────────────────────────
# 🧠 Charger le vrai modèle ML
# ─────────────────────────────────────────
MODEL_LOADED = False
model, scaler_X, scaler_y = None, None, None

def load_model():
    global model, scaler_X, scaler_y, MODEL_LOADED
    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("scaler_X.pkl", "rb") as f:
            scaler_X = pickle.load(f)
        with open("scaler_y.pkl", "rb") as f:
            scaler_y = pickle.load(f)
        MODEL_LOADED = True
        print("✅ Modèle ML chargé avec succès !")
    except FileNotFoundError:
        MODEL_LOADED = False
        print("⚠️  model.pkl introuvable — lance d'abord : python train_model.py")

load_model()
# ── En haut du fichier, après les autres imports ──
import json

# ── Après load_model(), ajoute le chargement du recommender ──
RECOMMENDER_LOADED = False
rec_model, rec_scaler, rec_encoder = None, None, None

def load_recommender():
    global rec_model, rec_scaler, rec_encoder, RECOMMENDER_LOADED
    try:
        with open("recommender_model.pkl", "rb") as f:
            rec_model = pickle.load(f)
        with open("recommender_scaler.pkl", "rb") as f:
            rec_scaler = pickle.load(f)
        with open("recommender_encoder.pkl", "rb") as f:
            rec_encoder = pickle.load(f)
        RECOMMENDER_LOADED = True
        print("✅ Modèle recommandation chargé !")
    except FileNotFoundError:
        print("⚠️  recommender_model.pkl manquant — lance train_recommender.py")

load_recommender()

# ── Ajoute cette route ──
@app.route('/api/recommend', methods=['POST'])
def recommend():
    d        = request.json
    temp     = float(d.get("temp", 20))
    pluie    = float(d.get("pluie", 10))
    humidite = float(d.get("humidite", 50))
    vent     = float(d.get("vent", 20))
    ph       = float(d.get("ph", 7.0))
    fertilite= float(d.get("fertilite", 65))

    if not RECOMMENDER_LOADED:
        return jsonify({"error": "Modèle non chargé"}), 500

    X = rec_scaler.transform([[temp, pluie, humidite, vent, ph, fertilite]])

    # Probabilités pour chaque culture
    probs = rec_model.predict_proba(X)[0]
    classes = rec_encoder.classes_

    # Top 3 recommandations
    top3_idx  = np.argsort(probs)[::-1][:3]
    top3 = [
        {"culture": classes[i], "score": round(float(probs[i]) * 100, 1)}
        for i in top3_idx
    ]

    # Conseils selon paramètres
    conseils = []
    if temp < 15:
        conseils.append("🌡️ Température fraîche — favorise blé et légumes d'hiver")
    elif temp > 28:
        conseils.append("🌡️ Forte chaleur — privilégie pastèque et agrumes")
    else:
        conseils.append("✅ Température idéale pour tomate et poivron")

    if pluie < 5:
        conseils.append("💧 Faible pluviométrie — irrigation indispensable")
    elif pluie > 30:
        conseils.append("🌧️ Forte pluie — risque de maladies fongiques")
    else:
        conseils.append("✅ Pluviométrie correcte")

    if ph < 6.5:
        conseils.append("⚗️ Sol acide — amendement calcaire recommandé")
    elif ph > 7.5:
        conseils.append("⚗️ Sol alcalin — peut limiter l'absorption des nutriments")
    else:
        conseils.append("✅ pH optimal pour la plupart des cultures")

    return jsonify({
        "top3": top3,
        "conseils": conseils,
        "best": top3[0]["culture"]
    })

# ── Route page données Souss-Massa ──
@app.route('/souss-massa')
def souss_massa():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        df_data = []
        with open("souss_massa_data.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                df_data.append(row)
    except FileNotFoundError:
        df_data = []
    return render_template('souss_massa.html',
                           username=session['user'],
                           data=json.dumps(df_data))
    
def predict_score(temp, humidity, fertility):
    """Prédiction avec vrai modèle ou fallback simple"""
    if MODEL_LOADED:
        X = scaler_X.transform([[temp, humidity, fertility]])
        y_scaled = model.predict(X)
        score = scaler_y.inverse_transform(y_scaled.reshape(-1, 1))[0][0]
        return round(float(np.clip(score, 0, 100)), 1)
    else:
        # Fallback si modèle pas encore entraîné
        score = 0
        if 20 <= temp <= 30:       score += 35
        elif 15 <= temp <= 35:     score += 20
        if 40 <= humidity <= 70:   score += 35
        elif 30 <= humidity <= 80: score += 20
        score += int(fertility * 0.30)
        return round(float(np.clip(score, 0, 100)), 1)

# ─────────────────────────────────────────
# 🛠️ Init DB
# ─────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temp REAL,
        humidity REAL,
        fertility REAL,
        score REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────
# 📁 Init CSV
# ─────────────────────────────────────────
def init_csv():
    if not os.path.exists("data.csv"):
        with open("data.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Temp", "Humidity", "Fertility", "Score"])

init_csv()

# ─────────────────────────────────────────
# 💾 Save Data
# ─────────────────────────────────────────
def save_data(temp, humidity, fertility, score):
    with open("data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([temp, humidity, fertility, score])

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO sensor_data (temp, humidity, fertility, score) VALUES (?, ?, ?, ?)",
        (temp, humidity, fertility, score)
    )
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# 🤖 AI Decision pompe
# ─────────────────────────────────────────
def ai_decision(score):
    return "ON" if score < 40 else "OFF"

# ─────────────────────────────────────────
# 🏠 Auth Routes
# ─────────────────────────────────────────
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed   = generate_password_hash(password)
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Utilisateur déjà existant ! <a href='/register'>Retour</a>"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        return "Identifiants incorrects ! <a href='/login'>Retour</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html',
                           username=session['user'],
                           model_loaded=MODEL_LOADED)

# ─────────────────────────────────────────
# 📡 API DATA live
# ─────────────────────────────────────────
@app.route('/api/data')
def api_data():
    global pump, mode

    temp      = round(random.uniform(10, 45), 1)
    humidity  = round(random.uniform(10, 100), 1)
    fertility = round(random.uniform(0, 100), 1)
    score     = predict_score(temp, humidity, fertility)

    if mode == "AUTO":
        pump = ai_decision(score)

    save_data(temp, humidity, fertility, score)

    return jsonify({
        "temp": temp,
        "humidity": humidity,
        "fertility": fertility,
        "score": score,
        "pump": pump,
        "mode": mode,
        "model_active": MODEL_LOADED
    })

# ─────────────────────────────────────────
# 📥 Reçoit données externes ESP32/sender
# ─────────────────────────────────────────
@app.route('/data', methods=['POST'])
def receive_data():
    d         = request.json
    temp      = d.get("temp")
    humidity  = d.get("humidity")
    fertility = d.get("fertility")
    score     = d.get("score")

    if None in [temp, humidity, fertility, score]:
        return {"status": "error", "message": "Données manquantes"}, 400

    save_data(temp, humidity, fertility, score)
    return {"status": "ok"}

# ─────────────────────────────────────────
# 🧠 API Prédiction via sliders
# ─────────────────────────────────────────
@app.route('/api/predict', methods=['POST'])
def predict():
    d         = request.json
    temp      = float(d.get("temp", 25))
    humidity  = float(d.get("humidity", 50))
    fertility = float(d.get("fertility", 50))
    score     = predict_score(temp, humidity, fertility)

    advice = []
    if temp < 15:        advice.append("🌡️ Température trop basse — risque de gel")
    elif temp > 35:      advice.append("🌡️ Température trop élevée — stress thermique")
    else:                advice.append("✅ Température optimale pour la culture")

    if humidity < 30:    advice.append("💧 Sol trop sec — irrigation recommandée")
    elif humidity > 80:  advice.append("💧 Humidité excessive — risque de moisissures")
    else:                advice.append("✅ Humidité correcte")

    if fertility < 30:   advice.append("🌱 Fertilité faible — ajout d'engrais conseillé")
    elif fertility > 70: advice.append("✅ Fertilité excellente")
    else:                advice.append("🌱 Fertilité moyenne — surveillance recommandée")

    if score >= 75:      advice.append("🏆 Sol en excellente condition !")
    elif score >= 50:    advice.append("📊 Sol en condition acceptable")
    else:                advice.append("⚠️ Sol en mauvaise condition — intervention requise")

    return jsonify({
        "score": score,
        "advice": advice,
        "model_used": "Neural Network (entraîné)" if MODEL_LOADED else "Règles agronomiques (fallback)"
    })

# ─────────────────────────────────────────
# 📊 Historique pour ML
# ─────────────────────────────────────────
@app.route('/api/history')
def history():
    if 'user' not in session:
        return jsonify({"error": "Non connecté"}), 401
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        SELECT temp, humidity, fertility, score, timestamp
        FROM sensor_data ORDER BY id DESC LIMIT 50
    """)
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {"temp": r[0], "humidity": r[1], "fertility": r[2],
         "score": r[3], "timestamp": r[4]}
        for r in rows
    ])

# ─────────────────────────────────────────
# 🎮 Contrôle pompe
# ─────────────────────────────────────────
@app.route('/control', methods=['POST'])
def control():
    global pump, mode
    action = request.form['action']
    if action == "AUTO":
        mode = "AUTO"
    else:
        mode = "MANUAL"
        pump = action
    return "OK"

# ─────────────────────────────────────────
# 🔑 Reset mot de passe
# ─────────────────────────────────────────
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username     = request.form['username']
        new_password = request.form['new_password']
        hashed       = generate_password_hash(new_password)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user:
            c.execute("UPDATE users SET password = ? WHERE username = ?",
                      (hashed, username))
            conn.commit()
            conn.close()
            flash("Mot de passe changé avec succès !", "success")
            return redirect(url_for('login'))
        conn.close()
        flash("Utilisateur introuvable !", "error")
        return redirect(url_for('reset_password'))
    return render_template('reset_password.html')


if __name__ == '__main__':
    app.run(debug=True)