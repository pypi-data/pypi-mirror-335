import json
import os

FICHIER_SAUVEGARDE = "parties.json"

def sauvegarder_partie(nom_joueur, nb_actions, historique_actions):
    """Sauvegarde une partie dans un fichier JSON."""
    partie = {
        "joueur": nom_joueur,
        "nombre_actions": nb_actions,
        "actions": historique_actions
    }

    if os.path.exists(FICHIER_SAUVEGARDE):
        with open(FICHIER_SAUVEGARDE, "r", encoding="utf-8") as f:
            try:
                donnees = json.load(f)
            except json.JSONDecodeError:
                donnees = []
    else:
        donnees = []

    donnees.append(partie)

    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4)

    print("Partie sauvegardée !")
