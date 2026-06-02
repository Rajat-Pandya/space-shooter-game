"""
High scores display scene.
"""

import pygame
import math
from typing import Optional
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState
from utils.asset_loader import AssetLoader
from ui import AnimatedButton

# Lazy import ScoreManager
ScoreManager = None


def _import_score_manager():
    global ScoreManager
    from managers import ScoreManager as SM
    ScoreManager = SM


class HighScoresScene:
    """Display high scores table."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.running = True
        self.next_state: Optional[GameState] = None
        
        # Background
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        
        # Fonts
        self.title_font = AssetLoader.get_default_font(48)
        self.header_font = AssetLoader.get_default_font(28)
        self.score_font = AssetLoader.get_default_font(24)
        self.small_font = AssetLoader.get_default_font(18)
        
        # Score manager
        _import_score_manager()
        self.score_manager = ScoreManager()
        self.high_scores = self.score_manager.get_high_scores()
        
        # Animation
        self.time = 0
        
        # Buttons
        def back():
            self.next_state = GameState.MENU
        
        def clear_scores():
            self.score_manager.clear_high_scores()
            self.high_scores = self.score_manager.get_high_scores()
        
        self.buttons = [
            AnimatedButton(
                SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 80, 160, 45,
                text="BACK", font_size=24,
                color=(40, 40, 70), hover_color=(70, 70, 120),
                text_color=COLORS['WHITE'],
                border_color=COLORS['UI_HIGHLIGHT'],
                callback=back
            ),
            AnimatedButton(
                SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT - 80, 160, 45,
                text="CLEAR", font_size=24,
                color=(70, 40, 40), hover_color=(120, 70, 70),
                text_color=COLORS['WHITE'],
                border_color=COLORS['RED'],
                callback=clear_scores
            ),
        ]
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.QUIT:
            self.next_state = GameState.QUIT
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = GameState.MENU
                return False
        
        return True
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update high scores scene."""
        self.time += dt
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for button in self.buttons:
            button.update(dt, mouse_pos, mouse_pressed)
        
        return self.next_state
    
    def render(self) -> None:
        """Render high scores scene."""
        # Overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Title with glow
        title = self.title_font.render("HIGH SCORES", True, COLORS['UI_HIGHLIGHT'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        
        glow_alpha = int(100 + 100 * math.sin(self.time * 3))
        glow = self.title_font.render("HIGH SCORES", True, COLORS['GOLD'])
        glow.set_alpha(glow_alpha)
        self.screen.blit(glow, (title_rect.x - 2, title_rect.y - 2))
        self.screen.blit(title, title_rect)
        
        # Table headers
        header_y = 140
        rank_x = 150
        score_x = 300
        wave_x = 450
        date_x = 600
        
        headers = ["RANK", "SCORE", "WAVE", "DATE"]
        positions = [rank_x, score_x, wave_x, date_x]
        
        for header, x in zip(headers, positions):
            surface = self.header_font.render(header, True, COLORS['GOLD'])
            rect = surface.get_rect(center=(x, header_y))
            self.screen.blit(surface, rect)
        
        # Separator line
        pygame.draw.line(self.screen, COLORS['GOLD'], 
                        (100, header_y + 25), 
                        (SCREEN_WIDTH - 100, header_y + 25), 2)
        
        # Scores
        if self.high_scores:
            y_pos = header_y + 60
            for i, entry in enumerate(self.high_scores[:10]):
                # Highlight top 3
                if i < 3:
                    bg_color = (40, 30, 20) if i == 0 else (30, 30, 30)
                    if i > 0:
                        bg_color = (35, 35, 25) if i == 1 else (30, 35, 30)
                    
                    pygame.draw.rect(self.screen, bg_color,
                                   (100, y_pos - 15, SCREEN_WIDTH - 200, 35), 
                                   border_radius=5)
                
                # Rank
                rank_colors = [COLORS['GOLD'], (192, 192, 192), (205, 127, 50)]
                rank_color = rank_colors[i] if i < 3 else COLORS['WHITE']
                rank_text = f"#{i + 1}"
                rank_surface = self.score_font.render(rank_text, True, rank_color)
                self.screen.blit(rank_surface, (rank_x - rank_surface.get_width()//2, y_pos - 10))
                
                # Score
                score_text = f"{entry['score']:,}"
                score_surface = self.score_font.render(score_text, True, COLORS['WHITE'])
                self.screen.blit(score_surface, (score_x - score_surface.get_width()//2, y_pos - 10))
                
                # Wave
                wave_text = str(entry.get('wave', '-'))
                wave_surface = self.score_font.render(wave_text, True, COLORS['WHITE'])
                self.screen.blit(wave_surface, (wave_x - wave_surface.get_width()//2, y_pos - 10))
                
                # Date
                date_text = entry['date']
                date_surface = self.small_font.render(date_text, True, COLORS['LIGHT_GRAY'])
                self.screen.blit(date_surface, (date_x - date_surface.get_width()//2, y_pos - 8))
                
                y_pos += 40
        else:
            # No scores yet
            no_scores = self.score_font.render("No scores yet!", True, COLORS['LIGHT_GRAY'])
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, 250))
            self.screen.blit(no_scores, no_scores_rect)
        
        # Buttons
        for button in self.buttons:
            button.render(self.screen)
    
    def run(self) -> GameState:
        """Run the high scores loop."""
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


# ScoreManager is imported lazily via _import_score_manager()
