"""
Player entity with health, shields, power-ups, and weapon systems.
"""

import pygame
import math
from typing import Optional
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS,
    PLAYER_MAX_HEALTH, PLAYER_MAX_SHIELD, PLAYER_INVINCIBILITY_TIME,
    BulletType, PlayerState, PowerUpType, BULLET_COOLDOWN_DEFAULT,
    BULLET_COOLDOWN_RAPID
)
from utils.asset_loader import AssetLoader
from utils.helpers import clamp


class Player:
    """Player ship with health, shields, and weapon systems."""
    
    def __init__(self, x: float = SCREEN_WIDTH // 2, y: float = SCREEN_HEIGHT - 100):
        # Position and movement
        self.x = x
        self.y = y
        self.speed = 5
        self.base_speed = 5
        self.vx = 0
        self.vy = 0
        
        # Health and shields
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.max_shield = PLAYER_MAX_SHIELD
        self.shield = self.max_shield
        self.lives = 3
        
        # State
        self.state = PlayerState.ALIVE
        self.invincibility_timer = 0
        self.flash_timer = 0
        self.visible = True
        
        # Weapons
        self.bullet_type = BulletType.PLAYER_NORMAL
        self.last_shot_time = 0
        self.cooldown = BULLET_COOLDOWN_DEFAULT
        self.double_bullets = False
        
        # Power-ups
        self.active_powerups: dict[PowerUpType, float] = {}
        self.powerup_timers: dict[PowerUpType, float] = {}
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        
        # Visual
        self.size = 48
        self.image = self._load_image()
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # Engine trail
        self.engine_trail = []
        
    def _load_image(self) -> pygame.Surface:
        """Load player sprite."""
        return AssetLoader.load_image("001-arcade-game.png", scale=(self.size, self.size))
    
    def update(self, dt: float, keys: dict, current_time: int) -> None:
        """Update player state."""
        # Handle invincibility
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt * 1000
            self.flash_timer += dt * 1000
            
            # Flash effect
            if self.flash_timer > 100:
                self.flash_timer = 0
                self.visible = not self.visible
            
            if self.invincibility_timer <= 0:
                self.invincibility_timer = 0
                self.state = PlayerState.ALIVE
                self.visible = True
        
        # Handle power-up timers
        self._update_powerups(dt)
        
        # Movement
        self._handle_movement(keys, dt)
        
        # Update rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Update engine trail
        self._update_engine_trail()
        
        # Animation
        self.anim_timer += dt * 1000
        if self.anim_timer > 100:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
    
    def _handle_movement(self, keys: dict, dt: float) -> None:
        """Handle player movement input."""
        self.vx = 0
        self.vy = 0
        
        # Horizontal movement
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.vx = -self.speed
        if keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.vx = self.speed
        
        # Vertical movement
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            self.vy = -self.speed
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            self.vy = self.speed
        
        # Apply movement
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Clamp to screen bounds
        margin = self.size // 2
        self.x = clamp(self.x, margin, SCREEN_WIDTH - margin)
        self.y = clamp(self.y, margin, SCREEN_HEIGHT - margin)
    
    def _update_powerups(self, dt: float) -> None:
        """Update active power-up timers."""
        for powerup_type in list(self.active_powerups.keys()):
            self.powerup_timers[powerup_type] -= dt * 1000
            
            if self.powerup_timers[powerup_type] <= 0:
                self._deactivate_powerup(powerup_type)
    
    def _deactivate_powerup(self, powerup_type: PowerUpType) -> None:
        """Deactivate a power-up."""
        if powerup_type in self.active_powerups:
            del self.active_powerups[powerup_type]
            del self.powerup_timers[powerup_type]
        
        # Reset effects
        if powerup_type == PowerUpType.RAPID_FIRE:
            self.cooldown = BULLET_COOLDOWN_DEFAULT
        elif powerup_type == PowerUpType.SPEED:
            self.speed = self.base_speed
        elif powerup_type == PowerUpType.DOUBLE_BULLETS:
            self.double_bullets = False
        elif powerup_type == PowerUpType.LASER:
            self.bullet_type = BulletType.PLAYER_NORMAL
    
    def _update_engine_trail(self) -> None:
        """Update engine particle trail."""
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.engine_trail.append({
                'x': self.x + random.randint(-5, 5),
                'y': self.y + self.size // 2,
                'life': 1.0,
                'size': random.randint(3, 6)
            })
        
        # Update existing trail particles
        for particle in self.engine_trail:
            particle['life'] -= 0.05
            particle['y'] += 2
        
        # Remove dead particles
        self.engine_trail = [p for p in self.engine_trail if p['life'] > 0]
    
    def can_shoot(self, current_time: int) -> bool:
        """Check if player can shoot."""
        return current_time - self.last_shot_time >= self.cooldown
    
    def shoot(self, current_time: int) -> list:
        """Create bullets based on current weapon configuration."""
        self.last_shot_time = current_time
        bullets_data = []
        
        if self.double_bullets:
            # Double bullet mode
            bullets_data.append({
                'x': self.x - 15,
                'y': self.y - self.size // 2,
                'type': self.bullet_type
            })
            bullets_data.append({
                'x': self.x + 15,
                'y': self.y - self.size // 2,
                'type': self.bullet_type
            })
        else:
            # Single bullet
            bullets_data.append({
                'x': self.x,
                'y': self.y - self.size // 2,
                'type': self.bullet_type
            })
        
        return bullets_data
    
    def apply_powerup(self, powerup_type: PowerUpType, duration: float = 10000) -> None:
        """Apply a power-up effect."""
        self.active_powerups[powerup_type] = duration
        self.powerup_timers[powerup_type] = duration
        
        # Apply immediate effects
        if powerup_type == PowerUpType.RAPID_FIRE:
            self.cooldown = BULLET_COOLDOWN_RAPID
        elif powerup_type == PowerUpType.SPEED:
            self.speed = self.base_speed * 1.5
        elif powerup_type == PowerUpType.DOUBLE_BULLETS:
            self.double_bullets = True
        elif powerup_type == PowerUpType.LASER:
            self.bullet_type = BulletType.PLAYER_LASER
        elif powerup_type == PowerUpType.HEALTH:
            self.health = min(self.health + 25, self.max_health)
        elif powerup_type == PowerUpType.SHIELD:
            self.shield = self.max_shield
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage to player. Returns True if player died."""
        if self.invincibility_timer > 0:
            return False
        
        # Shield absorbs damage first
        if self.shield > 0:
            shield_absorb = min(self.shield, damage)
            self.shield -= shield_absorb
            damage -= shield_absorb
        
        # Remaining damage to health
        self.health -= damage
        
        if self.health <= 0:
            self.health = 0
            self.lives -= 1
            
            if self.lives > 0:
                # Respawn with invincibility
                self.health = self.max_health
                self.shield = self.max_shield
                self.invincibility_timer = PLAYER_INVINCIBILITY_TIME
                self.state = PlayerState.INVINCIBLE
                return False
            else:
                self.state = PlayerState.DEAD
                return True
        
        # Brief hit invincibility
        self.invincibility_timer = 500
        self.state = PlayerState.HIT
        return False
    
    def heal(self, amount: int) -> None:
        """Heal the player."""
        self.health = min(self.health + amount, self.max_health)
    
    def recharge_shield(self, amount: int) -> None:
        """Recharge player shield."""
        self.shield = min(self.shield + amount, self.max_shield)
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        # Smaller hitbox than visual size
        shrink = 10
        return pygame.Rect(
            self.rect.x + shrink,
            self.rect.y + shrink,
            self.rect.width - shrink * 2,
            self.rect.height - shrink * 2
        )
    
    def render(self, screen: pygame.Surface) -> None:
        """Render player ship."""
        if not self.visible:
            return
        
        # Render engine trail
        for particle in self.engine_trail:
            color = (255, int(255 * particle['life']), 0)
            pygame.draw.circle(screen, color, 
                             (int(particle['x']), int(particle['y'])), 
                             int(particle['size'] * particle['life']))
        
        # Render ship
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback rectangle
            pygame.draw.rect(screen, COLORS['CYAN'], self.rect)
        
        # Render shield effect if active
        if self.shield > 0:
            shield_alpha = int(50 + 50 * math.sin(pygame.time.get_ticks() / 200))
            shield_surface = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 150, 255, shield_alpha), 
                             (self.size//2 + 10, self.size//2 + 10), self.size//2 + 5)
            screen.blit(shield_surface, (self.rect.x - 10, self.rect.y - 10))
    
    def get_powerup_time_remaining(self, powerup_type: PowerUpType) -> float:
        """Get remaining time for a power-up."""
        return self.powerup_timers.get(powerup_type, 0)
    
    def has_powerup(self, powerup_type: PowerUpType) -> bool:
        """Check if player has an active power-up."""
        return powerup_type in self.active_powerups
    
    def get_active_powerups_list(self) -> list:
        """Get list of active power-ups."""
        return list(self.active_powerups.keys())
    
    def reset(self) -> None:
        """Reset player to initial state."""
        self.health = self.max_health
        self.shield = self.max_shield
        self.lives = 3
        self.active_powerups.clear()
        self.powerup_timers.clear()
        self.invincibility_timer = 0
        self.state = PlayerState.ALIVE
        self.bullet_type = BulletType.PLAYER_NORMAL
        self.cooldown = BULLET_COOLDOWN_DEFAULT
        self.double_bullets = False
        self.speed = self.base_speed
        self.engine_trail.clear()


import random  # Import at end to avoid circular import issues
