"""
Bullet entity and bullet manager.
"""

import pygame
import math
from typing import List, Optional
from utils.constants import BulletType, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from utils.asset_loader import AssetLoader
from utils.helpers import distance_2d, clamp


class Bullet:
    """Represents a single bullet/projectile."""
    
    def __init__(self, x: float, y: float, bullet_type: BulletType, 
                 dx: float = 0, dy: float = -1, damage: int = 1):
        self.x = x
        self.y = y
        self.type = bullet_type
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.speed = self._get_speed()
        self.size = self._get_size()
        self.color = self._get_color()
        self.active = True
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.lifetime = 0
        self.max_lifetime = 3000  # Remove after 3 seconds
        
        # Load appropriate sprite
        self.image = self._load_image()
        
    def _get_speed(self) -> float:
        """Get bullet speed based on type."""
        speeds = {
            BulletType.PLAYER_NORMAL: 8,
            BulletType.PLAYER_RAPID: 10,
            BulletType.PLAYER_DOUBLE: 7,
            BulletType.PLAYER_LASER: 12,
            BulletType.ENEMY_NORMAL: 4,
            BulletType.BOSS: 6,
        }
        return speeds.get(self.type, 6)
    
    def _get_size(self) -> int:
        """Get bullet size based on type."""
        sizes = {
            BulletType.PLAYER_NORMAL: 8,
            BulletType.PLAYER_RAPID: 6,
            BulletType.PLAYER_DOUBLE: 10,
            BulletType.PLAYER_LASER: 16,
            BulletType.ENEMY_NORMAL: 6,
            BulletType.BOSS: 12,
        }
        return sizes.get(self.type, 8)
    
    def _get_color(self) -> tuple:
        """Get bullet color based on type."""
        colors = {
            BulletType.PLAYER_NORMAL: COLORS['CYAN'],
            BulletType.PLAYER_RAPID: COLORS['YELLOW'],
            BulletType.PLAYER_DOUBLE: COLORS['ORANGE'],
            BulletType.PLAYER_LASER: COLORS['MAGENTA'],
            BulletType.ENEMY_NORMAL: COLORS['RED'],
            BulletType.BOSS: COLORS['PURPLE'],
        }
        return colors.get(self.type, COLORS['WHITE'])
    
    def _load_image(self) -> Optional[pygame.Surface]:
        """Load bullet sprite."""
        # Try to load existing bullet image
        image = AssetLoader.load_image("001-bullet.png", 
                                      scale=(self.size * 2, self.size * 2))
        return image
    
    def update(self, dt: float) -> None:
        """Update bullet position."""
        self.x += self.dx * self.speed * dt * 60
        self.y += self.dy * self.speed * dt * 60
        self.lifetime += dt * 1000
        
        # Update rect
        self.rect.x = int(self.x - self.size//2)
        self.rect.y = int(self.y - self.size//2)
        
        # Check bounds
        if (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
            self.y < -50 or self.y > SCREEN_HEIGHT + 50 or
            self.lifetime > self.max_lifetime):
            self.active = False
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the bullet."""
        if self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, rect)
        else:
            # Fallback to colored circle
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return self.rect
    
    def deactivate(self) -> None:
        """Mark bullet as inactive."""
        self.active = False


class BulletManager:
    """Manages all bullets in the game."""
    
    def __init__(self, max_bullets: int = 100):
        self.bullets: List[Bullet] = []
        self.max_bullets = max_bullets
        
    def spawn_bullet(self, x: float, y: float, bullet_type: BulletType,
                     dx: float = 0, dy: float = -1, damage: int = 1) -> Optional[Bullet]:
        """Spawn a new bullet."""
        if len(self.bullets) >= self.max_bullets:
            # Remove oldest bullet
            self.bullets.pop(0)
        
        bullet = Bullet(x, y, bullet_type, dx, dy, damage)
        self.bullets.append(bullet)
        
        # Play sound
        if bullet_type in [BulletType.PLAYER_NORMAL, BulletType.PLAYER_RAPID, 
                          BulletType.PLAYER_DOUBLE]:
            from managers import AudioManager
            AudioManager().play_sound("laser.wav", volume=0.3)
        
        return bullet
    
    def spawn_spread(self, x: float, y: float, bullet_type: BulletType, 
                     count: int = 3, spread_angle: float = 30, damage: int = 1) -> List[Bullet]:
        """Spawn multiple bullets in a spread pattern."""
        bullets = []
        start_angle = -90 - spread_angle / 2
        angle_step = spread_angle / (count - 1) if count > 1 else 0
        
        for i in range(count):
            angle_rad = math.radians(start_angle + angle_step * i)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            bullet = self.spawn_bullet(x, y, bullet_type, dx, dy, damage)
            if bullet:
                bullets.append(bullet)
        
        return bullets
    
    def update(self, dt: float) -> None:
        """Update all bullets."""
        for bullet in self.bullets:
            bullet.update(dt)
        
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b.active]
    
    def render(self, screen: pygame.Surface) -> None:
        """Render all bullets."""
        for bullet in self.bullets:
            bullet.render(screen)
    
    def clear(self) -> None:
        """Remove all bullets."""
        self.bullets.clear()
    
    def get_active_count(self) -> int:
        """Get count of active bullets."""
        return len(self.bullets)
    
    def check_collision_with_rect(self, rect: pygame.Rect, bullet_type_filter: BulletType = None) -> List[Bullet]:
        """Check for collisions with a rectangle."""
        collided = []
        for bullet in self.bullets:
            if bullet.active and bullet.rect.colliderect(rect):
                if bullet_type_filter is None or bullet.type == bullet_type_filter:
                    collided.append(bullet)
        return collided
    
    def check_collision_with_entity(self, entity_rect: pygame.Rect, 
                                     exclude_player: bool = True) -> List[Bullet]:
        """Check for collisions, optionally filtering by owner type."""
        collided = []
        for bullet in self.bullets:
            if bullet.active and bullet.rect.colliderect(entity_rect):
                if exclude_player and bullet.type in [BulletType.PLAYER_NORMAL, 
                                                     BulletType.PLAYER_RAPID,
                                                     BulletType.PLAYER_DOUBLE,
                                                     BulletType.PLAYER_LASER]:
                    continue
                if not exclude_player and bullet.type in [BulletType.ENEMY_NORMAL, BulletType.BOSS]:
                    continue
                collided.append(bullet)
        return collided
