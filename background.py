"""
Système de génération procédurale d'arrière-plan
"""

import pygame
import random
import math

class Background:
    """Classe pour générer et afficher un arrière-plan procédural basé sur un tileset"""
    
    def __init__(self, config):
        self.config = config
        self.tile_size = 32  # Changé de 16 à 32
        self.map_width = 100
        self.map_height = 100
        
        # Charger le tileset
        try:
            self.tileset = pygame.image.load("assets/Tileset.png").convert_alpha()
            self.extract_tiles()
        except pygame.error:
            print("⚠️  Impossible de charger assets/Tileset.png")
            self.tileset = None
            self.tiles = None
            
        # Générer la carte
        self.base_map = []  # Terrain de fond
        self.decoration_map = []  # Éléments de décoration
        self.generate_map()
        
        # Calculer les limites du monde
        self.world_width = self.map_width * self.scaled_tile_size if hasattr(self, 'scaled_tile_size') else self.map_width * self.tile_size
        self.world_height = self.map_height * self.scaled_tile_size if hasattr(self, 'scaled_tile_size') else self.map_height * self.tile_size
    
    def extract_tiles(self):
        """Extrait tous les tiles du tileset"""
        if not self.tileset:
            return
            
        self.tiles = []
        tileset_width = self.tileset.get_width() // self.tile_size
        tileset_height = self.tileset.get_height() // self.tile_size
        
        # Extraire chaque tile
        for y in range(tileset_height):
            for x in range(tileset_width):
                tile_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                      self.tile_size, self.tile_size)
                tile = self.tileset.subsurface(tile_rect).copy()
                # Redimensionner le tile pour s'adapter à l'échelle du jeu
                scale_factor = max(1, self.config.WINDOW_WIDTH // 960)  # Échelle adaptative
                scaled_size = self.tile_size * scale_factor
                tile = pygame.transform.scale(tile, (scaled_size, scaled_size))
                self.tiles.append(tile)
        
        self.scaled_tile_size = self.tile_size * scale_factor
    
    def generate_map(self, forced_seed=None):
        """Génère la carte procéduralement"""
        # Générer un seed pour la reproductibilité
        if forced_seed is not None:
            seed = forced_seed
        else:
            seed = random.randint(0, 1000000)
        random.seed(seed)
        print(f"Génération du terrain avec le seed: {seed}")
        
        # Initialiser les cartes
        self.base_map = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.decoration_map = [[None for _ in range(self.map_width)] for _ in range(self.map_height)]
        
        # 1. Générer le terrain de base par zones
        self.generate_base_terrain()
        
        # 2. Ajouter les décorations
        self.generate_decorations()
        
        print(f"Terrain généré: {self.map_width}x{self.map_height} tiles")
    
    def generate_base_terrain(self):
        """Génère le terrain de base avec des zones cohérentes"""
        # Définir des centres de zones pour différents terrains
        num_zones = random.randint(6, 12)  # Entre 6 et 12 zones
        zones = []
        
        for _ in range(num_zones):
            center_x = random.randint(10, self.map_width - 10)
            center_y = random.randint(10, self.map_height - 10)
            terrain_type = random.randint(1, 8)  # Tiles 1-8 seulement (première ligne)
            radius = random.randint(8, 25)  # Rayon de la zone
            zones.append((center_x, center_y, terrain_type, radius))
        
        # Remplir la carte en fonction de la proximité aux zones
        for y in range(self.map_height):
            for x in range(self.map_width):
                # Trouver la zone la plus proche
                closest_distance = float('inf')
                closest_terrain = 1  # Terrain par défaut (tile 1)
                
                for zone_x, zone_y, terrain_type, radius in zones:
                    distance = math.sqrt((x - zone_x)**2 + (y - zone_y)**2)
                    # Pondérer par le rayon de la zone
                    weighted_distance = distance / radius
                    
                    if weighted_distance < closest_distance:
                        closest_distance = weighted_distance
                        closest_terrain = terrain_type
                
                # Ajouter un peu de randomisation pour éviter des zones trop parfaites
                if random.random() < 0.1:  # 10% de chance de changer
                    closest_terrain = random.randint(1, 8)  # Tiles 1-8 seulement
                
                self.base_map[y][x] = closest_terrain
    
    def generate_decorations(self):
        """Génère les éléments de décoration (tiles 18-84)"""
        decoration_tiles = list(range(18, 85))  # Tiles 18 à 84
        
        # Densité de décoration variable selon les zones
        for y in range(self.map_height):
            for x in range(self.map_width):
                # Probabilité de décoration basée sur le terrain de base
                base_terrain = self.base_map[y][x]
                
                # Différentes probabilités selon le type de terrain (encore plus réduites)
                if base_terrain in [2, 5, 8]:  # Terrains "naturels" (ajusté pour 1-8)
                    decoration_chance = 0.008  # Réduit de 1.5% à 0.8%
                elif base_terrain in [1, 4, 7]:  # Terrains "rocheux"
                    decoration_chance = 0.005  # Réduit de 0.8% à 0.5%
                else:  # Autres terrains (3, 6)
                    decoration_chance = 0.003  # Réduit de 0.5% à 0.3%
                
                if random.random() < decoration_chance:
                    decoration_tile = random.choice(decoration_tiles)
                    self.decoration_map[y][x] = decoration_tile
    
    def get_world_bounds(self):
        """Retourne les limites du monde en pixels"""
        # Utiliser la taille mise à l'échelle si disponible
        tile_size = self.scaled_tile_size if hasattr(self, 'scaled_tile_size') else self.tile_size
        return {
            'min_x': 0,
            'max_x': self.map_width * tile_size,
            'min_y': 0,
            'max_y': self.map_height * tile_size
        }
    
    def constrain_player(self, player):
        """Contraint le joueur dans les limites du monde"""
        bounds = self.get_world_bounds()
        
        # Contraindre la position du joueur
        if player.x < bounds['min_x']:
            player.x = bounds['min_x']
            player.vel_x = 0
        elif player.x + player.size > bounds['max_x']:
            player.x = bounds['max_x'] - player.size
            player.vel_x = 0
            
        if player.y < bounds['min_y']:
            player.y = bounds['min_y']
            player.vel_y = 0
        elif player.y + player.size > bounds['max_y']:
            player.y = bounds['max_y'] - player.size
            player.vel_y = 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine l'arrière-plan avec optimisation (ne dessine que les tiles visibles)"""
        if not self.tiles:
            # Fallback: fond coloré simple VISIBLE
            screen.fill((0, 150, 0))  # Vert visible
            return
        
        # Calculer les tiles visibles
        start_x = max(0, int(camera_x // self.scaled_tile_size))
        end_x = min(self.map_width, int((camera_x + self.config.WINDOW_WIDTH) // self.scaled_tile_size) + 1)
        start_y = max(0, int(camera_y // self.scaled_tile_size))
        end_y = min(self.map_height, int((camera_y + self.config.WINDOW_HEIGHT) // self.scaled_tile_size) + 1)
        
        # Dessiner les tiles visibles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Position à l'écran
                screen_x = x * self.scaled_tile_size - camera_x
                screen_y = y * self.scaled_tile_size - camera_y
                
                # Dessiner le terrain de base
                base_tile_id = self.base_map[y][x]
                if base_tile_id < len(self.tiles):
                    screen.blit(self.tiles[base_tile_id], (screen_x, screen_y))
                
                # Dessiner la décoration si elle existe
                decoration_tile_id = self.decoration_map[y][x]
                if decoration_tile_id is not None and decoration_tile_id < len(self.tiles):
                    screen.blit(self.tiles[decoration_tile_id], (screen_x, screen_y))
    
    def regenerate(self, forced_seed=None):
        """Régénère le terrain (pour le debug ou restart)"""
        self.generate_map(forced_seed)
