"""
Configuration du jeu Last Man Standing
"""

class Config:
    def __init__(self):
        # Paramètres de la fenêtre
        self.WINDOW_WIDTH = 1920 // 2  # 960 pixels
        self.WINDOW_HEIGHT = 1080 // 2  # 540 pixels
        self.FPS = 60
        self.TITLE = "Last Man Standing - Action 2D"
        
        # Couleurs (RGB)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (128, 0, 128)
        self.CYAN = (0, 255, 255)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        
        # Paramètres du joueur
        self.PLAYER_SIZE = int(self.WINDOW_WIDTH * 0.02)  # 2% de la largeur
        self.PLAYER_SPEED = self.WINDOW_WIDTH * 0.005  # Vitesse relative à la taille
        self.PLAYER_FRICTION = 0.85  # Friction pour l'inertie
        self.PLAYER_COLOR = self.CYAN
        
        # Paramètres des ennemis
        self.ENEMY_SIZE = int(self.WINDOW_WIDTH * 0.015)  # Plus petits que le joueur
        self.ENEMY_SPEED = self.WINDOW_WIDTH * 0.003  # Plus lents que le joueur
        self.ENEMY_COLOR = self.RED
        
        # Paramètres des projectiles (zaps/éclairs)
        self.ZAP_SPEED = self.WINDOW_WIDTH * 0.01  # Très rapides
        self.ZAP_WIDTH = int(self.WINDOW_WIDTH * 0.002)
        self.ZAP_LENGTH = int(self.WINDOW_WIDTH * 0.02)
        self.ZAP_COLOR = self.YELLOW
        self.ZAP_FIRE_RATE = 10  # Frames entre chaque tir
        
        # Paramètres des vagues
        self.INITIAL_ENEMIES = 3
        self.ENEMIES_PER_WAVE = 2  # Ennemis supplémentaires par vague
        self.WAVE_DELAY = 180  # Frames entre les vagues (3 secondes à 60 FPS)
        
        # Paramètres de difficulté
        self.DIFFICULTY_INCREASE = 0.1  # Augmentation de vitesse par vague
        self.MAX_ENEMY_SPEED_MULTIPLIER = 3.0
        
        # Interface utilisateur
        self.UI_FONT_SIZE = int(self.WINDOW_HEIGHT * 0.04)  # Taille relative
        self.UI_COLOR = self.WHITE
        self.UI_MARGIN = int(self.WINDOW_WIDTH * 0.02)
