"""
Classes du joueur et des entités du jeu
"""

import pygame
import pygame.gfxdraw  # Pour l'antialiasing
import random
import math

class Player:
    """Classe du joueur avec déplacement à inertie et animation directionnelle"""
    
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        self.size = config.PLAYER_SIZE
        self.speed = config.PLAYER_SPEED
        self.max_health = config.PLAYER_MAX_HEALTH
        self.health = self.max_health
        
        # Vélocité pour l'inertie
        self.vel_x = 0
        self.vel_y = 0
        self.friction = config.PLAYER_FRICTION
        
        # === SYSTÈME D'ANIMATION AVEC SPRITESHEET ===
        self.facing_direction = "right"  # "left" ou "right"
        self.last_movement_x = 0  # Pour détecter le changement de direction
        
        # Animation avec 5 sprites
        self.animation_frames = []  # Liste des frames d'animation
        self.animation_frames_left = []  # Frames pour la direction gauche
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_sequence = [4, 3, 2, 1, 0]  # Séquence 5-4-3-2-1 en boucle
        self.sequence_index = 0
        
        # Charger la spritesheet player2.png
        try:
            spritesheet = pygame.image.load("assets/player/player2.png").convert_alpha()
            
            # Dimensions des sprites individuels (à ajuster selon votre image)
            sprite_width = spritesheet.get_width() // 5  # 5 sprites horizontalement
            sprite_height = spritesheet.get_height()
            
            sprite_size = self.size * 4  # Facteur d'échelle x4 pour une meilleure visibilité
            
            # Extraire les 5 sprites (positions 0, 1, 2, 3, 4)
            for i in range(5):
                # Extraire le sprite à la position (i * sprite_width, 0)
                frame_rect = pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height)
                frame = spritesheet.subsurface(frame_rect).copy()
                
                # Redimensionner le sprite avec antialiasing si activé
                if config.SPRITE_SMOOTHING:
                    frame_scaled = pygame.transform.smoothscale(frame, (sprite_size, sprite_size))
                else:
                    frame_scaled = pygame.transform.scale(frame, (sprite_size, sprite_size))
                
                # Optimiser le format pour un rendu plus rapide
                frame_scaled = frame_scaled.convert_alpha()
                self.animation_frames.append(frame_scaled)
                
                # Créer la version miroir pour la gauche
                frame_left = pygame.transform.flip(frame_scaled, True, False)
                frame_left = frame_left.convert_alpha()  # Optimiser aussi la version miroir
                self.animation_frames_left.append(frame_left)
            
            self.has_image = True
            print(f"Animation spritesheet du joueur activée (5 frames, séquence 5-4-3-2-1 en boucle)")
        except (pygame.error, FileNotFoundError):
            print("Spritesheet assets/player/player2.png non trouvée, utilisation du rendu par défaut")
            self.animation_frames = []
            self.animation_frames_left = []
            self.has_image = False
    
    def update(self, keys):
        """Met à jour la position du joueur avec inertie et animation directionnelle"""
        # Accélération basée sur les touches
        accel_x = 0
        accel_y = 0
        
        if keys[pygame.K_w] or keys[pygame.K_z]:  # W ou Z (AZERTY)
            accel_y = -self.speed
        if keys[pygame.K_s]:
            accel_y = self.speed
        if keys[pygame.K_a] or keys[pygame.K_q]:  # A ou Q (AZERTY)
            accel_x = -self.speed
        if keys[pygame.K_d]:
            accel_x = self.speed
        
        # === DÉTECTION DE DIRECTION ===
        # Si le joueur se déplace horizontalement, mettre à jour la direction
        if accel_x > 0:  # Mouvement vers la droite
            self.facing_direction = "right"
        elif accel_x < 0:  # Mouvement vers la gauche
            self.facing_direction = "left"
        
        # Normalisation pour vitesse constante en diagonale
        if accel_x != 0 and accel_y != 0:
            norm = math.sqrt(accel_x ** 2 + accel_y ** 2)
            accel_x = accel_x / norm * self.speed
            accel_y = accel_y / norm * self.speed
        
        # Appliquer l'accélération
        self.vel_x += accel_x
        self.vel_y += accel_y
        
        # Appliquer la friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Mettre à jour la position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # === ANIMATION DES FRAMES ===
        # Mettre à jour l'animation seulement si on a des frames
        if self.has_image and self.animation_frames:
            # Avancer le timer d'animation (compteur de frames)
            self.animation_timer += 1
            
            # Changer de frame toutes les 9 frames de jeu (~6.7 FPS d'animation à 60 FPS)
            if self.animation_timer >= 9:
                self.animation_timer = 0
                self.sequence_index = (self.sequence_index + 1) % len(self.frame_sequence)
                self.current_frame = self.frame_sequence[self.sequence_index]
    
    def take_damage(self, damage):
        """Fait subir des dégâts au joueur"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen, shield_hits=0):
        """Dessine le joueur avec l'animation de spritesheet et l'effet de bouclier"""
        
        # === EFFET DE BOUCLIER ===
        if shield_hits > 0:
            center_x = int(self.x + self.size//2)
            center_y = int(self.y + self.size//2)
            shield_radius = int(self.size * 0.8)  # Rayon plus grand que le joueur
            
            # Couleur bleue pour le bouclier avec transparence
            shield_color = (100, 150, 255)  # Bleu clair
            shield_border_color = (50, 100, 255)  # Bleu plus foncé pour le contour
            
            # Dessiner le cercle de bouclier avec effet de pulsation
            import math
            import pygame.time
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.1 + 1.0  # Pulsation entre 0.9 et 1.1
            current_radius = int(shield_radius * pulse)
            
            # Dessiner le bouclier
            if self.config.ENABLE_ANTIALIASING:
                # Cercle semi-transparent avec antialiasing
                pygame.gfxdraw.aacircle(screen, center_x, center_y, current_radius, shield_border_color)
                pygame.gfxdraw.aacircle(screen, center_x, center_y, current_radius + 1, shield_border_color)
            else:
                # Cercle normal
                pygame.draw.circle(screen, shield_border_color, (center_x, center_y), current_radius, 2)
        
        # === DESSIN DU JOUEUR ===
        if self.has_image and self.animation_frames and self.animation_frames_left:
            # Choisir la bonne liste de frames selon la direction
            current_frames = self.animation_frames if self.facing_direction == "right" else self.animation_frames_left
            
            # S'assurer que current_frame est dans les limites
            if self.current_frame < len(current_frames):
                current_image = current_frames[self.current_frame]
                
                # Utiliser l'image du joueur centrée sur sa position
                image_rect = current_image.get_rect()
                # Centrer l'image sur les coordonnées du joueur
                image_rect.center = (int(self.x + self.size//2), int(self.y + self.size//2))
                screen.blit(current_image, image_rect)
            else:
                # Fallback si problème avec les frames
                self.current_frame = 0
        else:
            # Fallback : dessiner un cercle si l'image n'est pas disponible
            center_x = int(self.x + self.size//2)
            center_y = int(self.y + self.size//2)
            radius = self.size//2
            
            # Utiliser l'antialiasing si activé
            if self.config.ENABLE_ANTIALIASING:
                pygame.gfxdraw.filled_circle(screen, center_x, center_y, radius, self.config.PLAYER_COLOR)
                pygame.gfxdraw.aacircle(screen, center_x, center_y, radius, self.config.PLAYER_COLOR)
                # Contour blanc avec antialiasing
                pygame.gfxdraw.aacircle(screen, center_x, center_y, radius, self.config.WHITE)
            else:
                pygame.draw.circle(screen, self.config.PLAYER_COLOR, (center_x, center_y), radius)
                # Contour blanc
                pygame.draw.circle(screen, self.config.WHITE, (center_x, center_y), radius, 1)
            pygame.draw.circle(screen, self.config.WHITE,
                             (int(self.x + self.size//2), int(self.y + self.size//2)),
                             self.size//2, 2)
            
            # === INDICATEUR DE DIRECTION EN MODE FALLBACK ===
            # Dessiner un petit triangle pour indiquer la direction
            center_x = int(self.x + self.size//2)
            center_y = int(self.y + self.size//2)
            triangle_size = self.size // 4
            
            if self.facing_direction == "right":
                # Triangle pointant vers la droite
                points = [
                    (center_x + triangle_size, center_y),
                    (center_x - triangle_size//2, center_y - triangle_size//2),
                    (center_x - triangle_size//2, center_y + triangle_size//2)
                ]
            else:  # facing_direction == "left"
                # Triangle pointant vers la gauche
                points = [
                    (center_x - triangle_size, center_y),
                    (center_x + triangle_size//2, center_y - triangle_size//2),
                    (center_x + triangle_size//2, center_y + triangle_size//2)
                ]
            
            pygame.draw.polygon(screen, self.config.WHITE, points)


class Enemy:
    """Classe des ennemis avec IA de poursuite"""
    
    # Variables de classe pour les sprites (chargés une seule fois)
    sprites = None
    sprites_loaded = False
    
    @classmethod
    def load_sprites(cls):
        """Charge tous les sprites d'ennemis une seule fois"""
        if not cls.sprites_loaded:
            cls.sprites = {}
            try:
                # Charger les sprites 1.png à 5.png
                for i in range(1, 24):
                    sprite_path = f"assets/Enemy/{i}.png"
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    # Les sprites sont maintenant redimensionnés selon le preset actuel
                    # La taille sera définie lors de l'initialisation de l'ennemi
                    cls.sprites[i] = sprite  # Garder le sprite original pour le redimensionner plus tard
                cls.sprites_loaded = True
                print(f"{len(cls.sprites)} sprites d'ennemis chargés (redimensionnement selon preset)")
            except Exception as e:
                print(f"Erreur lors du chargement des sprites: {e}")
                cls.sprites = {}
                cls.sprites_loaded = True
    
    def __init__(self, x, y, config, is_special=False, wave_number=1):
        # Charger les sprites si ce n'est pas déjà fait
        if not Enemy.sprites_loaded:
            Enemy.load_sprites()
        
        self.x = x
        self.y = y
        self.config = config
        self.size = config.ENEMY_SIZE
        self.speed = config.ENEMY_SPEED
        
        # Choisir un sprite aléatoire pour cet ennemi et le redimensionner à la bonne taille
        if Enemy.sprites:
            self.sprite_id = random.choice(list(Enemy.sprites.keys()))
            # Redimensionner le sprite original à la taille définie dans le preset avec antialiasing
            original_sprite = Enemy.sprites[self.sprite_id]
            if config.SPRITE_SMOOTHING:
                self.sprite = pygame.transform.smoothscale(original_sprite, (self.size, self.size))
            else:
                self.sprite = pygame.transform.scale(original_sprite, (self.size, self.size))
            # Optimiser le format pour un rendu plus rapide
            self.sprite = self.sprite.convert_alpha()
        else:
            self.sprite_id = None
            self.sprite = None
        
        # Calcul des points de vie selon la vague et le type d'ennemi
        base_health = config.ENEMY_HEALTH
        wave_bonus = (wave_number - 1)  # Vague 1 = +0, Vague 2 = +1, etc.
        
        # Ennemi spécial
        self.is_special = is_special
        if is_special:
            # Points de vie spéciaux avec progression par vague
            special_wave_bonus = wave_bonus * config.SPECIAL_ENEMY_HEALTH_INCREASE_PER_WAVE
            self.max_health = int((base_health + wave_bonus * config.ENEMY_HEALTH_INCREASE_PER_WAVE) * config.SPECIAL_ENEMY_HEALTH_MULTIPLIER + special_wave_bonus)
            self.bonus_type = random.choice(config.BONUS_TYPES)
            # Taille x2 pour les ennemis spéciaux
            self.size = config.ENEMY_SIZE * 2
            # Redimensionner le sprite à la nouvelle taille avec antialiasing
            if self.sprite:
                if config.SPRITE_SMOOTHING:
                    self.sprite = pygame.transform.smoothscale(Enemy.sprites[self.sprite_id], (self.size, self.size))
                else:
                    self.sprite = pygame.transform.scale(Enemy.sprites[self.sprite_id], (self.size, self.size))
                # Optimiser le format
                self.sprite = self.sprite.convert_alpha()
        else:
            # Points de vie normaux avec progression par vague
            self.max_health = base_health + wave_bonus * config.ENEMY_HEALTH_INCREASE_PER_WAVE
            self.bonus_type = None
            
        self.health = self.max_health
        
        # Animation de rotation (ping-pong de -5° à +5° accéléré)
        self.rotation_angle = 0
        self.rotation_time = 0
        self.rotation_speed = 5  # Vitesse de rotation accélérée (20 au lieu de 10)
        
        # Composante aléatoire pour l'IA
        self.random_offset_x = 0
        self.random_offset_y = 0
        self.random_timer = 0
    
    def update(self, player_x, player_y):
        """Met à jour la position de l'ennemi (suit le joueur)"""
        # Mise à jour de l'animation de rotation accélérée avec rotation_speed
        dt = 1.0 / 60.0  # Delta time assumant 60 FPS
        self.rotation_time += dt * self.rotation_speed  # Utiliser rotation_speed pour accélérer
        
        # Calculer l'angle de rotation en ping-pong (-5° à +5°)
        # La vitesse est maintenant contrôlée par rotation_speed
        self.rotation_angle = 5 * math.sin(self.rotation_time * math.pi)
        
        # Mise à jour du mouvement aléatoire
        self.random_timer += 1
        if self.random_timer >= 30:  # Change de direction toutes les 0.5 secondes
            self.random_offset_x = random.uniform(-0.5, 0.5)
            self.random_offset_y = random.uniform(-0.5, 0.5)
            self.random_timer = 0
        
        # Direction vers le joueur
        dx = player_x - (self.x + self.size//2)
        dy = player_y - (self.y + self.size//2)
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normaliser et ajouter composante aléatoire
            dx = (dx / distance) + self.random_offset_x
            dy = (dy / distance) + self.random_offset_y
            # Normalisation pour vitesse constante
            norm = math.sqrt(dx**2 + dy**2)
            if norm > 0:
                dx = dx / norm
                dy = dy / norm
            # Appliquer le facteur de correction pour équilibrer avec le système d'accélération du joueur
            corrected_speed = self.speed * self.config.ENEMY_SPEED_CORRECTION_FACTOR
            # Déplacer l'ennemi
            self.x += dx * corrected_speed
            self.y += dy * corrected_speed
    
    def take_damage(self, damage):
        """Fait subir des dégâts à l'ennemi"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine l'ennemi avec animation de rotation"""
        if self.sprite:
            # Appliquer la rotation au sprite
            rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation_angle)
            
            # Calculer la nouvelle position pour centrer le sprite tourné
            rotated_rect = rotated_sprite.get_rect()
            sprite_center_x = self.x + self.size // 2
            sprite_center_y = self.y + self.size // 2
            rotated_rect.center = (sprite_center_x, sprite_center_y)
            
            # Dessiner le sprite tourné
            screen.blit(rotated_sprite, rotated_rect)
        else:
            # Fallback : dessiner des carrés colorés si les sprites ne sont pas chargés
            enemy_color = self.config.ENEMY_COLOR  # Couleur normale pour tous les ennemis
            
            # Corps principal avec antialiasing si activé
            if self.config.ENABLE_ANTIALIASING:
                # Utiliser un rectangle avec antialiasing (approximation avec gfxdraw)
                points = [
                    (int(self.x), int(self.y)),
                    (int(self.x + self.size), int(self.y)),
                    (int(self.x + self.size), int(self.y + self.size)),
                    (int(self.x), int(self.y + self.size))
                ]
                pygame.gfxdraw.filled_polygon(screen, points, enemy_color)
                pygame.gfxdraw.aapolygon(screen, points, enemy_color)
                
                # Contour blanc avec antialiasing (plus épais pour les ennemis spéciaux)
                border_width = 3 if self.is_special else 2
                for i in range(border_width):
                    border_points = [
                        (int(self.x - i), int(self.y - i)),
                        (int(self.x + self.size + i), int(self.y - i)),
                        (int(self.x + self.size + i), int(self.y + self.size + i)),
                        (int(self.x - i), int(self.y + self.size + i))
                    ]
                    pygame.gfxdraw.aapolygon(screen, border_points, self.config.WHITE)
            else:
                # Rendu normal sans antialiasing
                pygame.draw.rect(screen, enemy_color,
                                (int(self.x), int(self.y), self.size, self.size))
                
                # Contour blanc (plus épais pour les ennemis spéciaux)
                border_width = 3 if self.is_special else 2
                pygame.draw.rect(screen, self.config.WHITE,
                                (int(self.x), int(self.y), self.size, self.size), border_width)
            
            # Effet scintillant pour les ennemis spéciaux (inchangé)
            if self.is_special:
                pulse = int(50 * (1 + math.sin(pygame.time.get_ticks() * 0.01)))
                glow_color = (255, 255, 255, pulse)
                glow_rect = pygame.Rect(self.x - 2, self.y - 2, self.size + 4, self.size + 4)
                if self.config.ENABLE_ANTIALIASING:
                    # Contour avec antialiasing pour l'effet de scintillement
                    glow_points = [
                        (int(self.x - 2), int(self.y - 2)),
                        (int(self.x + self.size + 2), int(self.y - 2)),
                        (int(self.x + self.size + 2), int(self.y + self.size + 2)),
                        (int(self.x - 2), int(self.y + self.size + 2))
                    ]
                    pygame.gfxdraw.aapolygon(screen, glow_points, self.config.WHITE)
                else:
                    pygame.draw.rect(screen, self.config.WHITE, glow_rect, 1)
        
        # Barre de santé si endommagé (au-dessus du sprite)
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = self.size
            bar_height = 4
            
            # Fond rouge
            pygame.draw.rect(screen, self.config.RED,
                           (int(self.x), int(self.y - 8), bar_width, bar_height))
            
            # Santé actuelle
            current_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, self.config.GREEN,
                           (int(self.x), int(self.y - 8), current_width, bar_height))


