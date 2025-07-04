import pygame

class Config:
    """Configuration du jeu avec paramètres adaptatifs"""
    
    def __init__(self):
        # Dimensions de la fenêtre
        self.WINDOW_WIDTH = 1920 // 2  # 960 pixels
        self.WINDOW_HEIGHT = 1080 // 2  # 540 pixels
        self.FPS = 60
        
        # Facteurs d'échelle pour l'interface
        self.ui_scale = min(self.WINDOW_WIDTH / 1920, self.WINDOW_HEIGHT / 1080)
        self.font_scale = max(0.5, self.ui_scale)  # Échelle minimum pour la lisibilité
        
        # Couleurs principales
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.CYAN = (0, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.BLUE = (0, 100, 255)
        self.PURPLE = (128, 0, 128)
        
        # Couleurs spécifiques aux entités
        self.PLAYER_COLOR = self.CYAN
        self.ENEMY_COLOR = self.RED
        self.ZAP_COLOR = self.YELLOW
        self.HEALTH_COLOR_HIGH = self.GREEN
        self.HEALTH_COLOR_MID = self.YELLOW
        self.HEALTH_COLOR_LOW = self.RED
        
        # Paramètres du joueur (adaptatifs)
        self.PLAYER_SIZE = int(self.WINDOW_WIDTH * 0.02)  # 2% de la largeur
        self.PLAYER_SPEED = self.WINDOW_WIDTH * 0.001  # Vitesse proportionnelle
        self.PLAYER_MAX_HEALTH = 100
        self.PLAYER_FRICTION = 0.85  # Inertie
        
        # Paramètres des ennemis (adaptatifs)
        self.ENEMY_SIZE = int(self.WINDOW_WIDTH * 0.015)  # 1.5% de la largeur
        self.ENEMY_SPEED = self.WINDOW_WIDTH * 0.002  # Plus lent que le joueur
        self.ENEMY_HEALTH = 20
        self.ENEMY_DAMAGE = 10
        
        # Paramètres des projectiles (adaptatifs)
        self.ZAP_SPEED = self.WINDOW_WIDTH * 0.01  # 1% de la largeur par frame
        self.ZAP_DAMAGE = 25
        self.ZAP_FIRE_RATE = 60  # frames entre chaque tir
        self.ZAP_SIZE = 3  # Taille du point lumineux
        
        # Paramètres des éclairs (nouveau)
        self.LIGHTNING_DAMAGE = 50  # Plus de dégâts que les zaps
        self.LIGHTNING_FIRE_RATE = 30  # 1 seconde à 60fps
        self.LIGHTNING_RANGE = self.WINDOW_WIDTH * 0.3  # 30% de la largeur
        self.LIGHTNING_DISPLAY_TIME = 6  # 0.1 seconde à 60fps
        self.LIGHTNING_COLOR = (255, 255, 255)  # Blanc éclatant
        self.LIGHTNING_SECONDARY_COLOR = (173, 216, 230)  # Bleu clair
        
        # Paramètres des particules d'explosion
        self.PARTICLE_COUNT = 8  # Nombre de particules par explosion
        self.PARTICLE_SPEED = self.WINDOW_WIDTH * 0.003  # Vitesse des particules
        self.PARTICLE_LIFETIME = 30  # Durée de vie en frames
        self.PARTICLE_SIZE = 2  # Taille des particules
        self.PARTICLE_COLORS = [
            (255, 255, 0),   # Jaune
            (255, 165, 0),   # Orange
            (255, 0, 0),     # Rouge
            (255, 255, 255), # Blanc
            (255, 192, 203)  # Rose
        ]
        
        # Interface utilisateur
        self.HEALTH_BAR_WIDTH = int(self.WINDOW_WIDTH * 0.2)  # 20% de la largeur
        self.HEALTH_BAR_HEIGHT = int(self.WINDOW_HEIGHT * 0.02)  # 2% de la hauteur
        self.UI_MARGIN = int(self.WINDOW_WIDTH * 0.01)  # 1% de marge
