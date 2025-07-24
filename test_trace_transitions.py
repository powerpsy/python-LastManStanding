#!/usr/bin/env python3
"""
Test Debug ULTRA SIMPLE - Traçage des transitions
==================================================
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_trace_transitions():
    """Test avec traçage complet des transitions"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=3)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Trace Transitions")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    
    print("🔍 TEST TRACE TRANSITIONS")
    print("=" * 50)
    print("Instructions:")
    print("1 : Jouer normalement jusqu'à vague 3 pour tester upgrade auto")
    print("TAB : Test transition skills")
    print("ESC : Test transition menu exit")
    print("Q : Quitter")
    print("=" * 50)
    
    frame_count = 0
    
    while running:
        frame_count += 1
        current_time = pygame.time.get_ticks()
        
        # Affichage debug périodique
        if frame_count % 120 == 0:  # Toutes les 2 secondes à 60 FPS
            screen_state = "JEU"
            if game.show_upgrade_screen:
                screen_state = "UPGRADE"
            elif game.paused_skills:
                screen_state = "SKILLS"
            elif game.game_over:
                screen_state = "GAME_OVER"
            elif game.show_exit_menu:
                screen_state = "EXIT_MENU"
            
            print(f"📺 Frame {frame_count}: État={screen_state}, Wave={game.wave_number}, Transition={game.transition_manager.is_active}")
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_TAB:
                    print("🔑 TAB pressé - Test transition skills")
                    print(f"   Avant: paused_skills={game.paused_skills}, transition_active={game.transition_manager.is_active}")
                elif event.key == pygame.K_ESCAPE:
                    print("🔑 ESC pressé - Test transition menu exit")
                    print(f"   Avant: show_exit_menu={game.show_exit_menu}, transition_active={game.transition_manager.is_active}")
        
        # Traçage de l'état des upgrades
        if game.show_upgrade_screen and frame_count % 60 == 0:  # Chaque seconde
            print(f"🎯 UPGRADE ACTIF: options={len(game.upgrade_options)}, transition={game.transition_manager.is_active}")
        
        # Permettre au jeu de fonctionner normalement
        game.handle_events()
        game.update()
        
        # Traçage des transitions actives
        if game.transition_manager.is_active:
            effect = game.transition_manager.current_effect
            progress = game.transition_manager.progress
            print(f"    ⚡ {effect}: {progress:.1%}")
        
        # Affichage
        game.draw()
        
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test trace terminé")

if __name__ == "__main__":
    test_trace_transitions()
