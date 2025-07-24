#!/usr/bin/env python3
"""
Test des effets de transition style Star Wars
============================================
Fichier de test pour expérimenter avec différents effets de transition
"""

import pygame
import math
import sys

class TransitionEffects:
    """Classe pour gérer les effets de transition"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def wipe_horizontal_left_to_right(self, surface_old, surface_new, progress):
        """Transition wipe horizontale de gauche à droite (classique Star Wars)"""
        wipe_x = int(self.screen_width * progress)
        
        # Dessiner l'ancienne scène
        return_surface = surface_old.copy()
        
        # Dessiner la nouvelle scène par-dessus (partie révélée)
        if wipe_x > 0:
            new_rect = pygame.Rect(0, 0, wipe_x, self.screen_height)
            return_surface.blit(surface_new, (0, 0), new_rect)
            
        return return_surface
    
    def wipe_horizontal_right_to_left(self, surface_old, surface_new, progress):
        """Transition wipe horizontale de droite à gauche"""
        wipe_x = int(self.screen_width * (1 - progress))
        
        return_surface = surface_old.copy()
        
        if wipe_x < self.screen_width:
            new_rect = pygame.Rect(wipe_x, 0, self.screen_width - wipe_x, self.screen_height)
            return_surface.blit(surface_new, (wipe_x, 0), new_rect)
            
        return return_surface
    
    def wipe_vertical_top_to_bottom(self, surface_old, surface_new, progress):
        """Transition wipe verticale de haut en bas"""
        wipe_y = int(self.screen_height * progress)
        
        return_surface = surface_old.copy()
        
        if wipe_y > 0:
            new_rect = pygame.Rect(0, 0, self.screen_width, wipe_y)
            return_surface.blit(surface_new, (0, 0), new_rect)
            
        return return_surface
    
    def wipe_vertical_split(self, surface_old, surface_new, progress):
        """Transition wipe verticale double : gauche de haut en bas, droite de bas en haut"""
        return_surface = surface_old.copy()
        
        # Calculer les positions de wipe pour chaque moitié
        wipe_y_top = int(self.screen_height * progress)  # Progression de haut en bas
        wipe_y_bottom = int(self.screen_height * (1 - progress))  # Progression de bas en haut
        
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
    
    def wipe_diagonal(self, surface_old, surface_new, progress):
        """Transition wipe diagonale (de haut-gauche vers bas-droite)"""
        return_surface = surface_old.copy()  # Commencer par l'ancienne scène
        
        # Calculer la ligne diagonale
        diagonal_offset = int((self.screen_width + self.screen_height) * progress)
        
        # Dessiner pixel par pixel la nouvelle scène selon la ligne diagonale
        for x in range(self.screen_width):
            for y in range(self.screen_height):
                if x + y < diagonal_offset:
                    # Copier le pixel de la nouvelle scène
                    pixel_color = surface_new.get_at((x, y))
                    return_surface.set_at((x, y), pixel_color)
        
        return return_surface
    
    def wipe_diagonal_reverse(self, surface_old, surface_new, progress):
        """Transition wipe diagonale inverse (de bas-gauche vers haut-droite)"""
        return_surface = surface_old.copy()  # Commencer par l'ancienne scène
        
        # Calculer la ligne diagonale inverse
        # Pour aller de bas-gauche vers haut-droite, on utilise (screen_height - y) + x
        diagonal_offset = int((self.screen_width + self.screen_height) * progress)
        
        # Dessiner pixel par pixel la nouvelle scène selon la ligne diagonale inverse
        for x in range(self.screen_width):
            for y in range(self.screen_height):
                # Formule pour la diagonale de bas-gauche vers haut-droite
                if (self.screen_height - y - 1) + x < diagonal_offset:
                    # Copier le pixel de la nouvelle scène
                    pixel_color = surface_new.get_at((x, y))
                    return_surface.set_at((x, y), pixel_color)
        
        return return_surface
    
    def iris_close(self, surface_old, surface_new, progress):
        """Transition iris qui se ferme (cercle qui rétrécit)"""
        return_surface = surface_new.copy()  # Commencer par la nouvelle scène
        
        # Calculer le rayon du cercle (l'ancienne scène est visible dans le cercle qui rétrécit)
        max_radius = math.sqrt(self.screen_width**2 + self.screen_height**2) / 2
        current_radius = int(max_radius * (1 - progress))
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        if current_radius > 0:
            # Dessiner l'ancienne scène pixel par pixel dans le cercle
            for x in range(max(0, center_x - current_radius), min(self.screen_width, center_x + current_radius + 1)):
                for y in range(max(0, center_y - current_radius), min(self.screen_height, center_y + current_radius + 1)):
                    # Vérifier si le pixel est dans le cercle
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= current_radius:
                        pixel_color = surface_old.get_at((x, y))
                        return_surface.set_at((x, y), pixel_color)
        
        return return_surface
    
    def iris_open(self, surface_old, surface_new, progress):
        """Transition iris qui s'ouvre (cercle qui grandit)"""
        return_surface = surface_old.copy()  # Commencer par l'ancienne scène
        
        # Calculer le rayon du cercle (la nouvelle scène est visible dans le cercle qui grandit)
        max_radius = math.sqrt(self.screen_width**2 + self.screen_height**2) / 2
        current_radius = int(max_radius * progress)
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        if current_radius > 0:
            # Dessiner la nouvelle scène pixel par pixel dans le cercle
            for x in range(max(0, center_x - current_radius), min(self.screen_width, center_x + current_radius + 1)):
                for y in range(max(0, center_y - current_radius), min(self.screen_height, center_y + current_radius + 1)):
                    # Vérifier si le pixel est dans le cercle
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= current_radius:
                        pixel_color = surface_new.get_at((x, y))
                        return_surface.set_at((x, y), pixel_color)
        
        return return_surface
    
    def slide_left(self, surface_old, surface_new, progress):
        """Transition glissement vers la gauche"""
        offset_x = int(self.screen_width * progress)
        
        return_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Dessiner l'ancienne scène qui sort
        return_surface.blit(surface_old, (-offset_x, 0))
        
        # Dessiner la nouvelle scène qui entre
        return_surface.blit(surface_new, (self.screen_width - offset_x, 0))
        
        return return_surface
    
    def fade(self, surface_old, surface_new, progress):
        """Transition fondu enchaîné"""
        return_surface = surface_old.copy()
        
        # Créer une copie de la nouvelle surface avec transparence
        alpha_surface = surface_new.copy()
        alpha_surface.set_alpha(int(255 * progress))
        
        return_surface.blit(alpha_surface, (0, 0))
        return return_surface


