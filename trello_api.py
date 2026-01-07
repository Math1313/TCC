"""
Module pour l'interaction avec l'API Trello
Contient toutes les fonctions pour gérer les cartes, listes, labels et checklists
"""

import requests
from typing import List, Dict, Optional, Tuple, Callable


class TrelloClient:
    """Client pour interagir avec l'API Trello"""
    
    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.headers = {"Accept": "application/json"}
    
    def get_cards_with_label(self, board_id: str, label_name: str) -> List[Dict]:
        """Récupère toutes les cartes avec une étiquette spécifique"""
        url = f"https://api.trello.com/1/boards/{board_id}/cards"
        query = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'id,name,desc,idList,labels',
            'checklists': 'all'
        }
        
        response = requests.get(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            cards = response.json()
            # Filtrer par étiquette
            filtered_cards = []
            for card in cards:
                for label in card.get('labels', []):
                    if label.get('name') == label_name:
                        filtered_cards.append(card)
                        break
            return filtered_cards
        else:
            raise Exception(f"Erreur lors de la récupération des cartes: {response.status_code}")
    
    def get_card_checklists(self, card_id: str) -> List[Dict]:
        """Récupère les checklists d'une carte"""
        url = f"https://api.trello.com/1/cards/{card_id}/checklists"
        query = {'key': self.api_key, 'token': self.token}
        
        response = requests.get(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def create_card(self, name: str, desc: str, list_id: str, label_ids: List[str]) -> Optional[Dict]:
        """Crée une nouvelle carte"""
        url = "https://api.trello.com/1/cards"
        query = {
            'key': self.api_key,
            'token': self.token,
            'idList': list_id,
            'name': name,
            'desc': desc,
            'idLabels': ','.join(label_ids) if label_ids else ''
        }
        
        response = requests.post(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erreur lors de la création de la carte '{name}': {response.status_code}")
    
    def create_checklist(self, card_id: str, checklist_name: str, items: List[Dict]) -> Optional[Dict]:
        """Crée une checklist sur une carte"""
        url = "https://api.trello.com/1/checklists"
        query = {
            'key': self.api_key,
            'token': self.token,
            'idCard': card_id,
            'name': checklist_name
        }
        
        response = requests.post(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            checklist = response.json()
            # Ajouter les items à la checklist
            for item in items:
                self.add_checklist_item(checklist['id'], item['name'], item.get('state') == 'complete')
            return checklist
        else:
            raise Exception(f"Erreur lors de la création de la checklist '{checklist_name}': {response.status_code}")
    
    def add_checklist_item(self, checklist_id: str, item_name: str, checked: bool = False) -> bool:
        """Ajoute un item à une checklist"""
        url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
        query = {
            'key': self.api_key,
            'token': self.token,
            'name': item_name,
            'checked': 'true' if checked else 'false'
        }
        
        response = requests.post(url, headers=self.headers, params=query)
        return response.status_code == 200
    
    def get_board_labels(self, board_id: str) -> List[Dict]:
        """Récupère les labels d'un tableau"""
        url = f"https://api.trello.com/1/boards/{board_id}/labels"
        query = {'key': self.api_key, 'token': self.token}
        
        response = requests.get(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_board_lists(self, board_id: str) -> List[Dict]:
        """Récupère toutes les listes d'un tableau"""
        url = f"https://api.trello.com/1/boards/{board_id}/lists"
        query = {'key': self.api_key, 'token': self.token}
        
        response = requests.get(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_list_name(self, list_id: str) -> Optional[str]:
        """Récupère le nom d'une liste"""
        url = f"https://api.trello.com/1/lists/{list_id}"
        query = {'key': self.api_key, 'token': self.token, 'fields': 'name'}
        
        response = requests.get(url, headers=self.headers, params=query)
        
        if response.status_code == 200:
            return response.json().get('name')
        return None
    
    def find_or_create_labels(self, target_board_id: str, label_names_and_colors: List[Tuple[str, str]]) -> List[str]:
        """Trouve ou crée les labels dans le tableau de destination"""
        existing_labels = self.get_board_labels(target_board_id)
        label_ids = []
        
        for label_name, label_color in label_names_and_colors:
            # Chercher si le label existe déjà
            found = False
            for existing_label in existing_labels:
                if existing_label.get('name') == label_name:
                    label_ids.append(existing_label['id'])
                    found = True
                    break
            
            # Si le label n'existe pas, le créer
            if not found:
                url = f"https://api.trello.com/1/boards/{target_board_id}/labels"
                query = {
                    'key': self.api_key,
                    'token': self.token,
                    'name': label_name,
                    'color': label_color
                }
                response = requests.post(url, headers=self.headers, params=query)
                if response.status_code == 200:
                    new_label = response.json()
                    label_ids.append(new_label['id'])
        
        return label_ids
    
    def copy_card_to_board(self, card: Dict, target_board_id: str, target_lists_map: Dict[str, str], 
                           log_callback: Optional[Callable[[str], None]] = None) -> bool:
        """Copie une carte vers un tableau cible"""
        def log(message: str):
            if log_callback:
                log_callback(message)
        
        # Récupérer le nom de la liste source
        source_list_name = self.get_list_name(card['idList'])
        
        if not source_list_name:
            log(f"✗ Impossible de récupérer la liste source pour '{card['name']}'")
            return False
        
        # Trouver la liste de destination avec le même nom
        target_list_id = target_lists_map.get(source_list_name)
        
        if not target_list_id:
            log(f"✗ Liste '{source_list_name}' introuvable dans le tableau de destination pour '{card['name']}'")
            return False
        
        log(f"📋 Copie de la carte: {card['name']} → Liste: {source_list_name}")
        
        # Préparer les labels
        label_names_and_colors = [(label.get('name', ''), label.get('color', None)) for label in card.get('labels', [])]
        target_label_ids = self.find_or_create_labels(target_board_id, label_names_and_colors)
        
        # Créer la nouvelle carte
        try:
            new_card = self.create_card(
                name=card['name'],
                desc=card.get('desc', ''),
                list_id=target_list_id,
                label_ids=target_label_ids
            )
            
            if new_card:
                # Copier les checklists
                checklists = self.get_card_checklists(card['id'])
                for checklist in checklists:
                    self.create_checklist(
                        card_id=new_card['id'],
                        checklist_name=checklist['name'],
                        items=checklist.get('checkItems', [])
                    )
                
                log(f"✓ Carte copiée avec succès: {new_card['url']}")
                return True
            else:
                log(f"✗ Échec de la copie de la carte")
                return False
        except Exception as e:
            log(f"✗ Erreur: {str(e)}")
            return False
    
    def copy_cards_to_multiple_boards(self, source_board_id: str, target_board_ids: List[str], 
                                     label_name: str, log_callback: Optional[Callable[[str], None]] = None) -> Dict[str, any]:
        """
        Copie les cartes avec un label spécifique vers plusieurs tableaux
        
        Returns:
            Dict contenant les statistiques de copie (total, success, failed)
        """
        def log(message: str):
            if log_callback:
                log_callback(message)
        
        log(f"🔍 Récupération des cartes avec l'étiquette '{label_name}'...")
        
        try:
            # Récupérer les cartes à copier
            cards_to_copy = self.get_cards_with_label(source_board_id, label_name)
            log(f"📊 Nombre de cartes trouvées: {len(cards_to_copy)}")
            
            if len(cards_to_copy) == 0:
                log("⚠️ Aucune carte à copier.")
                return {"total": 0, "success": 0, "failed": 0}
            
            total_copied = 0
            total_failed = 0
            
            # Pour chaque tableau cible
            for target_board_id in target_board_ids:
                log(f"\n{'='*60}")
                log(f"🎯 Copie vers le tableau: {target_board_id}")
                log(f"{'='*60}")
                
                # Récupérer les listes du tableau de destination
                target_lists = self.get_board_lists(target_board_id)
                target_lists_map = {lst['name']: lst['id'] for lst in target_lists}
                log(f"📝 Listes trouvées: {', '.join(target_lists_map.keys())}")
                
                copied_count = 0
                failed_count = 0
                
                # Copier chaque carte
                for card in cards_to_copy:
                    if self.copy_card_to_board(card, target_board_id, target_lists_map, log_callback):
                        copied_count += 1
                    else:
                        failed_count += 1
                
                log(f"\n📈 Résumé pour {target_board_id}: {copied_count} copiées, {failed_count} échouées")
                total_copied += copied_count
                total_failed += failed_count
            
            log(f"\n{'='*60}")
            log(f"✅ RÉSUMÉ GLOBAL: {total_copied} cartes copiées, {total_failed} échouées sur {len(target_board_ids)} tableau(x)")
            log(f"{'='*60}")
            
            return {
                "total": len(cards_to_copy) * len(target_board_ids),
                "success": total_copied,
                "failed": total_failed
            }
            
        except Exception as e:
            log(f"❌ Erreur critique: {str(e)}")
            return {"total": 0, "success": 0, "failed": 0, "error": str(e)}
