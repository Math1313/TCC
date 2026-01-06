"""
Point d'entrée principal de l'application Trello Card Copier
Lance l'interface graphique
"""

import sys
import traceback
from .gui import TrelloGUI


def main():
    """Fonction principale de l'application"""
    try:
        # Créer et lancer l'interface graphique
        app = TrelloGUI()
        app.run()
    except Exception as e:
        print(f"❌ Erreur fatale lors du démarrage de l'application:")
        print(f"   {str(e)}")
        print("\n📋 Détails de l'erreur:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
