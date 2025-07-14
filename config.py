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
        self.SPECIAL_ENEMY_COLOR = self.ORANGE  # Couleur des ennemis spéciaux
        self.ZAP_COLOR = self.YELLOW
        self.HEALTH_COLOR_HIGH = self.GREEN
        self.HEALTH_COLOR_MID = self.YELLOW
        self.HEALTH_COLOR_LOW = self.RED
        
        # Paramètres du joueur (adaptatifs)
        self.PLAYER_SIZE = int(self.WINDOW_WIDTH * 0.02)  # 2% de la largeur
        self.PLAYER_SPEED = self.WINDOW_WIDTH * 0.0005  # Vitesse proportionnelle
        self.PLAYER_MAX_HEALTH = 100
        self.PLAYER_FRICTION = 0.85  # Inertie
        
        # Paramètres des ennemis (adaptatifs)
        self.ENEMY_SIZE = int(self.WINDOW_WIDTH * 0.015)  # 1.5% de la largeur
        self.ENEMY_SPEED = self.WINDOW_WIDTH * 0.002  # Plus lent que le joueur
        self.ENEMY_HEALTH = 20
        self.ENEMY_DAMAGE = 10
        self.SPECIAL_ENEMY_SPAWN_CHANCE = 0.1  # 10% de chance de spawn d'ennemi spécial
        self.SPECIAL_ENEMY_HEALTH_MULTIPLIER = 2.5  # Les ennemis spéciaux ont 2.5x plus de vie
        
        # Types de bonus donnés par les ennemis spéciaux
        self.BONUS_TYPES = [
            "damage_boost",      # Augmentation temporaire des dégâts
            "speed_boost",       # Augmentation temporaire de la vitesse
            "shield",           # Bouclier temporaire
            "lightning_boost",   # Amélioration temporaire des éclairs
            "orb_boost"         # Amélioration temporaire des orbes
        ]
        
        # Paramètres des bonus temporaires
        self.BONUS_HEAL_AMOUNT = 30                    # Points de vie récupérés
        self.BONUS_SHIELD_HITS = 3                     # Nombre de coups absorbés par le bouclier
        self.BONUS_DOUBLE_DAMAGE_DURATION = 300       # 5 secondes à 60fps
        self.BONUS_LIGHTNING_STORM_COUNT = 5           # Nombre d'éclairs dans la tempête
        self.BONUS_SPEED_BOOST_MULTIPLIER = 1.5        # Multiplicateur de vitesse
        self.BONUS_SPEED_BOOST_DURATION = 300          # 5 secondes à 60fps
        self.BONUS_INVINCIBILITY_DURATION = 180        # 3 secondes à 60fps
        self.BONUS_TIME_SLOW_DURATION = 300            # 5 secondes à 60fps
        self.BONUS_TIME_SLOW_FACTOR = 0.5              # Facteur de ralentissement
        self.BONUS_FREEZE_DURATION = 180               # 3 secondes à 60fps
        
        # Paramètres du canon (adaptatifs) - Valeurs de base seulement
        self.ZAP_SPEED = self.WINDOW_WIDTH * 0.005  # 1% de la largeur par frame
        self.ZAP_SIZE = 3  # Taille du point lumineux
        self.ZAP_DAMAGE = 25  # Compatibilité avec l'ancien code
        self.ZAP_FIRE_RATE = 60  # Compatibilité avec l'ancien code
        
        # Paramètres des lightning (nouveau) - Valeurs de base seulement
        self.LIGHTNING_RANGE = self.WINDOW_WIDTH * 0.3  # 30% de la largeur
        self.LIGHTNING_DISPLAY_TIME = 6  # 0.1 seconde à 60fps
        self.LIGHTNING_COLOR = (255, 255, 255)  # Blanc éclatant
        self.LIGHTNING_SECONDARY_COLOR = (173, 216, 230)  # Bleu clair
        self.LIGHTNING_CHAIN_RANGE = self.WINDOW_WIDTH * 0.2  # 20% de la largeur pour le chaînage
        self.LIGHTNING_DAMAGE = 50  # Compatibilité avec l'ancien code
        
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
        
        # Paramètres des orb orbitales (nouveau) - Valeurs de base seulement
        self.ENERGY_ORB_SPEED = 2 * 3.14159 / 60  # 1 tour/seconde constant
        self.ENERGY_ORB_RADIUS = self.WINDOW_WIDTH * 0.08  # 8% de la largeur
        self.ENERGY_ORB_SIZE = int(self.WINDOW_WIDTH * 0.01)  # 1% de la largeur
        self.ENERGY_ORB_COLOR = (138, 43, 226)  # Violet/Pourpre
        self.ENERGY_ORB_GLOW_COLOR = (255, 0, 255)  # Magenta lumineux
        self.ENERGY_ORB_DAMAGE = 40  # Compatibilité avec l'ancien code
        
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
        self.SCORE_PER_LIGHTNING_KILL = 15  # Points bonus pour les kills par lightning
        self.SCORE_WAVE_BONUS_MULTIPLIER = 100  # Bonus de points par vague
    
        # Options d'upgrade disponibles - Nouvelles améliorations d'armes
        self.UPGRADE_POOL = [
            # Améliorations générales du joueur
            {"id": "speed", "name": "Vitesse +20%", "description": "Augmente la vitesse de déplacement"},
            {"id": "healing", "name": "Régénération", "description": "Récupère de la vie au fil du temps"},
            {"id": "shield", "name": "Bouclier temporaire", "description": "Protection contre les dégâts"},
            {"id": "magnet", "name": "Aimant", "description": "Attire les objets à distance"},
            
            # Améliorations du canon (Zaps)
            {"id": "zap_damage", "name": "Canon +30%", "description": "Le canon fait plus de dégâts"},
            {"id": "zap_fire_rate", "name": "Cadence canon +40%", "description": "Tire plus rapidement"},
            {"id": "zap_range", "name": "Portée canon +50%", "description": "Portée du canon augmentée"},
            {"id": "zap_pierce", "name": "Canon perforant", "description": "Le canon traverse les ennemis"},
            
            # Améliorations des lightning
            {"id": "lightning_damage", "name": "Lightning +40%", "description": "Les lightning font plus de dégâts"},
            {"id": "lightning_fire_rate", "name": "Cadence lightning +50%", "description": "Lightning plus fréquents"},
            {"id": "lightning_chain", "name": "Chaîne lightning +1", "description": "Les lightning chaînent sur plus d'ennemis"},
            {"id": "lightning_storm", "name": "Tempête de lightning", "description": "Lightning multiples simultanés"},
            
            # Améliorations des orb
            {"id": "orb_count", "name": "Orb supplémentaire", "description": "Ajoute une orb défensive"},
            {"id": "orb_damage", "name": "Orb +50%", "description": "Les orb font plus de dégâts"},
            {"id": "orb_speed", "name": "Orb rapides", "description": "Les orb tournent plus vite"},
            {"id": "orb_size", "name": "Orb géantes", "description": "Orb plus grandes et plus de dégâts"},
        ]
        
        # Configuration de la minimap
        self.MINIMAP_SIZE_RATIO = 6.0  # Diviseur pour calculer la taille (window_width / 6)
        self.MINIMAP_ALPHA = 180  # Plus opaque pour être plus visible
        self.MINIMAP_MARGIN = 10
        self.MINIMAP_PLAYER_SIZE = 4  # Légèrement plus grand
        self.MINIMAP_ENEMY_SIZE = 3   # Légèrement plus grand
        
    def recalculate_adaptive_sizes(self):
        """Recalcule les tailles adaptatives après un redimensionnement"""
        # Recalculer les facteurs d'échelle pour l'interface
        self.ui_scale = min(self.WINDOW_WIDTH / 1920, self.WINDOW_HEIGHT / 1080)
        self.font_scale = max(0.5, self.ui_scale)  # Échelle minimum pour la lisibilité
        
        # Recalculer les paramètres du joueur
        self.PLAYER_SIZE = int(self.WINDOW_WIDTH * 0.02)
        self.PLAYER_SPEED = self.WINDOW_WIDTH * 0.001
        
        # Recalculer les paramètres des ennemis
        self.ENEMY_SIZE = int(self.WINDOW_WIDTH * 0.015)
        self.ENEMY_SPEED = self.WINDOW_WIDTH * 0.003
        
        # Recalculer les paramètres du canon
        self.ZAP_SPEED = self.WINDOW_WIDTH * 0.01
        self.ZAP_SIZE = int(self.WINDOW_WIDTH * 0.008)
        
        # Recalculer les paramètres des lightning
        self.LIGHTNING_SIZE = int(self.WINDOW_WIDTH * 0.015)
        
        # Recalculer les paramètres des particules
        self.PARTICLE_SIZE = max(2, int(self.WINDOW_WIDTH * 0.005))
        self.PARTICLE_SPEED = self.WINDOW_WIDTH * 0.002
        
        # Recalculer les paramètres des orb
        self.ENERGY_ORB_RADIUS = self.WINDOW_WIDTH * 0.08
        self.ENERGY_ORB_SIZE = int(self.WINDOW_WIDTH * 0.01)
        
        # Recalculer les paramètres de l'interface utilisateur
        self.HEALTH_BAR_WIDTH = int(self.WINDOW_WIDTH * 0.2)  # 20% de la largeur
        self.HEALTH_BAR_HEIGHT = int(self.WINDOW_HEIGHT * 0.02)  # 2% de la hauteur
        self.UI_MARGIN = int(self.WINDOW_WIDTH * 0.01)  # 1% de marge
        
        # Recalculer les paramètres de la minimap
        self.MINIMAP_SIZE_RATIO = 6.0
        self.MINIMAP_MARGIN = int(self.WINDOW_WIDTH * 0.01)
        
        print(f"📐 Tailles recalculées - Joueur: {self.PLAYER_SIZE}, Ennemis: {self.ENEMY_SIZE}, Orbes: {self.ENERGY_ORB_SIZE}")
