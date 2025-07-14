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
    try:
        # Initialise Pygame
        pygame.init()
        
        # Crée et lance une nouvelle partie
        config = Config()
        game = Game(config)
        game.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Jeu interrompu par l'utilisateur.")
        
    except Exception as e:
        print(f"❌ Une erreur s'est produite: {e}")
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
