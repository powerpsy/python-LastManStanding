"""
Classes du joueur et des entités du jeu
"""

import pygame
import math
import numpy as np

class Player:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        
        # Vecteurs de position et vitesse
        self.vel_x = 0
        self.vel_y = 0
        
        # Statistiques
        self.health = 100
        self.max_health = 100
        self.size = config.PLAYER_SIZE
        self.speed = config.PLAYER_SPEED
        self.color = config.PLAYER_COLOR
        
        # Combat
        self.last_fire_time = 0
        
        # Rectangle de collision
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
    def update(self, keys_pressed, frame_count):
        """Met à jour le joueur"""
        # Gestion des entrées avec inertie
        acceleration = self.speed * 0.3
        
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_z]:  # Support QWERTY et AZERTY
            self.vel_y -= acceleration
        if keys_pressed[pygame.K_s]:
            self.vel_y += acceleration
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_q]:  # Support QWERTY et AZERTY
            self.vel_x -= acceleration
        if keys_pressed[pygame.K_d]:
            self.vel_x += acceleration
            
        # Application de la friction
        self.vel_x *= self.config.PLAYER_FRICTION
        self.vel_y *= self.config.PLAYER_FRICTION
        
        # Limite de vitesse
        speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        if speed > self.speed:
            self.vel_x = (self.vel_x / speed) * self.speed
            self.vel_y = (self.vel_y / speed) * self.speed
        
        # Mise à jour de la position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Limites de l'écran
        self.x = max(self.size//2, min(self.config.WINDOW_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(self.config.WINDOW_HEIGHT - self.size//2, self.y))
        
        # Mise à jour du rectangle de collision
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, screen):
        """Dessine le joueur"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size//2)
        # Contour
        pygame.draw.circle(screen, self.config.WHITE, (int(self.x), int(self.y)), self.size//2, 2)
        
    def can_fire(self, frame_count):
        """Vérifie si le joueur peut tirer"""
        return frame_count - self.last_fire_time >= self.config.ZAP_FIRE_RATE
        
    def fire(self, frame_count):
        """Marque que le joueur a tiré"""
        self.last_fire_time = frame_count
        
    def take_damage(self, damage):
        """Subir des dégâts"""
        self.health -= damage
        return self.health <= 0  # Retourne True si mort


class Enemy:
    def __init__(self, x, y, config, wave_number=1):
        self.x = x
        self.y = y
        self.config = config
        
        # Statistiques basées sur la vague
        difficulty_multiplier = 1 + (wave_number - 1) * config.DIFFICULTY_INCREASE
        difficulty_multiplier = min(difficulty_multiplier, config.MAX_ENEMY_SPEED_MULTIPLIER)
        
        self.size = config.ENEMY_SIZE
        self.speed = config.ENEMY_SPEED * difficulty_multiplier
        self.color = config.ENEMY_COLOR
        self.health = int(20 + wave_number * 5)  # Plus de santé par vague
        
        # IA
        self.target_x = x
        self.target_y = y
        self.random_factor = 0.1  # Composante aléatoire du mouvement
        
        # Rectangle de collision
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
    def update(self, player_x, player_y):
        """Met à jour l'ennemi"""
        # Direction vers le joueur
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalisation de la direction
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Ajout d'une composante aléatoire
            random_angle = (np.random.random() - 0.5) * self.random_factor
            cos_a = math.cos(random_angle)
            sin_a = math.sin(random_angle)
            
            # Rotation de la direction
            new_dir_x = dir_x * cos_a - dir_y * sin_a
            new_dir_y = dir_x * sin_a + dir_y * cos_a
            
            # Mouvement
            self.x += new_dir_x * self.speed
            self.y += new_dir_y * self.speed
            
        # Mise à jour du rectangle de collision
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, screen):
        """Dessine l'ennemi"""
        pygame.draw.rect(screen, self.color, (int(self.x - self.size//2), 
                                             int(self.y - self.size//2), 
                                             self.size, self.size))
        # Contour
        pygame.draw.rect(screen, self.config.WHITE, (int(self.x - self.size//2), 
                                                     int(self.y - self.size//2), 
                                                     self.size, self.size), 1)
        
    def take_damage(self, damage):
        """Subir des dégâts"""
        self.health -= damage
        return self.health <= 0  # Retourne True si mort


class Zap:
    def __init__(self, start_x, start_y, target_x, target_y, config):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.config = config
        
        # Direction vers la cible
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vel_x = (dx / distance) * config.ZAP_SPEED
            self.vel_y = (dy / distance) * config.ZAP_SPEED
        else:
            self.vel_x = 0
            self.vel_y = config.ZAP_SPEED
            
        # Propriétés visuelles
        self.width = config.ZAP_WIDTH
        self.length = config.ZAP_LENGTH
        self.color = config.ZAP_COLOR
        self.damage = 25
        
        # Rectangle de collision
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.width)
        
    def update(self):
        """Met à jour le projectile"""
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Mise à jour du rectangle de collision
        self.rect.center = (int(self.x), int(self.y))
        
        # Vérifier si hors écran
        return (self.x < -50 or self.x > self.config.WINDOW_WIDTH + 50 or
                self.y < -50 or self.y > self.config.WINDOW_HEIGHT + 50)
        
    def draw(self, screen):
        """Dessine l'éclair"""
        # Ligne principale de l'éclair
        end_x = self.x - self.vel_x * 0.3  # Queue de l'éclair
        end_y = self.y - self.vel_y * 0.3
        
        pygame.draw.line(screen, self.color, (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), self.width)
        
        # Point lumineux à la tête
        pygame.draw.circle(screen, self.config.WHITE, (int(self.x), int(self.y)), self.width//2)
