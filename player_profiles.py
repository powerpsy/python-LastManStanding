"""
Configuration des profils de joueurs
===================================

Définit les caractéristiques uniques de chaque type de joueur/sprite.
Chaque profil peut avoir des armes de départ différentes, des modificateurs de stats,
des compétences spéciales, etc.
"""

from weapons import CannonWeapon, LightningWeapon, OrbWeapon, BeamWeapon
from weapons import SpeedSkill, RegenSkill, ShieldSkill, MagnetSkill


class PlayerProfile:
    """Classe de base pour un profil de joueur"""
    
    def __init__(self, name, description, profile_id=1):
        self.name = name
        self.description = description
        self.profile_id = profile_id  # ID numérique du profil
        
        # Arme de départ
        self.starting_weapon_class = CannonWeapon
        self.weapon_modifications = {}  # Modifications spécifiques aux armes
        
        # Modificateurs de stats de base
        self.health_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        
        # Compétences de départ (optionnelles)
        self.starting_skills = []
        
        # Modificateurs de progression
        self.xp_multiplier = 1.0
        self.regen_bonus = 0  # Régénération passive bonus
        
    def apply_weapon_modifications(self, weapon):
        """Applique les modifications spécifiques aux armes selon le profil"""
        weapon_name = weapon.name
        if weapon_name in self.weapon_modifications:
            modifications = self.weapon_modifications[weapon_name]
            weapon.config = weapon.config.copy()
            
            for stat_name, modifier in modifications.items():
                if stat_name in weapon.config:
                    if isinstance(modifier, dict):
                        if "multiply" in modifier:
                            weapon.config[stat_name] = int(weapon.config[stat_name] * modifier["multiply"])
                        elif "add" in modifier:
                            weapon.config[stat_name] = weapon.config[stat_name] + modifier["add"]
                    else:
                        # Remplacement direct
                        weapon.config[stat_name] = modifier
    
    def get_starting_weapon(self):
        """Retourne l'arme de départ configurée pour ce profil"""
        weapon = self.starting_weapon_class()
        self.apply_weapon_modifications(weapon)
        return weapon
    
    def apply_player_stats(self, player, base_config):
        """Applique les modificateurs de stats au joueur"""
        player.max_health = int(player.max_health * self.health_multiplier)
        player.health = player.max_health  # Remettre la santé au max après modification
        
        base_speed = getattr(base_config, 'PLAYER_SPEED', 3)
        player.speed = base_speed * self.speed_multiplier


class WarriorProfile(PlayerProfile):
    """Profil Guerrier - Type 1 (player2.png) - Défensif avec orbes"""
    
    def __init__(self):
        super().__init__("Guerrier", "Spécialiste défensif avec orbes protectrices", profile_id=1)
        
        # Arme de départ : Orb
        self.starting_weapon_class = OrbWeapon
        
        # Stats : Plus de vie, un peu plus lent
        self.health_multiplier = 1.3  # +30% de vie
        self.speed_multiplier = 0.9   # -10% de vitesse
        
        # Bonus défensif
        self.regen_bonus = 1  # +1 HP de régénération passive par cycle
        
        # Compétence de départ : Résistance niveau 1
        # (sera implémentée dans le WeaponManager)


class MageProfile(PlayerProfile):
    """Profil Mage - Type 2 (player3.png) - Équilibré avec canon"""
    
    def __init__(self):
        super().__init__("Mage", "Combattant équilibré avec armes projectiles", profile_id=2)
        
        # Arme de départ : Canon
        self.starting_weapon_class = CannonWeapon
        
        # Modifications du Canon pour le Mage
        self.weapon_modifications = {
            "Canon": {
                "base_range": {"multiply": 1.2},  # +20% de portée
                "base_damage": {"multiply": 1.1}  # +10% de dégâts
            }
        }
        
        # Stats équilibrées avec bonus XP
        self.health_multiplier = 1.0   # Vie normale
        self.speed_multiplier = 1.0    # Vitesse normale
        self.xp_multiplier = 1.1       # +10% XP
        
        # Compétence de départ : Vitesse niveau 1


class AssassinProfile(PlayerProfile):
    """Profil Assassin - Type 3 (player4.png) - Rapide avec lightning"""
    
    def __init__(self):
        super().__init__("Assassin", "Combattant rapide avec éclairs destructeurs", profile_id=3)
        
        # Arme de départ : Lightning
        self.starting_weapon_class = LightningWeapon
        
        # Lightning modifié pour l'Assassin
        self.weapon_modifications = {
            "Lightning": {
                "base_fire_rate": 60,  # Plus rapide (au lieu de 120)
                "base_damage": {"multiply": 1.15}  # +15% de dégâts
            }
        }
        
        # Stats : Moins de vie, beaucoup plus rapide
        self.health_multiplier = 0.8   # -20% de vie
        self.speed_multiplier = 1.1    # +40% de vitesse
        self.damage_multiplier = 1.1   # +10% de dégâts globaux
        
        # Compétence de départ : Vitesse niveau 1


class PlayerProfileManager:
    """Gestionnaire des profils de joueurs"""
    
    PROFILES = {
        1: WarriorProfile(),
        2: MageProfile(), 
        3: AssassinProfile()
    }
    
    @classmethod
    def get_profile(cls, sprite_type):
        """Retourne le profil correspondant au type de sprite"""
        return cls.PROFILES.get(sprite_type, cls.PROFILES[2])  # Défaut : Mage
    
    @classmethod
    def get_profile_name(cls, sprite_type):
        """Retourne le nom du profil"""
        profile = cls.get_profile(sprite_type)
        return profile.name
    
    @classmethod
    def get_profile_description(cls, sprite_type):
        """Retourne la description du profil"""
        profile = cls.get_profile(sprite_type)
        return profile.description
