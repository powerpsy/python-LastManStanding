# Last Man Standing - Jeu d'Action Temps Réel

## Architecture du Code

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

## 🎮 Contrôles

| Touche | Action |
|--------|--------|
| W | Déplacement vers le haut |
| A | Déplacement vers la gauche |
| S | Déplacement vers le bas |
| D | Déplacement vers la droite |
| ESC | Quitter le jeu |

## Compétences passives

🛡️ Compétences Défensives
1. Bouclier - Donne des points de bouclier temporaires
    Niveau 1-5 : +20/40/60/80/100 points de bouclier
    Se régénère lentement hors combat

2. Évasion - Chance d'esquiver complètement les attaques
    Niveau 1-5 : 5%/10%/15%/20%/25% de chance d'esquive

3. Réflexion - Renvoie une partie des dégâts à l'attaquant
    Niveau 1-5 : 10%/20%/30%/40%/50% des dégâts renvoyés

⚔️ Compétences Offensives
4. Rage - Plus la vie est basse, plus les dégâts augmentent
    Niveau 1-5 : +10%/20%/30%/40%/50% de dégâts quand vie < 50%

5. Critique - Chance d'infliger des dégâts critiques
    Niveau 1-5 : 5%/10%/15%/20%/25% de chance de x2 dégâts

6. Poison - Les attaques empoisonnent les ennemis
    Niveau 1-5 : 2/4/6/8/10 dégâts/seconde pendant 3 secondes

🏃 Compétences de Mobilité
7. Dash - Téléportation courte distance avec invulnérabilité
    Niveau 1-5 : Cooldown 10/8/6/4/2 secondes, distance fixe

8. Fantôme - Traverser les ennemis pendant quelques secondes
    Niveau 1-5 : Durée 1/2/3/4/5 secondes, cooldown 30s

🎯 Compétences Utilitaires
9. Zone de Ralentissement - Aura qui ralentit les ennemis proches
    Niveau 1-5 : Ralentit de 20%/30%/40%/50%/60% dans un rayon de 100px

10. Vampirisme - Récupère de la vie en tuant des ennemis
    Niveau 1-5 : +2/4/6/8/10 PV par ennemi tué

11. Multiplicateur d'XP - Augmente l'expérience gagnée
    Niveau 1-3 : +25%/50%/100% d'XP

🔥 Compétences Spéciales

12. Explosion à la Mort - Explose quand la vie tombe à zéro
    Niveau 1-3 : Dégâts 100/200/300 dans un rayon de 150px
    Une seule utilisation par vie

13. Aura de Feu - Brûle automatiquement les ennemis proches
    Niveau 1-5 : 5/10/15/20/25 dégâts/seconde dans 80px de rayon

14. Lucky Drop - Augmente la chance de drops rares
    Niveau 1-3 : +20%/40%/60% de chance de bonus rares

🔄 Compétences Combo
15. Synergie d'Armes - Les armes se renforcent mutuellement
    Niveau 1-5 : +5%/10%/15%/20%/25% de dégâts par arme possédée

## 🎯 Améliorations Restantes à Implémenter

### 🎨 Graphismes et Visuels
- [ ] **Particules d'impact** : Effets visuels lors des attaques et collisions
- [ ] **Animations d'ennemis** : Sprites animés pour les différents types d'ennemis
- [ ] **Effets de lumière** : Éclairage dynamique et ombres
- [ ] **Amélioration du tileset** : Transitions plus naturelles entre biomes
- [ ] **Interface graphique** : Menus avec boutons et graphismes améliorés

### 🎮 Gameplay et Mécaniques
- [x] **Système d'armes** : Différents types d'armes avec caractéristiques uniques
- [x] **Capacités spéciales** : Compétences déblocables avec cooldowns
- [x] **Système de loot** : Objets ramassables avec effets temporaires (cœurs de vie)
- [x] **Système de bouclier** : Protection temporaire obtenue en tuant les ennemis d'élite
- [ ] **Boss battles** : Ennemis uniques avec patterns d'attaque complexes
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