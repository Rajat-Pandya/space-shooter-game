"""
Controls display scene.
"""

import pygame
from typing import Optional
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState
from utils.asset_loader import AssetLoader
from ui import AnimatedButton


class ControlsScene:
    """Display game controls."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.running = True
        self.next_state: Optional[GameState] = None
        
        # Background
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        
        # Fonts
        self.title_font = AssetLoader.get_default_font(48)
        self.heading_font = AssetLoader.get_default_font(32)
        self.text_font = AssetLoader.get_default_font(24)
        
        # Controls data
        self.controls = [
            ("MOVEMENT", [
                ("Move Left", "LEFT ARROW / A"),
                ("Move Right", "RIGHT ARROW / D"),
                ("Move Up", "UP ARROW / W"),
                ("Move Down", "DOWN ARROW / S"),
            ]),
            ("ACTIONS", [
                ("Shoot", "SPACE"),
                ("Pause", "ESC"),
            ]),
            ("POWER-UPS", [
                ("Rapid Fire", "Faster shooting"),
                ("Double Bullets", "Two bullets at once"),
                ("Shield", "Temporary invincibility"),
                ("Health", "Restore health"),
                ("Speed", "Faster movement"),
                ("Laser", "Powerful laser weapon"),
            ]),
        ]
        
        # Button - positioned at bottom of screen
        self.back_button = AnimatedButton(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, 200, 45,
            text="BACK", font_size=26,
            color=(40, 40, 70), hover_color=(70, 70, 120),
            text_color=COLORS['WHITE'],
            border_color=COLORS['UI_HIGHLIGHT'],
            callback=None  # Handle click manually in update
        )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.QUIT:
            print("QUIT event received in ControlsScene")
            self.next_state = GameState.QUIT
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC key pressed in ControlsScene")
                self.next_state = GameState.MENU
                return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse button down at: {event.pos}")
        
        return True
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update controls scene."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Check if button was clicked
        button_clicked = self.back_button.update(dt, mouse_pos, mouse_pressed)
        if button_clicked:
            print(f"Back button clicked! Setting next_state to MENU")
            self.next_state = GameState.MENU
            return self.next_state
        
        return self.next_state
    
    def render(self) -> None:
        """Render controls scene."""
        # Overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Title
        title = self.title_font.render("CONTROLS", True, COLORS['UI_HIGHLIGHT'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Render controls - compact layout
        y_pos = 110
        x_left = 80
        x_right = SCREEN_WIDTH - 80
        
        for section_name, controls in self.controls:
            # Section heading
            heading = self.heading_font.render(section_name, True, COLORS['GOLD'])
            self.screen.blit(heading, (x_left, y_pos))
            y_pos += 35
            
            # Controls in section
            for action, key in controls:
                action_surface = self.text_font.render(action, True, COLORS['WHITE'])
                key_surface = self.text_font.render(key, True, COLORS['CYAN'])
                
                # Right-align the key binding
                key_rect = key_surface.get_rect()
                key_rect.right = x_right
                key_rect.top = y_pos
                
                self.screen.blit(action_surface, (x_left + 20, y_pos))
                self.screen.blit(key_surface, key_rect)
                
                y_pos += 25
            
            y_pos += 10  # Smaller spacing between sections
        
        # Back button
        self.back_button.render(self.screen)
    
    def run(self) -> GameState:
        """Run the controls loop."""
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
        
        return self.next_state or GameState.MENU
