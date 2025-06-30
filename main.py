#!/usr/bin/env python3
"""
Last Man Standing - Jeu d'Action 2D
===================================

Un jeu d'action en temps réel où le joueur doit survivre à des vagues
d'ennemis de plus en plus nombreuses et difficiles.

Fonctionnalités:
- Contrôles WASD avec inertie
- Tir automatique d'éclairs vers les ennemis
- Ennemis qui suivent le joueur avec IA
- Vagues progressives de difficulté croissante
- Interface graphique paramétrable
- Système de progression et d'upgrades

Auteur: GitHub Copilot
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
