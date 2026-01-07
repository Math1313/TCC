# 📋 Trello Card Copier - Application Web

Application web moderne pour copier automatiquement des cartes Trello d'un tableau source vers plusieurs tableaux cibles, basée sur un label spécifique.

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration

Créez un fichier `.env` avec vos identifiants Trello :

```env
TRELLO_API_KEY=votre_api_key
TRELLO_TOKEN=votre_token
```

> 💡 **Obtenir vos identifiants :**
> - API Key : https://trello.com/app-key
> - Token : Cliquez sur "Token" sur la page de l'API Key

### 3. Lancer l'application

```bash
python app.py
```

Ouvrez votre navigateur sur `http://localhost:5000`

## 📖 Utilisation

1. **Source Board ID** : ID du tableau Trello source (ex: `KRoXlMPp`)
2. **Target Board IDs** : IDs des tableaux de destination (un par ligne)
3. **Label Name** : Nom exact du label à copier
4. Cliquez sur **🚀 Copier les Cartes**

Les cartes avec le label spécifié seront copiées avec :
- ✅ Nom et description
- ✅ Labels (créés automatiquement si nécessaires)
- ✅ Checklists et items
- ✅ Position dans la liste correspondante

## 🎨 Fonctionnalités

- **Interface moderne** : Design responsive avec thème clair/sombre
- **Logs en temps réel** : Console interactive pour suivre la copie
- **Sauvegarde automatique** : Vos paramètres sont conservés
- **Multi-tableaux** : Copie vers plusieurs tableaux en une fois

## 📁 Structure

```
.
├── app.py              # Backend Flask
├── trello_api.py       # Client API Trello
├── config.py           # Gestion configuration
├── requirements.txt    # Dépendances Python
├── static/
│   ├── style.css      # Styles CSS
│   └── app.js         # JavaScript
└── templates/
    └── index.html     # Interface web
```

## 🛠️ Technologies

- **Backend** : Flask (Python)
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **API** : Trello REST API

## 📝 Notes

- Les identifiants API sont chargés depuis le fichier `.env`
- La configuration utilisateur est sauvegardée dans `config.json`
- Les cartes sont copiées dans les listes du même nom
