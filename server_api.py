from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

app = FastAPI(title="GÉO FONTA - FONTAMAT API")

DATA_DIR = "."

def charger_json(nom_fichier):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    if os.path.exists(chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def sauvegarder_json(nom_fichier, data):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class Equipment(BaseModel):
    ref_interne: str
    numero_serie: str
    nom: str
    categorie: str

class Chef(BaseModel):
    nom: str
    telephone: str
    pin: str

@app.get("/equipment")
def get_equipment():
    return charger_json("equipement.json")

@app.post("/equipment")
def add_equipment(eq: Equipment):
    data = charger_json("equipement.json")
    for item in data:
        if item.get("ref_interne") == eq.ref_interne:
            raise HTTPException(status_code=400, detail="Cette référence existe déjà.")
    
    nouveau = eq.dict()
    nouveau.update({
        "statut": "Disponible",
        "statut_controle": "Conforme",
        "date_dernier_controle": "",
        "chantier_actuel": "Dépôt",
        "responsable": "Dépôt"
    })
    data.append(nouveau)
    sauvegarder_json("equipement.json", data)
    return {"message": "Matériel ajouté avec succès"}

@app.get("/chefs")
def get_chefs():
    return charger_json("chefs.json")

@app.post("/chefs")
def add_chef(chef: Chef):
    data = charger_json("chefs.json")
    for item in data:
        if item.get("nom").lower() == chef.nom.lower():
            raise HTTPException(status_code=400, detail="Ce chef existe déjà.")
    data.append(chef.dict())
    sauvegarder_json("chefs.json", data)
    return {"message": "Chef enregistré avec succès"}

@app.get("/mouvements/search")
def search_mouvements(chef: str = "", equipment: str = "", appareil: str = ""):
    mouvements = charger_json("mouvements.json")
    resultats = []
    for m in mouvements:
        if chef and chef.lower() not in m.get("chef_chantier", "").lower():
            continue
        if equipment and equipment.lower() not in m.get("equipment_ref", "").lower():
            continue
        if appareil and appareil.lower() not in m.get("appareil", "").lower():
            continue
        resultats.append(m)
    return resultats

@app.get("/export/mouvements/xlsx")
def export_excel_multionglets(chef: str = "", equipment: str = "", appareil: str = ""):
    equipements = charger_json("equipement.json")
    chefs = charger_json("chefs.json")
    
    wb = openpyxl.Workbook()
    # Supprimer la feuille par défaut
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2980B9", end_color="2980B9", fill_type="solid")
    align_center = Alignment(horizontal="center", vertical="center")
    border_thin = Border(
        left=Side(style='thin', color='BDC3C7'),
        right=Side(style='thin', color='BDC3C7'),
        top=Side(style='thin', color='BDC3C7'),
        bottom=Side(style='thin', color='BDC3C7')
    )

    def styliser_feuille(ws, titre, data_items):
        ws.title = titre[:31]  # Limitation Excel à 31 caractères par onglet
        ws.views.sheetView[0].showGridLines = True
        
        headers = ["Réf Interne", "N° Série", "Modèle / Nom", "Catégorie", "Statut", "Chantier Actuel", "Responsable"]
        ws.append(headers)
        
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center
            
        for item in data_items:
            row = [
                str(item.get("ref_interne", "")),
                str(item.get("numero_serie", "")),
                str(item.get("nom", "")),
                str(item.get("categorie", "")),
                str(item.get("statut", "")),
                str(item.get("chantier_actuel", "")),
                str(item.get("responsable", ""))
            ]
            ws.append(row)
            
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = border_thin
                cell.alignment = Alignment(vertical="center")

    # 1. Créer un onglet par chef de chantier
    liste_noms_chefs = [c.get("nom") for c in chefs if c.get("nom")]
    if not liste_noms_chefs:
        liste_noms_chefs = list(set(e.get("responsable") for e in equipements if e.get("responsable")))

    for nom_chef in liste_noms_chefs:
        mat_chef = [e for e in equipements if e.get("responsable") and nom_chef.lower() in e.get("responsable", "").lower()]
        ws = wb.create_sheet()
        styliser_feuille(ws, f"Chef - {nom_chef}", mat_chef)

    # 2. Créer l'onglet Dépôt (stock restant)
    mat_depot = [e for e in equipements if not e.get("responsable") or e.get("responsable").lower() in ["dépôt", "depot", ""]]
    ws_depot = wb.create_sheet()
    styliser_feuille(ws_depot, "Dépôt (Stock)", mat_depot)

    # Sauvegarde temporaire du fichier
    export_path = os.path.join(DATA_DIR, "export_materiel_fontamat.xlsx")
    wb.save(export_path)
    
    return FileResponse(export_path, filename="export_materiel_fontamat.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")