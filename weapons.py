"""
Système d'armes et de compétences orienté objet
==============================================

Classes pour gérer les armes et compétences du joueur de manière modulaire.
Utilise weapon_config.py pour tous les paramètres et progressions.
"""

import math
import pygame
from abc import ABC, abstractmethod
from entities import Zap, Lightning, EnergyOrb
from weapon_config import WeaponConfig, SkillConfig, get_weapon_stat, get_skill_stat


class Weapon(ABC):
    """Classe de base abstraite pour toutes les armes"""
    
    def __init__(self, name, max_level=10):
        self.name = name
        self.level = 1
        self.max_level = max_level
        self.fire_timer = 999  # Permettre le premier tir immédiatement
        self.is_active = True
    
    @abstractmethod
    def fire(self, player, enemies, projectiles, config):
        """Méthode abstraite pour tirer avec l'arme"""
        pass
    
    @abstractmethod
    def update(self, config):
        """Met à jour les timers de l'arme"""
        pass
    
    @abstractmethod
    def get_fire_rate(self, config):
        """Retourne la cadence de tir actuelle"""
        pass
    
    def can_fire(self, config):
        """Vérifie si l'arme peut tirer"""
        return self.fire_timer >= self.get_fire_rate(config)
    
    def upgrade(self):
        """Améliore l'arme d'un niveau"""
        if self.level < self.max_level:
            self.level += 1
            return True
        return False
    
    def get_info(self):
        """Retourne les informations de l'arme"""
        return {
            "name": self.name,
            "level": self.level,
            "max_level": self.max_level
        }


class CannonWeapon(Weapon):
    """Arme Canon - tir de projectiles directs"""
    
    def __init__(self):
        config = WeaponConfig.CANON
        super().__init__(config["name"], max_level=config["max_level"])
        self.config = config
    
    def fire(self, player, enemies, projectiles, config):
        if not enemies or not self.can_fire(config):
            return
        
        # Trouver l'ennemi le plus proche dans la portée
        player_center_x = player.x + player.size // 2
        player_center_y = player.y + player.size // 2
        
        weapon_range = get_weapon_stat("Canon", "range", self.level)
        enemies_in_range = [e for e in enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= weapon_range]
        
        if not enemies_in_range:
            return
        
        closest_enemy = min(enemies_in_range, key=lambda e: 
            math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2))
        
        # Calculer la direction
        enemy_center_x = closest_enemy.x + closest_enemy.size // 2
        enemy_center_y = closest_enemy.y + closest_enemy.size // 2
        
        direction_x = enemy_center_x - player_center_x
        direction_y = enemy_center_y - player_center_y
        direction_length = math.sqrt(direction_x**2 + direction_y**2)
        
        if direction_length > 0:
            direction_x /= direction_length
            direction_y /= direction_length
        
        # Créer le projectile avec les dégâts du niveau actuel
        zap = Zap(player_center_x, player_center_y, direction_x, direction_y, config)
        zap.damage = get_weapon_stat("Canon", "damage", self.level)
        projectiles.append(zap)
        
        self.fire_timer = 0
    
    def update(self, config):
        self.fire_timer += 1
    
    def get_fire_rate(self, config):
        base_rate = self.config["base_fire_rate"]
        fire_rate_multiplier = get_weapon_stat("Canon", "fire_rate", self.level)
        return int(base_rate * fire_rate_multiplier)
    
    def get_damage(self):
        return get_weapon_stat("Canon", "damage", self.level)


