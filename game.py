"""
Moteur principal du jeu Last Man Standing
"""

import pygame
import math
import random
import numpy as np
from entities import Player, Enemy, Zap

class Game:
    def __init__(self, config):
        self.config = config
        
        # Initialisation de Pygame
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, config.UI_FONT_SIZE)
        
        # État du jeu
        self.running = True
        self.paused = False
        self.game_over = False
        self.frame_count = 0
        
        # Entités du jeu
        self.player = Player(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2, config)
        self.enemies = []
        self.zaps = []
        
        # Système de vagues
        self.current_wave = 1
        self.enemies_spawned_this_wave = 0
        self.enemies_to_spawn = config.INITIAL_ENEMIES
        self.wave_start_time = 0
        self.enemies_killed = 0
        
        # Score
        self.score = 0
        
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            self.handle_events()
            
            if not self.paused and not self.game_over:
                self.update()
            
            self.draw()
            self.clock.tick(self.config.FPS)
            self.frame_count += 1
            
    def handle_events(self):
        """Gestion des événements"""
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
        if self.game_over:
            return
            
        keys_pressed = pygame.key.get_pressed()
        
        # Mise à jour du joueur
        self.player.update(keys_pressed, self.frame_count)
        
        # Gestion du tir automatique
        if self.enemies and self.player.can_fire(self.frame_count):
            self.auto_fire()
            
        # Mise à jour des ennemis
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y)
            
            # Collision ennemi-joueur
            if enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(10):  # 10 dégâts par contact
                    self.game_over = True
                self.enemies.remove(enemy)
                
        # Mise à jour des projectiles
        for zap in self.zaps[:]:
            if zap.update():  # Retourne True si hors écran
                self.zaps.remove(zap)
                continue
                
            # Collision zap-ennemi
            for enemy in self.enemies[:]:
                if zap.rect.colliderect(enemy.rect):
                    if enemy.take_damage(zap.damage):
                        self.enemies.remove(enemy)
                        self.enemies_killed += 1
                        self.score += 10 + self.current_wave * 5
                    self.zaps.remove(zap)
                    break
                    
        # Gestion des vagues
        self.manage_waves()
        
    def auto_fire(self):
        """Tir automatique vers l'ennemi le plus proche"""
        if not self.enemies:
            return
            
        # Trouve l'ennemi le plus proche
        closest_enemy = min(self.enemies, 
                           key=lambda e: math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2))
        
        # Crée un projectile
        zap = Zap(self.player.x, self.player.y, closest_enemy.x, closest_enemy.y, self.config)
        self.zaps.append(zap)
        self.player.fire(self.frame_count)
        
    def manage_waves(self):
        """Gestion du système de vagues"""
        # Si tous les ennemis de la vague sont tués, commence la suivante
        if len(self.enemies) == 0 and self.enemies_spawned_this_wave >= self.enemies_to_spawn:
            self.start_next_wave()
            
        # Spawn d'ennemis pour la vague actuelle
        elif self.enemies_spawned_this_wave < self.enemies_to_spawn:
            if self.frame_count - self.wave_start_time > 60:  # Délai entre les spawns
                self.spawn_enemy()
                self.wave_start_time = self.frame_count
                
    def start_next_wave(self):
        """Démarre la vague suivante"""
        self.current_wave += 1
        self.enemies_to_spawn = self.config.INITIAL_ENEMIES + (self.current_wave - 1) * self.config.ENEMIES_PER_WAVE
        self.enemies_spawned_this_wave = 0
        self.wave_start_time = self.frame_count
        
        # Bonus de score pour survivre à une vague
        self.score += 50 * self.current_wave
        
    def spawn_enemy(self):
        """Fait apparaître un nouvel ennemi"""
        # Position aléatoire sur les bords de l'écran
        side = random.randint(0, 3)
        if side == 0:  # Haut
            x = random.randint(0, self.config.WINDOW_WIDTH)
            y = -20
        elif side == 1:  # Droite
            x = self.config.WINDOW_WIDTH + 20
            y = random.randint(0, self.config.WINDOW_HEIGHT)
        elif side == 2:  # Bas
            x = random.randint(0, self.config.WINDOW_WIDTH)
            y = self.config.WINDOW_HEIGHT + 20
        else:  # Gauche
            x = -20
            y = random.randint(0, self.config.WINDOW_HEIGHT)
            
        enemy = Enemy(x, y, self.config, self.current_wave)
        self.enemies.append(enemy)
        self.enemies_spawned_this_wave += 1
        
    def draw(self):
        """Dessine tous les éléments du jeu"""
        # Fond
        self.screen.fill(self.config.BLACK)
        
        if not self.game_over:
            # Dessine les entités
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            for zap in self.zaps:
                zap.draw(self.screen)
                
        # Interface utilisateur
        self.draw_ui()
        
        # Pause
        if self.paused:
            self.draw_pause_screen()
            
        # Game Over
        if self.game_over:
            self.draw_game_over_screen()
            
        pygame.display.flip()
        
    def draw_ui(self):
        """Dessine l'interface utilisateur"""
        margin = self.config.UI_MARGIN
        
        # Santé du joueur
        health_text = f"Santé: {self.player.health}/{self.player.max_health}"
        health_surface = self.font.render(health_text, True, self.config.UI_COLOR)
        self.screen.blit(health_surface, (margin, margin))
        
        # Barre de santé
        bar_width = 200
        bar_height = 20
        bar_x = margin
        bar_y = margin + 30
        
        # Fond de la barre
        pygame.draw.rect(self.screen, self.config.DARK_GRAY, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Barre de santé
        health_ratio = self.player.health / self.player.max_health
        health_bar_width = int(bar_width * health_ratio)
        
        # Couleur selon la santé
        if health_ratio > 0.6:
            health_color = self.config.GREEN
        elif health_ratio > 0.3:
            health_color = self.config.YELLOW
        else:
            health_color = self.config.RED
            
        pygame.draw.rect(self.screen, health_color, 
                        (bar_x, bar_y, health_bar_width, bar_height))
        
        # Vague actuelle
        wave_text = f"Vague: {self.current_wave}"
        wave_surface = self.font.render(wave_text, True, self.config.UI_COLOR)
        self.screen.blit(wave_surface, (margin, bar_y + 40))
        
        # Ennemis restants
        enemies_text = f"Ennemis: {len(self.enemies)}"
        enemies_surface = self.font.render(enemies_text, True, self.config.UI_COLOR)
        self.screen.blit(enemies_surface, (margin, bar_y + 70))
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, self.config.UI_COLOR)
        self.screen.blit(score_surface, (margin, bar_y + 100))
        
        # Instructions
        if self.current_wave == 1 and len(self.enemies) < 2:
            instructions = [
                "WASD/ZQSD - Déplacer",
                "Tir automatique vers les ennemis",
                "P - Pause",
                "ESC - Quitter"
            ]
            
            for i, instruction in enumerate(instructions):
                text_surface = self.font.render(instruction, True, self.config.GRAY)
                self.screen.blit(text_surface, 
                               (self.config.WINDOW_WIDTH - 300, margin + i * 25))
                
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
        pause_rect = pause_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 
                                                   self.config.WINDOW_HEIGHT//2))
        self.screen.blit(pause_surface, pause_rect)
        
        # Instructions
        instruction_text = "Appuyez sur P pour reprendre"
        instruction_surface = self.font.render(instruction_text, True, self.config.GRAY)
        instruction_rect = instruction_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 
                                                               self.config.WINDOW_HEIGHT//2 + 50))
        self.screen.blit(instruction_surface, instruction_rect)
        
    def draw_game_over_screen(self):
        """Dessine l'écran de game over"""
        # Overlay semi-transparent
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(self.config.RED)
        self.screen.blit(overlay, (0, 0))
        
        # Texte de game over
        game_over_text = "GAME OVER"
        game_over_surface = self.font.render(game_over_text, True, self.config.WHITE)
        game_over_rect = game_over_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 
                                                           self.config.WINDOW_HEIGHT//2 - 50))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # Score final
        final_score_text = f"Score final: {self.score}"
        final_score_surface = self.font.render(final_score_text, True, self.config.WHITE)
        final_score_rect = final_score_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 
                                                               self.config.WINDOW_HEIGHT//2))
        self.screen.blit(final_score_surface, final_score_rect)
        
        # Vague atteinte
        wave_text = f"Vague atteinte: {self.current_wave}"
        wave_surface = self.font.render(wave_text, True, self.config.WHITE)
        wave_rect = wave_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 
                                                 self.config.WINDOW_HEIGHT//2 + 30))
        self.screen.blit(wave_surface, wave_rect)
        
        # Instructions
        restart_text = "R - Recommencer | ESC - Quitter"
        restart_surface = self.font.render(restart_text, True, self.config.GRAY)
        restart_rect = restart_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, 
                                                       self.config.WINDOW_HEIGHT//2 + 80))
        self.screen.blit(restart_surface, restart_rect)
        
    def restart_game(self):
        """Redémarre le jeu"""
        self.game_over = False
        self.paused = False
        self.frame_count = 0
        
        # Reset du joueur
        self.player = Player(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2, self.config)
        
        # Reset des entités
        self.enemies = []
        self.zaps = []
        
        # Reset du système de vagues
        self.current_wave = 1
        self.enemies_spawned_this_wave = 0
        self.enemies_to_spawn = self.config.INITIAL_ENEMIES
        self.wave_start_time = 0
        self.enemies_killed = 0
        
        # Reset du score
        self.score = 0
        
    def add_player(self, name, player_type="human"):
        """Ajoute un joueur à la partie"""
        player = Player(name, player_type)
        self.players.append(player)
        return player
    
    def setup_game(self):
        """Configure la partie"""
        print("🎮 === LAST MAN STANDING === 🎮")
        print("Bienvenue dans ce jeu de bataille royale !")
        print()
        
        # Demande le nombre de joueurs
        while True:
            try:
                num_players = int(input("Combien de joueurs au total (2-10) ? "))
                if 2 <= num_players <= 10:
                    break
                else:
                    print("Veuillez entrer un nombre entre 2 et 10.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Demande le nombre de joueurs humains
        while True:
            try:
                human_players = int(input(f"Combien de joueurs humains (1-{num_players}) ? "))
                if 1 <= human_players <= num_players:
                    break
                else:
                    print(f"Veuillez entrer un nombre entre 1 et {num_players}.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Crée les joueurs humains
        for i in range(human_players):
            name = input(f"Nom du joueur {i+1} : ").strip()
            if not name:
                name = f"Joueur{i+1}"
            self.add_player(name, "human")
        
        # Crée les joueurs IA
        ai_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota"]
        for i in range(num_players - human_players):
            ai_name = ai_names[i] if i < len(ai_names) else f"IA{i+1}"
            self.add_player(ai_name, "ai")
        
        print(f"\n🏁 Partie créée avec {len(self.players)} joueurs !")
        self.display_players_stats()
    
    def display_map(self):
        """Affiche la carte avec les positions des joueurs"""
        print(f"\n📍 CARTE (Zone sûre: rayon {self.zone_size//2} du centre):")
        
        # Crée une grille vide
        grid = [['.' for _ in range(self.map_size)] for _ in range(self.map_size)]
        
        # Place les joueurs sur la grille
        for i, player in enumerate(self.players):
            if player.is_alive:
                symbol = str(i + 1) if player.player_type == "human" else chr(65 + i - len([p for p in self.players if p.player_type == "human"]))
                grid[player.position_y][player.position_x] = symbol
        
        # Affiche la grille
        print("  " + "".join([str(i) for i in range(self.map_size)]))
        for y in range(self.map_size):
            print(f"{y} " + "".join(grid[y]))
        
        print("\nLégende: Joueurs humains = 1,2,3... | IA = A,B,C... | Vide = .")
    
    def display_players_stats(self):
        """Affiche les statistiques de tous les joueurs"""
        print("\n📊 ÉTAT DES JOUEURS:")
        for i, player in enumerate(self.players):
            status_emoji = "❤️" if player.is_alive else "💀"
            player_type_emoji = "👤" if player.player_type == "human" else "🤖"
            print(f"{i+1}. {status_emoji} {player_type_emoji} {player.get_status()}")
    
    def shrink_zone(self):
        """Rétrécit la zone sûre et inflige des dégâts aux joueurs en dehors"""
        if self.round_number > 0 and self.round_number % 3 == 0:
            self.zone_size = max(3, self.zone_size - 1)
            print(f"⚠️ LA ZONE SE RÉTRÉCIT ! Nouvelle taille: {self.zone_size}x{self.zone_size}")
            
            # Inflige des dégâts aux joueurs en dehors de la zone
            for player in self.players:
                if player.is_alive:
                    distance_from_center = max(
                        abs(player.position_x - self.zone_center_x),
                        abs(player.position_y - self.zone_center_y)
                    )
                    if distance_from_center > self.zone_size // 2:
                        damage = 20
                        player.take_damage(damage)
                        print(f"💥 {player.name} subit {damage} dégâts de zone !")
                        if not player.is_alive:
                            print(f"💀 {player.name} est éliminé par la zone !")
    
    def get_alive_players(self):
        """Retourne la liste des joueurs vivants"""
        return [p for p in self.players if p.is_alive]
    
    def get_nearby_players(self, player, max_distance=1.5):
        """Retourne les joueurs à portée d'attaque"""
        nearby = []
        for other in self.players:
            if other != player and other.is_alive and player.distance_to(other) <= max_distance:
                nearby.append(other)
        return nearby
    
    def player_turn(self, player):
        """Gère le tour d'un joueur"""
        if not player.is_alive:
            return
        
        if player.player_type == "ai":
            player.ai_action(self.players)
            return
        
        print(f"\n🎯 Tour de {player.name}")
        print(f"Santé: {player.health}/{player.max_health} HP")
        print(f"Position: ({player.position_x}, {player.position_y})")
        
        while True:
            print("\nActions disponibles:")
            print("1. Se déplacer")
            print("2. Attaquer")
            print("3. Se soigner")
            print("4. Passer le tour")
            print("5. Afficher la carte")
            print("6. Afficher les stats des joueurs")
            
            try:
                choice = int(input("Votre choix (1-6) : "))
                
                if choice == 1:
                    self.handle_movement(player)
                    break
                elif choice == 2:
                    if self.handle_attack(player):
                        break
                elif choice == 3:
                    player.heal()
                    print(f"💚 {player.name} se soigne ! Santé: {player.health}/{player.max_health} HP")
                    break
                elif choice == 4:
                    print(f"⏭️ {player.name} passe son tour.")
                    break
                elif choice == 5:
                    self.display_map()
                elif choice == 6:
                    self.display_players_stats()
                else:
                    print("Choix invalide. Veuillez choisir entre 1 et 6.")
                    
            except ValueError:
                print("Veuillez entrer un nombre valide.")
    
    def handle_movement(self, player):
        """Gère le déplacement d'un joueur"""
        print("\nDéplacement:")
        print("1. Nord (↑)")
        print("2. Sud (↓)")
        print("3. Est (→)")
        print("4. Ouest (←)")
        print("5. Nord-Est (↗)")
        print("6. Nord-Ouest (↖)")
        print("7. Sud-Est (↘)")
        print("8. Sud-Ouest (↙)")
        
        directions = {
            1: (0, -1),   # Nord
            2: (0, 1),    # Sud
            3: (1, 0),    # Est
            4: (-1, 0),   # Ouest
            5: (1, -1),   # Nord-Est
            6: (-1, -1),  # Nord-Ouest
            7: (1, 1),    # Sud-Est
            8: (-1, 1)    # Sud-Ouest
        }
        
        try:
            direction = int(input("Direction (1-8) : "))
            if direction in directions:
                dx, dy = directions[direction]
                old_pos = (player.position_x, player.position_y)
                player.move(dx, dy, self.map_size)
                print(f"🚶 {player.name} se déplace de {old_pos} vers ({player.position_x}, {player.position_y})")
            else:
                print("Direction invalide.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    def handle_attack(self, player):
        """Gère l'attaque d'un joueur"""
        nearby_enemies = self.get_nearby_players(player)
        
        if not nearby_enemies:
            print("❌ Aucun ennemi à portée d'attaque !")
            return False
        
        print("\nEnnemis à portée:")
        for i, enemy in enumerate(nearby_enemies):
            print(f"{i+1}. {enemy.name} - {enemy.health}/{enemy.max_health} HP")
        
        try:
            choice = int(input("Qui attaquer ? ")) - 1
            if 0 <= choice < len(nearby_enemies):
                target = nearby_enemies[choice]
                damage = player.attack_player(target)
                print(f"⚔️ {player.name} attaque {target.name} et inflige {damage} dégâts !")
                
                if not target.is_alive:
                    print(f"💀 {target.name} est éliminé !")
                
                return True
            else:
                print("Choix invalide.")
                return False
        except ValueError:
            print("Veuillez entrer un nombre valide.")
            return False
    
    def play_round(self):
        """Joue un round complet"""
        self.round_number += 1
        print(f"\n🔥 === ROUND {self.round_number} === 🔥")
        
        # Rétrécit la zone périodiquement
        self.shrink_zone()
        
        # Mélange l'ordre des joueurs pour la fairness
        alive_players = self.get_alive_players()
        random.shuffle(alive_players)
        
        # Chaque joueur joue son tour
        for player in alive_players:
            if player.is_alive:  # Vérifier à nouveau car un joueur peut mourir pendant le round
                self.player_turn(player)
                
                # Vérifier s'il ne reste qu'un joueur
                if len(self.get_alive_players()) <= 1:
                    break
    
    def is_game_over(self):
        """Vérifie si la partie est terminée"""
        alive_players = self.get_alive_players()
        return len(alive_players) <= 1
    
    def get_winner(self):
        """Retourne le gagnant de la partie"""
        alive_players = self.get_alive_players()
        return alive_players[0] if alive_players else None
    
    def play(self):
        """Lance et gère la partie complète"""
        self.setup_game()
        
        while not self.is_game_over():
            self.play_round()
            
            # Affiche l'état après chaque round
            self.display_players_stats()
            
            # Pause entre les rounds
            input("\nAppuyez sur Entrée pour continuer...")
        
        # Annonce le résultat
        winner = self.get_winner()
        print("\n" + "="*50)
        if winner:
            player_type = "👤 HUMAIN" if winner.player_type == "human" else "🤖 IA"
            print(f"🏆 VICTOIRE ! {winner.name} ({player_type}) remporte la partie !")
            print(f"Santé restante: {winner.health}/{winner.max_health} HP")
        else:
            print("💀 Égalité ! Tous les joueurs sont éliminés !")
        print("="*50)
