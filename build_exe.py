"""
Script de build pour créer l'exécutable Windows
Ce script utilise PyInstaller pour packager l'application Flask
"""

import PyInstaller.__main__
import os
import shutil

# Nettoyer les anciens builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Configuration PyInstaller
PyInstaller.__main__.run([
    'app.py',                          # Script principal
    '--name=TrelloCardCopier',         # Nom de l'exécutable
    '--onefile',                       # Créer un seul fichier exe
    '--noconsole',                     # Pas de fenêtre console
    '--add-data=templates;templates',  # Inclure le dossier templates
    '--add-data=static;static',        # Inclure le dossier static
    '--add-data=config.json.example;.',# Inclure le fichier exemple
    '--hidden-import=flask',
    '--hidden-import=flask_cors',
    '--hidden-import=requests',
    '--hidden-import=dotenv',
    '--hidden-import=werkzeug',
    '--hidden-import=jinja2',
    '--hidden-import=click',
    '--hidden-import=itsdangerous',
    '--hidden-import=markupsafe',
    '--hidden-import=flaskwebgui',
    '--hidden-import=psutil',
    '--collect-all=flask',
    '--collect-all=flask_cors',
    '--collect-all=flaskwebgui',
    '--icon=NONE',                     # Ajoutez un chemin d'icône si vous en avez une
    '--clean',                         # Nettoyer les fichiers temporaires
])

print("\n✅ Build terminé ! L'exécutable se trouve dans le dossier 'dist'")
print("📦 Fichier: dist/TrelloCardCopier.exe")

# Copier le fichier .env s'il existe
if os.path.exists('.env'):
    shutil.copy('.env', 'dist/.env')
    print("✅ Fichier .env copié dans dist/")
else:
    print("\n⚠️  Attention: fichier .env non trouvé !")
    print("   Créez un fichier .env avec vos clés API Trello à côté de l'exe")

# Copier le fichier config.json s'il existe
if os.path.exists('config.json'):
    shutil.copy('config.json', 'dist/config.json')
    print("✅ Fichier config.json copié dans dist/")

print("\n✅ Build complet ! Vous pouvez maintenant lancer l'exe en double-cliquant dessus.")
