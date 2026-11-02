import sys
import os
import json
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QTabWidget, QFileDialog)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QTimer

API_URL = "http://127.0.0.1:8000"
CONFIG_FILE = "config_fontamat.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GÉO FONTA - FONTAMAT - Gestion du Matériel de Chantier")
        self.setGeometry(100, 100, 1300, 850)
        
        app_font = QFont("Arial", 10)
        self.setFont(app_font)
        
        self.load_config()
        
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        
        # Bannière d'alerte pour les demandes de chefs en attente
        self.alert_banner = QLabel("🔔 NOUVELLE DEMANDE DE CHEF EN ATTENTE SUR LE DRIVE !")
        self.alert_banner.setStyleSheet("background-color: #e67e22; color: white; font-size: 13px; font-weight: bold; padding: 8px; border-radius: 4px;")
        self.alert_banner.setHidden(True)
        self.main_layout.addWidget(self.alert_banner)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #bdc3c7; background: #ffffff; }
            QTabBar::tab { 
                font-size: 12px; 
                font-weight: bold; 
                padding: 10px 16px; 
                margin-right: 4px;
                background: #ecf0f1; 
                color: #2c3e50; 
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { 
                background: #3498db; 
                color: white; 
            }
        """)
        self.main_layout.addWidget(tabs)
        self.setCentralWidget(main_widget)
        
        self.tab_parc = QWidget()
        self.init_parc_tab(self.tab_parc)
        tabs.addTab(self.tab_parc, "📦 Parc Matériel")
        
        self.tab_histo = QWidget()
        self.init_histo_tab(self.tab_histo)
        tabs.addTab(self.tab_histo, "📜 Historique & Mouvements")
        
        self.tab_ajout = QWidget()
        self.init_ajout_tab(self.tab_ajout)
        tabs.addTab(self.tab_ajout, "➕ Ajouter Matériel")
        
        self.tab_chefs = QWidget()
        self.init_chefs_tab(self.tab_chefs)
        tabs.addTab(self.tab_chefs, "👷 Chefs & PIN")
        
        self.tab_appareils = QWidget()
        self.init_appareils_tab(self.tab_appareils)
        tabs.addTab(self.tab_appareils, "📱 Appareils (Drive)")
        
        self.tab_config = QWidget()
        self.init_config_tab(self.tab_config)
        tabs.addTab(self.tab_config, "⚙️ Paramètres")

        # Timer pour vérifier périodiquement les demandes de chefs sur le Drive
        self.timer = QTimer()
        self.timer.timeout.connect(self.verifier_demandes_chefs)
        self.timer.start(5000)

    def verifier_demandes_chefs(self):
        drive_path = self.config.get("dossier_drive", "")
        demande_file = os.path.join(drive_path, "demandes_chefs.json") if drive_path else "demandes_chefs.json"
        
        if os.path.exists(demande_file):
            try:
                with open(demande_file, "r", encoding="utf-8") as f:
                    demandes = json.load(f)
                if demandes:
                    self.alert_banner.setText(f"🔔 {len(demandes)} demande(s) de création de chef en attente de validation !")
                    self.alert_banner.setHidden(False)
                else:
                    self.alert_banner.setHidden(True)
            except Exception:
                pass
        else:
            self.alert_banner.setHidden(True)

    def load_config(self):
        self.config = {"dossier_source": "", "dossier_drive": ""}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                pass

    def save_config_file(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            QMessageBox.information(self, "Super !", "Configuration enregistrée !")
        except Exception as e:
            QMessageBox.critical(self, "Oups !", f"Erreur : {e}")

    def init_parc_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("<b>🌟 État en direct de tout le matériel 🌟</b>")
        title.setStyleSheet("font-size: 16px; color: #2c3e50;")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Réf Interne", "N° Série", "Nom", "Catégorie", 
            "Statut", "Contrôle", "Dernier Contrôle", "Chantier Actuel", "Responsable"
        ])
        layout.addWidget(self.table)
        
        layout_btn = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Actualiser la liste")
        btn_refresh.setStyleSheet("background-color: #3498db; color: white; font-size: 14px; font-weight: bold; padding: 12px; border-radius: 8px;")
        btn_refresh.clicked.connect(self.load_data)
        layout_btn.addWidget(btn_refresh)
        
        layout.addLayout(layout_btn)
        self.load_data()

    def init_histo_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("<b>📜 Historique complet et export multi-onglets par chef & dépôt</b>")
        title.setStyleSheet("font-size: 16px; color: #2c3e50;")
        layout.addWidget(title)
        
        filter_box = QHBoxLayout()
        
        self.filter_chef = QLineEdit()
        self.filter_chef.setPlaceholderText("🔍 Filtrer par Chef (ex: Dupont)")
        self.filter_chef.textChanged.connect(self.filter_mouvements)
        
        self.filter_equip = QLineEdit()
        self.filter_equip.setPlaceholderText("🔍 Filtrer par Matériel / Ref")
        self.filter_equip.textChanged.connect(self.filter_mouvements)
        
        self.filter_app = QLineEdit()
        self.filter_app.setPlaceholderText("🔍 Filtrer par Appareil")
        self.filter_app.textChanged.connect(self.filter_mouvements)
        
        btn_reset = QPushButton("🔄 Réinitialiser")
        btn_reset.setStyleSheet("background-color: #95a5a6; color: white; font-weight: bold; padding: 8px;")
        btn_reset.clicked.connect(self.reset_filters)
        
        filter_box.addWidget(self.filter_chef)
        filter_box.addWidget(self.filter_equip)
        filter_box.addWidget(self.filter_app)
        filter_box.addWidget(btn_reset)
        layout.addLayout(filter_box)
        
        self.histo_table = QTableWidget()
        self.histo_table.setColumnCount(6)
        self.histo_table.setHorizontalHeaderLabels([
            "Date & Heure", "Réf Matériel", "Action / Mouvement", "Chef de Chantier", "Chantier / Destination", "Appareil Source"
        ])
        layout.addWidget(self.histo_table)
        
        btn_export_xlsx = QPushButton("📊 EXPORTER EN EXCEL (Multi-onglets Chefs + Dépôt) ✨")
        btn_export_xlsx.setStyleSheet("background-color: #27ae60; color: white; font-size: 14px; font-weight: bold; padding: 14px; border-radius: 8px;")
        btn_export_xlsx.clicked.connect(self.export_xlsx_ludique)
        layout.addWidget(btn_export_xlsx)
        
        self.filter_mouvements()

    def filter_mouvements(self):
        chef = self.filter_chef.text().strip()
        equip = self.filter_equip.text().strip()
        app = self.filter_app.text().strip()
        
        try:
            res = requests.get(f"{API_URL}/mouvements/search", params={"chef": chef, "equipment": equip, "appareil": app})
            if res.status_code == 200:
                data = res.json()
                self.histo_table.setRowCount(len(data))
                for row_idx, item in enumerate(data):
                    self.histo_table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("date_heure", ""))))
                    self.histo_table.setItem(row_idx, 1, QTableWidgetItem(str(item.get("equipment_ref", ""))))
                    
                    action_item = QTableWidgetItem("🚀 SORTIE" if item.get("action") == "SORTIE" else "🎯 RETOUR")
                    if item.get("action") == "SORTIE":
                        action_item.setForeground(QColor("#c0392b"))
                    else:
                        action_item.setForeground(QColor("#27ae60"))
                    
                    self.histo_table.setItem(row_idx, 2, action_item)
                    self.histo_table.setItem(row_idx, 3, QTableWidgetItem(str(item.get("chef_chantier", ""))))
                    self.histo_table.setItem(row_idx, 4, QTableWidgetItem(str(item.get("chantier", ""))))
                    self.histo_table.setItem(row_idx, 5, QTableWidgetItem(str(item.get("appareil", "GÉO FONTA App"))))
        except Exception:
            pass

    def reset_filters(self):
        self.filter_chef.clear()
        self.filter_equip.clear()
        self.filter_app.clear()
        self.filter_mouvements()

    def export_xlsx_ludique(self):
        try:
            res = requests.get(f"{API_URL}/export/mouvements/xlsx")
            if res.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier Excel", "export_materiel_fontamat.xlsx", "Excel Files (*.xlsx)")
                if file_path:
                    with open(file_path, "wb") as f:
                        f.write(res.content)
                    QMessageBox.information(self, "Super !", "Le fichier Excel multi-onglets (par chef + dépôt) a été généré avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {e}")

    def init_ajout_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        lbl = QLabel("<b>🚀 Enregistrer un nouvel outil ou matériel</b>")
        lbl.setStyleSheet("font-size: 18px; color: #e67e22;")
        layout.addWidget(lbl)
        
        self.in_ref = QLineEdit()
        self.in_ref.setPlaceholderText("Référence interne (ex: LAS-CANA-01)")
        layout.addWidget(self.in_ref)
        
        self.in_serie = QLineEdit()
        self.in_serie.setPlaceholderText("Numéro de série constructeur")
        layout.addWidget(self.in_serie)
        
        self.in_nom = QLineEdit()
        self.in_nom.setPlaceholderText("Nom du modèle")
        layout.addWidget(self.in_nom)
        
        self.cb_cat = QComboBox()
        self.cb_cat.addItems(["Laser de canalisation", "Niveau laser rotatif", "Niveau optique", "Cellule", "Trépied", "Mire", "Accessoire"])
        layout.addWidget(self.cb_cat)
        
        btn_save = QPushButton("✨ AJOUTER AU PARC ✨")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; font-size: 16px; font-weight: bold; padding: 15px; border-radius: 10px;")
        btn_save.clicked.connect(self.save_equipment)
        layout.addWidget(btn_save)
        layout.addStretch()

    def init_chefs_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        lbl = QLabel("<b>👷 Gestion des Chefs de Chantier & Code PIN Mobile</b>")
        lbl.setStyleSheet("font-size: 18px; color: #8e44ad;")
        layout.addWidget(lbl)
        
        self.chef_nom = QLineEdit()
        self.chef_nom.setPlaceholderText("Nom et Prénom du chef de chantier")
        layout.addWidget(self.chef_nom)
        
        self.chef_tel = QLineEdit()
        self.chef_tel.setPlaceholderText("Numéro de téléphone")
        layout.addWidget(self.chef_tel)
        
        self.chef_pin = QLineEdit()
        self.chef_pin.setPlaceholderText("Code PIN mobile à 4 chiffres (ex: 1234)")
        self.chef_pin.setMaxLength(4)
        layout.addWidget(self.chef_pin)
        
        btn_add_chef = QPushButton("➕ ENREGISTRER LE CHEF ET SON PIN")
        btn_add_chef.setStyleSheet("background-color: #9b59b6; color: white; font-size: 15px; font-weight: bold; padding: 12px; border-radius: 8px;")
        btn_add_chef.clicked.connect(self.save_chef)
        layout.addWidget(btn_add_chef)
        
        self.chefs_table = QTableWidget()
        self.chefs_table.setColumnCount(3)
        self.chefs_table.setHorizontalHeaderLabels(["Nom", "Téléphone", "Statut"])
        layout.addWidget(self.chefs_table)
        self.load_chefs()

    def init_appareils_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        lbl = QLabel("<b>📱 Gestion des Appareils Mobiles (Synchronisé Drive)</b>")
        lbl.setStyleSheet("font-size: 18px; color: #2980b9;")
        layout.addWidget(lbl)
        
        form_layout = QHBoxLayout()
        self.app_nom_input = QLineEdit()
        self.app_nom_input.setPlaceholderText("Nom du téléphone (ex: Xiaomi - Jean)")
        self.app_chef_input = QLineEdit()
        self.app_chef_input.setPlaceholderText("Chef rattaché")
        
        btn_add_app = QPushButton("➕ Ajouter l'appareil")
        btn_add_app.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        btn_add_app.clicked.connect(self.ajouter_appareil_json)
        
        form_layout.addWidget(self.app_nom_input)
        form_layout.addWidget(self.app_chef_input)
        form_layout.addWidget(btn_add_app)
        layout.addLayout(form_layout)
        
        self.app_table = QTableWidget()
        self.app_table.setColumnCount(4)
        self.app_table.setHorizontalHeaderLabels(["Nom / Modèle du Téléphone", "Chef Rattaché", "Statut Autorisé", "Actions"])
        layout.addWidget(self.app_table)
        
        btn_load_file = QPushButton("🔄 Actualiser la liste depuis le Drive")
        btn_load_file.setStyleSheet("background-color: #3498db; color: white; font-size: 14px; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_load_file.clicked.connect(self.load_appareils_json)
        layout.addWidget(btn_load_file)
        
        self.load_appareils_json()

    def get_appareils_filepath(self):
        drive_path = self.config.get("dossier_drive", "")
        return os.path.join(drive_path, "appareils_autorises.json") if drive_path else "appareils_autorises.json"

    def load_appareils_json(self):
        file_path = self.get_appareils_filepath()
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.app_table.setRowCount(len(data))
                    for idx, item in enumerate(data):
                        nom_app = item.get("nom_appareil", "")
                        self.app_table.setItem(idx, 0, QTableWidgetItem(nom_app))
                        self.app_table.setItem(idx, 1, QTableWidgetItem(item.get("chef", "")))
                        
                        est_autorise = item.get("autorise", False)
                        self.app_table.setItem(idx, 2, QTableWidgetItem("✅ Autorisée" if est_autorise else "❌ Bloquée"))
                        
                        widget_btn = QWidget()
                        layout_h = QHBoxLayout(widget_btn)
                        layout_h.setContentsMargins(2, 2, 2, 2)
                        
                        btn_toggle = QPushButton("Désactiver" if est_autorise else "Autoriser")
                        btn_toggle.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;" if est_autorise else "background-color: #2ecc71; color: white; font-weight: bold;")
                        btn_toggle.clicked.connect(lambda checked, name=nom_app: self.basculer_statut_appareil(name))
                        
                        btn_del = QPushButton("🗑️ Supprimer")
                        btn_del.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
                        btn_del.clicked.connect(lambda checked, name=nom_app: self.supprimer_appareil_json(name))
                        
                        layout_h.addWidget(btn_toggle)
                        layout_h.addWidget(btn_del)
                        self.app_table.setCellWidget(idx, 3, widget_btn)
            except Exception:
                pass

    def ajouter_appareil_json(self):
        nom = self.app_nom_input.text().strip()
        chef = self.app_chef_input.text().strip()
        if not nom:
            QMessageBox.warning(None, "Attention", "Veuillez saisir le nom de l'appareil.")
            return
            
        file_path = self.get_appareils_filepath()
        data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
                
        data.append({"nom_appareil": nom, "chef": chef, "autorise": True})
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.app_nom_input.clear()
            self.app_chef_input.clear()
            self.load_appareils_json()
            QMessageBox.information(None, "Succès", "Appareil ajouté et enregistré dans le Drive !")
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Impossible d'enregistrer : {e}")

    def basculer_statut_appareil(self, nom_appareil):
        file_path = self.get_appareils_filepath()
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    if item.get("nom_appareil") == nom_appareil:
                        item["autorise"] = not item.get("autorise", False)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                self.load_appareils_json()
            except Exception:
                pass

    def supprimer_appareil_json(self, nom_appareil):
        file_path = self.get_appareils_filepath()
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data = [item for item in data if item.get("nom_appareil") != nom_appareil]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                self.load_appareils_json()
            except Exception:
                pass

    def init_config_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        lbl = QLabel("<b>⚙️ Paramètres des dossiers et du Drive</b>")
        lbl.setStyleSheet("font-size: 18px; color: #16a085;")
        layout.addWidget(lbl)
        
        self.input_source = QLineEdit(self.config.get("dossier_source", ""))
        self.input_drive = QLineEdit(self.config.get("dossier_drive", ""))
        
        layout.addWidget(QLabel("Dossier Source Local :"))
        layout.addWidget(self.input_source)
        
        layout.addWidget(QLabel("Dossier Drive Destinataire :"))
        layout.addWidget(self.input_drive)
        
        btn_save_cfg = QPushButton("💾 SAUVEGARDER LES PARAMÈTRES")
        btn_save_cfg.setStyleSheet("background-color: #1abc9c; color: white; font-size: 15px; font-weight: bold; padding: 14px; border-radius: 8px;")
        btn_save_cfg.clicked.connect(self.apply_and_save_config)
        layout.addWidget(btn_save_cfg)
        layout.addStretch()

    def load_data(self):
        try:
            res = requests.get(f"{API_URL}/equipment")
            if res.status_code == 200:
                data = res.json()
                self.table.setRowCount(len(data))
                for row_idx, item in enumerate(data):
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("ref_interne", ""))))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(str(item.get("numero_serie", ""))))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(str(item.get("nom", ""))))
                    self.table.setItem(row_idx, 3, QTableWidgetItem(str(item.get("categorie", ""))))
                    self.table.setItem(row_idx, 4, QTableWidgetItem(str(item.get("statut", ""))))
                    self.table.setItem(row_idx, 5, QTableWidgetItem(str(item.get("statut_controle", ""))))
                    self.table.setItem(row_idx, 6, QTableWidgetItem(str(item.get("date_dernier_controle", "") or "")))
                    self.table.setItem(row_idx, 7, QTableWidgetItem(str(item.get("chantier_actuel", "") or "")))
                    self.table.setItem(row_idx, 8, QTableWidgetItem(str(item.get("responsable", "") or "")))
        except Exception:
            pass

    def load_chefs(self):
        try:
            res = requests.get(f"{API_URL}/chefs")
            if res.status_code == 200:
                data = res.json()
                self.chefs_table.setRowCount(len(data))
                for row_idx, item in enumerate(data):
                    self.chefs_table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("nom", ""))))
                    self.chefs_table.setItem(row_idx, 1, QTableWidgetItem(str(item.get("telephone", ""))))
                    self.chefs_table.setItem(row_idx, 2, QTableWidgetItem("Actif avec PIN"))
        except Exception:
            pass

    def save_equipment(self):
        payload = {
            "ref_interne": self.in_ref.text().strip(),
            "numero_serie": self.in_serie.text().strip(),
            "nom": self.in_nom.text().strip(),
            "categorie": self.cb_cat.currentText()
        }
        try:
            res = requests.post(f"{API_URL}/equipment", json=payload)
            if res.status_code == 200:
                QMessageBox.information(None, "Bravo !", "Matériel ajouté !")
                self.in_ref.clear()
                self.in_serie.clear()
                self.in_nom.clear()
                self.load_data()
            else:
                QMessageBox.warning(None, "Attention", res.json().get("detail", "Erreur"))
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Erreur : {e}")

    def save_chef(self):
        payload = {
            "nom": self.chef_nom.text().strip(),
            "telephone": self.chef_tel.text().strip(),
            "pin": self.chef_pin.text().strip() or "0000"
        }
        try:
            res = requests.post(f"{API_URL}/chefs", json=payload)
            if res.status_code == 200:
                QMessageBox.information(None, "Bravo !", "Chef et code PIN enregistrés avec succès !")
                self.chef_nom.clear()
                self.chef_tel.clear()
                self.chef_pin.clear()
                self.load_chefs()
            else:
                QMessageBox.warning(None, "Attention", res.json().get("detail", "Erreur"))
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Erreur : {e}")

    def apply_and_save_config(self):
        self.config["dossier_source"] = self.input_source.text().strip()
        self.config["dossier_drive"] = self.input_drive.text().strip()
        self.save_config_file()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())