#!/usr/bin/env python3
"""
Test des transitions dans le jeu principal
==========================================
Test spécifique pour déboguer les transitions dans le contexte du jeu.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_game_transitions():
    """Teste les transitions dans le contexte du jeu principal"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=1)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Transitions Jeu Principal")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Modifier pour éviter le trigger automatique de la vague 3
    game.wave_number = 1
    game.enemies_per_wave = 50  # Beaucoup d'enemies pour éviter vague 3
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    test_started = False
    test_start_time = 0
    
    print("🎮 Test des transitions dans le jeu principal")
    print("Instructions:")
    print("- TAB: Transition vers écran compétences")
    print("- ESPACE: Forcer transition vers écran upgrade")
    print("- G: Forcer transition game over")
    print("- ESC: Quitter")
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game.transition_manager.is_active:
                    # Test: Forcer une transition d'upgrade
                    print("🔄 Test: Déclenchement transition vers écran d'upgrade")
                    print(f"Avant transition: show_upgrade_screen={game.show_upgrade_screen}, paused={game.paused}")
                    print(f"Transition manager: is_active={game.transition_manager.is_active}")
                    game.trigger_upgrade_screen()
                    print(f"Après trigger: show_upgrade_screen={game.show_upgrade_screen}, paused={game.paused}")
                    print(f"Transition manager: is_active={game.transition_manager.is_active}, effect={game.transition_manager.current_effect}")
                elif event.key == pygame.K_g and not game.transition_manager.is_active:
                    # Test: Game over
                    if not game.game_over:
                        print("🔄 Test: Déclenchement transition game over")
                        game.transition_to_game_over()
                elif event.key == pygame.K_t and not game.transition_manager.is_active:
                    # Debug: Afficher l'état des transitions
                    print(f"État transition: active={game.transition_manager.is_active}, "
                          f"progress={game.transition_manager.progress:.2f}, "
                          f"pre_state={getattr(game, '_pre_transition_state', 'None')}")
        
        # Permettre au jeu de traiter ses propres événements aussi
        game.handle_events()
        
        # Mise à jour
        game.update()
        
        # Debug: Afficher les états importants
        if current_time % 1000 < 16:  # Toutes les secondes environ
            transition_info = ""
            if game.transition_manager.is_active:
                transition_info = f" | Transition: {game.transition_manager.current_effect} ({game.transition_manager.progress:.2f})"
            
            screen_state = "JEU"
            if game.show_upgrade_screen:
                screen_state = "UPGRADE"
            elif game.paused_skills:
                screen_state = "SKILLS"
            elif game.game_over:
                screen_state = "GAME_OVER"
            
            print(f"État: {screen_state}{transition_info}")
        
        # Affichage
        game.draw()
        
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test terminé")

if __name__ == "__main__":
    test_game_transitions()
