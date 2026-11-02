import sqlite3

DB_NAME = "fontamat.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chefs_chantier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            telephone TEXT,
            pin TEXT DEFAULT '0000',
            actif INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chantiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_chantier TEXT UNIQUE NOT NULL,
            localisation TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_interne TEXT UNIQUE NOT NULL,
            numero_serie TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            statut TEXT DEFAULT 'Disponible',
            statut_controle TEXT DEFAULT 'Conforme',
            date_dernier_controle TEXT,
            chantier_actuel TEXT,
            responsable TEXT,
            date_sortie TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_ref TEXT,
            chemin_photo TEXT,
            date_ajout TEXT,
            FOREIGN KEY(equipment_ref) REFERENCES equipment(ref_interne)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS controles_materiel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_ref TEXT,
            date_controle TEXT,
            technicien TEXT,
            resultat TEXT,
            remarques TEXT,
            FOREIGN KEY(equipment_ref) REFERENCES equipment(ref_interne)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mouvements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_ref TEXT,
            action TEXT,
            chef_chantier TEXT,
            chantier TEXT,
            date_heure TEXT,
            appareil TEXT DEFAULT 'Non spécifié',
            FOREIGN KEY(equipment_ref) REFERENCES equipment(ref_interne)
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE mouvements ADD COLUMN appareil TEXT DEFAULT 'Non spécifié'")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()
    print("[FONTAMAT] Base de données initialisée avec toutes les tables.")

if __name__ == "__main__":
    init_db()