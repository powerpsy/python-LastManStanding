#!/usr/bin/env python3
"""
Last Man Standing - Jeu d'Action 2D
"""

import pygame
import sys
from game_manager import GameManager
from config import Config

def main():
    """Fonction principale du jeu"""
    # === CONFIGURATION DE LA RESOLUTION ===
    # 1 = 1280x720 (720p)
    # 2 = 1920x1080 (1080p) 
    # 3 = 2560x1440 (1440p)
    # None = Détection automatique selon l'écran
    screen_size = 3  # Test en 1440p pour ajustements
    
    try:
        pygame.init()
        
        # Créer la configuration
        config = Config(forced_screen_size=screen_size)
        
        # Créer et lancer le gestionnaire de jeu
        game_manager = GameManager(config)
        game_manager.run()
        
    except KeyboardInterrupt:
        print("\nJeu interrompu par l'utilisateur.")
        
    except Exception as e:
        import traceback
        print(f"Une erreur s'est produite: {e}")
        print("Traceback complet:")
        traceback.print_exc()
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()