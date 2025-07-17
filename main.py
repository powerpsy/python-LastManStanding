#!/usr/bin/env python3
"""
Last Man Standing - Jeu d'Action 2D
===================================

"""

import pygame
import sys
from game import Game
from config import Config

def main():
    """Fonction principale du jeu"""
    # === CONFIGURATION DE TEST ===
    # Choisir la taille d'écran pour les tests :
    # 1 = 1280x720 (720p)
    # 2 = 1920x1080 (1080p) 
    # 3 = 2560x1440 (1440p)
    # None = Détection automatique selon l'écran
    screen_size = 3  # Test en 1440p pour ajustements
    
    # Mode test "Always Skip" - pour tester rapidement le système
    test_always_skip = False  # Mettre True pour tester
    
    try:
        # Initialise Pygame
        pygame.init()
        
        # Crée et lance une nouvelle partie
        config = Config(forced_screen_size=screen_size)
        game = Game(config)
        
        # Si mode test activé, simuler une situation où toutes les upgrades sont au max
        if test_always_skip:
            print("🧪 MODE TEST ALWAYS SKIP ACTIVÉ")
            # Simuler qu'on a atteint tous les niveaux max (simplifié)
            game.level = 50  # Niveau élevé
            # Cette ligne sera décommentée pour le test réel
            # game.upgrade_options = []  # Pas d'options disponibles
        
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
