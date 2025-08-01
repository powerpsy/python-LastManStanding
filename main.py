#!/usr/bin/env python3
"""
Last Man Standing - Jeu d'Action 2D
"""

import pygame
import sys
from game import Game
from config import Config

def main():
    """Fonction principale du jeu"""
    # === CONFIGURATION DE LA RESOLUTION ===
    # 1 = 1280x720 (720p)
    # 2 = 1920x1080 (1080p) 
    # 3 = 2560x1440 (1440p)
    # None = Détection automatique selon l'écran
    screen_size = 3  # Test en 1440p pour ajustements
    
    # === TYPE DE SPRITE JOUEUR ===
    # Type de sprite joueur à utiliser :
    # 1 = player2.png (Guerrier - Défensif avec orbes protectrices)
    # 2 = player3.png (Mage - Équilibré avec armes projectiles améliorées) 
    # 3 = player4.png (Assassin - Rapide avec éclairs destructeurs)
    # Les animations ont une durée d'environ 1 seconde pour une fluidité cohérente
    player_sprite_type = 1  # Choisir 1, 2 ou 3
    
    try:
        pygame.init()
        
        # Crée et lance une nouvelle partie
        config = Config(forced_screen_size=screen_size)
        config.PLAYER_SPRITE_TYPE = player_sprite_type  # Ajouter le type de sprite à la config
        
        # Afficher le profil sélectionné
        from player_profiles import PlayerProfileManager
        profile = PlayerProfileManager.get_profile(player_sprite_type)
        print(f"🎮 Profil sélectionné: {profile.name} - {profile.description}")
        
        game = Game(config)
        
        game.run()
        
    except KeyboardInterrupt:
        print("\nJeu interrompu par l'utilisateur.")
        
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()