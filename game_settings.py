#!/usr/bin/env python3
"""
Gestionnaire des paramètres de jeu - Sauvegarde et chargement des préférences utilisateur
"""

import json
import os
from typing import Dict, Any

class GameSettings:
    """Gestionnaire des paramètres de jeu persistants"""
    
    def __init__(self, settings_file: str = "game_config.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "selected_player": 1,  # Joueur sélectionné par défaut (1=Warrior, 2=Mage, 3=Assassin)
            "screen_size": None,   # Taille d'écran forcée (None=auto, 1=720p, 2=1080p, 3=1440p)
            "volume_master": 1.0,  # Volume principal (0.0 à 1.0)
            "volume_sfx": 1.0,     # Volume des effets sonores
            "volume_music": 1.0,   # Volume de la musique
            "show_fps": False,     # Afficher les FPS
            "show_debug": False,   # Afficher les informations de debug
            "controls": {
                "move_up": "z",
                "move_down": "s", 
                "move_left": "q",
                "move_right": "d"
            },
            "graphics": {
                "particles_quality": "high",  # "low", "medium", "high"
                "screen_shake": True,
                "camera_smooth": True
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Charge les paramètres depuis le fichier JSON"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                # Fusionner avec les paramètres par défaut pour gérer les nouvelles options
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                
                # Mise à jour récursive pour les dictionnaires imbriqués
                for key, value in loaded_settings.items():
                    if isinstance(value, dict) and key in settings:
                        settings[key].update(value)
                    else:
                        settings[key] = value
                
                print(f"✅ Paramètres chargés depuis {self.settings_file}")
                return settings
            else:
                print(f"📄 Fichier de configuration non trouvé, utilisation des paramètres par défaut")
                return self.default_settings.copy()
                
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des paramètres: {e}")
            print(f"📄 Utilisation des paramètres par défaut")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Sauvegarde les paramètres dans le fichier JSON"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            print(f"💾 Paramètres sauvegardés dans {self.settings_file}")
            return True
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde des paramètres: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de paramètre"""
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, save_immediately: bool = True) -> None:
        """Définit une valeur de paramètre"""
        keys = key.split('.')
        current = self.settings
        
        # Naviguer jusqu'au dernier niveau
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Définir la valeur finale
        current[keys[-1]] = value
        
        if save_immediately:
            self.save_settings()
    
    def get_selected_player(self) -> int:
        """Récupère le joueur sélectionné"""
        return self.get("selected_player", 1)
    
    def set_selected_player(self, player_id: int) -> None:
        """Définit le joueur sélectionné (1, 2, ou 3)"""
        if player_id in [1, 2, 3]:
            self.set("selected_player", player_id)
            print(f"🎮 Joueur {player_id} sélectionné et sauvegardé")
        else:
            print(f"⚠️ ID de joueur invalide: {player_id}")
    
    def get_screen_size(self) -> Any:
        """Récupère la taille d'écran configurée"""
        return self.get("screen_size", None)
    
    def set_screen_size(self, size: Any) -> None:
        """Définit la taille d'écran"""
        self.set("screen_size", size)
    
    def reset_to_defaults(self) -> None:
        """Remet tous les paramètres aux valeurs par défaut"""
        self.settings = self.default_settings.copy()
        self.save_settings()
        print("🔄 Paramètres remis aux valeurs par défaut")
    
    def __str__(self) -> str:
        """Représentation textuelle des paramètres"""
        return f"GameSettings: {json.dumps(self.settings, indent=2, ensure_ascii=False)}"
