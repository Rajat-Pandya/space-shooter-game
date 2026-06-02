"""
Power-up entities that grant temporary abilities to the player.
"""

import pygame
import math
import random
from typing import List, Optional
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, PowerUpType
)
from utils.asset_loader import AssetLoader


class PowerUp:
    """Represents a collectible power-up."""
    
    def __init__(self, x: float, y: float, powerup_type: PowerUpType = None):
        self.x = x
        self.y = y
        self.type = powerup_type if powerup_type else self._random_type()
        
        # Movement
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = 2.0  # Falls down
        
        # State
        self.active = True
        self.lifetime = 0
        self.max_lifetime = 10000  # Disappears after 10 seconds
        
        # Visual
        self.size = 32
        self.color = self._get_color()
        self.glow_color = self._get_glow_color()
        self.symbol = self._get_symbol()
        
        # Animation
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.rotation = 0
        
        # Rect
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
    
    def _random_type(self) -> PowerUpType:
        """Generate random power-up type."""
        weights = {
            PowerUpType.RAPID_FIRE: 0.15,
            PowerUpType.DOUBLE_BULLETS: 0.15,
            PowerUpType.SHIELD: 0.15,
            PowerUpType.HEALTH: 0.25,
            PowerUpType.SPEED: 0.15,
            PowerUpType.LASER: 0.15,
        }
        types = list(weights.keys())
        weights_list = list(weights.values())
        return random.choices(types, weights=weights_list)[0]
    
    def _get_color(self) -> tuple:
        """Get power-up color based on type."""
        colors = {
            PowerUpType.RAPID_FIRE: COLORS['YELLOW'],
            PowerUpType.DOUBLE_BULLETS: COLORS['ORANGE'],
            PowerUpType.SHIELD: COLORS['BLUE'],
            PowerUpType.HEALTH: COLORS['GREEN'],
            PowerUpType.SPEED: COLORS['CYAN'],
            PowerUpType.LASER: COLORS['MAGENTA'],
        }
        return colors.get(self.type, COLORS['WHITE'])
    
    def _get_glow_color(self) -> tuple:
        """Get power-up glow color."""
        r, g, b = self._get_color()
        return (r, g, b, 100)
    
    def _get_symbol(self) -> str:
        """Get display symbol for power-up."""
        symbols = {
            PowerUpType.RAPID_FIRE: "R",
            PowerUpType.DOUBLE_BULLETS: "2x",
            PowerUpType.SHIELD: "S",
            PowerUpType.HEALTH: "+",
            PowerUpType.SPEED: ">",
            PowerUpType.LASER: "L",
        }
        return symbols.get(self.type, "?")
    
    def update(self, dt: float) -> None:
        """Update power-up state."""
        if not self.active:
            return
        
        # Movement
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Screen bounds
        if self.x < self.size // 2:
            self.x = self.size // 2
            self.vx = abs(self.vx)
        elif self.x > SCREEN_WIDTH - self.size // 2:
            self.x = SCREEN_WIDTH - self.size // 2
            self.vx = -abs(self.vx)
        
        # Remove if off screen
        if self.y > SCREEN_HEIGHT + 50:
            self.active = False
        
        # Update lifetime
        self.lifetime += dt * 1000
        if self.lifetime > self.max_lifetime:
            self.active = False
        
        # Animation
        self.rotation += dt * 90
        
        # Update rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render power-up."""
        if not self.active:
            return
        
        # Calculate bobbing effect
        bob = math.sin(pygame.time.get_ticks() / 200 + self.bob_offset) * 3
        
        # Draw glow
        glow_surface = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
        glow_alpha = int(100 - (self.lifetime / self.max_lifetime) * 50)
        pygame.draw.circle(glow_surface, (*self.color[:3], glow_alpha),
                         (self.size//2 + 10, self.size//2 + 10), self.size//2 + 8)
        screen.blit(glow_surface, (self.rect.x - 10, int(self.rect.y - 10 + bob)))
        
        # Draw power-up box
        box_rect = pygame.Rect(self.rect.x, int(self.rect.y + bob), self.size, self.size)
        pygame.draw.rect(screen, self.color, box_rect, border_radius=4)
        pygame.draw.rect(screen, COLORS['WHITE'], box_rect, 2, border_radius=4)
        
        # Draw symbol
        font = AssetLoader.get_default_font(16)
        symbol_surface = font.render(self.symbol, True, COLORS['WHITE'])
        symbol_rect = symbol_surface.get_rect(center=box_rect.center)
        screen.blit(symbol_surface, symbol_rect)
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return self.rect
    
    def collect(self) -> None:
        """Mark power-up as collected."""
        self.active = False


class PowerUpManager:
    """Manages power-up spawning and updates."""
    
    def __init__(self, spawn_chance: float = 0.15):
        self.powerups: List[PowerUp] = []
        self.spawn_chance = spawn_chance
    
    def update(self, dt: float) -> None:
        """Update all power-ups."""
        for powerup in self.powerups:
            powerup.update(dt)
        
        # Remove inactive power-ups
        self.powerups = [p for p in self.powerups if p.active]
    
    def spawn_powerup(self, x: float, y: float, powerup_type: PowerUpType = None) -> Optional[PowerUp]:
        """Spawn a power-up at position."""
        if random.random() > self.spawn_chance and powerup_type is None:
            return None
        
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.append(powerup)
        return powerup
    
    def try_spawn_from_enemy(self, enemy_x: float, enemy_y: float) -> Optional[PowerUp]:
        """Attempt to spawn power-up from defeated enemy."""
        if random.random() < self.spawn_chance:
            return self.spawn_powerup(enemy_x, enemy_y)
        return None
    
    def check_collision_with_rect(self, rect: pygame.Rect) -> Optional[PowerUp]:
        """Check for collision with a rectangle. Returns collected power-up or None."""
        for powerup in self.powerups:
            if powerup.active and powerup.rect.colliderect(rect):
                powerup.collect()
                return powerup
        return None
    
    def clear(self) -> None:
        """Remove all power-ups."""
        self.powerups.clear()
    
    def render(self, screen: pygame.Surface) -> None:
        """Render all power-ups."""
        for powerup in self.powerups:
            powerup.render(screen)
    
    def get_active_count(self) -> int:
        """Get count of active power-ups."""
        return len(self.powerups)


# Import at end to avoid circular imports
from utils.constants import POWERUP_DURATION
