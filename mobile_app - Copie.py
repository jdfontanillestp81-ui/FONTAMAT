from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import traceback

class DiagnosticApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20)
        try:
            # Test des importations critiques
            import requests
            import json
            import os
            
            # Si tout est OK, on affiche un message de succès
            layout.add_widget(Label(
                text="[b]DIAGNOSTIC : SUCCÈS ![/b]\nLes modules Kivy et Requests sont bien chargés.",
                markup=True,
                font_size=18,
                color=(0.1, 0.8, 0.2, 1)
            ))
        except Exception as e:
            # Si une erreur survient, on l'affiche lisiblement à l'écran
            erreur_complete = traceback.format_exc()
            layout.add_widget(Label(
                text=f"[b]ERREUR DÉTECTÉE :[/b]\n{erreur_complete}",
                markup=True,
                font_size=12,
                color=(1, 0.2, 0.2, 1)
            ))
        return layout

if __name__ == '__main__':
    DiagnosticApp().run()