"""
Game over scene with score display and options.
"""

import pygame
import math
from typing import Optional
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState
from utils.asset_loader import AssetLoader
from ui import AnimatedButton

# ScoreManager imported at end to avoid circular imports
ScoreManager = None


class GameOverScene:
    """Game over screen with final score display."""
    
    def __init__(self, screen: pygame.Surface, score: int = 0, 
                 wave: int = 0, is_new_highscore: bool = False):
        self.screen = screen
        self.score = score
        self.wave = wave
        self.is_new_highscore = is_new_highscore
        self.running = True
        self.next_state: Optional[GameState] = None
        
        # Background
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))
        
        # Fonts
        self.title_font = AssetLoader.get_default_font(64)
        self.score_font = AssetLoader.get_default_font(48)
        self.small_font = AssetLoader.get_default_font(24)
        
        # Animation
        self.time = 0
        self.score_reveal = 0
        
        # Buttons
        self.buttons = []
        self._create_buttons()
        
        # High scores
        _import_score_manager()
        self.score_manager = ScoreManager()
        self.high_scores = self.score_manager.get_high_scores()
    
    def _create_buttons(self) -> None:
        """Create game over buttons."""
        button_width = 200
        button_height = 50
        start_y = SCREEN_HEIGHT // 2 + 100
        spacing = 60
        
        def restart():
            self.next_state = GameState.PLAYING
        
        def main_menu():
            self.next_state = GameState.MENU
        
        def quit_game():
            self.next_state = GameState.QUIT
        
        buttons_data = [
            ("TRY AGAIN", restart),
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
                font_size=26,
                color=(60, 30, 30),
                hover_color=(100, 50, 50),
                text_color=COLORS['WHITE'],
                border_color=COLORS['RED'],
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
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_state = GameState.PLAYING
                return False
            if event.key == pygame.K_ESCAPE:
                self.next_state = GameState.MENU
                return False
        
        return True
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update game over scene."""
        self.time += dt
        
        # Score reveal animation
        if self.score_reveal < self.score:
            self.score_reveal = min(
                self.score,
                self.score_reveal + int(self.score * dt * 2) + 100
            )
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for button in self.buttons:
            button.update(dt, mouse_pos, mouse_pressed)
        
        return self.next_state
    
    def render(self) -> None:
        """Render game over screen."""
        # Overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Game Over title with animation
        title_color = COLORS['RED'] if math.sin(self.time * 3) > 0 else COLORS['ORANGE']
        title = self.title_font.render("GAME OVER", True, title_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        # Shake effect
        shake_x = int(math.sin(self.time * 20) * 3)
        self.screen.blit(title, (title_rect.x + shake_x, title_rect.y))
        
        # Score display
        score_text = f"SCORE: {self.score_reveal:,}"
        score_surface = self.score_font.render(score_text, True, COLORS['GOLD'])
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        
        # Glow effect
        glow_alpha = int(100 + 100 * math.sin(self.time * 4))
        glow_surface = self.score_font.render(score_text, True, COLORS['YELLOW'])
        glow_surface.set_alpha(glow_alpha)
        self.screen.blit(glow_surface, (score_rect.x - 2, score_rect.y - 2))
        self.screen.blit(score_surface, score_rect)
        
        # Wave reached
        wave_text = f"WAVE REACHED: {self.wave}"
        wave_surface = self.small_font.render(wave_text, True, COLORS['WHITE'])
        wave_rect = wave_surface.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(wave_surface, wave_rect)
        
        # High score indicator
        if self.is_new_highscore:
            new_hs_text = "NEW HIGH SCORE!"
            new_hs_surface = self.small_font.render(new_hs_text, True, COLORS['GREEN'])
            new_hs_rect = new_hs_surface.get_rect(center=(SCREEN_WIDTH // 2, 320))
            
            # Pulse effect
            scale = 1.0 + 0.1 * math.sin(self.time * 8)
            scaled = pygame.transform.scale(
                new_hs_surface,
                (int(new_hs_surface.get_width() * scale),
                 int(new_hs_surface.get_height() * scale))
            )
            scaled_rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, 320))
            self.screen.blit(scaled, scaled_rect)
        
        # Top 3 high scores
        y_pos = 380
        self.screen.blit(
            self.small_font.render("HIGH SCORES", True, COLORS['UI_HIGHLIGHT']),
            (SCREEN_WIDTH // 2 - 50, y_pos)
        )
        
        y_pos += 35
        for i, entry in enumerate(self.high_scores[:3]):
            rank = i + 1
            score = entry['score']
            date = entry['date']
            
            text = f"{rank}. {score:,}  {date}"
            color = COLORS['GOLD'] if i == 0 else COLORS['WHITE']
            surface = self.small_font.render(text, True, color)
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(surface, rect)
            y_pos += 25
        
        # Buttons
        for button in self.buttons:
            button.render(self.screen)
    
    def run(self) -> GameState:
        """Run the game over loop."""
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


# Import at end - resolve circular import
def _import_score_manager():
    global ScoreManager
    from managers import ScoreManager as SM
    ScoreManager = SM
