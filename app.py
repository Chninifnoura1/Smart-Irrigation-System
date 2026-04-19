from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = "cle_secrete_dyal_projet" # Darori bach tekhdem les sessions (Login)

# Valeurs par défaut
humidity = 40
pump = "OFF"
mode = "AUTO"

# 🛠️ Initialisation dyal Base de Données (SQLite)
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Nlanciou la base de données fach ybda l'app
init_db()

# 🤖 AI Logic (Simulation)
def ai_decision(h):
    return "ON" if h < 30 else "OFF"

# 🏠 HOME (Redirection vers Login)
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 🔐 INSCRIPTION (Register)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cryptage dyal mot de passe
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Had l'utilisateur deja kayn ! <a href='/register'>Rje3</a>"
            
    return render_template('register.html')

# 🔓 LOGIN
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
        
        # user[2] hia l'password li f la base de données
        if user and check_password_hash(user[2], password):
            session['user'] = username # Sauvegarder session
            return redirect(url_for('dashboard'))
        else:
            return "Mot de passe wla username ghalet ! <a href='/login'>Rje3</a>"

    return render_template('login.html')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None) # Nms7ou la session
    return redirect(url_for('login'))

# 🖥️ DASHBOARD (Protégé)
@app.route('/dashboard')
def dashboard():
    # Ila makanch connecte, nrej3ouh l login
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

# 📡 API DATA & 🎮 CONTROL (Khllithoum kima huma)
@app.route('/api/data')
def data():
    global humidity, pump, mode
    humidity = random.randint(20, 80)
    if mode == "AUTO":
        pump = ai_decision(humidity)
    return jsonify({
        "temp": random.randint(20, 35),
        "humidity": humidity,
        "rain": random.randint(0, 50),
        "pump": pump,
        "mode": mode
    })

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

# 🔑 MOT DE PASSE OUBLIÉ
# 🔑 MOT DE PASSE OUBLIÉ
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        
        hashed_password = generate_password_hash(new_password)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user:
            # Ila l9inah, nbddlou lih l'mot de passe
            c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
            conn.commit()
            conn.close()
            
            # 🟢 Nssifto message de succès w nrej3ouh l login
            flash("Mot de passe mbeddel b naja7 ! T9der tconnecta daba.", "success")
            return redirect(url_for('login'))
        else:
            conn.close()
            
            # 🔴 Nssifto message d'erreur w nkhaliwh f nfs lpage
            flash("Had l'utilisateur makaynch !", "error")
            return redirect(url_for('reset_password'))

    return render_template('reset_password.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    