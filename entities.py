"""
Classes du joueur et des entités du jeu
"""

import pygame
import random
import math

class Player:
    """Classe du joueur avec déplacement à inertie"""
    
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
    
    def update(self, keys):
        """Met à jour la position du joueur avec inertie"""
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
        
        # Appliquer l'accélération
        self.vel_x += accel_x
        self.vel_y += accel_y
        
        # Appliquer la friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Mettre à jour la position
        self.x += self.vel_x
        self.y += self.vel_y
    
    def take_damage(self, damage):
        """Fait subir des dégâts au joueur"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen):
        """Dessine le joueur"""
        # Corps principal
        pygame.draw.circle(screen, self.config.PLAYER_COLOR,
                         (int(self.x + self.size//2), int(self.y + self.size//2)),
                         self.size//2)
        
        # Contour blanc
        pygame.draw.circle(screen, self.config.WHITE,
                         (int(self.x + self.size//2), int(self.y + self.size//2)),
                         self.size//2, 2)


class Enemy:
    """Classe des ennemis avec IA de poursuite"""
    
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        self.size = config.ENEMY_SIZE
        self.speed = config.ENEMY_SPEED
        self.max_health = config.ENEMY_HEALTH
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
            
            # Déplacer l'ennemi
            self.x += dx * self.speed
            self.y += dy * self.speed
    
    def take_damage(self, damage):
        """Fait subir des dégâts à l'ennemi"""
        self.health = max(0, self.health - damage)
    
    def draw(self, screen):
        """Dessine l'ennemi"""
        # Corps principal
        pygame.draw.rect(screen, self.config.ENEMY_COLOR,
                        (int(self.x), int(self.y), self.size, self.size))
        
        # Contour blanc
        pygame.draw.rect(screen, self.config.WHITE,
                        (int(self.x), int(self.y), self.size, self.size), 2)
        
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
    
    def __init__(self, start_x, start_y, target_x, target_y, config):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.config = config
        self.damage = config.LIGHTNING_DAMAGE
        
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
    
    def draw(self, screen):
        """Dessine l'éclair avec effet de zigzag"""
        if self.current_life <= 0:
            return
        
        # Intensité basée sur la durée de vie restante
        intensity = self.current_life / self.lifetime
        
        # Couleur qui s'estompe
        color = tuple(int(c * intensity) for c in self.config.LIGHTNING_COLOR)
        secondary_color = tuple(int(c * intensity) for c in self.config.LIGHTNING_SECONDARY_COLOR)
        
        # Dessiner les segments de l'éclair
        for i in range(len(self.points) - 1):
            start_point = (int(self.points[i][0]), int(self.points[i][1]))
            end_point = (int(self.points[i + 1][0]), int(self.points[i + 1][1]))
            
            # Ligne principale (épaisse)
            pygame.draw.line(screen, color, start_point, end_point, 3)
            
            # Ligne secondaire (fine) pour l'effet de lueur
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
