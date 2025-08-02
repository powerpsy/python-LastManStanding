"""
Carte de démarrage interactive
=============================

Menu principal sous forme de carte 2D où le joueur peut se déplacer vers différentes zones
pour accéder aux options du jeu.
"""

import pygame
import math
from entities import Player
from background import Background
from player_profiles import PlayerProfileManager


class PlayerSelector:
    """Gère la sélection visuelle des joueurs"""
    
    def __init__(self, config):
        self.config = config
        self.selected_player_id = 1  # ID du joueur sélectionné
        self.player_sprites = {}
        self.player_entities = {}  # Entités Player pour l'animation
        self.animation_time = 0.0
        self.load_player_sprites()
    
    def load_player_sprites(self):
        """Charge les sprites des 3 joueurs et crée des entités pour l'animation"""
        sprite_configs = {
            1: ("assets/player/player2.png", 1),  # Guerrier
            2: ("assets/player/player3.png", 2),  # Mage  
            3: ("assets/player/player4.png", 3)   # Assassin
        }
        
        for player_id, (sprite_path, sprite_type) in sprite_configs.items():
            try:
                # Créer une configuration complète en copiant la config principale
                temp_config = type('TempConfig', (), {})()
                
                # Copier tous les attributs nécessaires de la config principale
                for attr in dir(self.config):
                    if not attr.startswith('_'):
                        setattr(temp_config, attr, getattr(self.config, attr))
                
                # Modifier les attributs spécifiques
                temp_config.PLAYER_SPRITE_TYPE = sprite_type
                temp_config.PLAYER_SIZE = 64  # Taille plus grande pour l'affichage
                
                # Créer le joueur temporaire
                temp_player = Player(0, 0, temp_config)
                self.player_entities[player_id] = temp_player
                
                print(f"Entité joueur {player_id} créée pour animation")
            except Exception as e:
                print(f"Erreur création entité joueur {player_id}: {e}")
                # Créer un sprite de remplacement simple
                fallback_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
                color = [(255, 100, 100), (100, 255, 100), (100, 100, 255)][player_id - 1]
                pygame.draw.circle(fallback_sprite, color, (32, 32), 30)
                self.player_sprites[player_id] = fallback_sprite
    
    def update(self, dt):
        """Met à jour les animations des joueurs"""
        self.animation_time += dt
        
        # Mettre à jour les animations de tous les joueurs
        for player_id, player_entity in self.player_entities.items():
            if hasattr(player_entity, 'update'):
                # Créer un objet simulant les touches pressées pour forcer l'animation
                class FakeKeys:
                    def __getitem__(self, key):
                        # Simuler une touche pressée pour déclencher l'animation
                        import pygame
                        if key == pygame.K_DOWN:  # Toujours "presser" la touche BAS
                            return True
                        return False
                
                fake_keys = FakeKeys()
                
                # Forcer l'animation en simulant un mouvement
                old_x, old_y = player_entity.x, player_entity.y
                player_entity.vel_x = 0
                player_entity.vel_y = 0.1  # Très léger mouvement pour déclencher l'animation
                
                # Mettre à jour avec les fausses touches (Player.update prend seulement keys)
                player_entity.update(fake_keys)
                
                # Restaurer la position exacte (pas de mouvement réel)
                player_entity.x, player_entity.y = old_x, old_y
    
    def draw(self, screen, zone_x, zone_y, zone_width, zone_height):
        """Dessine la sélection de joueur dans la zone spécifiée"""
        # Dessiner le titre "SELECTION DU JOUEUR" en haut de la zone
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render("SELECTION DU JOUEUR", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(zone_x + zone_width // 2, zone_y + 25))
        screen.blit(title_text, title_rect)
        
        # Calculer la disposition des sprites avec ajustement pour le titre
        sprite_size = 64
        spacing = 120  # Espacement entre sprites
        total_width_needed = 3 * sprite_size + 2 * spacing  # 3 sprites + 2 espaces
        start_x = zone_x + (zone_width - total_width_needed) // 2
        # Positionner les sprites en tenant compte du titre (centrage dans l'espace restant)
        remaining_height = zone_height - 50  # 50px pour le titre
        sprite_y = zone_y + 50 + (remaining_height - sprite_size) // 2
        
        for player_id in range(1, 4):
            # Calculer la position X de chaque sprite avec espacement fixe
            sprite_x = start_x + (player_id - 1) * (sprite_size + spacing)  # 120px d'espacement entre sprites
            
            # Couleur de fond selon la sélection
            if player_id == self.selected_player_id:
                # Joueur sélectionné : fond doré animé avec cadre plus grand
                import math
                glow_intensity = int(200 + 55 * abs(math.cos(self.animation_time * 3)))
                selection_rect = pygame.Rect(sprite_x - 25, sprite_y - 25, sprite_size + 50, sprite_size + 50)
                pygame.draw.rect(screen, (glow_intensity, glow_intensity // 2, 0), selection_rect, 5)
                pygame.draw.rect(screen, (255, 255, 255, 50), selection_rect.inflate(-10, -10))
            else:
                # Joueur non sélectionné : fond gris discret avec cadre plus grand
                selection_rect = pygame.Rect(sprite_x - 20, sprite_y - 20, sprite_size + 40, sprite_size + 40)
                pygame.draw.rect(screen, (100, 100, 100), selection_rect, 2)
            
            # Dessiner l'entité animée du joueur
            if player_id in self.player_entities:
                player_entity = self.player_entities[player_id]
                # Sauvegarder la position originale
                orig_x, orig_y = player_entity.x, player_entity.y
                # Positionner temporairement pour le dessin
                player_entity.x = sprite_x
                player_entity.y = sprite_y
                # Dessiner le joueur animé
                player_entity.draw(screen)
                # Restaurer la position originale
                player_entity.x, player_entity.y = orig_x, orig_y
            
            # Nom du profil sous le sprite (plus bas)
            from player_profiles import PlayerProfileManager
            profile = PlayerProfileManager.get_profile(player_id)
            name_font = pygame.font.Font(None, 24)
            name_text = name_font.render(profile.name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(sprite_x + sprite_size // 2, sprite_y + sprite_size + 35))
            screen.blit(name_text, name_rect)
    
    def handle_click(self, zone_x, zone_y, zone_width, zone_height, click_x, click_y):
        """Gère les clics dans la zone de sélection"""
        # Calculer les positions des sprites (même logique que draw)
        sprite_size = 64
        spacing = 120  # Même espacement que dans draw
        total_width_needed = 3 * sprite_size + 2 * spacing
        start_x = zone_x + (zone_width - total_width_needed) // 2
        # Même position Y que dans draw (avec ajustement pour le titre)
        remaining_height = zone_height - 50  # 50px pour le titre
        sprite_y = zone_y + 50 + (remaining_height - sprite_size) // 2
        
        for player_id in range(1, 4):
            sprite_x = start_x + (player_id - 1) * (sprite_size + spacing)
            # Utiliser la même taille de cadre agrandie que dans draw (pour le joueur sélectionné)
            sprite_rect = pygame.Rect(sprite_x - 25, sprite_y - 25, sprite_size + 50, sprite_size + 50)
            
            if sprite_rect.collidepoint(click_x, click_y):
                self.selected_player_id = player_id
                return True
        return False
    
    def get_sprite_positions(self, zone_x, zone_y, zone_width, zone_height):
        """Retourne les positions des sprites pour la détection de collision"""
        sprite_size = 64
        spacing = 120  # Même espacement que dans draw
        total_width_needed = 3 * sprite_size + 2 * spacing
        start_x = zone_x + (zone_width - total_width_needed) // 2
        # Même position Y que dans draw (avec ajustement pour le titre)
        remaining_height = zone_height - 50  # 50px pour le titre
        sprite_y = zone_y + 50 + (remaining_height - sprite_size) // 2
        
        positions = {}
        for player_id in range(1, 4):
            sprite_x = start_x + (player_id - 1) * (sprite_size + spacing)
            positions[player_id] = pygame.Rect(sprite_x, sprite_y, sprite_size, sprite_size)
        
        return positions


from entities import Player
from background import Background


class StartMapZone:
    """Zone interactive sur la carte de démarrage"""
    
    def __init__(self, x, y, width, height, name, description, action, color=(100, 200, 100)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.description = description
        self.action = action  # Action à exécuter quand le joueur entre dans la zone
        self.color = color
        self.hover_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        self.is_hovered = False
        
    def contains_point(self, x, y):
        """Vérifie si le point (x, y) est dans la zone"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, screen, camera_x, camera_y, alpha=120):
        """Dessine la zone sur l'écran"""
        # Calculer la position à l'écran
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Créer une surface avec transparence pour la zone
        zone_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        current_color = self.hover_color if self.is_hovered else self.color
        zone_surface.fill((*current_color, alpha))
        
        screen.blit(zone_surface, (screen_x, screen_y))
        
        # Dessiner le contour
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, border_color, 
                        (screen_x, screen_y, self.width, self.height), 3)


class StartMap:
    """Carte de démarrage interactive avec zones d'action"""
    
    def __init__(self, config):
        self.config = config
        self.tile_size = 64  # Taille d'une tuile
        self.map_width = 50   # 50 tuiles de largeur
        self.map_height = 50  # 50 tuiles de hauteur
        
        # Créer le joueur pour la carte de démarrage
        self.player = Player(
            self.map_width * self.tile_size // 2,
            self.map_height * self.tile_size // 2,
            config
        )
        
        # Créer le sélecteur de joueur
        self.player_selector = PlayerSelector(config)
        
        # Définir le joueur initial selon la config
        initial_player_type = getattr(config, 'PLAYER_SPRITE_TYPE', 1)
        self.player_selector.selected_player_id = initial_player_type
        
        # Appliquer le profil du joueur
        current_profile = self.player_profile
        current_profile.apply_player_stats(self.player, config)
        
        # Accélérer le joueur x4 pour la navigation dans le menu
        self.player.speed *= 4
        
        # Créer un arrière-plan pour la carte de démarrage
        self.background = Background(config)
        
        # Forcer la taille de la carte pour le menu
        self.background.map_width = self.map_width
        self.background.map_height = self.map_height
        
        # Caméra
        self.camera_x = 0
        self.camera_y = 0
        
        # Créer les zones interactives
        self.zones = self._create_zones()
        
        # Zone actuellement survolée
        self.current_zone = None
        
        # Police pour le texte
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Action sélectionnée (None tant qu'aucune zone n'est activée)
        self.selected_action = None
    
    def _create_zones(self):
        """Crée les zones interactives de la carte en disposition pentagonale"""
        zones = []
        
        # Calcul du centre de la carte
        center_x = (self.map_width * self.tile_size) // 2
        center_y = (self.map_height * self.tile_size) // 2
        
        # Paramètres du pentagone
        pentagon_radius = 400  # Rayon du pentagone
        zone_width = 300
        zone_height = 150
        
        # Calcul des positions des 5 sommets d'un pentagone régulier
        # Commencer par le haut (angle -90°) et tourner dans le sens horaire
        import math
        
        # Zone 1: "JOUER" (sommet du haut)
        angle1 = -math.pi / 2  # -90° (haut)
        play_x = center_x + pentagon_radius * math.cos(angle1) - zone_width // 2
        play_y = center_y + pentagon_radius * math.sin(angle1) - zone_height // 2
        play_zone = StartMapZone(
            play_x, play_y, zone_width, zone_height,
            "JOUER", 
            "Commencer une nouvelle partie",
            "play",
            color=(100, 200, 100)
        )
        zones.append(play_zone)
        
        # Zone 2: "SÉLECTION JOUEUR" (haut-droite)
        angle2 = -math.pi / 2 + 2 * math.pi / 5  # -90° + 72°
        player_x = center_x + pentagon_radius * math.cos(angle2) - zone_width // 2
        player_y = center_y + pentagon_radius * math.sin(angle2) - zone_height // 2
        player_select_zone = StartMapZone(
            player_x, player_y, zone_width * 2.5, zone_height * 2.5,  # Encore plus grand
            "",
            "Choisissez votre personnage",
            "player_select",
            color=(200, 180, 100)
        )
        zones.append(player_select_zone)
        
        # Zone 3: "MINI-JEUX" (bas-droite)
        angle3 = -math.pi / 2 + 4 * math.pi / 5  # -90° + 144°
        minigames_x = center_x + pentagon_radius * math.cos(angle3) - zone_width // 2
        minigames_y = center_y + pentagon_radius * math.sin(angle3) - zone_height // 2
        minigames_zone = StartMapZone(
            minigames_x, minigames_y, zone_width, zone_height,
            "MINI-JEUX",
            "Modes de jeu alternatifs",
            "minigames",
            color=(200, 150, 100)
        )
        zones.append(minigames_zone)
        
        # Zone 4: "QUITTER" (bas-gauche)
        angle4 = -math.pi / 2 + 6 * math.pi / 5  # -90° + 216°
        quit_x = center_x + pentagon_radius * math.cos(angle4) - zone_width // 2
        quit_y = center_y + pentagon_radius * math.sin(angle4) - zone_height // 2
        quit_zone = StartMapZone(
            quit_x, quit_y, zone_width, zone_height,
            "QUITTER",
            "Fermer le jeu",
            "quit",
            color=(200, 100, 100)
        )
        zones.append(quit_zone)
        
        # Zone 5: "OPTIONS" (haut-gauche)
        angle5 = -math.pi / 2 + 8 * math.pi / 5  # -90° + 288°
        options_x = center_x + pentagon_radius * math.cos(angle5) - zone_width // 2
        options_y = center_y + pentagon_radius * math.sin(angle5) - zone_height // 2
        options_zone = StartMapZone(
            options_x, options_y, zone_width, zone_height,
            "OPTIONS",
            "Configurer le jeu",
            "options",
            color=(100, 150, 200)
        )
        zones.append(options_zone)
        
        # Zone centrale d'information sur le profil
        profile_zone = StartMapZone(
            center_x - zone_width // 3, center_y - zone_height // 3, 
            zone_width // 1.5, zone_height // 1.5,
            f"PROFIL",
            f"Profil actuel: {self.player_profile.name}",
            "profile_info",
            color=(150, 100, 200)
        )
        zones.append(profile_zone)
        
        return zones
    
    def update(self, dt):
        """Met à jour la carte de démarrage"""
        # Mettre à jour les animations du sélecteur de joueur
        self.player_selector.update(dt)
        
        # Gérer les entrées du joueur
        keys = pygame.key.get_pressed()
        
        # Mouvement du joueur
        vel_x, vel_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x = self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vel_y = -self.player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vel_y = self.player.speed
        
        # Appliquer le mouvement
        self.player.vel_x = vel_x
        self.player.vel_y = vel_y
        
        # Obtenir l'état du clavier pour la méthode update du joueur
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Limiter le joueur aux bordures de la carte
        world_width = self.map_width * self.tile_size
        world_height = self.map_height * self.tile_size
        
        self.player.x = max(0, min(world_width - self.player.size, self.player.x))
        self.player.y = max(0, min(world_height - self.player.size, self.player.y))
        
        # Vérifier les collisions avec les sprites de sélection
        self._check_sprite_collision(keys)
        
        # Mettre à jour la caméra pour suivre le joueur
        self._update_camera()
        
        # Vérifier quelle zone est survolée
        self._check_zone_hover()
        
        # Vérifier les interactions avec les zones
        self._check_zone_interaction()
    
    def _update_camera(self):
        """Met à jour la caméra pour suivre le joueur"""
        # Centrer la caméra sur le joueur
        target_camera_x = self.player.x + self.player.size // 2 - self.config.WINDOW_WIDTH // 2
        target_camera_y = self.player.y + self.player.size // 2 - self.config.WINDOW_HEIGHT // 2
        
        # Limiter la caméra aux bordures de la carte
        world_width = self.map_width * self.tile_size
        world_height = self.map_height * self.tile_size
        
        self.camera_x = max(0, min(world_width - self.config.WINDOW_WIDTH, target_camera_x))
        self.camera_y = max(0, min(world_height - self.config.WINDOW_HEIGHT, target_camera_y))
    
    def _check_sprite_collision(self, keys):
        """Vérifie les collisions avec les sprites de sélection de joueur"""
        # Trouver la zone de sélection de joueur
        player_select_zone = None
        for zone in self.zones:
            if zone.action == "player_select":
                player_select_zone = zone
                break
        
        if not player_select_zone:
            return
        
        # Obtenir les positions des sprites
        sprite_positions = self.player_selector.get_sprite_positions(
            player_select_zone.x, player_select_zone.y, 
            player_select_zone.width, player_select_zone.height
        )
        
        # Rectangle du joueur
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
        
        # Vérifier les collisions avec chaque sprite
        for player_id, sprite_rect in sprite_positions.items():
            if player_rect.colliderect(sprite_rect):
                # Collision détectée ! Vérifier si E ou Space est pressé
                if keys[pygame.K_e] or keys[pygame.K_SPACE]:
                    if self.player_selector.selected_player_id != player_id:
                        self.player_selector.selected_player_id = player_id
                        self._update_player_profile()
                        from player_profiles import PlayerProfileManager
                        print(f"🎮 Profil changé par collision: {PlayerProfileManager.get_profile(player_id).name}")
                        # Attendre un court délai pour éviter les changements répétés
                        import time
                        time.sleep(0.2)
                break
    
    def _check_zone_hover(self):
        """Vérifie quelle zone est survolée par le joueur"""
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        
        # Réinitialiser l'état de survol de toutes les zones
        for zone in self.zones:
            zone.is_hovered = False
        
        # Vérifier quelle zone contient le joueur
        self.current_zone = None
        for zone in self.zones:
            if zone.contains_point(player_center_x, player_center_y):
                zone.is_hovered = True
                self.current_zone = zone
                break
    
    def _check_zone_interaction(self):
        """Vérifie les interactions avec les zones"""
        # Interaction avec Espace ou E
        keys = pygame.key.get_pressed()
        if self.current_zone and (keys[pygame.K_SPACE] or keys[pygame.K_e]):
            self.selected_action = self.current_zone.action
    
    def handle_event(self, event):
        """Gère les événements de la carte de démarrage"""
        if event.type == pygame.KEYDOWN:
            if self.current_zone and (event.key == pygame.K_SPACE or event.key == pygame.K_e):
                # Gestion spéciale pour la zone de sélection de joueur
                if self.current_zone.action == "player_select":
                    # Dans la zone de sélection, E/Space ne fait rien de spécial
                    # L'interaction se fait par clic de souris
                    pass
                else:
                    self.selected_action = self.current_zone.action
                    return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Gestion des clics de souris
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Convertir les coordonnées écran en coordonnées monde
            world_x = mouse_x + self.camera_x
            world_y = mouse_y + self.camera_y
            
            # Vérifier si on clique dans la zone de sélection de joueur
            for zone in self.zones:
                if zone.action == "player_select" and zone.contains_point(world_x, world_y):
                    # Calculer les coordonnées relatives à la zone
                    relative_x = world_x - zone.x
                    relative_y = world_y - zone.y
                    
                    # Passer le clic au sélecteur de joueur
                    if self.player_selector.handle_click(0, 0, zone.width, zone.height, relative_x, relative_y):
                        # Mettre à jour le profil du joueur
                        self._update_player_profile()
                        return True
        return False
    
    def _update_player_profile(self):
        """Met à jour le profil du joueur selon la sélection"""
        selected_id = self.player_selector.selected_player_id
        current_profile = PlayerProfileManager.get_profile(selected_id)
        
        # Sauvegarder la vitesse actuelle (modifiée pour le menu)
        current_speed = self.player.speed
        
        # Appliquer les stats du profil
        current_profile.apply_player_stats(self.player, self.config)
        
        # Restaurer la vitesse du menu (x4)
        self.player.speed = current_speed
        
        # Mettre à jour la zone de profil
        for zone in self.zones:
            if zone.action == "profile_info":
                zone.description = f"Profil actuel: {current_profile.name}"
                break
        
        print(f"🎮 Profil changé: {current_profile.name}")
    
    def draw(self, screen):
        """Dessine la carte de démarrage"""
        # Dessiner l'arrière-plan
        self.background.draw(screen, self.camera_x, self.camera_y)
        
        # Dessiner les zones
        for zone in self.zones:
            zone.draw(screen, self.camera_x, self.camera_y)
            
            # Dessiner la sélection de joueur si c'est la zone appropriée
            if zone.action == "player_select":
                screen_x = zone.x - self.camera_x
                screen_y = zone.y - self.camera_y
                self.player_selector.draw(screen, screen_x, screen_y, zone.width, zone.height)
        
        # Dessiner le joueur avec offset de caméra
        temp_x, temp_y = self.player.x, self.player.y
        self.player.x -= self.camera_x
        self.player.y -= self.camera_y
        self.player.draw(screen)  # La méthode draw du joueur ne prend que screen et optionnellement shield_hits
        self.player.x, self.player.y = temp_x, temp_y
        
        # Dessiner les textes des zones
        self._draw_zone_texts(screen)
        
        # Dessiner l'interface
        self._draw_ui(screen)
    
    def _draw_zone_texts(self, screen):
        """Dessine les textes des zones"""
        for zone in self.zones:
            # Position à l'écran
            screen_x = zone.x - self.camera_x
            screen_y = zone.y - self.camera_y
            
            # Vérifier si la zone est visible à l'écran
            if (screen_x < -zone.width or screen_x > self.config.WINDOW_WIDTH or
                screen_y < -zone.height or screen_y > self.config.WINDOW_HEIGHT):
                continue
            
            # Dessiner le nom de la zone
            text_color = (255, 255, 255) if zone.is_hovered else (200, 200, 200)
            text_surface = self.font_medium.render(zone.name, True, text_color)
            text_rect = text_surface.get_rect(center=(screen_x + zone.width // 2, screen_y + zone.height // 2))
            screen.blit(text_surface, text_rect)
    
    def _draw_ui(self, screen):
        """Dessine l'interface utilisateur"""
        # Titre du jeu en haut
        title_text = self.font_large.render("LAST MAN STANDING", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Informations sur la zone actuelle
        if self.current_zone:
            # Fond semi-transparent pour le texte d'aide
            help_surface = pygame.Surface((self.config.WINDOW_WIDTH, 80), pygame.SRCALPHA)
            help_surface.fill((0, 0, 0, 150))
            screen.blit(help_surface, (0, self.config.WINDOW_HEIGHT - 80))
            
            # Texte d'aide
            help_text = f"{self.current_zone.description}"
            help_surface_text = self.font_medium.render(help_text, True, (255, 255, 255))
            help_rect = help_surface_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT - 50))
            screen.blit(help_surface_text, help_rect)
            
            # Instructions
            instruction_text = "Appuyez sur ESPACE ou E pour sélectionner"
            instruction_surface = self.font_small.render(instruction_text, True, (200, 200, 200))
            instruction_rect = instruction_surface.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT - 20))
            screen.blit(instruction_surface, instruction_rect)
        
        # Instructions de mouvement
        movement_text = "Utilisez WASD ou les flèches pour vous déplacer"
        movement_surface = self.font_small.render(movement_text, True, (150, 150, 150))
        movement_rect = movement_surface.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT - 100))
        screen.blit(movement_surface, movement_rect)
    
    def get_selected_action(self):
        """Retourne l'action sélectionnée et la remet à None"""
        action = self.selected_action
        self.selected_action = None
        return action
    
    @property
    def player_profile(self):
        """Retourne le profil actuellement sélectionné"""
        return PlayerProfileManager.get_profile(self.player_selector.selected_player_id)
