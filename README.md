# Last Man Standing - Jeu d'Action 2D

Un jeu d'action en temps réel développé en Python avec Pygame où le joueur doit survivre à des vagues d'ennemis de plus en plus nombreuses et difficiles.

## 🎮 Fonctionnalités

- **Interface graphique** : Fenêtre paramétrable (960x540 par défaut)
- **Contrôles fluides** : Déplacements WASD avec inertie physique
- **Tir automatique** : Éclairs dirigés vers l'ennemi le plus proche
- **IA ennemie** : Ennemis qui suivent le joueur avec composante aléatoire
- **Système de vagues** : Difficulté progressive avec délai décroissant
- **Interface responsive** : Tous les éléments s'adaptent à la taille de fenêtre

## 🚀 Comment jouer

### Installation
```bash
pip install pygame
```

### Lancement du jeu
```bash
python main.py
```

### Contrôles

- **WASD** ou **ZQSD** : Se déplacer (avec inertie)
- **Tir** : Automatique vers l'ennemi le plus proche
- **P** : Pause
- **R** : Recommencer (après game over)
- **ESC** : Quitter

### Règles du jeu

1. **Objectif** : Survivre le plus longtemps possible
2. **Santé** : 100 HP au départ, contact avec ennemi = -10 HP
3. **Vagues** : Chaque vague apporte plus d'ennemis avec délai réduit
4. **Score** : +10 points par ennemi tué, +50×vague bonus par vague
5. **Game Over** : Quand la santé atteint 0

## 🎯 Mécaniques de jeu

### Joueur
- **Taille** : 2% de la largeur d'écran (adaptative)
- **Vitesse** : Proportionnelle à la taille d'écran
- **Inertie** : Friction de 85% pour un mouvement fluide
- **Couleur** : Cyan avec contour blanc
- **Santé** : 100 HP avec régénération impossible

### Ennemis
- **Apparition** : Sur les bords de l'écran par vagues
- **IA** : Suivent le joueur avec mouvement aléatoire (changement toutes les 0.5s)
- **Difficulté** : Vitesse augmente de 10% par vague
- **Santé** : 20 HP + 5 HP par vague (progression linéaire)
- **Couleur** : Rouge avec contour blanc et barre de santé

### Projectiles (Zaps)
- **Type** : Éclairs électriques avec visuel de traînée
- **Vitesse** : Très rapide (1% de la largeur par frame)
- **Cadence** : 10 frames entre chaque tir (6 tirs/seconde)
- **Dégâts** : 25 HP par impact
- **Visuel** : Ligne jaune avec point lumineux blanc
- **Ciblage** : Automatique vers l'ennemi le plus proche

### Système de vagues progressives
- **Vague 1** : 5 ennemis, délai 2.0s entre apparitions
- **Vague 2** : 7 ennemis, délai 1.7s (-15%)
- **Vague 3** : 9 ennemis, délai 1.4s (-15%)
- **Vague N** : (3 + 2×N) ennemis, délai×0.85^(N-1)
- **Délai minimum** : 0.33 secondes (20 frames)

## 🎨 Interface

### Affichage temps réel
- **Barre de santé** : Colorée selon l'état (vert>60%, jaune>30%, rouge≤30%)
- **Vague actuelle** : Numéro de la vague en cours
- **Ennemis restants** : Nombre d'ennemis vivants sur l'écran
- **Score** : Points accumulés avec bonus de vague
- **Délai spawn** : Temps entre apparitions d'ennemis (feedback visuel)

### États du jeu
- **Jeu actif** : Gameplay normal avec tous les éléments
- **Pause** : Overlay semi-transparent avec instructions (P pour reprendre)
- **Game Over** : Écran rouge avec score final et vague atteinte

## 🛠️ Configuration technique

### Paramètres adaptatifs
Tous les éléments sont dimensionnés relativement à la taille de fenêtre :
- **Tailles des entités** : Pourcentages de la largeur/hauteur
- **Vitesses** : Proportionnelles aux dimensions d'écran
- **Interface** : Police et marges adaptatives
- **Facteur d'échelle** : Calculé automatiquement selon la résolution

### Performance
- **60 FPS** : Boucle de jeu optimisée avec pygame.time.Clock()
- **Collision** : Détection rectangulaire optimisée
- **Rendu** : Double buffering automatique avec pygame.display.flip()
- **Mémoire** : Gestion automatique des listes d'entités

## 📁 Structure du projet

```
python-LastManStanding/
├── main.py         # Point d'entrée avec gestion d'erreurs
├── game.py         # Moteur principal et logique de jeu
├── entities.py     # Classes Player, Enemy, Zap
├── config.py       # Configuration paramétrable et couleurs
├── requirements.txt # Dépendances Python (pygame)
└── README.md       # Documentation complète
```

## 🛠️ Développement

### Prérequis
- Python 3.6+
- Pygame 2.0+

### Architecture modulaire
- **main.py** : Initialisation Pygame et boucle de gestion d'erreurs
- **game.py** : Logique de jeu, gestion des vagues, interface utilisateur
- **entities.py** : Classes des entités avec physique et rendu
- **config.py** : Paramètres adaptatifs, couleurs et constantes

### Détails techniques
- **Système de coordonnées** : Origine en haut à gauche
- **Détection de collision** : Rectangles AABB (Axis-Aligned Bounding Box)
- **Mouvement avec inertie** : Accélération + friction pour fluidité
- **Ciblage automatique** : Calcul de distance euclidienne pour trouver l'ennemi le plus proche

## 🎮 Mécaniques avancées

### Système de spawn d'ennemis
- **Position aléatoire** : Apparition sur les 4 bords de l'écran
- **Progression exponentielle** : Délai réduit de 15% par vague
- **Évitement du spam** : Délai minimum pour maintenir la jouabilité

### IA des ennemis
- **Pathfinding simple** : Direction vers le joueur + composante aléatoire
- **Mise à jour périodique** : Changement de direction toutes les 30 frames
- **Collision mortelle** : Contact avec le joueur inflige des dégâts

### Système de tir automatique
- **Ciblage intelligent** : Vers l'ennemi le plus proche
- **Cadence limitée** : 10 frames entre chaque tir
- **Projectiles physiques** : Vitesse et direction calculées

## 🎉 Améliorations futures possibles

### Système de progression
- Expérience et niveaux du joueur
- Amélioration des statistiques (santé, vitesse, dégâts)
- Nouvelles compétences et power-ups

### Variété des ennemis
- Types différents (rapides, tankés, explosifs)
- Boss de fin de vague avec patterns d'attaque
- Comportements IA variés (fuite, embuscade, groupe)

### Effets visuels
- Système de particules pour les explosions
- Effets de lumière pour les zaps
- Animations plus fluides et feedback visuel

### Audio et polish
- Effets sonores et musique de fond
- Menu principal et options
- Système de sauvegarde des meilleurs scores

## 🎯 Survivez le plus longtemps possible !

Affrontez des vagues d'ennemis de plus en plus intenses dans cette bataille électrique où seul le dernier survivant l'emporte !

**Défi** : Pouvez-vous atteindre la vague 10 ? 🏆
