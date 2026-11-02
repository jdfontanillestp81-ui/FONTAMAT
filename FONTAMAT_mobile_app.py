import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

# Dossier local de l'application sur le téléphone (ou chemin pointant vers le dossier Drive synchro)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "fontamat_data")
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER, exist_ok=True)

class FontamatMobileApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FONTAMAT TERRAIN")
        self.root.geometry("350x720")
        self.root.config(bg="#f5f7f8")

        title_label = tk.Label(root, text="🌟 FONTAMAT TERRAIN 🌟", font=("Arial", 16, "bold"), fg="#1b4f72", bg="#f5f7f8")
        title_label.pack(pady=15)

        # Chef de chantier
        tk.Label(root, text="👷 Sélectionne ton nom :", font=("Arial", 11, "bold"), bg="#f5f7f8", fg="#2c3e50").pack(anchor="w", padx=25)
        self.chef_var = tk.StringVar(root)
        self.chefs_list = self.charger_chefs()
        self.chef_var.set(self.chefs_list[0] if self.chefs_list else "Aucun chef")
        self.chef_menu = tk.OptionMenu(root, self.chef_var, *self.chefs_list)
        self.chef_menu.config(font=("Arial", 11), width=22, bg="white")
        self.chef_menu.pack(pady=5, padx=25)

        # Code PIN
        tk.Label(root, text="🔒 Code PIN (4 chiffres) :", font=("Arial", 11, "bold"), bg="#f5f7f8", fg="#2c3e50").pack(anchor="w", padx=25)
        self.pin_entry = tk.Entry(root, show="*", font=("Arial", 14), width=18, justify="center")
        self.pin_entry.pack(pady=5, padx=25)

        # Référence Matériel
        tk.Label(root, text="🏷️ Référence Matériel :", font=("Arial", 11, "bold"), bg="#f5f7f8", fg="#2c3e50").pack(anchor="w", padx=25)
        self.ref_entry = tk.Entry(root, font=("Arial", 12), width=22, justify="center")
        self.ref_entry.pack(pady=5, padx=25)

        # Chantier
        tk.Label(root, text="🏗️ Nom du Chantier :", font=("Arial", 11, "bold"), bg="#f5f7f8", fg="#2c3e50").pack(anchor="w", padx=25)
        self.chantier_entry = tk.Entry(root, font=("Arial", 12), width=22, justify="center")
        self.chantier_entry.pack(pady=5, padx=25)

        # Boutons de validation mouvement
        btn_sortie = tk.Button(root, text="🚀 VALIDER SORTIE", bg="#d35400", fg="white", font=("Arial", 11, "bold"), command=lambda: self.enregistrer("SORTIE"))
        btn_sortie.pack(pady=10, padx=25, fill="x")

        btn_retour = tk.Button(root, text="🎯 VALIDER RETOUR", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), command=lambda: self.enregistrer("RETOUR"))
        btn_retour.pack(pady=5, padx=25, fill="x")

        # --- SECTION DEMANDE NOUVEAU CHEF ---
        tk.Label(root, text="--- Nouveau sur le terrain ? ---", font=("Arial", 9, "italic"), bg="#f5f7f8", fg="#7f8c8d").pack(pady=10)
        
        btn_demande = tk.Button(root, text="➕ Demander l'ajout d'un Chef", bg="#8e44ad", fg="white", font=("Arial", 10, "bold"), command=self.ouvrir_fenetre_demande_chef)
        btn_demande.pack(pady=5, padx=25, fill="x")

        self.status_label = tk.Label(root, text="", font=("Arial", 10, "bold"), bg="#f5f7f8")
        self.status_label.pack(pady=10)

    def charger_chefs(self):
        chefs_path = os.path.join(DATA_FOLDER, "chefs.json")
        if os.path.exists(chefs_path):
            try:
                with open(chefs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [item["nom"] for item in data]
            except Exception:
                pass
        return ["Jean Dupont", "Marc Martin"]

    def enregistrer(self, action):
        ref = self.ref_entry.get().strip()
        chef = self.chef_var.get()
        pin = self.pin_entry.get().strip()
        chantier = self.chantier_entry.get().strip()

        if not ref or not pin:
            self.status_label.config(text="⚠️ Remplis la référence et le PIN !", fg="red")
            return

        mvt_path = os.path.join(DATA_FOLDER, "mouvements.json")
        mouvements = []
        if os.path.exists(mvt_path):
            try:
                with open(mvt_path, "r", encoding="utf-8") as f:
                    mouvements = json.load(f)
            except Exception:
                pass

        nouveau = {
            "date_heure": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "equipment_ref": ref,
            "action": action,
            "chef_chantier": chef,
            "chantier": chantier if action == "SORTIE" else "Dépôt",
            "appareil": f"Smartphone - {chef}"
        }

        mouvements.insert(0, nouveau)
        try:
            with open(mvt_path, "w", encoding="utf-8") as f:
                json.dump(mouvements, f, indent=4, ensure_ascii=False)
            self.status_label.config(text=f"🎉 Succès : {action} enregistrée !", fg="green")
            self.ref_entry.delete(0, tk.END)
            self.pin_entry.delete(0, tk.END)
        except Exception as e:
            self.status_label.config(text=f"❌ Erreur : {e}", fg="red")

    def ouvrir_fenetre_demande_chef(self):
        fen = tk.Toplevel(self.root)
        fen.title("Demande Chef")
        fen.geometry("300x350")
        fen.config(bg="#f5f7f8")

        tk.Label(fen, text="Nouveau Chef de Chantier", font=("Arial", 12, "bold"), bg="#f5f7f8", fg="#8e44ad").pack(pady=15)
        
        tk.Label(fen, text="Nom et Prénom :", bg="#f5f7f8").pack(anchor="w", padx=20)
        e_nom = tk.Entry(fen, font=("Arial", 11), width=20); e_nom.pack(pady=5, padx=20)

        tk.Label(fen, text="Téléphone :", bg="#f5f7f8").pack(anchor="w", padx=20)
        e_tel = tk.Entry(fen, font=("Arial", 11), width=20); e_tel.pack(pady=5, padx=20)

        tk.Label(fen, text="Code PIN (4 chiffres) :", bg="#f5f7f8").pack(anchor="w", padx=20)
        e_pin = tk.Entry(fen, font=("Arial", 11), width=20, show="*"); e_pin.pack(pady=5, padx=20)

        def envoyer_demande():
            nom = e_nom.get().strip()
            tel = e_tel.get().strip()
            pin = e_pin.get().strip()
            if not nom or len(pin) != 4:
                messagebox.showerror("Erreur", "Veuillez remplir le nom et un PIN à 4 chiffres.")
                return
            
            demande_path = os.path.join(DATA_FOLDER, "demandes_chefs.json")
            demandes = []
            if os.path.exists(demande_path):
                try:
                    with open(demande_path, "r", encoding="utf-8") as f:
                        demandes = json.load(f)
                except Exception:
                    pass
            
            demandes.append({"nom": nom, "telephone": tel, "pin": pin, "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
            
            try:
                with open(demande_path, "w", encoding="utf-8") as f:
                    json.dump(demandes, f, indent=4, ensure_ascii=False)
                messagebox.สำเร็จ("Succès" if "Succès" in "Succès" else "Succès", "Demande envoyée au PC via le Drive !")
                fen.destroy()
            except Exception as ex:
                messagebox.showerror("Erreur", str(ex))

        tk.Button(fen, text="Envoyer la demande", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=envoyer_demande).pack(pady=20, padx=20, fill="x")

if __name__ == "__main__":
    root = tk.Tk()
    app = FontamatMobileApp(root)
    root.mainloop()