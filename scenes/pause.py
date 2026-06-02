"""
Pause menu scene.
"""

import pygame
from typing import Optional
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState
from utils.asset_loader import AssetLoader
from ui import AnimatedButton


class PauseMenu:
    """Pause menu with resume and options."""
    
    def __init__(self, screen: pygame.Surface, gameplay_scene=None):
        self.screen = screen
        self.gameplay_scene = gameplay_scene
        self.running = True
        self.next_state: Optional[GameState] = None
        
        # Background
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        
        # Fonts
        self.title_font = AssetLoader.get_default_font(48)
        
        # Buttons
        self.buttons = []
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create pause menu buttons."""
        button_width = 220
        button_height = 45
        start_y = SCREEN_HEIGHT // 2 - 40
        spacing = 55
        
        def resume():
            self.next_state = GameState.PLAYING
        
        def restart():
            if self.gameplay_scene:
                self.gameplay_scene.reset()
            self.next_state = GameState.PLAYING
        
        def settings():
            self.next_state = GameState.SETTINGS
        
        def main_menu():
            self.next_state = GameState.MENU
        
        def quit_game():
            self.next_state = GameState.QUIT
        
        buttons_data = [
            ("RESUME", resume),
            ("RESTART", restart),
            ("SETTINGS", settings),
            ("MAIN MENU", main_menu),
            ("QUIT", quit_game),
        ]
        
        for i, (text, callback) in enumerate(buttons_data):
            button = AnimatedButton(
                SCREEN_WIDTH // 2,
                start_y + i * spacing,
                button_width,
                button_height,
                text=text,
                font_size=24,
                color=(40, 40, 70),
                hover_color=(70, 70, 120),
                text_color=COLORS['WHITE'],
                border_color=COLORS['UI_HIGHLIGHT'],
                border_width=2,
                callback=callback
            )
            self.buttons.append(button)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.QUIT:
            self.next_state = GameState.QUIT
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = GameState.PLAYING
                return False
        
        return True
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update pause menu."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for button in self.buttons:
            button.update(dt, mouse_pos, mouse_pressed)
        
        return self.next_state
    
    def render(self, background: pygame.Surface = None) -> None:
        """Render pause menu."""
        # Draw previous frame if available
        if background:
            self.screen.blit(background, (0, 0))
        
        # Overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Title
        title = self.title_font.render("PAUSED", True, COLORS['WHITE'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Shadow
        shadow = self.title_font.render("PAUSED", True, COLORS['BLACK'])
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # Buttons
        for button in self.buttons:
            button.render(self.screen)
    
    def run(self) -> GameState:
        """Run the pause menu loop."""
        clock = pygame.time.Clock()
        
        while self.running and self.next_state is None:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if not self.handle_event(event):
                    break
            
            result = self.update(dt)
            if result:
                return result
            
            self.render()
            pygame.display.flip()
        
        return self.next_state or GameState.PLAYING
