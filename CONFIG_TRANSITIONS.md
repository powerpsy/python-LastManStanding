# ⚙️ **SYSTÈME DE CONFIGURATION DES TRANSITIONS**

## 🎯 **NOUVEAU PARAMÈTRE CENTRALISÉ**

Toutes les transitions sont maintenant gérées par un **seul paramètre** dans `config.py` !

---

## 📁 **FICHIER : `config.py`**

### **Nouveau paramètre ajouté :**
```python
# Durée des transitions (en secondes)
self.TRANSITION_DURATION = 0.2  # Durée par défaut pour toutes les transitions
```

### **Emplacement :**
```python
# FPS fixe pour tous les presets
self.FPS = 60

# Durée des transitions (en secondes)  ← NOUVEAU
self.TRANSITION_DURATION = 0.2        ← NOUVEAU

# Paramètres de jeu fixes
self.PLAYER_MAX_HEALTH = 300
```

---

## 🔧 **FICHIER : `game.py`**

### **Toutes les transitions modifiées :**

**AVANT (durées codées en dur) :**
```python
duration=0.2,  # ❌ Valeur fixe
duration=0.4,  # ❌ Valeur fixe  
duration=0.5,  # ❌ Valeur fixe
```

**APRÈS (paramètre centralisé) :**
```python
duration=self.config.TRANSITION_DURATION,  # ✅ Configurable
```

### **Transitions mises à jour :**
- ✅ **Upgrade** : `wipe_vertical_split` / `wipe_vertical_split_reverse`
- ✅ **Skills** : `diagonal_top_left_to_bottom_right` / `diagonal_bottom_right_to_top_left`
- ✅ **Exit Menu** : `fade` (entrée/sortie)
- ✅ **Game Over** : `wipe_horizontal_left_to_right`
- ✅ **Auto-restart** : `fade`

---

## 🎮 **UTILISATION**

### **1. Modification Simple :**
```python
# Dans config.py, changez simplement :
self.TRANSITION_DURATION = 0.1  # Ultra-rapide
self.TRANSITION_DURATION = 0.2  # Rapide (par défaut)
self.TRANSITION_DURATION = 0.5  # Normal
self.TRANSITION_DURATION = 1.0  # Lent
```

### **2. Modification Dynamique :**
```python
# Dans le code du jeu :
game.config.TRANSITION_DURATION = 0.3  # Personnalisé
```

### **3. Test Facile :**
```bash
python test_transition_config.py
```

---

## 📊 **AVANTAGES DU NOUVEAU SYSTÈME**

### **🔧 Maintenance :**
- ✅ **Une seule ligne** à modifier pour changer toutes les transitions
- ✅ **Aucun risque** d'oublier une transition
- ✅ **Cohérence garantie** sur tous les effets
- ✅ **Facilité de test** avec différentes vitesses

### **🎛️ Configuration :**
- ✅ **Paramètre centralisé** dans config.py
- ✅ **Modification sans recompilation**
- ✅ **Ajustement en temps réel** possible
- ✅ **Valeurs par défaut** intelligentes

### **🧪 Tests :**
- ✅ **Script de test** interactif inclus
- ✅ **Choix de vitesse** facile
- ✅ **Validation immédiate** des changements
- ✅ **Comparaison** entre différentes vitesses

---

## 🎯 **EXEMPLES D'USAGE**

### **Transitions Ultra-Rapides (Gameplay intense) :**
```python
self.TRANSITION_DURATION = 0.1  # Réactivité maximale
```

### **Transitions Rapides (Par défaut) :**
```python
self.TRANSITION_DURATION = 0.2  # Équilibre optimal
```

### **Transitions Normales (Cinématique) :**
```python
self.TRANSITION_DURATION = 0.5  # Plus visuel
```

### **Transitions Lentes (Démonstration) :**
```python
self.TRANSITION_DURATION = 1.0  # Effet dramatique
```

---

## 🚀 **TEST INTERACTIF**

### **Lancer le test :**
```bash
python test_transition_config.py
```

### **Options disponibles :**
1. ⚡ **Ultra-rapide** (0.1s)
2. 🚀 **Rapide** (0.2s) - Par défaut  
3. ⚙️ **Normal** (0.5s)
4. 🐌 **Lent** (1.0s)
5. 🔥 **Personnalisé** (valeur libre)

---

## ✅ **RÉSULTAT**

### **Avant :**
- ❌ **8 durées** codées en dur dans game.py
- ❌ **Maintenance complexe** pour changer les vitesses
- ❌ **Risque d'incohérence** entre transitions
- ❌ **Tests fastidieux** de différentes vitesses

### **Après :**
- ✅ **1 paramètre** centralisé dans config.py
- ✅ **Modification ultra-simple**
- ✅ **Cohérence garantie**
- ✅ **Test interactif** inclus

---

## 🎛️ **SYSTÈME DE CONFIGURATION OPÉRATIONNEL !**

**Paramètre :** `config.TRANSITION_DURATION`  
**Valeur par défaut :** 0.2s  
**Flexibilité :** Totale  
**Maintenance :** Simplifiée  
**Statut :** ✅ **PRODUCTION READY**

**Date d'implémentation :** 25 Juillet 2025  
**Tests validés :** ✅ Complet
