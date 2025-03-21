# tamagotchi.py
import random
import json

class Tamagotchi:
    def __init__(self, nom):
        self.nom = nom
        self.bonheur = 50
        self.energie = 50
        self.capital_biologique = 100
        self.actions_effectuees = []

    def effectuer_action(self, action):
        if action == "nourrir":
            self.energie += 20
            self.bonheur += 5
            self.vieillissement(1.5)
        elif action == "jouer":
            self.energie -= 30
            self.bonheur += 20
            self.vieillissement(1.3)
        elif action == "ignorer":
            self.energie -= 10
            self.bonheur -= 20
            self.vieillissement(1.0)
        
        self.actions_effectuees.append(action)

    def vieillissement(self, facteur):
        self.capital_biologique -= random.uniform(0.5, 1.0) * facteur

    def est_vivant(self):
        return 0 < self.energie < 150 and 0 < self.bonheur < 150 and self.capital_biologique > 0
    
    def sauvegarder_partie(self, fichier="historique.json"):
        try:
            with open(fichier, "r") as f:
                historique = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            historique = {}
        
        historique[self.nom] = {
            "actions": self.actions_effectuees,
            "etapes": len(self.actions_effectuees)
        }
        
        with open(fichier, "w") as f:
            json.dump(historique, f, indent=4)
