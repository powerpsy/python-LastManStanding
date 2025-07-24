#!/usr/bin/env python3
"""
Système de transitions pour Last Man Standing
============================================
Effets de transition style Star Wars pour les changements d'écrans
"""

import pygame
import math

class TransitionManager:
    """Gestionnaire des effets de transition entre écrans"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # État de la transition
        self.is_active = False
        self.progress = 0.0
        self.duration = 2
        self.start_time = 0
        self.current_effect = None
        
        # Surfaces pour la transition
        self.surface_old = None
        self.surface_new = None
        
        # Callback à appeler quand la transition est terminée
        self.on_complete_callback = None
        
        # Surface de référence pour les captures d'écran
        self.screen_surface = None

    def start_transition(self, transition_type="wipe_horizontal", duration=0.2, on_complete=None):
        """
        Démarre une transition simple avec capture d'écran automatique
        
        Args:
            transition_type: Type de transition à utiliser
            duration: Durée de la transition en secondes
            on_complete: Fonction à appeler quand la transition est terminée
        """
        if self.is_active:
            return False  # Une transition est déjà en cours
            
        # Capturer l'écran actuel si une surface de référence est disponible
        if self.screen_surface:
            self.surface_old = self.screen_surface.copy()
        else:
            # Créer une surface vide si aucune référence
            self.surface_old = pygame.Surface((self.screen_width, self.screen_height))
            self.surface_old.fill((0, 0, 0))
        
        # Pour l'instant, surface nouvelle = surface noire (sera mise à jour après callback)
        self.surface_new = pygame.Surface((self.screen_width, self.screen_height))
        self.surface_new.fill((0, 0, 0))
        
        self.current_effect = transition_type
        self.duration = duration
        self.on_complete_callback = on_complete
        
        self.is_active = True
        self.progress = 0.0
        self.start_time = pygame.time.get_ticks()
        
        return True
    
    def update_new_surface(self, new_surface):
        """Met à jour la surface 'nouvelle' pendant la transition"""
        if self.is_active and new_surface:
            self.surface_new = new_surface.copy()
    
    def set_screen_reference(self, screen_surface):
        """Définit la surface d'écran de référence pour les captures"""
        self.screen_surface = screen_surface
        
    def start_transition_with_surfaces(self, old_surface, new_surface, effect_name="wipe_horizontal", duration=1.0, on_complete=None):
        """
        Démarre une transition entre deux surfaces (méthode originale)
        
        Args:
            old_surface: Surface de l'écran actuel
            new_surface: Surface du nouvel écran
            effect_name: Nom de l'effet à utiliser
            duration: Durée de la transition en secondes
            on_complete: Fonction à appeler quand la transition est terminée
        """
        if self.is_active:
            return False  # Une transition est déjà en cours
            
        self.surface_old = old_surface.copy()
        self.surface_new = new_surface.copy()
        self.current_effect = effect_name
        self.duration = duration
        self.on_complete_callback = on_complete
        
        self.is_active = True
        self.progress = 0.0
        self.start_time = pygame.time.get_ticks()
        
        return True
    
    def update(self):
        """Met à jour l'état de la transition"""
        if not self.is_active:
            return False
            
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.start_time) / 1000.0  # en secondes
        
        self.progress = min(1.0, elapsed / self.duration)
        
        # À mi-parcours, exécuter le callback pour changer l'état
        # Pour la plupart des transitions, exécuter plus tôt pour éviter l'écran noir
        callback_threshold = 0.1 if self.current_effect in [
            "diagonal_top_left_to_bottom_right", 
            "diagonal_bottom_right_to_top_left",
            "fade",
            "iris_close",
            "iris_open",
            "wipe_horizontal_left_to_right",
            "wipe_horizontal",
            "wipe_vertical",
            "wipe_vertical_split",
            "wipe_vertical_split_reverse",
            "wipe_diagonal"
        ] else 0.5
        
        if self.progress >= callback_threshold and self.on_complete_callback and not hasattr(self, '_callback_executed'):
            self.on_complete_callback()
            self._callback_executed = True
        
        if self.progress >= 1.0:
            # Transition terminée
            self.is_active = False
            self.progress = 1.0
            
            # Nettoyer le flag de callback
            if hasattr(self, '_callback_executed'):
                delattr(self, '_callback_executed')
            
            # Nettoyer les surfaces pour économiser la mémoire
            self.surface_old = None
            self.surface_new = None
            self.on_complete_callback = None
            
            return True  # Transition terminée
        
        return False  # Transition en cours
    
    def render(self, screen):
        """Rend la transition sur l'écran"""
        if not self.is_active or not self.surface_old or not self.surface_new:
            return
            
        # Appliquer l'effet de transition
        result_surface = self._apply_effect(self.surface_old, self.surface_new, self.progress, self.current_effect)
        screen.blit(result_surface, (0, 0))
    
    def _apply_effect(self, surface_old, surface_new, progress, effect_name):
        """Applique l'effet de transition spécifié"""
        
        # Mapping des noms d'effets complets vers les méthodes
        if effect_name == "wipe_horizontal_left_to_right" or effect_name == "wipe_horizontal":
            return self._wipe_horizontal_left_to_right(surface_old, surface_new, progress)
        elif effect_name == "wipe_horizontal_right_to_left" or effect_name == "wipe_horizontal_reverse":
            return self._wipe_horizontal_right_to_left(surface_old, surface_new, progress)
        elif effect_name == "wipe_vertical_top_to_bottom" or effect_name == "wipe_vertical":
            return self._wipe_vertical_top_to_bottom(surface_old, surface_new, progress)
        elif effect_name == "wipe_vertical_bottom_to_top":
            return self._wipe_vertical_bottom_to_top(surface_old, surface_new, progress)
        elif effect_name == "wipe_vertical_split":
            return self._wipe_vertical_split(surface_old, surface_new, progress)
        elif effect_name == "wipe_vertical_split_reverse":
            return self._wipe_vertical_split_reverse(surface_old, surface_new, progress)
        elif effect_name == "diagonal_top_left_to_bottom_right" or effect_name == "wipe_diagonal":
            return self._wipe_diagonal(surface_old, surface_new, progress)
        elif effect_name == "diagonal_bottom_right_to_top_left" or effect_name == "wipe_diagonal_reverse":
            return self._wipe_diagonal_reverse(surface_old, surface_new, progress)
        elif effect_name == "diagonal_top_right_to_bottom_left":
            return self._wipe_diagonal_reverse(surface_old, surface_new, progress)  # Utiliser la même méthode pour l'instant
        elif effect_name == "diagonal_bottom_left_to_top_right":
            return self._wipe_diagonal(surface_old, surface_new, progress)  # Utiliser la même méthode pour l'instant
        elif effect_name == "iris_close":
            return self._iris_close(surface_old, surface_new, progress)
        elif effect_name == "iris_open":
            return self._iris_open(surface_old, surface_new, progress)
        elif effect_name == "fade":
            return self._fade(surface_old, surface_new, progress)
        else:
            # Effet par défaut : fade
            return self._fade(surface_old, surface_new, progress)
    
    def _wipe_horizontal_left_to_right(self, surface_old, surface_new, progress):
        """Transition wipe horizontale de gauche à droite (classique Star Wars)"""
        wipe_x = int(self.screen_width * progress)
        
        return_surface = surface_old.copy()
        
        if wipe_x > 0:
            new_rect = pygame.Rect(0, 0, wipe_x, self.screen_height)
            return_surface.blit(surface_new, (0, 0), new_rect)
            
        return return_surface
    
    def _wipe_horizontal_right_to_left(self, surface_old, surface_new, progress):
        """Transition wipe horizontale de droite à gauche"""
        wipe_x = int(self.screen_width * (1 - progress))
        
        return_surface = surface_old.copy()
        
        if wipe_x < self.screen_width:
            new_rect = pygame.Rect(wipe_x, 0, self.screen_width - wipe_x, self.screen_height)
            return_surface.blit(surface_new, (wipe_x, 0), new_rect)
            
        return return_surface
    
    def _wipe_vertical_top_to_bottom(self, surface_old, surface_new, progress):
        """Transition wipe verticale de haut en bas"""
        wipe_y = int(self.screen_height * progress)
        
        return_surface = surface_old.copy()
        
        if wipe_y > 0:
            new_rect = pygame.Rect(0, 0, self.screen_width, wipe_y)
            return_surface.blit(surface_new, (0, 0), new_rect)
            
        return return_surface
    
    def _wipe_vertical_bottom_to_top(self, surface_old, surface_new, progress):
        """Transition wipe verticale de bas en haut"""
        wipe_height = int(self.screen_height * progress)
        wipe_y = self.screen_height - wipe_height
        
        return_surface = surface_old.copy()
        
        if wipe_height > 0:
            new_rect = pygame.Rect(0, wipe_y, self.screen_width, wipe_height)
            return_surface.blit(surface_new, (0, wipe_y), new_rect)
            
        return return_surface
    
    def _wipe_vertical_split(self, surface_old, surface_new, progress):
        """Transition wipe verticale double : gauche de haut en bas, droite de bas en haut"""
        return_surface = surface_old.copy()
        
        wipe_y_top = int(self.screen_height * progress)
        wipe_y_bottom = int(self.screen_height * (1 - progress))
        
        # Moitié gauche : wipe de haut en bas
        if wipe_y_top > 0:
            left_rect = pygame.Rect(0, 0, self.screen_width // 2, wipe_y_top)
            return_surface.blit(surface_new, (0, 0), left_rect)
        
        # Moitié droite : wipe de bas en haut
        if wipe_y_bottom < self.screen_height:
            right_rect = pygame.Rect(self.screen_width // 2, wipe_y_bottom, 
                                   self.screen_width // 2, self.screen_height - wipe_y_bottom)
            return_surface.blit(surface_new, (self.screen_width // 2, wipe_y_bottom), right_rect)
        
        return return_surface
    
    def _wipe_vertical_split_reverse(self, surface_old, surface_new, progress):
        """Transition wipe verticale double inverse : gauche de bas en haut, droite de haut en bas"""
        return_surface = surface_old.copy()
        
        wipe_y_bottom = int(self.screen_height * progress)
        wipe_y_top = int(self.screen_height * (1 - progress))
        
        # Moitié gauche : wipe de bas en haut
        if wipe_y_bottom > 0:
            left_rect = pygame.Rect(0, self.screen_height - wipe_y_bottom, self.screen_width // 2, wipe_y_bottom)
            return_surface.blit(surface_new, (0, self.screen_height - wipe_y_bottom), left_rect)
        
        # Moitié droite : wipe de haut en bas
        if wipe_y_top < self.screen_height:
            right_rect = pygame.Rect(self.screen_width // 2, 0, 
                                   self.screen_width // 2, self.screen_height - wipe_y_top)
            return_surface.blit(surface_new, (self.screen_width // 2, 0), right_rect)
        
        return return_surface
    
    def _wipe_diagonal(self, surface_old, surface_new, progress):
        """Transition wipe diagonale simple (de haut-gauche vers bas-droite)"""
        return_surface = surface_old.copy()
        
        # Calculer la position de la ligne diagonale
        diagonal_pos = int((self.screen_width + self.screen_height) * progress)
        
        # Méthode simple : dessiner ligne par ligne
        for y in range(self.screen_height):
            line_end_x = diagonal_pos - y
            if line_end_x > 0:
                line_width = min(line_end_x, self.screen_width)
                if line_width > 0:
                    # Copier une ligne de la nouvelle surface
                    line_rect = pygame.Rect(0, y, line_width, 1)
                    return_surface.blit(surface_new, (0, y), line_rect)
        
        return return_surface
    
    def _wipe_diagonal_reverse(self, surface_old, surface_new, progress):
        """Transition wipe diagonale inverse (de bas-droite vers haut-gauche)"""
        return_surface = surface_old.copy()
        
        # Calculer la position de la ligne diagonale (depuis le bas-droite)
        diagonal_pos = int((self.screen_width + self.screen_height) * progress)
        
        # Méthode simple : dessiner ligne par ligne depuis le bas
        for y in range(self.screen_height):
            line_start_x = self.screen_width - (diagonal_pos - (self.screen_height - 1 - y))
            if line_start_x < self.screen_width:
                line_start_x = max(0, line_start_x)
                line_width = self.screen_width - line_start_x
                if line_width > 0:
                    # Copier une ligne de la nouvelle surface
                    line_rect = pygame.Rect(line_start_x, y, line_width, 1)
                    return_surface.blit(surface_new, (line_start_x, y), line_rect)
        
        return return_surface
    
    def _iris_close(self, surface_old, surface_new, progress):
        """Transition iris qui se ferme (cercle qui rétrécit)"""
        return_surface = surface_new.copy()
        
        max_radius = math.sqrt(self.screen_width**2 + self.screen_height**2) / 2
        current_radius = int(max_radius * (1 - progress))
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        if current_radius > 0:
            for x in range(max(0, center_x - current_radius), min(self.screen_width, center_x + current_radius + 1)):
                for y in range(max(0, center_y - current_radius), min(self.screen_height, center_y + current_radius + 1)):
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= current_radius:
                        pixel_color = surface_old.get_at((x, y))
                        return_surface.set_at((x, y), pixel_color)
        
        return return_surface
    
    def _iris_open(self, surface_old, surface_new, progress):
        """Transition iris qui s'ouvre (cercle qui grandit)"""
        return_surface = surface_old.copy()
        
        max_radius = math.sqrt(self.screen_width**2 + self.screen_height**2) / 2
        current_radius = int(max_radius * progress)
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        if current_radius > 0:
            for x in range(max(0, center_x - current_radius), min(self.screen_width, center_x + current_radius + 1)):
                for y in range(max(0, center_y - current_radius), min(self.screen_height, center_y + current_radius + 1)):
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= current_radius:
                        pixel_color = surface_new.get_at((x, y))
                        return_surface.set_at((x, y), pixel_color)
        
        return return_surface
    
    def _fade(self, surface_old, surface_new, progress):
        """Transition fondu enchaîné"""
        return_surface = surface_old.copy()
        
        alpha_surface = surface_new.copy()
        alpha_surface.set_alpha(int(255 * progress))
        
        return_surface.blit(alpha_surface, (0, 0))
        return return_surface

# Types de transitions disponibles avec leurs noms d'usage
TRANSITION_TYPES = {
    "wipe_horizontal": "Wipe Horizontal →",
    "wipe_horizontal_reverse": "Wipe Horizontal ←",
    "wipe_vertical": "Wipe Vertical ↓",
    "wipe_vertical_split": "Wipe Vertical Split ↕",
    "wipe_vertical_split_reverse": "Wipe Vertical Split Reverse ↕",
    "wipe_diagonal": "Wipe Diagonal ↘",
    "wipe_diagonal_reverse": "Wipe Diagonal ↗",
    "iris_close": "Iris Close ○",
    "iris_open": "Iris Open ◯",
    "fade": "Fade"
}
