"""
Gestionnaire principal du jeu
============================

Gère les différents états du jeu : menu de démarrage, jeu principal, options, mini-jeux, etc.
"""

import pygame
import sys
from enum import Enum
from start_map import StartMap
from game import Game


class GameState(Enum):
    """États possibles du jeu"""
    START_MAP = "start_map"
    MAIN_GAME = "main_game"
    OPTIONS = "options"
    MINIGAMES = "minigames"
    QUIT = "quit"


class GameManager:
    """Gestionnaire principal qui orchestre tous les états du jeu"""
    
    def __init__(self, config):
        self.config = config
        self.current_state = GameState.START_MAP
        self.clock = pygame.time.Clock()
        
        # Créer l'écran principal (comme le fait Game.__init__)
        flags = pygame.RESIZABLE
        if config.ENABLE_ANTIALIASING:
            try:
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
            except:
                pass
        
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Last Man Standing")
        
        # Initialiser la carte de démarrage
        self.start_map = StartMap(config)
        
        # Le jeu principal sera créé à la demande
        self.main_game = None
        
        # État de l'application
        self.running = True
    
    def run(self):
        """Boucle principale du gestionnaire de jeu"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time en secondes
            
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self._handle_event(event)
            
            # Mettre à jour l'état actuel
            self._update(dt)
            
            # Dessiner l'état actuel
            self._draw()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
        
        # Nettoyage à la fermeture
        pygame.quit()
        sys.exit()
    
    def _handle_event(self, event):
        """Gère les événements selon l'état actuel"""
        if self.current_state == GameState.START_MAP:
            if self.start_map.handle_event(event):
                # Une action a été sélectionnée dans la carte de démarrage
                action = self.start_map.get_selected_action()
                self._handle_start_map_action(action)
        
        elif self.current_state == GameState.MAIN_GAME:
            if self.main_game:
                # Laisser le jeu principal gérer les événements
                # Ajouter une touche pour revenir au menu principal
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._return_to_start_map()
                else:
                    # Le jeu principal gère ses propres événements dans sa boucle
                    pass
        
        elif self.current_state == GameState.OPTIONS:
            # Gérer les événements du menu d'options
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._return_to_start_map()
        
        elif self.current_state == GameState.MINIGAMES:
            # Gérer les événements des mini-jeux
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._return_to_start_map()
    
    def _update(self, dt):
        """Met à jour l'état actuel"""
        if self.current_state == GameState.START_MAP:
            self.start_map.update(dt)
            
            # Vérifier si une action a été sélectionnée
            action = self.start_map.get_selected_action()
            if action:
                self._handle_start_map_action(action)
        
        elif self.current_state == GameState.MAIN_GAME:
            # Le jeu principal gère sa propre boucle de mise à jour
            # Nous n'avons besoin de rien faire ici
            pass
        
        elif self.current_state == GameState.OPTIONS:
            # Mettre à jour le menu d'options
            pass
        
        elif self.current_state == GameState.MINIGAMES:
            # Mettre à jour les mini-jeux
            pass
    
    def _draw(self):
        """Dessine l'état actuel"""
        self.screen.fill((0, 0, 0))  # Fond noir
        
        if self.current_state == GameState.START_MAP:
            self.start_map.draw(self.screen)
        
        elif self.current_state == GameState.MAIN_GAME:
            # Le jeu principal gère son propre dessin
            pass
        
        elif self.current_state == GameState.OPTIONS:
            self._draw_options_menu()
        
        elif self.current_state == GameState.MINIGAMES:
            self._draw_minigames_menu()
    
    def _handle_start_map_action(self, action):
        """Gère les actions sélectionnées dans la carte de démarrage"""
        if action == "play":
            self._start_main_game()
        elif action == "options":
            self.current_state = GameState.OPTIONS
        elif action == "minigames":
            self.current_state = GameState.MINIGAMES
        elif action == "quit":
            self.running = False
        elif action == "profile_info":
            # Afficher les informations du profil (pour l'instant, juste un print)
            profile = self.start_map.player_profile
            print(f"📊 Profil: {profile.name}")
            print(f"   Description: {profile.description}")
            print(f"   Multiplicateur vie: {profile.health_multiplier}")
            print(f"   Multiplicateur vitesse: {profile.speed_multiplier}")
    
    def _start_main_game(self):
        """Lance le jeu principal"""
        # Récupérer le profil sélectionné dans la carte de démarrage
        selected_profile = self.start_map.player_profile
        
        # Ajouter le type de profil à la configuration
        self.config.PLAYER_SPRITE_TYPE = selected_profile.profile_id
        
        # Créer une nouvelle instance du jeu principal
        self.main_game = Game(self.config)
        self.current_state = GameState.MAIN_GAME
        
        # Lancer la boucle du jeu principal
        # Le jeu principal va prendre le contrôle complet
        try:
            self.main_game.run()
        except Exception as e:
            print(f"Erreur dans le jeu principal: {e}")
        finally:
            # Une fois le jeu principal terminé, revenir à la carte de démarrage
            self._return_to_start_map()
    
    def _return_to_start_map(self):
        """Retourne à la carte de démarrage"""
        self.current_state = GameState.START_MAP
        # Nettoyer l'instance du jeu principal si elle existe
        self.main_game = None
        
        # Recréer la carte de démarrage pour repartir sur une base propre
        self.start_map = StartMap(self.config)
    
    def _draw_options_menu(self):
        """Dessine le menu d'options (placeholder)"""
        font = pygame.font.Font(None, 48)
        
        # Titre
        title_text = font.render("OPTIONS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Contenu placeholder
        content_font = pygame.font.Font(None, 32)
        content_lines = [
            "Menu d'options en développement",
            "",
            "Fonctionnalités prévues:",
            "- Configuration des contrôles",
            "- Réglages audio",
            "- Options graphiques",
            "- Sélection du profil de joueur",
            "",
            "Appuyez sur ÉCHAP pour revenir au menu principal"
        ]
        
        for i, line in enumerate(content_lines):
            if line:  # Ne pas dessiner les lignes vides
                text_surface = content_font.render(line, True, (200, 200, 200))
                text_rect = text_surface.get_rect(center=(self.config.WINDOW_WIDTH // 2, 200 + i * 40))
                self.screen.blit(text_surface, text_rect)
    
    def _draw_minigames_menu(self):
        """Dessine le menu des mini-jeux (placeholder)"""
        font = pygame.font.Font(None, 48)
        
        # Titre
        title_text = font.render("MINI-JEUX", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Contenu placeholder
        content_font = pygame.font.Font(None, 32)
        content_lines = [
            "Mini-jeux en développement",
            "",
            "Modes prévus:",
            "- Mode Survie par vagues",
            "- Mode Boss Rush",
            "- Mode Course contre la montre",
            "- Mode Défense de base",
            "",
            "Appuyez sur ÉCHAP pour revenir au menu principal"
        ]
        
        for i, line in enumerate(content_lines):
            if line:  # Ne pas dessiner les lignes vides
                text_surface = content_font.render(line, True, (200, 200, 200))
                text_rect = text_surface.get_rect(center=(self.config.WINDOW_WIDTH // 2, 200 + i * 40))
                self.screen.blit(text_surface, text_rect)
