#!/usr/bin/env python3
"""
Test final des transitions intégrées
===================================
Test rapide pour valider que les transitions fonctionnent correctement.
"""

import pygame
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transitions import TransitionManager

def test_simple_transitions():
    """Test simple des transitions avec capture d'écran automatique"""
    pygame.init()
    
    # Configuration
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Test Transitions Simples")
    
    # Créer le gestionnaire de transitions
    transition_manager = TransitionManager(WIDTH, HEIGHT)
    
    # Variables de test
    clock = pygame.time.Clock()
    running = True
    current_screen = 0  # 0 = jeu, 1 = menu
    transition_active = False
    last_transition = pygame.time.get_ticks()
    
    # Liste des effets de transition à tester
    effects = [
        "iris_close",
        "wipe_horizontal_left_to_right", 
        "wipe_vertical_top_to_bottom",
        "diagonal_top_left_to_bottom_right",
        "wipe_horizontal_right_to_left",
        "wipe_vertical_bottom_to_top",
        "diagonal_bottom_right_to_top_left",
        "iris_open"
    ]
    current_effect_index = 0
    
    font = pygame.font.Font(None, 48)
    
    print("🎮 Test simple des transitions")
    print("Appuyez sur ESPACE pour déclencher des transitions automatiques")
    print(f"Effet actuel: {effects[current_effect_index]}")
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT and not transition_manager.is_active:
                    # Changer d'effet de transition
                    current_effect_index = (current_effect_index + 1) % len(effects)
                    print(f"Effet actuel: {effects[current_effect_index]}")
                elif event.key == pygame.K_LEFT and not transition_manager.is_active:
                    # Changer d'effet de transition (précédent)
                    current_effect_index = (current_effect_index - 1) % len(effects)
                    print(f"Effet actuel: {effects[current_effect_index]}")
                elif event.key == pygame.K_SPACE and not transition_manager.is_active:
                    # Déclencher une transition
                    # D'abord capturer l'écran actuel
                    old_surface = screen.copy()
                    
                    # Changer l'état de l'écran
                    new_screen = 1 - current_screen
                    
                    # Dessiner temporairement le nouvel écran pour le capturer
                    temp_surface = pygame.Surface((WIDTH, HEIGHT))
                    if new_screen == 0:
                        # Écran de jeu (bleu)
                        temp_surface.fill((30, 50, 150))
                        text = font.render("ÉCRAN JEU", True, (255, 255, 255))
                        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                        temp_surface.blit(text, text_rect)
                        
                        # Dessiner des éléments de jeu simulés
                        for i in range(5):
                            pygame.draw.circle(temp_surface, (255, 255, 0), 
                                             (100 + i * 120, HEIGHT//2 + 50), 20)
                    else:
                        # Écran de menu (rouge)
                        temp_surface.fill((150, 30, 50))
                        text = font.render("ÉCRAN MENU", True, (255, 255, 255))
                        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                        temp_surface.blit(text, text_rect)
                        
                        # Dessiner des éléments de menu simulés
                        for i in range(3):
                            pygame.draw.rect(temp_surface, (200, 200, 200), 
                                           (WIDTH//2 - 100, HEIGHT//2 + i * 60 - 20, 200, 40))
                    
                    # Maintenant démarrer la transition avec les deux surfaces
                    def change_screen():
                        nonlocal current_screen
                        current_screen = new_screen
                    
                    transition_manager.start_transition_with_surfaces(
                        old_surface=old_surface,
                        new_surface=temp_surface,
                        effect_name=effects[current_effect_index],
                        duration=1.5,
                        on_complete=change_screen
                    )
                    
                    print(f"🔄 Transition déclenchée: {current_screen} -> {new_screen} avec {effects[current_effect_index]}")
        
        # Mise à jour des transitions
        transition_manager.update()
        
        # Dessiner l'écran selon l'état actuel (seulement si pas de transition active)
        if not transition_manager.is_active:
            if current_screen == 0:
                # Écran de jeu (bleu)
                screen.fill((30, 50, 150))
                text = font.render("ÉCRAN JEU", True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                screen.blit(text, text_rect)
                
                # Dessiner des éléments de jeu simulés
                for i in range(5):
                    pygame.draw.circle(screen, (255, 255, 0), 
                                     (100 + i * 120, HEIGHT//2 + 50), 20)
            else:
                # Écran de menu (rouge)
                screen.fill((150, 30, 50))
                text = font.render("ÉCRAN MENU", True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                screen.blit(text, text_rect)
                
                # Dessiner des éléments de menu simulés
                for i in range(3):
                    pygame.draw.rect(screen, (200, 200, 200), 
                                   (WIDTH//2 - 100, HEIGHT//2 + i * 60 - 20, 200, 40))
            
            # Instructions
            instruction_text = "ESPACE: Transition  ←→: Changer effet"
            instruction_surface = pygame.font.Font(None, 24).render(instruction_text, True, (255, 255, 255))
            screen.blit(instruction_surface, (10, 10))
            
            # Afficher l'effet actuel
            effect_text = f"Effet: {effects[current_effect_index]}"
            effect_surface = pygame.font.Font(None, 20).render(effect_text, True, (200, 200, 200))
            screen.blit(effect_surface, (10, 35))
        
        # Afficher l'état de transition
        if transition_manager.is_active:
            progress_text = f"Transition: {transition_manager.progress:.2f}"
            progress_surface = pygame.font.Font(None, 24).render(progress_text, True, (255, 255, 0))
            screen.blit(progress_surface, (10, 40))
        
        # Dessiner les transitions par-dessus tout
        transition_manager.render(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Test terminé")

if __name__ == "__main__":
    test_simple_transitions()
