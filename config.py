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
        self.ENEMY_SPEED = self.WINDOW_WIDTH * 0.003  # Plus lent que le joueur
        self.ENEMY_HEALTH = 20
        self.ENEMY_DAMAGE = 10
        
        # Paramètres des projectiles (adaptatifs)
        self.ZAP_SPEED = self.WINDOW_WIDTH * 0.01  # 1% de la largeur par frame
        self.ZAP_DAMAGE = 25
        self.ZAP_FIRE_RATE = 100000  # frames entre chaque tir
        self.ZAP_SIZE = 3  # Taille du point lumineux
        
        # Paramètres des éclairs (nouveau)
        self.LIGHTNING_DAMAGE = 50  # Plus de dégâts que les zaps
        self.LIGHTNING_FIRE_RATE_BASE = 30  # 1 seconde de base à 60fps
        self.LIGHTNING_FIRE_RATE_MIN = 6   # 0.1 seconde minimum à 60fps
        self.LIGHTNING_RANGE = self.WINDOW_WIDTH * 0.3  # 30% de la largeur
        self.LIGHTNING_DISPLAY_TIME = 6  # 0.1 seconde à 60fps
        self.LIGHTNING_COLOR = (255, 255, 255)  # Blanc éclatant
        self.LIGHTNING_SECONDARY_COLOR = (173, 216, 230)  # Bleu clair
        self.LIGHTNING_CHAIN_CHANCE = 0.5  # 50% de chance de chaîner sur un second ennemi
        self.LIGHTNING_CHAIN_RANGE = self.WINDOW_WIDTH * 0.2  # 20% de la largeur pour le chaînage
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
        
        # Paramètres des boules d'énergie orbitales (nouveau)
        self.ENERGY_ORB_DAMAGE = 40  # Dégâts des boules d'énergie
        self.ENERGY_ORB_SPEED = 2 * 3.14159 / 60  # 1 tour/seconde constant
        self.ENERGY_ORB_RADIUS = self.WINDOW_WIDTH * 0.08  # 8% de la largeur
        self.ENERGY_ORB_SIZE = int(self.WINDOW_WIDTH * 0.01)  # 1% de la largeur
        self.ENERGY_ORB_COLOR = (138, 43, 226)  # Violet/Pourpre
        self.ENERGY_ORB_GLOW_COLOR = (255, 0, 255)  # Magenta lumineux
        self.ENERGY_ORB_MAX_COUNT_BASE = 1  # Nombre de départ (niveau 1)
        self.ENERGY_ORB_MAX_COUNT_FINAL = 7  # Maximum final possible (niveau 7)
        self.ENERGY_ORB_PROGRESSION_INTERVAL = 1  # Nouvelle orbe à chaque niveau
        
        # Interface utilisateur
        self.HEALTH_BAR_WIDTH = int(self.WINDOW_WIDTH * 0.2)  # 20% de la largeur
        self.HEALTH_BAR_HEIGHT = int(self.WINDOW_HEIGHT * 0.02)  # 2% de la hauteur
        self.UI_MARGIN = int(self.WINDOW_WIDTH * 0.01)  # 1% de marge
        
        # Paramètres des vagues d'ennemis
        self.INITIAL_ENEMIES_PER_WAVE = 1  # Nombre d'ennemis dans la première vague
        self.ENEMIES_INCREASE_PER_WAVE = 5  # Augmentation du nombre d'ennemis par vague
        self.ENEMY_SPAWN_DELAY_BASE = 20    # Délai de base entre les spawns (frames)
        self.ENEMY_SPAWN_DELAY_MIN = 5     # Délai minimum entre les spawns (frames)
        self.ENEMY_SPAWN_DELAY_REDUCTION = 0.85  # Facteur de réduction du délai par vague
        
        # Système de caméra
        self.CAMERA_DELAY_DURATION = 12     # Délai avant que la caméra suive (frames)
        self.CAMERA_FOLLOW_SPEED = 0.08     # Vitesse de suivi de la caméra (0-1)
        self.CAMERA_MARGIN = 20             # Marge autour des bords de l'écran
        
        # Scores et progression
        self.SCORE_PER_ENEMY_KILL = 10      # Points par ennemi tué
        self.SCORE_PER_LIGHTNING_KILL = 15  # Points bonus pour les kills par éclair
        self.SCORE_WAVE_BONUS_MULTIPLIER = 100  # Bonus de points par vague
    
        # Options d'upgrade disponibles
        self.UPGRADE_POOL = [
            {"id": "speed", "name": "Vitesse +20%", "description": "Augmente la vitesse de déplacement"},
            {"id": "fire_rate", "name": "Cadence +30%", "description": "Tire plus rapidement"},
            {"id": "damage", "name": "Dégâts +25%", "description": "Les éclairs font plus de dégâts"},
            {"id": "orb_damage", "name": "Orbes +40%", "description": "Les orbes font plus de dégâts"},
            {"id": "orb_count", "name": "Orbe supplémentaire", "description": "Ajoute une orbe défensive"},
            {"id": "lightning_pierce", "name": "Éclair perforant", "description": "Les éclairs traversent les ennemis"},
            {"id": "healing", "name": "Régénération", "description": "Récupère de la vie au fil du temps"},
            {"id": "shield", "name": "Bouclier temporaire", "description": "Protection contre les dégâts"},
            {"id": "explosion", "name": "Éclairs explosifs", "description": "Les éclairs explosent à l'impact"},
            {"id": "magnet", "name": "Aimant", "description": "Attire les objets à distance"},
            {"id": "multishot", "name": "Tir multiple", "description": "Tire plusieurs éclairs"},
            {"id": "freeze", "name": "Ralentissement", "description": "Les ennemis touchés ralentissent"},
        ]
        
        # Configuration de la minimap
        self.MINIMAP_SIZE_RATIO = 6.0  # Diviseur pour calculer la taille (window_width / 6)
        self.MINIMAP_ALPHA = 180  # Plus opaque pour être plus visible
        self.MINIMAP_MARGIN = 10
        self.MINIMAP_PLAYER_SIZE = 4  # Légèrement plus grand
        self.MINIMAP_ENEMY_SIZE = 3   # Légèrement plus grand
        
        # Configuration des ennemis spéciaux
        self.SPECIAL_ENEMY_SPAWN_CHANCE = 0.1
        self.SPECIAL_ENEMY_HEALTH_MULTIPLIER = 3.0
        self.SPECIAL_ENEMY_DAMAGE_MULTIPLIER = 1.5
        self.SPECIAL_ENEMY_SPEED_MULTIPLIER = 0.8
        self.SPECIAL_ENEMY_COLOR = (255, 100, 0)  # Orange pour les distinguer
        
        # Paramètres des bonus
        self.BONUS_HEAL_AMOUNT = 20             # Points de vie restaurés
        self.BONUS_SHIELD_HITS = 1              # Nombre de coups bloqués
        self.BONUS_DOUBLE_DAMAGE_DURATION = 600 # 10 secondes à 60fps
        self.BONUS_LIGHTNING_STORM_COUNT = 5    # Nombre d'éclairs
        self.BONUS_SPEED_BOOST_DURATION = 480   # 8 secondes à 60fps
        self.BONUS_SPEED_BOOST_MULTIPLIER = 2.0 # Multiplicateur de vitesse
        self.BONUS_INVINCIBILITY_DURATION = 180 # 3 secondes à 60fps
        self.BONUS_TIME_SLOW_DURATION = 480     # 8 secondes à 60fps
        self.BONUS_TIME_SLOW_FACTOR = 0.3       # Facteur de ralentissement
        self.BONUS_FREEZE_DURATION = 240        # 4 secondes à 60fps
        
        # Types de bonus disponibles
        self.BONUS_TYPES = [
            "heal",
            "shield", 
            "double_damage",
            "lightning_storm",
            "speed_boost",
            "invincibility",
            "time_slow",
            "freeze"
        ]
