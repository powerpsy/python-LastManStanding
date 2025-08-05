"""
Système d'armes et de compétences orienté objet
==============================================

Classes pour gérer les armes et compétences du joueur de manière modulaire.
Utilise weapon_config.py pour tous les paramètres et progressions.
"""

import math
import pygame
from entities import Beam
from abc import ABC, abstractmethod
from entities import CanonProjectile, Lightning, EnergyOrb, Beam
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
    
    def record_shot_fired(self, weapon_type, game):
        """Enregistre un tir dans les statistiques du jeu"""
        if game and hasattr(game, 'record_shot_fired'):
            game.record_shot_fired(weapon_type)
    
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
            return False
        
        # Trouver l'ennemi le plus proche dans la portée
        player_center_x = player.x + player.size // 2
        player_center_y = player.y + player.size // 2
        
        weapon_range = get_weapon_stat("Canon", "range", self.level)
        enemies_in_range = [e for e in enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= weapon_range]
        
        if not enemies_in_range:
            return False
        
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
        canon_projectile = CanonProjectile(player_center_x, player_center_y, direction_x, direction_y, config)
        canon_projectile.damage = get_weapon_stat("Canon", "damage", self.level)
        projectiles.append(canon_projectile)
        
        self.fire_timer = 0
        return True  # A tiré
        return None  # Pas d'effets spéciaux pour le canon
    
    def update(self, config):
        self.fire_timer += 1
    
    def get_fire_rate(self, config):
        return int(get_weapon_stat("Canon", "fire_rate", self.level))
    
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
            return []
        
        # Trouver l'ennemi le plus proche dans la portée
        player_center_x = player.x + player.size // 2
        player_center_y = player.y + player.size // 2
        
        weapon_range = get_weapon_stat("Lightning", "range", self.level)
        enemies_in_range = [e for e in enemies 
                           if math.sqrt((e.x - player_center_x)**2 + (e.y - player_center_y)**2) <= weapon_range]
        
        if not enemies_in_range:
            return []
        
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
        hit_enemies = []
        for enemy in targets:
            enemy.take_damage(damage)
            hit_enemies.append((enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))
        
        self.fire_timer = 0
        return hit_enemies  # Retourner les positions touchées
        return hit_enemies  # Retourner les positions des ennemis touchés pour les effets
    
    def update(self, config):
        self.fire_timer += 1
    
    def get_fire_rate(self, config):
        # Utiliser la configuration de l'instance (modifiée pour le joueur type 3)
        base_rate = self.config.get("base_fire_rate", 120)
        progression = self.config.get("fire_rate_progression", [1.0])
        index = min(self.level - 1, len(progression) - 1)
        multiplier = progression[index] if index >= 0 else 1.0
        return int(base_rate * multiplier)
    
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


class BeamWeapon(Weapon):
    """Arme Beam - rayon laser continu qui traverse les ennemis"""
    
    def __init__(self):
        config = WeaponConfig.BEAM
        super().__init__(config["name"], max_level=config["max_level"])
        self.config = config
    
    def fire(self, player, enemies, projectiles, config):
        # Vérifier si on a déjà des beams actifs pour ce niveau
        current_beams = [p for p in projectiles if isinstance(p, Beam)]
        expected_beam_count = get_weapon_stat("Beam", "count", self.level)
        
        # Si on a déjà le bon nombre de beams, ne rien faire
        if len(current_beams) == expected_beam_count:
            return False
        
        # Sinon, supprimer tous les beams existants et en créer de nouveaux
        projectiles[:] = [p for p in projectiles if not isinstance(p, Beam)]
        
        player_center_x = player.x + player.size // 2
        player_center_y = player.y + player.size // 2
        
        # Direction initiale arbitraire (vers la droite par défaut)
        direction_x, direction_y = 1.0, 0.0
        
        # Créer le nombre approprié de beams selon le niveau
        beam_count = expected_beam_count
        
        for i in range(beam_count):
            # Créer le faisceau laser avec référence au joueur et index pour positionnement
            beam = Beam(player_center_x, player_center_y, direction_x, direction_y, 
                       config, self.level, player, beam_index=i, total_beams=beam_count)
            projectiles.append(beam)
        
        return True  # A créé des nouveaux beams
    
    def update(self, config):
        self.fire_timer += 1
    
    def get_fire_rate(self, config):
        return int(get_weapon_stat("Beam", "fire_rate", self.level))
    
    def get_damage(self):
        return get_weapon_stat("Beam", "damage", self.level)
    
    def get_range(self):
        return get_weapon_stat("Beam", "range", self.level)
    
    def get_width(self):
        return get_weapon_stat("Beam", "width", self.level)


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


