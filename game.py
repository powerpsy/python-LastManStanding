import pygame
import random
import math
from entities import Player, Enemy, Zap, Lightning, Particle, EnergyOrb, BonusManager, Beam
from background import Background
from weapons import WeaponManager, SkillManager, CannonWeapon, LightningWeapon, OrbWeapon, BeamWeapon, SpeedSkill, ShieldSkill, RegenSkill

class Game:
    """Classe principale du jeu"""
    
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)
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
        self.show_exit_menu = False  # Nouvel état pour la fenêtre de sortie
        
        # Entités
        self.player = Player(
            config.WINDOW_WIDTH // 2,
            config.WINDOW_HEIGHT // 2,
            config
        )
        self.enemies = []
        self.zaps = []
        self.lightnings = []  # Nouvelle liste pour les éclairs
        self.beams = []       # Nouvelle liste pour les rayons laser
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
        self.lightning_timer = 0  # Nouveau timer pour les lightning
        
        # Nouveau système d'armes et compétences orienté objet
        self.weapon_manager = WeaponManager()  # Commence avec le canon
        self.skill_manager = SkillManager()    # Commence sans compétences
        
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
        
        # Système de progression
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        
        # Initialisation du background
        self.background = Background(config)
        
        # Gestionnaire de bonus
        self.bonus_manager = BonusManager(config)
        
        # === STATISTIQUES DE JEU ===
        self.game_start_time = pygame.time.get_ticks()  # Temps de début en millisecondes
        self.enemies_killed = 0  # Nombre d'ennemis tués
        self.max_level_reached = 1  # Niveau maximum atteint
    
    def handle_events(self):
        """Gère les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.VIDEORESIZE:
                # Gestion du redimensionnement de la fenêtre
                self.handle_window_resize(event.w, event.h)
            if self.show_upgrade_screen:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    # Boutons (agrandis)
                    btn_w, btn_h = 180, 72  # Agrandis pour correspondre à draw_upgrade_screen
                    screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
                    btn_y = screen_h//2 + 120
                    roll_rect = pygame.Rect(screen_w//2-300, btn_y, btn_w, btn_h)  # Position ajustée
                    ban_rect = pygame.Rect(screen_w//2-90, btn_y, btn_w, btn_h)   # Position ajustée
                    skip_rect = pygame.Rect(screen_w//2+120, btn_y, btn_w, btn_h)  # Position ajustée
                    
                    # Sélection d'une option d'upgrade (clic sur les options)
                    if not self.ban_mode:
                        for i, rect in enumerate(self.get_upgrade_option_rects()):
                            if rect.collidepoint(mx, my):
                                # Appliquer l'upgrade sélectionné
                                selected_upgrade = self.upgrade_options[i]
                                print(f"✨ Upgrade sélectionné: {selected_upgrade['name']}")
                                self.apply_upgrade(selected_upgrade)
                                # Fermer l'écran d'upgrade
                                self.show_upgrade_screen = False
                                self.paused = False
                                self.ban_mode = False
                                return
                    
                    # ROLL
                    if roll_rect.collidepoint(mx, my) and self.roll_count > 0 and not self.ban_mode:
                        self.upgrade_options = self.get_smart_upgrade_options()
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
            
            elif event.type == pygame.KEYDOWN:
                # Gestion de la fenêtre de compétences
                if self.paused_skills:
                    if event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
                        self.paused_skills = False
                        self.paused = False
                        return
                # Gestion de la fenêtre de sortie
                elif self.show_exit_menu:
                    if event.key == pygame.K_ESCAPE:
                        self.show_exit_menu = False
                        self.paused = False
                        return
                # Ouverture de la fenêtre de compétences
                elif event.key == pygame.K_TAB and not self.show_exit_menu and not self.show_upgrade_screen:
                    self.paused_skills = True
                    self.paused = True
                    return
                # Ouverture du menu de sortie
                elif event.key == pygame.K_ESCAPE and not self.paused_skills and not self.show_upgrade_screen and not self.show_exit_menu:
                    self.show_exit_menu = True
                    self.paused = True
                    return
            
            # Menu de sortie : détection des clics sur les boutons
            elif self.show_exit_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if hasattr(self, "exit_menu_btn_rects"):
                    for i, rect in enumerate(self.exit_menu_btn_rects):
                        if rect.collidepoint(mx, my):
                            if i == 0:  # QUIT
                                self.running = False
                            elif i == 1:  # RESTART
                                self.show_exit_menu = False
                                self.paused = False
                                self.restart_game()
                            elif i == 2:  # OPTION
                                # À compléter : ouvrir un menu d'options si besoin
                                pass
                            return

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
            
            # Déclencher l'écran d'upgrade seulement à partir de la vague 3
            if self.wave_number >= 3:
                self.trigger_upgrade_screen()
            
            # Réduction du délai entre les ennemis (plus difficile)
            reduction_factor = self.config.ENEMY_SPAWN_DELAY_REDUCTION ** (self.wave_number - 1)
            self.enemy_spawn_delay = max(
                self.min_spawn_delay,
                int(self.base_spawn_delay * reduction_factor)
            )
            
            print(f"Vague {self.wave_number} - {self.enemies_per_wave} ennemis")
            
            # Affichage des armes et compétences du nouveau système
            weapons = self.weapon_manager.get_weapon_list()
            skills = self.skill_manager.get_skill_list()
            
            weapon_names = [f"{w['name']} Niv.{w['level']}" for w in weapons]
            skill_names = [f"{s['name']} Niv.{s['level']}" for s in skills]
            
            print(f"Armes ({len(weapons)}/7): {', '.join(weapon_names) if weapons else 'Aucune'}")
            print(f"Compétences ({len(skills)}/14): {', '.join(skill_names) if skills else 'Aucune'}")
        
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
        
        # Nouveau système d'armes orienté objet
        self.weapon_manager.update_all(self.config)
        
        # Pour chaque arme, on utilise la liste de projectiles appropriée
        for weapon in self.weapon_manager.weapons:
            if weapon.is_active:
                if weapon.name == "Canon":  # CORRIGÉ: "Canon" au lieu de "Cannon"
                    weapon.fire(self.player, self.enemies, self.zaps, self.config)
                elif weapon.name == "Lightning":
                    hit_positions = weapon.fire(self.player, self.enemies, self.lightnings, self.config)
                    # Créer des effets d'explosion pour chaque ennemi touché
                    if hit_positions:
                        for x, y in hit_positions:
                            self.create_explosion_particles(x, y)
                elif weapon.name == "Beam":
                    weapon.fire(self.player, self.enemies, self.beams, self.config)
                elif weapon.name == "Orb":
                    # Les orb ne tirent pas de projectiles, elles orbitent
                    weapon.update_orbs(self.player.x, self.player.y, self.player.size)
        
        # Appliquer les effets des compétences passives
        self.skill_manager.apply_all_effects(self.player, self.config)
        
        # Vérification de sécurité : s'assurer d'avoir le bon nombre d'orb (uniquement si débloqué)
        self.ensure_correct_orb_count()
        
        # Nettoyer toutes les entités (optimisé)
        self.cleanup_entities()
    
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
        
        # Créer l'ennemi (avec chance d'être spécial et progression par vague)
        is_special = random.random() < self.config.SPECIAL_ENEMY_SPAWN_CHANCE
        enemy = Enemy(x, y, self.config, is_special, self.wave_number)
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
    
    def handle_window_resize(self, new_width, new_height):
        """Gère le redimensionnement de la fenêtre"""
        # Tailles minimales pour éviter des fenêtres trop petites
        min_width, min_height = 800, 600
        new_width = max(min_width, new_width)
        new_height = max(min_height, new_height)
        
        # Mettre à jour la configuration
        old_width = self.config.WINDOW_WIDTH
        old_height = self.config.WINDOW_HEIGHT
        
        self.config.WINDOW_WIDTH = new_width
        self.config.WINDOW_HEIGHT = new_height
        self.config.SCREEN_WIDTH = new_width
        self.config.SCREEN_HEIGHT = new_height
        
        # Recalculer les éléments adaptatifs
        self.config.recalculate_adaptive_sizes()
        
        # Recréer la surface d'affichage
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        
        # Recalculer les polices avec la nouvelle échelle
        self.font = pygame.font.Font(None, int(36 * self.config.font_scale))
        self.small_font = pygame.font.Font(None, int(24 * self.config.font_scale))
        
        # Ajuster la position de la caméra pour maintenir le centrage
        camera_offset_x = (new_width - old_width) // 2
        camera_offset_y = (new_height - old_height) // 2
        self.camera_x -= camera_offset_x
        self.camera_y -= camera_offset_y
        
        # Recreer les orb avec les nouvelles dimensions
        if hasattr(self, 'energy_orbs') and self.energy_orbs:
            self.energy_orbs.clear()
            self.recreate_all_energy_orbs()
        
        print(f"Fenêtre redimensionnée: {new_width}x{new_height}")
    
    def update_abilities_progression(self):
        """Met à jour les capacités du joueur - Évolution manuelle via upgrades seulement"""
        # L'évolution des armes se fait maintenant uniquement via le système d'upgrades
        # Plus d'évolution automatique !
        pass
    
    def auto_fire(self):
        """Tire automatiquement vers l'ennemi le plus proche"""
        if not self.enemies:
            return
        
        # Portée maximale du canon : 10 tiles (320 pixels) - un peu plus que les lightning
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
        
        # Créer un projectile de canon
        enemy_center_x = closest_enemy.x + closest_enemy.size // 2
        enemy_center_y = closest_enemy.y + closest_enemy.size // 2
        
        # Calculer la direction normalisée
        direction_x = enemy_center_x - player_center_x
        direction_y = enemy_center_y - player_center_y
        direction_length = math.sqrt(direction_x**2 + direction_y**2)
        
        if direction_length > 0:
            direction_x /= direction_length
            direction_y /= direction_length
        
        zap = Zap(player_center_x, player_center_y, direction_x, direction_y, self.config)
        self.zaps.append(zap)
    
    def auto_lightning(self):
        """Tire automatiquement des lightning vers plusieurs ennemis"""
        if not self.enemies:
            return
        
        # Trouver l'ennemi le plus proche dans la portée des lightning
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Portée maximale du lightning : 8 tiles (256 pixels)
        lightning_range = 384  # Augmenté de 320 à 384 (12 tiles au lieu de 10)
        
        # Filtrer les ennemis dans la portée
        enemies_in_range = [e for e in self.enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= lightning_range]
        
        if not enemies_in_range:
            return  # Aucun ennemi dans la portée
        
        # Trouver l'ennemi le plus proche parmi ceux dans la portée
        closest_enemy = min(enemies_in_range, key=lambda e: 
            math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2))
        
        # Créer un lightning
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
            
            # Créer un lightning vers la cible suivante
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
                    self.enemies_killed += 1  # Incrémenter les statistiques
                self.score += self.config.SCORE_PER_LIGHTNING_KILL  # Plus de points pour les lightning
    
    def create_explosion_particles(self, x, y):
        """Crée des particules d'explosion à la position donnée"""
        for _ in range(self.config.PARTICLE_COUNT):
            particle = Particle(x, y, self.config)
            self.particles.append(particle)
    
    def check_collision(self, obj1, obj2):
        """Vérifie la collision circulaire entre deux objets"""
        # Calculer les centres des objets
        obj1_center_x = obj1.x + obj1.size // 2
        obj1_center_y = obj1.y + obj1.size // 2
        obj2_center_x = obj2.x + obj2.size // 2
        obj2_center_y = obj2.y + obj2.size // 2
        
        # Calculer la distance entre les centres
        distance = math.sqrt((obj1_center_x - obj2_center_x)**2 + (obj1_center_y - obj2_center_y)**2)
        
        # Rayons des cercles (rayon = largeur du sprite / 2)
        obj1_radius = obj1.size // 2  # Pour un sprite 32x32, rayon = 16
        obj2_radius = obj2.size // 2  # Pour un sprite 32x32, rayon = 16
        
        # Collision si la distance est inférieure à la somme des rayons
        return distance < (obj1_radius + obj2_radius)
    
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

        if self.show_exit_menu:
            self.draw_exit_menu()
            pygame.display.flip()
            return
        
        # Utiliser les coordonnées de caméra avec délai
        camera_x = self.camera_x
        camera_y = self.camera_y
        
        # Dessiner l'arrière-plan procédural en premier
        self.background.draw(self.screen, camera_x, camera_y)
        
        if not self.game_over:
            # Dessiner toutes les entités
            self.draw_entities(camera_x, camera_y)
        
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

    def draw_exit_menu(self):
        """Dessine le menu de sortie avec boutons cliquables"""
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(160)
        overlay.fill((20, 20, 20))
        self.screen.blit(overlay, (0, 0))

        # Titre
        title = "Menu de sortie"
        title_surface = self.font.render(title, True, self.config.WHITE)
        title_rect = title_surface.get_rect(center=(screen_w//2, screen_h//2 - 120))
        self.screen.blit(title_surface, title_rect)

        # Boutons
        btn_w, btn_h = 220, 60
        btn_margin = 40
        btn_names = ["QUIT", "RESTART", "OPTION"]
        btn_rects = []
        for i, name in enumerate(btn_names):
            rect = pygame.Rect(
                screen_w//2 - btn_w//2,
                screen_h//2 - btn_h//2 + i*(btn_h + btn_margin),
                btn_w, btn_h
            )
            btn_rects.append(rect)
            color = (200, 60, 60) if name == "QUIT" else (60, 200, 120) if name == "RESTART" else (60, 120, 200)
            pygame.draw.rect(self.screen, color, rect, border_radius=14)
            text_surface = self.font.render(name, True, self.config.WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

        # Stocker les rects pour la détection dans handle_events
        self.exit_menu_btn_rects = btn_rects

    def draw_ui(self):
        """Dessine l'interface utilisateur"""
        # Calculer le ratio de santé et la couleur
        health_ratio = self.player.health / self.player.max_health
        if health_ratio > 0.7:
            health_color = self.config.GREEN
        elif health_ratio > 0.3:
            health_color = self.config.YELLOW
        else:
            health_color = self.config.RED
        
        # Calculer les dimensions et position centrée de la barre de vie (2x plus grande)
        health_bar_width = self.config.HEALTH_BAR_WIDTH * 2
        health_bar_height = self.config.HEALTH_BAR_HEIGHT * 2
        health_bar_x = (self.config.WINDOW_WIDTH - health_bar_width) // 2
        health_bar_y = 10  # Plus proche du haut de l'écran
        
        # Fond de la barre de santé
        health_bg_rect = pygame.Rect(health_bar_x, health_bar_y, health_bar_width, health_bar_height)
        pygame.draw.rect(self.screen, self.config.GRAY, health_bg_rect)
        
        # Barre de santé actuelle
        health_width = int(health_bar_width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(health_bar_x, health_bar_y, health_width, health_bar_height)
            pygame.draw.rect(self.screen, health_color, health_rect)
        
        # Contour de la barre
        pygame.draw.rect(self.screen, self.config.WHITE, health_bg_rect, 2)
        
        wave_text = f"Vague {self.wave_number} - Ennemis: {len(self.enemies)}"
        wave_surface = self.font.render(wave_text, True, self.config.WHITE)
        self.screen.blit(wave_surface, (10, 60))
        
        # Afficher les armes du joueur (sans caractères spéciaux, avec espacement)
        weapons_text = f"ARMES ({len(self.weapon_manager.weapons)}/7):"
        weapons_surface = self.small_font.render(weapons_text, True, self.config.CYAN)
        self.screen.blit(weapons_surface, (10, 85))
        
        y_offset = 105  # Espacement augmenté
        for weapon in self.weapon_manager.weapons:
            weapon_text = f"  {weapon.name} Niv.{weapon.level}"
            weapon_surface = self.small_font.render(weapon_text, True, self.config.WHITE)
            self.screen.blit(weapon_surface, (10, y_offset))
            y_offset += 40  # Espacement doublé de 20 à 40
        
        # Afficher les compétences du joueur (sans caractères spéciaux, avec espacement)
        y_offset += 20  # Espacement avant section augmenté
        skills_text = f"COMPETENCES ({len(self.skill_manager.skills)}/14):"
        skills_surface = self.small_font.render(skills_text, True, self.config.PURPLE)
        self.screen.blit(skills_surface, (10, y_offset))
        y_offset += 40  # Espacement doublé de 20 à 40
        
        for skill in self.skill_manager.skills:
            skill_text = f"  {skill.name} Niv.{skill.level}"
            skill_surface = self.small_font.render(skill_text, True, self.config.WHITE)
            self.screen.blit(skill_surface, (10, y_offset))
            y_offset += 40  # Espacement doublé de 20 à 40
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, self.config.WHITE)
        score_rect = score_surface.get_rect()
        score_rect.topright = (self.config.WINDOW_WIDTH - 10, 10)
        self.screen.blit(score_surface, score_rect)
        
        # Afficher les bonus actifs
        y_offset += 20
        for bonus_type, frames_left in self.bonus_manager.active_bonuses.items():
            seconds_left = frames_left / 60
            bonus_text = f"{bonus_type.replace('_', ' ').title()}: {seconds_left:.1f}s"
            bonus_surface = self.small_font.render(bonus_text, True, self.config.YELLOW)
            self.screen.blit(bonus_surface, (10, y_offset))
            y_offset += 40  # Espacement doublé de 20 à 40
        
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
        """Dessine l'écran de game over avec les statistiques"""
        # Overlay rouge semi-transparent
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(self.config.RED)
        self.screen.blit(overlay, (0, 0))
        
        # === TITRE ===
        game_over_text = "GAME OVER"
        game_over_surface = self.font.render(game_over_text, True, self.config.WHITE)
        game_over_rect = game_over_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 60))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # === STATISTIQUES PRINCIPALES ===
        y_offset = 120
        
        # Temps de jeu
        game_time_ms = pygame.time.get_ticks() - self.game_start_time
        minutes = game_time_ms // 60000
        seconds = (game_time_ms % 60000) // 1000
        time_text = f"Temps de jeu: {minutes:02d}:{seconds:02d}"
        time_surface = self.small_font.render(time_text, True, self.config.WHITE)
        time_rect = time_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(time_surface, time_rect)
        y_offset += 30
        
        # Score final
        score_text = f"Score Final: {self.score}"
        score_surface = self.small_font.render(score_text, True, self.config.WHITE)
        score_rect = score_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(score_surface, score_rect)
        y_offset += 30
        
        # Niveau atteint
        level_text = f"Niveau atteint: {max(self.level, self.max_level_reached)}"
        level_surface = self.small_font.render(level_text, True, self.config.WHITE)
        level_rect = level_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(level_surface, level_rect)
        y_offset += 30
        
        # Vague atteinte
        wave_text = f"Vague atteinte: {self.wave_number}"
        wave_surface = self.small_font.render(wave_text, True, self.config.WHITE)
        wave_rect = wave_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(wave_surface, wave_rect)
        y_offset += 30
        
        # Ennemis tués
        enemies_text = f"Ennemis éliminés: {self.enemies_killed}"
        enemies_surface = self.small_font.render(enemies_text, True, self.config.WHITE)
        enemies_rect = enemies_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(enemies_surface, enemies_rect)
        y_offset += 50
        
        # === ARMES ACQUISES ===
        weapons_title = f"ARMES ({len(self.weapon_manager.weapons)}/7):"
        weapons_title_surface = self.small_font.render(weapons_title, True, self.config.CYAN)
        weapons_title_rect = weapons_title_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(weapons_title_surface, weapons_title_rect)
        y_offset += 25
        
        for weapon in self.weapon_manager.weapons:
            weapon_text = f"• {weapon.name} Niveau {weapon.level}"
            weapon_surface = self.small_font.render(weapon_text, True, self.config.WHITE)
            weapon_rect = weapon_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
            self.screen.blit(weapon_surface, weapon_rect)
            y_offset += 20
        
        y_offset += 20
        
        # === COMPÉTENCES ACQUISES ===
        skills_title = f"COMPÉTENCES ({len(self.skill_manager.skills)}/14):"
        skills_title_surface = self.small_font.render(skills_title, True, self.config.PURPLE)
        skills_title_rect = skills_title_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
        self.screen.blit(skills_title_surface, skills_title_rect)
        y_offset += 25
        
        if len(self.skill_manager.skills) == 0:
            no_skills_text = "Aucune compétence acquise"
            no_skills_surface = self.small_font.render(no_skills_text, True, (128, 128, 128))
            no_skills_rect = no_skills_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
            self.screen.blit(no_skills_surface, no_skills_rect)
            y_offset += 20
        else:
            for skill in self.skill_manager.skills:
                skill_text = f"• {skill.name} Niveau {skill.level}"
                skill_surface = self.small_font.render(skill_text, True, self.config.WHITE)
                self.screen.blit(skill_surface, (self.config.WINDOW_WIDTH//2 - 100, y_offset))
                y_offset += 20
        
        # === INSTRUCTIONS ===
        y_offset += 30
        restart_text = "R - Recommencer    ESC - Quitter"
        restart_surface = self.small_font.render(restart_text, True, self.config.WHITE)
        restart_rect = restart_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, y_offset))
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
        self.lightning_timer = 0
        
        # === RÉINITIALISER LE SYSTÈME DE PROGRESSION ===
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.upgrade_options = []
        self.show_upgrade_screen = False
        self.ban_mode = False
        self.roll_count = 3
        self.ban_count = 1
        
        # === RÉINITIALISER LES GESTIONNAIRES D'ARMES ET COMPÉTENCES ===
        self.weapon_manager = WeaponManager()  # Recommence avec juste le canon
        self.skill_manager = SkillManager()    # Recommence sans compétences
        
        # === RÉINITIALISER LES STATISTIQUES ===
        self.game_start_time = pygame.time.get_ticks()
        self.enemies_killed = 0
        self.max_level_reached = 1
        
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
        self.beams.clear()       # Nouveau
        self.particles.clear()   # Nouveau
        self.energy_orbs.clear()  # Nouveau
        
        # Créer les orb initiales
        self.recreate_all_energy_orbs()
        
        # Réinitialiser le gestionnaire de bonus
        self.bonus_manager = BonusManager(self.config)
        
        print("🔄 RESTART: Jeu complètement réinitialisé !")
        print(f"   📊 Niveau: {self.level}, XP: {self.xp}/{self.xp_to_next_level}")
        print(f"   ⚔️ Armes: {len(self.weapon_manager.weapons)}/7")
        print(f"   🎯 Compétences: {len(self.skill_manager.skills)}/14")
        print(f"   🎲 Bans disponibles: {self.ban_count}")
    
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)
    
    def ensure_correct_orb_count(self):
        """S'assure que le joueur a le bon nombre d'orb selon son niveau (uniquement si débloqué)"""
        # Vérifier si les orb sont débloquées
        if not self.weapon_manager.has_weapon("Orb"):
            # Si les orb ne sont pas débloquées, supprimer toutes les orb existantes
            if len(self.energy_orbs) > 0:
                self.energy_orbs.clear()
            return
        
        # Laisser le système OOP gérer les orbes via OrbWeapon
        orb_weapon = None
        for weapon in self.weapon_manager.weapons:
            if weapon.name == "Orb":
                orb_weapon = weapon
                break
        
        if orb_weapon:
            # Synchroniser la liste legacy avec les orbes OOP
            self.energy_orbs = orb_weapon.orbs
    
    def recreate_all_energy_orbs(self):
        """Méthode legacy - maintenant gérée par OrbWeapon"""
        # Cette méthode n'est plus nécessaire avec le système OOP
        pass
    
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
        # Overlay semi-transparent (75% de transparence sur 3/4 de l'écran)
        overlay_width = int(self.config.WINDOW_WIDTH * 0.75)
        overlay_height = int(self.config.WINDOW_HEIGHT * 0.75)
        overlay_x = (self.config.WINDOW_WIDTH - overlay_width) // 2
        overlay_y = (self.config.WINDOW_HEIGHT - overlay_height) // 2
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.fill((20, 20, 40))
        overlay.set_alpha(192)  # 75% de 255 = 192 (plus opaque et lisible)
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
        self.upgrade_options = self.get_smart_upgrade_options()
    
    def get_upgrade_option_rects(self):
        # Retourne les rects des 3 options pour la détection (boutons agrandis x2)
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        opt_w, opt_h = 440, 128  # Agrandis x2 : 220->440, 64->128
        y = screen_h//2 - 80
        return [pygame.Rect(screen_w//2-660+i*480, y, opt_w, opt_h) for i in range(3)]
    
    def draw_upgrade_screen(self):
        """Affiche l'écran de choix d'upgrade"""
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        overlay = pygame.Surface((int(screen_w*0.75), int(screen_h*0.75)))
        overlay.fill((60, 60, 80) if not self.ban_mode else (80, 20, 20))
        overlay.set_alpha(51)  # 20% de transparence
        overlay_x = (screen_w - overlay.get_width()) // 2
        overlay_y = (screen_h - overlay.get_height()) // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))
        # Titre (sans caractères spéciaux)
        title = "Choisissez une amelioration" if not self.ban_mode else "Bannissez une option"
        title_surface = self.font.render(title, True, self.config.WHITE)
        title_rect = title_surface.get_rect(center=(screen_w//2, overlay_y+60))
        self.screen.blit(title_surface, title_rect)
        # Options (boutons agrandis avec texte adapté)
        for i, option in enumerate(self.upgrade_options):
            rect = self.get_upgrade_option_rects()[i]
            
            # Couleur spéciale pour les nouvelles armes
            if option.get("is_new_weapon", False):
                # Jaune doré pour les nouvelles armes
                color = (255, 215, 0) if not self.ban_mode else (255, 180, 100)
            else:
                color = (180,220,255) if not self.ban_mode else (255,120,120)
                
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            
            # Texte adapté à la taille des boutons (police plus petite ou 2 lignes)
            text_color = self.config.BLACK if not option.get("is_new_weapon", False) else (139, 69, 19)
            
            # Diviser le texte en 2 lignes si trop long
            name = option["name"]
            if len(name) > 15:  # Si le texte est trop long
                # Chercher un point de coupure naturel
                words = name.split()
                if len(words) > 1:
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])
                    line2 = " ".join(words[mid:])
                    
                    # Afficher sur 2 lignes
                    line1_surface = self.small_font.render(line1, True, text_color)
                    line2_surface = self.small_font.render(line2, True, text_color)
                    
                    line1_rect = line1_surface.get_rect(center=(rect.centerx, rect.centery - 12))
                    line2_rect = line2_surface.get_rect(center=(rect.centerx, rect.centery + 12))
                    
                    self.screen.blit(line1_surface, line1_rect)
                    self.screen.blit(line2_surface, line2_rect)
                else:
                    # Une seule ligne avec police plus petite
                    opt_surface = self.small_font.render(name, True, text_color)
                    opt_rect = opt_surface.get_rect(center=rect.center)
                    self.screen.blit(opt_surface, opt_rect)
            else:
                # Texte court, police normale
                opt_surface = self.font.render(name, True, text_color)
                opt_rect = opt_surface.get_rect(center=rect.center)
                self.screen.blit(opt_surface, opt_rect)
        # Boutons ROLL, BAN, SKIP (agrandis)
        btn_w, btn_h = 180, 72  # Agrandis : 120->180, 48->72
        btn_y = screen_h//2 + 120
        # ROLL
        roll_rect = pygame.Rect(screen_w//2-300, btn_y, btn_w, btn_h)  # Position ajustée
        roll_color = (200,200,200) if self.roll_count > 0 and not self.ban_mode else (100,100,100)
        pygame.draw.rect(self.screen, roll_color, roll_rect, border_radius=10)
        roll_text = f"ROLL ({self.roll_count})"
        roll_surface = self.font.render(roll_text, True, self.config.BLACK)
        roll_rect_center = roll_surface.get_rect(center=roll_rect.center)
        self.screen.blit(roll_surface, roll_rect_center)
        
        # BAN
        ban_rect = pygame.Rect(screen_w//2-90, btn_y, btn_w, btn_h)  # Position ajustée
        ban_color = (200,100,100) if self.ban_count > 0 and not self.ban_mode else (100,50,50)
        pygame.draw.rect(self.screen, ban_color, ban_rect, border_radius=10)
        ban_text = f"BAN ({self.ban_count})"
        ban_surface = self.font.render(ban_text, True, self.config.BLACK)
        ban_rect_center = ban_surface.get_rect(center=ban_rect.center)
        self.screen.blit(ban_surface, ban_rect_center)
        
        # SKIP
        skip_rect = pygame.Rect(screen_w//2+120, btn_y, btn_w, btn_h)  # Position ajustée
        pygame.draw.rect(self.screen, (180,180,180), skip_rect, border_radius=10)
        skip_surface = self.font.render("SKIP", True, self.config.BLACK)
        skip_rect_center = skip_surface.get_rect(center=skip_rect.center)
        self.screen.blit(skip_surface, skip_rect_center)

    def draw_entity_with_camera_offset(self, entity, camera_x, camera_y):
        """Dessine une entité en appliquant l'offset de caméra"""
        entity_screen_x = entity.x - camera_x
        entity_screen_y = entity.y - camera_y
        temp_x, temp_y = entity.x, entity.y
        entity.x, entity.y = entity_screen_x, entity_screen_y
        entity.draw(self.screen)
        entity.x, entity.y = temp_x, temp_y
    
    def draw_entities(self, camera_x, camera_y):
        """Dessine toutes les entités du jeu avec l'offset de caméra"""
        # Dessiner les ennemis en premier
        for enemy in self.enemies:
            self.draw_entity_with_camera_offset(enemy, camera_x, camera_y)
        
        # Dessiner les projectiles de canon
        for zap in self.zaps:
            self.draw_entity_with_camera_offset(zap, camera_x, camera_y)
        
        # Dessiner les lightning (derrière le joueur)
        for lightning in self.lightnings:
            # Les lightning ont leurs propres coordonnées dans leurs points
            lightning.draw(self.screen, camera_x, camera_y)
        
        # Dessiner les beams (rayons laser)
        for beam in self.beams:
            beam.draw(self.screen, camera_x, camera_y)
        
        # Dessiner les particules
        for particle in self.particles:
            self.draw_entity_with_camera_offset(particle, camera_x, camera_y)
        
        # Dessiner les orb
        for orb in self.energy_orbs:
            self.draw_entity_with_camera_offset(orb, camera_x, camera_y)
        
        # Dessiner le joueur EN DERNIER (au premier plan)
        self.draw_entity_with_camera_offset(self.player, camera_x, camera_y)

    def cleanup_entities(self):
        """Nettoie les entités et gère les collisions"""
        margin = 200  # Marge pour garder les projectiles un peu plus longtemps
        camera_bounds = {
            'left': self.camera_x - margin,
            'right': self.camera_x + self.config.WINDOW_WIDTH + margin,
            'top': self.camera_y - margin,
            'bottom': self.camera_y + self.config.WINDOW_HEIGHT + margin
        }
        
        # Mettre à jour et gérer les collisions des zaps
        zaps_to_remove = []
        for zap in self.zaps:
            zap.update()
            
            # Vérifier si hors limites
            if not (camera_bounds['left'] <= zap.x <= camera_bounds['right'] and 
                    camera_bounds['top'] <= zap.y <= camera_bounds['bottom']):
                zaps_to_remove.append(zap)
                continue
            
            # Collision avec les ennemis
            for enemy in self.enemies[:]:
                if self.check_collision(zap, enemy):
                    damage = int(self.config.ZAP_DAMAGE * self.bonus_manager.get_damage_multiplier())
                    enemy.take_damage(damage)
                    zaps_to_remove.append(zap)
                    
                    if enemy.health <= 0:
                        # Appliquer bonus si c'est un ennemi spécial
                        if enemy.is_special and enemy.bonus_type:
                            self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                        
                        # Vérifier que l'ennemi est encore dans la liste
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1  # Incrémenter les statistiques
                        self.score += self.config.SCORE_PER_ENEMY_KILL
                    break
        
        # Supprimer les zaps marqués pour suppression
        for zap in zaps_to_remove:
            if zap in self.zaps:
                self.zaps.remove(zap)
        
        # Nettoyer les éclairs (ils se suppriment automatiquement via update())
        self.lightnings = [lightning for lightning in self.lightnings if lightning.update()]
        
        # Mettre à jour et gérer les collisions des beams
        active_beams = []
        for beam in self.beams:
            if beam.update():
                # Vérifier les collisions avec les ennemis
                hit_positions = beam.check_collision_with_enemies(self.enemies)
                # Créer des effets d'explosion pour chaque ennemi touché
                for x, y in hit_positions:
                    self.create_explosion_particles(x, y)
                active_beams.append(beam)
        self.beams = active_beams
        
        # Nettoyer les particules (elles se suppriment automatiquement via update())
        self.particles = [particle for particle in self.particles if particle.update()]
        
        # Nettoyer les orb et gérer leurs collisions
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Mettre à jour les orb et vérifier les collisions avec les ennemis
        for orb in self.energy_orbs[:]:
            orb.update(player_center_x, player_center_y)
            
            # Vérifier les collisions avec les ennemis
            for enemy in self.enemies[:]:
                if self.check_collision(orb, enemy):
                    # Infliger des dégâts à l'ennemi
                    damage = int(self.config.ENERGY_ORB_DAMAGE * self.bonus_manager.get_damage_multiplier())
                    enemy.take_damage(damage)
                    
                    # Créer des particules à l'impact
                    impact_particles = []
                    for i in range(5):
                        particle = Particle(orb.x, orb.y, self.config)
                        impact_particles.append(particle)
                    self.particles.extend(impact_particles)
                    
                    if enemy.health <= 0:
                        # Appliquer bonus si c'est un ennemi spécial
                        if enemy.is_special and enemy.bonus_type:
                            self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                        
                        # Vérifier que l'ennemi est encore dans la liste
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1  # Incrémenter les statistiques
                        self.score += self.config.SCORE_PER_ENEMY_KILL
                    break  # Une orb ne peut toucher qu'un ennemi à la fois
    
    def apply_upgrade(self, upgrade):
        """Applique l'upgrade sélectionné avec le nouveau système orienté objet"""
        upgrade_id = upgrade["id"]
        
        # === NOUVELLES ARMES ===
        if upgrade_id == "weapon_lightning":
            if self.weapon_manager.add_weapon(LightningWeapon):
                print("LIGHTNING DÉBLOQUÉ ! Nouvelle arme disponible !")
            else:
                print("Impossible d'ajouter Lightning : limite d'armes atteinte")
        
        elif upgrade_id == "weapon_beam":
            if self.weapon_manager.add_weapon(BeamWeapon):
                print("BEAM DÉBLOQUÉ ! Nouvelle arme disponible !")
            else:
                print("Impossible d'ajouter Beam : limite d'armes atteinte")
        
        # === AMÉLIORATIONS D'ARMES ===
        elif upgrade_id.startswith("upgrade_weapon_"):
            weapon_name = upgrade_id.replace("upgrade_weapon_", "").capitalize()
            if self.weapon_manager.upgrade_weapon(weapon_name):
                weapon_info = next((w for w in self.weapon_manager.get_weapon_list() if w['name'] == weapon_name), None)
                if weapon_info:
                    print(f"{weapon_name} amélioré au niveau {weapon_info['level']} !")
            else:
                print(f"Impossible d'améliorer {weapon_name}")
        
        # === NOUVELLES COMPÉTENCES ===
        elif upgrade_id == "skill_speed":
            if self.skill_manager.add_skill(SpeedSkill):
                print("COMPÉTENCE VITESSE DÉBLOQUÉE !")
            else:
                print("Impossible d'ajouter Vitesse : limite de compétences atteinte")
        
        elif upgrade_id == "skill_shield":
            if self.skill_manager.add_skill(ShieldSkill):
                print("COMPÉTENCE BOUCLIER DÉBLOQUÉE !")
            else:
                print("Impossible d'ajouter Bouclier : limite de compétences atteinte")
        
        elif upgrade_id == "skill_regen":
            if self.skill_manager.add_skill(RegenSkill):
                print("COMPÉTENCE RÉGÉNÉRATION DÉBLOQUÉE !")
            else:
                print("Impossible d'ajouter Régénération : limite de compétences atteinte")
        
        # === AMÉLIORATIONS DE COMPÉTENCES ===
        elif upgrade_id.startswith("upgrade_skill_"):
            skill_name = upgrade_id.replace("upgrade_skill_", "").capitalize()
            if self.skill_manager.upgrade_skill(skill_name):
                skill_info = next((s for s in self.skill_manager.get_skill_list() if s['name'] == skill_name), None)
                if skill_info:
                    print(f"{skill_name} amélioré au niveau {skill_info['level']} !")
            else:
                print(f"Impossible d'améliorer {skill_name}")
        
        else:
            print(f"Upgrade non reconnu: {upgrade_id}")
    
    def get_smart_upgrade_options(self):
        """Génère des options d'upgrade intelligentes basées sur le nouveau système d'armes et compétences"""
        available_upgrades = []
        
        # === NOUVELLES ARMES ===
        if not self.weapon_manager.has_weapon("Lightning") and len(self.weapon_manager.weapons) < 7:
            available_upgrades.append({
                "id": "weapon_lightning", 
                "name": "DÉBLOQUER: Lightning", 
                "description": "Nouvelle arme: Lightning instantanés avec chaînage !",
                "is_new_weapon": True
            })
        
        if not self.weapon_manager.has_weapon("Beam") and len(self.weapon_manager.weapons) < 7:
            available_upgrades.append({
                "id": "weapon_beam", 
                "name": "DÉBLOQUER: Beam", 
                "description": "Nouvelle arme: Rayon laser qui traverse les ennemis !",
                "is_new_weapon": True
            })
        
        # === AMÉLIORATIONS D'ARMES EXISTANTES ===
        for weapon in self.weapon_manager.weapons:
            if weapon.level < weapon.max_level:
                available_upgrades.append({
                    "id": f"upgrade_weapon_{weapon.name.lower()}", 
                    "name": f"{weapon.name} Niv.{weapon.level + 1}", 
                    "description": f"Améliore {weapon.name} (actuellement niveau {weapon.level})",
                    "is_new_weapon": False
                })
        
        # === NOUVELLES COMPÉTENCES ===
        if not self.skill_manager.has_skill("Vitesse") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_speed", 
                "name": "COMPÉTENCE: Vitesse", 
                "description": "Nouvelle compétence: Augmente la vitesse de déplacement !",
                "is_new_weapon": True
            })
        
        if not self.skill_manager.has_skill("Bouclier") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_shield", 
                "name": "COMPÉTENCE: Bouclier", 
                "description": "Nouvelle compétence: Protection contre les dégâts !",
                "is_new_weapon": True
            })
        
        if not self.skill_manager.has_skill("Régénération") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_regen", 
                "name": "COMPÉTENCE: Régénération", 
                "description": "Nouvelle compétence: Récupère la vie au fil du temps !",
                "is_new_weapon": True
            })
        
        # === AMÉLIORATIONS DE COMPÉTENCES EXISTANTES ===
        for skill in self.skill_manager.skills:
            if skill.level < skill.max_level:
                available_upgrades.append({
                    "id": f"upgrade_skill_{skill.name.lower()}", 
                    "name": f"{skill.name} Niv.{skill.level + 1}", 
                    "description": f"Améliore {skill.name} (actuellement niveau {skill.level})",
                    "is_new_weapon": False
                })
        
        # Retourner 3 options aléatoirement choisies (ou moins s'il n'y en a pas assez)
        result = random.sample(available_upgrades, min(3, len(available_upgrades)))
        return result
    
    def handle_window_resize(self, new_width, new_height):
        """Gère le redimensionnement de la fenêtre"""
        # Tailles minimales pour éviter des fenêtres trop petites
        min_width, min_height = 800, 600
        new_width = max(min_width, new_width)
        new_height = max(min_height, new_height)
        
        # Mettre à jour la configuration
        old_width = self.config.WINDOW_WIDTH
        old_height = self.config.WINDOW_HEIGHT
        
        self.config.WINDOW_WIDTH = new_width
        self.config.WINDOW_HEIGHT = new_height
        self.config.SCREEN_WIDTH = new_width
        self.config.SCREEN_HEIGHT = new_height
        
        # Recalculer les éléments adaptatifs
        self.config.recalculate_adaptive_sizes()
        
        # Recréer la surface d'affichage
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        
        # Recalculer les polices avec la nouvelle échelle
        self.font = pygame.font.Font(None, int(36 * self.config.font_scale))
        self.small_font = pygame.font.Font(None, int(24 * self.config.font_scale))
        
        # Ajuster la position de la caméra pour maintenir le centrage
        camera_offset_x = (new_width - old_width) // 2
        camera_offset_y = (new_height - old_height) // 2
        self.camera_x -= camera_offset_x
        self.camera_y -= camera_offset_y
        
        # Recreer les orb avec les nouvelles dimensions
        if hasattr(self, 'energy_orbs') and self.energy_orbs:
            self.energy_orbs.clear()
            self.recreate_all_energy_orbs()
        
        print(f"Fenêtre redimensionnée: {new_width}x{new_height}")