class LightningWeapon(Weapon):
    """Arme Lightning - éclairs instantanés avec chaînage"""
    
    def __init__(self):
        config = WeaponConfig.LIGHTNING
        super().__init__(config["name"], max_level=config["max_level"])
        self.config = config
    
    def fire(self, player, enemies, projectiles, config):
        if not enemies or not self.can_fire(config):
            return
        
        # Trouver l'ennemi le plus proche dans la portée
        player_center_x = player.x + player.size // 2
        player_center_y = player.y + player.size // 2
        
        weapon_range = get_weapon_stat("Lightning", "range", self.level)
        enemies_in_range = [e for e in enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= weapon_range]
        
        if not enemies_in_range:
            return
        
        closest_enemy = min(enemies_in_range, key=lambda e: 
            math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2))
        
        # Créer le lightning principal
        lightning = Lightning(player_center_x, player_center_y, 
                            closest_enemy.x + closest_enemy.size // 2,
                            closest_enemy.y + closest_enemy.size // 2,
                            config)
        projectiles.append(lightning)
        
        # Gestion du chaînage
        targets = [closest_enemy]
        current_target = closest_enemy
        chain_range = self.config["chain_range"]
        chain_count = get_weapon_stat("Lightning", "chain_count", self.level)
        
        for _ in range(chain_count):
            nearby_enemies = [e for e in enemies 
                            if e not in targets and 
                            math.sqrt((e.x - current_target.x)**2 + (e.y - current_target.y)**2) <= chain_range]
            if not nearby_enemies:
                break
            
            next_target = min(nearby_enemies, key=lambda e: 
                math.sqrt((e.x - current_target.x)**2 + (e.y - current_target.y)**2))
            targets.append(next_target)
            
            # Créer lightning vers la cible suivante
            chain_lightning = Lightning(current_target.x + current_target.size // 2,
                                      current_target.y + current_target.size // 2,
                                      next_target.x + next_target.size // 2,
                                      next_target.y + next_target.size // 2,
                                      config)
            projectiles.append(chain_lightning)
            current_target = next_target
        
        # Appliquer les dégâts
        damage = get_weapon_stat("Lightning", "damage", self.level)
        for enemy in targets:
            enemy.take_damage(damage)
        
        self.fire_timer = 0
    
    def update(self, config):
        self.fire_timer += 1
    
    def get_fire_rate(self, config):
        base_rate = self.config["base_fire_rate"]
        return int(base_rate * get_weapon_stat("Lightning", "fire_rate", self.level))
    
    def get_damage(self):
        return get_weapon_stat("Lightning", "damage", self.level)
    
    def get_chain_count(self):
        return get_weapon_stat("Lightning", "chain_count", self.level)


class OrbWeapon(Weapon):
    """Arme Orb - orbes défensives orbitales"""
    
    def __init__(self):
        config = WeaponConfig.ORB
        super().__init__(config["name"], max_level=config["max_level"])
        self.config = config
        self.orbs = []
    
    def fire(self, player, enemies, projectiles, config):
        # Les orbes attaquent automatiquement, pas de "tir" manuel
        pass
    
    def update(self, config):
        # Maintenir le bon nombre d'orbes
        expected_count = get_weapon_stat("Orb", "orb_count", self.level)
        if len(self.orbs) != expected_count:
            self.recreate_orbs(config)
    
    def recreate_orbs(self, config):
        """Recrée toutes les orbes avec le bon nombre"""
        self.orbs.clear()
        orb_count = get_weapon_stat("Orb", "orb_count", self.level)
        damage = get_weapon_stat("Orb", "damage", self.level)
        
        for i in range(orb_count):
            orb = EnergyOrb(0, 0, i, orb_count, config)
            orb.damage = damage
            self.orbs.append(orb)
    
    def update_orbs(self, player_x, player_y, player_size):
        """Met à jour la position des orbes autour du joueur"""
        player_center_x = player_x + player_size // 2
        player_center_y = player_y + player_size // 2
        
        for orb in self.orbs:
            orb.update(player_center_x, player_center_y)
    
    def get_fire_rate(self, config):
        return 1  # Les orbes sont toujours actives
    
    def get_damage(self):
        return get_weapon_stat("Orb", "damage", self.level)
    
    def get_orb_count(self):
        return get_weapon_stat("Orb", "orb_count", self.level)


class Skill(ABC):
    """Classe de base abstraite pour toutes les compétences passives"""
    
    def __init__(self, name, description, max_level=5):
        self.name = name
        self.description = description
        self.level = 1
        self.max_level = max_level
        self.is_active = True
    
    @abstractmethod
    def apply_effect(self, player, config):
        """Applique l'effet de la compétence"""
        pass
    
    def upgrade(self):
        """Améliore la compétence d'un niveau"""
        if self.level < self.max_level:
            self.level += 1
            return True
        return False
    
    def get_info(self):
        """Retourne les informations de la compétence"""
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_level": self.max_level
        }