class Enemy:
    """Classe des ennemis avec IA de poursuite"""
    
    # Variables de classe pour les sprites (chargés une seule fois)
    sprites = None
    sprites_loaded = False
    
    @classmethod
    def load_sprites(cls):
        """Charge tous les sprites d'ennemis une seule fois"""
        if not cls.sprites_loaded:
            cls.sprites = {}
            try:
                # Charger les sprites 1.png à 5.png
                for i in range(1, 24):
                    sprite_path = f"assets/Enemy/{i}.png"
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    # Les sprites sont maintenant redimensionnés selon le preset actuel
                    # La taille sera définie lors de l'initialisation de l'ennemi
                    cls.sprites[i] = sprite  # Garder le sprite original pour le redimensionner plus tard
                cls.sprites_loaded = True
                print(f"{len(cls.sprites)} sprites d'ennemis chargés (redimensionnement selon preset)")
            except Exception as e:
                print(f"Erreur lors du chargement des sprites: {e}")
                cls.sprites = {}
                cls.sprites_loaded = True
    
    def __init__(self, x, y, config, is_special=False, wave_number=1):
        # Charger les sprites si ce n'est pas déjà fait
        if not Enemy.sprites_loaded:
            Enemy.load_sprites()
        
        self.x = x
        self.y = y
        self.config = config
        self.size = config.ENEMY_SIZE
        self.speed = config.ENEMY_SPEED
        
        # Choisir un sprite aléatoire pour cet ennemi et le redimensionner à la bonne taille
        if Enemy.sprites:
            self.sprite_id = random.choice(list(Enemy.sprites.keys()))
            # Redimensionner le sprite original à la taille définie dans le preset avec antialiasing
            original_sprite = Enemy.sprites[self.sprite_id]
            if config.SPRITE_SMOOTHING:
                self.sprite = pygame.transform.smoothscale(original_sprite, (self.size, self.size))
            else:
                self.sprite = pygame.transform.scale(original_sprite, (self.size, self.size))
            # Optimiser le format pour un rendu plus rapide
            self.sprite = self.sprite.convert_alpha()
        else:
            self.sprite_id = None
            self.sprite = None
        
        # Calcul des points de vie selon la vague et le type d'ennemi
        base_health = config.ENEMY_HEALTH
        wave_bonus = (wave_number - 1)  # Vague 1 = +0, Vague 2 = +1, etc.
        
        # Ennemi spécial
        self.is_special = is_special
        if is_special:
            # Points de vie spéciaux avec progression par vague
            special_wave_bonus = wave_bonus * config.SPECIAL_ENEMY_HEALTH_INCREASE_PER_WAVE
            self.max_health = int((base_health + wave_bonus * config.ENEMY_HEALTH_INCREASE_PER_WAVE) * config.SPECIAL_ENEMY_HEALTH_MULTIPLIER + special_wave_bonus)
            self.bonus_type = random.choice(config.BONUS_TYPES)
            # Taille x2 pour les ennemis spéciaux
            self.size = config.ENEMY_SIZE * 2
            # Redimensionner le sprite à la nouvelle taille avec antialiasing
            if self.sprite:
                if config.SPRITE_SMOOTHING:
                    self.sprite = pygame.transform.smoothscale(Enemy.sprites[self.sprite_id], (self.size, self.size))
                else:
                    self.sprite = pygame.transform.scale(Enemy.sprites[self.sprite_id], (self.size, self.size))
                # Optimiser le format
                self.sprite = self.sprite.convert_alpha()
        else:
            # Points de vie normaux avec progression par vague
            self.max_health = base_health + wave_bonus * config.ENEMY_HEALTH_INCREASE_PER_WAVE
            self.bonus_type = None
            
        self.health = self.max_health
        
        # Animation de rotation (ping-pong de -5° à +5° accéléré)
        self.rotation_angle = 0
        self.rotation_time = 0
        self.rotation_speed = 5  # Vitesse de rotation accélérée (20 au lieu de 10)
        
        # Composante aléatoire pour l'IA
        self.random_offset_x = 0
        self.random_offset_y = 0
        self.random_timer = 0
    
    def update(self, player_x, player_y):
        """Met à jour la position de l'ennemi (suit le joueur)"""
        # Mise à jour de l'animation de rotation accélérée avec rotation_speed
        dt = 1.0 / 60.0  # Delta time assumant 60 FPS
        self.rotation_time += dt * self.rotation_speed  # Utiliser rotation_speed pour accélérer
        
        # Calculer l'angle de rotation en ping-pong (-5° à +5°)
        # La vitesse est maintenant contrôlée par rotation_speed
        self.rotation_angle = 5 * math.sin(self.rotation_time * math.pi)
        
        # Mise à jour du mouvement aléatoire
        self.random_timer += 1
        if self.random_timer >= 30:  # Change de direction toutes les 0.5 secondes
            self.random_offset_x = random.uniform(-0.5, 0.5)
            self.random_offset_y = random.uniform(-0.5, 0.5)
            self.random_timer = 0
        
        # Direction vers le joueur
        dx = player_x - (self.x + self.size//2)
        dy = player_y - (self.y + self.size//2)
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normaliser et ajouter composante aléatoire
            dx = (dx / distance) + self.random_offset_x
            dy = (dy / distance) + self.random_offset_y
            # Normalisation pour vitesse constante
            norm = math.sqrt(dx**2 + dy**2)
            if norm > 0:
                dx = dx / norm
                dy = dy / norm
            # Appliquer le facteur de correction pour équilibrer avec le système d'accélération du joueur
            corrected_speed = self.speed * self.config.ENEMY_SPEED_CORRECTION_FACTOR
            # Déplacer l'ennemi
            self.x += dx * corrected_speed
            self.y += dy * corrected_speed
    
    def take_damage(self, damage):
        """Fait subir des dégâts à l'ennemi"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine l'ennemi avec animation de rotation"""
        if self.sprite:
            # Appliquer la rotation au sprite
            rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation_angle)
            
            # Calculer la nouvelle position pour centrer le sprite tourné
            rotated_rect = rotated_sprite.get_rect()
            sprite_center_x = self.x + self.size // 2
            sprite_center_y = self.y + self.size // 2
            rotated_rect.center = (sprite_center_x, sprite_center_y)
            
            # Dessiner le sprite tourné
            screen.blit(rotated_sprite, rotated_rect)
        else:
            # Fallback : dessiner des carrés colorés si les sprites ne sont pas chargés
            enemy_color = self.config.ENEMY_COLOR  # Couleur normale pour tous les ennemis
            
            # Corps principal avec antialiasing si activé
            if self.config.ENABLE_ANTIALIASING:
                # Utiliser un rectangle avec antialiasing (approximation avec gfxdraw)
                points = [
                    (int(self.x), int(self.y)),
                    (int(self.x + self.size), int(self.y)),
                    (int(self.x + self.size), int(self.y + self.size)),
                    (int(self.x), int(self.y + self.size))
                ]
                pygame.gfxdraw.filled_polygon(screen, points, enemy_color)
                pygame.gfxdraw.aapolygon(screen, points, enemy_color)
                
                # Contour blanc avec antialiasing (plus épais pour les ennemis spéciaux)
                border_width = 3 if self.is_special else 2
                for i in range(border_width):
                    border_points = [
                        (int(self.x - i), int(self.y - i)),
                        (int(self.x + self.size + i), int(self.y - i)),
                        (int(self.x + self.size + i), int(self.y + self.size + i)),
                        (int(self.x - i), int(self.y + self.size + i))
                    ]
                    pygame.gfxdraw.aapolygon(screen, border_points, self.config.WHITE)
            else:
                # Rendu normal sans antialiasing
                pygame.draw.rect(screen, enemy_color,
                                (int(self.x), int(self.y), self.size, self.size))
                
                # Contour blanc (plus épais pour les ennemis spéciaux)
                border_width = 3 if self.is_special else 2
                pygame.draw.rect(screen, self.config.WHITE,
                                (int(self.x), int(self.y), self.size, self.size), border_width)
            
            # Effet scintillant pour les ennemis spéciaux (inchangé)
            if self.is_special:
                pulse = int(50 * (1 + math.sin(pygame.time.get_ticks() * 0.01)))
                glow_color = (255, 255, 255, pulse)
                glow_rect = pygame.Rect(self.x - 2, self.y - 2, self.size + 4, self.size + 4)
                if self.config.ENABLE_ANTIALIASING:
                    # Contour avec antialiasing pour l'effet de scintillement
                    glow_points = [
                        (int(self.x - 2), int(self.y - 2)),
                        (int(self.x + self.size + 2), int(self.y - 2)),
                        (int(self.x + self.size + 2), int(self.y + self.size + 2)),
                        (int(self.x - 2), int(self.y + self.size + 2))
                    ]
                    pygame.gfxdraw.aapolygon(screen, glow_points, self.config.WHITE)
                else:
                    pygame.draw.rect(screen, self.config.WHITE, glow_rect, 1)
        
        # Barre de santé si endommagé (au-dessus du sprite)
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = self.size
            bar_height = 4
            
            # Fond rouge
            pygame.draw.rect(screen, self.config.RED,
                           (int(self.x), int(self.y - 8), bar_width, bar_height))
            
            # Santé actuelle
            current_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, self.config.GREEN,
                           (int(self.x), int(self.y - 8), current_width, bar_height))


