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
        "range_progression": [1.0, 1.15, 1.35, 1.55, 1.8, 2.1, 2.4, 2.75, 3.1, 3.5]
    }
    
    # === LIGHTNING ===
    LIGHTNING = {
        "name": "Lightning",
        "max_level": 10,
        "base_damage": 150,  # Triplé de 50 à 150
        "base_fire_rate": 120,  # frames entre les tirs (2 secondes)
        "base_range": 500,
        "chain_range": 256,
        "base_chain_count": 1,
        "display_time": 18,  # Doublé de 6 à 12 frames (0.2s à 60 FPS)
        
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
    
    # === BEAM ===
    BEAM = {
        "name": "Beam",
        "max_level": 10,
        "base_damage": 15,  # Dégâts par frame (continu)
        "base_fire_rate": 120,  # frames entre les activations (2 secondes)
        "base_range": 750,
        "base_width": 12,  # Largeur du faisceau en pixels
        "base_duration": 60,  # Durée du faisceau en frames (1 seconde)
        "base_rotation_angle": 30,  # Rotation initiale en degrés (niveau 1)
        
        # Progressions par niveau
        "damage_progression": [1.0, 1.25, 1.56, 1.95, 2.44, 3.05, 3.81, 4.76, 5.95, 7.44],
        "fire_rate_progression": [1.0, 0.9, 0.81, 0.73, 0.66, 0.59, 0.53, 0.48, 0.43, 0.39],  # Plus bas = plus rapide
        "range_progression": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
        "width_progression": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
        
        # Nouvelles progressions pour la rotation
        "duration_progression": [60, 75, 90, 105, 120, 135, 150, 165, 180, 180],  # De 1s à 3s au niveau 10
        "rotation_progression": [30, 45, 60, 90, 120, 180, 240, 270, 320, 360]  # De 30° à 360° (tour complet)
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
        "range_progression": [100, 200, 300, 400],
        "strength_progression": [0.1, 0.2, 0.5, 1]
    }
    
    # === BOUCLIER ===
    SHIELD = {
        "name": "Bouclier",
        "description": "Donne des points de bouclier temporaires",
        "max_level": 5,
        "base_shield_amount": 20,
        "base_regen_rate": 600,  # frames entre les régénérations (10 secondes)
        "base_regen_delay": 300,  # frames avant de commencer à régénérer (5 secondes hors combat)
        
        # Progressions (index 0 = niveau 1, index 1 = niveau 2, etc.)
        "shield_progression": [20, 40, 60, 80, 100],  # Points de bouclier par niveau
        "regen_rate_progression": [600, 550, 500, 450, 400],  # Plus bas = plus rapide
        "regen_delay_progression": [300, 270, 240, 210, 180]  # Délai avant régénération
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


def get_weapon_stat(weapon_name, stat_name, level):
    """
    Récupère une statistique d'arme pour un niveau donné
    
    Args:
        weapon_name: Nom de l'arme ("Canon", "Lightning", "Orb", "Beam")
        stat_name: Nom de la statistique ("damage", "fire_rate", "duration", "rotation", etc.)
        level: Niveau de l'arme (1-max_level)
    
    Returns:
        Valeur de la statistique pour ce niveau
    """
    weapon_config = getattr(WeaponConfig, weapon_name.upper(), None)
    if not weapon_config:
        return 0
    
    # Gestion spéciale pour les nouvelles stats du Beam
    if weapon_name.upper() == "BEAM":
        if stat_name == "duration":
            progression = weapon_config.get("duration_progression", [60] * 10)
            index = min(level - 1, len(progression) - 1)
            return progression[index] if index >= 0 else 60
        elif stat_name == "rotation":
            progression = weapon_config.get("rotation_progression", [30] * 10)
            index = min(level - 1, len(progression) - 1)
            return progression[index] if index >= 0 else 30
    
    # Valeur de base
    base_key = f"base_{stat_name}"
    base_value = weapon_config.get(base_key, 0)
    
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
