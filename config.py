"""
Gestion de la configuration de l'application Trello
Sauvegarde et charge les paramètres utilisateur dans un fichier JSON
Les variables sensibles (API key, token) sont chargées depuis .env
"""

import json
import os
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv

# Déterminer le répertoire de base
if getattr(sys, 'frozen', False):
    # Si l'application est packagée avec PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si on est en mode développement
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Charger les variables d'environnement depuis .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "api_key": os.getenv("TRELLO_API_KEY", ""),
    "token": os.getenv("TRELLO_TOKEN", ""),
    "source_board_id": "",
    "target_board_ids": [],
    "label_name": "Laboratoire 2 - Dockerisation"
}


class ConfigManager:
    """Gestionnaire de configuration pour l'application"""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Fusionner avec les valeurs par défaut pour gérer les nouvelles clés
                    config = DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement de la configuration: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Sauvegarde la configuration dans le fichier JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration"""
        self.config[key] = value
    
    def get_source_board_id(self) -> str:
        """Récupère l'ID du tableau source"""
        return self.config.get("source_board_id", "")
    
    def set_source_board_id(self, board_id: str) -> None:
        """Définit l'ID du tableau source"""
        self.config["source_board_id"] = board_id
    
    def get_target_board_ids(self) -> List[str]:
        """Récupère la liste des IDs des tableaux cibles"""
        return self.config.get("target_board_ids", [])
    
    def set_target_board_ids(self, board_ids: List[str]) -> None:
        """Définit la liste des IDs des tableaux cibles"""
        self.config["target_board_ids"] = board_ids
    
    def get_label_name(self) -> str:
        """Récupère le nom du label"""
        return self.config.get("label_name", "")
    
    def set_label_name(self, label_name: str) -> None:
        """Définit le nom du label"""
        self.config["label_name"] = label_name
    
    def get_api_credentials(self) -> tuple[str, str]:
        """Récupère les identifiants API (key, token)"""
        return (
            self.config.get("api_key", ""),
            self.config.get("token", "")
        )
    
    def set_api_credentials(self, api_key: str, token: str) -> None:
        """Définit les identifiants API"""
        self.config["api_key"] = api_key
        self.config["token"] = token