class Zap:
    """Classe des projectiles électriques"""
    
    def __init__(self, x, y, dx, dy, config):
        self.x = x
        self.y = y
        self.config = config
        self.size = config.ZAP_SIZE
        self.speed = config.ZAP_SPEED
        
        # Direction normalisée
        self.dx = dx
        self.dy = dy
    
    def update(self):
        """Met à jour la position du zap"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
    
    def draw(self, screen):
        """Dessine le zap comme un éclair"""
        # Ligne principale (éclair)
        end_x = self.x + self.dx * 20
        end_y = self.y + self.dy * 20
        
        pygame.draw.line(screen, self.config.ZAP_COLOR,
                        (int(self.x), int(self.y)),
                        (int(end_x), int(end_y)), 2)
        
        # Point lumineux au centre
        pygame.draw.circle(screen, self.config.WHITE,
                         (int(self.x), int(self.y)), self.size)


class Lightning:
    """Classe pour les éclairs instantanés"""
    
    def __init__(self, start_x, start_y, target_x, target_y, config, is_chained=False):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.config = config
        self.damage = config.LIGHTNING_DAMAGE
        self.is_chained = is_chained  # Nouveau paramètre
        
        # Durée d'affichage
        self.lifetime = config.LIGHTNING_DISPLAY_TIME
        self.current_life = self.lifetime
        
        # Points intermédiaires pour effet de zigzag
        self.points = self.generate_lightning_points()
    
    def generate_lightning_points(self):
        """Génère des points intermédiaires pour l'effet de zigzag"""
        points = [(self.start_x, self.start_y)]
        
        # Nombre de segments
        segments = 5
        
        for i in range(1, segments):
            # Interpolation linéaire entre start et target
            t = i / segments
            x = self.start_x + (self.target_x - self.start_x) * t
            y = self.start_y + (self.target_y - self.start_y) * t
            
            # Ajouter du bruit pour l'effet zigzag
            offset = self.config.WINDOW_WIDTH * 0.02  # 2% de la largeur
            x += random.uniform(-offset, offset)
            y += random.uniform(-offset, offset)
            
            points.append((x, y))
        
        points.append((self.target_x, self.target_y))
        return points
    
    def update(self):
        """Met à jour l'éclair"""
        self.current_life -= 1
        return self.current_life > 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine l'éclair avec effet de zigzag"""
        if self.current_life <= 0:
            return
        
        # Intensité basée sur la durée de vie restante
        intensity = self.current_life / self.lifetime
        
        # Couleurs différentes selon le type d'éclair
        if self.is_chained:
            # Éclair chaîné : couleur violette/magenta
            color = tuple(int(c * intensity) for c in (255, 100, 255))
            secondary_color = tuple(int(c * intensity) for c in (200, 50, 200))
            thickness = 4  # Augmenté de 2 à 4
        else:
            # Éclair principal : couleur blanche/bleue
            color = tuple(int(c * intensity) for c in self.config.LIGHTNING_COLOR)
            secondary_color = tuple(int(c * intensity) for c in self.config.LIGHTNING_SECONDARY_COLOR)
            thickness = 6  # Augmenté de 3 à 6
        
        # Dessiner les segments de l'éclair avec ajustement de caméra
        for i in range(len(self.points) - 1):
            start_point = (int(self.points[i][0] - camera_x), int(self.points[i][1] - camera_y))
            end_point = (int(self.points[i + 1][0] - camera_x), int(self.points[i + 1][1] - camera_y))
            
            # Ligne principale (plus épaisse)
            pygame.draw.line(screen, color, start_point, end_point, thickness)
            
            # Ligne secondaire pour l'effet de lueur (plus épaisse aussi)
            pygame.draw.line(screen, secondary_color, start_point, end_point, thickness // 2)
            
            # Ligne centrale ultra-brillante
            inner_color = tuple(min(255, int(c * 1.5)) for c in color)
            pygame.draw.line(screen, inner_color, start_point, end_point, max(1, thickness // 3))


class Particle:
    """Classe pour les particules d'explosion"""
    
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        
        # Vélocité aléatoire
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 1.5) * config.PARTICLE_SPEED
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        
        # Propriétés visuelles
        self.color = random.choice(config.PARTICLE_COLORS)
        self.size = random.randint(1, config.PARTICLE_SIZE)
        self.lifetime = config.PARTICLE_LIFETIME
        self.current_life = self.lifetime
        
        # Gravité légère
        self.gravity = 0.1
    
    def update(self):
        """Met à jour la particule"""
        # Mouvement
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Gravité
        self.vel_y += self.gravity
        
        # Friction
        self.vel_x *= 0.98
        self.vel_y *= 0.98
        
        # Durée de vie
        self.current_life -= 1
        
        return self.current_life > 0
    
    def draw(self, screen):
        """Dessine la particule"""
        if self.current_life <= 0:
            return
        
        # Transparence basée sur la durée de vie
        alpha = self.current_life / self.lifetime
        
        # Couleur avec transparence
        color = tuple(int(c * alpha) for c in self.color)
        
        # Dessiner la particule
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class WeldingParticle:
    """Classe pour les particules de soudure (effet du Beam)"""
    
    def __init__(self, x, y, config, direction_x=None, direction_y=None):
        self.x = x
        self.y = y
        self.config = config
        
        # Particules plus rapides et dans toutes les directions
        if direction_x is not None and direction_y is not None:
            # 50% des particules rebondissent depuis l'impact
            if random.random() < 0.5:
                angle_variation = math.pi / 3  # 60° de variation (plus large)
                base_angle = math.atan2(direction_y, direction_x) + math.pi  # Direction opposée
                angle = base_angle + random.uniform(-angle_variation, angle_variation)
            else:
                # 50% des particules vont dans toutes les directions
                angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 6.0) * config.PARTICLE_SPEED  # Beaucoup plus rapides
        else:
            # Particules complètement aléatoires et rapides
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 5.0) * config.PARTICLE_SPEED
            
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        
        # Propriétés visuelles TRÈS brillantes pour la soudure
        self.color = random.choice([
            (255, 255, 255),  # Blanc éclatant
            (255, 255, 255),  # Plus de blanc pour plus de brillance
            (255, 255, 200),  # Jaune très brillant
            (255, 255, 150),  # Jaune éclatant
            (200, 255, 255),  # Bleu électrique brillant
            (255, 200, 255),  # Violet électrique brillant
            (255, 255, 100),  # Jaune pur brillant
            (150, 255, 255),  # Cyan électrique
        ])
        self.size = 1  # Particules très petites comme de vraies étincelles
        self.lifetime = random.randint(12, 25)  # Durée de vie réduite
        self.current_life = self.lifetime
        
        # Pas de gravité pour l'effet de soudure (particules électriques)
        self.gravity = 0
        
        # Scintillement plus intense
        self.flicker_timer = 0
        self.flicker_speed = random.uniform(0.3, 0.8)  # Vitesse de scintillement variée
    
    def update(self):
        """Met à jour la particule de soudure"""
        # Mouvement
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Friction moins importante pour garder la vitesse
        self.vel_x *= 0.97  # Moins de friction = plus rapide plus longtemps
        self.vel_y *= 0.97
        
        # Durée de vie
        self.current_life -= 1
        self.flicker_timer += 1
        
        return self.current_life > 0
    
    def draw(self, screen):
        """Dessine la particule de soudure avec effet TRÈS brillant"""
        if self.current_life <= 0:
            return
        
        # Transparence basée sur la durée de vie
        alpha = self.current_life / self.lifetime
        
        # Effet de scintillement INTENSE
        flicker = 0.6 + 0.4 * math.sin(self.flicker_timer * self.flicker_speed)
        alpha *= flicker
        
        # Intensité augmentée pour plus de brillance
        brightness_multiplier = 1.3  # 30% plus brillant
        color = tuple(min(255, int(c * alpha * brightness_multiplier)) for c in self.color)
        
        # Dessiner la particule avec effet de halo INTENSE mais adapté à la petite taille
        center_x, center_y = int(self.x), int(self.y)
        
        if self.config.ENABLE_ANTIALIASING:
            # Version avec antialiasing - effet de halo réduit pour petites particules
            halo_size = self.size + 1  # Halo très petit
            for i in range(halo_size, 0, -1):
                halo_alpha = alpha * (1.0 - i / (halo_size + 2)) * 0.4  # Halo plus subtil
                halo_color = tuple(min(255, int(c * halo_alpha * brightness_multiplier)) for c in self.color)
                try:
                    pygame.gfxdraw.filled_circle(screen, center_x, center_y, i, halo_color)
                    pygame.gfxdraw.aacircle(screen, center_x, center_y, i, halo_color)
                except:
                    pygame.draw.circle(screen, halo_color, (center_x, center_y), i)
            
            # Centre ultra-brillant (toujours au moins 1 pixel)
            core_color = tuple(min(255, int(c * alpha * 1.5)) for c in self.color)  # Centre 50% plus brillant
            try:
                pygame.gfxdraw.filled_circle(screen, center_x, center_y, 1, core_color)
                pygame.gfxdraw.aacircle(screen, center_x, center_y, 1, core_color)
            except:
                pygame.draw.circle(screen, core_color, (center_x, center_y), 1)
        else:
            # Version normale avec halo manuel très réduit
            # Halo minimal pour petites particules
            if self.size > 1:
                halo_alpha = alpha * 0.3
                halo_color = tuple(min(255, int(c * halo_alpha * brightness_multiplier)) for c in self.color)
                pygame.draw.circle(screen, halo_color, (center_x, center_y), self.size + 1)
            
            # Centre brillant (toujours au moins 1 pixel)
            pygame.draw.circle(screen, color, (center_x, center_y), max(1, self.size))


