"""
Main menu scene with animated background and navigation.
"""

import pygame
import math
import random
from typing import Optional
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState
from utils.asset_loader import AssetLoader
from ui import AnimatedButton


class MainMenu:
    """Main menu with animated background and navigation."""
    
    def __init__(self, screen: pygame.Surface, settings: dict = None):
        self.screen = screen
        self.settings = settings or {}
        self.running = True
        self.next_state: Optional[GameState] = None
        
        # Background
        self.background = self._create_background()
        self.bg_offset = 0
        
        # Title
        self.title_font = AssetLoader.get_default_font(64)
        self.subtitle_font = AssetLoader.get_default_font(24)
        
        # Stars animation
        self.stars = self._create_stars()
        
        # Buttons
        self.buttons = []
        self._create_buttons()
        
        # Animation
        self.time = 0
    
    def _create_background(self) -> pygame.Surface:
        """Create animated background."""
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            color = (
                int(10 + progress * 20),
                int(10 + progress * 10),
                int(30 + progress * 40)
            )
            pygame.draw.line(bg, color, (0, y), (SCREEN_WIDTH, y))
        return bg
    
    def _create_stars(self) -> list:
        """Create starfield for background."""
        stars = []
        for _ in range(100):
            stars.append({
                'x': random.random() * SCREEN_WIDTH,
                'y': random.random() * SCREEN_HEIGHT,
                'size': random.random() * 3,
                'speed': 0.5 + random.random() * 2
            })
        return stars
    
    def _create_buttons(self) -> None:
        """Create menu buttons."""
        button_width = 250
        button_height = 50
        start_y = SCREEN_HEIGHT // 2 - 40
        spacing = 60
        
        buttons_data = [
            ("START GAME", lambda: setattr(self, 'next_state', GameState.PLAYING)),
            ("SETTINGS", lambda: setattr(self, 'next_state', GameState.SETTINGS)),
            ("CONTROLS", lambda: setattr(self, 'next_state', GameState.CONTROLS)),
            ("HIGH SCORES", lambda: setattr(self, 'next_state', GameState.HIGHSCORES)),
            ("EXIT", lambda: setattr(self, 'next_state', GameState.QUIT)),
        ]
        
        for i, (text, callback) in enumerate(buttons_data):
            button = AnimatedButton(
                SCREEN_WIDTH // 2,
                start_y + i * spacing,
                button_width,
                button_height,
                text=text,
                font_size=28,
                color=(30, 30, 60),
                hover_color=(60, 60, 120),
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
                self.next_state = GameState.QUIT
                return False
        
        return True
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update menu state."""
        self.time += dt
        
        # Get input state
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Update background
        self.bg_offset += dt * 20
        if self.bg_offset > SCREEN_HEIGHT:
            self.bg_offset = 0
        
        # Update stars
        for star in self.stars:
            star['y'] += star['speed'] * dt * 60
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.random() * SCREEN_WIDTH
        
        # Update buttons
        for button in self.buttons:
            button.update(dt, mouse_pos, mouse_pressed)
        
        return self.next_state
    
    def render(self) -> None:
        """Render the menu."""
        # Background
        self.screen.blit(self.background, (0, 0))
        
        # Stars
        for star in self.stars:
            brightness = int(150 + 105 * math.sin(self.time * 2 + star['x'] * 0.01))
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, 
                             (int(star['x']), int(star['y'])), 
                             int(star['size']))
        
        # Title
        title_text = "NEBULA DEFENDER"
        title_surface = self.title_font.render(title_text, True, COLORS['UI_HIGHLIGHT'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        # Title glow effect
        glow_surface = self.title_font.render(title_text, True, COLORS['GOLD'])
        glow_alpha = int(100 + 100 * math.sin(self.time * 3))
        glow_surface.set_alpha(glow_alpha)
        
        self.screen.blit(glow_surface, (title_rect.x - 2, title_rect.y - 2))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle = self.subtitle_font.render("Press START to Begin", True, COLORS['LIGHT_GRAY'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Buttons
        for button in self.buttons:
            button.render(self.screen)
    
    def run(self) -> GameState:
        """Run the menu loop and return next state."""
        clock = pygame.time.Clock()
        
        # Wait for mouse button to be released before starting (prevents accidental clicks)
        waiting_for_mouse_release = pygame.mouse.get_pressed()[0]
        while waiting_for_mouse_release:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return GameState.QUIT
            if not pygame.mouse.get_pressed()[0]:
                waiting_for_mouse_release = False
            clock.tick(60)
        
        while self.running and self.next_state is None:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.next_state = GameState.QUIT
                    break
                if not self.handle_event(event):
                    break
            
            if self.next_state is not None:
                break
            
            result = self.update(dt)
            if result:
                return result
            
            self.render()
            pygame.display.flip()
        
        return self.next_state or GameState.MENU