class ShieldSkill(Skill):
    """Compétence de bouclier - Donne des points de bouclier temporaires"""
    
    def __init__(self):
        config = SkillConfig.SHIELD
        super().__init__(config["name"], config["description"], max_level=config["max_level"])
        self.config = config
        self.regen_timer = 0
        self.combat_timer = 0  # Timer pour détecter quand on est hors combat
    
    def apply_effect(self, player, config):
        """Applique l'effet de bouclier"""
        # Incrémenter le timer de combat
        self.combat_timer += 1
        
        # Obtenir les statistiques selon le niveau
        max_shield = get_skill_stat("Shield", "shield", self.level)
        regen_rate = get_skill_stat("Shield", "regen_rate", self.level)
        regen_delay = get_skill_stat("Shield", "regen_delay", self.level)
        
        # Initialiser le bouclier si pas encore fait
        if not hasattr(player, 'shield_points'):
            player.shield_points = max_shield
            player.max_shield_points = max_shield
        else:
            # Mettre à jour le max si le niveau a changé
            player.max_shield_points = max_shield
        
        # Régénération du bouclier (seulement si pas au maximum et hors combat)
        if (player.shield_points < player.max_shield_points and 
            self.combat_timer >= regen_delay):
            
            self.regen_timer += 1
            if self.regen_timer >= regen_rate:
                regen_amount = 1  # Régénère 1 point à la fois
                player.shield_points = min(player.max_shield_points, 
                                         player.shield_points + regen_amount)
                self.regen_timer = 0
    
    def reset_combat_timer(self):
        """Remet à zéro le timer de combat (appelé quand le joueur prend des dégâts)"""
        self.combat_timer = 0


class MagnetSkill(Skill):
    """Compétence d'aimant - Attire les objets collectibles"""
    
    def __init__(self):
        config = SkillConfig.MAGNET
        super().__init__(config["name"], config["description"], max_level=config["max_level"])
        self.config = config
    
    def apply_effect(self, player, config):
        """Applique l'effet magnétique sur les objets collectibles"""
        # Cette méthode sera appelée par le SkillManager
        # L'attraction sera gérée dans game.py via get_magnet_range() et get_magnet_strength()
        pass
    
    def get_magnet_range(self):
        """Retourne la portée de l'aimant selon le niveau"""
        if self.level == 0:
            return 0
        return self.config["range_progression"][self.level]
    
    def get_magnet_strength(self):
        """Retourne la force d'attraction selon le niveau"""
        if self.level == 0:
            return 0
        return self.config["strength_progression"][self.level]


class WeaponManager:
    """Gestionnaire des armes du joueur"""
    
    def __init__(self, config=None):
        self.weapons = []
        self.max_weapons = 7
        
        # Utiliser le système de profils pour déterminer l'arme de départ
        sprite_type = getattr(config, 'PLAYER_SPRITE_TYPE', 1) if config else 1
        
        # Importer ici pour éviter les imports circulaires
        from player_profiles import PlayerProfileManager
        
        # Obtenir le profil du joueur et son arme de départ
        profile = PlayerProfileManager.get_profile(sprite_type)
        starting_weapon = profile.get_starting_weapon()
        
        self.weapons.append(starting_weapon)
        
        # Stocker le profil pour référence future
        self.player_profile = profile
    
    def add_weapon(self, weapon_class):
        """Ajoute une nouvelle arme si possible"""
        if len(self.weapons) < self.max_weapons:
            weapon = weapon_class()
            
            # Appliquer les modifications du profil à la nouvelle arme
            if hasattr(self, 'player_profile'):
                self.player_profile.apply_weapon_modifications(weapon)
            
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
    
    def get_skill(self, skill_name):
        """Retourne une compétence spécifique par nom"""
        for skill in self.skills:
            if skill.name == skill_name:
                return skill
        return None
    
    def get_magnet_effect(self):
        """Retourne les effets de l'aimant (portée et force) ou None si pas d'aimant"""
        magnet_skill = self.get_skill("Aimant")
        if magnet_skill and magnet_skill.is_active:
            return {
                "range": magnet_skill.get_magnet_range(),
                "strength": magnet_skill.get_magnet_strength()
            }
        return None
    
    def notify_damage_taken(self):
        """Notifie toutes les compétences qu'un dégât a été pris"""
        for skill in self.skills:
            if skill.is_active and hasattr(skill, 'reset_combat_timer'):
                skill.reset_combat_timer()
