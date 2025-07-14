"""
Classes du joueur et des entités du jeu
"""

import pygame
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
        
        # Animation
        self.animation_frames = []  # Liste des frames d'animation
        self.animation_frames_left = []  # Frames pour la direction gauche
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_sequence = [0, 1, 2, 1]  # Séquence 1-2-3-2
        self.sequence_index = 0
        
        # Charger la spritesheet Birds.png
        try:
            spritesheet = pygame.image.load("Birds.png").convert_alpha()
            
            # Dimensions des sprites individuels (64x64 pixels)
            sprite_width = 64
            sprite_height = 64
            
            sprite_size = self.size * 4  # Facteur d'échelle x2 supplémentaire pour une meilleure visibilité
            
            # Extraire les 3 premiers sprites (64x64 chacun)
            for i in range(3):
                # Extraire le sprite à la position (i * 64, 0)
                frame_rect = pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height)
                frame = spritesheet.subsurface(frame_rect).copy()
                
                # Redimensionner le sprite
                frame_scaled = pygame.transform.scale(frame, (sprite_size, sprite_size))
                self.animation_frames.append(frame_scaled)
                
                # Créer la version miroir pour la gauche
                frame_left = pygame.transform.flip(frame_scaled, True, False)
                self.animation_frames_left.append(frame_left)
            
            self.has_image = True
            print(f"✅ Animation spritesheet du joueur activée (3 frames, séquence 1-2-3-2)")
        except (pygame.error, FileNotFoundError):
            print("⚠️ Spritesheet Birds.png non trouvée, utilisation du rendu par défaut")
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
    
    def draw(self, screen):
        """Dessine le joueur avec l'animation de spritesheet"""
        if self.has_image and self.animation_frames and self.animation_frames_left:
            # Choisir la bonne liste de frames selon la direction
            current_frames = self.animation_frames_left if self.facing_direction == "right" else self.animation_frames
            
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
            pygame.draw.circle(screen, self.config.PLAYER_COLOR,
                             (int(self.x + self.size//2), int(self.y + self.size//2)),
                             self.size//2)
            
            # Contour blanc
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
    
    def __init__(self, x, y, config, is_special=False):
        self.x = x
        self.y = y
        self.config = config
        self.size = config.ENEMY_SIZE
        self.speed = config.ENEMY_SPEED
        
        # Ennemi spécial
        self.is_special = is_special
        if is_special:
            self.max_health = int(config.ENEMY_HEALTH * config.SPECIAL_ENEMY_HEALTH_MULTIPLIER)
            self.bonus_type = random.choice(config.BONUS_TYPES)
        else:
            self.max_health = config.ENEMY_HEALTH
            self.bonus_type = None
            
        self.health = self.max_health
        
        # Composante aléatoire pour l'IA
        self.random_offset_x = 0
        self.random_offset_y = 0
        self.random_timer = 0
    
    def update(self, player_x, player_y):
        """Met à jour la position de l'ennemi (suit le joueur)"""
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
            # Déplacer l'ennemi
            self.x += dx * self.speed
            self.y += dy * self.speed
    
    def take_damage(self, damage):
        """Fait subir des dégâts à l'ennemi"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen):
        """Dessine l'ennemi"""
        # Couleur selon le type d'ennemi
        enemy_color = self.config.SPECIAL_ENEMY_COLOR if self.is_special else self.config.ENEMY_COLOR
        
        # Corps principal
        pygame.draw.rect(screen, enemy_color,
                        (int(self.x), int(self.y), self.size, self.size))
        
        # Contour blanc (plus épais pour les ennemis spéciaux)
        border_width = 3 if self.is_special else 2
        pygame.draw.rect(screen, self.config.WHITE,
                        (int(self.x), int(self.y), self.size, self.size), border_width)
        
        # Effet scintillant pour les ennemis spéciaux
        if self.is_special:
            pulse = int(50 * (1 + math.sin(pygame.time.get_ticks() * 0.01)))
            glow_color = (255, 255, 255, pulse)
            glow_rect = pygame.Rect(self.x - 2, self.y - 2, self.size + 4, self.size + 4)
            pygame.draw.rect(screen, self.config.WHITE, glow_rect, 1)
        
        # Barre de santé si endommagé
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
            thickness = 2  # Plus fin
        else:
            # Éclair principal : couleur blanche/bleue
            color = tuple(int(c * intensity) for c in self.config.LIGHTNING_COLOR)
            secondary_color = tuple(int(c * intensity) for c in self.config.LIGHTNING_SECONDARY_COLOR)
            thickness = 3  # Plus épais
        
        # Dessiner les segments de l'éclair avec ajustement de caméra
        for i in range(len(self.points) - 1):
            start_point = (int(self.points[i][0] - camera_x), int(self.points[i][1] - camera_y))
            end_point = (int(self.points[i + 1][0] - camera_x), int(self.points[i + 1][1] - camera_y))
            
            # Ligne principale
            pygame.draw.line(screen, color, start_point, end_point, thickness)
            
            # Ligne secondaire pour l'effet de lueur
            pygame.draw.line(screen, secondary_color, start_point, end_point, 1)


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
            print(f"❤️ Soigné de {healed} points de vie")
            
        elif bonus_type == "shield":
            # Aura de protection
            self.shield_hits_remaining = self.config.BONUS_SHIELD_HITS
            print(f"🛡️ Bouclier activé ({self.shield_hits_remaining} coups)")
            
        elif bonus_type == "double_damage":
            # Double dégâts
            self.active_bonuses["double_damage"] = self.config.BONUS_DOUBLE_DAMAGE_DURATION
            print("⚔️ Double dégâts activé")
            
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
            print(f"⚡ Tempête d'éclairs ! {self.config.BONUS_LIGHTNING_STORM_COUNT} éclairs")
            
        elif bonus_type == "speed_boost":
            # Boost de vitesse
            if self.original_speed is None:
                self.original_speed = game_instance.player.speed
            game_instance.player.speed = self.original_speed * self.config.BONUS_SPEED_BOOST_MULTIPLIER
            self.active_bonuses["speed_boost"] = self.config.BONUS_SPEED_BOOST_DURATION
            print("🚀 Boost de vitesse activé")
            
        elif bonus_type == "invincibility":
            # Invincibilité temporaire
            self.active_bonuses["invincibility"] = self.config.BONUS_INVINCIBILITY_DURATION
            print("✨ Invincibilité activée")
            
        elif bonus_type == "time_slow":
            # Ralentissement du temps
            self.active_bonuses["time_slow"] = self.config.BONUS_TIME_SLOW_DURATION
            print("⏰ Temps ralenti")
            
        elif bonus_type == "freeze":
            # Gel des ennemis
            self.active_bonuses["freeze"] = self.config.BONUS_FREEZE_DURATION
            print("❄️ Ennemis gelés")
    
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
            print("🚀 Boost de vitesse terminé")
        elif bonus_type == "invincibility":
            print("✨ Invincibilité terminée")
        elif bonus_type == "time_slow":
            print("⏰ Temps normal")
        elif bonus_type == "freeze":
            print("❄️ Dégel des ennemis")
    
    def can_take_damage(self):
        """Vérifie si le joueur peut subir des dégâts"""
        # Bouclier
        if self.shield_hits_remaining > 0:
            self.shield_hits_remaining -= 1
            print(f"🛡️ Bouclier ! ({self.shield_hits_remaining} coups restants)")
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