class EnergyOrb:
    """Classe pour les boules d'énergie qui orbitent autour du joueur"""
    
    def __init__(self, player_x, player_y, orb_index, total_orbs, config):
        self.config = config
        self.orb_index = orb_index
        self.total_orbs = total_orbs
        
        # Calcul de l'angle de départ basé sur la répartition uniforme
        self.base_angle = (orb_index * 2 * math.pi) / total_orbs
        self.angle = self.base_angle
        
        self.radius = config.ENERGY_ORB_RADIUS
        self.size = config.ENERGY_ORB_SIZE
        self.damage = config.ENERGY_ORB_DAMAGE
        
        # Calcul de la position initiale
        self.x = player_x + math.cos(self.angle) * self.radius
        self.y = player_y + math.sin(self.angle) * self.radius
        
        # Vitesse constante
        self.angular_speed = config.ENERGY_ORB_SPEED
        
        # Effet de pulsation
        self.pulse_timer = 0
        self.pulse_intensity = 1.0
    
    def update(self, player_x, player_y):
        """Met à jour la position de la boule d'énergie"""
        # Mise à jour de l'angle avec vitesse constante
        self.angle += self.angular_speed
        
        # Garder l'angle dans [0, 2π]
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
        
        # Calcul de la nouvelle position
        self.x = player_x + math.cos(self.angle) * self.radius
        self.y = player_y + math.sin(self.angle) * self.radius
        
        # Mise à jour de l'effet de pulsation
        self.pulse_timer += 1
        self.pulse_intensity = 0.8 + 0.2 * math.sin(self.pulse_timer * 0.2)
        
        return True  # Les orbes persistent maintenant
    
    def draw(self, screen):
        """Dessine la boule d'énergie avec effet de lueur"""
        # Intensité basée sur la pulsation (plus de diminution due à la durée de vie)
        intensity = self.pulse_intensity
        
        # Couleurs avec intensité variable
        core_color = tuple(int(c * intensity) for c in self.config.ENERGY_ORB_COLOR)
        glow_color = tuple(int(c * intensity * 0.7) for c in self.config.ENERGY_ORB_GLOW_COLOR)
        
        # Dessiner l'aura (cercle plus grand, semi-transparent)
        aura_size = int(self.size * 1.5)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), aura_size)
        
        # Dessiner le noyau principal
        pygame.draw.circle(screen, core_color, (int(self.x), int(self.y)), self.size)
        
        # Dessiner le point lumineux central
        center_color = tuple(min(255, int(c * 1.2)) for c in self.config.WHITE)
        pygame.draw.circle(screen, center_color, (int(self.x), int(self.y)), self.size // 2)
    
    def get_collision_rect(self):
        """Retourne le rectangle de collision"""
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class BonusManager:
    """Gestionnaire des bonus temporaires du joueur"""
    
    def __init__(self, config):
        self.config = config
        self.active_bonuses = {}  # {bonus_type: frames_restants}
        
        # États temporaires
        self.shield_hits_remaining = 0
        self.original_speed = None
        
    def apply_bonus(self, bonus_type, game_instance):
        """Applique un bonus selon son type"""
        if bonus_type == "bomb":
            # Bombe générale - élimine tous les ennemis
            enemies_killed = len(game_instance.enemies)
            game_instance.enemies.clear()
            game_instance.score += enemies_killed * game_instance.config.SCORE_PER_ENEMY_KILL
            print(f"💣 Bombe ! {enemies_killed} ennemis éliminés")
            
        elif bonus_type == "heal":
            # Potion de soin
            old_health = game_instance.player.health
            game_instance.player.health = min(
                game_instance.player.max_health,
                game_instance.player.health + self.config.BONUS_HEAL_AMOUNT
            )
            healed = game_instance.player.health - old_health
            print(f"Soigné de {healed} points de vie")
            
        elif bonus_type == "shield":
            # Aura de protection
            self.shield_hits_remaining = self.config.BONUS_SHIELD_HITS
            print(f"Bouclier activé ({self.shield_hits_remaining} coups)")
            
        elif bonus_type == "double_damage":
            # Double dégâts
            self.active_bonuses["double_damage"] = self.config.BONUS_DOUBLE_DAMAGE_DURATION
            print("Double dégâts activé")
            
        elif bonus_type == "lightning_storm":
            # Tempête d'éclairs
            player_center_x = game_instance.player.x + game_instance.player.size // 2
            player_center_y = game_instance.player.y + game_instance.player.size // 2
            
            for _ in range(self.config.BONUS_LIGHTNING_STORM_COUNT):
                if game_instance.enemies:
                    target = random.choice(game_instance.enemies)
                    lightning = Lightning(
                        player_center_x, player_center_y,
                        target.x + target.size // 2, target.y + target.size // 2,
                        self.config
                    )
                    game_instance.lightnings.append(lightning)
            print(f"Tempête d'éclairs ! {self.config.BONUS_LIGHTNING_STORM_COUNT} éclairs")
            
        elif bonus_type == "speed_boost":
            # Boost de vitesse
            if self.original_speed is None:
                self.original_speed = game_instance.player.speed
            game_instance.player.speed = self.original_speed * self.config.BONUS_SPEED_BOOST_MULTIPLIER
            self.active_bonuses["speed_boost"] = self.config.BONUS_SPEED_BOOST_DURATION
            print("Boost de vitesse activé")
            
        elif bonus_type == "invincibility":
            # Invincibilité temporaire
            self.active_bonuses["invincibility"] = self.config.BONUS_INVINCIBILITY_DURATION
            print("Invincibilité activée")
            
        elif bonus_type == "time_slow":
            # Ralentissement du temps
            self.active_bonuses["time_slow"] = self.config.BONUS_TIME_SLOW_DURATION
            print("Temps ralenti")
            
        elif bonus_type == "freeze":
            # Gel des ennemis
            self.active_bonuses["freeze"] = self.config.BONUS_FREEZE_DURATION
            print("Ennemis gelés")
    
    def update(self, game_instance):
        """Met à jour les bonus actifs"""
        # Décrémenter les durées
        for bonus_type in list(self.active_bonuses.keys()):
            self.active_bonuses[bonus_type] -= 1
            if self.active_bonuses[bonus_type] <= 0:
                self._end_bonus(bonus_type, game_instance)
                del self.active_bonuses[bonus_type]
    
    def _end_bonus(self, bonus_type, game_instance):
        """Termine un bonus"""
        if bonus_type == "speed_boost" and self.original_speed is not None:
            game_instance.player.speed = self.original_speed
            self.original_speed = None
            print("Boost de vitesse terminé")
        elif bonus_type == "invincibility":
            print("Invincibilité terminée")
        elif bonus_type == "time_slow":
            print("Temps normal")
        elif bonus_type == "freeze":
            print("Dégel des ennemis")
    
    def can_take_damage(self):
        """Vérifie si le joueur peut subir des dégâts"""
        # Bouclier
        if self.shield_hits_remaining > 0:
            self.shield_hits_remaining -= 1
            print(f"Bouclier ! ({self.shield_hits_remaining} coups restants)")
            return False
        
        # Invincibilité
        if "invincibility" in self.active_bonuses:
            return False
            
        return True
    
    def get_damage_multiplier(self):
        """Retourne le multiplicateur de dégâts"""
        return 2.0 if "double_damage" in self.active_bonuses else 1.0
    
    def get_enemy_speed_multiplier(self):
        """Retourne le multiplicateur de vitesse des ennemis"""
        if "time_slow" in self.active_bonuses:
            return self.config.BONUS_TIME_SLOW_FACTOR
        elif "freeze" in self.active_bonuses:
            return 0.0
        return 1.0
    
    def is_active(self, bonus_type):
        """Vérifie si un bonus est actif"""
        return bonus_type in self.active_bonuses


class Beam:
    """
    Classe pour les rayons laser continus avec rotation
    
    NOUVEAU COMPORTEMENT:
    - Vise l'ennemi le plus proche au moment de la création
    - Effectue une rotation antihoraire autour du joueur pendant sa durée de vie
    - La rotation augmente avec le niveau (30° à 360° au niveau 10)
    - La durée augmente avec le niveau (1s à 3s au niveau 10)
    """
    
    def __init__(self, start_x, start_y, direction_x, direction_y, config, level, player=None):
        from weapon_config import get_weapon_stat
        
        # Position du joueur (centre de rotation)
        self.player = player
        self.center_x = start_x
        self.center_y = start_y
        
        self.config = config
        self.level = level
        
        # Propriétés du faisceau
        self.range = get_weapon_stat("Beam", "range", level)
        self.width = get_weapon_stat("Beam", "width", level)
        self.damage = get_weapon_stat("Beam", "damage", level)
        
        # Nouvelle gestion de la durée et rotation avec progressions
        beam_config = getattr(config, 'BEAM', None)
        if hasattr(config, 'BEAM') and hasattr(config.BEAM, 'duration_progression'):
            # Si on a accès à la config complète
            duration_progression = getattr(config.BEAM, 'duration_progression', [60] * 10)
            rotation_progression = getattr(config.BEAM, 'rotation_progression', [30] * 10)
        else:
            # Fallback avec progressions codées en dur
            duration_progression = [60, 75, 90, 105, 120, 135, 150, 165, 180, 180]
            rotation_progression = [30, 45, 60, 90, 120, 180, 240, 270, 320, 360]
        
        # Durée et rotation selon le niveau
        level_index = min(level - 1, len(duration_progression) - 1)
        self.duration = duration_progression[level_index]
        self.total_rotation_degrees = rotation_progression[level_index]
        
        self.current_life = self.duration
        
        # Angle initial vers l'ennemi le plus proche
        self.initial_angle = math.atan2(direction_y, direction_x)
        self.current_angle = self.initial_angle
        
        # Vitesse de rotation (antihoraire)
        self.rotation_speed = math.radians(self.total_rotation_degrees) / self.duration  # radians par frame
        
        # Calcul des points actuels du beam
        self.start_x = self.center_x
        self.start_y = self.center_y
        self.end_x = self.center_x + math.cos(self.current_angle) * self.range
        self.end_y = self.center_y + math.sin(self.current_angle) * self.range
        
        # Liste des ennemis déjà touchés pour éviter les dégâts multiples
        self.hit_enemies = set()
        
        # Timer pour la génération continue de particules
        self.particle_timer = 0
    
    def update(self):
        """Met à jour le faisceau avec rotation antihoraire"""
        self.current_life -= 1
        self.particle_timer += 1  # Incrémenter le timer des particules
        
        # Mettre à jour la position du centre avec le joueur
        if self.player:
            player_center_x = self.player.x + self.player.size // 2
            player_center_y = self.player.y + self.player.size // 2
            self.center_x = player_center_x
            self.center_y = player_center_y
        
        # Effectuer la rotation antihoraire
        self.current_angle = self.initial_angle + (self.duration - self.current_life) * self.rotation_speed
        
        # Recalculer les points du beam
        self.start_x = self.center_x
        self.start_y = self.center_y
        self.end_x = self.center_x + math.cos(self.current_angle) * self.range
        self.end_y = self.center_y + math.sin(self.current_angle) * self.range
        
        return self.current_life > 0
    
    def check_collision_with_enemies(self, enemies, game=None):
        """Vérifie les collisions avec les ennemis et applique les dégâts"""
        hit_positions = []
        continuous_hits = []  # Pour les particules continues
        
        # Direction actuelle du beam pour les particules
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        beam_length = math.sqrt(dx**2 + dy**2)
        if beam_length > 0:
            current_direction_x = dx / beam_length
            current_direction_y = dy / beam_length
        else:
            current_direction_x, current_direction_y = 1, 0
        
        for enemy in enemies:
            # Vérifier si l'ennemi intersecte avec le rayon laser
            if self.line_intersects_rect(enemy):
                # Calculer le point d'impact pour les particules
                impact_x = enemy.x + enemy.size // 2
                impact_y = enemy.y + enemy.size // 2
                
                # Générer des particules de soudure en continu (fréquence réduite)
                if game and self.particle_timer % 4 == 0:  # Toutes les 4 frames = effet continu mais plus modéré
                    game.create_welding_particles(impact_x, impact_y, 
                                                 current_direction_x, 
                                                 current_direction_y)
                
                # Appliquer les dégâts seulement une fois par ennemi
                if id(enemy) not in self.hit_enemies:
                    enemy_was_alive = enemy.health > 0
                    enemy.take_damage(self.damage)
                    self.hit_enemies.add(id(enemy))
                    
                    # Si l'ennemi est éliminé, créer une explosion renforcée
                    if enemy_was_alive and enemy.health <= 0 and game:
                        game.create_beam_explosion_particles(impact_x, impact_y)
                
                hit_positions.append((impact_x, impact_y))
                continuous_hits.append((impact_x, impact_y))
        
        return hit_positions
    
    def line_intersects_rect(self, enemy):
        """Vérifie si le rayon laser intersecte avec un cercle (ennemi)"""
        # Centre du cercle de l'ennemi
        enemy_center_x = enemy.x + enemy.size // 2
        enemy_center_y = enemy.y + enemy.size // 2
        enemy_radius = enemy.size // 2  # Rayon = largeur du sprite / 2
        
        # Distance du centre de l'ennemi à la ligne du laser
        distance_to_line = self.point_to_line_distance(enemy_center_x, enemy_center_y)
        
        # Vérifier si le cercle intersecte avec la ligne
        if distance_to_line <= enemy_radius + self.width / 2:
            # Vérifier que le point est dans la portée du rayon
            proj = self.project_point_on_line(enemy_center_x, enemy_center_y)
            if 0 <= proj <= 1:  # Le point projeté est sur le segment
                return True
        
        return False
    
    def point_to_line_distance(self, px, py):
        """Calcule la distance d'un point à la ligne du rayon"""
        # Utiliser les coordonnées actuelles du beam
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        line_length = math.sqrt(dx**2 + dy**2)
        
        if line_length == 0:
            return math.sqrt((px - self.start_x)**2 + (py - self.start_y)**2)
        
        # Normaliser la direction
        dir_x = dx / line_length
        dir_y = dy / line_length
        
        # Distance perpendiculaire à la ligne
        t = ((px - self.start_x) * dir_x + (py - self.start_y) * dir_y)
        
        # Point le plus proche sur la ligne
        closest_x = self.start_x + t * dir_x
        closest_y = self.start_y + t * dir_y
        
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    
    def project_point_on_line(self, px, py):
        """Projette un point sur la ligne et retourne la position normalisée (0-1)"""
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        line_length_sq = dx**2 + dy**2
        
        if line_length_sq == 0:
            return 0
        
        t = ((px - self.start_x) * dx + (py - self.start_y) * dy) / line_length_sq
        return max(0, min(1, t))
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine le rayon laser avec effet de lueur"""
        if self.current_life <= 0:
            return
        
        # Intensité basée sur la durée de vie restante
        intensity = self.current_life / self.duration
        
        # Couleurs du laser (rouge/orange)
        core_color = tuple(int(c * intensity) for c in (255, 100, 100))  # Rouge/orange
        glow_color = tuple(int(c * intensity * 0.6) for c in (255, 200, 150))  # Lueur plus douce
        
        # Points ajustés pour la caméra (utiliser les coordonnées actuelles)
        start_point = (int(self.start_x - camera_x), int(self.start_y - camera_y))
        end_point = (int(self.end_x - camera_x), int(self.end_y - camera_y))
        
        # Dessiner la lueur (plus large)
        if self.width > 2:
            pygame.draw.line(screen, glow_color, start_point, end_point, int(self.width))
        
        # Dessiner le cœur du laser (plus fin)
        core_width = max(2, int(self.width * 0.4))
        pygame.draw.line(screen, core_color, start_point, end_point, core_width)
        
        # Point lumineux au départ
        pygame.draw.circle(screen, core_color, start_point, max(2, int(self.width * 0.3)))

class DeathEffect:
    """Effet spécial pour la mort des ennemis spéciaux"""
    
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.config = config
        
        # Paramètres de l'animation
        self.life_time = 0
        self.fade_in_duration = 6  # 0.1s à 60 FPS
        self.display_duration = 30  # 0.5s à 60 FPS
        self.fade_out_duration = 30  # 0.5s à 60 FPS
        self.total_duration = self.fade_in_duration + self.display_duration + self.fade_out_duration
        self.rise_distance = 200  # pixels à monter
        
        # État de l'animation
        self.alpha = 0
        self.is_finished = False
        
        # Charger le sprite mort.png
        try:
            self.sprite = pygame.image.load("assets/enemy/mort.png").convert_alpha()
            # Redimensionner le sprite (par exemple à la taille d'un ennemi spécial)
            sprite_size = config.ENEMY_SIZE * 2  # Taille d'un ennemi spécial
            if config.SPRITE_SMOOTHING:
                self.sprite = pygame.transform.smoothscale(self.sprite, (sprite_size, sprite_size))
            else:
                self.sprite = pygame.transform.scale(self.sprite, (sprite_size, sprite_size))
            self.sprite = self.sprite.convert_alpha()
            self.has_sprite = True
        except (pygame.error, FileNotFoundError):
            print("Sprite assets/enemy/mort.png non trouvé, utilisation d'un effet par défaut")
            self.sprite = None
            self.has_sprite = False
    
    def update(self):
        """Met à jour l'animation de l'effet de mort"""
        self.life_time += 1
        
        # Calculer la position Y (mouvement vers le haut)
        progress = min(self.life_time / self.total_duration, 1.0)
        self.y = self.start_y - (self.rise_distance * progress)
        
        # Calculer l'alpha selon la phase
        if self.life_time <= self.fade_in_duration:
            # Phase fade in
            self.alpha = int(255 * (self.life_time / self.fade_in_duration))
        elif self.life_time <= self.fade_in_duration + self.display_duration:
            # Phase d'affichage complet
            self.alpha = 255
        elif self.life_time <= self.total_duration:
            # Phase fade out
            fade_out_progress = (self.life_time - self.fade_in_duration - self.display_duration) / self.fade_out_duration
            self.alpha = int(255 * (1.0 - fade_out_progress))
        else:
            # Animation terminée
            self.alpha = 0
            self.is_finished = True
        
        # S'assurer que l'alpha reste dans les limites
        self.alpha = max(0, min(255, self.alpha))
    
    def draw(self, screen, camera_x, camera_y):
        """Dessine l'effet de mort avec l'offset de caméra"""
        if self.is_finished or self.alpha <= 0:
            return
        
        # Position à l'écran avec offset de caméra
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if self.has_sprite:
            # Créer une copie du sprite avec l'alpha approprié
            sprite_with_alpha = self.sprite.copy()
            sprite_with_alpha.set_alpha(self.alpha)
            
            # Centrer le sprite
            sprite_rect = sprite_with_alpha.get_rect()
            sprite_rect.center = (screen_x, screen_y)
            
            screen.blit(sprite_with_alpha, sprite_rect)
        else:
            # Effet par défaut si le sprite n'est pas disponible
            # Cercle rouge qui disparaît
            radius = max(10, 30 - int(20 * (self.life_time / self.total_duration)))
            color = (255, 0, 0, self.alpha)  # Rouge avec alpha
            
            # Créer une surface temporaire pour l'alpha
            temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (radius, radius), radius)
            screen.blit(temp_surface, (screen_x - radius, screen_y - radius))


class Collectible:
    """Classe de base pour les objets collectibles"""
    
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        self.is_collected = False
        self.attraction_started = False
        self.vel_x = 0
        self.vel_y = 0
    
    def update(self, player_x, player_y):
        """Met à jour l'objet collectible (attraction vers le joueur)"""
        # Calculer la distance au joueur
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Si le joueur est assez proche, attirer l'objet
        if distance <= self.config.COLLECTIBLE_PICKUP_DISTANCE:
            if not self.attraction_started:
                self.attraction_started = True
            
            # Calculer la direction vers le joueur
            if distance > 5:  # Éviter la division par zéro
                direction_x = dx / distance
                direction_y = dy / distance
                
                # Appliquer la vitesse d'attraction
                self.vel_x = direction_x * self.config.COLLECTIBLE_ATTRACTION_SPEED
                self.vel_y = direction_y * self.config.COLLECTIBLE_ATTRACTION_SPEED
                
                # Mettre à jour la position
                self.x += self.vel_x
                self.y += self.vel_y
            else:
                # Collecté ! 
                self.is_collected = True
    
    def draw(self, screen, camera_x, camera_y):
        """Dessine l'objet collectible (à redéfinir dans les sous-classes)"""
        pass
    
    def on_collect(self, player):
        """Effet appliqué au joueur lors de la collecte (à redéfinir dans les sous-classes)"""
        pass


class Heart(Collectible):
    """Objet collectible coeur qui restaure la vie"""
    
    def __init__(self, x, y, config):
        super().__init__(x, y, config)
        self.size = 24  # Taille du coeur
        self.pulse_timer = 0
        self.pulse_scale = 1.0
        
        # Charger le sprite du coeur
        try:
            self.image = pygame.image.load("assets/drops/heart.png").convert_alpha()
            # Redimensionner le coeur
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.has_image = True
        except (pygame.error, FileNotFoundError):
            print("Image assets/drops/heart.png non trouvée, utilisation du rendu par défaut")
            self.has_image = False
    
    def update(self, player_x, player_y):
        """Met à jour le coeur avec animation de pulsation"""
        super().update(player_x, player_y)
        
        # Animation de pulsation
        self.pulse_timer += 1
        self.pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_timer * 0.1)
    
    def draw(self, screen, camera_x, camera_y):
        """Dessine le coeur avec l'offset de caméra"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        if self.has_image:
            # Appliquer l'effet de pulsation
            scaled_size = int(self.size * self.pulse_scale)
            scaled_image = pygame.transform.scale(self.image, (scaled_size, scaled_size))
            
            # Centrer l'image
            image_rect = scaled_image.get_rect()
            image_rect.center = (screen_x, screen_y)
            screen.blit(scaled_image, image_rect)
        else:
            # Rendu par défaut : coeur rouge
            scaled_size = int(self.size * self.pulse_scale)
            pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), scaled_size // 2)
            pygame.draw.circle(screen, (255, 100, 100), (screen_x, screen_y), scaled_size // 4)
    
    def on_collect(self, player):
        """Restaure la vie du joueur"""
        old_health = player.health
        player.health = min(player.max_health, player.health + self.config.HEART_HEAL_AMOUNT)
        healed = player.health - old_health
        if healed > 0:
            print(f"💚 Coeur collecté ! +{healed} points de vie (vie: {player.health}/{player.max_health})")
        else:
            print(f"💚 Coeur collecté mais vie déjà au maximum ({player.health}/{player.max_health})")
