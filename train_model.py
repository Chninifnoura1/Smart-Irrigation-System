import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os

# ─────────────────────────────────────────
# 📊 Générer données synthétiques si CSV vide
# ─────────────────────────────────────────
def generate_synthetic_data(n=2000):
    np.random.seed(42)
    data = []
    for _ in range(n):
        temp      = round(np.random.uniform(10, 45), 1)
        humidity  = round(np.random.uniform(10, 100), 1)
        fertility = round(np.random.uniform(0, 100), 1)

        # Score basé sur règles agronomiques réalistes
        score = 0

        # Température (max 35 pts)
        if 20 <= temp <= 30:
            score += 35
        elif 15 <= temp <= 35:
            score += 20
        elif 10 <= temp <= 38:
            score += 10
        else:
            score += 0

        # Humidité (max 35 pts)
        if 40 <= humidity <= 70:
            score += 35
        elif 30 <= humidity <= 80:
            score += 20
        elif 20 <= humidity <= 90:
            score += 10
        else:
            score += 0

        # Fertilité (max 30 pts)
        score += int(fertility * 0.30)

        # Bruit réaliste
        score += np.random.normal(0, 3)
        score  = round(float(np.clip(score, 0, 100)), 1)

        data.append([temp, humidity, fertility, score])

    df = pd.DataFrame(data, columns=["Temp", "Humidity", "Fertility", "Score"])
    return df

# ─────────────────────────────────────────
# 📁 Charger ou générer données
# ─────────────────────────────────────────
CSV_FILE = "data.csv"

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    print(f"✅ CSV chargé : {len(df)} lignes")
    if len(df) < 100:
        print("⚠️  Pas assez de données réelles, ajout de données synthétiques...")
        df_synth = generate_synthetic_data(2000)
        df = pd.concat([df, df_synth], ignore_index=True)
        print(f"✅ Total après ajout : {len(df)} lignes")
else:
    print("⚠️  Pas de CSV trouvé, génération de données synthétiques...")
    df = generate_synthetic_data(2000)
    df.to_csv(CSV_FILE, index=False)
    print(f"✅ CSV créé avec {len(df)} lignes")

# ─────────────────────────────────────────
# 🔧 Préparation des données
# ─────────────────────────────────────────
X = df[["Temp", "Humidity", "Fertility"]].values
y = df["Score"].values

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_scaled, test_size=0.2, random_state=42
)

print(f"\n📊 Entraînement : {len(X_train)} lignes")
print(f"📊 Test         : {len(X_test)} lignes")

# ─────────────────────────────────────────
# 🧠 Modèle Neural Network
# ─────────────────────────────────────────
model = MLPRegressor(
    hidden_layer_sizes=(128, 64, 32),   # 3 couches cachées
    activation='relu',
    solver='adam',
    learning_rate='adaptive',
    max_iter=2000,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=20,
    verbose=False
)

print("\n🚀 Entraînement en cours...")
model.fit(X_train, y_train)
print("✅ Entraînement terminé !")

# ─────────────────────────────────────────
# 📈 Évaluation
# ─────────────────────────────────────────
y_pred       = model.predict(X_test)
y_pred_real  = scaler_y.inverse_transform(y_pred.reshape(-1, 1)).ravel()
y_test_real  = scaler_y.inverse_transform(y_test.reshape(-1, 1)).ravel()

mae = mean_absolute_error(y_test_real, y_pred_real)
r2  = r2_score(y_test_real, y_pred_real)

print(f"\n📊 Résultats :")
print(f"   MAE (erreur moyenne) : {mae:.2f} points")
print(f"   R²  (précision)      : {r2:.4f}")

if r2 >= 0.90:
    print("   ✅ Excellent modèle !")
elif r2 >= 0.75:
    print("   🟡 Bon modèle")
else:
    print("   🔴 Modèle à améliorer — collecte plus de données")

# ─────────────────────────────────────────
# 💾 Sauvegarde
# ─────────────────────────────────────────
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("scaler_X.pkl", "wb") as f:
    pickle.dump(scaler_X, f)
with open("scaler_y.pkl", "wb") as f:
    pickle.dump(scaler_y, f)

print("\n💾 Fichiers sauvegardés : model.pkl, scaler_X.pkl, scaler_y.pkl")
print("🎉 Lance maintenant : python app.py")