#!/usr/bin/env python3
"""
Last Man Standing - Jeu d'Action 2D
"""

import pygame
import sys
from game_manager import GameManager
from config import Config
from game_settings import GameSettings

def main():
    """Fonction principale du jeu"""
    # Charger les paramètres de jeu
    game_settings = GameSettings()
    
    # === CONFIGURATION DE LA RESOLUTION ===
    # Utiliser la configuration sauvegardée ou forcer en 1440p pour les tests
    screen_size = game_settings.get_screen_size()
    if screen_size is None:
        screen_size = 3  # Test en 1440p pour ajustements
    
    try:
        pygame.init()
        
        # Créer la configuration
        config = Config(forced_screen_size=screen_size)
        
        # Créer et lancer le gestionnaire de jeu avec les paramètres
        game_manager = GameManager(config, game_settings)
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