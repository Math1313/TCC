# Instructions pour créer un exécutable Windows

## Prérequis
- Python 3.x installé
- PyInstaller installé : `pip install pyinstaller`

## Méthode 1 : Utiliser le script de build (Recommandé)

Exécutez simplement :
```bash
python build_exe.py
```

L'exécutable sera créé dans le dossier `dist/TrelloCardCopier.exe`

## Méthode 2 : Commande PyInstaller directe

```bash
pyinstaller --onefile --windowed --name=TrelloCardCopier --add-data="templates:templates" --add-data="static:static" --add-data="config.json.example:." --hidden-import=flask --hidden-import=flask_cors --hidden-import=requests --hidden-import=dotenv app.py
```

**Note pour Linux/Mac** : Remplacez `:` par `;` dans les chemins `--add-data` :
```bash
pyinstaller --onefile --windowed --name=TrelloCardCopier --add-data="templates;templates" --add-data="static;static" --add-data="config.json.example;." --hidden-import=flask --hidden-import=flask_cors --hidden-import=requests --hidden-import=dotenv app.py
```

## Configuration pour l'exécution

1. **Créer un fichier .env** à côté de l'exécutable avec vos clés API :
```
TRELLO_API_KEY=votre_api_key
TRELLO_TOKEN=votre_token
```

2. **Structure des fichiers pour la distribution** :
```
TrelloCardCopier.exe
.env
config.json (créé automatiquement au premier lancement)
```

## Options de build

- `--onefile` : Crée un seul fichier .exe
- `--windowed` : Pas de console (utiliser `--console` pour le debug)
- `--add-data` : Inclut les fichiers statiques (templates, CSS, JS)
- `--hidden-import` : Force l'inclusion des modules Flask

## Debug

Si l'application ne démarre pas :
1. Remplacez `--windowed` par `--console` pour voir les erreurs
2. Vérifiez que le fichier .env est présent
3. Vérifiez les logs dans la console

## Taille de l'exécutable

L'exécutable fera environ 20-30 MB car il inclut Python et toutes les dépendances.

Pour réduire la taille, vous pouvez :
- Utiliser UPX : `pyinstaller --upx-dir=chemin/vers/upx ...`
- Créer un mode `--onedir` au lieu de `--onefile` (plus rapide mais plusieurs fichiers)
