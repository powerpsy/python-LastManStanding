#!/usr/bin/env python3
"""
Test debug pour les transitions upgrade
======================================
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_upgrade_transitions():
    """Test spécifique pour déboguer les transitions upgrade"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=1)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Debug Transitions Upgrade")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Rendre le joueur VRAIMENT invincible
    game.player.health = 999
    game.player.max_health = 999
    game.player.invulnerable = True  # Ajouter invulnérabilité si ça existe
    
    # Vider la liste des ennemis pour éviter les dégâts
    game.enemies.clear()
    game.enemy_projectiles.clear()
    
    # Forcer une vague élevée pour avoir les upgrades
    game.wave_number = 3
    game.enemies_per_wave = 999  # Pour éviter auto-trigger mais permettre upgrades
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    
    print("🔧 DEBUG TRANSITIONS UPGRADE")
    print("=" * 50)
    print("U : Forcer transition vers upgrade")
    print("ESC : Tester menu exit avec transition")
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
                    print("🔄 FORCER UPGRADE SCREEN...")
                    print(f"  Avant: show_upgrade={game.show_upgrade_screen}, transition_active={game.transition_manager.is_active}")
                    game.trigger_upgrade_screen()
                    print(f"  Après: show_upgrade={game.show_upgrade_screen}, transition_active={game.transition_manager.is_active}")
                elif event.key == pygame.K_ESCAPE and not game.transition_manager.is_active:
                    print("🔄 TESTER MENU EXIT...")
                    if not game.show_exit_menu:
                        print("  -> Ouvrir menu exit")
                        # Pour l'instant sans transition
                        game.show_exit_menu = True
                        game.paused = True
                    else:
                        print("  -> Fermer menu exit")
                        game.show_exit_menu = False
                        game.paused = False
        
        # Permettre au jeu de traiter ses propres événements aussi
        game.handle_events()
        
        # Mise à jour
        game.update()
        
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
    print("✅ Test debug terminé")

if __name__ == "__main__":
    test_upgrade_transitions()
