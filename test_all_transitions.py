#!/usr/bin/env python3
"""
Test complet des transitions du jeu
====================================
Test final pour valider toutes les transitions Star Wars du jeu.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_all_game_transitions():
    """Test complet de toutes les transitions du jeu"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=1)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Complet Transitions Last Man Standing")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Rendre le joueur invincible pour test
    game.player.health = 999
    game.player.max_health = 999
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    
    print("🎬 TEST COMPLET DES TRANSITIONS STAR WARS")
    print("=" * 60)
    print("Transitions disponibles:")
    print("1. U : Transition UPGRADE (iris_close)")
    print("2. S : Transition SKILLS (diagonal_top_left_to_bottom_right)")
    print("3. G : Transition GAME OVER (wipe_horizontal_left_to_right)")
    print("4. TAB : Retour depuis SKILLS (diagonal_bottom_right_to_top_left)")
    print("5. ESC : Retour depuis autres écrans (iris_open)")
    print("6. Q : Quitter le test")
    print("=" * 60)
    
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
                    print("🌟 Test transition UPGRADE (iris_close)...")
                    game.trigger_upgrade_screen()
                elif event.key == pygame.K_s and not game.transition_manager.is_active:
                    print("🌟 Test transition SKILLS (diagonal_top_left_to_bottom_right)...")
                    game.transition_to_skills_screen()
                elif event.key == pygame.K_g and not game.transition_manager.is_active:
                    print("🌟 Test transition GAME OVER (wipe_horizontal_left_to_right)...")
                    game.transition_to_game_over()
                elif event.key == pygame.K_TAB:
                    if game.paused_skills and not game.transition_manager.is_active:
                        print("🌟 Test retour depuis SKILLS (diagonal_bottom_right_to_top_left)...")
                        game.transition_from_skills_screen()
                elif event.key == pygame.K_ESCAPE:
                    if game.show_upgrade_screen and not game.transition_manager.is_active:
                        print("🌟 Test retour depuis UPGRADE (iris_open)...")
                        game.transition_from_upgrade_screen()
                    elif game.show_exit_menu and not game.transition_manager.is_active:
                        game.show_exit_menu = False
        
        # Permettre au jeu de traiter ses propres événements aussi
        game.handle_events()
        
        # Mise à jour
        game.update()
        
        # Affichage des informations de transition
        if game.transition_manager.is_active:
            effect = game.transition_manager.current_effect
            progress = game.transition_manager.progress
            print(f"  ⚡ {effect}: {progress:.1%}")
        
        # Affichage de l'état actuel
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
            
            print(f"📺 État actuel: {screen_state}{transition_info}")
        
        # Affichage
        game.draw()
        
        clock.tick(60)
    
    pygame.quit()
    print("\n✅ Test complet terminé")
    print("Toutes les transitions Star Wars ont été testées !")

if __name__ == "__main__":
    test_all_game_transitions()
