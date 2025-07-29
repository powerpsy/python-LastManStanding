import pygame
import pygame.gfxdraw  # Pour l'antialiasing
import random
import math
from entities import Player, Enemy, Zap, Lightning, Particle, WeldingParticle, EnergyOrb, BonusManager, Beam, DeathEffect, Heart, Coin, EnemyProjectile, OrbDeathEffect, BeamDeathEffect
from background import Background
from weapons import WeaponManager, SkillManager, CannonWeapon, LightningWeapon, OrbWeapon, BeamWeapon, SpeedSkill, RegenSkill, MagnetSkill, ShieldSkill
from transitions import TransitionManager, TRANSITION_TYPES

class Game:
    """Classe principale du jeu"""
    
    def __init__(self, config):
        self.config = config
        # Configurer l'affichage avec antialiasing si disponible
        flags = pygame.RESIZABLE
        if config.ENABLE_ANTIALIASING:
            # Essayer d'activer le multisampling (antialiasing matériel)
            try:
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
            except:
                # Si le multisampling n'est pas disponible, continuer sans
                pass
        
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Last Man Standing")
        self.clock = pygame.time.Clock()
        
        # === CURSEUR PERSONNALISÉ ===
        try:
            # Charger l'image du curseur
            cursor_image = pygame.image.load("assets/player/pointer2.png").convert_alpha()
            # Redimensionner si nécessaire (2x plus gros que la taille de base)
            cursor_size = max(48, int(48 * self.config.font_scale))  # Taille adaptative x2
            cursor_image = pygame.transform.scale(cursor_image, (cursor_size, cursor_size))
            # Créer le curseur avec le hotspot au centre de l'image
            hotspot = (cursor_size // 2, cursor_size // 2)
            cursor = pygame.cursors.Cursor(hotspot, cursor_image)
            pygame.mouse.set_cursor(cursor)
            print(f"Curseur personnalisé chargé: assets/player/pointer.png ({cursor_size}x{cursor_size})")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Impossible de charger le curseur personnalisé: {e}")
            print("Utilisation du curseur par défaut")
        
        # Police adaptative
        self.font = pygame.font.Font(None, int(36 * self.config.font_scale))
        self.small_font = pygame.font.Font(None, int(24 * self.config.font_scale))
        
        # Cache pour les images d'armes et de compétences
        self.weapon_images = {}
        self.skill_images = {}
        self._load_weapon_and_skill_images()
        
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
        self.enemy_projectiles = []  # Nouvelle liste pour les projectiles d'ennemis
        self.lightnings = []  # Nouvelle liste pour les éclairs
        self.beams = []       # Nouvelle liste pour les rayons laser
        self.particles = []   # Nouvelle liste pour les particules
        self.welding_particles = []  # Nouvelle liste pour les particules de soudure du Beam
        self.energy_orbs = []  # Nouvelle liste pour les boules d'énergie
        self.death_effects = []  # Nouvelle liste pour les effets de mort
        self.orb_death_effects = []  # Nouvelle liste pour les effets de mort par orbe
        self.beam_death_effects = []  # Nouvelle liste pour les effets de mort par beam
        self.collectibles = []  # Nouvelle liste pour les objets collectibles
        
        # Système de score
        self.score = 0  # Score total du joueur
        
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
        self.banned_upgrades = []  # Liste des upgrades bannis pour cette partie
        self.always_skip_mode = False  # Mode "Always Skip" activé
        self.roll_count = 3
        self.ban_count = 3
        
        # Système de progression basé sur les pièces
        self.level = 1
        self.coins_collected = 0  # Nombre total de pièces collectées
        self.coins_to_next_level = 5  # Sera corrigé après l'initialisation
        self.progression_animation_timer = 0  # Timer pour l'animation de la barre
        self.progression_bar_progress = 0.0  # Progression actuelle de la barre (0.0 à 1.0)
        self.target_progression = 0.0  # Progression cible pour l'animation
        
        # Anciens champs XP gardés pour compatibilité (mais non utilisés)
        self.xp = 0
        self.xp_to_next_level = 100
        
        # Initialisation du background
        self.background = Background(config)
        
        # Gestionnaire de transitions
        self.transition_manager = TransitionManager(self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        self.transition_manager.set_screen_reference(self.screen)
        self._capture_new_screen = False  # Flag pour capturer le nouvel écran
        self._pre_transition_state = 'game'  # État d'écran avant transition
        
        # Gestionnaire de bonus
        self.bonus_manager = BonusManager(config)
        
        # === STATISTIQUES DE JEU ===
        self.game_start_time = pygame.time.get_ticks()  # Temps de début en millisecondes
        self.game_end_time = None  # Temps de fin (survie) en millisecondes
        self.enemies_killed = 0  # Nombre d'ennemis tués
        self.max_level_reached = 1  # Niveau maximum atteint
        
        # Corriger la valeur de coins_to_next_level - pour le niveau 2, il faut 5 pièces au total
        self.coins_to_next_level = 5  # Pièces nécessaires pour atteindre le niveau 2
    
    def trigger_game_over(self):
        """Déclenche la fin de partie et enregistre le temps de survie"""
        if not self.game_over:  # Éviter de redéclencher
            self.game_over = True
            self.game_end_time = pygame.time.get_ticks()
            print(f"💀 GAME OVER - Temps de survie: {self.get_survival_time_string()}")
    
    def get_survival_time_ms(self):
        """Retourne le temps de survie en millisecondes"""
        if self.game_end_time is not None:
            return self.game_end_time - self.game_start_time
        else:
            # Si le jeu n'est pas fini, retourner le temps actuel
            return pygame.time.get_ticks() - self.game_start_time
    
    def get_survival_time_string(self):
        """Retourne le temps de survie formaté en mm:ss"""
        survival_time_ms = self.get_survival_time_ms()
        minutes = survival_time_ms // 60000
        seconds = (survival_time_ms % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"
    
    def transition_to_upgrade_screen(self):
        """Démarre une transition vers l'écran d'upgrade"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'game'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def show_upgrade():
            self.show_upgrade_screen = True
            self.paused = True
            self.paused_skills = False
            self.ban_mode = False
            self._pre_transition_state = 'upgrade'  # Changer l'état de transition
            
            # Forcer le rendu immédiat du nouvel écran (upgrade)
            self.screen.fill((50, 50, 50))  # Fond
            self.draw_upgrade_screen()  # Dessiner l'écran upgrade
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="wipe_vertical_split",
            duration=self.config.TRANSITION_DURATION,
            on_complete=show_upgrade
        )
    
    def transition_from_upgrade_screen(self):
        """Démarre une transition de retour au jeu depuis l'écran d'upgrade"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'upgrade'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def hide_upgrade():
            self.show_upgrade_screen = False
            self.paused = False
            self.ban_mode = False
            self._pre_transition_state = 'game'  # Changer l'état de transition
            
            # Forcer le rendu immédiat du nouvel écran (jeu)
            self.screen.fill((50, 50, 50))  # Fond
            self._draw_game_screen()  # Dessiner l'écran de jeu
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="wipe_vertical_split_reverse",
            duration=self.config.TRANSITION_DURATION,
            on_complete=hide_upgrade
        )
    
    def transition_to_game_over(self):
        """Démarre une transition vers l'écran de game over"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'game'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def show_game_over():
            self.trigger_game_over()
            self._pre_transition_state = 'game'  # L'écran de game over fait partie du jeu
            
            # Forcer le rendu immédiat du nouvel écran (game over)
            self.screen.fill((50, 50, 50))  # Fond
            self._draw_game_screen()  # Dessiner l'écran de jeu (avec game over)
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="wipe_horizontal_left_to_right",
            duration=self.config.TRANSITION_DURATION,
            on_complete=show_game_over
        )
    
    def transition_to_skills_screen(self):
        """Démarre une transition vers l'écran des compétences"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'game'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def show_skills():
            self.paused_skills = True
            self.paused = True
            self.show_upgrade_screen = False
            self._pre_transition_state = 'skills'  # Changer l'état de transition
            
            # Forcer le rendu immédiat du nouvel écran
            self.screen.fill((50, 50, 50))  # Fond
            self.draw_skills_screen()  # Dessiner l'écran skills
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="diagonal_top_left_to_bottom_right",
            duration=self.config.TRANSITION_DURATION,
            on_complete=show_skills
        )
    
    def calculate_coins_for_level(self, level):
        """Calcule le nombre total cumulé de pièces nécessaires pour atteindre un niveau donné"""
        if level <= 1:
            return 0
        
        total = 0
        for lvl in range(2, level + 1):
            if lvl <= 5:
                # Premiers niveaux : 5, 8, 12, 16, 22
                coins_for_this_level = int(5 + (lvl - 2) * 3 + (lvl - 2) * 0.5)
            elif lvl <= 15:
                # Niveaux intermédiaires
                base = 22  # Coins pour niveau 5
                additional = (lvl - 5) * 4
                coins_for_this_level = int(base + additional)
            else:
                # Niveaux élevés
                base = 62  # Coins pour niveau 15
                additional = (lvl - 15) * 6
                coins_for_this_level = int(base + additional)
            
            total += coins_for_this_level
        
        return total

    def check_level_progression(self):
        """Vérifie si le joueur peut passer au niveau suivant basé sur les pièces collectées"""
        if self.coins_collected >= self.coins_to_next_level:
            # Level up !
            self.level += 1
            self.max_level_reached = max(self.max_level_reached, self.level)
            
            # Calculer les pièces nécessaires pour le prochain niveau en utilisant la méthode centralisée
            self.coins_to_next_level = self.calculate_coins_for_level(self.level + 1)
            
            print(f"🎉 NIVEAU {self.level} ! Prochain niveau: {self.coins_to_next_level} pièces au total")
            
            # Déclencher l'écran d'upgrade
            if not self.always_skip_mode:
                self.trigger_upgrade_screen()
            else:
                print("🚀 Always Skip activé - Level up automatique")
                self.score += 1000  # Bonus de score
        
        # Mettre à jour la progression pour l'animation de la barre
        self.update_progression_animation()
    
    def update_progression_animation(self):
        """Met à jour l'animation de la barre de progression"""
        # Calculer la progression cible (0.0 à 1.0)
        if self.level == 1:
            # Pour le premier niveau, utiliser les pièces collectées directement
            if self.coins_to_next_level > 0:
                self.target_progression = min(1.0, self.coins_collected / self.coins_to_next_level)
            else:
                self.target_progression = 1.0
        else:
            # Pour les niveaux suivants, calculer la progression vers le niveau suivant (level + 1)
            next_level_total_needed = self.calculate_coins_for_level(self.level + 1)
            current_level_total_needed = self.calculate_coins_for_level(self.level)
            coins_needed_this_level = next_level_total_needed - current_level_total_needed
            coins_progress_this_level = self.coins_collected - current_level_total_needed
            
            # Vérification pour éviter la division par zéro
            if coins_needed_this_level > 0:
                self.target_progression = min(1.0, max(0.0, coins_progress_this_level / coins_needed_this_level))
            else:
                self.target_progression = 1.0
        
        # Animation fluide vers la progression cible
        if abs(self.progression_bar_progress - self.target_progression) > 0.001:
            self.progression_bar_progress += (self.target_progression - self.progression_bar_progress) * 0.1
        else:
            self.progression_bar_progress = self.target_progression

    def transition_from_skills_screen(self):
        """Démarre une transition de retour au jeu depuis l'écran des compétences"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'skills'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def hide_skills():
            self.paused_skills = False
            self.paused = False
            self._pre_transition_state = 'game'  # Changer l'état de transition
            
            # Forcer le rendu immédiat du nouvel écran (jeu)
            self.screen.fill((50, 50, 50))  # Fond
            self._draw_game_screen()  # Dessiner l'écran de jeu
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="diagonal_bottom_right_to_top_left", 
            duration=self.config.TRANSITION_DURATION,
            on_complete=hide_skills
        )

    def transition_to_exit_menu(self):
        """Démarre une transition vers le menu de sortie"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'game'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def show_exit():
            self.show_exit_menu = True
            self.paused = True
            self._pre_transition_state = 'exit'  # Changer l'état de transition
            
            # Forcer le rendu immédiat du nouvel écran (exit menu)
            self.screen.fill((50, 50, 50))  # Fond
            self.draw_exit_menu()  # Dessiner l'écran exit
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="fade",
            duration=self.config.TRANSITION_DURATION,
            on_complete=show_exit
        )
    
    def transition_from_exit_menu(self):
        """Démarre une transition de retour au jeu depuis le menu de sortie"""
        # Sauvegarder l'état actuel pour la transition
        self._pre_transition_state = 'exit'
        
        # Capturer l'écran actuel
        self.transition_manager.set_screen_reference(self.screen)
        
        def hide_exit():
            self.show_exit_menu = False
            self.paused = False
            self._pre_transition_state = 'game'  # Changer l'état de transition
            
            # Forcer le rendu immédiat du nouvel écran (jeu)
            self.screen.fill((50, 50, 50))  # Fond
            self._draw_game_screen()  # Dessiner l'écran de jeu
            self.transition_manager.update_new_surface(self.screen)  # Capturer immédiatement
        
        self.transition_manager.start_transition(
            transition_type="fade",
            duration=self.config.TRANSITION_DURATION,
            on_complete=hide_exit
        )

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
                    # Boutons (agrandis) - synchronisé avec draw_upgrade_screen
                    btn_w, btn_h = 180, 72  # Agrandis pour correspondre à draw_upgrade_screen
                    screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
                    overlay_y = (screen_h - int(screen_h*0.75)) // 2  # Position de l'overlay
                    btn_y = overlay_y + 30  # Même position que dans draw_upgrade_screen
                    # Positions centrées par rapport aux upgrades
                    roll_rect = pygame.Rect(screen_w//2-320, btn_y, btn_w, btn_h)  # Recentré
                    ban_rect = pygame.Rect(screen_w//2-90, btn_y, btn_w, btn_h)   # Centre
                    skip_rect = pygame.Rect(screen_w//2+140, btn_y, btn_w, btn_h)  # Recentré
                    
                    # Sélection d'une option d'upgrade (clic sur les cadres englobants)
                    if not self.ban_mode:
                        for i, rect in enumerate(self.get_upgrade_combined_rects()):
                            if rect.collidepoint(mx, my):
                                # Appliquer l'upgrade sélectionné
                                selected_upgrade = self.upgrade_options[i]
                                print(f"✨ Upgrade sélectionné: {selected_upgrade['name']}")
                                self.apply_upgrade(selected_upgrade)
                                # Fermer l'écran d'upgrade avec transition
                                self.transition_from_upgrade_screen()
                                return
                    
                    # ROLL (seulement si des options sont disponibles)
                    if roll_rect.collidepoint(mx, my) and self.roll_count > 0 and not self.ban_mode and len(self.upgrade_options) > 0:
                        self.upgrade_options = self.get_smart_upgrade_options()
                        self.roll_count -= 1
                    # BAN (seulement si des options sont disponibles)
                    elif ban_rect.collidepoint(mx, my) and self.ban_count > 0 and not self.ban_mode and len(self.upgrade_options) > 0:
                        self.ban_mode = True
                        # Changer le background à la prochaine draw
                    # SKIP
                    elif skip_rect.collidepoint(mx, my):
                        self.transition_from_upgrade_screen()
                    # ALWAYS SKIP (seulement si aucune option disponible)
                    elif len(self.upgrade_options) == 0:
                        # Définir le rect du bouton Always Skip
                        always_skip_rect = pygame.Rect(screen_w//2+320, btn_y, btn_w, btn_h)
                        if always_skip_rect.collidepoint(mx, my):
                            print("🚀 Mode 'Always Skip' activé ! Plus d'écrans d'upgrade jusqu'à la fin de la partie.")
                            self.always_skip_mode = True
                            self.transition_from_upgrade_screen()
                    # Sélection d'une option en mode BAN (clic sur les cadres englobants)
                    elif self.ban_mode:
                        for i, rect in enumerate(self.get_upgrade_combined_rects()):
                            if rect.collidepoint(mx, my):
                                # Vérifier qu'il y a assez d'options avant de pop
                                if i < len(self.upgrade_options) and len(self.upgrade_options) > 0:
                                    # Ajouter l'option à la liste des bannis persistants
                                    banned_option = self.upgrade_options[i]
                                    self.banned_upgrades.append(banned_option["name"])
                                    print(f"🚫 Option bannie définitivement: {banned_option['name']}")
                                    
                                    # Retirer l'option de la liste actuelle
                                    self.upgrade_options.pop(i)
                                    self.ban_count -= 1
                                    self.ban_mode = False
                                    # Régénérer les options si la liste devient vide
                                    if len(self.upgrade_options) == 0:
                                        self.upgrade_options = self.get_smart_upgrade_options()
                                        # Si toujours vide, désactiver l'écran d'upgrade
                                        if len(self.upgrade_options) == 0:
                                            print("Plus d'options d'upgrade disponibles !")
                                            self.transition_from_upgrade_screen()
                                else:
                                    print("Erreur: Index d'option invalide pour BAN")
                                    self.ban_mode = False
                                break
                return
            
            elif event.type == pygame.KEYDOWN:
                # Gestion de l'écran d'upgrade
                if self.show_upgrade_screen:
                    if event.key == pygame.K_ESCAPE and not self.transition_manager.is_active:
                        self.transition_from_upgrade_screen()
                        return
                # Gestion de la fenêtre de compétences
                elif self.paused_skills:
                    if event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
                        self.transition_from_skills_screen()
                        return
                # Gestion de la fenêtre de sortie
                elif self.show_exit_menu:
                    if event.key == pygame.K_ESCAPE and not self.transition_manager.is_active:
                        self.transition_from_exit_menu()
                        return
                # Ouverture de la fenêtre de compétences
                elif event.key == pygame.K_TAB and not self.show_exit_menu and not self.show_upgrade_screen:
                    self.transition_to_skills_screen()
                    return
                # Ouverture du menu de sortie
                elif event.key == pygame.K_ESCAPE and not self.paused_skills and not self.show_upgrade_screen and not self.show_exit_menu and not self.transition_manager.is_active:
                    self.transition_to_exit_menu()
                    return
                # Gestion du game over - Restart avec R
                elif self.game_over and event.key == pygame.K_r and not self.transition_manager.is_active:
                    # Transition avant restart
                    def do_restart():
                        self.restart_game()
                    
                    self._pre_transition_state = 'game_over'
                    self.transition_manager.set_screen_reference(self.screen)
                    self.transition_manager.start_transition(
                        transition_type="fade",
                        duration=self.config.TRANSITION_DURATION,
                        on_complete=do_restart
                    )
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
                                # Transition avant restart
                                def do_restart():
                                    self.restart_game()
                                
                                self._pre_transition_state = 'exit'
                                self.transition_manager.set_screen_reference(self.screen)
                                self.transition_manager.start_transition(
                                    transition_type="fade",
                                    duration=self.config.TRANSITION_DURATION,
                                    on_complete=do_restart
                                )
                            elif i == 2:  # OPTION
                                # À compléter : ouvrir un menu d'options si besoin
                                pass
                            return

    def update(self):
        """Met à jour la logique du jeu"""
        # Mettre à jour les transitions (toujours actif)
        self.transition_manager.update()
        
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
            
            # La progression des niveaux est maintenant basée sur les pièces collectées
            # L'ancien système basé sur les vagues a été remplacé
            
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
            
            # Vérifier si l'ennemi tireur doit tirer un projectile
            if enemy.should_fire():
                projectile = EnemyProjectile(
                    enemy.x + enemy.size // 2,
                    enemy.y + enemy.size // 2,
                    self.player.x + self.player.size // 2,
                    self.player.y + self.player.size // 2,
                    self.config
                )
                self.enemy_projectiles.append(projectile)
            
            # Collision avec le joueur
            if self.check_collision(self.player, enemy):
                # Vérifier si le joueur peut subir des dégâts (bouclier, invincibilité)
                if self.bonus_manager.can_take_damage():
                    self.player.take_damage(self.config.ENEMY_DAMAGE, self.skill_manager)
                    if self.player.health <= 0:
                        self.transition_to_game_over()
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
                    # Créer des effets d'explosion renforcés pour chaque ennemi touché par Lightning
                    if hit_positions:
                        for x, y in hit_positions:
                            self.create_lightning_explosion_particles(x, y)
                    
                    # Supprimer les ennemis morts après l'attaque Lightning
                    enemies_to_remove = []
                    for enemy in self.enemies:
                        if enemy.health <= 0:
                            # Créer effet de mort pour les ennemis spéciaux
                            if enemy.is_special:
                                death_effect = DeathEffect(enemy.x, enemy.y, self.config)
                                self.death_effects.append(death_effect)
                            
                            # Appliquer bonus si c'est un ennemi spécial
                            if enemy.is_special and enemy.bonus_type:
                                self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                            enemies_to_remove.append(enemy)
                            self.enemies_killed += 1
                            self.score += self.config.SCORE_PER_LIGHTNING_KILL
                    
                    # Supprimer les ennemis morts de la liste
                    for enemy in enemies_to_remove:
                        if enemy in self.enemies:  # Vérification de sécurité
                            # Gérer les drops avant de supprimer l'ennemi
                            self.handle_enemy_drops(enemy)
                            self.enemies.remove(enemy)
                elif weapon.name == "Beam":
                    weapon.fire(self.player, self.enemies, self.beams, self.config)
                elif weapon.name == "Orb":
                    # Les orb ne tirent pas de projectiles, elles orbitent
                    weapon.update_orbs(self.player.x, self.player.y, self.player.size)
        
        # Appliquer les effets des compétences passives
        self.skill_manager.apply_all_effects(self.player, self.config)
        
        # Vérification de sécurité : s'assurer d'avoir le bon nombre d'orb (uniquement si débloqué)
        self.ensure_correct_orb_count()
        
        # Mettre à jour les collectibles
        self.update_collectibles()
        
        # Mettre à jour l'animation de progression (si nécessaire)
        if hasattr(self, 'progression_animation_timer'):
            self.update_progression_animation()
        
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
        
        # Recalculer les polices avec la nouvelle échelle
        self.font = pygame.font.Font(None, int(36 * self.config.font_scale))
        self.small_font = pygame.font.Font(None, int(24 * self.config.font_scale))
        
        # Ajuster la position de la caméra pour maintenir le centrage
        camera_offset_x = (new_width - old_width) // 2
        camera_offset_y = (new_height - old_height) // 2
        self.camera_x -= camera_offset_x
        self.camera_y -= camera_offset_y
        
        # Les orb sont maintenant gérées par le système OOP de WeaponManager
        # Plus besoin de les recréer manuellement
        
        print(f"Fenêtre redimensionnée: {new_width}x{new_height}")
    
    def update_abilities_progression(self):
        """Met à jour les capacités du joueur - Évolution manuelle via upgrades seulement"""
        # L'évolution des armes se fait maintenant uniquement via le système d'upgrades
        # Plus d'évolution automatique !
        pass
    
    def auto_fire(self):
        """Tire automatiquement vers l'ennemi le plus proche - OBSOLÈTE"""
        # Cette méthode est maintenant obsolète.
        # Le tir automatique est géré par le système OOP via CannonWeapon.fire()
        # qui utilise automatiquement la portée dynamique selon le niveau.
        pass
    
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
                # Créer effet de mort pour les ennemis spéciaux
                if enemy.is_special:
                    death_effect = DeathEffect(enemy.x, enemy.y, self.config)
                    self.death_effects.append(death_effect)
                
                # Appliquer bonus si c'est un ennemi spécial
                if enemy.is_special and enemy.bonus_type:
                    self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                
                # Vérifier que l'ennemi est encore dans la liste (au cas où le bonus l'aurait supprimé)
                if enemy in self.enemies:
                    # Gérer les drops avant de supprimer l'ennemi
                    self.handle_enemy_drops(enemy)
                    self.enemies.remove(enemy)
                    self.enemies_killed += 1  # Incrémenter les statistiques
                self.score += self.config.SCORE_PER_LIGHTNING_KILL  # Plus de points pour les lightning
    
    def create_particles(self, x, y, particle_type="explosion", multiplier=1.0, beam_direction=None):
        """
        Méthode unifiée pour créer différents types de particules
        
        Args:
            x, y: Position
            particle_type: "explosion", "lightning", "welding", "beam_explosion"
            multiplier: Multiplicateur du nombre de particules
            beam_direction: Tuple (dx, dy) pour les particules de soudure
        """
        if particle_type == "lightning":
            # Triple le nombre de particules pour un effet spectaculaire
            count = int(self.config.PARTICLE_COUNT * 3 * multiplier)
            for _ in range(count):
                particle = Particle(x, y, self.config)
                # Effet électrique avec particules plus grosses
                particle.vel_x *= random.uniform(1.2, 2.0)
                particle.vel_y *= random.uniform(1.2, 2.0)
                particle.color = random.choice([
                    (255, 255, 255), (200, 200, 255), (255, 255, 200), (150, 150, 255)
                ])
                # Particules un peu plus grosses pour le lightning (x1.5 à x2)
                particle.size = random.randint(int(self.config.PARTICLE_SIZE * 1.5), self.config.PARTICLE_SIZE * 2)
                particle.lifetime = int(particle.lifetime * random.uniform(1.2, 1.8))
                particle.current_life = particle.lifetime
                self.particles.append(particle)
                
        elif particle_type == "welding":
            # Particules de soudure spécialisées
            base_count = max(4, self.config.PARTICLE_COUNT // 2)
            count = int(base_count * multiplier)
            
            beam_dir_x, beam_dir_y = beam_direction if beam_direction else (None, None)
            
            for _ in range(count):
                particle = WeldingParticle(x, y, self.config, beam_dir_x, beam_dir_y)
                self.welding_particles.append(particle)
            
            # Particules ultra-brillantes
            for _ in range(max(1, count // 4)):
                particle = WeldingParticle(x, y, self.config, beam_dir_x, beam_dir_y)
                particle.color = (255, 255, 255)
                particle.size = 1
                particle.lifetime = random.randint(15, 30)
                particle.current_life = particle.lifetime
                self.welding_particles.append(particle)
                
        elif particle_type == "beam_explosion":
            # Double explosion pour beam
            count = int(self.config.PARTICLE_COUNT * 2 * multiplier)
            for _ in range(count):
                particle = Particle(x, y, self.config)
                self.particles.append(particle)
                
        else:  # particle_type == "explosion" ou par défaut
            # Explosion normale
            count = int(self.config.PARTICLE_COUNT * multiplier)
            for _ in range(count):
                particle = Particle(x, y, self.config)
                self.particles.append(particle)
    
    # Méthodes legacy conservées pour compatibilité
    def create_explosion_particles(self, x, y):
        """Crée des particules d'explosion à la position donnée"""
        self.create_particles(x, y, "explosion")
    
    def create_lightning_explosion_particles(self, x, y):
        """Crée une explosion renforcée spécifique au Lightning"""
        self.create_particles(x, y, "lightning")
    
    def create_welding_particles(self, x, y, beam_direction_x=None, beam_direction_y=None):
        """Crée des particules de soudure au point d'impact du Beam"""
        self.create_particles(x, y, "welding", beam_direction=(beam_direction_x, beam_direction_y))
    
    def create_beam_explosion_particles(self, x, y):
        """Crée une explosion renforcée quand un ennemi est tué par un Beam"""
        self.create_particles(x, y, "beam_explosion")
    
    def handle_enemy_drops(self, enemy):
        """Gère les drops d'objets collectibles quand un ennemi meurt"""
        # Compter le nombre de pièces actuellement sur le terrain
        current_coins = sum(1 for collectible in self.collectibles if isinstance(collectible, Coin))
        
        # TOUJOURS lâcher une pièce quand un ennemi meurt (si limite pas atteinte)
        if current_coins < self.config.COIN_MAX_ON_FIELD:
            # Calculer le centre exact de l'ennemi
            enemy_center_x = enemy.x + enemy.size // 2
            enemy_center_y = enemy.y + enemy.size // 2
            
            coin = Coin(
                enemy_center_x,
                enemy_center_y,
                self.config
            )
            self.collectibles.append(coin)
        else:
            # Si trop de pièces, supprimer la plus ancienne
            oldest_coin = None
            for collectible in self.collectibles:
                if isinstance(collectible, Coin):
                    oldest_coin = collectible
                    break
            if oldest_coin:
                self.collectibles.remove(oldest_coin)
                
                # Ajouter la nouvelle pièce au centre de l'ennemi
                enemy_center_x = enemy.x + enemy.size // 2
                enemy_center_y = enemy.y + enemy.size // 2
                
                coin = Coin(
                    enemy_center_x,
                    enemy_center_y,
                    self.config
                )
                self.collectibles.append(coin)
        
        # Compter le nombre de cœurs actuellement sur le terrain
        current_hearts = sum(1 for collectible in self.collectibles if isinstance(collectible, Heart))
        
        # Vérifier si un coeur doit être lâché (probabilité de 1/200 pour tous les ennemis)
        if random.random() < self.config.HEART_DROP_PROBABILITY:
            # Vérifier la limite maximum de cœurs sur le terrain
            if current_hearts >= self.config.HEART_MAX_ON_FIELD:
                print(f"💔 Limite de {self.config.HEART_MAX_ON_FIELD} cœurs atteinte - aucun cœur supplémentaire lâché")
                return
            
            # Déterminer le nombre de coeurs à lâcher
            if enemy.is_special:
                drop_count = self.config.HEART_ELITE_DROP_COUNT
            else:
                drop_count = self.config.HEART_NORMAL_DROP_COUNT
            
            # Limiter le nombre de coeurs à créer pour ne pas dépasser la limite
            drop_count = min(drop_count, self.config.HEART_MAX_ON_FIELD - current_hearts)
            
            # Créer les coeurs
            for i in range(drop_count):
                # Position légèrement décalée pour éviter la superposition
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                heart = Heart(
                    enemy.x + offset_x, 
                    enemy.y + offset_y, 
                    self.config
                )
                self.collectibles.append(heart)
                
            print(f"💚 Ennemi {enemy.sprite_id} {'spécial' if enemy.is_special else 'normal'} tué - {drop_count} coeur(s) lâché(s) ! (probabilité {self.config.HEART_DROP_PROBABILITY:.1%}) [{current_hearts + drop_count}/{self.config.HEART_MAX_ON_FIELD}]")
    
    def update_collectibles(self):
        """Met à jour tous les objets collectibles"""
        # Obtenir les effets de l'aimant s'il est actif
        magnet_effect = self.skill_manager.get_magnet_effect()
        
        for collectible in self.collectibles[:]:
            # Appliquer l'attraction magnétique si l'aimant est actif
            if magnet_effect:
                self.apply_magnet_effect(collectible, magnet_effect)
            
            collectible.update(self.player.x, self.player.y)
            
            # Vérifier si l'objet a été collecté
            if collectible.is_collected:
                collectible.on_collect(self.player, self)
                self.collectibles.remove(collectible)
    
    def apply_magnet_effect(self, collectible, magnet_effect):
        """Applique l'effet magnétique sur un objet collectible"""
        import math
        
        # Calculer la distance entre le joueur et l'objet
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        collectible_center_x = collectible.x + collectible.size // 2
        collectible_center_y = collectible.y + collectible.size // 2
        
        distance_x = player_center_x - collectible_center_x
        distance_y = player_center_y - collectible_center_y
        distance = math.sqrt(distance_x**2 + distance_y**2)
        
        # Si l'objet est dans la portée de l'aimant
        if distance <= magnet_effect["range"] and distance > 0:
            # Calculer la direction normalisée
            direction_x = distance_x / distance
            direction_y = distance_y / distance
            
            # Appliquer la force d'attraction (plus fort quand plus proche)
            attraction_force = magnet_effect["strength"] * (magnet_effect["range"] - distance) / magnet_effect["range"]
            
            # Déplacer l'objet vers le joueur
            collectible.x += direction_x * attraction_force * 10  # Multiplier pour effet visible
            collectible.y += direction_y * attraction_force * 10
    
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
        
        # Si une transition est active, ne pas changer d'écran encore
        if self.transition_manager.is_active:
            # Pendant la transition, dessiner l'écran approprié selon l'état actuel
            # (pas l'état de pré-transition)
            if self.show_upgrade_screen:
                self.draw_upgrade_screen()
            elif self.paused_skills:
                self.draw_skills_screen()
            elif self.show_exit_menu:
                self.draw_exit_menu()
            else:
                self._draw_game_screen()
        else:
            # Pas de transition active, dessiner normalement
            if self.show_upgrade_screen:
                self.draw_upgrade_screen()
            elif self.paused_skills:
                self.draw_skills_screen()
            elif self.show_exit_menu:
                self.draw_exit_menu()
            else:
                self._draw_game_screen()
        
        # Capturer le nouvel écran si nécessaire (après changement d'état)
        if self._capture_new_screen and self.transition_manager.is_active:
            self.transition_manager.update_new_surface(self.screen)
            self._capture_new_screen = False
        
        # Dessiner les transitions par-dessus tout le reste
        self.transition_manager.render(self.screen)
        
        # TOUJOURS faire le flip pour afficher à l'écran
        pygame.display.flip()
    
    def _draw_game_screen(self):
        """Dessine l'écran de jeu principal"""
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

    def draw_button(self, text, rect, color, text_color=None, border_radius=14):
        """
        Méthode helper pour dessiner un bouton standardisé
        
        Args:
            text: Texte du bouton
            rect: Rectangle pygame.Rect
            color: Couleur de fond du bouton
            text_color: Couleur du texte (blanc par défaut)
            border_radius: Rayon des coins arrondis
        """
        if text_color is None:
            text_color = self.config.WHITE
            
        pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_overlay_background(self, alpha=160, color=(20, 20, 20)):
        """Dessine un overlay semi-transparent pour les menus"""
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(alpha)
        overlay.fill(color)
        self.screen.blit(overlay, (0, 0))

    def draw_exit_menu(self):
        """Dessine le menu de sortie avec boutons cliquables"""
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        
        # Background overlay
        self.draw_overlay_background()

        # Titre
        title = "Menu de sortie"
        title_surface = self.font.render(title, True, self.config.WHITE)
        title_rect = title_surface.get_rect(center=(screen_w//2, screen_h//2 - 120))
        self.screen.blit(title_surface, title_rect)

        # Boutons avec helper
        btn_w, btn_h = 220, 60
        btn_margin = 40
        btn_configs = [
            ("QUIT", (200, 60, 60)),
            ("RESTART", (60, 200, 120)),
            ("OPTION", (60, 120, 200))
        ]
        
        btn_rects = []
        for i, (name, color) in enumerate(btn_configs):
            rect = pygame.Rect(
                screen_w//2 - btn_w//2,
                screen_h//2 - btn_h//2 + i*(btn_h + btn_margin),
                btn_w, btn_h
            )
            btn_rects.append(rect)
            self.draw_button(name, rect, color)

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
        
        # === BARRE DE BOUCLIER ===
        if hasattr(self.player, 'shield_points') and hasattr(self.player, 'max_shield_points'):
            if self.player.max_shield_points > 0:
                shield_ratio = self.player.shield_points / self.player.max_shield_points
                
                # Position sous la barre de vie
                shield_bar_y = health_bar_y + health_bar_height + 5
                shield_bar_height = health_bar_height // 2  # Plus petite que la barre de vie
                
                # Fond de la barre de bouclier
                shield_bg_rect = pygame.Rect(health_bar_x, shield_bar_y, health_bar_width, shield_bar_height)
                pygame.draw.rect(self.screen, self.config.GRAY, shield_bg_rect)
                
                # Barre de bouclier actuelle (couleur dorée)
                shield_width = int(health_bar_width * shield_ratio)
                if shield_width > 0:
                    shield_rect = pygame.Rect(health_bar_x, shield_bar_y, shield_width, shield_bar_height)
                    shield_color = (255, 215, 0)  # Doré
                    pygame.draw.rect(self.screen, shield_color, shield_rect)
                
                # Contour de la barre de bouclier
                pygame.draw.rect(self.screen, self.config.WHITE, shield_bg_rect, 1)
        
        wave_text = f"Vague {self.wave_number} - Ennemis: {len(self.enemies)}"
        wave_surface = self.font.render(wave_text, True, self.config.WHITE)
        self.screen.blit(wave_surface, (30, 60))
        
        # Afficher les armes du joueur (sans caractères spéciaux, avec espacement)
        weapons_text = f"ARMES ({len(self.weapon_manager.weapons)}/7):"
        weapons_surface = self.small_font.render(weapons_text, True, self.config.CYAN)
        self.screen.blit(weapons_surface, (30, 100))  # Remettre la position originale
        
        y_offset = 130  # Remettre la position originale
        for weapon in self.weapon_manager.weapons:
            weapon_text = f"  {weapon.name} Niv.{weapon.level}"
            weapon_surface = self.small_font.render(weapon_text, True, self.config.WHITE)
            self.screen.blit(weapon_surface, (50, y_offset))
            y_offset += 50  # Espacement augmenté de 40 à 50
        
        # Afficher les compétences du joueur (sans caractères spéciaux, avec espacement)
        y_offset += 30  # Plus d'espacement avant section compétences
        skills_text = f"COMPETENCES ({len(self.skill_manager.skills)}/14):"
        skills_surface = self.small_font.render(skills_text, True, self.config.PURPLE)
        self.screen.blit(skills_surface, (30, y_offset))
        y_offset += 50  # Plus d'espacement après titre section
        
        for skill in self.skill_manager.skills:
            skill_text = f"  {skill.name} Niv.{skill.level}"
            skill_surface = self.small_font.render(skill_text, True, self.config.WHITE)
            self.screen.blit(skill_surface, (50, y_offset))
            y_offset += 50  # Espacement augmenté de 40 à 50
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, self.config.WHITE)
        score_rect = score_surface.get_rect()
        score_rect.topright = (self.config.WINDOW_WIDTH - 10, 10)
        self.screen.blit(score_surface, score_rect)
        
        # Temps de survie en cours
        survival_time = self.get_survival_time_string()
        time_text = f"Time: {survival_time}"
        time_surface = self.font.render(time_text, True, self.config.CYAN)
        time_rect = time_surface.get_rect()
        time_rect.topright = (self.config.WINDOW_WIDTH - 10, 50)
        self.screen.blit(time_surface, time_rect)
        
        # Barre de progression basée sur les pièces collectées
        self.draw_progression_bar()
        
        # Indicateur "Always Skip" si activé
        if self.always_skip_mode:
            always_skip_text = "🚀 ALWAYS SKIP ACTIF"
            always_skip_surface = self.font.render(always_skip_text, True, (100, 255, 100))
            always_skip_rect = always_skip_surface.get_rect()
            always_skip_rect.topright = (self.config.WINDOW_WIDTH - 10, 90)
            self.screen.blit(always_skip_surface, always_skip_rect)
        
        # Afficher les bonus actifs
        y_offset += 30  # Plus d'espacement avant section bonus
        for bonus_type, frames_left in self.bonus_manager.active_bonuses.items():
            seconds_left = frames_left / 60
            bonus_text = f"{bonus_type.replace('_', ' ').title()}: {seconds_left:.1f}s"
            bonus_surface = self.small_font.render(bonus_text, True, self.config.YELLOW)
            self.screen.blit(bonus_surface, (30, y_offset))
            y_offset += 50  # Espacement augmenté de 40 à 50
        
        # Afficher le bouclier s'il est actif
        if self.bonus_manager.shield_hits_remaining > 0:
            shield_text = f"Bouclier: {self.bonus_manager.shield_hits_remaining} coups"
            shield_surface = self.small_font.render(shield_text, True, self.config.CYAN)
            self.screen.blit(shield_surface, (30, y_offset))
    
    def draw_progression_bar(self):
        """Dessine la barre de progression des niveaux basée sur les pièces collectées"""
        # Mettre à jour l'animation
        self.update_progression_animation()
        
        # Calculer l'espace occupé par la minimap
        minimap_size = min(self.config.WINDOW_WIDTH // self.config.MINIMAP_SIZE_RATIO, 
                          self.config.WINDOW_HEIGHT // self.config.MINIMAP_SIZE_RATIO)
        minimap_space = minimap_size + self.config.MINIMAP_MARGIN + 20  # +20 pour marge supplémentaire
        
        # Dimensions et position de la barre
        margin_left = 50  # Marge à gauche réduite
        margin_right = minimap_space  # Marge à droite basée sur la minimap
        bar_width = self.config.WINDOW_WIDTH - margin_left - margin_right
        bar_height = 25  # Hauteur de la barre
        bar_x = margin_left
        bar_y = self.config.WINDOW_HEIGHT - 60  # 60 pixels du bas de l'écran
        
        # Fond de la barre (gris foncé) avec bords arrondis
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (40, 40, 40), background_rect, border_radius=12)
        
        # Bordure de la barre avec bords arrondis
        pygame.draw.rect(self.screen, (200, 200, 200), background_rect, 2, border_radius=12)
        
        # Barre de progression avec bords arrondis (couleur dorée unie)
        if self.progression_bar_progress > 0:
            progress_width = int(bar_width * self.progression_bar_progress)
            # Réduire la largeur pour laisser voir le cadre blanc (marge de 3 pixels de chaque côté)
            progress_rect = pygame.Rect(bar_x + 3, bar_y + 3, max(0, progress_width - 6), max(0, bar_height - 6))
            
            if progress_rect.width > 0 and progress_rect.height > 0:
                # Couleur dorée de base
                gold_color = (255, 215, 0)
                pygame.draw.rect(self.screen, gold_color, progress_rect, border_radius=9)
        
        # Effet de brillance avec bords arrondis (barre plus claire au centre)
        if self.progression_bar_progress > 0:
            progress_width = int(bar_width * self.progression_bar_progress)
            # Ajuster pour la nouvelle taille réduite de la barre
            shine_rect = pygame.Rect(bar_x + 5, bar_y + bar_height // 3 + 1, max(0, progress_width - 10), max(0, bar_height // 3 - 2))
            if shine_rect.width > 0 and shine_rect.height > 0:
                shine_surface = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
                shine_surface.set_alpha(80)  # Réduit l'opacité pour un effet plus subtil
                shine_surface.fill((255, 245, 100))
                # Créer un masque arrondi pour l'effet de brillance
                pygame.draw.rect(shine_surface, (255, 245, 100, 80), (0, 0, shine_rect.width, shine_rect.height), border_radius=7)
                self.screen.blit(shine_surface, (shine_rect.x, shine_rect.y))
        
        # Texte de progression (au centre de la barre)
        if self.level == 1:
            progress_text = f"{self.coins_collected} / {self.coins_to_next_level} pièces"
        else:
            # Calculer la progression vers le niveau suivant (level + 1)
            next_level_total_needed = self.calculate_coins_for_level(self.level + 1)
            current_level_total_needed = self.calculate_coins_for_level(self.level)
            coins_needed_this_level = next_level_total_needed - current_level_total_needed
            coins_progress_this_level = self.coins_collected - current_level_total_needed
            
            # Vérification pour éviter les valeurs négatives
            coins_needed_this_level = max(1, coins_needed_this_level)
            coins_progress_this_level = max(0, min(coins_progress_this_level, coins_needed_this_level))
            
            progress_text = f"{coins_progress_this_level} / {coins_needed_this_level} pièces"
        
        progress_surface = self.small_font.render(progress_text, True, (255, 255, 255))
        progress_rect = progress_surface.get_rect()
        progress_rect.center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
        self.screen.blit(progress_surface, progress_rect)

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
        
        # Temps de survie (arrêté au moment de la mort)
        survival_time = self.get_survival_time_string()
        time_text = f"Survival Time: {survival_time}"
        time_surface = self.small_font.render(time_text, True, self.config.YELLOW)
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
        # === FERMER TOUS LES MENUS ===
        self.show_exit_menu = False
        self.paused_skills = False
        self.show_upgrade_screen = False
        
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
        self.game_end_time = None  # Réinitialiser le temps de fin
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
        self.welding_particles.clear()  # Nouveau
        self.energy_orbs.clear()  # Nouveau
        self.death_effects.clear()  # Nouveau - pour les effets de mort
        self.orb_death_effects.clear()  # Nouveau - pour les effets de mort par orbe
        self.beam_death_effects.clear()  # Nouveau - pour les effets de mort par beam
        
        # Les orb sont maintenant gérées automatiquement par le WeaponManager
        # Plus besoin d'appel manuel
        
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
    
    def _load_weapon_and_skill_images(self):
        """Charge et met en cache les images d'armes et de compétences"""
        # Charger les images d'armes
        weapon_files = {
            "Canon": "canon.png",
            "Orb": "orb.png", 
            "Lightning": "lightning.png",
            "Beam": "beam.png"
        }
        
        for weapon_name, filename in weapon_files.items():
            try:
                image_path = f"assets/weapons/{filename}"
                image = pygame.image.load(image_path).convert_alpha()
                self.weapon_images[weapon_name] = image
                print(f"✅ Image d'arme chargée: {weapon_name} ({filename})")
            except (pygame.error, FileNotFoundError) as e:
                print(f"❌ Impossible de charger l'image d'arme {weapon_name}: {e}")
                self.weapon_images[weapon_name] = None
        
        # Charger les images de compétences
        skill_files = {
            "Vitesse": "vitesse.png",
            "Régénération": "régénération.png", 
            "Résistance": "bouclier.png",  # bouclier.png pour Résistance
            "Aimant": "aimant.png",
            "Bouclier": "bouclier.png"  # Même image que Résistance pour l'instant
        }
        
        for skill_name, filename in skill_files.items():
            try:
                image_path = f"assets/competences/{filename}"
                image = pygame.image.load(image_path).convert_alpha()
                self.skill_images[skill_name] = image
                print(f"✅ Image de compétence chargée: {skill_name} ({filename})")
            except (pygame.error, FileNotFoundError) as e:
                print(f"❌ Impossible de charger l'image de compétence {skill_name}: {e}")
                self.skill_images[skill_name] = None
    
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

        # Titre principal
        title = "Compétences & Armes"
        title_surface = self.font.render(title, True, self.config.WHITE)
        title_rect = title_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 80))  # Plus bas pour laisser de l'espace
        self.screen.blit(title_surface, title_rect)

        # Label section Armes
        weapons_label = "ARMES"
        weapons_label_surface = self.small_font.render(weapons_label, True, self.config.CYAN)
        weapons_label_rect = weapons_label_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 300))
        self.screen.blit(weapons_label_surface, weapons_label_rect)

        # Affichage des armes (7 slots) - Agrandies de 50% supplémentaires et encore plus bas
        slot_size = 192  # Agrandies de 50% : 128 → 192
        slot_margin = 40  # Ajusté pour la nouvelle taille encore plus grande
        total_slots = 7
        start_x = (self.config.WINDOW_WIDTH - (total_slots * slot_size + (total_slots-1)*slot_margin)) // 2
        y = 360  # Encore plus bas pour être parfaitement dans le cadre
        for i in range(total_slots):
            rect = pygame.Rect(start_x + i*(slot_size+slot_margin), y, slot_size, slot_size)
            pygame.draw.rect(self.screen, (80,80,80), rect, border_radius=12)
            # Si arme présente, dessiner une icône
            if i < len(self.weapon_manager.weapons):
                self.draw_weapon_icon(self.weapon_manager.weapons[i], rect)
            else:
                pygame.draw.rect(self.screen, (40,40,40), rect.inflate(-16,-16), border_radius=8)

        # Label section Compétences
        skills_label = "PASSIFS"
        skills_label_surface = self.small_font.render(skills_label, True, self.config.PURPLE)
        skills_label_rect = skills_label_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 650))
        self.screen.blit(skills_label_surface, skills_label_rect)

        # Affichage des compétences (14 slots, 2 lignes de 7) - Agrandies de 50% et encore plus bas
        skill_slot_size = 144  # Agrandies de 50% : 96 → 144
        skill_slot_margin = 32  # Ajusté pour la nouvelle taille encore plus grande
        total_skills = 14
        start_x = (self.config.WINDOW_WIDTH - (7 * skill_slot_size + 6*skill_slot_margin)) // 2
        y_skills = 710  # Encore plus bas pour être parfaitement dans le cadre avec les nouvelles tailles
        for i in range(total_skills):
            row = i // 7
            col = i % 7
            rect = pygame.Rect(start_x + col*(skill_slot_size+skill_slot_margin), y_skills + row*(skill_slot_size+skill_slot_margin), skill_slot_size, skill_slot_size)
            pygame.draw.rect(self.screen, (100,100,100), rect, border_radius=10)
            # Si compétence présente, dessiner une icône
            if i < len(self.skill_manager.skills):
                self.draw_skill_icon(self.skill_manager.skills[i], rect)
            else:
                pygame.draw.rect(self.screen, (60,60,60), rect.inflate(-12,-12), border_radius=8)

        # Instructions
        text = "TAB - Reprendre le jeu"
        text_surface = self.small_font.render(text, True, self.config.WHITE)
        text_rect = text_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT-40))
        self.screen.blit(text_surface, text_rect)

    def draw_weapon_icon(self, weapon, rect):
        """Dessine l'icône d'une arme selon son type en utilisant les vraies images"""
        # Essayer d'utiliser l'image chargée
        weapon_image = self.weapon_images.get(weapon.name)
        
        if weapon_image:
            # Redimensionner l'image pour qu'elle remplisse presque tout le rect (avec une petite marge)
            margin = 8  # Marge de 8px de chaque côté
            target_size = (rect.width - margin*2, rect.height - margin*2)
            scaled_image = pygame.transform.scale(weapon_image, target_size)
            
            # Centrer l'image dans le rect
            image_rect = scaled_image.get_rect()
            image_rect.center = rect.center
            self.screen.blit(scaled_image, image_rect)
        else:
            # Fallback sur les dessins géométriques si l'image n'est pas disponible
            center = rect.center
            
            if weapon.name == "Orb":
                pygame.draw.circle(self.screen, (0, 200, 255), center, rect.width//3)
                pygame.draw.circle(self.screen, (255, 255, 255), center, rect.width//3, 2)
            elif weapon.name == "Lightning":
                pygame.draw.polygon(self.screen, (255, 255, 0), [
                    (center[0], center[1]-rect.height//3),
                    (center[0]+rect.width//4, center[1]-rect.height//6),
                    (center[0]+rect.width//6, center[1]),
                    (center[0], center[1]+rect.height//3),
                    (center[0]-rect.width//6, center[1]+rect.height//6),
                    (center[0]-rect.width//4, center[1]-rect.height//6),
                ])
            elif weapon.name == "Beam":
                pygame.draw.rect(self.screen, (255, 100, 100), 
                               (center[0]-rect.width//3, center[1]-rect.height//8, 
                                rect.width//1.5, rect.height//4))
                pygame.draw.rect(self.screen, (255, 200, 200), 
                               (center[0]-rect.width//4, center[1]-rect.height//12, 
                                rect.width//2, rect.height//6))
            elif weapon.name == "Canon":
                pygame.draw.circle(self.screen, (150, 150, 150), center, rect.width//3)
                pygame.draw.circle(self.screen, (100, 100, 100), center, rect.width//4)
                pygame.draw.circle(self.screen, (200, 200, 200), center, rect.width//3, 2)
            else:
                pygame.draw.rect(self.screen, (180, 180, 180), rect.inflate(-20, -20), border_radius=6)
        
        # Afficher le niveau de l'arme au centre avec un fond semi-transparent
        level_text = str(weapon.level)
        level_surface = self.font.render(level_text, True, self.config.WHITE)  # Utilise self.font au lieu de self.small_font
        
        # Créer un fond semi-transparent pour le niveau
        level_bg_size = max(level_surface.get_width() + 12, level_surface.get_height() + 12)
        level_bg = pygame.Surface((level_bg_size, level_bg_size))
        level_bg.set_alpha(128)  # Semi-transparent
        level_bg.fill((0, 0, 0))  # Fond noir
        
        # Positionner le fond et le texte au centre de l'icône
        level_bg_rect = level_bg.get_rect()
        level_bg_rect.center = rect.center
        self.screen.blit(level_bg, level_bg_rect)
        
        level_rect = level_surface.get_rect()
        level_rect.center = level_bg_rect.center
        self.screen.blit(level_surface, level_rect)

    def draw_skill_icon(self, skill, rect):
        """Dessine l'icône d'une compétence selon son type en utilisant les vraies images"""
        # Essayer d'utiliser l'image chargée
        skill_image = self.skill_images.get(skill.name)
        
        if skill_image:
            # Redimensionner l'image pour qu'elle remplisse presque tout le rect (avec une petite marge)
            margin = 6  # Marge un peu plus petite pour les compétences
            target_size = (rect.width - margin*2, rect.height - margin*2)
            scaled_image = pygame.transform.scale(skill_image, target_size)
            
            # Centrer l'image dans le rect
            image_rect = scaled_image.get_rect()
            image_rect.center = rect.center
            self.screen.blit(scaled_image, image_rect)
        else:
            # Fallback sur les dessins géométriques si l'image n'est pas disponible
            center = rect.center
            
            if skill.name == "Vitesse":
                arrow_points = [
                    (center[0]-rect.width//4, center[1]),
                    (center[0]+rect.width//4, center[1]-rect.height//4),
                    (center[0]+rect.width//6, center[1]),
                    (center[0]+rect.width//4, center[1]+rect.height//4)
                ]
                pygame.draw.polygon(self.screen, (100, 255, 100), arrow_points)
            elif skill.name == "Régénération":
                pygame.draw.rect(self.screen, (255, 100, 100), 
                               (center[0]-rect.width//8, center[1]-rect.height//3, 
                                rect.width//4, rect.height//1.5))
                pygame.draw.rect(self.screen, (255, 100, 100), 
                               (center[0]-rect.width//3, center[1]-rect.height//8, 
                                rect.width//1.5, rect.width//4))
            elif skill.name == "Aimant":
                pygame.draw.rect(self.screen, (255, 150, 0), 
                               (center[0]-rect.width//3, center[1]-rect.height//4, 
                                rect.width//8, rect.height//2))
                pygame.draw.rect(self.screen, (255, 150, 0), 
                               (center[0]+rect.width//4, center[1]-rect.height//4, 
                                rect.width//8, rect.height//2))
                pygame.draw.rect(self.screen, (255, 150, 0), 
                               (center[0]-rect.width//3, center[1]+rect.height//6, 
                                rect.width//1.5, rect.height//8))
            elif skill.name == "Résistance":
                shield_points = [
                    (center[0], center[1]-rect.height//3),
                    (center[0]+rect.width//3, center[1]-rect.height//6),
                    (center[0]+rect.width//3, center[1]+rect.height//6),
                    (center[0], center[1]+rect.height//3),
                    (center[0]-rect.width//3, center[1]+rect.height//6),
                    (center[0]-rect.width//3, center[1]-rect.height//6)
                ]
                pygame.draw.polygon(self.screen, (100, 150, 255), shield_points)
            else:
                pygame.draw.circle(self.screen, (120, 255, 120), center, rect.width//3)
        
        # Afficher le niveau de la compétence au centre avec un fond semi-transparent
        level_text = str(skill.level)
        level_surface = self.font.render(level_text, True, self.config.WHITE)  # Utilise self.font au lieu de self.small_font
        
        # Créer un fond semi-transparent pour le niveau
        level_bg_size = max(level_surface.get_width() + 12, level_surface.get_height() + 12)
        level_bg = pygame.Surface((level_bg_size, level_bg_size))
        level_bg.set_alpha(128)  # Semi-transparent
        level_bg.fill((0, 0, 0))  # Fond noir
        
        # Positionner le fond et le texte au centre de l'icône
        level_bg_rect = level_bg.get_rect()
        level_bg_rect.center = rect.center
        self.screen.blit(level_bg, level_bg_rect)
        
        level_rect = level_surface.get_rect()
        level_rect.center = level_bg_rect.center
        self.screen.blit(level_surface, level_rect)
    
    def trigger_upgrade_screen(self):
        """Affiche l'écran de choix d'upgrade à la montée de niveau"""
        self.upgrade_options = self.get_smart_upgrade_options()
        
        # Vérifier s'il y a des options d'upgrade disponibles
        if len(self.upgrade_options) == 0:
            print("🎯 Aucune amélioration disponible - Activation automatique du mode Always Skip")
            self.always_skip_mode = True
            self.score += 1000  # Bonus de score pour compensation
            return  # Ne pas afficher l'écran d'upgrade
        
        # Démarrer la transition vers l'écran d'upgrade seulement s'il y a des options
        self.transition_to_upgrade_screen()
    
    def get_upgrade_option_rects(self):
        # Retourne les rects des 3 options pour la détection (boutons agrandis x2)
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        opt_w, opt_h = 440, 128  # Agrandis x2 : 220->440, 64->128
        y = screen_h//2 + 320  # Déplacé encore plus bas pour les icônes carrées
        return [pygame.Rect(screen_w//2-660+i*480, y, opt_w, opt_h) for i in range(3)]
    
    def get_upgrade_icon_rects(self):
        # Retourne les rects des 3 cadres d'icônes au-dessus des boutons
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        icon_size = 440  # Icônes carrées de la largeur des boutons
        y = screen_h//2 - 160  # Ajusté pour la nouvelle hauteur
        return [pygame.Rect(screen_w//2-660+i*480, y, icon_size, icon_size) for i in range(3)]
    
    def load_upgrade_icon(self, option):
        """Charge l'icône appropriée pour une option d'upgrade"""
        try:
            name = option["name"]
            
            # Extraire le nom de l'arme/compétence
            if "|" in name:
                lines = name.split("|")
                item_name = lines[1].strip().lower()  # Deuxième partie (nom de l'item)
                
                # Nettoyer le nom (enlever "niv.X" pour les améliorations)
                if " niv." in item_name:
                    item_name = item_name.split(" niv.")[0]
                
                # Déterminer le dossier selon le type
                if "débloquer" in lines[0].lower():
                    # Nouvelle arme
                    folder = "weapons"
                elif "compétence" in lines[0].lower():
                    # Compétence
                    folder = "competences"
                elif "améliorer" in lines[0].lower():
                    # Amélioration - déterminer si c'est arme ou compétence
                    if item_name in ["canon", "lightning", "orb", "beam"]:
                        folder = "weapons"
                    else:
                        folder = "competences"
                else:
                    return None
                
                # Charger l'image
                image_path = f"assets/{folder}/{item_name}.png"
                image = pygame.image.load(image_path).convert_alpha()
                return image
                
        except (pygame.error, FileNotFoundError, IndexError):
            # Image non trouvée ou erreur de parsing
            return None
        
        return None
    
    def draw_upgrade_screen(self):
        """Affiche l'écran de choix d'upgrade"""
        # Vérification de sécurité : si pas d'options, fermer l'écran
        # MAIS pas pendant une transition active
        if len(self.upgrade_options) == 0 and not self.transition_manager.is_active:
            print("Aucune option d'upgrade disponible, fermeture de l'écran")
            self.show_upgrade_screen = False
            self.paused = False
            self.ban_mode = False
            return
        
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        overlay = pygame.Surface((int(screen_w*0.75), int(screen_h*0.75)))
        overlay.fill((60, 60, 80) if not self.ban_mode else (80, 20, 20))
        overlay.set_alpha(51)  # 20% de transparence
        overlay_x = (screen_w - overlay.get_width()) // 2
        overlay_y = (screen_h - overlay.get_height()) // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))
        
        # Dessiner les cadres englobants cliquables pour chaque compétence
        combined_rects = self.get_upgrade_combined_rects()
        icon_rects = self.get_upgrade_icon_rects()
        option_rects = self.get_upgrade_option_rects()
        
        # Options (cadres englobants avec icônes et boutons)
        for i, option in enumerate(self.upgrade_options):
            # === CADRE ENGLOBANT CLIQUABLE ===
            combined_rect = combined_rects[i]
            
            # Dessiner le cadre principal (zone cliquable)
            frame_color = (220, 220, 220) if not option.get("is_new_weapon", False) else (255, 215, 0)
            pygame.draw.rect(self.screen, frame_color, combined_rect, 2, border_radius=15)
            
            # Fond semi-transparent pour tout le cadre
            background_color = (240, 240, 240, 30) if not option.get("is_new_weapon", False) else (255, 240, 200, 30)
            s = pygame.Surface((combined_rect.width, combined_rect.height))
            s.set_alpha(30)
            s.fill(background_color[:3])
            self.screen.blit(s, combined_rect)
            
            # === CADRE D'ICÔNE ===
            icon_rect = icon_rects[i]
            
            # Dessiner le cadre de l'icône
            icon_frame_color = (200, 200, 200) if not option.get("is_new_weapon", False) else (255, 215, 0)
            pygame.draw.rect(self.screen, icon_frame_color, icon_rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 100, 100), icon_rect, 3, border_radius=8)  # Bordure
            
            # Charger et afficher l'icône si disponible
            icon_image = self.load_upgrade_icon(option)
            if icon_image:
                # Traitement de l'image pour la rendre carrée sans déformation
                original_w, original_h = icon_image.get_size()
                
                # Calculer la taille du carré (la plus petite dimension)
                square_size = min(original_w, original_h)
                
                # Calculer la position pour centrer le crop
                crop_x = (original_w - square_size) // 2
                crop_y = (original_h - square_size) // 2
                
                # Créer une surface carrée avec la partie centrale de l'image
                square_surface = pygame.Surface((square_size, square_size))
                source_rect = pygame.Rect(crop_x, crop_y, square_size, square_size)
                square_surface.blit(icon_image, (0, 0), source_rect)
                
                # Redimensionner à la taille de l'icône carrée (avec marge)
                icon_size = icon_rect.width - 20  # Marge de 10px de chaque côté
                scaled_icon = pygame.transform.smoothscale(square_surface, (icon_size, icon_size))
                
                # Centrer l'image carrée dans le cadre carré
                icon_x = icon_rect.centerx - icon_size // 2
                icon_y = icon_rect.centery - icon_size // 2
                self.screen.blit(scaled_icon, (icon_x, icon_y))
            else:
                # Pas d'image trouvée - afficher un placeholder
                placeholder_color = (150, 150, 150)
                placeholder_rect = pygame.Rect(icon_rect.x + 20, icon_rect.y + 20, 
                                             icon_rect.width - 40, icon_rect.height - 40)
                pygame.draw.rect(self.screen, placeholder_color, placeholder_rect, border_radius=4)
                
                # Texte "?" au centre
                question_surface = self.font.render("?", True, (80, 80, 80))
                question_rect = question_surface.get_rect(center=placeholder_rect.center)
                self.screen.blit(question_surface, question_rect)
            
            # === BOUTON DE DESCRIPTION ===
            rect = option_rects[i]
            
            # Couleur spéciale pour les nouvelles armes
            if option.get("is_new_weapon", False):
                # Jaune doré pour les nouvelles armes
                color = (255, 215, 0) if not self.ban_mode else (255, 180, 100)
            else:
                color = (180,220,255) if not self.ban_mode else (255,120,120)
                
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            
            # Texte standardisé sur 2 lignes avec même police
            text_color = self.config.BLACK if not option.get("is_new_weapon", False) else (139, 69, 19)
            
            # Séparer le texte par le caractère "|" pour 2 lignes uniformes
            name = option["name"]
            if "|" in name:
                lines = name.split("|")
                line1 = lines[0].strip()
                line2 = lines[1].strip()
            else:
                # Fallback pour les anciens formats
                if len(name) > 15:
                    words = name.split()
                    if len(words) > 1:
                        mid = len(words) // 2
                        line1 = " ".join(words[:mid])
                        line2 = " ".join(words[mid:])
                    else:
                        line1 = name[:15]
                        line2 = name[15:]
                else:
                    line1 = name
                    line2 = ""
            
            # Affichage sur 2 lignes avec la même police (small_font pour uniformité)
            line1_surface = self.small_font.render(line1, True, text_color)
            line1_rect = line1_surface.get_rect(center=(rect.centerx, rect.centery - 18))
            self.screen.blit(line1_surface, line1_rect)
            
            if line2:  # Afficher la deuxième ligne seulement si elle existe
                line2_surface = self.small_font.render(line2, True, text_color)
                line2_rect = line2_surface.get_rect(center=(rect.centerx, rect.centery + 18))
                self.screen.blit(line2_surface, line2_rect)
        
        # Boutons ROLL, BAN, SKIP en haut de l'écran (recentrés)
        btn_w, btn_h = 180, 72  # Agrandis : 120->180, 48->72
        btn_y = overlay_y + 30  # En haut de l'overlay
        
        # Si pas d'options disponibles, afficher message et bouton "Always Skip"
        if len(self.upgrade_options) == 0:
            # Message d'information
            no_options_text = "🎯 Toutes les améliorations disponibles sont au maximum !"
            no_options_surface = self.font.render(no_options_text, True, self.config.WHITE)
            no_options_rect = no_options_surface.get_rect(center=(screen_w//2, screen_h//2))
            self.screen.blit(no_options_surface, no_options_rect)
            
            # Bouton "Always Skip" à droite des autres boutons
            always_skip_rect = pygame.Rect(screen_w//2+320, btn_y, btn_w, btn_h)
            pygame.draw.rect(self.screen, (100,200,100), always_skip_rect, border_radius=10)
            always_skip_surface = self.font.render("ALWAYS SKIP", True, self.config.BLACK)
            always_skip_rect_center = always_skip_surface.get_rect(center=always_skip_rect.center)
            self.screen.blit(always_skip_surface, always_skip_rect_center)
        
        # ROLL (recentré) - désactivé s'il n'y a pas d'options
        roll_rect = pygame.Rect(screen_w//2-320, btn_y, btn_w, btn_h)
        roll_enabled = self.roll_count > 0 and not self.ban_mode and len(self.upgrade_options) > 0
        roll_color = (200,200,200) if roll_enabled else (100,100,100)
        pygame.draw.rect(self.screen, roll_color, roll_rect, border_radius=10)
        roll_text = f"ROLL ({self.roll_count})"
        roll_surface = self.font.render(roll_text, True, self.config.BLACK)
        roll_rect_center = roll_surface.get_rect(center=roll_rect.center)
        self.screen.blit(roll_surface, roll_rect_center)
        
        # BAN (centre) - désactivé s'il n'y a pas d'options
        ban_rect = pygame.Rect(screen_w//2-90, btn_y, btn_w, btn_h)
        ban_enabled = self.ban_count > 0 and not self.ban_mode and len(self.upgrade_options) > 0
        ban_color = (200,100,100) if ban_enabled else (100,50,50)
        pygame.draw.rect(self.screen, ban_color, ban_rect, border_radius=10)
        ban_text = f"BAN ({self.ban_count})"
        ban_surface = self.font.render(ban_text, True, self.config.BLACK)
        ban_rect_center = ban_surface.get_rect(center=ban_rect.center)
        self.screen.blit(ban_surface, ban_rect_center)
        
        # SKIP (recentré)
        skip_rect = pygame.Rect(screen_w//2+140, btn_y, btn_w, btn_h)
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
        
        # Si c'est le joueur, passer l'état du bouclier
        if entity == self.player:
            entity.draw(self.screen, shield_hits=self.bonus_manager.shield_hits_remaining)
        else:
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
        
        # Dessiner les projectiles ennemis
        for projectile in self.enemy_projectiles:
            self.draw_entity_with_camera_offset(projectile, camera_x, camera_y)
        
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
        
        # Dessiner les particules de soudure (au premier plan pour effet brillant)
        for welding_particle in self.welding_particles:
            self.draw_entity_with_camera_offset(welding_particle, camera_x, camera_y)
        
        # Dessiner les orb
        for orb in self.energy_orbs:
            self.draw_entity_with_camera_offset(orb, camera_x, camera_y)
        
        # Dessiner les effets de mort (au premier plan, avant le joueur)
        for death_effect in self.death_effects:
            death_effect.draw(self.screen, camera_x, camera_y)
        
        # Dessiner les effets de mort par orbe
        for orb_death_effect in self.orb_death_effects:
            orb_death_effect.draw(self.screen, camera_x, camera_y)
        
        # Dessiner les effets de mort par beam (cendres)
        for beam_death_effect in self.beam_death_effects:
            beam_death_effect.draw(self.screen, camera_x, camera_y)
        
        # Dessiner les collectibles (coeurs, etc.)
        for collectible in self.collectibles:
            collectible.draw(self.screen, camera_x, camera_y)
        
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
                        # Créer effet de mort pour les ennemis spéciaux
                        if enemy.is_special:
                            death_effect = DeathEffect(enemy.x, enemy.y, self.config)
                            self.death_effects.append(death_effect)
                        
                        # Appliquer bonus si c'est un ennemi spécial
                        if enemy.is_special and enemy.bonus_type:
                            self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                        
                        # Vérifier que l'ennemi est encore dans la liste
                        if enemy in self.enemies:
                            # Gérer les drops avant de supprimer l'ennemi
                            self.handle_enemy_drops(enemy)
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1  # Incrémenter les statistiques
                        self.score += self.config.SCORE_PER_ENEMY_KILL
                    break
        
        # Supprimer les zaps marqués pour suppression
        for zap in zaps_to_remove:
            if zap in self.zaps:
                self.zaps.remove(zap)
        
        # Mettre à jour et gérer les collisions des projectiles ennemis
        projectiles_to_remove = []
        for projectile in self.enemy_projectiles:
            projectile.update()
            
            # Vérifier si hors limites
            if not (camera_bounds['left'] <= projectile.x <= camera_bounds['right'] and 
                    camera_bounds['top'] <= projectile.y <= camera_bounds['bottom']):
                projectiles_to_remove.append(projectile)
                continue
            
            # Collision avec le joueur
            if self.check_collision(projectile, self.player):
                # Vérifier si le joueur peut subir des dégâts (bouclier, invincibilité)
                if self.bonus_manager.can_take_damage():
                    self.player.take_damage(projectile.damage, self.skill_manager)
                    
                    # Vérifier si le joueur est mort
                    if self.player.health <= 0:
                        self.player.health = 0
                        self.transition_to_game_over()
                
                projectiles_to_remove.append(projectile)
        
        # Supprimer les projectiles marqués pour suppression
        for projectile in projectiles_to_remove:
            if projectile in self.enemy_projectiles:
                self.enemy_projectiles.remove(projectile)
        
        # Nettoyer les éclairs (ils se suppriment automatiquement via update())
        self.lightnings = [lightning for lightning in self.lightnings if lightning.update()]
        
        # Mettre à jour et gérer les collisions des beams
        active_beams = []
        for beam in self.beams:
            if beam.update():
                # Vérifier les collisions avec les ennemis
                hit_positions = beam.check_collision_with_enemies(self.enemies, self)
                # Créer des effets d'explosion pour chaque ennemi touché
                for x, y in hit_positions:
                    self.create_explosion_particles(x, y)
                active_beams.append(beam)
        self.beams = active_beams
        
        # Supprimer les ennemis morts tués par les beams
        enemies_to_remove = []
        for enemy in self.enemies:
            if enemy.health <= 0:
                # Créer effet de mort pour les ennemis spéciaux
                if enemy.is_special:
                    death_effect = DeathEffect(enemy.x, enemy.y, self.config)
                    self.death_effects.append(death_effect)
                
                # Appliquer bonus si c'est un ennemi spécial
                if enemy.is_special and enemy.bonus_type:
                    self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                
                # Gérer les drops avant de supprimer l'ennemi
                self.handle_enemy_drops(enemy)
                enemies_to_remove.append(enemy)
                self.enemies_killed += 1  # Incrémenter les statistiques
                self.score += self.config.SCORE_PER_ENEMY_KILL
        
        # Supprimer les ennemis morts de la liste
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
        
        # Nettoyer les particules (elles se suppriment automatiquement via update())
        self.particles = [particle for particle in self.particles if particle.update()]
        
        # Nettoyer les particules de soudure (elles se suppriment automatiquement via update())
        self.welding_particles = [particle for particle in self.welding_particles if particle.update()]
        
        # Mettre à jour et nettoyer les effets de mort
        for death_effect in self.death_effects[:]:
            death_effect.update()
            if death_effect.is_finished:
                self.death_effects.remove(death_effect)
        
        # Mettre à jour et nettoyer les effets de mort par orbe
        for orb_death_effect in self.orb_death_effects[:]:
            if not orb_death_effect.update():
                self.orb_death_effects.remove(orb_death_effect)
        
        # Mettre à jour et nettoyer les effets de mort par beam
        for beam_death_effect in self.beam_death_effects[:]:
            if not beam_death_effect.update():
                self.beam_death_effects.remove(beam_death_effect)
        
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
                        # Calculer la direction de l'orbe pour l'effet de repousse
                        orb_direction_x = orb.x - player_center_x
                        orb_direction_y = orb.y - player_center_y
                        
                        # Créer l'effet de mort par orbe (repousse et fade rouge)
                        orb_death_effect = OrbDeathEffect(enemy, orb_direction_x, orb_direction_y, self.config)
                        self.orb_death_effects.append(orb_death_effect)
                        
                        # Créer effet de mort pour les ennemis spéciaux
                        if enemy.is_special:
                            death_effect = DeathEffect(enemy.x, enemy.y, self.config)
                            self.death_effects.append(death_effect)
                        
                        # Appliquer bonus si c'est un ennemi spécial
                        if enemy.is_special and enemy.bonus_type:
                            self.bonus_manager.apply_bonus(enemy.bonus_type, self)
                        
                        # Vérifier que l'ennemi est encore dans la liste
                        if enemy in self.enemies:
                            # Gérer les drops avant de supprimer l'ennemi
                            self.handle_enemy_drops(enemy)
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
        
        elif upgrade_id == "weapon_orb":
            if self.weapon_manager.add_weapon(OrbWeapon):
                print("ORB DÉBLOQUÉ ! Nouvelle arme disponible !")
            else:
                print("Impossible d'ajouter Orb : limite d'armes atteinte")
        
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
        
        elif upgrade_id == "skill_regen":
            if self.skill_manager.add_skill(RegenSkill):
                print("COMPÉTENCE RÉGÉNÉRATION DÉBLOQUÉE !")
            else:
                print("Impossible d'ajouter Régénération : limite de compétences atteinte")
        
        elif upgrade_id == "skill_magnet":
            if self.skill_manager.add_skill(MagnetSkill):
                print("COMPÉTENCE AIMANT DÉBLOQUÉE !")
            else:
                print("Impossible d'ajouter Aimant : limite de compétences atteinte")
        
        elif upgrade_id == "skill_shield":
            if self.skill_manager.add_skill(ShieldSkill):
                print("COMPÉTENCE BOUCLIER DÉBLOQUÉE !")
            else:
                print("Impossible d'ajouter Bouclier : limite de compétences atteinte")
        
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
                "name": "DÉBLOQUER|LIGHTNING", 
                "description": "Nouvelle arme: Lightning instantanés avec chaînage !",
                "is_new_weapon": True
            })
        
        if not self.weapon_manager.has_weapon("Orb") and len(self.weapon_manager.weapons) < 7:
            available_upgrades.append({
                "id": "weapon_orb", 
                "name": "DÉBLOQUER|ORB", 
                "description": "Nouvelle arme: Boules d'énergie orbitales !",
                "is_new_weapon": True
            })
        
        if not self.weapon_manager.has_weapon("Beam") and len(self.weapon_manager.weapons) < 7:
            available_upgrades.append({
                "id": "weapon_beam", 
                "name": "DÉBLOQUER|BEAM", 
                "description": "Nouvelle arme: Rayon laser qui traverse les ennemis !",
                "is_new_weapon": True
            })
        
        # === AMÉLIORATIONS D'ARMES EXISTANTES ===
        for weapon in self.weapon_manager.weapons:
            if weapon.level < weapon.max_level:
                available_upgrades.append({
                    "id": f"upgrade_weapon_{weapon.name.lower()}", 
                    "name": f"AMÉLIORER|{weapon.name.upper()} NIV.{weapon.level + 1}", 
                    "description": f"Améliore {weapon.name} (actuellement niveau {weapon.level})",
                    "is_new_weapon": False
                })
        
        # === NOUVELLES COMPÉTENCES ===
        if not self.skill_manager.has_skill("Vitesse") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_speed", 
                "name": "COMPÉTENCE|VITESSE", 
                "description": "Nouvelle compétence: Augmente la vitesse de déplacement !",
                "is_new_weapon": True
            })
        
        if not self.skill_manager.has_skill("Régénération") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_regen", 
                "name": "COMPÉTENCE|RÉGÉNÉRATION", 
                "description": "Nouvelle compétence: Récupère la vie au fil du temps !",
                "is_new_weapon": True
            })
        
        if not self.skill_manager.has_skill("Aimant") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_magnet", 
                "name": "COMPÉTENCE|AIMANT", 
                "description": "Nouvelle compétence: Attire automatiquement les objets collectibles !",
                "is_new_weapon": True
            })
        
        if not self.skill_manager.has_skill("Bouclier") and len(self.skill_manager.skills) < 14:
            available_upgrades.append({
                "id": "skill_shield", 
                "name": "COMPÉTENCE|BOUCLIER", 
                "description": "Nouvelle compétence: Donne des points de bouclier temporaires !",
                "is_new_weapon": True
            })
        
        # === AMÉLIORATIONS DE COMPÉTENCES EXISTANTES ===
        for skill in self.skill_manager.skills:
            if skill.level < skill.max_level:
                available_upgrades.append({
                    "id": f"upgrade_skill_{skill.name.lower()}", 
                    "name": f"AMÉLIORER|{skill.name.upper()} NIV.{skill.level + 1}", 
                    "description": f"Améliore {skill.name} (actuellement niveau {skill.level})",
                    "is_new_weapon": False
                })
        
        # === FILTRAGE DES OPTIONS BANNIES ===
        # Exclure les options qui ont été bannies pendant cette partie
        filtered_upgrades = []
        banned_count = 0
        for upgrade in available_upgrades:
            if upgrade["name"] not in self.banned_upgrades:
                filtered_upgrades.append(upgrade)
            else:
                banned_count += 1
        
        # Debug: Afficher le nombre d'options filtrées
        if banned_count > 0:
            print(f"🚫 {banned_count} option(s) bannie(s) exclue(s). Restantes: {len(filtered_upgrades)}")
        
        # Retourner 3 options aléatoirement choisies (ou moins s'il n'y en a pas assez)
        result = random.sample(filtered_upgrades, min(3, len(filtered_upgrades)))
        return result
    
    def get_upgrade_combined_rects(self):
        # Retourne les rects englobants (icône + bouton) pour chaque option
        screen_w, screen_h = self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT
        
        # Calculer les dimensions pour englober icône + bouton + marge
        icon_rects = self.get_upgrade_icon_rects()
        option_rects = self.get_upgrade_option_rects()
        
        combined_rects = []
        for i in range(3):
            icon_rect = icon_rects[i]
            option_rect = option_rects[i]
            
            # Calculer le rectangle englobant avec marge
            left = min(icon_rect.left, option_rect.left) - 10
            top = icon_rect.top - 10
            right = max(icon_rect.right, option_rect.right) + 10
            bottom = option_rect.bottom + 10
            
            combined_rect = pygame.Rect(left, top, right - left, bottom - top)
            combined_rects.append(combined_rect)
        
        return combined_rects
