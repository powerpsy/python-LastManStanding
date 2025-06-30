# Last Man Standing - Jeu d'Action 2D

Un jeu d'action en temps réel développé en Python avec Pygame où le joueur doit survivre à des vagues d'ennemis de plus en plus nombreuses et difficiles.

## 🎮 Fonctionnalités

- **Interface graphique** : Fenêtre paramétrable (960x540 par défaut)
- **Contrôles fluides** : Déplacements WASD avec inertie physique
- **Tir automatique** : Éclairs dirigés vers les ennemis
- **IA ennemie** : Ennemis qui suivent le joueur avec composante aléatoire
- **Système de vagues** : Difficulté progressive avec plus d'ennemis
- **Interface responsive** : Tous les éléments s'adaptent à la taille de fenêtre

## 🚀 Comment jouer

### Installation
```bash
pip install pygame numpy
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
3. **Vagues** : Chaque vague apporte plus d'ennemis
4. **Score** : +10 points par ennemi (+5 par vague)
5. **Game Over** : Quand la santé atteint 0

## 🎯 Mécaniques de jeu

### Joueur
- **Taille** : 2% de la largeur d'écran
- **Vitesse** : Proportionnelle à la taille d'écran
- **Inertie** : Friction de 85% pour un mouvement fluide
- **Couleur** : Cyan avec contour blanc

### Ennemis
- **Apparition** : Sur les bords de l'écran par vagues
- **IA** : Suivent le joueur avec mouvement aléatoire
- **Difficulté** : Vitesse augmente de 10% par vague
- **Santé** : 20 HP + 5 HP par vague

### Projectiles (Zaps)
- **Type** : Éclairs électriques
- **Vitesse** : Très rapide (1% de la largeur par frame)
- **Cadence** : 10 frames entre chaque tir
- **Dégâts** : 25 HP par impact
- **Visuel** : Ligne jaune avec point lumineux blanc

## 🎨 Interface

### Affichage temps réel
- **Barre de santé** : Colorée selon l'état (vert/jaune/rouge)
- **Vague actuelle** : Numéro de la vague en cours
- **Ennemis restants** : Nombre d'ennemis sur l'écran
- **Score** : Points accumulés

### États du jeu
- **Jeu actif** : Gameplay normal
- **Pause** : Overlay semi-transparent avec instructions
- **Game Over** : Écran rouge avec score final et options

## 🛠️ Configuration technique

### Paramètres adaptatifs
Tous les éléments sont dimensionnés relativement à la taille de fenêtre :
- Tailles des entités : Pourcentages de la largeur/hauteur
- Vitesses : Proportionnelles aux dimensions
- Interface : Police et marges adaptatives

### Performance
- **60 FPS** : Boucle de jeu optimisée
- **Collision** : Détection par rectangles Pygame
- **Rendu** : Double buffering automatique

## 📁 Structure du projet

```
python-LastManStanding/
├── main.py         # Point d'entrée du jeu
├── game.py         # Moteur principal et logique de jeu
├── entities.py     # Classes Player, Enemy, Zap
├── config.py       # Configuration paramétrable
├── requirements.txt # Dépendances Python
└── README.md       # Ce fichier
```

## 🛠️ Développement

### Prérequis
- Python 3.6+
- Pygame 2.0+
- NumPy 1.20+

### Architecture
- **main.py** : Initialisation et boucle principale
- **game.py** : Logique de jeu, gestion des vagues, interface
- **entities.py** : Classes des entités avec physique et rendu
- **config.py** : Paramètres adaptatifs et constantes

### Extensibilité
Le jeu est conçu pour être facilement extensible :
- **Nouveaux ennemis** : Hériter de la classe Enemy
- **Nouvelles armes** : Hériter de la classe Zap
- **Power-ups** : Nouvelles classes d'entités
- **Effets visuels** : Système de particules

## 🎮 Améliorations futures

### Système de progression
- Expérience et niveaux
- Amélioration des statistiques
- Nouvelles compétences

### Variété des ennemis
- Types différents (rapides, tankés, explosifs)
- Boss de fin de vague
- Comportements IA variés

### Effets visuels
- Particules pour les explosions
- Effets de lumière pour les zaps
- Animations plus fluides

### Audio
- Effets sonores
- Musique de fond
- Audio spatial

## 🎉 Amusez-vous bien !

Survivez le plus longtemps possible dans cette bataille électrique !
