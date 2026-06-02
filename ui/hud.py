"""
Heads-Up Display for in-game information.
"""

import pygame
import math
from typing import Dict, List, Optional
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, 
    PLAYER_MAX_HEALTH, PLAYER_MAX_SHIELD
)
from utils.asset_loader import AssetLoader
from utils.helpers import clamp, format_score
from entities.powerup import PowerUpType


class HUD:
    """In-game HUD displaying player stats and game info."""
    
    def __init__(self):
        self.font_large = AssetLoader.get_default_font(32)
        self.font_medium = AssetLoader.get_default_font(24)
        self.font_small = AssetLoader.get_default_font(16)
        
        # Layout
        self.padding = 10
        self.bar_width = 200
        self.bar_height = 20
        
        # Messages
        self.messages: List[Dict] = []
        self.message_duration = 3000
        
        # Score animation
        self.displayed_score = 0
        self.target_score = 0
        
        # Wave indicator
        self.wave_pulse = 0
    
    def update(self, dt: float, score: int, wave: int) -> None:
        """Update HUD animations."""
        # Smooth score animation
        self.target_score = score
        self.displayed_score = int(clamp(
            self.displayed_score + (self.target_score - self.displayed_score) * dt * 10,
            self.displayed_score,
            self.target_score
        ))
        
        # Wave pulse
        self.wave_pulse += dt * 5
        
        # Update messages
        for msg in self.messages:
            msg['timer'] -= dt * 1000
        self.messages = [m for m in self.messages if m['timer'] > 0]
    
    def render(self, screen: pygame.Surface, player, score: int, wave: int,
               active_powerups: List[PowerUpType] = None) -> None:
        """Render the HUD."""
        if active_powerups is None:
            active_powerups = []
        
        # Background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Health bar
        self._render_health_bar(screen, player.health, player.max_health, 10, 10)
        
        # Shield bar
        if player.shield > 0:
            self._render_shield_bar(screen, player.shield, player.max_shield, 10, 35)
        
        # Lives
        self._render_lives(screen, player.lives, SCREEN_WIDTH - 100, 10)
        
        # Score
        self._render_score(screen, score, SCREEN_WIDTH // 2, 10)
        
        # Wave indicator
        self._render_wave_indicator(screen, wave, SCREEN_WIDTH // 2, 40)
        
        # Active power-ups
        self._render_powerups(screen, active_powerups, 10, 60)
        
        # Messages
        self._render_messages(screen)
    
    def _render_health_bar(self, screen: pygame.Surface, health: int, max_health: int,
                          x: int, y: int) -> None:
        """Render health bar."""
        # Background
        pygame.draw.rect(screen, COLORS['DARK_GRAY'],
                        (x, y, self.bar_width, self.bar_height), border_radius=4)
        
        # Fill
        health_pct = clamp(health / max_health, 0, 1)
        fill_width = int(self.bar_width * health_pct)
        
        # Color based on health
        if health_pct > 0.5:
            color = COLORS['GREEN']
        elif health_pct > 0.25:
            color = COLORS['YELLOW']
        else:
            color = COLORS['RED']
        
        pygame.draw.rect(screen, color,
                        (x, y, fill_width, self.bar_height), border_radius=4)
        
        # Border
        pygame.draw.rect(screen, COLORS['WHITE'],
                        (x, y, self.bar_width, self.bar_height), 2, border_radius=4)
        
        # Label
        label = self.font_small.render(f"HP: {health}/{max_health}", True, COLORS['WHITE'])
        screen.blit(label, (x + 5, y + 2))
    
    def _render_shield_bar(self, screen: pygame.Surface, shield: int, max_shield: int,
                          x: int, y: int) -> None:
        """Render shield bar."""
        # Background
        pygame.draw.rect(screen, COLORS['DARK_GRAY'],
                        (x, y, self.bar_width, 15), border_radius=3)
        
        # Fill
        shield_pct = clamp(shield / max_shield, 0, 1)
        fill_width = int(self.bar_width * shield_pct)
        
        pygame.draw.rect(screen, COLORS['SHIELD_BAR_FG'],
                        (x, y, fill_width, 15), border_radius=3)
        
        # Border
        pygame.draw.rect(screen, COLORS['WHITE'],
                        (x, y, self.bar_width, 15), 1, border_radius=3)
        
        # Label
        label = self.font_small.render("SHIELD", True, COLORS['WHITE'])
        screen.blit(label, (x + 5, y + 1))
    
    def _render_lives(self, screen: pygame.Surface, lives: int, x: int, y: int) -> None:
        """Render player lives."""
        # Load player icon for lives
        try:
            icon = AssetLoader.load_image("001-arcade-game.png", scale=(24, 24))
            for i in range(lives):
                screen.blit(icon, (x + i * 30, y))
        except:
            # Fallback: draw hearts
            for i in range(lives):
                self._draw_heart(screen, x + i * 25, y + 10, 10, COLORS['RED'])
    
    def _draw_heart(self, screen: pygame.Surface, x: int, y: int, size: int, color: tuple) -> None:
        """Draw a heart shape."""
        points = [
            (x, y + size // 4),
            (x - size // 2, y - size // 4),
            (x - size // 2, y - size // 2),
            (x - size // 4, y - size // 2),
            (x, y - size // 4),
            (x + size // 4, y - size // 2),
            (x + size // 2, y - size // 2),
            (x + size // 2, y - size // 4),
            (x, y + size // 4),
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _render_score(self, screen: pygame.Surface, score: int, x: int, y: int) -> None:
        """Render score."""
        score_text = format_score(score)
        text = self.font_large.render(f"SCORE: {score_text}", True, COLORS['WHITE'])
        rect = text.get_rect(center=(x, y + 15))
        
        # Shadow
        shadow = self.font_large.render(f"SCORE: {score_text}", True, COLORS['BLACK'])
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(text, rect)
    
    def _render_wave_indicator(self, screen: pygame.Surface, wave: int, x: int, y: int) -> None:
        """Render wave indicator."""
        # Pulse effect
        pulse = 1.0 + 0.1 * math.sin(self.wave_pulse)
        
        text = self.font_medium.render(f"WAVE {wave}", True, COLORS['GOLD'])
        rect = text.get_rect(center=(x, y))
        
        # Scale effect
        scaled_text = pygame.transform.scale(
            text, 
            (int(text.get_width() * pulse), int(text.get_height() * pulse))
        )
        scaled_rect = scaled_text.get_rect(center=(x, y))
        
        screen.blit(scaled_text, scaled_rect)
    
    def _render_powerups(self, screen: pygame.Surface, powerups: List[PowerUpType],
                        x: int, y: int) -> None:
        """Render active power-up icons."""
        icons = {
            PowerUpType.RAPID_FIRE: "R",
            PowerUpType.DOUBLE_BULLETS: "2x",
            PowerUpType.SHIELD: "S",
            PowerUpType.HEALTH: "+",
            PowerUpType.SPEED: ">",
            PowerUpType.LASER: "L",
        }
        
        colors = {
            PowerUpType.RAPID_FIRE: COLORS['YELLOW'],
            PowerUpType.DOUBLE_BULLETS: COLORS['ORANGE'],
            PowerUpType.SHIELD: COLORS['BLUE'],
            PowerUpType.HEALTH: COLORS['GREEN'],
            PowerUpType.SPEED: COLORS['CYAN'],
            PowerUpType.LASER: COLORS['MAGENTA'],
        }
        
        offset_x = 0
        for powerup in powerups:
            if powerup in icons:
                # Draw icon background
                size = 30
                rect = pygame.Rect(x + offset_x, y, size, size)
                pygame.draw.rect(screen, colors.get(powerup, COLORS['WHITE']), 
                               rect, border_radius=4)
                
                # Draw text
                icon_text = self.font_small.render(icons[powerup], True, COLORS['WHITE'])
                icon_rect = icon_text.get_rect(center=rect.center)
                screen.blit(icon_text, icon_rect)
                
                offset_x += size + 5
    
    def _render_messages(self, screen: pygame.Surface) -> None:
        """Render floating messages."""
        y_offset = SCREEN_HEIGHT - 100
        
        for msg in self.messages:
            alpha = int(255 * (msg['timer'] / self.message_duration))
            text_surface = self.font_medium.render(msg['text'], True, msg['color'])
            text_surface.set_alpha(alpha)
            
            rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, rect)
            
            y_offset -= 30
    
    def add_message(self, text: str, color: tuple = COLORS['WHITE']) -> None:
        """Add a floating message."""
        self.messages.append({
            'text': text,
            'color': color,
            'timer': self.message_duration
        })
    
    def render_pause_overlay(self, screen: pygame.Surface) -> None:
        """Render pause screen overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        text = self.font_large.render("PAUSED", True, COLORS['WHITE'])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Shadow
        shadow = self.font_large.render("PAUSED", True, COLORS['BLACK'])
        screen.blit(shadow, (rect.x + 3, rect.y + 3))
        screen.blit(text, rect)
        
        # Subtext
        subtext = self.font_small.render("Press ESC to resume", True, COLORS['LIGHT_GRAY'])
        sub_rect = subtext.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(subtext, sub_rect)


class FloatingText:
    """Floating text effect for damage numbers, etc."""
    
    def __init__(self, x: float, y: float, text: str, 
                 color: tuple = COLORS['WHITE'],
                 font_size: int = 20,
                 duration: float = 1000):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = AssetLoader.get_default_font(font_size)
        self.duration = duration
        self.timer = duration
        self.vy = -50  # Float upward
        
        self.surface = self.font.render(text, True, color)
        self.rect = self.surface.get_rect(center=(int(x), int(y)))
    
    def update(self, dt: float) -> bool:
        """Update floating text. Returns True if still active."""
        self.timer -= dt * 1000
        self.y += self.vy * dt
        self.rect.centery = int(self.y)
        
        # Fade out
        alpha = int(255 * (self.timer / self.duration))
        self.surface.set_alpha(alpha)
        
        return self.timer > 0
    
    def render(self, screen: pygame.Surface) -> None:
        """Render floating text."""
        if self.timer > 0:
            screen.blit(self.surface, self.rect)


class FloatingTextManager:
    """Manages floating text effects."""
    
    def __init__(self):
        self.texts: List[FloatingText] = []
    
    def spawn_text(self, x: float, y: float, text: str,
                  color: tuple = COLORS['WHITE'], font_size: int = 20) -> None:
        """Spawn floating text."""
        self.texts.append(FloatingText(x, y, text, color, font_size))
    
    def update(self, dt: float) -> None:
        """Update all floating text."""
        self.texts = [t for t in self.texts if t.update(dt)]
    
    def render(self, screen: pygame.Surface) -> None:
        """Render all floating text."""
        for text in self.texts:
            text.render(screen)
    
    def clear(self) -> None:
        """Clear all floating text."""
        self.texts.clear()
