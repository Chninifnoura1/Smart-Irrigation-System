import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import classification_report, accuracy_score
import pickle

# ─────────────────────────────────────────
# 📊 Charger données
# ─────────────────────────────────────────
df = pd.read_csv("souss_massa_data.csv")
print(f"✅ Données chargées : {len(df)} lignes")
print(f"   Cultures uniques : {df['Culture'].unique()}")

# ─────────────────────────────────────────
# 🔧 Préparation
# ─────────────────────────────────────────
features = ["Temp_moy", "Pluie_mm", "Humidite", "Vent_kmh", "pH_sol", "Fertilite"]
X = df[features].values
y = df["Culture"].values

# Encoder les labels (Tomate=0, Poivron=1, etc.)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Normaliser les features
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42
)

print(f"\n📊 Entraînement : {len(X_train)} | Test : {len(X_test)}")

# ─────────────────────────────────────────
# 🌲 Random Forest Classifier
# ─────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)

print("\n🚀 Entraînement Random Forest...")
model.fit(X_train, y_train)

# ─────────────────────────────────────────
# 📈 Évaluation
# ─────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"\n📊 Résultats :")
print(f"   Précision globale : {acc*100:.1f}%")
print(f"\n{classification_report(y_test, y_pred, target_names=le.classes_)}")

# Importance des features
importances = model.feature_importances_
print("📊 Importance des paramètres :")
for f, i in sorted(zip(features, importances), key=lambda x: -x[1]):
    bar = "█" * int(i * 50)
    print(f"   {f:15s} {bar} {i*100:.1f}%")

# ─────────────────────────────────────────
# 💾 Sauvegarde
# ─────────────────────────────────────────
with open("recommender_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("recommender_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("recommender_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("\n💾 Modèle sauvegardé : recommender_model.pkl")
print("🎉 Lance maintenant : python app.py")
