"""
Boss enemy with multiple phases and complex attack patterns.
"""

import pygame
import math
import random
from typing import List, Optional, Tuple
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, BulletType, EnemyType
)
from utils.asset_loader import AssetLoader
from utils.helpers import distance_2d, clamp, normalize_angle, angle_to_target
from .enemy import Enemy


class BossPhase:
    """Represents a boss phase with specific behaviors."""
    
    def __init__(self, name: str, health_threshold: float, duration: float = 0):
        self.name = name
        self.health_threshold = health_threshold  # Switch when health drops below this %
        self.duration = duration  # 0 = infinite, otherwise phase ends after duration
        self.timer = 0


class Boss(Enemy):
    """Boss enemy with complex AI and multiple phases."""
    
    def __init__(self, x: float = SCREEN_WIDTH // 2, y: float = 150, 
                 difficulty: str = 'medium'):
        # Initialize as enemy first
        super().__init__(x, y, EnemyType.BOSS, difficulty)
        
        # Boss specific stats
        self.max_health = 100 * DIFFICULTY_SETTINGS[difficulty]['enemy_health']
        self.health = self.max_health
        self.damage = 50
        self.speed = 1.5
        self.score_value = 1000
        self.size = 128
        
        # Movement bounds
        self.min_x = 100
        self.max_x = SCREEN_WIDTH - 100
        self.min_y = 50
        self.max_y = 300
        
        # Phase system
        self.phases = [
            BossPhase("Entry", 1.0),      # Entry phase - boss enters screen
            BossPhase("Pattern1", 0.8),    # Phase 1 - basic attacks
            BossPhase("Pattern2", 0.5),    # Phase 2 - more aggressive
            BossPhase("Pattern3", 0.25),   # Phase 3 - desperate
            BossPhase("Enraged", 0.0),     # Final phase - enraged
        ]
        self.current_phase_idx = 0
        self.current_phase = self.phases[0]
        
        # Attack patterns
        self.attack_timer = 0
        self.attack_pattern = 0
        self.pattern_timer = 0
        
        # Movement
        self.target_x = x
        self.target_y = y
        self.movement_pattern = 'hover'
        
        # Visual
        self.image = self._create_boss_sprite()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # Sub-enemies (minions)
        self.max_minions = 2
        
    def _create_boss_sprite(self) -> pygame.Surface:
        """Create boss sprite."""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Main body
        body_color = COLORS['PURPLE']
        pygame.draw.ellipse(surface, body_color, 
                          (self.size//4, self.size//4, self.size//2, self.size//2))
        
        # Wings
        wing_color = COLORS['DARK_GRAY']
        pygame.draw.polygon(surface, wing_color, [
            (0, self.size//2),
            (self.size//4, self.size//3),
            (self.size//4, self.size*2//3)
        ])
        pygame.draw.polygon(surface, wing_color, [
            (self.size, self.size//2),
            (self.size*3//4, self.size//3),
            (self.size*3//4, self.size*2//3)
        ])
        
        # Eyes
        eye_color = COLORS['RED']
        pygame.draw.circle(surface, eye_color, (self.size//3, self.size//2), 8)
        pygame.draw.circle(surface, eye_color, (self.size*2//3, self.size//2), 8)
        
        return surface
    
    def update(self, dt: float, player_x: float = None, player_y: float = None,
               current_time: int = 0) -> List[dict]:
        """Update boss state. Returns list of bullets."""
        if not self.active:
            return []
        
        # Update phase
        self._update_phase()
        
        # Update movement
        self._update_movement(dt, player_x, player_y)
        
        # Update position
        self.x = clamp(self.x + self.vx * dt * 60, self.min_x, self.max_x)
        self.y = clamp(self.y + self.vy * dt * 60, self.min_y, self.max_y)
        
        # Update rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Update timers
        self.attack_timer += dt * 1000
        self.pattern_timer += dt * 1000
        
        # Execute attack pattern
        bullets = self._execute_attack_pattern(player_x, player_y)
        
        # Flash when hit
        if self.hits_flash > 0:
            self.hits_flash -= dt * 1000
        
        return bullets
    
    def _update_phase(self) -> None:
        """Update current phase based on health."""
        health_pct = self.health / self.max_health
        
        # Check if we should advance phase
        for i, phase in enumerate(self.phases):
            if health_pct <= phase.health_threshold and i > self.current_phase_idx:
                self.current_phase_idx = i
                self.current_phase = phase
                self._on_phase_change(phase)
                break
    
    def _on_phase_change(self, phase: BossPhase) -> None:
        """Called when boss enters a new phase."""
        if phase.name == "Enraged":
            self.speed *= 1.5
            self.damage *= 2
        elif phase.name == "Pattern3":
            self.speed *= 1.3
    
    def _update_movement(self, dt: float, player_x: float, player_y: float) -> None:
        """Update boss movement based on phase."""
        phase = self.current_phase.name
        
        if phase == "Entry":
            # Move to center
            self.target_x = SCREEN_WIDTH // 2
            self.target_y = 150
            self.vx = (self.target_x - self.x) * 0.02
            self.vy = (self.target_y - self.y) * 0.02
            
        elif phase == "Pattern1":
            # Hover and follow player horizontally
            self.target_x = player_x if player_x else SCREEN_WIDTH // 2
            self.target_y = 150
            self.vx = (self.target_x - self.x) * 0.05
            self.vy = (self.target_y - self.y) * 0.05
            self.vx = clamp(self.vx, -self.speed, self.speed)
            self.vy = clamp(self.vy, -self.speed * 0.5, self.speed * 0.5)
            
        elif phase == "Pattern2":
            # Figure-8 movement
            t = pygame.time.get_ticks() / 1000
            self.target_x = SCREEN_WIDTH // 2 + math.sin(t) * 200
            self.target_y = 150 + math.sin(t * 2) * 50
            self.vx = (self.target_x - self.x) * 0.1
            self.vy = (self.target_y - self.y) * 0.1
            
        elif phase == "Pattern3":
            # Aggressive pursuit
            if player_x and player_y:
                self.target_x = player_x
                self.target_y = max(100, player_y - 200)
                self.vx = (self.target_x - self.x) * 0.08
                self.vy = (self.target_y - self.y) * 0.08
            
        elif phase == "Enraged":
            # Rapid zigzag
            t = pygame.time.get_ticks() / 200
            self.vx = math.sin(t) * self.speed * 2
            self.vy = math.cos(t * 1.5) * self.speed
    
    def _execute_attack_pattern(self, player_x: float, player_y: float) -> List[dict]:
        """Execute attack pattern based on phase."""
        bullets = []
        phase = self.current_phase.name
        
        if phase == "Entry":
            # No attacks during entry
            return bullets
        
        base_cooldown = 1500
        if phase == "Pattern2":
            base_cooldown = 1000
        elif phase == "Pattern3":
            base_cooldown = 700
        elif phase == "Enraged":
            base_cooldown = 400
        
        if self.attack_timer < base_cooldown:
            return bullets
        
        self.attack_timer = 0
        
        # Choose attack based on phase
        if phase == "Pattern1":
            bullets.extend(self._attack_single(player_x, player_y))
        
        elif phase == "Pattern2":
            if random.random() < 0.5:
                bullets.extend(self._attack_single(player_x, player_y))
            else:
                bullets.extend(self._attack_triple())
        
        elif phase == "Pattern3":
            attack = random.choice([
                lambda: self._attack_single(player_x, player_y),
                lambda: self._attack_triple(),
                lambda: self._attack_spiral(),
            ])
            bullets.extend(attack())
        
        elif phase == "Enraged":
            # Rapid fire combination
            bullets.extend(self._attack_rapid())
            if random.random() < 0.3:
                bullets.extend(self._attack_spiral())
        
        return bullets
    
    def _attack_single(self, player_x: float, player_y: float) -> List[dict]:
        """Fire a single aimed bullet."""
        dx = 0
        dy = 1
        
        if player_x and player_y:
            angle = angle_to_target(self.x, self.y, player_x, player_y)
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
        
        return [{
            'x': self.x,
            'y': self.y + self.size//3,
            'dx': dx,
            'dy': dy,
            'type': BulletType.BOSS
        }]
    
    def _attack_triple(self) -> List[dict]:
        """Fire three bullets in spread pattern."""
        bullets = []
        angles = [-30, 0, 30]
        
        for angle_offset in angles:
            angle = 90 + angle_offset
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            
            bullets.append({
                'x': self.x,
                'y': self.y + self.size//3,
                'dx': dx,
                'dy': dy,
                'type': BulletType.BOSS
            })
        
        return bullets
    
    def _attack_spiral(self) -> List[dict]:
        """Fire bullets in spiral pattern."""
        bullets = []
        num_shots = 8
        
        for i in range(num_shots):
            angle = (self.pattern_timer / 100) + (i * 360 / num_shots)
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            
            bullets.append({
                'x': self.x,
                'y': self.y,
                'dx': dx,
                'dy': dy,
                'type': BulletType.BOSS
            })
        
        return bullets
    
    def _attack_rapid(self) -> List[dict]:
        """Fire rapid bullets."""
        bullets = []
        angles = [0, -15, 15]
        
        for angle_offset in angles:
            dx = math.sin(math.radians(angle_offset))
            dy = 1
            
            bullets.append({
                'x': self.x,
                'y': self.y + self.size//3,
                'dx': dx,
                'dy': dy,
                'type': BulletType.BOSS
            })
        
        return bullets
    
    def render(self, screen: pygame.Surface) -> None:
        """Render boss."""
        if not self.active:
            return
        
        # Draw health bar
        bar_width = self.size
        bar_height = 8
        health_pct = self.health / self.max_health
        
        # Background
        pygame.draw.rect(screen, COLORS['DARK_GRAY'],
                        (self.rect.x, self.rect.y - 20, bar_width, bar_height))
        
        # Health fill - color changes based on phase
        if self.current_phase.name == "Enraged":
            color = COLORS['RED']
        elif self.current_phase.name == "Pattern3":
            color = COLORS['ORANGE']
        else:
            color = COLORS['GREEN']
        
        pygame.draw.rect(screen, color,
                        (self.rect.x, self.rect.y - 20, int(bar_width * health_pct), bar_height))
        
        # Boss name
        font = AssetLoader.get_default_font(16)
        name_text = font.render(f"BOSS - {self.current_phase.name}", True, COLORS['WHITE'])
        screen.blit(name_text, (self.rect.x, self.rect.y - 40))
        
        # Flash white when hit
        image = self.image
        if self.hits_flash > 0:
            flash_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, 150))
            image = image.copy()
            image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        screen.blit(image, self.rect)


# Import at end to avoid circular import
from utils.constants import DIFFICULTY_SETTINGS
