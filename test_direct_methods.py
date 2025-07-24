#!/usr/bin/env python3
"""
Test DEBUG - Méthodes de transition directes
==========================================
Test pour vérifier que les méthodes de transition fonctionnent quand appelées directement.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_direct_transition_methods():
    """Test appel direct des méthodes de transition"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=3)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Méthodes Transition Directes")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    
    print("🔧 TEST MÉTHODES TRANSITION DIRECTES")
    print("=" * 50)
    print("1 : Appel direct transition_to_skills_screen()")
    print("2 : Appel direct transition_to_exit_menu()")
    print("3 : Appel direct trigger_upgrade_screen()")
    print("Q : Quitter")
    print("=" * 50)
    
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("🚪 Fermeture par QUIT")
            elif event.type == pygame.KEYDOWN:
                print(f"🔑 Touche pressée: {pygame.key.name(event.key)}")
                if event.key == pygame.K_q:
                    running = False
                    print("🚪 Fermeture par Q")
                elif event.key == pygame.K_1 and not game.transition_manager.is_active:
                    print("🔧 APPEL DIRECT: transition_to_skills_screen()")
                    try:
                        game.transition_to_skills_screen()
                        print("   ✅ Méthode appelée avec succès")
                    except Exception as e:
                        print(f"   ❌ Erreur: {e}")
                elif event.key == pygame.K_2 and not game.transition_manager.is_active:
                    print("🔧 APPEL DIRECT: transition_to_exit_menu()")
                    try:
                        game.transition_to_exit_menu()
                        print("   ✅ Méthode appelée avec succès")
                    except Exception as e:
                        print(f"   ❌ Erreur: {e}")
                elif event.key == pygame.K_3 and not game.transition_manager.is_active:
                    print("🔧 APPEL DIRECT: trigger_upgrade_screen()")
                    try:
                        game.trigger_upgrade_screen()
                        print("   ✅ Méthode appelée avec succès")
                    except Exception as e:
                        print(f"   ❌ Erreur: {e}")
        
        # NE PAS appeler game.handle_events() pour éviter les interférences
        # Juste mettre à jour les transitions et afficher
        game.transition_manager.update()
        
        # Debug transitions
        if game.transition_manager.is_active:
            effect = game.transition_manager.current_effect
            progress = game.transition_manager.progress
            print(f"    ⚡ {effect}: {progress:.1%}")
        
        # État actuel
        screen_state = "JEU"
        if game.show_upgrade_screen:
            screen_state = "UPGRADE"
        elif game.paused_skills:
            screen_state = "SKILLS"
        elif game.game_over:
            screen_state = "GAME_OVER"
        elif game.show_exit_menu:
            screen_state = "EXIT_MENU"
        
        # Affichage
        game.draw()
        
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test méthodes directes terminé")

if __name__ == "__main__":
    test_direct_transition_methods()
