# fix_db.py
import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Ajouter les colonnes manquantes si elles n'existent pas
try:
    c.execute("ALTER TABLE sensor_data ADD COLUMN fertility REAL")
    print("✅ Colonne fertility ajoutée")
except:
    print("⚠️ fertility existe déjà")

try:
    c.execute("ALTER TABLE sensor_data ADD COLUMN score REAL")
    print("✅ Colonne score ajoutée")
except:
    print("⚠️ score existe déjà")

conn.commit()
conn.close()
print("✅ Base de données mise à jour !")