class TransitionTest:
    """Classe principale pour tester les transitions"""
    
    def __init__(self):
        pygame.init()
        
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Test des Transitions Star Wars")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Créer les surfaces de test
        self.scene_old = self.create_old_scene()
        self.scene_new = self.create_new_scene()
        
        # Gestionnaire d'effets
        self.effects = TransitionEffects(self.screen_width, self.screen_height)
        
        # État de la transition
        self.transition_active = False
        self.transition_progress = 0.0
        self.transition_duration = 0.5
        self.transition_start_time = 0
        
        # Liste des transitions disponibles
        self.transitions = [
            ("Wipe Horizontal (L→R)", self.effects.wipe_horizontal_left_to_right),
            ("Wipe Horizontal (R→L)", self.effects.wipe_horizontal_right_to_left),
            ("Wipe Vertical (T→B)", self.effects.wipe_vertical_top_to_bottom),
            ("Wipe Vertical Split", self.effects.wipe_vertical_split),
            ("Wipe Diagonal ↘", self.effects.wipe_diagonal),
            ("Wipe Diagonal ↗", self.effects.wipe_diagonal_reverse),
            ("Iris Close", self.effects.iris_close),
            ("Iris Open", self.effects.iris_open),
            ("Fade", self.effects.fade),
        ]
        
        self.current_transition = 0
        
    def create_old_scene(self):
        """Crée la scène ancienne (orange)"""
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill((255, 140, 0))  # Orange
        
        # Ajouter du texte
        title = self.font.render("ANCIENNE SCÈNE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        surface.blit(title, title_rect)
        
        subtitle = self.small_font.render("(Écran Orange)", True, (255, 255, 255))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, self.screen_height//2))
        surface.blit(subtitle, subtitle_rect)
        
        # Ajouter quelques éléments visuels
        for i in range(10):
            x = (i * self.screen_width // 10) + 50
            y = self.screen_height // 2 + 100
            pygame.draw.circle(surface, (255, 200, 100), (x, y), 30)
            pygame.draw.circle(surface, (200, 100, 0), (x, y), 30, 3)
        
        return surface
    
    def create_new_scene(self):
        """Crée la nouvelle scène (bleue)"""
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill((0, 100, 200))  # Bleu
        
        # Ajouter du texte
        title = self.font.render("NOUVELLE SCÈNE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        surface.blit(title, title_rect)
        
        subtitle = self.small_font.render("(Écran Bleu)", True, (255, 255, 255))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, self.screen_height//2))
        surface.blit(subtitle, subtitle_rect)
        
        # Ajouter quelques éléments visuels
        for i in range(8):
            x = (i * self.screen_width // 8) + 80
            y = self.screen_height // 2 + 100
            pygame.draw.rect(surface, (100, 150, 255), (x-20, y-20, 40, 40))
            pygame.draw.rect(surface, (0, 50, 150), (x-20, y-20, 40, 40), 3)
        
        return surface
    
    def start_transition(self):
        """Démarre une transition"""
        if not self.transition_active:
            self.transition_active = True
            self.transition_progress = 0.0
            self.transition_start_time = pygame.time.get_ticks()
    
    def update_transition(self):
        """Met à jour l'état de la transition"""
        if self.transition_active:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.transition_start_time) / 1000.0  # en secondes
            
            self.transition_progress = min(1.0, elapsed / self.transition_duration)
            
            if self.transition_progress >= 1.0:
                self.transition_active = False
                self.transition_progress = 0.0
    
    def draw_ui(self):
        """Dessine l'interface utilisateur"""
        # Fond semi-transparent pour l'UI
        ui_surface = pygame.Surface((self.screen_width, 120))
        ui_surface.fill((0, 0, 0))
        ui_surface.set_alpha(180)
        self.screen.blit(ui_surface, (0, 0))
        
        # Instructions
        instructions = [
            "ESPACE: Lancer la transition | ←→: Changer de transition | ESC: Quitter",
            f"Transition actuelle: {self.transitions[self.current_transition][0]}",
            f"Progression: {self.transition_progress:.1%}" if self.transition_active else "Prêt"
        ]
        
        for i, text in enumerate(instructions):
            color = (255, 255, 0) if i == 1 else (255, 255, 255)
            surface = self.small_font.render(text, True, color)
            self.screen.blit(surface, (10, 10 + i * 25))
    
    def run(self):
        """Boucle principale"""
        running = True
        
        while running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.start_transition()
                    elif event.key == pygame.K_LEFT:
                        self.current_transition = (self.current_transition - 1) % len(self.transitions)
                    elif event.key == pygame.K_RIGHT:
                        self.current_transition = (self.current_transition + 1) % len(self.transitions)
            
            # Mettre à jour la transition
            self.update_transition()
            
            # Dessiner la scène
            if self.transition_active:
                # Appliquer l'effet de transition
                transition_func = self.transitions[self.current_transition][1]
                result_surface = transition_func(self.scene_old, self.scene_new, self.transition_progress)
                self.screen.blit(result_surface, (0, 0))
            else:
                # Dessiner la scène statique (ancienne)
                self.screen.blit(self.scene_old, (0, 0))
            
            # Dessiner l'UI
            self.draw_ui()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    test = TransitionTest()
    test.run()
