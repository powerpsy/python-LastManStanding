#!/usr/bin/env python3
"""
Test rapide des transitions TAB (Skills Screen)
"""

import pygame
import sys
sys.path.append('.')
from game import Game
from config import Config

def test_transitions_tab():
    """Test spécifique des transitions TAB"""
    pygame.init()
    
    config = Config(forced_screen_size=2)  # 1080p pour test rapide
    config.PLAYER_SPRITE_TYPE = 2
    
    game = Game(config)
    
    print("🧪 TEST TRANSITIONS TAB")
    print("Instructions:")
    print("- Appuyez sur TAB pour tester la transition vers Skills")
    print("- Appuyez à nouveau sur TAB pour tester le retour")
    print("- Appuyez sur ESC pour quitter")
    print("- Vérifiez qu'il n'y a pas d'écran noir pendant les transitions")
    
    game.run()
    
    pygame.quit()

if __name__ == "__main__":
    test_transitions_tab()
