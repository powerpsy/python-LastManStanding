# Progression des Capacités - Last Man Standing

## Système simplifié des Orbes d'Énergie

### Nouveau comportement :
- **Durée de vie** : ∞ (permanentes)
- **Spawn automatique** : Non (seulement à la progression)
- **Progression** : Nouvelle orbe à chaque niveau jusqu'au niveau 7

### Tableau de progression :

| Niveau | Orbes d'Énergie | Éclairs (délai) | Commentaire |
|--------|-----------------|------------------|-------------|
| 1      | 1               | 1.0s            | Début du jeu |
| 2      | 2               | 1.0s            | +1 orbe |
| 3      | 3               | 1.0s            | +1 orbe |
| 4      | 4               | 1.0s            | +1 orbe |
| 5      | 5               | 0.9s            | +1 orbe + amélioration éclairs |
| 6      | 6               | 0.9s            | +1 orbe |
| 7      | 7               | 0.9s            | +1 orbe (maximum) |
| 8      | 7               | 0.9s            | Maximum orbes atteint |
| 10     | 7               | 0.8s            | Amélioration éclairs |
| 15     | 7               | 0.7s            | Amélioration éclairs |
| 20     | 7               | 0.6s            | Amélioration éclairs |
| 25     | 7               | 0.5s            | Amélioration éclairs |
| 30+    | 7               | 0.1s            | Maximum éclairs atteint |

### Formules :
- **Orbes d'énergie** : `min(niveau, 7)` (maximum 7)
- **Éclairs** : `1.0s - (niveau // 5) * 0.1s` (minimum 0.1s)

### Changements apportés :
1. ✅ Progression rapide des orbes (1 par niveau)
2. ✅ Maximum de 7 orbes au niveau 7
3. ✅ Orbes permanentes (pas de durée de vie)
4. ✅ Progression claire et prévisible
5. ✅ Séparation des progressions orbes/éclairs
6. ✅ Gameplay plus dynamique en début de partie
7. ✅ **Nouveau** : Éclairs avec chaînage (50% de chance)

### Système d'Éclairs Chaînés :
- **Chance de chaînage** : 50% (configurable)
- **Portée initiale** : 30% de la largeur d'écran
- **Portée de chaînage** : 20% de la largeur d'écran
- **Visuel** : Éclairs chaînés en violet/magenta
- **Dégâts** : Identiques pour cible primaire et secondaire
- **Points** : 15 pts (primaire), 10 pts (chaîné)
