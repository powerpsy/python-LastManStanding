import pygame
import random
import math
from entities import Player, Enemy, Zap, Lightning, Particle, EnergyOrb, BonusManager
from background import Background

class Game:
    """Classe principale du jeu"""
    
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Last Man Standing")
        self.clock = pygame.time.Clock()
        
        # Police adaptative
        self.font = pygame.font.Font(None, int(36 * self.config.font_scale))
        self.small_font = pygame.font.Font(None, int(24 * self.config.font_scale))
        
        # État du jeu
        self.running = True
        self.paused = False
        self.paused_skills = False  # Nouvel état pour l'écran de compétences
        self.game_over = False
        self.score = 0
        
        # Entités
        self.player = Player(
            config.WINDOW_WIDTH // 2,
            config.WINDOW_HEIGHT // 2,
            config
        )
        self.enemies = []
        self.zaps = []
        self.lightnings = []  # Nouvelle liste pour les éclairs
        self.particles = []   # Nouvelle liste pour les particules
        self.energy_orbs = []  # Nouvelle liste pour les boules d'énergie
        
        # Gestion des vagues d'ennemis
        self.wave_number = 1
        self.enemies_per_wave = config.INITIAL_ENEMIES_PER_WAVE
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = config.ENEMY_SPAWN_DELAY_BASE
        self.base_spawn_delay = config.ENEMY_SPAWN_DELAY_BASE
        self.min_spawn_delay = config.ENEMY_SPAWN_DELAY_MIN
        
        # Tir automatique
        self.fire_timer = 0
        self.lightning_timer = 0  # Nouveau timer pour les éclairs
        
        # Progression des capacités avec les vagues
        self.current_energy_orb_max = config.ENERGY_ORB_MAX_COUNT_BASE  # Commence avec 1 boule
        self.current_lightning_fire_rate = config.LIGHTNING_FIRE_RATE_BASE  # Commence avec 1s
        
        # Système de caméra avec délai
        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0
        self.camera_delay_timer = 0
        self.camera_follow_speed = 0.1
        self.camera_delay_duration = config.CAMERA_DELAY_DURATION
        
        # Système d'upgrade
        self.show_upgrade_screen = False
        self.ban_mode = False
        self.upgrade_options = []
        self.roll_count = 3
        self.ban_count = 3
        
        # Initialisation du background
        self.background = Background(config)
        
        # Gestionnaire de bonus
        self.bonus_manager = BonusManager(config)
    
    def handle_events(self):
        """Gère les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if self.show_upgrade_screen:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    # Boutons
                    btn_w, btn_h = 120, 48
                    screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
                    btn_y = screen_h//2 + 120
                    roll_rect = pygame.Rect(screen_w//2-200, btn_y, btn_w, btn_h)
                    ban_rect = pygame.Rect(screen_w//2-60, btn_y, btn_w, btn_h)
                    skip_rect = pygame.Rect(screen_w//2+80, btn_y, btn_w, btn_h)
                    # ROLL
                    if roll_rect.collidepoint(mx, my) and self.roll_count > 0 and not self.ban_mode:
                        self.upgrade_options = random.sample(self.config.UPGRADE_POOL, 3)
                        self.roll_count -= 1
                    # BAN
                    elif ban_rect.collidepoint(mx, my) and self.ban_count > 0 and not self.ban_mode:
                        self.ban_mode = True
                        # Changer le background à la prochaine draw
                    # SKIP
                    elif skip_rect.collidepoint(mx, my):
                        self.show_upgrade_screen = False
                        self.paused = False
                        self.ban_mode = False
                    # Sélection d'une option en mode BAN
                    elif self.ban_mode:
                        for i, rect in enumerate(self.get_upgrade_option_rects()):
                            if rect.collidepoint(mx, my):
                                self.upgrade_options.pop(i)
                                self.ban_count -= 1
                                self.ban_mode = False
                                break
                return
            # ...existing code...

    def update(self):
        """Met à jour la logique du jeu"""
        if self.paused or self.game_over:
            return
        
        # Met à jour le joueur
        keys = pygame.key.get_pressed()
        player_was_moving = self.player.vel_x != 0 or self.player.vel_y != 0
        self.player.update(keys)
        player_is_moving = self.player.vel_x != 0 or self.player.vel_y != 0
        
        # Contraindre le joueur dans les limites du monde généré
        self.background.constrain_player(self.player)
        
        # Mise à jour de la caméra avec délai
        self.update_camera(player_was_moving, player_is_moving)
        
        # Mettre à jour le gestionnaire de bonus
        self.bonus_manager.update(self)
        
        # Spawn des ennemis par vagues avec délai décroissant
        if len(self.enemies) == 0 and self.enemies_spawned >= self.enemies_per_wave:
            # Nouvelle vague
            self.wave_number += 1
            self.score += self.config.SCORE_WAVE_BONUS_MULTIPLIER * self.wave_number  # Bonus de vague
            self.enemies_per_wave += self.config.ENEMIES_INCREASE_PER_WAVE
            self.enemies_spawned = 0
            
            # Déclencher l'écran d'upgrade
            self.trigger_upgrade_screen()
            
            # Progression des capacités tous les 5 niveaux
            self.update_abilities_progression()
            
            # Réduction du délai entre les ennemis (plus difficile)
            reduction_factor = self.config.ENEMY_SPAWN_DELAY_REDUCTION ** (self.wave_number - 1)
            self.enemy_spawn_delay = max(
                self.min_spawn_delay,
                int(self.base_spawn_delay * reduction_factor)
            )
            
            print(f"🌊 Vague {self.wave_number} - {self.enemies_per_wave} ennemis")
            print(f"⚡ Capacités: {len(self.energy_orbs)}/{self.current_energy_orb_max} orbes, Éclair: {self.current_lightning_fire_rate/60:.1f}s")
        
        # Spawn d'un nouvel ennemi si nécessaire
        if self.enemies_spawned < self.enemies_per_wave:
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_delay:
                self.spawn_enemy()
                self.enemies_spawned += 1
                self.enemy_spawn_timer = 0
        
        # Met à jour les ennemis
        enemy_speed_multiplier = self.bonus_manager.get_enemy_speed_multiplier()
        for enemy in self.enemies[:]:
            # Appliquer le multiplicateur de vitesse (pour les bonus time_slow et freeze)
            original_speed = enemy.speed
            enemy.speed = original_speed * enemy_speed_multiplier
            
            enemy.update(self.player.x, self.player.y)
            
            # Restaurer la vitesse originale
            enemy.speed = original_speed
            
            # Collision avec le joueur
            if self.check_collision(self.player, enemy):
                # Vérifier si le joueur peut subir des dégâts (bouclier, invincibilité)
                if self.bonus_manager.can_take_damage():
                    self.player.take_damage(self.config.ENEMY_DAMAGE)
                    if self.player.health <= 0:
                        self.game_over = True
                        break
        
        # Tir automatique (restauré)
        self.fire_timer += 1
        if self.fire_timer >= self.config.ZAP_FIRE_RATE and self.enemies:
            self.auto_fire()
            self.fire_timer = 0
        
        # Éclairs automatiques (restauré)
        self.lightning_timer += 1
        if self.lightning_timer >= self.current_lightning_fire_rate:
            self.auto_lightning()
            self.lightning_timer = 0
        
        # Vérification de sécurité : s'assurer d'avoir le bon nombre de boules
        self.ensure_correct_orb_count()
        
        # Met à jour les zaps
        for zap in self.zaps[:]:
            zap.update()
            
            # Retirer les zaps qui sortent de la zone de caméra étendue
            margin = 200  # Marge pour garder les projectiles un peu plus longtemps
            if (zap.x < self.camera_x - margin or 
                zap.x > self.camera_x + self.config.WINDOW_WIDTH + margin or 
                zap.y < self.camera_y - margin or 
                zap.y > self.camera_y + self.config.WINDOW_HEIGHT + margin):
                self.zaps.remove(zap)
                continue
            
            # Collision avec les ennemis
            for enemy in self.enemies[:]:
                if self.check_collision(zap, enemy):
                    damage = int(self.config.ZAP_DAMAGE * self.bonus_manager.get_damage_multiplier())
                    enemy.take_damage(damage)
                    self.zaps.remove(zap)
                    
                    if enemy.health <= 0:
                        # Appliquer bonus si c'est un ennemi spécial
                        if enemy.is_special and enemy.bonus_type:
                            self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                        
                        # Vérifier que l'ennemi est encore dans la liste (au cas où le bonus l'aurait supprimé)
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.score += self.config.SCORE_PER_ENEMY_KILL
                    break
        
        # Met à jour les éclairs
        for lightning in self.lightnings[:]:
            if not lightning.update():
                self.lightnings.remove(lightning)
        
        # Met à jour les particules
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
        
        # Met à jour les boules d'énergie (avant le rendu pour éviter les interférences)
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        for orb in self.energy_orbs[:]:
            if not orb.update(player_center_x, player_center_y):
                self.energy_orbs.remove(orb)
    
    def spawn_enemy(self):
        """Crée un nouvel ennemi juste en dehors de la zone de caméra visible"""
        world_bounds = self.background.get_world_bounds()
        
        # Calculer la zone visible actuelle de la caméra
        camera_left = int(self.camera_x)
        camera_right = int(self.camera_x + self.config.WINDOW_WIDTH)
        camera_top = int(self.camera_y)
        camera_bottom = int(self.camera_y + self.config.WINDOW_HEIGHT)
        
        # Distance en dehors de l'écran (environ 2 tiles de 32px = 64px)
        spawn_margin = 64
        
        # Choisir un côté aléatoire pour faire apparaître l'ennemi
        side = random.randint(0, 3)
        
        if side == 0:  # Haut
            x = random.randint(max(0, camera_left - spawn_margin), 
                             min(world_bounds['max_x'], camera_right + spawn_margin))
            y = max(0, camera_top - spawn_margin - random.randint(0, spawn_margin))
            
        elif side == 1:  # Droite
            x = min(world_bounds['max_x'], camera_right + spawn_margin + random.randint(0, spawn_margin))
            y = random.randint(max(0, camera_top - spawn_margin), 
                             min(world_bounds['max_y'], camera_bottom + spawn_margin))
            
        elif side == 2:  # Bas
            x = random.randint(max(0, camera_left - spawn_margin), 
                             min(world_bounds['max_x'], camera_right + spawn_margin))
            y = min(world_bounds['max_y'], camera_bottom + spawn_margin + random.randint(0, spawn_margin))
            
        else:  # Gauche
            x = max(0, camera_left - spawn_margin - random.randint(0, spawn_margin))
            y = random.randint(max(0, camera_top - spawn_margin), 
                             min(world_bounds['max_y'], camera_bottom + spawn_margin))
        
        # S'assurer que les coordonnées sont dans les limites du monde et sont des entiers
        x = int(max(0, min(x, world_bounds['max_x'] - 32)))  # 32 = taille de l'ennemi
        y = int(max(0, min(y, world_bounds['max_y'] - 32)))
        
        # Créer l'ennemi (avec chance d'être spécial)
        is_special = random.random() < self.config.SPECIAL_ENEMY_SPAWN_CHANCE
        enemy = Enemy(x, y, self.config, is_special)
        self.enemies.append(enemy)
    
    def update_camera(self, player_was_moving, player_is_moving):
        """Met à jour la position de la caméra avec un délai"""
        # Calculer la position cible de la caméra (centrée sur le joueur)
        target_x = self.player.x + self.player.size // 2 - self.config.WINDOW_WIDTH // 2
        target_y = self.player.y + self.player.size // 2 - self.config.WINDOW_HEIGHT // 2
        
        # Contraindre la cible dans les limites du monde
        world_bounds = self.background.get_world_bounds()
        target_x = max(0, min(target_x, world_bounds['max_x'] - self.config.WINDOW_WIDTH))
        target_y = max(0, min(target_y, world_bounds['max_y'] - self.config.WINDOW_HEIGHT))
        
        # Si le joueur commence à bouger, démarrer le timer de délai
        if not player_was_moving and player_is_moving:
            self.camera_delay_timer = self.camera_delay_duration
        
        # Diminuer le timer de délai
        if self.camera_delay_timer > 0:
            self.camera_delay_timer -= 1
        
        # Si le délai est terminé, la caméra suit le joueur
        if self.camera_delay_timer <= 0:
            # Interpolation douce vers la position cible
            self.camera_x += (target_x - self.camera_x) * self.camera_follow_speed
            self.camera_y += (target_y - self.camera_y) * self.camera_follow_speed
        
        # Si le joueur s'arrête, centrer immédiatement
        if player_was_moving and not player_is_moving:
            self.camera_x = target_x
            self.camera_y = target_y
    
    def update_abilities_progression(self):
        """Met à jour les capacités du joueur"""
        # Progression des orbes d'énergie : 1 orbe par niveau jusqu'au niveau 7
        if self.wave_number <= 7:
            expected_orbs = min(self.wave_number, self.config.ENERGY_ORB_MAX_COUNT_FINAL)
            
            if expected_orbs > self.current_energy_orb_max:
                self.current_energy_orb_max = expected_orbs
                # Supprimer toutes les orbes existantes et les recréer
                self.energy_orbs.clear()
                self.recreate_all_energy_orbs()
        
        # Améliorer la vitesse des éclairs tous les 5 niveaux
        if self.wave_number % 5 == 0:
            if self.current_lightning_fire_rate > self.config.LIGHTNING_FIRE_RATE_MIN:
                self.current_lightning_fire_rate = max(
                    self.config.LIGHTNING_FIRE_RATE_MIN,
                    self.current_lightning_fire_rate - 6
                )
    
    def auto_fire(self):
        """Tire automatiquement vers l'ennemi le plus proche"""
        if not self.enemies:
            return
        
        # Portée maximale des projectiles : 10 tiles (320 pixels) - un peu plus que les éclairs
        zap_range = 320
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Filtrer les ennemis dans la portée
        enemies_in_range = [e for e in self.enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= zap_range]
        
        if not enemies_in_range:
            return  # Aucun ennemi dans la portée
        
        # Trouver l'ennemi le plus proche parmi ceux dans la portée
        closest_enemy = min(enemies_in_range, key=lambda e: 
            math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2))
        
        # Créer un projectile
        enemy_center_x = closest_enemy.x + closest_enemy.size // 2
        enemy_center_y = closest_enemy.y + closest_enemy.size // 2
        
        zap = Zap(player_center_x, player_center_y, enemy_center_x, enemy_center_y, self.config)
        self.zaps.append(zap)
    
    def auto_lightning(self):
        """Tire automatiquement des éclairs vers plusieurs ennemis"""
        if not self.enemies:
            return
        
        # Trouver l'ennemi le plus proche dans la portée des éclairs
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Portée maximale de l'éclair : 8 tiles (256 pixels)
        lightning_range = 384  # Augmenté de 320 à 384 (12 tiles au lieu de 10)
        
        # Filtrer les ennemis dans la portée
        enemies_in_range = [e for e in self.enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= lightning_range]
        
        if not enemies_in_range:
            return  # Aucun ennemi dans la portée
        
        # Trouver l'ennemi le plus proche parmi ceux dans la portée
        closest_enemy = min(enemies_in_range, key=lambda e: 
            math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2))
        
        # Créer un éclair
        lightning = Lightning(player_center_x, player_center_y, 
                            closest_enemy.x + closest_enemy.size // 2,
                            closest_enemy.y + closest_enemy.size // 2,
                            self.config)
        self.lightnings.append(lightning)
        
        # Créer des particules d'explosion
        self.create_explosion_particles(closest_enemy.x + closest_enemy.size // 2,
                                      closest_enemy.y + closest_enemy.size // 2)
        
        # Appliquer des dégâts et trouver d'autres ennemis proches pour l'effet de chaîne
        targets = [closest_enemy]
        current_target = closest_enemy
        
        # Effet de chaîne : jusqu'à 3 ennemis supplémentaires dans un rayon de 8 tiles (256 pixels)
        chain_range = 256  # 8 tiles × 32 pixels = 256 pixels
        for _ in range(3):
            nearby_enemies = [e for e in self.enemies 
                            if e not in targets and 
                            math.sqrt((e.x - current_target.x)**2 + (e.y - current_target.y)**2) <= chain_range]
            if not nearby_enemies:
                break
            
            next_target = min(nearby_enemies, key=lambda e: 
                math.sqrt((e.x - current_target.x)**2 + (e.y - current_target.y)**2))
            targets.append(next_target)
            
            # Créer un éclair vers la cible suivante
            lightning = Lightning(current_target.x + current_target.size // 2,
                                current_target.y + current_target.size // 2,
                                next_target.x + next_target.size // 2,
                                next_target.y + next_target.size // 2,
                                self.config)
            self.lightnings.append(lightning)
            
            current_target = next_target
        
        # Appliquer les dégâts à tous les ennemis touchés
        for enemy in targets:
            damage = int(self.config.LIGHTNING_DAMAGE * self.bonus_manager.get_damage_multiplier())
            enemy.take_damage(damage)
            self.create_explosion_particles(enemy.x + enemy.size // 2,
                                          enemy.y + enemy.size // 2)
            
            if enemy.health <= 0:
                # Appliquer bonus si c'est un ennemi spécial
                if enemy.is_special and enemy.bonus_type:
                    self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                
                # Vérifier que l'ennemi est encore dans la liste (au cas où le bonus l'aurait supprimé)
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                self.score += self.config.SCORE_PER_LIGHTNING_KILL  # Plus de points pour les éclairs
    
    def create_explosion_particles(self, x, y):
        """Crée des particules d'explosion à la position donnée"""
        for _ in range(self.config.PARTICLE_COUNT):
            particle = Particle(x, y, self.config)
            self.particles.append(particle)
    
    def check_collision(self, obj1, obj2):
        """Vérifie la collision entre deux objets"""
        return (obj1.x < obj2.x + obj2.size and
                obj1.x + obj1.size > obj2.x and
                obj1.y < obj2.y + obj2.size and
                obj1.y + obj1.size > obj2.y)
    
    def draw(self):
        """Dessine tous les éléments du jeu"""
        # TOUJOURS remplir l'écran d'abord pour éviter l'écran noir
        self.screen.fill((50, 50, 50))  # Fond gris foncé
        
        if self.show_upgrade_screen:
            self.draw_upgrade_screen()
            pygame.display.flip()
            return
        
        if self.paused_skills:
            self.draw_skills_screen()
            pygame.display.flip()
            return
        
        # Utiliser les coordonnées de caméra avec délai
        camera_x = self.camera_x
        camera_y = self.camera_y
        
        # Dessiner l'arrière-plan procédural en premier
        self.background.draw(self.screen, camera_x, camera_y)
        
        if not self.game_over:
            # Dessiner les entités (ordre d'arrière-plan vers premier plan)
            
            # Dessiner les ennemis en premier
            for enemy in self.enemies:
                enemy_screen_x = enemy.x - camera_x
                enemy_screen_y = enemy.y - camera_y
                temp_x, temp_y = enemy.x, enemy.y
                enemy.x, enemy.y = enemy_screen_x, enemy_screen_y
                enemy.draw(self.screen)
                enemy.x, enemy.y = temp_x, temp_y
            
            # Dessiner les projectiles
            for zap in self.zaps:
                zap_screen_x = zap.x - camera_x
                zap_screen_y = zap.y - camera_y
                temp_x, temp_y = zap.x, zap.y
                zap.x, zap.y = zap_screen_x, zap_screen_y
                zap.draw(self.screen)
                zap.x, zap.y = temp_x, temp_y
            
            # Dessiner les éclairs (derrière le joueur)
            for lightning in self.lightnings:
                # Les éclairs ont leurs propres coordonnées dans leurs points
                lightning.draw(self.screen, camera_x, camera_y)
            
            # Dessiner les particules
            for particle in self.particles:
                particle_screen_x = particle.x - camera_x
                particle_screen_y = particle.y - camera_y
                temp_x, temp_y = particle.x, particle.y
                particle.x, particle.y = particle_screen_x, particle_screen_y
                particle.draw(self.screen)
                particle.x, particle.y = temp_x, temp_y
            
            # Dessiner les boules d'énergie
            for orb in self.energy_orbs:
                orb_screen_x = orb.x - camera_x
                orb_screen_y = orb.y - camera_y
                temp_x, temp_y = orb.x, orb.y
                orb.x, orb.y = orb_screen_x, orb_screen_y
                orb.draw(self.screen)
                orb.x, orb.y = temp_x, temp_y
            
            # Dessiner le joueur EN DERNIER (au premier plan)
            player_screen_x = self.player.x - camera_x
            player_screen_y = self.player.y - camera_y
            temp_x, temp_y = self.player.x, self.player.y
            self.player.x, self.player.y = player_screen_x, player_screen_y
            self.player.draw(self.screen)
            self.player.x, self.player.y = temp_x, temp_y
        
        # Minimap
        self.draw_minimap()
        
        # Interface utilisateur
        self.draw_ui()
        
        if self.paused:
            self.draw_pause_screen()
        elif self.game_over:
            self.draw_game_over_screen()
        
        # TOUJOURS faire le flip pour afficher à l'écran
        pygame.display.flip()
        # ...existing code...
    
    def draw_ui(self):
        """Dessine l'interface utilisateur"""
        # Barre de santé
        health_ratio = max(0, self.player.health / self.player.max_health)
        
        # Couleur de la barre selon la santé
        if health_ratio > 0.6:
            health_color = self.config.GREEN
        elif health_ratio > 0.3:
            health_color = self.config.YELLOW
        else:
            health_color = self.config.RED
        
        # Fond de la barre de santé
        health_bg_rect = pygame.Rect(10, 10, self.config.HEALTH_BAR_WIDTH, self.config.HEALTH_BAR_HEIGHT)
        pygame.draw.rect(self.screen, self.config.GRAY, health_bg_rect)
        
        # Barre de santé actuelle
        health_width = int(self.config.HEALTH_BAR_WIDTH * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(10, 10, health_width, self.config.HEALTH_BAR_HEIGHT)
            pygame.draw.rect(self.screen, health_color, health_rect)
        
        # Contour de la barre
        pygame.draw.rect(self.screen, self.config.WHITE, health_bg_rect, 2)
        
        # Textes (pré-calculer les surfaces)
        health_text = f"HP: {self.player.health}/{self.player.max_health}"
        health_surface = self.small_font.render(health_text, True, self.config.WHITE)
        self.screen.blit(health_surface, (10, 35))
        
        wave_text = f"Vague {self.wave_number} - Ennemis: {len(self.enemies)}"
        wave_surface = self.font.render(wave_text, True, self.config.WHITE)
        self.screen.blit(wave_surface, (10, 60))
        
        # Afficher le statut des éclairs
        lightning_cooldown = max(0, self.current_lightning_fire_rate - self.lightning_timer) / 60
        lightning_text = f"Éclair: {lightning_cooldown:.1f}s (Chaîne: {self.config.LIGHTNING_CHAIN_CHANCE*100:.0f}%)"
        lightning_surface = self.small_font.render(lightning_text, True, self.config.CYAN)
        self.screen.blit(lightning_surface, (10, 85))
        
        # Afficher le statut des boules d'énergie
        orb_text = f"Boules d'énergie: {len(self.energy_orbs)}/{self.current_energy_orb_max}"
        orb_surface = self.small_font.render(orb_text, True, self.config.PURPLE)
        self.screen.blit(orb_surface, (10, 110))
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, self.config.WHITE)
        score_rect = score_surface.get_rect()
        score_rect.topright = (self.config.WINDOW_WIDTH - 10, 10)
        self.screen.blit(score_surface, score_rect)
        
        # Afficher les bonus actifs
        y_offset = 135
        for bonus_type, frames_left in self.bonus_manager.active_bonuses.items():
            seconds_left = frames_left / 60
            bonus_text = f"{bonus_type.replace('_', ' ').title()}: {seconds_left:.1f}s"
            bonus_surface = self.small_font.render(bonus_text, True, self.config.YELLOW)
            self.screen.blit(bonus_surface, (10, y_offset))
            y_offset += 20
        
        # Afficher le bouclier s'il est actif
        if self.bonus_manager.shield_hits_remaining > 0:
            shield_text = f"🛡️ Bouclier: {self.bonus_manager.shield_hits_remaining} coups"
            shield_surface = self.small_font.render(shield_text, True, self.config.CYAN)
            self.screen.blit(shield_surface, (10, y_offset))
    
    def draw_pause_screen(self):
        """Dessine l'écran de pause"""
        # Overlay semi-transparent
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(self.config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texte de pause
        pause_text = "PAUSE"
        pause_surface = self.font.render(pause_text, True, self.config.WHITE)
        pause_rect = pause_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 50))
        self.screen.blit(pause_surface, pause_rect)
        
        # Instructions
        instructions = [
            "P - Reprendre",
            "R - Recommencer",
            "ESC - Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.small_font.render(instruction, True, self.config.WHITE)
            text_rect = text_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + i*30))
            self.screen.blit(text_surface, text_rect)
    
    def draw_game_over_screen(self):
        """Dessine l'écran de game over"""
        # Overlay rouge semi-transparent
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(self.config.RED)
        self.screen.blit(overlay, (0, 0))
        
        # Texte Game Over
        game_over_text = "GAME OVER"
        game_over_surface = self.font.render(game_over_text, True, self.config.WHITE)
        game_over_rect = game_over_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 100))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # Score final
        final_score_text = f"Score Final: {self.score}"
        final_score_surface = self.font.render(final_score_text, True, self.config.WHITE)
        final_score_rect = final_score_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 50))
        self.screen.blit(final_score_surface, final_score_rect)
        
        # Vague atteinte
        wave_text = f"Vague atteinte: {self.wave_number}"
        wave_surface = self.font.render(wave_text, True, self.config.WHITE)
        wave_rect = wave_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2))
        self.screen.blit(wave_surface, wave_rect)
        
        # Instructions
        restart_text = "R - Recommencer    ESC - Quitter"
        restart_surface = self.small_font.render(restart_text, True, self.config.WHITE)
        restart_rect = restart_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 50))
        self.screen.blit(restart_surface, restart_rect)
    
    def restart_game(self):
        """Redémarre le jeu"""
        self.game_over = False
        self.paused = False
        self.score = 0
        self.wave_number = 1
        self.enemies_per_wave = self.config.INITIAL_ENEMIES_PER_WAVE
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = self.config.ENEMY_SPAWN_DELAY_BASE
        self.fire_timer = 0
        self.lightning_timer = 0  # Nouveau
        
        # Réinitialiser les capacités
        self.current_energy_orb_max = self.config.ENERGY_ORB_MAX_COUNT_BASE
        self.current_lightning_fire_rate = self.config.LIGHTNING_FIRE_RATE_BASE
        
        # Régénérer un nouveau terrain
        self.background.regenerate()
        
        # Placer le joueur au centre du nouveau monde
        world_bounds = self.background.get_world_bounds()
        self.player = Player(
            world_bounds['max_x'] // 2,
            world_bounds['max_y'] // 2,
            self.config
        )
        
        # Réinitialiser la caméra
        self.camera_x = self.player.x + self.player.size // 2 - self.config.WINDOW_WIDTH // 2
        self.camera_y = self.player.y + self.player.size // 2 - self.config.WINDOW_HEIGHT // 2
        self.camera_delay_timer = 0
        
        # Vider les listes
        self.enemies.clear()
        self.zaps.clear()
        self.lightnings.clear()  # Nouveau
        self.particles.clear()   # Nouveau
        self.energy_orbs.clear()  # Nouveau
        
        # Créer les orbes d'énergie initiales
        self.recreate_all_energy_orbs()
        
        # Réinitialiser le gestionnaire de bonus
        self.bonus_manager = BonusManager(self.config)
    
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)
    
    def ensure_correct_orb_count(self):
        """S'assure que le joueur a le bon nombre de boules d'énergie selon son niveau"""
        expected_orb_count = self.current_energy_orb_max
        
        # Si le nombre d'orbes ne correspond pas, les recréer toutes
        if len(self.energy_orbs) != expected_orb_count:
            self.energy_orbs.clear()
            self.recreate_all_energy_orbs()
    
    def recreate_all_energy_orbs(self):
        """Recrée toutes les orbes d'énergie avec les positions optimales"""
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Créer toutes les orbes avec une répartition uniforme
        for i in range(self.current_energy_orb_max):
            orb = EnergyOrb(player_center_x, player_center_y, i, self.current_energy_orb_max, self.config)
            self.energy_orbs.append(orb)
    
    def draw_minimap(self):
        """Dessine une minimap en bas à droite de la fenêtre"""
        # Paramètres de la minimap - CARRÉE puisque la map est carrée (100x100)
        # Utiliser la plus petite dimension pour que la minimap soit carrée et tienne à l'écran
        minimap_size = min(self.config.WINDOW_WIDTH // self.config.MINIMAP_SIZE_RATIO, 
                          self.config.WINDOW_HEIGHT // self.config.MINIMAP_SIZE_RATIO)
        minimap_width = minimap_size
        minimap_height = minimap_size
        
        # Position de la minimap (en bas à droite avec marge)
        minimap_x = self.config.WINDOW_WIDTH - minimap_width - self.config.MINIMAP_MARGIN
        minimap_y = self.config.WINDOW_HEIGHT - minimap_height - self.config.MINIMAP_MARGIN
        
        # Créer une surface pour la minimap avec support de la transparence
        minimap_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
        minimap_surface.fill((50, 50, 50, self.config.MINIMAP_ALPHA))  # Fond gris foncé avec transparence
        
        # Obtenir les limites du monde avec une marge pour garder le joueur visible
        world_bounds = self.background.get_world_bounds()
        margin_pixels = 64  # Marge de 6 pixels pour que le joueur (3x3) reste toujours visible aux bords
        
        # Ajouter une marge virtuelle au monde pour le calcul de l'échelle
        extended_world_width = world_bounds['max_x'] + (margin_pixels * 2)
        extended_world_height = world_bounds['max_y'] + (margin_pixels * 2)
        
        # Calculer le ratio d'échelle pour adapter le monde étendu à la minimap
        scale_x = minimap_width / extended_world_width
        scale_y = minimap_height / extended_world_height
        scale = min(scale_x, scale_y)  # Utiliser le plus petit ratio pour garder les proportions
        
        # Calculer l'offset pour centrer le monde réel dans la minimap étendue
        offset_x = margin_pixels * scale
        offset_y = margin_pixels * scale
        
        # Dessiner le joueur (carré blanc avec transparence)
        player_minimap_x = int(self.player.x * scale + offset_x)
        player_minimap_y = int(self.player.y * scale + offset_y)
        player_color = (255, 255, 255, self.config.MINIMAP_ALPHA)
        player_half_size = self.config.MINIMAP_PLAYER_SIZE // 2
        pygame.draw.rect(minimap_surface, player_color, 
                        (player_minimap_x - player_half_size, player_minimap_y - player_half_size, 
                         self.config.MINIMAP_PLAYER_SIZE, self.config.MINIMAP_PLAYER_SIZE))
        
        # Dessiner les ennemis (carrés rouges ou verts selon le type)
        for enemy in self.enemies:
            enemy_minimap_x = int(enemy.x * scale + offset_x)
            enemy_minimap_y = int(enemy.y * scale + offset_y)
            
            # Couleur selon le type d'ennemi
            if enemy.is_special:
                enemy_color = (0, 255, 0, self.config.MINIMAP_ALPHA)  # Vert pour les spéciaux
            else:
                enemy_color = (255, 0, 0, self.config.MINIMAP_ALPHA)  # Rouge pour les normaux
                
            enemy_half_size = self.config.MINIMAP_ENEMY_SIZE // 2
            pygame.draw.rect(minimap_surface, enemy_color, 
                            (enemy_minimap_x - enemy_half_size, enemy_minimap_y - enemy_half_size, 
                             self.config.MINIMAP_ENEMY_SIZE, self.config.MINIMAP_ENEMY_SIZE))
        
        # Dessiner un rectangle de bordure autour de la minimap avec transparence
        border_color = (200, 200, 200, self.config.MINIMAP_ALPHA)
        pygame.draw.rect(minimap_surface, border_color, 
                        (0, 0, minimap_width, minimap_height), 2)
        
        # Afficher la minimap sur l'écran principal
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
    
    def draw_skills_screen(self):
        """Affiche l'écran graphique des compétences et armes obtenues"""
        # Overlay semi-transparent (20% de transparence sur 3/4 de l'écran)
        overlay_width = int(self.config.WINDOW_WIDTH * 0.75)
        overlay_height = int(self.config.WINDOW_HEIGHT * 0.75)
        overlay_x = (self.config.WINDOW_WIDTH - overlay_width) // 2
        overlay_y = (self.config.WINDOW_HEIGHT - overlay_height) // 2
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.fill((20, 20, 40))
        overlay.set_alpha(10)  # 20% de 255 = 51
        self.screen.blit(overlay, (overlay_x, overlay_y))

        # Titre
        title = "Compétences & Armes"
        title_surface = self.font.render(title, True, self.config.WHITE)
        title_rect = title_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 60))
        self.screen.blit(title_surface, title_rect)

        # Affichage des armes (7 slots)
        slot_size = 64
        slot_margin = 24
        total_slots = 7
        start_x = (self.config.WINDOW_WIDTH - (total_slots * slot_size + (total_slots-1)*slot_margin)) // 2
        y = 150
        for i in range(total_slots):
            rect = pygame.Rect(start_x + i*(slot_size+slot_margin), y, slot_size, slot_size)
            pygame.draw.rect(self.screen, (80,80,80), rect, border_radius=12)
            # Si arme présente, dessiner une icône (exemple: orbe, éclair, etc.)
            if hasattr(self, 'weapons') and i < len(self.weapons):
                self.draw_weapon_icon(self.weapons[i], rect)
            else:
                pygame.draw.rect(self.screen, (40,40,40), rect.inflate(-16,-16), border_radius=8)

        # Affichage des compétences (14 slots, 2 lignes de 7)
        skill_slot_size = 48
        skill_slot_margin = 18
        total_skills = 14
        start_x = (self.config.WINDOW_WIDTH - (7 * skill_slot_size + 6*skill_slot_margin)) // 2
        y_skills = 270
        for i in range(total_skills):
            row = i // 7
            col = i % 7
            rect = pygame.Rect(start_x + col*(skill_slot_size+skill_slot_margin), y_skills + row*(skill_slot_size+skill_slot_margin), skill_slot_size, skill_slot_size)
            pygame.draw.rect(self.screen, (100,100,100), rect, border_radius=10)
            # Si compétence présente, dessiner une icône
            if hasattr(self, 'skills') and i < len(self.skills):
                self.draw_skill_icon(self.skills[i], rect)
            else:
                pygame.draw.rect(self.screen, (60,60,60), rect.inflate(-12,-12), border_radius=8)

        # Instructions
        text = "TAB - Reprendre le jeu"
        text_surface = self.small_font.render(text, True, self.config.WHITE)
        text_rect = text_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT-40))
        self.screen.blit(text_surface, text_rect)

    def draw_weapon_icon(self, weapon, rect):
        # Exemple d'icône graphique selon le type d'arme (à adapter selon vos armes)
        center = rect.center
        if weapon == "orb":
            pygame.draw.circle(self.screen, (0,200,255), center, rect.width//3)
        elif weapon == "lightning":
            pygame.draw.polygon(self.screen, (255,255,0), [
                (center[0], center[1]-rect.height//4),
                (center[0]+rect.width//6, center[1]),
                (center[0], center[1]+rect.height//4),
                (center[0]-rect.width//8, center[1]),
            ])
        # Ajouter d'autres armes ici
        else:
            pygame.draw.rect(self.screen, (180,180,180), rect.inflate(-20,-20), border_radius=6)

    def draw_skill_icon(self, skill, rect):
        # Exemple d'icône graphique selon le type de compétence (à adapter selon vos skills)
        center = rect.center
        pygame.draw.circle(self.screen, (120,255,120), center, rect.width//3)
        # Ajouter d'autres styles selon le skill
    
    def trigger_upgrade_screen(self):
        """Affiche l'écran de choix d'upgrade à la montée de niveau"""
        self.show_upgrade_screen = True
        self.paused = True
        self.paused_skills = False
        self.ban_mode = False
        self.upgrade_options = random.sample(self.config.UPGRADE_POOL, 3)
    
    def get_upgrade_option_rects(self):
        # Retourne les rects des 3 options pour la détection
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        opt_w, opt_h = 220, 64
        y = screen_h//2 - 80
        return [pygame.Rect(screen_w//2-340+i*240, y, opt_w, opt_h) for i in range(3)]
    
    def draw_upgrade_screen(self):
        """Affiche l'écran de choix d'upgrade"""
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        overlay = pygame.Surface((int(screen_w*0.75), int(screen_h*0.75)))
        overlay.fill((60, 60, 80) if not self.ban_mode else (80, 20, 20))
        overlay.set_alpha(51)  # 20% de transparence
        overlay_x = (screen_w - overlay.get_width()) // 2
        overlay_y = (screen_h - overlay.get_height()) // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))
        # Titre
        title = "Choisissez une amélioration" if not self.ban_mode else "Bannissez une option"
        title_surface = self.font.render(title, True, self.config.WHITE)
        title_rect = title_surface.get_rect(center=(screen_w//2, overlay_y+60))
        self.screen.blit(title_surface, title_rect)
        # Options
        for i, option in enumerate(self.upgrade_options):
            rect = self.get_upgrade_option_rects()[i]
            color = (180,220,255) if not self.ban_mode else (255,120,120)
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            opt_surface = self.small_font.render(option["name"], True, self.config.BLACK)
            opt_rect = opt_surface.get_rect(center=rect.center)
            self.screen.blit(opt_surface, opt_rect)
        # Boutons
        btn_w, btn_h = 120, 48
        btn_y = screen_h//2 + 120
        # ROLL
        roll_rect = pygame.Rect(screen_w//2-200, btn_y, btn_w, btn_h)
        roll_color = (200,200,200) if self.roll_count > 0 and not self.ban_mode else (100,100,100)
        pygame.draw.rect(self.screen, roll_color, roll_rect, border_radius=10)
        roll_text = f"ROLL ({self.roll_count})"
        roll_surface = self.small_font.render(roll_text, True, self.config.BLACK)
        self.screen.blit(roll_surface, roll_rect.move(20,10))
        # BAN
        ban_rect = pygame.Rect(screen_w//2-60, btn_y, btn_w, btn_h)
        ban_color = (200,100,100) if self.ban_count > 0 and not self.ban_mode else (100,50,50)
        pygame.draw.rect(self.screen, ban_color, ban_rect, border_radius=10)
        ban_text = f"BAN ({self.ban_count})"
        ban_surface = self.small_font.render(ban_text, True, self.config.BLACK)
        self.screen.blit(ban_surface, ban_rect.move(20,10))
        # SKIP
        skip_rect = pygame.Rect(screen_w//2+80, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (180,180,180), skip_rect, border_radius=10)
        skip_surface = self.small_font.render("SKIP", True, self.config.BLACK)
        self.screen.blit(skip_surface, skip_rect.move(30,10))
