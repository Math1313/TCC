# 🚀 Trello Card Copier

Application simple pour copier des cartes Trello d'un tableau vers plusieurs tableaux en filtrant par label.

## 📦 Installation

```bash
pip install customtkinter requests python-dotenv
```

## 🚀 Lancement

```bash
python main.py
```

## ⚙️ Configuration

Créez un fichier `.env` à la racine avec vos clés Trello :

```env
TRELLO_API_KEY=votre_clé_api
TRELLO_TOKEN=votre_token
```

**Obtenir vos clés :**
1. API Key : https://trello.com/app-key
2. Cliquez sur "Token" pour générer un token

## 📋 Utilisation

1. **Source Board ID** : ID du tableau source (dans l'URL : `trello.com/b/ABC123`)
2. **Target Board IDs** : Un ID par ligne
3. **Label Name** : Nom exact du label à copier
4. Cliquer sur **Copier les Cartes**

## 🎯 Fonctionnalités

- Interface graphique moderne (thème sombre/clair)
- Copie vers plusieurs tableaux simultanément
- Conservation des descriptions, checklists et labels
- Sauvegarde automatique de la configuration
- Logs en temps réel

## 📁 Structure

```
TCC/
├── src/              # Code source
│   ├── config.py     # Gestion configuration
│   ├── gui.py        # Interface graphique
│   ├── main.py       # Point d'entrée
│   └── trello_api.py # Client API Trello
├── main.py           # Lanceur
└── config.json       # Config sauvegardée (auto-généré)
```

## 🔧 Développement

Le code est organisé dans le dossier `src/` :
- `config.py` : Charge/sauvegarde les paramètres
- `trello_api.py` : Toutes les requêtes API Trello
- `gui.py` : Interface CustomTkinter
- `main.py` : Initialise et lance l'app
