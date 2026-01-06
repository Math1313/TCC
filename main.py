"""
Point d'entrée principal de l'application Trello Card Copier
Lance l'interface graphique
"""

import sys
import os

# Ajouter le dossier parent au path pour permettre les imports depuis src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer le main du package src
from src.main import main

if __name__ == "__main__":
    main()