class SpeedSkill(Skill):
    """Compétence de vitesse"""
    
    def __init__(self):
        config = SkillConfig.SPEED
        super().__init__(config["name"], config["description"], max_level=config["max_level"])
        self.config = config
    
    def apply_effect(self, player, config):
        # Augmente la vitesse du joueur selon la progression
        base_speed = config.PLAYER_SPEED
        multiplier = get_skill_stat("Speed", "speed", self.level)
        player.speed = base_speed * multiplier


class ShieldSkill(Skill):
    """Compétence de bouclier"""
    
    def __init__(self):
        config = SkillConfig.SHIELD
        super().__init__(config["name"], config["description"], max_level=config["max_level"])
        self.config = config
        self.shield_points = 0
    
    def apply_effect(self, player, config):
        # Donne des points de bouclier selon la progression
        self.shield_points = get_skill_stat("Shield", "shield", self.level)


class RegenSkill(Skill):
    """Compétence de régénération"""
    
    def __init__(self):
        config = SkillConfig.REGENERATION
        super().__init__(config["name"], config["description"], max_level=config["max_level"])
        self.config = config
        self.regen_timer = 0
    
    def apply_effect(self, player, config):
        self.regen_timer += 1
        regen_rate = get_skill_stat("Regeneration", "rate", self.level)
        
        if self.regen_timer >= regen_rate:
            heal_amount = get_skill_stat("Regeneration", "heal", self.level)
            player.health = min(player.max_health, player.health + heal_amount)
            self.regen_timer = 0


class WeaponManager:
    """Gestionnaire des armes du joueur"""
    
    def __init__(self):
        self.weapons = []
        self.max_weapons = 7
        
        # Commencer avec le canon
        cannon = CannonWeapon()
        self.weapons.append(cannon)
    
    def add_weapon(self, weapon_class):
        """Ajoute une nouvelle arme si possible"""
        if len(self.weapons) < self.max_weapons:
            weapon = weapon_class()
            self.weapons.append(weapon)
            return True
        return False
    
    def upgrade_weapon(self, weapon_name):
        """Améliore une arme spécifique"""
        for weapon in self.weapons:
            if weapon.name == weapon_name:
                return weapon.upgrade()
        return False
    
    def update_all(self, config):
        """Met à jour toutes les armes"""
        for weapon in self.weapons:
            if weapon.is_active:
                weapon.update(config)
    
    def fire_all(self, player, enemies, projectiles, config):
        """Fait tirer toutes les armes actives"""
        for weapon in self.weapons:
            if weapon.is_active:
                weapon.fire(player, enemies, projectiles, config)
    
    def get_weapon_list(self):
        """Retourne la liste des armes avec leurs infos"""
        return [weapon.get_info() for weapon in self.weapons]
    
    def has_weapon(self, weapon_name):
        """Vérifie si le joueur possède une arme"""
        return any(weapon.name == weapon_name for weapon in self.weapons)


class SkillManager:
    """Gestionnaire des compétences passives du joueur"""
    
    def __init__(self):
        self.skills = []
        self.max_skills = 14
    
    def add_skill(self, skill_class):
        """Ajoute une nouvelle compétence si possible"""
        if len(self.skills) < self.max_skills:
            skill = skill_class()
            self.skills.append(skill)
            return True
        return False
    
    def upgrade_skill(self, skill_name):
        """Améliore une compétence spécifique"""
        for skill in self.skills:
            if skill.name == skill_name:
                return skill.upgrade()
        return False
    
    def apply_all_effects(self, player, config):
        """Applique tous les effets des compétences actives"""
        for skill in self.skills:
            if skill.is_active:
                skill.apply_effect(player, config)
    
    def get_skill_list(self):
        """Retourne la liste des compétences avec leurs infos"""
        return [skill.get_info() for skill in self.skills]
    
    def has_skill(self, skill_name):
        """Vérifie si le joueur possède une compétence"""
        return any(skill.name == skill_name for skill in self.skills)
