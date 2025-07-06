# Last Man Standing - Jeu d'Action Temps Réel

## 🎮 Description

**Last Man Standing** est un jeu d'action temps réel développé en Python avec Pygame. Le joueur contrôle un personnage dans un monde procédural et doit survivre face à des vagues d'ennemis en utilisant diverses capacités offensives et défensives.

## ✨ Fonctionnalités Actuelles

### 🕹️ Gameplay
- **Contrôles fluides** : Déplacement inertiel avec les touches WASD
- **Combat automatique** : Tir automatique de projectiles Zap vers les ennemis proches
- **Éclairs chaînés** : Attaque électrique automatique qui frappe plusieurs ennemis (portée 12 tiles)
- **Orbes d'énergie** : Système d'orbes qui suivent le joueur et régénèrent l'énergie
- **Progression** : Système d'XP et de niveaux avec amélioration des capacités

### 🎨 Graphismes et Animation
- **Sprite animé** : Personnage avec animation de vol utilisant une spritesheet ("Birds.png")
- **Miroir directionnel** : Le sprite se retourne selon la direction du mouvement
- **Terrain procédural** : Monde généré algorithmiquement avec un tileset 32x32 ("Tileset.png")
- **Zones cohérentes** : Génération de biomes naturels avec transitions fluides
- **Décorations dispersées** : Props placés aléatoirement pour enrichir le terrain

### 🌍 Monde et Environnement
- **Monde 100x100 tiles** : Terrain procédural avec seed reproductible
- **Caméra intelligente** : Suivi du joueur avec délai et contraintes de limites
- **Optimisation du rendu** : Affichage uniquement des tiles visibles
- **Limites du monde** : Contraintes physiques empêchant le joueur de sortir

### 🤖 Intelligence Artificielle
- **IA ennemie** : Comportement de poursuite et d'attaque
- **Génération intelligente** : Ennemis créés hors de la zone visible de la caméra
- **Gestion des collisions** : Système de détection et de résolution des collisions

### 🎯 Interface et Expérience
- **Interface responsive** : Adaptée à différentes résolutions
- **Affichage des stats** : Santé, énergie, niveau, XP
- **Feedback visuel** : Indicateurs d'état et d'actions
- **Performance optimisée** : Gestion efficace des ressources

## 🏗️ Architecture du Code

```
📁 python-LastManStanding/
├── 📄 main.py           # Point d'entrée du jeu
├── 📄 game.py           # Moteur principal du jeu
├── 📄 entities.py       # Classes des entités (joueur, ennemis, projectiles)
├── 📄 config.py         # Configuration et constantes
├── 📄 background.py     # Génération procédurale du terrain
├── 🖼️ Birds.png         # Spritesheet du personnage
├── 🖼️ Tileset.png       # Tileset pour le terrain
└── 📄 README.md         # Documentation
```

## 🚀 Installation et Lancement

### Prérequis
- Python 3.7+
- Pygame

### Installation
```bash
pip install pygame
```

### Lancement
```bash
python main.py
```

## 🎮 Contrôles

| Touche | Action |
|--------|--------|
| W | Déplacement vers le haut |
| A | Déplacement vers la gauche |
| S | Déplacement vers le bas |
| D | Déplacement vers la droite |
| ESC | Quitter le jeu |

*Note : Le tir et les éclairs sont automatiques quand des ennemis sont à portée.*

## 🔧 Configuration

Le fichier `config.py` contient tous les paramètres ajustables :
- Résolution d'écran
- Vitesses de déplacement
- Portées d'attaque
- Couleurs et styles
- Paramètres de gameplay

## 🎯 Améliorations Restantes à Implémenter

### 🎨 Graphismes et Visuels
- [ ] **Particules d'impact** : Effets visuels lors des attaques et collisions
- [ ] **Animations d'ennemis** : Sprites animés pour les différents types d'ennemis
- [ ] **Effets de lumière** : Éclairage dynamique et ombres
- [ ] **Amélioration du tileset** : Transitions plus naturelles entre biomes
- [ ] **Interface graphique** : Menus avec boutons et graphismes améliorés

### 🎮 Gameplay et Mécaniques
- [ ] **Système d'armes** : Différents types d'armes avec caractéristiques uniques
- [ ] **Capacités spéciales** : Compétences déblocables avec cooldowns
- [ ] **Boss battles** : Ennemis uniques avec patterns d'attaque complexes
- [ ] **Système de loot** : Objets ramassables avec effets temporaires/permanents
- [ ] **Modes de difficulté** : Ajustement de la difficulté selon le niveau

### 🤖 Intelligence Artificielle
- [ ] **Types d'ennemis variés** : Comportements différents (distance, mêlée, support)
- [ ] **Formation d'ennemis** : Coordination entre ennemis pour des attaques groupées
- [ ] **Pathfinding avancé** : Navigation intelligente autour des obstacles
- [ ] **Adaptation dynamique** : IA qui s'adapte au style de jeu du joueur

### 🌍 Monde et Environnement
- [ ] **Biomes spécialisés** : Zones avec propriétés uniques (glace, lave, marais)
- [ ] **Obstacles interactifs** : Éléments destructibles ou utilisables
- [ ] **Événements aléatoires** : Événements spéciaux qui modifient le gameplay
- [ ] **Cycle jour/nuit** : Changement d'ambiance et d'ennemis selon l'heure
- [ ] **Météo dynamique** : Effets météorologiques affectant le gameplay

### 📊 Progression et Méta-jeu
- [ ] **Arbre de compétences** : Système de progression avec choix stratégiques
- [ ] **Succès/Achievements** : Objectifs à long terme avec récompenses
- [ ] **Statistiques détaillées** : Tracking des performances et records
- [ ] **Sauvegarde de progression** : Persistance des données entre sessions
- [ ] **Classements** : Système de scores et comparaisons

### 🔊 Audio et Ambiance
- [ ] **Effets sonores** : Sons d'attaque, de mouvement, d'impacts
- [ ] **Musique adaptative** : Bandes sonores changeant selon le contexte
- [ ] **Ambiance sonore** : Sons d'environnement pour l'immersion
- [ ] **Feedback audio** : Signaux sonores pour les actions importantes

### 🛠️ Technique et Performance
- [ ] **Optimisation avancée** : Amélioration des performances pour de plus grands mondes
- [ ] **Multithreading** : Parallélisation des calculs lourds
- [ ] **Format de sauvegarde** : Système de sauvegarde/chargement robuste
- [ ] **Configuration avancée** : Interface pour ajuster les paramètres en jeu
- [ ] **Debugging tools** : Outils de développement et de test

### 🌐 Fonctionnalités Réseau (Optionnel)
- [ ] **Multijoueur coopératif** : Jeu en équipe local ou en ligne
- [ ] **Partage de mondes** : Possibilité de partager des seeds de terrain
- [ ] **Classements en ligne** : Comparaison avec d'autres joueurs

## 🐛 Problèmes Connus

Aucun problème majeur identifié actuellement. Le jeu est stable et jouable.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre du code
- Créer des assets graphiques

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🎉 Remerciements

- Pygame pour le framework de développement
- La communauté open-source pour les ressources et l'inspiration
- Les testeurs pour leurs retours constructifs

---

*Dernière mise à jour : 6 juillet 2025*
