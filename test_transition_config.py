#!/usr/bin/env python3
"""
Test du nouveau système de configuration des transitions
========================================================
Démontre comment facilement ajuster la vitesse de toutes les transitions
"""

import pygame
import sys
sys.path.append('.')
from game import Game
from config import Config

def test_transition_config():
    """Test avec différentes vitesses de transition"""
    pygame.init()
    
    print("🎛️ TEST SYSTÈME DE CONFIGURATION DES TRANSITIONS")
    print("=" * 60)
    print()
    
    # Demander à l'utilisateur quelle vitesse tester
    print("Choisissez la vitesse des transitions à tester :")
    print("1. ⚡ Ultra-rapide (0.1s)")
    print("2. 🚀 Rapide (0.2s) - Par défaut")
    print("3. ⚙️ Normal (0.5s)")
    print("4. 🐌 Lent (1.0s)")
    print("5. 🔥 Personnalisé")
    print()
    
    try:
        choice = input("Votre choix (1-5) : ").strip()
        
        config = Config(forced_screen_size=2)  # 1080p pour test
        config.PLAYER_SPRITE_TYPE = 2
        
        # Appliquer la durée choisie
        if choice == "1":
            config.TRANSITION_DURATION = 0.1
            speed_name = "Ultra-rapide"
        elif choice == "2":
            config.TRANSITION_DURATION = 0.2
            speed_name = "Rapide"
        elif choice == "3":
            config.TRANSITION_DURATION = 0.5
            speed_name = "Normal"
        elif choice == "4":
            config.TRANSITION_DURATION = 1.0
            speed_name = "Lent"
        elif choice == "5":
            try:
                custom_duration = float(input("Durée personnalisée (en secondes, ex: 0.3) : "))
                config.TRANSITION_DURATION = custom_duration
                speed_name = f"Personnalisé ({custom_duration}s)"
            except ValueError:
                print("Valeur invalide, utilisation de la valeur par défaut (0.2s)")
                config.TRANSITION_DURATION = 0.2
                speed_name = "Par défaut"
        else:
            print("Choix invalide, utilisation de la valeur par défaut (0.2s)")
            config.TRANSITION_DURATION = 0.2
            speed_name = "Par défaut"
        
        print()
        print("🎯 CONFIGURATION APPLIQUÉE :")
        print(f"   Vitesse : {speed_name}")
        print(f"   Durée : {config.TRANSITION_DURATION}s")
        print()
        print("📋 TRANSITIONS À TESTER :")
        print("   🛡️ TAB : Écran skills (diagonal)")
        print("   🔄 Level Up : Écran upgrade (wipe split)")  
        print("   🚪 ESC : Menu exit (fade)")
        print("   💀 Game Over : Écran final (wipe horizontal)")
        print()
        print("🎮 LANCEMENT DU TEST...")
        print("=" * 60)
        
        game = Game(config)
        game.run()
        
    except KeyboardInterrupt:
        print("\nTest interrompu par l'utilisateur.")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_transition_config()
