import random

class Player:
    def __init__(self, name, player_type="human"):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack = random.randint(15, 25)
        self.defense = random.randint(5, 15)
        self.is_alive = True
        self.player_type = player_type
        self.position_x = random.randint(0, 9)
        self.position_y = random.randint(0, 9)
        
    def take_damage(self, damage):
        """Le joueur reçoit des dégâts"""
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
        return actual_damage
    
    def attack_player(self, target):
        """Attaque un autre joueur"""
        if not self.is_alive or not target.is_alive:
            return 0
        
        # Calcul des dégâts avec un facteur aléatoire
        base_damage = self.attack
        damage_variance = random.randint(-5, 10)
        total_damage = max(1, base_damage + damage_variance)
        
        actual_damage = target.take_damage(total_damage)
        return actual_damage
    
    def heal(self, amount=20):
        """Soigne le joueur"""
        if self.is_alive:
            self.health = min(self.max_health, self.health + amount)
    
    def move(self, dx, dy, map_size=10):
        """Déplace le joueur sur la carte"""
        new_x = max(0, min(map_size - 1, self.position_x + dx))
        new_y = max(0, min(map_size - 1, self.position_y + dy))
        self.position_x = new_x
        self.position_y = new_y
    
    def distance_to(self, other_player):
        """Calcule la distance avec un autre joueur"""
        dx = self.position_x - other_player.position_x
        dy = self.position_y - other_player.position_y
        return (dx * dx + dy * dy) ** 0.5
    
    def get_status(self):
        """Retourne le statut du joueur"""
        status = "VIVANT" if self.is_alive else "MORT"
        return f"{self.name}: {self.health}/{self.max_health} HP - {status} - Position: ({self.position_x}, {self.position_y})"
    
    def ai_action(self, all_players):
        """Action IA pour les joueurs contrôlés par l'ordinateur"""
        if not self.is_alive:
            return
        
        alive_enemies = [p for p in all_players if p.is_alive and p != self]
        if not alive_enemies:
            return
        
        # Trouve l'ennemi le plus proche
        closest_enemy = min(alive_enemies, key=lambda p: self.distance_to(p))
        distance = self.distance_to(closest_enemy)
        
        # Si l'ennemi est adjacent (distance <= 1.5), attaque
        if distance <= 1.5:
            damage = self.attack_player(closest_enemy)
            print(f"🤖 {self.name} attaque {closest_enemy.name} et inflige {damage} dégâts!")
            if not closest_enemy.is_alive:
                print(f"💀 {closest_enemy.name} est éliminé!")
        else:
            # Sinon, se déplace vers l'ennemi
            dx = 1 if closest_enemy.position_x > self.position_x else -1 if closest_enemy.position_x < self.position_x else 0
            dy = 1 if closest_enemy.position_y > self.position_y else -1 if closest_enemy.position_y < self.position_y else 0
            self.move(dx, dy)
            print(f"🚶 {self.name} se déplace vers ({self.position_x}, {self.position_y})")
        
        # Chance de se soigner si la santé est faible
        if self.health < 30 and random.random() < 0.3:
            self.heal()
            print(f"💚 {self.name} se soigne et récupère des points de vie!")
