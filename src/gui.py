"""
Interface graphique moderne pour l'application de copie de cartes Trello
Utilise CustomTkinter pour un design moderne
"""

import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import threading
from typing import List
from .config import ConfigManager
from .trello_api import TrelloClient


class TrelloGUI:
    """Interface graphique principale de l'application"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.trello_client = None
        
        # Configuration de l'apparence
        ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Créer la fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Trello Card Copier")
        self.root.geometry("900x800")
        self.root.minsize(700, 600)
        
        # Initialiser le client Trello
        api_key, token = self.config_manager.get_api_credentials()
        self.trello_client = TrelloClient(api_key, token)
        
        self.setup_ui()
        self.load_saved_values()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        
        # Titre principal
        title_label = ctk.CTkLabel(
            self.root,
            text="Trello Card Copier",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Frame principal avec scroll
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Section: Board Source
        self.create_section_label(main_frame, "[SOURCE] Tableau Source")
        
        source_frame = ctk.CTkFrame(main_frame)
        source_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            source_frame,
            text="Source Board ID:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.source_board_entry = ctk.CTkEntry(
            source_frame,
            placeholder_text="Ex: KRoXlMPp",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.source_board_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Section: Tableaux Cibles
        self.create_section_label(main_frame, "[CIBLES] Tableaux Cibles")
        
        target_frame = ctk.CTkFrame(main_frame)
        target_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            target_frame,
            text="Target Board IDs (un par ligne):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.target_boards_text = ctk.CTkTextbox(
            target_frame,
            height=120,
            font=ctk.CTkFont(size=13)
        )
        self.target_boards_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Section: Label
        self.create_section_label(main_frame, "[LABEL] Label a Copier")
        
        label_frame = ctk.CTkFrame(main_frame)
        label_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            label_frame,
            text="Nom du Label:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.label_entry = ctk.CTkEntry(
            label_frame,
            placeholder_text="Ex: Laboratoire 2 - Dockerisation",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.label_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Section: Boutons d'action
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=(0, 20))
        
        buttons_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        buttons_container.pack(pady=15)
        
        self.copy_button = ctk.CTkButton(
            buttons_container,
            text=">> Copier les Cartes",
            command=self.start_copy,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.copy_button.pack(side="left", padx=10)
        
        self.clear_button = ctk.CTkButton(
            buttons_container,
            text="[X] Effacer",
            command=self.clear_logs,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.clear_button.pack(side="left", padx=10)
        
        self.theme_button = ctk.CTkButton(
            buttons_container,
            text="[*] Theme",
            command=self.toggle_theme,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        self.theme_button.pack(side="left", padx=10)
        
        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(main_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.pack_forget()  # Cacher initialement
        
        # Section: Console de logs
        self.create_section_label(main_frame, "[LOGS] Console")
        
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=250,
            font=ctk.CTkFont(family="Courier", size=12),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Message de bienvenue
        self.log("*** Bienvenue dans Trello Card Copier!")
        self.log(">>> Remplissez les champs ci-dessus et cliquez sur 'Copier les Cartes'")
        self.log("-" * 70)
    
    def create_section_label(self, parent, text):
        """Crée un label de section stylisé"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        label.pack(fill="x", pady=(10, 10))
    
    def load_saved_values(self):
        """Charge les valeurs sauvegardées depuis la configuration"""
        # Charger le Source Board ID
        source_board_id = self.config_manager.get_source_board_id()
        if source_board_id:
            self.source_board_entry.insert(0, source_board_id)
        
        # Charger les Target Board IDs
        target_board_ids = self.config_manager.get_target_board_ids()
        if target_board_ids:
            self.target_boards_text.insert("1.0", "\n".join(target_board_ids))
        
        # Charger le Label Name
        label_name = self.config_manager.get_label_name()
        if label_name:
            self.label_entry.insert(0, label_name)
        
        self.log("[OK] Configuration precedente chargee")
    
    def save_values(self):
        """Sauvegarde les valeurs actuelles dans la configuration"""
        source_board_id = self.source_board_entry.get().strip()
        target_boards_text = self.target_boards_text.get("1.0", "end").strip()
        target_board_ids = [line.strip() for line in target_boards_text.split("\n") if line.strip()]
        label_name = self.label_entry.get().strip()
        
        self.config_manager.set_source_board_id(source_board_id)
        self.config_manager.set_target_board_ids(target_board_ids)
        self.config_manager.set_label_name(label_name)
        
        if self.config_manager.save_config():
            self.log("[OK] Configuration sauvegardee avec succes")
        else:
            self.log("[ERREUR] Erreur lors de la sauvegarde de la configuration")
    
    def validate_inputs(self) -> tuple[bool, str]:
        """Valide les entrées utilisateur"""
        source_board_id = self.source_board_entry.get().strip()
        if not source_board_id:
            return False, "[!] Le Source Board ID est requis"
        
        target_boards_text = self.target_boards_text.get("1.0", "end").strip()
        target_board_ids = [line.strip() for line in target_boards_text.split("\n") if line.strip()]
        if not target_board_ids:
            return False, "[!] Au moins un Target Board ID est requis"
        
        label_name = self.label_entry.get().strip()
        if not label_name:
            return False, "[!] Le nom du Label est requis"
        
        return True, ""
    
    def log(self, message: str):
        """Ajoute un message dans la console de logs"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def clear_logs(self):
        """Efface la console de logs"""
        self.log_text.delete("1.0", "end")
        self.log("[OK] Console effacee")
    
    def toggle_theme(self):
        """Bascule entre les thèmes clair et sombre"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.log(f"[*] Theme change: {new_mode}")
    
    def start_copy(self):
        """Démarre le processus de copie dans un thread séparé"""
        # Validation des entrées
        is_valid, error_message = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Erreur de validation", error_message)
            self.log(error_message)
            return
        
        # Confirmation
        source_board_id = self.source_board_entry.get().strip()
        target_boards_text = self.target_boards_text.get("1.0", "end").strip()
        target_board_ids = [line.strip() for line in target_boards_text.split("\n") if line.strip()]
        label_name = self.label_entry.get().strip()
        
        confirm_message = (
            f"Voulez-vous copier les cartes avec le label '{label_name}' "
            f"depuis le tableau {source_board_id} vers {len(target_board_ids)} tableau(x) ?"
        )
        
        if not messagebox.askyesno("Confirmation", confirm_message):
            self.log("[X] Operation annulee par l'utilisateur")
            return
        
        # Désactiver les boutons pendant la copie
        self.copy_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.start()
        
        # Lancer la copie dans un thread séparé
        thread = threading.Thread(target=self.perform_copy, daemon=True)
        thread.start()
    
    def perform_copy(self):
        """Effectue la copie des cartes (exécuté dans un thread séparé)"""
        try:
            source_board_id = self.source_board_entry.get().strip()
            target_boards_text = self.target_boards_text.get("1.0", "end").strip()
            target_board_ids = [line.strip() for line in target_boards_text.split("\n") if line.strip()]
            label_name = self.label_entry.get().strip()
            
            self.log("\n" + "="*70)
            self.log(">>> DEBUT DE LA COPIE")
            self.log("="*70)
            
            # Effectuer la copie
            result = self.trello_client.copy_cards_to_multiple_boards(
                source_board_id=source_board_id,
                target_board_ids=target_board_ids,
                label_name=label_name,
                log_callback=self.log
            )
            
            # Sauvegarder la configuration si succès
            if result["success"] > 0:
                self.save_values()
            
            # Afficher un message de fin
            if "error" in result:
                messagebox.showerror("Erreur", f"Une erreur s'est produite: {result['error']}")
            elif result["failed"] == 0:
                messagebox.showinfo("Succes", f"[OK] {result['success']} carte(s) copiee(s) avec succes!")
            else:
                messagebox.showwarning(
                    "Copie partielle",
                    f"[!] {result['success']} carte(s) copiee(s), {result['failed']} echouee(s)"
                )
            
        except Exception as e:
            error_msg = f"[ERREUR] Erreur critique: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("Erreur", error_msg)
        
        finally:
            # Réactiver les boutons
            self.copy_button.configure(state="normal")
            self.clear_button.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = TrelloGUI()
    app.run()
