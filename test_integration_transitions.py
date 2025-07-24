#!/usr/bin/env python3
"""
Test d'intégration des transitions dans le jeu principal
=======================================================
Ce script teste rapidement les transitions intégrées dans le jeu.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_transitions():
    """Teste les transitions intégrées dans le jeu"""
    pygame.init()
    
    # Configuration
    config = Config()
    config.WINDOW_WIDTH = 1280
    config.WINDOW_HEIGHT = 720
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Transitions Intégrées")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    test_phase = 0
    last_test_time = pygame.time.get_ticks()
    
    print("🎮 Test des transitions intégrées dans le jeu")
    print("Phase 0: Jeu normal - Appuyez sur TAB pour voir transition compétences")
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Test: Forcer une montée de niveau pour tester la transition d'upgrade
                    if not game.show_upgrade_screen and not game.paused_skills:
                        print("🔄 Test: Déclenchement transition vers écran d'upgrade")
                        game.trigger_upgrade_screen()
                elif event.key == pygame.K_TAB:
                    # Test: Écran des compétences
                    if not game.show_upgrade_screen and not game.paused_skills:
                        print("🔄 Test: Déclenchement transition vers écran compétences")
                        game.transition_to_skills_screen()
                elif event.key == pygame.K_g:
                    # Test: Game over
                    if not game.game_over:
                        print("🔄 Test: Déclenchement transition game over")
                        game.transition_to_game_over()
        
        # Permettre au jeu de traiter ses propres événements aussi
        game.handle_events()
        
        # Mise à jour
        game.update()
        
        # Affichage
        game.draw()
        
        # Tests automatiques
        if current_time - last_test_time > 5000:  # Toutes les 5 secondes
            if test_phase == 0 and not game.transition_manager.is_active:
                print("Phase 1: Test transition écran compétences automatique...")
                game.transition_to_skills_screen()
                test_phase = 1
            elif test_phase == 1 and not game.transition_manager.is_active and game.paused_skills:
                print("Phase 2: Retour du test écran compétences...")
                game.transition_from_skills_screen()
                test_phase = 2
            elif test_phase == 2 and not game.transition_manager.is_active:
                print("Phase 3: Test transition écran upgrade automatique...")
                game.trigger_upgrade_screen()
                test_phase = 3
            
            last_test_time = current_time
        
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test terminé")

if __name__ == "__main__":
    print("Instructions de test:")
    print("- ESPACE: Déclencher transition vers écran d'upgrade")
    print("- TAB: Déclencher transition vers écran compétences")
    print("- G: Déclencher transition game over")
    print("- ESC: Quitter")
    print("- Tests automatiques toutes les 5 secondes")
    print()
    
    test_transitions()
