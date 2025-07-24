#!/usr/bin/env python3
"""
Test des transitions - Debug spécifique
======================================
Test ultra spécifique pour déboguer le problème de transition.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from game import Game

def test_transition_debug():
    """Test de debug ultra spécifique pour les transitions"""
    pygame.init()
    
    # Configuration simplifiée
    config = Config(forced_screen_size=1)  # 720p pour test rapide
    config.PLAYER_SPRITE_TYPE = 1  # Sprite simple
    
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Test Debug Transitions")
    
    # Créer une instance du jeu
    game = Game(config)
    
    # Empêcher le déclenchement automatique et la mort
    game.wave_number = 1
    game.enemies_per_wave = 999  # Énorme pour éviter auto-trigger
    game.player.health = 999  # Joueur invincible pour le test
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    
    print("🔍 Test DEBUG des transitions")
    print("ESPACE: Test transition upgrade")
    print("ESC: Quitter")
    
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
                    if not game.transition_manager.is_active:
                        print("=" * 50)
                        print("🔄 DÉCLENCHEMENT MANUEL DE TRANSITION")
                        print(f"Avant trigger_upgrade_screen():")
                        print(f"  show_upgrade_screen: {game.show_upgrade_screen}")
                        print(f"  paused: {game.paused}")
                        print(f"  transition_manager.is_active: {game.transition_manager.is_active}")
                        print(f"  transition_manager.current_effect: {game.transition_manager.current_effect}")
                        print(f"  _pre_transition_state: {getattr(game, '_pre_transition_state', 'Non défini')}")
                        
                        game.trigger_upgrade_screen()
                        
                        print(f"Après trigger_upgrade_screen():")
                        print(f"  show_upgrade_screen: {game.show_upgrade_screen}")
                        print(f"  paused: {game.paused}")
                        print(f"  transition_manager.is_active: {game.transition_manager.is_active}")
                        print(f"  transition_manager.current_effect: {game.transition_manager.current_effect}")
                        print(f"  _pre_transition_state: {getattr(game, '_pre_transition_state', 'Non défini')}")
                        print("=" * 50)
                    else:
                        print("⚠️ Transition déjà active!")
        
        # Mise à jour
        game.update()
        
        # Affichage des infos en continu si transition active
        if game.transition_manager.is_active:
            print(f"Transition: {game.transition_manager.current_effect} - Progress: {game.transition_manager.progress:.2f}")
        
        # Affichage
        game.draw()
        
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test terminé")

if __name__ == "__main__":
    test_transition_debug()
