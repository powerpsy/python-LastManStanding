#!/usr/bin/env python3
"""
Test spécifique des nouvelles transitions d'upgrade avec wipe vertical split
"""

import pygame
import sys
sys.path.append('.')
from game import Game
from config import Config

def test_upgrade_transitions():
    """Test des nouvelles transitions d'upgrade"""
    pygame.init()
    
    config = Config(forced_screen_size=2)  # 1080p pour test rapide
    config.PLAYER_SPRITE_TYPE = 2
    
    game = Game(config)
    
    print("🧪 TEST NOUVELLES TRANSITIONS UPGRADE")
    print("=====================================")
    print("✅ NOUVELLES TRANSITIONS UPGRADE :")
    print("  🔄 Level Up → Upgrade Screen : wipe_vertical_split")
    print("     (Gauche de haut en bas + Droite de bas en haut)")
    print("  🔄 Upgrade → Retour Jeu : wipe_vertical_split_reverse")
    print("     (Gauche de bas en haut + Droite de haut en bas)")
    print()
    print("🎮 POUR TESTER RAPIDEMENT :")
    print("  - Tuez quelques ennemis pour gagner de l'XP")
    print("  - Ou modifiez main.py : test_always_skip=True")
    print("  - Ou attendez le level up automatique")
    print()
    print("⚡ EFFET ATTENDU :")
    print("  - Transition en 2 parties simultanées")
    print("  - Effet visuel style 'portes qui s'ouvrent/ferment'")
    print("  - Durée : 0.4s (optimisée)")
    print()
    print("Appuyez sur ESC pour quitter")
    print("=====================================")
    
    # Pour test rapide, donner plus d'XP au joueur
    game.player.experience = 95  # Proche du level up
    print(f"XP initial: {game.player.experience}/100 (proche du level up)")
    
    game.run()
    
    pygame.quit()

if __name__ == "__main__":
    test_upgrade_transitions()
