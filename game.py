import pygame
import random
import math
from entities import Player, Enemy, Zap, Lightning, Particle, EnergyOrb

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
        self.enemies_per_wave = 5
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 120  # frames entre chaque ennemi (2 secondes à 60fps)
        self.base_spawn_delay = 120   # délai de base pour calculer la réduction
        self.min_spawn_delay = 20     # délai minimum (0.33 secondes)
        
        # Tir automatique
        self.fire_timer = 0
        self.lightning_timer = 0  # Nouveau timer pour les éclairs
        
        # Progression des capacités avec les vagues
        self.current_energy_orb_max = config.ENERGY_ORB_MAX_COUNT_BASE  # Commence avec 1 boule
        self.current_lightning_fire_rate = config.LIGHTNING_FIRE_RATE_BASE  # Commence avec 1s
        
        # Créer les orbes d'énergie initiales
        self.recreate_all_energy_orbs()
    
    def handle_events(self):
        """Gère les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
    
    def update(self):
        """Met à jour la logique du jeu"""
        if self.paused or self.game_over:
            return
        
        # Met à jour le joueur
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Vérifier les limites d'écran pour le joueur
        if self.player.x < 0:
            self.player.x = 0
        elif self.player.x > self.config.WINDOW_WIDTH - self.player.size:
            self.player.x = self.config.WINDOW_WIDTH - self.player.size
        
        if self.player.y < 0:
            self.player.y = 0
        elif self.player.y > self.config.WINDOW_HEIGHT - self.player.size:
            self.player.y = self.config.WINDOW_HEIGHT - self.player.size
        
        # Spawn des ennemis par vagues avec délai décroissant
        if len(self.enemies) == 0 and self.enemies_spawned >= self.enemies_per_wave:
            # Nouvelle vague
            self.wave_number += 1
            self.score += 50 * self.wave_number  # Bonus de vague
            self.enemies_per_wave += 2  # Plus d'ennemis par vague
            self.enemies_spawned = 0
            
            # Progression des capacités tous les 5 niveaux
            self.update_abilities_progression()
            
            # Réduction du délai entre les ennemis (plus difficile)
            reduction_factor = 0.85 ** (self.wave_number - 1)
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
        for enemy in self.enemies[:]:
            enemy.update(self.player.x + self.player.size//2, 
                        self.player.y + self.player.size//2)
            
            # Collision avec le joueur
            if self.check_collision(self.player, enemy):
                self.player.take_damage(self.config.ENEMY_DAMAGE)
                self.enemies.remove(enemy)
                
                if self.player.health <= 0:
                    self.game_over = True
        
        # Tir automatique (zaps)
        self.fire_timer += 1
        if self.fire_timer >= self.config.ZAP_FIRE_RATE and self.enemies:
            self.auto_fire()
            self.fire_timer = 0
        
        # Éclairs automatiques (nouveau)
        self.lightning_timer += 1
        if self.lightning_timer >= self.current_lightning_fire_rate:
            self.auto_lightning()
            self.lightning_timer = 0
        
        # Vérification de sécurité : s'assurer d'avoir le bon nombre de boules
        self.ensure_correct_orb_count()
        
        # Met à jour les zaps
        for zap in self.zaps[:]:
            zap.update()
            
            # Retirer les zaps qui sortent de l'écran
            if (zap.x < 0 or zap.x > self.config.WINDOW_WIDTH or 
                zap.y < 0 or zap.y > self.config.WINDOW_HEIGHT):
                self.zaps.remove(zap)
                continue
            
            # Collision avec les ennemis
            for enemy in self.enemies[:]:
                if self.check_collision(zap, enemy):
                    enemy.take_damage(self.config.ZAP_DAMAGE)
                    self.zaps.remove(zap)
                    
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 10
                    break
        
        # Met à jour les éclairs (nouveau)
        for lightning in self.lightnings[:]:
            if not lightning.update():
                self.lightnings.remove(lightning)
        
        # Met à jour les particules (nouveau)
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
        
        # Met à jour les boules d'énergie (nouveau)
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        for orb in self.energy_orbs[:]:
            if not orb.update(player_center_x, player_center_y):
                self.energy_orbs.remove(orb)
            else:
                # Vérifier les collisions avec les ennemis
                orb_rect = orb.get_collision_rect()
                for enemy in self.enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                    if orb_rect.colliderect(enemy_rect):
                        enemy.take_damage(self.config.ENERGY_ORB_DAMAGE)
                        
                        # Créer des particules d'explosion
                        self.create_explosion_particles(orb.x, orb.y)
                        
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += 20  # Encore plus de points pour les boules d'énergie
                        break
    
    def spawn_enemy(self):
        """Fait apparaître un ennemi sur le bord de l'écran"""
        side = random.randint(0, 3)  # 0=haut, 1=droite, 2=bas, 3=gauche
        
        if side == 0:  # Haut
            x = random.randint(0, self.config.WINDOW_WIDTH - self.config.ENEMY_SIZE)
            y = -self.config.ENEMY_SIZE
        elif side == 1:  # Droite
            x = self.config.WINDOW_WIDTH
            y = random.randint(0, self.config.WINDOW_HEIGHT - self.config.ENEMY_SIZE)
        elif side == 2:  # Bas
            x = random.randint(0, self.config.WINDOW_WIDTH - self.config.ENEMY_SIZE)
            y = self.config.WINDOW_HEIGHT
        else:  # Gauche
            x = -self.config.ENEMY_SIZE
            y = random.randint(0, self.config.WINDOW_HEIGHT - self.config.ENEMY_SIZE)
        
        # Augmenter la santé des ennemis avec les vagues
        enemy_health = self.config.ENEMY_HEALTH + (self.wave_number - 1) * 5
        
        enemy = Enemy(x, y, self.config)
        enemy.health = enemy_health
        enemy.max_health = enemy_health
        
        # Augmenter la vitesse des ennemis avec les vagues
        enemy.speed *= (1 + (self.wave_number - 1) * 0.1)
        
        self.enemies.append(enemy)
    
    def auto_fire(self):
        """Tire automatiquement vers l'ennemi le plus proche"""
        if not self.enemies:
            return
        
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Trouver l'ennemi le plus proche (optimisé)
        min_distance_sq = float('inf')
        closest_enemy = None
        
        for enemy in self.enemies:
            dx = enemy.x - player_center_x
            dy = enemy.y - player_center_y
            distance_sq = dx * dx + dy * dy  # Éviter sqrt pour la performance
            
            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                closest_enemy = enemy
        
        if closest_enemy:
            # Calculer la direction vers l'ennemi
            dx = closest_enemy.x - player_center_x
            dy = closest_enemy.y - player_center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                # Normaliser la direction
                dx /= distance
                dy /= distance
                
                # Créer le zap
                zap = Zap(player_center_x, player_center_y, dx, dy, self.config)
                self.zaps.append(zap)
    
    def auto_lightning(self):
        """Lance un éclair automatique si un ennemi est à portée"""
        if not self.enemies:
            return
        
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Trouver les ennemis à portée
        enemies_in_range = []
        for enemy in self.enemies:
            enemy_center_x = enemy.x + enemy.size // 2
            enemy_center_y = enemy.y + enemy.size // 2
            
            distance = math.sqrt((enemy_center_x - player_center_x)**2 + 
                               (enemy_center_y - player_center_y)**2)
            
            if distance <= self.config.LIGHTNING_RANGE:
                enemies_in_range.append(enemy)
        
        if enemies_in_range:
            # Choisir un ennemi aléatoire dans la portée
            primary_target = random.choice(enemies_in_range)
            
            # Traiter l'éclair principal
            self.process_lightning_strike(player_center_x, player_center_y, primary_target, True)
    
    def process_lightning_strike(self, start_x, start_y, target, is_primary=False):
        """Traite un éclair individuel et gère le chaînage"""
        if not target or target not in self.enemies:
            return
        
        target_x = target.x + target.size // 2
        target_y = target.y + target.size // 2
        
        # Créer l'éclair visuel
        lightning = Lightning(start_x, start_y, target_x, target_y, self.config, not is_primary)
        self.lightnings.append(lightning)
        
        # Infliger des dégâts
        target.take_damage(self.config.LIGHTNING_DAMAGE)
        
        # Créer les particules d'explosion
        self.create_explosion_particles(target_x, target_y)
        
        # Points et suppression si mort
        if target.health <= 0:
            self.enemies.remove(target)
            self.score += 15 if is_primary else 10  # Moins de points pour les cibles secondaires
        
        # Chaînage uniquement pour l'éclair principal
        if is_primary and random.random() < self.config.LIGHTNING_CHAIN_CHANCE:
            # Chercher un second ennemi à portée de chaînage
            secondary_targets = []
            for enemy in self.enemies:
                if enemy == target:  # Ne pas cibler le même ennemi
                    continue
                
                enemy_center_x = enemy.x + enemy.size // 2
                enemy_center_y = enemy.y + enemy.size // 2
                
                # Distance depuis la cible primaire
                distance = math.sqrt((enemy_center_x - target_x)**2 + 
                                   (enemy_center_y - target_y)**2)
                
                if distance <= self.config.LIGHTNING_CHAIN_RANGE:
                    secondary_targets.append(enemy)
            
            if secondary_targets:
                # Choisir la cible secondaire la plus proche
                secondary_target = min(secondary_targets, key=lambda e: 
                    math.sqrt((e.x + e.size//2 - target_x)**2 + (e.y + e.size//2 - target_y)**2))
                
                # Traiter l'éclair secondaire (sans chaînage supplémentaire)
                self.process_lightning_strike(target_x, target_y, secondary_target, False)
    
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
        self.screen.fill(self.config.BLACK)
        
        if not self.game_over:
            # Dessiner les entités (ordre d'arrière-plan vers premier plan)
            
            # Dessiner les ennemis en premier
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Dessiner les projectiles
            for zap in self.zaps:
                zap.draw(self.screen)
            
            # Dessiner les éclairs (derrière le joueur)
            for lightning in self.lightnings:
                lightning.draw(self.screen)
            
            # Dessiner les particules
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Dessiner les boules d'énergie
            for orb in self.energy_orbs:
                orb.draw(self.screen)
            
            # Dessiner le joueur EN DERNIER (au premier plan)
            self.player.draw(self.screen)
        
        # Interface utilisateur
        self.draw_ui()
        
        if self.paused:
            self.draw_pause_screen()
        elif self.game_over:
            self.draw_game_over_screen()
        
        pygame.display.flip()
    
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
        self.enemies_per_wave = 5
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 120
        self.fire_timer = 0
        self.lightning_timer = 0  # Nouveau
        
        # Réinitialiser les capacités
        self.current_energy_orb_max = self.config.ENERGY_ORB_MAX_COUNT_BASE
        self.current_lightning_fire_rate = self.config.LIGHTNING_FIRE_RATE_BASE
        
        # Réinitialiser le joueur
        self.player = Player(
            self.config.WINDOW_WIDTH // 2,
            self.config.WINDOW_HEIGHT // 2,
            self.config
        )
        
        # Vider les listes
        self.enemies.clear()
        self.zaps.clear()
        self.lightnings.clear()  # Nouveau
        self.particles.clear()   # Nouveau
        self.energy_orbs.clear()  # Nouveau
        
        # Créer les orbes d'énergie initiales
        self.recreate_all_energy_orbs()
    
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
