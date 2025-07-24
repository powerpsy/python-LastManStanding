#!/usr/bin/env python3
"""
Last Man Standing - Jeu d'Action 2D
===================================

"""

import pygame
import sys
from game import Game
from config import Config

def main():
    """Fonction principale du jeu"""
    # === CONFIGURATION DE TEST ===
    # Choisir la taille d'écran pour les tests :
    # 1 = 1280x720 (720p)
    # 2 = 1920x1080 (1080p) 
    # 3 = 2560x1440 (1440p)
    # None = Détection automatique selon l'écran
    screen_size = 3  # Test en 1440p pour ajustements
    
    # === TYPE DE SPRITE JOUEUR ===
    # Type de sprite joueur à utiliser :
    # 1 = player2.png (5 frames horizontales, animation séquence 5-4-3-2-1 en boucle)
    # 2 = player3.png (9 frames horizontales, animation séquence 1-2-3-4-5-6-7-8-9 en boucle)
    # Les deux animations ont une durée d'environ 1 seconde pour une fluidité cohérente
    player_sprite_type = 2  # Choisir 1 ou 2
    
    # Mode test "Always Skip" - pour tester rapidement le système
    test_always_skip = False  # Mettre True pour tester
    test_survival_timer = False  # Mettre True pour tester le timer de survie
    test_lightning_effects = False  # Mettre True pour tester les effets de lightning
    test_beam_effects = False  # Mettre True pour tester les effets de beam
    test_shield_effects = False  # Mettre True pour tester les boucliers
    test_force_shooters = False  # Mettre True pour forcer des ennemis tireurs
    
    try:
        # Initialise Pygame
        pygame.init()
        
        # Crée et lance une nouvelle partie
        config = Config(forced_screen_size=screen_size)
        config.PLAYER_SPRITE_TYPE = player_sprite_type  # Ajouter le type de sprite à la config
        game = Game(config)
        
        # Si mode test activé, simuler une situation où toutes les upgrades sont au max
        if test_always_skip:
            print("🧪 MODE TEST ALWAYS SKIP ACTIVÉ")
            # Simuler qu'on a atteint tous les niveaux max (simplifié)
            game.level = 50  # Niveau élevé
            # Cette ligne sera décommentée pour le test réel
            # game.upgrade_options = []  # Pas d'options disponibles
        
        # Si mode test timer activé, réduire la santé pour tester le game over
        if test_survival_timer:
            print("🧪 MODE TEST SURVIVAL TIMER ACTIVÉ")
            game.player.health = 20  # Santé très faible pour test rapide
        
        # Si mode test lightning activé, débloquer automatiquement le Lightning
        if test_lightning_effects:
            print("🧪 MODE TEST LIGHTNING EFFECTS ACTIVÉ")
            from weapons import LightningWeapon
            game.weapon_manager.add_weapon(LightningWeapon)
            print("Lightning débloqué pour tester les effets de particules !")
        
        # Si mode test beam activé, débloquer automatiquement le Beam
        if test_beam_effects:
            print("🧪 MODE TEST BEAM EFFECTS ACTIVÉ")
            from weapons import BeamWeapon
            game.weapon_manager.add_weapon(BeamWeapon)
            print("Beam débloqué pour tester les dégâts !")
        
        # Si mode test shield activé, donner un bouclier au joueur
        if test_shield_effects:
            print("🧪 MODE TEST SHIELD EFFECTS ACTIVÉ")
            game.bonus_manager.apply_bonus("shield", game)
            print("Bouclier activé pour tester les projectiles ennemis !")
        
        # Si mode test force shooters activé, forcer des ennemis tireurs
        if test_force_shooters:
            print("🧪 MODE TEST FORCE SHOOTERS ACTIVÉ")
            # Passer le mode test à la config pour forcer les tireurs
            game.config.FORCE_SHOOTER_ENEMIES = True
            print("Mode tireurs forcés activé !")
        
        game.run()
        
    except KeyboardInterrupt:
        print("\nJeu interrompu par l'utilisateur.")
        
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
