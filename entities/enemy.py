"""
Enemy entities with various behaviors and AI patterns.
"""

import pygame
import math
import random
from typing import List, Optional
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, EnemyType,
    BulletType, DIFFICULTY_SETTINGS
)
from utils.asset_loader import AssetLoader
from utils.helpers import distance_2d, clamp, normalize_angle


class Enemy:
    """Base enemy class with various behavior types."""
    
    def __init__(self, x: float, y: float, enemy_type: EnemyType = EnemyType.BASIC,
                 difficulty: str = 'medium'):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.difficulty = difficulty
        
        # Stats based on type and difficulty
        settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS['medium'])
        self.health = self._get_health() * settings['enemy_health']
        self.max_health = self.health
        self.damage = settings['enemy_damage']
        self.speed = self._get_speed() * settings['enemy_speed']
        self.score_value = self._get_score()
        
        # Movement
        self.vx = random.choice([-1, 1]) * self.speed
        self.vy = self.speed * 0.3
        
        # State
        self.active = True
        self.state = 'moving'
        self.shoot_timer = 0
        self.shoot_interval = random.randint(2000, 4000)
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        self.hits_flash = 0
        
        # Visual
        self.size = self._get_size()
        self.image = self._load_image()
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # Special behavior variables
        self.move_phase = 0
        self.move_timer = 0
        self.original_y = y
        
    def _get_health(self) -> int:
        """Get base health based on enemy type."""
        healths = {
            EnemyType.BASIC: 1,
            EnemyType.FAST: 1,
            EnemyType.TANK: 3,
            EnemyType.SHOOTER: 2,
            EnemyType.DODGER: 2,
        }
        return healths.get(self.type, 1)
    
    def _get_speed(self) -> float:
        """Get base speed based on enemy type."""
        speeds = {
            EnemyType.BASIC: 2.0,
            EnemyType.FAST: 4.0,
            EnemyType.TANK: 1.0,
            EnemyType.SHOOTER: 1.5,
            EnemyType.DODGER: 3.0,
        }
        return speeds.get(self.type, 2.0)
    
    def _get_size(self) -> int:
        """Get size based on enemy type."""
        sizes = {
            EnemyType.BASIC: 40,
            EnemyType.FAST: 32,
            EnemyType.TANK: 56,
            EnemyType.SHOOTER: 44,
            EnemyType.DODGER: 36,
        }
        return sizes.get(self.type, 40)
    
    def _get_score(self) -> int:
        """Get score value based on enemy type."""
        scores = {
            EnemyType.BASIC: 10,
            EnemyType.FAST: 20,
            EnemyType.TANK: 30,
            EnemyType.SHOOTER: 25,
            EnemyType.DODGER: 15,
        }
        return scores.get(self.type, 10)
    
    def _get_color(self) -> tuple:
        """Get color based on enemy type."""
        colors = {
            EnemyType.BASIC: COLORS['RED'],
            EnemyType.FAST: COLORS['YELLOW'],
            EnemyType.TANK: COLORS['DARK_GRAY'],
            EnemyType.SHOOTER: COLORS['PURPLE'],
            EnemyType.DODGER: COLORS['CYAN'],
        }
        return colors.get(self.type, COLORS['RED'])
    
    def _load_image(self) -> pygame.Surface:
        """Load enemy sprite."""
        image = AssetLoader.load_image("001-ghost.png", scale=(self.size, self.size))
        # Color tint the image
        if self.type == EnemyType.FAST:
            image = self._tint_image(image, COLORS['YELLOW'])
        elif self.type == EnemyType.TANK:
            image = self._tint_image(image, COLORS['DARK_GRAY'])
        return image
    
    def _tint_image(self, image: pygame.Surface, color: tuple) -> pygame.Surface:
        """Apply color tint to image."""
        tinted = image.copy()
        tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*color, 50))
        tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return tinted
    
    def update(self, dt: float, player_x: float = None, player_y: float = None,
               current_time: int = 0) -> Optional[dict]:
        """Update enemy state. Returns bullet data if enemy shoots."""
        if not self.active:
            return None
        
        # Flash effect when hit
        if self.hits_flash > 0:
            self.hits_flash -= dt * 1000
        
        # Movement behavior
        self._update_movement(dt, player_x, player_y)
        
        # Update position
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Screen bounds bouncing
        if self.x < self.size // 2:
            self.x = self.size // 2
            self.vx = abs(self.vx)
        elif self.x > SCREEN_WIDTH - self.size // 2:
            self.x = SCREEN_WIDTH - self.size // 2
            self.vx = -abs(self.vx)
        
        # Check if reached bottom
        if self.y > SCREEN_HEIGHT + 50:
            self.active = False
        
        # Update rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Animation
        self.anim_timer += dt * 1000
        if self.anim_timer > 150:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 2
        
        # Shooting behavior
        if self.type == EnemyType.SHOOTER:
            self.shoot_timer += dt * 1000
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0
                self.shoot_interval = random.randint(2000, 4000)
                
                # Aim at player
                if player_x is not None and player_y is not None:
                    dx = player_x - self.x
                    dy = player_y - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                    else:
                        dx = 0
                        dy = 1
                else:
                    dx = 0
                    dy = 1
                
                return {
                    'x': self.x,
                    'y': self.y + self.size//2,
                    'dx': dx,
                    'dy': dy,
                    'type': BulletType.ENEMY_NORMAL
                }
        
        return None
    
    def _update_movement(self, dt: float, player_x: float, player_y: float) -> None:
        """Update movement based on enemy type."""
        if self.type == EnemyType.BASIC:
            # Basic movement - horizontal bounce with slow descent
            pass  # Default behavior
        
        elif self.type == EnemyType.FAST:
            # Fast enemy - faster horizontal movement
            self.vx = clamp(self.vx * 1.5, -self.speed * 2, self.speed * 2)
        
        elif self.type == EnemyType.TANK:
            # Tank - slower but steady
            self.vy = self.speed * 0.2
        
        elif self.type == EnemyType.DODGER:
            # Dodger - tries to avoid player bullets (moves away from player x)
            if player_x is not None:
                if abs(player_x - self.x) < 100:
                    if player_x > self.x:
                        self.vx = -self.speed
                    else:
                        self.vx = self.speed
        
        # Sine wave movement for variety
        self.move_timer += dt * 2
        if self.type == EnemyType.BASIC or self.type == EnemyType.SHOOTER:
            self.vx += math.sin(self.move_timer) * 0.5
            self.vx = clamp(self.vx, -self.speed, self.speed)
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage. Returns True if enemy died."""
        self.health -= damage
        self.hits_flash = 200
        
        if self.health <= 0:
            self.active = False
            return True
        return False
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        shrink = 8
        return pygame.Rect(
            self.rect.x + shrink,
            self.rect.y + shrink,
            self.rect.width - shrink * 2,
            self.rect.height - shrink * 2
        )
    
    def render(self, screen: pygame.Surface) -> None:
        """Render enemy."""
        if not self.active:
            return
        
        # Flash white when hit
        image = self.image
        if self.hits_flash > 0:
            flash_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, 150))
            image = image.copy()
            image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        screen.blit(image, self.rect)
        
        # Health bar for tank enemies
        if self.type == EnemyType.TANK and self.health < self.max_health:
            bar_width = self.size
            bar_height = 4
            health_pct = self.health / self.max_health
            
            pygame.draw.rect(screen, COLORS['DARK_GRAY'],
                           (self.rect.x, self.rect.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, COLORS['GREEN'],
                           (self.rect.x, self.rect.y - 10, int(bar_width * health_pct), bar_height))


class EnemyManager:
    """Manages enemy spawning and updates."""
    
    def __init__(self, difficulty: str = 'medium'):
        self.enemies: List[Enemy] = []
        self.difficulty = difficulty
        self.spawn_timer = 0
        self.spawn_interval = DIFFICULTY_SETTINGS[difficulty]['spawn_rate']
        self.wave_number = 1
        self.wave_timer = 0
        self.difficulty_multiplier = 1.0
        
    def update(self, dt: float, player_x: float = None, player_y: float = None,
               current_time: int = 0) -> List[dict]:
        """Update all enemies. Returns list of bullets fired."""
        bullets = []
        
        # Spawn new enemies
        self.spawn_timer += dt * 1000
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_enemy()
        
        # Update wave
        self.wave_timer += dt
        if self.wave_timer >= 30:  # New wave every 30 seconds
            self.wave_timer = 0
            self.wave_number += 1
            self.difficulty_multiplier += 0.1
            self.spawn_interval = max(500, self.spawn_interval - 100)
        
        # Update enemies
        for enemy in self.enemies:
            bullet = enemy.update(dt, player_x, player_y, current_time)
            if bullet:
                bullets.append(bullet)
        
        # Remove inactive enemies
        self.enemies = [e for e in self.enemies if e.active]
        
        return bullets
    
    def spawn_enemy(self, enemy_type: EnemyType = None, x: float = None, y: float = None) -> Enemy:
        """Spawn an enemy."""
        if enemy_type is None:
            enemy_type = self._choose_enemy_type()
        
        if x is None:
            x = random.randint(50, SCREEN_WIDTH - 50)
        if y is None:
            y = -50
        
        enemy = Enemy(x, y, enemy_type, self.difficulty)
        self.enemies.append(enemy)
        return enemy
    
    def _choose_enemy_type(self) -> EnemyType:
        """Choose enemy type based on wave and randomness."""
        weights = {
            EnemyType.BASIC: 0.5,
            EnemyType.FAST: 0.2,
            EnemyType.TANK: 0.1,
            EnemyType.SHOOTER: 0.1,
            EnemyType.DODGER: 0.1,
        }
        
        # Adjust weights based on wave
        if self.wave_number > 3:
            weights[EnemyType.SHOOTER] = 0.2
            weights[EnemyType.TANK] = 0.15
        if self.wave_number > 5:
            weights[EnemyType.FAST] = 0.3
        
        types = list(weights.keys())
        weights_list = list(weights.values())
        
        return random.choices(types, weights=weights_list)[0]
    
    def spawn_wave(self, count: int = 5) -> List[Enemy]:
        """Spawn a wave of enemies."""
        enemies = []
        for i in range(count):
            x = (SCREEN_WIDTH // (count + 1)) * (i + 1)
            y = -50 - (i * 30)
            enemy = self.spawn_enemy(x=x, y=y)
            enemies.append(enemy)
        return enemies
    
    def spawn_formation(self, formation_type: str = 'line') -> List[Enemy]:
        """Spawn enemies in a formation."""
        enemies = []
        
        if formation_type == 'line':
            for i in range(5):
                x = 100 + i * 150
                y = -50
                enemies.append(self.spawn_enemy(x=x, y=y))
        
        elif formation_type == 'v':
            for i in range(5):
                x = SCREEN_WIDTH // 2 + (i - 2) * 80
                y = -50 - abs(i - 2) * 40
                enemies.append(self.spawn_enemy(x=x, y=y))
        
        elif formation_type == 'diamond':
            positions = [
                (SCREEN_WIDTH // 2, -50),
                (SCREEN_WIDTH // 2 - 80, -100),
                (SCREEN_WIDTH // 2 + 80, -100),
                (SCREEN_WIDTH // 2 - 40, -150),
                (SCREEN_WIDTH // 2 + 40, -150),
            ]
            for x, y in positions:
                enemies.append(self.spawn_enemy(x=x, y=y))
        
        return enemies
    
    def clear(self) -> None:
        """Remove all enemies."""
        self.enemies.clear()
    
    def render(self, screen: pygame.Surface) -> None:
        """Render all enemies."""
        for enemy in self.enemies:
            enemy.render(screen)
    
    def get_active_count(self) -> int:
        """Get count of active enemies."""
        return len(self.enemies)
    
    def check_collisions_with_rect(self, rect: pygame.Rect) -> List[Enemy]:
        """Check for collisions with a rectangle."""
        collided = []
        for enemy in self.enemies:
            if enemy.active and enemy.get_rect().colliderect(rect):
                collided.append(enemy)
        return collided
    
    def reset(self) -> None:
        """Reset enemy manager."""
        self.enemies.clear()
        self.wave_number = 1
        self.wave_timer = 0
        self.difficulty_multiplier = 1.0
        self.spawn_timer = 0
        self.spawn_interval = DIFFICULTY_SETTINGS[self.difficulty]['spawn_rate']
