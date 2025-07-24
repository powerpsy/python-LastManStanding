#!/usr/bin/env python3
"""
Test ultra-simple des transitions upgrade
========================================
Test minimal sans gameplay pour isoler le problème des transitions.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_isolated_upgrade_transitions():
    """Test isolé des transitions upgrade"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=1)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Isolé Transitions Upgrade")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    
    print("🎯 TEST ISOLÉ TRANSITIONS UPGRADE")
    print("=" * 50)
    print("U : Déclencher transition upgrade (iris_close)")
    print("R : Déclencher retour upgrade (iris_open)")
    print("M : Déclencher transition menu exit")
    print("Q : Quitter")
    print("=" * 50)
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_u and not game.transition_manager.is_active:
                    print("🔄 TEST TRANSITION VERS UPGRADE (iris_close)...")
                    # Utiliser trigger_upgrade_screen au lieu de transition_to_upgrade_screen
                    # pour générer les options d'upgrade
                    game.trigger_upgrade_screen()
                elif event.key == pygame.K_r and not game.transition_manager.is_active:
                    print("🔄 TEST RETOUR DEPUIS UPGRADE (iris_open)...")
                    # Mettre en état upgrade et faire le retour
                    game.show_upgrade_screen = True
                    game.paused = True
                    game.transition_from_upgrade_screen()
                elif event.key == pygame.K_m and not game.transition_manager.is_active:
                    print("🔄 TEST TRANSITION MENU EXIT...")
                    if not game.show_exit_menu:
                        print("  -> Déclencher transition vers menu exit (fade)")
                        game.transition_to_exit_menu()
                    else:
                        print("  -> Déclencher transition retour menu exit (fade)")
                        game.transition_from_exit_menu()
        
        # NE PAS appeler game.handle_events() ni game.update() pour éviter le gameplay
        # Juste mettre à jour les transitions
        game.transition_manager.update()
        
        # Debug continu des transitions
        if game.transition_manager.is_active:
            effect = game.transition_manager.current_effect
            progress = game.transition_manager.progress
            print(f"  ⚡ {effect}: {progress:.1%}")
        
        # État actuel
        if current_time % 2000 < 16:  # Toutes les 2 secondes
            screen_state = "JEU"
            if game.show_upgrade_screen:
                screen_state = "UPGRADE"
            elif game.paused_skills:
                screen_state = "SKILLS"
            elif game.game_over:
                screen_state = "GAME_OVER"
            elif game.show_exit_menu:
                screen_state = "EXIT_MENU"
            
            transition_info = ""
            if game.transition_manager.is_active:
                transition_info = f" [TRANSITION: {game.transition_manager.current_effect}]"
            
            print(f"📺 État: {screen_state}{transition_info}")
        
        # Affichage
        game.draw()
        
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test isolé terminé")

if __name__ == "__main__":
    test_isolated_upgrade_transitions()
