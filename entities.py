"""
Classes du joueur et des entités du jeu
"""

import pygame
import pygame.gfxdraw  # Pour l'antialiasing
import pygame.surfarray  # Pour l'accès aux pixels
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
        
        # Animation - paramètres par défaut (seront ajustés selon le type de sprite)
        self.animation_frames = []  # Liste des frames d'animation
        self.animation_frames_left = []  # Frames pour la direction gauche
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_sequence = []  # Sera défini selon le type de sprite
        self.sequence_index = 0
        
        # Obtenir le type de sprite depuis la config (défaut : 1)
        sprite_type = getattr(config, 'PLAYER_SPRITE_TYPE', 1)
        
        # Charger la spritesheet selon le type
        self._load_player_sprite(sprite_type)
        
        # Ajuster la vitesse d'animation selon le nombre de frames
        # Pour une durée d'animation totale similaire, calculer le délai entre frames
        if len(self.frame_sequence) > 0:
            # Viser environ 1 seconde pour un cycle complet d'animation à 60 FPS
            total_animation_duration = 60  # frames (1 seconde à 60 FPS)
            self.animation_delay = max(1, total_animation_duration // len(self.frame_sequence))
        else:
            self.animation_delay = 9  # Valeur par défaut
    def _load_player_sprite(self, sprite_type):
        """Charge la spritesheet du joueur selon le type spécifié"""
        try:
            if sprite_type == 1:
                # Type 1 : player2.png (5 frames, séquence 5-4-3-2-1)
                spritesheet = pygame.image.load("assets/player/player2.png").convert_alpha()
                num_frames = 5
                self.frame_sequence = [4, 3, 2, 1, 0]  # Séquence 5-4-3-2-1 en boucle
                print(f"Chargement sprite type 1 : player2.png (5 frames, séquence 5-4-3-2-1)")
                
            elif sprite_type == 2:
                # Type 2 : player3.png (9 frames, séquence 1-2-3-4-5-6-7-8-9)
                spritesheet = pygame.image.load("assets/player/player3.png").convert_alpha()
                num_frames = 9
                self.frame_sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # Séquence 1-2-3-4-5-6-7-8-9 en boucle
                print(f"Chargement sprite type 2 : player3.png (9 frames, séquence 1-2-3-4-5-6-7-8-9)")
                
            elif sprite_type == 3:
                # Type 3 : player4.png (5 frames, animation ping-pong 1-2-3-4-5-4-3-2-1)
                spritesheet = pygame.image.load("assets/player/player4.png").convert_alpha()
                num_frames = 5
                self.frame_sequence = [0, 1, 2, 3, 4, 3, 2, 1]  # Séquence ping-pong 1-2-3-4-5-4-3-2-1 en boucle
                print(f"Chargement sprite type 3 : player4.png (5 frames, séquence ping-pong 1-2-3-4-5-4-3-2-1)")
                
            else:
                print(f"Type de sprite non supporté : {sprite_type}, utilisation du type 1 par défaut")
                return self._load_player_sprite(1)
            
            # Dimensions des sprites individuels
            sprite_width = spritesheet.get_width() // num_frames  # Frames horizontalement
            sprite_height = spritesheet.get_height()
            
            sprite_size = self.size * 4  # Facteur d'échelle x4 pour une meilleure visibilité
            
            # Extraire tous les sprites
            for i in range(num_frames):
                # Extraire le sprite à la position (i * sprite_width, 0)
                frame_rect = pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height)
                frame = spritesheet.subsurface(frame_rect).copy()
                
                # Redimensionner le sprite avec antialiasing si activé
                if self.config.SPRITE_SMOOTHING:
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
            # Calculer la vitesse d'animation pour ce type de sprite
            total_animation_duration = 60  # frames (1 seconde à 60 FPS)
            animation_delay = max(1, total_animation_duration // num_frames)
            animation_fps = 60.0 / animation_delay
            print(f"Animation spritesheet du joueur activée ({num_frames} frames, ~{animation_fps:.1f} FPS d'animation)")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"Spritesheet du joueur non trouvée : {e}")
            print("Utilisation du rendu par défaut")
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
            
            # Changer de frame selon le délai calculé pour ce type de sprite
            if self.animation_timer >= self.animation_delay:
                self.animation_timer = 0
                self.sequence_index = (self.sequence_index + 1) % len(self.frame_sequence)
                self.current_frame = self.frame_sequence[self.sequence_index]
    
    def take_damage(self, damage, skill_manager=None):
        """Fait subir des dégâts au joueur en tenant compte du bouclier"""
        original_damage = damage
        
        # Vérifier si le joueur a des points de bouclier (compétence Bouclier)
        if hasattr(self, 'shield_points') and self.shield_points > 0:
            if damage <= self.shield_points:
                # Le bouclier absorbe tous les dégâts
                self.shield_points -= damage
                print(f"🛡️ Bouclier absorbe {damage} dégâts (reste: {self.shield_points})")
                damage = 0
            else:
                # Le bouclier absorbe une partie des dégâts
                absorbed = self.shield_points
                damage -= self.shield_points
                self.shield_points = 0
                print(f"🛡️ Bouclier absorbe {absorbed} dégâts, {damage} dégâts restants")
        
        # Appliquer les dégâts restants à la vie
        if damage > 0:
            self.health = max(0, self.health - damage)
        
        # Notifier les compétences qu'un dégât a été pris (seulement si on a vraiment pris des dégâts)
        if (original_damage > 0 and skill_manager and 
            hasattr(skill_manager, 'notify_damage_taken')):
            skill_manager.notify_damage_taken()
    
    def draw(self, screen, shield_hits=0):
        """Dessine le joueur avec l'animation de spritesheet et l'effet de bouclier"""
        
        # === EFFET DE BOUCLIER TEMPORAIRE ===
        if shield_hits > 0:
            center_x = int(self.x + self.size//2)
            center_y = int(self.y + self.size//2)
            shield_radius = int(self.size * 0.8)  # Rayon plus grand que le joueur
            
            # Couleur bleue pour le bouclier avec transparence
            shield_color = (100, 150, 255)  # Bleu clair
            shield_border_color = (50, 100, 255)  # Bleu plus foncé pour le contour
            
            # Dessiner le cercle de bouclier avec effet de pulsation
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
        
        # === EFFET DE BOUCLIER DE LA COMPÉTENCE ===
        if hasattr(self, 'shield_points') and self.shield_points > 0:
            center_x = int(self.x + self.size//2)
            center_y = int(self.y + self.size//2)
            shield_radius = int(self.size * 0.6)  # Plus petit que le bouclier temporaire
            
            # Couleur dorée/orange pour le bouclier de compétence
            shield_opacity = min(255, int(255 * (self.shield_points / getattr(self, 'max_shield_points', 100))))
            shield_color = (255, 215, 0, shield_opacity)  # Doré avec transparence
            shield_border_color = (255, 165, 0)  # Orange pour le contour
            
            # Dessiner le bouclier de compétence
            if self.config.ENABLE_ANTIALIASING:
                pygame.gfxdraw.aacircle(screen, center_x, center_y, shield_radius, shield_border_color)
            else:
                pygame.draw.circle(screen, shield_border_color, (center_x, center_y), shield_radius, 1)
        
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
            # Mode test : forcer des ennemis tireurs si configuré
            if hasattr(config, 'FORCE_SHOOTER_ENEMIES') and config.FORCE_SHOOTER_ENEMIES:
                self.sprite_id = config.SHOOTER_ENEMY_SPRITE_ID
            else:
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
        
        # Type de mort pour les effets spéciaux
        self.death_type = None  # "lightning", "orb", "beam", ou None pour explosion normale
        self.death_data = {}  # Données supplémentaires pour l'effet de mort
        
        # Animation de rotation (ping-pong de -5° à +5° accéléré)
        self.rotation_angle = 0
        self.rotation_time = 0
        self.rotation_speed = 5  # Vitesse de rotation accélérée (20 au lieu de 10)
        
        # Composante aléatoire pour l'IA
        self.random_offset_x = 0
        self.random_offset_y = 0
        self.random_timer = 0
        
        # Attributs spécifiques au tireur (ennemi 14)
        self.is_shooter = (self.sprite_id == config.SHOOTER_ENEMY_SPRITE_ID)
        self.fire_timer = 0
        self.is_stationary = False  # L'ennemi tireur devient stationnaire quand il est proche
    
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
        
        # Comportement spécial pour l'ennemi tireur (sprite 14)
        if self.is_shooter:
            # Gestion du timer de tir
            self.fire_timer += 1
            
            # L'ennemi s'arrête quand il atteint la distance de tir
            if distance <= self.config.SHOOTER_ENEMY_STOP_DISTANCE:
                self.is_stationary = True
            else:
                self.is_stationary = False
            
            # Si l'ennemi n'est pas encore à distance de tir, il se rapproche
            if not self.is_stationary and distance > 0:
                # Normaliser et ajouter composante aléatoire
                dx = (dx / distance) + self.random_offset_x
                dy = (dy / distance) + self.random_offset_y
                # Normalisation pour vitesse constante
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    dx = dx / norm
                    dy = dy / norm
                # Appliquer le facteur de correction
                corrected_speed = self.speed * self.config.ENEMY_SPEED_CORRECTION_FACTOR
                # Déplacer l'ennemi
                self.x += dx * corrected_speed
                self.y += dy * corrected_speed
        else:
            # Comportement normal pour les autres ennemis
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
    
    def should_fire(self):
        """Vérifie si l'ennemi tireur doit tirer un projectile"""
        if not self.is_shooter or not self.is_stationary:
            return False
        
        # Tirer selon la fréquence configurée
        if self.fire_timer >= self.config.SHOOTER_ENEMY_FIRE_RATE:
            self.fire_timer = 0
            return True
        return False
    
    def take_damage(self, damage):
        """Fait subir des dégâts à l'ennemi"""
        self.health = max(0, self.health - damage)
    
    def set_death_type(self, death_type, **death_data):
        """Définit le type de mort et les données associées"""
        self.death_type = death_type
        self.death_data = death_data
    
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


class CanonProjectile:
    """Classe des projectiles du canon"""
    
    def __init__(self, x, y, dx, dy, config):
        self.x = x
        self.y = y
        self.config = config
        self.size = 6  # Taille du projectile
        self.speed = 8.0  # Vitesse du projectile
        self.damage = 25  # Dégâts de base (sera surchargé par l'arme)
        
        # Direction normalisée
        self.dx = dx
        self.dy = dy
    
    def update(self):
        """Met à jour la position du projectile"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
    
    def draw(self, screen):
        """Dessine le projectile du canon"""
        # Ligne principale (trait d'énergie)
        end_x = self.x + self.dx * 20
        end_y = self.y + self.dy * 20
        
        pygame.draw.line(screen, self.config.YELLOW,
                        (int(self.x), int(self.y)),
                        (int(end_x), int(end_y)), 2)
        
        # Point lumineux au centre
        pygame.draw.circle(screen, self.config.WHITE,
                         (int(self.x), int(self.y)), self.size)


class EnemyProjectile:
    """Classe des projectiles d'ennemis"""
    
    def __init__(self, x, y, target_x, target_y, config):
        self.x = x
        self.y = y
        self.config = config
        self.size = 6  # Taille du projectile
        self.speed = config.SHOOTER_ENEMY_PROJECTILE_SPEED
        self.damage = config.SHOOTER_ENEMY_PROJECTILE_DAMAGE
        
        # Calculer la direction vers la cible
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.dx = dx / distance
            self.dy = dy / distance
        else:
            self.dx = 0
            self.dy = 0
    
    def update(self):
        """Met à jour la position du projectile"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine le projectile ennemi"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Projectile rouge avec contour noir
        pygame.draw.circle(screen, (255, 100, 100), (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (100, 0, 0), (screen_x, screen_y), self.size, 2)


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
    Classe pour les rayons laser néon bleus persistants avec rotation continue
    
    NOUVEAU COMPORTEMENT:
    - Vise l'ennemi le plus proche au moment de la création
    - Rotation continue sans limite de durée
    - Effet visuel néon bleu avec halo transparent
    - Plusieurs beams selon le niveau (1, 2 ou 3 beams)
    """
    
    # Surface statique partagée pour les halos (optimisation performance)
    _halo_surface = None
    _screen_size = None
    
    @classmethod
    def _get_halo_surface(cls, screen):
        """Obtient la surface de halo statique, la crée si nécessaire"""
        current_size = (screen.get_width(), screen.get_height())
        if cls._halo_surface is None or cls._screen_size != current_size:
            cls._halo_surface = pygame.Surface(current_size, pygame.SRCALPHA)
            cls._screen_size = current_size
        return cls._halo_surface
    
    def __init__(self, start_x, start_y, direction_x, direction_y, config, level, player=None, beam_index=0, total_beams=1):
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
        self.rotation_speed_deg_per_sec = get_weapon_stat("Beam", "speed", level)
        
        # Gestion des beams multiples
        self.beam_index = beam_index
        self.total_beams = total_beams
        
        # Angle initial arbitraire + décalage pour les beams multiples
        base_angle = math.atan2(direction_y, direction_x)
        if total_beams == 1:
            self.initial_angle = base_angle
        elif total_beams == 2:
            # 2 beams : opposés à 180°
            angle_offset = beam_index * math.pi  # 0° et 180°
            self.initial_angle = base_angle + angle_offset
        elif total_beams == 3:
            # 3 beams : espacés de 120°
            angle_offset = beam_index * (2 * math.pi / 3)  # 0°, 120°, 240°
            self.initial_angle = base_angle + angle_offset
        
        self.current_angle = self.initial_angle
        
        # Calcul des points actuels du beam
        self.start_x = self.center_x
        self.start_y = self.center_y
        self.end_x = self.center_x + math.cos(self.current_angle) * self.range
        self.end_y = self.center_y + math.sin(self.current_angle) * self.range
        
        # Timer pour les dégâts continus (toutes les 10 frames = ~6 dégâts par seconde)
        self.damage_timer = 0
        self.damage_interval = 10  # Appliquer les dégâts toutes les 10 frames
        
        # Timer pour la génération continue de particules
        self.particle_timer = 0
    
    def update(self):
        """Met à jour le faisceau avec rotation continue et persistance - OPTIMISÉ"""
        self.particle_timer += 1  # Incrémenter le timer des particules
        self.damage_timer += 1  # Incrémenter le timer des dégâts
        
        # Mettre à jour la position du centre avec le joueur
        if self.player:
            player_center_x = self.player.x + self.player.size // 2
            player_center_y = self.player.y + self.player.size // 2
            
            # OPTIMISATION : Ne recalculer que si la position a changé
            if (self.center_x != player_center_x) or (self.center_y != player_center_y):
                self.center_x = player_center_x
                self.center_y = player_center_y
                # Invalider le cache de beam si la position change
                if hasattr(self, '_cached_beam_data'):
                    delattr(self, '_cached_beam_data')
        
        # OPTIMISATION : Calcul trigonométrique plus efficace
        # Convertir la vitesse en radians par frame (60 FPS)
        rotation_speed_rad_per_frame = math.radians(self.rotation_speed_deg_per_sec) / 60.0
        
        # Incrémenter l'angle de rotation
        self.current_angle += rotation_speed_rad_per_frame
        
        # OPTIMISATION : Précalculer cos et sin une seule fois
        cos_angle = math.cos(self.current_angle)
        sin_angle = math.sin(self.current_angle)
        
        # Recalculer les points du beam
        self.start_x = self.center_x
        self.start_y = self.center_y
        self.end_x = self.center_x + cos_angle * self.range
        self.end_y = self.center_y + sin_angle * self.range
        
        # OPTIMISATION : Invalider le cache de calculs géométriques
        if hasattr(self, '_cached_beam_data'):
            delattr(self, '_cached_beam_data')
        
        # Le beam est maintenant persistant (toujours actif)
        return True
    
    def check_collision_with_enemies(self, enemies, game=None):
        """Vérifie les collisions avec les ennemis et applique les dégâts continus - OPTIMISÉ"""
        hit_positions = []
        continuous_hits = []  # Pour les particules continues
        
        # OPTIMISATION : Précalculer une seule fois la direction du beam
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        beam_length = math.sqrt(dx**2 + dy**2)
        if beam_length > 0:
            current_direction_x = dx / beam_length
            current_direction_y = dy / beam_length
        else:
            current_direction_x, current_direction_y = 1, 0
        
        # OPTIMISATION : Early exit si pas d'ennemis
        if not enemies:
            return hit_positions
        
        # OPTIMISATION : Cache des rayons d'ennemi pour éviter les recalculs
        beam_radius = self.width / 2
        
        for enemy in enemies:
            # OPTIMISATION : Early exit avec distance approximative rapide
            enemy_center_x = enemy.x + enemy.size // 2
            enemy_center_y = enemy.y + enemy.size // 2
            
            # Distance rapide au centre du beam (approximation)
            beam_center_x = (self.start_x + self.end_x) / 2
            beam_center_y = (self.start_y + self.end_y) / 2
            quick_distance = abs(enemy_center_x - beam_center_x) + abs(enemy_center_y - beam_center_y)
            
            # Si trop loin, skip la collision précise (économise 70% des calculs)
            max_possible_distance = beam_length / 2 + enemy.size + self.width
            if quick_distance > max_possible_distance:
                continue
            
            # Vérification précise seulement si nécessaire
            if self.line_intersects_rect_optimized(enemy, enemy_center_x, enemy_center_y):
                # Calculer le point d'impact pour les particules
                impact_x = enemy_center_x
                impact_y = enemy_center_y
                
                # OPTIMISATION : Réduire la fréquence des particules (÷4)
                if game and self.particle_timer % 16 == 0:  # Toutes les 16 frames au lieu de 4
                    game.create_welding_particles(impact_x, impact_y, 
                                                 current_direction_x, 
                                                 current_direction_y)
                
                # Appliquer les dégâts continus à intervalles réguliers
                if self.damage_timer % self.damage_interval == 0:
                    enemy_was_alive = enemy.health > 0
                    enemy.take_damage(self.damage)
                    
                    # Si l'ennemi est éliminé, créer une explosion renforcée et l'effet de désintégration
                    if enemy_was_alive and enemy.health <= 0 and game:
                        game.create_beam_explosion_particles(impact_x, impact_y)
                        # Créer l'effet de désintégration en cendres
                        beam_death_effect = BeamDeathEffect(enemy, self.config)
                        game.beam_death_effects.append(beam_death_effect)
                
                hit_positions.append((impact_x, impact_y))
                continuous_hits.append((impact_x, impact_y))
        
        return hit_positions
    
    def line_intersects_rect_optimized(self, enemy, enemy_center_x, enemy_center_y):
        """Version optimisée de la détection de collision (réutilise les coordonnées précalculées)"""
        enemy_radius = enemy.size // 2  # Rayon = largeur du sprite / 2
        
        # Distance du centre de l'ennemi à la ligne du laser
        distance_to_line = self.point_to_line_distance_optimized(enemy_center_x, enemy_center_y)
        
        # Vérifier si le cercle intersecte avec la ligne
        if distance_to_line <= enemy_radius + self.width / 2:
            # Vérifier que le point est dans la portée du rayon
            proj = self.project_point_on_line_optimized(enemy_center_x, enemy_center_y)
            if 0 <= proj <= 1:  # Le point projeté est sur le segment
                return True
        
        return False
    
    def line_intersects_rect(self, enemy):
        """Vérifie si le rayon laser intersecte avec un cercle (ennemi) - VERSION LEGACY"""
        # Centre du cercle de l'ennemi
        enemy_center_x = enemy.x + enemy.size // 2
        enemy_center_y = enemy.y + enemy.size // 2
        return self.line_intersects_rect_optimized(enemy, enemy_center_x, enemy_center_y)
    
    def point_to_line_distance_optimized(self, px, py):
        """Version optimisée du calcul de distance - cache les calculs répétitifs"""
        # Cache les coordonnées du beam si elles n'ont pas changé
        if not hasattr(self, '_cached_beam_data') or self._cached_beam_data[0] != (self.start_x, self.start_y, self.end_x, self.end_y):
            dx = self.end_x - self.start_x
            dy = self.end_y - self.start_y
            self._cached_line_length = math.sqrt(dx**2 + dy**2)
            if self._cached_line_length > 0:
                self._cached_dir_x = dx / self._cached_line_length
                self._cached_dir_y = dy / self._cached_line_length
            else:
                self._cached_dir_x = self._cached_dir_y = 0
            self._cached_beam_data = (self.start_x, self.start_y, self.end_x, self.end_y)
        
        if self._cached_line_length == 0:
            return math.sqrt((px - self.start_x)**2 + (py - self.start_y)**2)
        
        # Distance perpendiculaire à la ligne
        t = ((px - self.start_x) * self._cached_dir_x + (py - self.start_y) * self._cached_dir_y)
        
        # Point le plus proche sur la ligne
        closest_x = self.start_x + t * self._cached_dir_x
        closest_y = self.start_y + t * self._cached_dir_y
        
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    
    def project_point_on_line_optimized(self, px, py):
        """Version optimisée de la projection - réutilise les données cachées"""
        if not hasattr(self, '_cached_beam_data'):
            # Forcer le calcul du cache
            self.point_to_line_distance_optimized(px, py)
        
        if self._cached_line_length == 0:
            return 0
        
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        line_length_sq = dx**2 + dy**2
        
        t = ((px - self.start_x) * dx + (py - self.start_y) * dy) / line_length_sq
        return max(0, min(1, t))
    
    def point_to_line_distance(self, px, py):
        """Calcule la distance d'un point à la ligne du rayon - VERSION LEGACY"""
        return self.point_to_line_distance_optimized(px, py)
    
    def project_point_on_line(self, px, py):
        """Projette un point sur la ligne et retourne la position normalisée (0-1) - VERSION LEGACY"""
        return self.project_point_on_line_optimized(px, py)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine le rayon laser avec effet néon bleu optimisé"""
        # Intensité constante pour l'effet néon persistant
        intensity = 1.0
        
        # Couleurs néon bleues avec effet de halo
        halo_color = (0, 50, 150, int(80 * intensity))     # Bleu foncé transparent pour le halo
        edge_color = tuple(int(c * intensity) for c in (100, 200, 255))  # Bleu clair pour les bords
        core_color = tuple(int(c * intensity) for c in (255, 255, 255))  # Blanc pur pour le centre
        
        # Points ajustés pour la caméra (utiliser les coordonnées actuelles)
        start_point = (int(self.start_x - camera_x), int(self.start_y - camera_y))
        end_point = (int(self.end_x - camera_x), int(self.end_y - camera_y))
        
        # Utiliser la surface statique pour l'effet de halo (OPTIMISATION MAJEURE)
        halo_surface = self._get_halo_surface(screen)
        halo_surface.fill((0, 0, 0, 0))  # Effacer le contenu précédent
        halo_width = int(self.width + 8)
        if halo_width > 0:
            pygame.draw.line(halo_surface, halo_color, start_point, end_point, halo_width)
            screen.blit(halo_surface, (0, 0))
        
        # Dessiner la couche périphérique (bleu clair)
        if self.width > 2:
            pygame.draw.line(screen, edge_color, start_point, end_point, int(self.width))
        
        # Dessiner le cœur du laser (blanc, plus fin)
        core_width = max(2, int(self.width * 0.5))
        pygame.draw.line(screen, core_color, start_point, end_point, core_width)
        
        # Point lumineux au départ (effet néon)
        pygame.draw.circle(screen, core_color, start_point, max(3, int(self.width * 0.4)))
        pygame.draw.circle(screen, edge_color, start_point, max(5, int(self.width * 0.6)))

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
    
    def on_collect(self, player, game=None):
        """Restaure la vie du joueur"""
        old_health = player.health
        player.health = min(player.max_health, player.health + self.config.HEART_HEAL_AMOUNT)
        healed = player.health - old_health
        if healed > 0:
            print(f"💚 Coeur collecté ! +{healed} points de vie (vie: {player.health}/{player.max_health})")
        else:
            print(f"💚 Coeur collecté mais vie déjà au maximum ({player.health}/{player.max_health})")


class Coin(Collectible):
    """Objet collectible pièce animée qui donne des points/monnaie"""
    
    def __init__(self, x, y, config, throw_direction=None):
        super().__init__(x, y, config)
        self.size = 32  # Taille de la pièce
        self.animation_timer = 0
        self.current_frame = 0
        self.frames_per_sprite = config.COIN_ANIMATION_SPEED  # Utiliser la config
        self.sprite_frames = []
        
        # Système de trajectoire de "jet"
        self.is_being_thrown = True  # Indique si la pièce est en cours de jet
        self.throw_timer = 0
        self.throw_duration = config.COIN_THROW_DURATION  # Utiliser la config
        self.throw_friction = config.COIN_THROW_FRICTION  # Utiliser la config
        
        # Vitesse initiale de jet dans une direction aléatoire
        if throw_direction:
            # Direction spécifique fournie
            self.throw_vel_x = throw_direction[0]
            self.throw_vel_y = throw_direction[1]
        else:
            # Direction aléatoire
            import math
            import random
            angle = random.uniform(0, 2 * math.pi)
            throw_speed = random.uniform(config.COIN_THROW_SPEED_MIN, config.COIN_THROW_SPEED_MAX)
            self.throw_vel_x = math.cos(angle) * throw_speed
            self.throw_vel_y = math.sin(angle) * throw_speed
        
        # Charger les sprites de la pièce animée
        try:
            # Charger l'image complète
            full_image = pygame.image.load("assets/drops/coin.png").convert_alpha()
            image_width = full_image.get_width()
            image_height = full_image.get_height()
            
            # Calculer la taille de chaque frame (6 sprites horizontaux)
            frame_width = image_width // 6
            frame_height = image_height
            
            # Extraire chaque frame
            for i in range(6):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(full_image, (0, 0), frame_rect)
                
                # Redimensionner la frame à la taille désirée
                scaled_frame = pygame.transform.scale(frame_surface, (self.size, self.size))
                self.sprite_frames.append(scaled_frame)
            
            self.has_animation = True
            print(f"🪙 Animation de pièce chargée : {len(self.sprite_frames)} frames")
            
        except (pygame.error, FileNotFoundError):
            print("Image assets/drops/coin.png non trouvée, utilisation du rendu par défaut")
            self.has_animation = False
    
    def update(self, player_x, player_y):
        """Met à jour la pièce avec animation de rotation et trajectoire de jet"""
        # Gestion de la trajectoire de jet
        if self.is_being_thrown:
            self.throw_timer += 1
            
            # Appliquer la vitesse de jet
            self.x += self.throw_vel_x
            self.y += self.throw_vel_y
            
            # Appliquer la friction
            self.throw_vel_x *= self.throw_friction
            self.throw_vel_y *= self.throw_friction
            
            # Arrêter le jet après la durée définie
            if self.throw_timer >= self.throw_duration:
                self.is_being_thrown = False
                self.throw_vel_x = 0
                self.throw_vel_y = 0
        else:
            # Comportement normal de collectible (attraction magnétique, etc.)
            super().update(player_x, player_y)
        
        # Animation des sprites (toujours active)
        if self.has_animation:
            self.animation_timer += 1
            if self.animation_timer >= self.frames_per_sprite:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
    
    def draw(self, screen, camera_x, camera_y):
        """Dessine la pièce animée avec l'offset de caméra"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        if self.has_animation and self.sprite_frames:
            # Dessiner la frame actuelle
            current_sprite = self.sprite_frames[self.current_frame]
            image_rect = current_sprite.get_rect()
            image_rect.center = (screen_x, screen_y)
            screen.blit(current_sprite, image_rect)
        else:
            # Rendu par défaut : cercle doré
            pygame.draw.circle(screen, (255, 215, 0), (screen_x, screen_y), self.size // 2)
            pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), self.size // 3)
            pygame.draw.circle(screen, (255, 215, 0), (screen_x, screen_y), self.size // 6)
    
    def on_collect(self, player, game=None):
        """Donne des points/monnaie au joueur et met à jour la progression"""
        # Utiliser la valeur de la config
        if game:
            game.score += self.config.COIN_VALUE
            game.coins_collected += 1  # Incrémenter les pièces collectées
            print(f"🪙 Pièce collectée ! +{self.config.COIN_VALUE} points (Score total: {game.score})")
            
            # Vérifier la progression du niveau
            game.check_level_progression()
        else:
            print(f"🪙 Pièce collectée ! +{self.config.COIN_VALUE} points")


class OrbDeathEffect:
    """Effet de mort par orbe : repousse et fade rouge"""
    
    def __init__(self, enemy, orb_direction_x, orb_direction_y, config):
        self.config = config
        self.original_x = enemy.x
        self.original_y = enemy.y
        self.size = enemy.size
        self.sprite = enemy.sprite
        
        # Direction de repousse (normalisée)
        magnitude = math.sqrt(orb_direction_x**2 + orb_direction_y**2)
        if magnitude > 0:
            self.push_x = (orb_direction_x / magnitude) * config.ORB_DEATH_PUSHBACK_DISTANCE
            self.push_y = (orb_direction_y / magnitude) * config.ORB_DEATH_PUSHBACK_DISTANCE
        else:
            self.push_x = 0
            self.push_y = 0
        
        # Position finale après repousse
        self.target_x = self.original_x + self.push_x
        self.target_y = self.original_y + self.push_y
        
        # État de l'animation
        self.current_life = config.ORB_DEATH_FADE_DURATION
        self.max_life = config.ORB_DEATH_FADE_DURATION
        
        # Position actuelle
        self.x = self.original_x
        self.y = self.original_y
    
    def update(self):
        """Met à jour l'effet de mort"""
        self.current_life -= 1
        
        # Progression de l'animation (0.0 à 1.0)
        progress = 1.0 - (self.current_life / self.max_life)
        
        # Interpolation de la position (repousse)
        self.x = self.original_x + self.push_x * progress
        self.y = self.original_y + self.push_y * progress
        
        return self.current_life > 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine l'effet de mort avec fade et teinte rouge"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Calcul de l'alpha pour le fade
        alpha = int(255 * (self.current_life / self.max_life))
        
        if self.sprite and self.config.SPRITE_SMOOTHING:
            # Créer une surface temporaire avec teinte rouge et fade
            temp_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            temp_surface.blit(self.sprite, (0, 0))
            
            # Appliquer la teinte rouge
            red_overlay = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            red_overlay.fill((*self.config.ORB_DEATH_COLOR_TINT, 128))  # 50% de rouge
            temp_surface.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
            
            # Appliquer l'alpha
            temp_surface.set_alpha(alpha)
            
            screen.blit(temp_surface, (screen_x, screen_y))
        else:
            # Rendu de fallback avec rectangle rouge qui fade
            rect_color = (*self.config.ORB_DEATH_COLOR_TINT, alpha)
            temp_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            temp_surface.fill(rect_color)
            screen.blit(temp_surface, (screen_x, screen_y))


class BeamDeathEffect:
    """Effet de mort par beam : désintégration en cendres du sprite réel"""
    
    def __init__(self, enemy, config):
        self.config = config
        self.x = enemy.x
        self.y = enemy.y
        self.size = enemy.size
        self.sprite = enemy.sprite
        
        # Générer les particules de cendres à partir des pixels du sprite
        self.ash_particles = []
        self._generate_ash_from_sprite()
    
    def _generate_ash_from_sprite(self):
        """Génère les particules de cendres à partir des pixels du sprite de l'ennemi"""
        if not self.sprite:
            return
        
        # Créer un masque noir du sprite
        sprite_rect = self.sprite.get_rect()
        
        # Échantillonner les pixels du sprite (pas tous pour éviter trop de particules)
        sample_rate = max(1, self.size // 16)  # Échantillonner 1 pixel sur N
        
        try:
            # Obtenir les données de pixels du sprite
            sprite_array = pygame.surfarray.array3d(self.sprite)
            
            for x in range(0, sprite_rect.width, sample_rate):
                for y in range(0, sprite_rect.height, sample_rate):
                    if x < sprite_array.shape[0] and y < sprite_array.shape[1]:
                        # Vérifier si le pixel n'est pas transparent
                        pixel_color = sprite_array[x, y]
                        # Si le pixel a une couleur (pas transparent), créer une particule de cendre
                        if not (pixel_color[0] == 0 and pixel_color[1] == 0 and pixel_color[2] == 0):
                            # Position absolue de la particule
                            world_x = self.x + (x * self.size) // sprite_rect.width
                            world_y = self.y + (y * self.size) // sprite_rect.height
                            
                            particle = {
                                'x': float(world_x),
                                'y': float(world_y),
                                'vel_x': random.uniform(-0.8, 0.8),  # Légère dérive horizontale
                                'vel_y': random.uniform(0.5, 2.0),   # Vitesse de chute variable
                                'size': random.randint(2, 4),        # Particules plus grosses pour meilleure visibilité
                                'life': random.randint(60, 120),     # Durée de vie variable
                                'max_life': 120,
                                'color': (40, 40, 40)  # Gris très foncé (cendres)
                            }
                            self.ash_particles.append(particle)
        except Exception:
            # Si l'extraction des pixels échoue, utiliser l'ancienne méthode
            self._generate_fallback_ash()
    
    def _generate_fallback_ash(self):
        """Méthode de secours si l'extraction des pixels échoue"""
        particle_count = self.config.BEAM_DEATH_ASH_COUNT
        
        for _ in range(particle_count):
            # Position aléatoire dans la zone de l'ennemi
            offset_x = random.uniform(-self.size/2, self.size/2)
            offset_y = random.uniform(-self.size/2, self.size/2)
            
            particle = {
                'x': self.x + self.size/2 + offset_x,
                'y': self.y + self.size/2 + offset_y,
                'vel_x': random.uniform(-0.5, 0.5),
                'vel_y': random.uniform(0.5, 2.0),
                'size': random.randint(3, 5),  # Particules plus grosses pour la méthode de secours
                'life': random.randint(60, 120),
                'max_life': 120,
                'color': (40, 40, 40)
            }
            self.ash_particles.append(particle)
    
    def update(self):
        """Met à jour les particules de cendres"""
        active_particles = []
        
        for particle in self.ash_particles:
            # Mise à jour de la position
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            # Gravité légère pour un effet réaliste
            particle['vel_y'] += 0.08
            
            # Diminuer la durée de vie
            particle['life'] -= 1
            
            # Garder seulement les particules vivantes
            if particle['life'] > 0:
                active_particles.append(particle)
        
        self.ash_particles = active_particles
        return len(self.ash_particles) > 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dessine les particules de cendres"""
        for particle in self.ash_particles:
            screen_x = int(particle['x'] - camera_x)
            screen_y = int(particle['y'] - camera_y)
            
            # Alpha basé sur la durée de vie restante pour effet de disparition
            alpha = int(255 * (particle['life'] / particle['max_life']))
            
            # Couleur des cendres avec transparence
            color = particle['color'] + (alpha,)
            
            # Dessiner la particule de cendre
            if alpha > 0 and particle['size'] > 0:
                try:
                    temp_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
                    temp_surface.fill(color)
                    screen.blit(temp_surface, (screen_x, screen_y))
                except Exception:
                    # Si le dessin échoue, utiliser un point simple
                    pygame.draw.rect(screen, particle['color'], 
                                   (screen_x, screen_y, particle['size'], particle['size']))
