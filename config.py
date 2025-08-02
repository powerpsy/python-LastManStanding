import pygame

class Config:
    """Configuration du jeu avec 3 presets de résolution fixes"""
    
    def __init__(self, forced_screen_size=None):
        # Détecter la résolution de l'écran pour choisir le meilleur preset
        self.detect_and_set_resolution(forced_screen_size)
        
        # Configuration de l'antialiasing pour un rendu plus lisse
        self.ENABLE_ANTIALIASING = True
        self.SPRITE_SMOOTHING = True  # Utilise un algorithme de lissage pour les sprites
        
        # Couleurs principales (fixes pour tous les presets)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.CYAN = (0, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        
        # Couleurs spécifiques aux entités
        self.PLAYER_COLOR = self.CYAN
        self.ENEMY_COLOR = self.RED
        self.SPECIAL_ENEMY_COLOR = self.ORANGE
        self.ZAP_COLOR = self.YELLOW
        self.HEALTH_COLOR_HIGH = self.GREEN
        self.HEALTH_COLOR_MID = self.YELLOW
        self.HEALTH_COLOR_LOW = self.RED
        
        # FPS fixe pour tous les presets
        self.FPS = 60
        
        # Durée des transitions (en secondes)
        self.TRANSITION_DURATION = 0.2  # Durée par défaut pour toutes les transitions
        
        # Paramètres de jeu fixes
        self.PLAYER_MAX_HEALTH = 300
        self.PLAYER_FRICTION = 0.85
        self.ENEMY_HEALTH = 20
        self.ENEMY_DAMAGE = 10
        self.SPECIAL_ENEMY_SPAWN_CHANCE = 0.1
        self.SPECIAL_ENEMY_HEALTH_MULTIPLIER = 5.0  # Augmenté de 2.5 à 5.0 (x2)
        
        # Facteur de correction de vitesse pour équilibrer joueur vs ennemis
        # Le joueur utilise un système d'accélération, les ennemis un mouvement direct
        # Ce facteur compense la différence pour avoir des vitesses comparables
        self.ENEMY_SPEED_CORRECTION_FACTOR = 6.5  # Facteur empirique pour équilibrer
        
        # Progression des points de vie par vague
        self.ENEMY_HEALTH_INCREASE_PER_WAVE = 1  # +1 HP par vague pour ennemis normaux
        self.SPECIAL_ENEMY_HEALTH_INCREASE_PER_WAVE = 2  # +2 HP par vague pour ennemis spéciaux
        
        # Paramètres de l'ennemi tireur (sprite 14.png)
        self.SHOOTER_ENEMY_SPRITE_ID = 15  # ID du sprite pour l'ennemi tireur
        self.SHOOTER_ENEMY_STOP_DISTANCE = 600  # Distance à laquelle l'ennemi s'arrête pour tirer
        self.SHOOTER_ENEMY_FIRE_RATE = 90  # Fréquence de tir (frames entre chaque tir)
        self.SHOOTER_ENEMY_PROJECTILE_SPEED = 4.0  # Vitesse des projectiles
        self.SHOOTER_ENEMY_PROJECTILE_DAMAGE = 15  # Dégâts des projectiles
    
    def detect_and_set_resolution(self, forced_screen_size=None):
        """Détecte la résolution d'écran et applique le preset approprié"""
        if forced_screen_size is not None:
            # Mode forcé pour les tests
            if forced_screen_size == 1:
                self.apply_preset_1280x720()
                print(f"Mode test: Preset 1280x720 forcé")
            elif forced_screen_size == 2:
                self.apply_preset_1920x1080()
                print(f"Mode test: Preset 1920x1080 forcé")
            elif forced_screen_size == 3:
                self.apply_preset_2560x1440()
                print(f"Mode test: Preset 2560x1440 forcé")
            else:
                print(f"Taille d'écran forcée invalide: {forced_screen_size}. Utilisation de la détection automatique.")
                forced_screen_size = None
        
        if forced_screen_size is None:
            # Obtenir la résolution de l'écran
            pygame.init()
            info = pygame.display.Info()
            screen_width = info.current_w
            screen_height = info.current_h
            
            # Choisir le preset le plus approprié
            if screen_width >= 2560 and screen_height >= 1440:
                self.apply_preset_2560x1440()
            elif screen_width >= 1920 and screen_height >= 1080:
                self.apply_preset_1920x1080()
            else:
                self.apply_preset_1280x720()
            
            print(f"Résolution détectée: {screen_width}x{screen_height}")
        
        print(f"Preset appliqué: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
    
    def apply_preset_2560x1440(self):
        """Preset optimisé pour 2560x1440 (1440p)"""
        # Fenêtre
        self.WINDOW_WIDTH = 2560
        self.WINDOW_HEIGHT = 1440
        self.SCREEN_WIDTH = self.WINDOW_WIDTH
        self.SCREEN_HEIGHT = self.WINDOW_HEIGHT
        
        # Entités - Tailles fixes optimisées (x2 pour ennemis)
        self.PLAYER_SIZE = 48  # Plus grand pour 1440p
        self.ENEMY_SIZE = 80   # Scale x2 : 40 -> 80 pixels pour meilleure visibilité
        
        # Vitesses (maintenant équilibrées grâce au facteur de correction)
        self.PLAYER_SPEED = 1.0
        self.ENEMY_SPEED = 0.75
        
        # Projectiles
        self.LIGHTNING_SIZE = 40
        
        # Particules
        self.PARTICLE_SIZE = 4
        self.PARTICLE_SPEED = 3.0
        self.PARTICLE_COUNT = 8
        
        # Orbes d'énergie
        self.ENERGY_ORB_SIZE = 24
        self.ENERGY_ORB_RADIUS = 120
        self.ENERGY_ORB_SPEED = 0.08
        
        # Interface utilisateur
        self.HEALTH_BAR_WIDTH = 400
        self.HEALTH_BAR_HEIGHT = 24
        self.UI_MARGIN = 20
        
        # Police et texte
        self.font_scale = 1.5
        
        # Minimap
        self.MINIMAP_SIZE_RATIO = 8.0
        self.MINIMAP_MARGIN = 30
        self.MINIMAP_PLAYER_SIZE = 8
        self.MINIMAP_ENEMY_SIZE = 6
        self.MINIMAP_ALPHA = 180
        
        # Appliquer les paramètres communs
        self.apply_common_parameters()
    
    def apply_preset_1920x1080(self):
        """Preset optimisé pour 1920x1080 (1080p) - Référence"""
        # Fenêtre
        self.WINDOW_WIDTH = 1920
        self.WINDOW_HEIGHT = 1080
        self.SCREEN_WIDTH = self.WINDOW_WIDTH
        self.SCREEN_HEIGHT = self.WINDOW_HEIGHT
        
        # Entités - Tailles fixes optimisées
        self.PLAYER_SIZE = 36  # Taille de référence
        self.ENEMY_SIZE = 32   # Sprites 32x32 comme actuellement
        
        # Vitesses
        self.PLAYER_SPEED = 3.0
        self.ENEMY_SPEED = 2.0
        
        # Projectiles
        self.LIGHTNING_SIZE = 32
        
        # Particules
        self.PARTICLE_SIZE = 3
        self.PARTICLE_SPEED = 2.5
        self.PARTICLE_COUNT = 6
        
        # Orbes d'énergie
        self.ENERGY_ORB_SIZE = 18
        self.ENERGY_ORB_RADIUS = 90
        self.ENERGY_ORB_SPEED = 0.06
        
        # Interface utilisateur
        self.HEALTH_BAR_WIDTH = 300
        self.HEALTH_BAR_HEIGHT = 18
        self.UI_MARGIN = 15
        
        # Police et texte
        self.font_scale = 1.0
        
        # Minimap
        self.MINIMAP_SIZE_RATIO = 6.0
        self.MINIMAP_MARGIN = 20
        self.MINIMAP_PLAYER_SIZE = 6
        self.MINIMAP_ENEMY_SIZE = 4
        self.MINIMAP_ALPHA = 160
        
        # Appliquer les paramètres communs
        self.apply_common_parameters()
    
    def apply_preset_1280x720(self):
        """Preset optimisé pour 1280x720 (720p)"""
        # Fenêtre
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.SCREEN_WIDTH = self.WINDOW_WIDTH
        self.SCREEN_HEIGHT = self.WINDOW_HEIGHT
        
        # Entités - Tailles fixes optimisées
        self.PLAYER_SIZE = 24  # Plus petit pour 720p
        self.ENEMY_SIZE = 20   # Sprites 20x20 pour proportions
        
        # Vitesses
        self.PLAYER_SPEED = 0.7
        self.ENEMY_SPEED = 0.5
        
        # Projectiles
        self.LIGHTNING_SIZE = 20
        
        # Particules
        self.PARTICLE_SIZE = 2
        self.PARTICLE_SPEED = 2.0
        self.PARTICLE_COUNT = 4
        
        # Orbes d'énergie
        self.ENERGY_ORB_SIZE = 12
        self.ENERGY_ORB_RADIUS = 60
        self.ENERGY_ORB_SPEED = 0.04
        
        # Interface utilisateur
        self.HEALTH_BAR_WIDTH = 200
        self.HEALTH_BAR_HEIGHT = 12
        self.UI_MARGIN = 10
        
        # Police et texte
        self.font_scale = 0.7
        
        # Minimap
        self.MINIMAP_SIZE_RATIO = 4.0
        self.MINIMAP_MARGIN = 15
        self.MINIMAP_PLAYER_SIZE = 4
        self.MINIMAP_ENEMY_SIZE = 3
        self.MINIMAP_ALPHA = 140
        
        # Appliquer les paramètres communs après avoir défini le preset
        self.apply_common_parameters()
    
    def apply_common_parameters(self):
        """Applique les paramètres communs à tous les presets"""
        # Paramètres des vagues d'ennemis (identiques pour tous)
        self.INITIAL_ENEMIES_PER_WAVE = 1
        self.ENEMIES_INCREASE_PER_WAVE = 5
        self.ENEMY_SPAWN_DELAY_BASE = 19
        self.ENEMY_SPAWN_DELAY_MIN = 1
        self.ENEMY_SPAWN_DELAY_REDUCTION = 0.85
        
        # Système de caméra (identique pour tous)
        self.CAMERA_DELAY_DURATION = 12
        self.CAMERA_FOLLOW_SPEED = 0.08
        self.CAMERA_MARGIN = 20
        
        # Scores et progression (identiques pour tous)
        self.SCORE_PER_ENEMY_KILL = 10
        self.SCORE_PER_LIGHTNING_KILL = 15
        self.SCORE_WAVE_BONUS_MULTIPLIER = 100
        
        # Dégâts des armes (fixes, équilibrés)
        self.LIGHTNING_DAMAGE = 50
        self.ENERGY_ORB_DAMAGE = 40
        
        # Paramètres des lightning (fixes)
        self.LIGHTNING_DISPLAY_TIME = 6
        self.LIGHTNING_COLOR = (255, 255, 255)
        self.LIGHTNING_SECONDARY_COLOR = (173, 216, 230)
        
        # Paramètres des beams (fixes)
        self.BEAM_DURATION = 60
        self.BEAM_COLOR = (255, 100, 100)
        self.BEAM_GLOW_COLOR = (255, 200, 150)
        
        # Paramètres des particules (fixes mais utilise PARTICLE_SIZE du preset)
        self.PARTICLE_LIFETIME = 30
        self.PARTICLE_COLORS = [
            (255, 255, 0), (255, 165, 0), (255, 0, 0), (255, 255, 255), (255, 192, 203)
        ]
        
        # Couleurs des orbes (fixes)
        self.ENERGY_ORB_COLOR = (138, 43, 226)
        self.ENERGY_ORB_GLOW_COLOR = (255, 0, 255)
        
        # Paramètres des objets collectibles
        self.COLLECTIBLE_PICKUP_DISTANCE = 120  # Distance minimum pour attirer l'objet
        self.COLLECTIBLE_ATTRACTION_SPEED = 8  # Vitesse d'attraction vers le joueur
        self.HEART_HEAL_AMOUNT = 20  # Points de vie récupérés par coeur
        self.HEART_DROP_PROBABILITY = 1/200  # Probabilité de drop de coeur (1/200 = 0.5%)
        self.HEART_ELITE_DROP_COUNT = 3  # Nombre de coeurs lâchés par les ennemis spéciaux
        self.HEART_NORMAL_DROP_COUNT = 1  # Nombre de coeurs lâchés par les ennemis normaux
        self.HEART_MAX_ON_FIELD = 100  # Nombre maximum de coeurs sur le terrain
        
        # Paramètres des pièces (coins)
        self.COIN_VALUE = 10  # Points gagnés par pièce collectée
        self.COIN_ANIMATION_SPEED = 5   # Vitesse d'animation (frames par sprite)
        self.COIN_MAX_ON_FIELD = 200  # Nombre maximum de pièces sur le terrain
        self.COIN_THROW_DURATION = 10  # Durée du jet en frames (0.5 sec à 60fps)
        self.COIN_THROW_SPEED_MIN = 1  # Vitesse minimum de jet
        self.COIN_THROW_SPEED_MAX = 20  # Vitesse maximum de jet
        self.COIN_THROW_FRICTION = 0.70  # Friction appliquée pendant le jet
        
        # Paramètres des bonus temporaires (identiques pour tous)
        self.BONUS_HEAL_AMOUNT = 30
        self.BONUS_SHIELD_HITS = 3
        self.BONUS_DOUBLE_DAMAGE_DURATION = 300
        self.BONUS_LIGHTNING_STORM_COUNT = 5
        self.BONUS_SPEED_BOOST_MULTIPLIER = 1.5
        self.BONUS_SPEED_BOOST_DURATION = 300
        self.BONUS_INVINCIBILITY_DURATION = 180
        self.BONUS_TIME_SLOW_DURATION = 300
        self.BONUS_TIME_SLOW_FACTOR = 0.5
        self.BONUS_FREEZE_DURATION = 180
        
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
        
        # Paramètres des lightning (nouveau) - Valeurs de base seulement
        self.LIGHTNING_RANGE = self.WINDOW_WIDTH * 0.3  # 30% de la largeur
        self.LIGHTNING_DISPLAY_TIME = 6  # 0.1 seconde à 60fps
        self.LIGHTNING_COLOR = (255, 255, 255)  # Blanc éclatant
        self.LIGHTNING_SECONDARY_COLOR = (173, 216, 230)  # Bleu clair
        self.LIGHTNING_CHAIN_RANGE = self.WINDOW_WIDTH * 0.2  # 20% de la largeur pour le chaînage
        self.LIGHTNING_DAMAGE = 50  # Compatibilité avec l'ancien code
        
        # Paramètres des beams (nouveau)
        self.BEAM_DURATION = 60  # 1 seconde à 60fps
        self.BEAM_COLOR = (255, 100, 100)  # Rouge/orange
        self.BEAM_GLOW_COLOR = (255, 200, 150)  # Lueur dorée
        
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
            
            # Améliorations du canon
            {"id": "canon_damage", "name": "Canon +30%", "description": "Le canon fait plus de dégâts"},
            {"id": "canon_fire_rate", "name": "Cadence canon +40%", "description": "Tire plus rapidement"},
            {"id": "canon_range", "name": "Portée canon +50%", "description": "Portée du canon augmentée"},
            {"id": "canon_pierce", "name": "Canon perforant", "description": "Le canon traverse les ennemis"},
            
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
        
        # Système d'effets de mort différenciés par arme
        # Effet de repousse pour les orbes
        self.ORB_DEATH_PUSHBACK_DISTANCE = 15  # Distance de repousse en pixels
        self.ORB_DEATH_FADE_DURATION = 30  # Durée du fade en frames
        self.ORB_DEATH_COLOR_TINT = (255, 50, 50)  # Teinte rouge
        
        # Effet de désintégration pour les beams
        self.BEAM_DEATH_ASH_COUNT = 50  # Nombre de particules de cendres
        self.BEAM_DEATH_ASH_FALL_SPEED_MIN = 1.0  # Vitesse min de chute
        self.BEAM_DEATH_ASH_FALL_SPEED_MAX = 3.0  # Vitesse max de chute
        self.BEAM_DEATH_ASH_LIFETIME = 60  # Durée de vie des cendres en frames
        self.BEAM_DEATH_ASH_COLOR = (30, 30, 30)  # Couleur des cendres
        

