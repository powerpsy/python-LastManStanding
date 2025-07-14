"""
Configuration des armes et compétences
=====================================

Paramètres initiaux et matrices d'évolution pour toutes les armes et compétences.
"""

class WeaponConfig:
    """Configuration centralisée des armes et de leurs progressions"""
    
    # === CANON ===
    CANON = {
        "name": "Canon",
        "max_level": 10,
        "base_damage": 25,
        "base_fire_rate": 10,  # frames entre les tirs
        "base_range": 320,
        "projectile_speed": 8.0,
        
        # Progressions par niveau (multiplicateurs)
        "damage_progression": [1.0, 1.2, 1.44, 1.73, 2.07, 2.49, 2.99, 3.58, 4.30, 5.16],
        "fire_rate_progression": [1.0, 0.9, 0.81, 0.73, 0.66, 0.59, 0.53, 0.48, 0.43, 0.39],  # Plus bas = plus rapide
        "range_progression": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    }
    
    # === LIGHTNING ===
    LIGHTNING = {
        "name": "Lightning",
        "max_level": 10,
        "base_damage": 50,
        "base_fire_rate": 300,  # frames entre les tirs (5 secondes)
        "base_range": 384,
        "chain_range": 256,
        "base_chain_count": 1,
        "display_time": 6,  # frames d'affichage
        
        # Progressions par niveau
        "damage_progression": [1.0, 1.3, 1.69, 2.20, 2.86, 3.72, 4.84, 6.29, 8.18, 10.63],
        "fire_rate_progression": [1.0, 0.85, 0.72, 0.61, 0.52, 0.44, 0.37, 0.32, 0.27, 0.23],  # Plus bas = plus rapide
        "chain_count_progression": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        "range_progression": [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45]
    }
    
    # === ORB ===
    ORB = {
        "name": "Orb",
        "max_level": 7,
        "base_damage": 40,
        "orbit_radius": 64,
        "orbit_speed": 0.05,  # radians par frame
        "base_orb_count": 1,
        
        # Progressions par niveau
        "damage_progression": [1.0, 1.4, 1.96, 2.74, 3.84, 5.38, 7.53],
        "orb_count_progression": [1, 2, 3, 4, 5, 6, 7],
        "orbit_speed_progression": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
        "radius_progression": [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]
    }


class SkillConfig:
    """Configuration centralisée des compétences passives"""
    
    # === VITESSE ===
    SPEED = {
        "name": "Vitesse",
        "description": "Augmente la vitesse de déplacement",
        "max_level": 5,
        "base_multiplier": 1.0,
        
        # Progression: +15% par niveau
        "speed_progression": [1.0, 1.15, 1.30, 1.45, 1.60]
    }
    
    # === BOUCLIER ===
    SHIELD = {
        "name": "Bouclier",
        "description": "Donne des points de bouclier",
        "max_level": 10,
        "base_shield_points": 0,
        
        # Progression: +2 points par niveau
        "shield_progression": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    }
    
    # === RÉGÉNÉRATION ===
    REGENERATION = {
        "name": "Régénération",
        "description": "Régénère la vie au fil du temps",
        "max_level": 5,
        "base_heal_amount": 5,
        "base_regen_rate": 300,  # frames entre les soins (5 secondes)
        
        # Progressions
        "heal_progression": [0, 5, 10, 15, 20],  # points de vie par tick
        "rate_progression": [300, 280, 260, 240, 220]  # frames entre les ticks (plus bas = plus rapide)
    }
    
    # === AIMANT ===
    MAGNET = {
        "name": "Aimant",
        "description": "Attire les bonus et objets",
        "max_level": 3,
        "base_range": 80,
        "base_strength": 0.1,
        
        # Progressions
        "range_progression": [0, 80, 120, 160],
        "strength_progression": [0, 0.1, 0.15, 0.2]
    }
    
    # === RÉSISTANCE ===
    RESISTANCE = {
        "name": "Résistance",
        "description": "Réduit les dégâts subis",
        "max_level": 5,
        "base_reduction": 0.0,
        
        # Progression: 5% de réduction par niveau
        "damage_reduction_progression": [0.0, 0.05, 0.10, 0.15, 0.20]
    }


class WeaponUnlockConfig:
    """Configuration du système de déblocage des armes"""
    
    UNLOCK_REQUIREMENTS = {
        "Canon": {
            "level": 1,
            "description": "Arme de départ"
        },
        "Lightning": {
            "level": 3,
            "description": "Débloqué au niveau 3"
        },
        "Orb": {
            "level": 5,
            "description": "Débloqué au niveau 5"
        }
    }


class UpgradeConfig:
    """Configuration du système d'amélioration"""
    
    # Probabilités d'apparition des améliorations selon le niveau du joueur
    UPGRADE_WEIGHTS = {
        # Armes (plus fréquentes en début de partie)
        "weapon_upgrades": {
            1: 60,   # 60% de chance niveau 1
            5: 50,   # 50% de chance niveau 5
            10: 40,  # 40% de chance niveau 10
            15: 30   # 30% de chance niveau 15+
        },
        
        # Compétences (plus fréquentes en milieu de partie)
        "skill_upgrades": {
            1: 30,   # 30% de chance niveau 1
            5: 40,   # 40% de chance niveau 5
            10: 50,  # 50% de chance niveau 10
            15: 60   # 60% de chance niveau 15+
        },
        
        # Nouvelles armes (rares mais importantes)
        "new_weapons": {
            1: 10,   # 10% de chance niveau 1
            5: 10,   # 10% de chance niveau 5
            10: 10,  # 10% de chance niveau 10
            15: 10   # 10% de chance niveau 15+
        }
    }
    
    # Coût d'amélioration par niveau (si système de monnaie)
    UPGRADE_COSTS = {
        "weapons": [0, 10, 20, 35, 55, 80, 110, 145, 185, 230],
        "skills": [0, 5, 10, 18, 28, 40]
    }


def get_weapon_stat(weapon_name, stat_name, level):
    """
    Récupère une statistique d'arme pour un niveau donné
    
    Args:
        weapon_name: Nom de l'arme ("Canon", "Lightning", "Orb")
        stat_name: Nom de la statistique ("damage", "fire_rate", etc.)
        level: Niveau de l'arme (1-max_level)
    
    Returns:
        Valeur de la statistique pour ce niveau
    """
    weapon_config = getattr(WeaponConfig, weapon_name.upper(), None)
    if not weapon_config:
        return 0
    
    # Valeur de base
    base_value = weapon_config.get(f"base_{stat_name}", 0)
    
    # Progression
    progression_key = f"{stat_name}_progression"
    progression = weapon_config.get(progression_key, [1.0])
    
    # Index sécurisé (level commence à 1)
    index = min(level - 1, len(progression) - 1)
    multiplier = progression[index] if index >= 0 else 1.0
    
    return base_value * multiplier


def get_skill_stat(skill_name, stat_name, level):
    """
    Récupère une statistique de compétence pour un niveau donné
    
    Args:
        skill_name: Nom de la compétence
        stat_name: Nom de la statistique
        level: Niveau de la compétence (1-max_level)
    
    Returns:
        Valeur de la statistique pour ce niveau
    """
    skill_config = getattr(SkillConfig, skill_name.upper(), None)
    if not skill_config:
        return 0
    
    progression_key = f"{stat_name}_progression"
    progression = skill_config.get(progression_key, [0])
    
    # Index sécurisé (level commence à 1)
    index = min(level - 1, len(progression) - 1)
    return progression[index] if index >= 0 else 0
