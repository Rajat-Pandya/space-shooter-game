"""
Particle effects system.
"""

import pygame
import random
import math
from typing import List
from utils.constants import COLORS, MAX_PARTICLES


class Particle:
    """Single particle for visual effects."""
    
    def __init__(self, x, y, vx, vy, color, size, lifetime, gravity=0, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.fade = fade
        self.active = True
    
    def update(self, dt):
        """Update particle state."""
        if not self.active:
            return
        
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        self.lifetime -= dt * 1000
        
        if self.lifetime <= 0:
            self.active = False
    
    def render(self, screen):
        """Render the particle."""
        if not self.active:
            return
        
        alpha = 1.0
        if self.fade:
            alpha = self.lifetime / self.max_lifetime
        
        r, g, b = self.color[:3]
        color = (int(r * alpha), int(g * alpha), int(b * alpha))
        size = self.size * alpha
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(size))


class ParticleManager:
    """Manages all particle effects in the game."""
    
    def __init__(self, max_particles=MAX_PARTICLES):
        self.particles = []
        self.max_particles = max_particles
    
    def spawn_particle(self, x, y, vx, vy, color, size, lifetime, gravity=0, fade=True):
        """Spawn a single particle."""
        particle = Particle(x, y, vx, vy, color, size, lifetime, gravity, fade)
        self.particles.append(particle)
        
        if len(self.particles) > self.max_particles:
            self.particles.pop(0)
        
        return particle
    
    def spawn_explosion(self, x, y, intensity=50, colors=None):
        """Spawn explosion particles."""
        if colors is None:
            colors = [COLORS['ORANGE'], COLORS['RED'], COLORS['YELLOW']]
        
        num_particles = min(intensity // 3, 30)
        
        for _ in range(num_particles):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 8)
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            
            color = random.choice(colors)
            size = random.uniform(2, 6)
            lifetime = random.uniform(500, 1500)
            
            self.spawn_particle(x, y, vx, vy, color, size, lifetime, 0.1)
    
    def spawn_hit(self, x, y, color=None):
        """Spawn hit effect particles."""
        if color is None:
            color = COLORS['WHITE']
        
        for _ in range(8):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 4)
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            
            self.spawn_particle(x, y, vx, vy, color, random.uniform(1, 3), random.uniform(200, 500))
    
    def spawn_thrust(self, x, y, angle=90):
        """Spawn engine thrust particles."""
        for _ in range(3):
            spread = random.uniform(-20, 20)
            speed = random.uniform(2, 5)
            rad = math.radians(angle + spread)
            vx = math.cos(rad) * speed
            vy = math.sin(rad) * speed
            
            color = random.choice([(255, 100, 0), (255, 150, 0), (255, 200, 0)])
            self.spawn_particle(x, y, vx, vy, color, 3, 300, 0.2)
    
    def spawn_sparkle(self, x, y, color=None):
        """Spawn sparkle effect."""
        if color is None:
            color = COLORS['GOLD']
        
        for _ in range(5):
            angle = random.uniform(0, 360)
            speed = random.uniform(0.5, 2)
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            
            self.spawn_particle(x, y, vx, vy, color, random.uniform(1, 2), random.uniform(500, 1000))
    
    def update(self, dt):
        """Update all particles."""
        for particle in self.particles:
            particle.update(dt)
        
        self.particles = [p for p in self.particles if p.active]
    
    def render(self, screen):
        """Render all particles."""
        for particle in self.particles:
            particle.render(screen)
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear()
