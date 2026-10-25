"""
Main gameplay scene with all game logic.
"""

import pygame
import random
import math
from typing import Optional, Dict
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState,
    DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD, DIFFICULTY_ENDLESS,
    POWERUP_DURATION
)
from utils.asset_loader import AssetLoader
from entities import Player, EnemyManager, BulletManager, PowerUpManager, Boss
from entities.powerup import PowerUpType
from ui import HUD
from effects import ParticleManager, ScreenShake
from managers import AudioManager


class GameplayScene:
    """Main gameplay scene with all game logic."""
    
    def __init__(self, screen: pygame.Surface, settings: dict = None, 
                 difficulty: str = DIFFICULTY_MEDIUM):
        self.screen = screen
        self.settings = settings or {}
        self.difficulty = difficulty
        
        # Game state
        self.score = 0
        self.wave = 1
        self.running = True
        self.paused = False
        self.next_state: Optional[GameState] = None
        
        # Background
        self.background = self._load_background()
        self.bg_offset = 0
        
        # Entities
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemy_manager = EnemyManager(difficulty)
        self.bullet_manager = BulletManager()
        self.powerup_manager = PowerUpManager()
        
        # Boss
        self.boss: Optional[Boss] = None
        self.boss_spawned = False
        
        # HUD
        self.hud = HUD()
        
        # Effects
        self.particle_manager = ParticleManager()
        self.screen_shake = ScreenShake()
        
        # Audio
        self.audio_manager = AudioManager()
        
        # Input
        self.keys: Dict[int, bool] = {}
        
        # Timing
        self.last_shot_time = 0
        self.current_time = 0
    
    def _load_background(self) -> pygame.Surface:
        """Load or create background."""
        try:
            bg = AssetLoader.load_image("spc.jpg", convert_alpha=False)
            if bg.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return bg
        except:
            # Create default background
            bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            bg.fill((10, 20, 40))
            return bg
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.QUIT:
            self.next_state = GameState.QUIT
            return False
        
        if event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
            
            if event.key == pygame.K_ESCAPE:
                self.next_state = GameState.PAUSED
                return False
            
            if event.key == pygame.K_SPACE:
                if self.player.can_shoot(pygame.time.get_ticks()):
                    self._fire_player_bullets()
        
        if event.type == pygame.KEYUP:
            self.keys[event.key] = False
        
        return True
    
    def _fire_player_bullets(self) -> None:
        """Fire bullets from player."""
        self.current_time = pygame.time.get_ticks()
        bullet_data = self.player.shoot(self.current_time)
        
        for data in bullet_data:
            self.bullet_manager.spawn_bullet(
                data['x'], data['y'],
                data['type'],
                dx=0, dy=-1,
                damage=1
            )
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update gameplay state."""
        if self.paused:
            return None
        
        self.current_time = pygame.time.get_ticks()
        
        # Background scroll
        self.bg_offset += dt * 30
        if self.bg_offset > SCREEN_HEIGHT:
            self.bg_offset = 0
        
        # Update player
        self.player.update(dt, self.keys, self.current_time)
        
        # Update enemy manager
        enemy_bullets = self.enemy_manager.update(
            dt, self.player.x, self.player.y, self.current_time
        )
        
        # Spawn enemy bullets
        for bullet_data in enemy_bullets:
            self.bullet_manager.spawn_bullet(
                bullet_data['x'], bullet_data['y'],
                bullet_data['type'],
                dx=bullet_data['dx'], dy=bullet_data['dy'],
                damage=1
            )
        
        # Update boss
        if self.boss:
            boss_bullets = self.boss.update(dt, self.player.x, self.player.y, self.current_time)
            for bullet_data in boss_bullets:
                self.bullet_manager.spawn_bullet(
                    bullet_data['x'], bullet_data['y'],
                    bullet_data['type'],
                    dx=bullet_data['dx'], dy=bullet_data['dy'],
                    damage=2
                )
        
        # Check boss spawn
        self._check_boss_spawn()
        
        # Update bullets
        self.bullet_manager.update(dt)
        
        # Update power-ups
        self.powerup_manager.update(dt)
        
        # Update effects
        self.particle_manager.update(dt)
        self.screen_shake.update(dt)
        
        # Update HUD
        self.hud.update(dt, self.score, self.wave)
        
        # Check collisions
        self._check_collisions()
        
        # Check game over
        if self.player.state.name == 'DEAD':
            self.next_state = GameState.GAME_OVER
        
        return self.next_state
    
    def _check_boss_spawn(self) -> None:
        """Check if boss should spawn."""
        if not self.boss_spawned and self.wave % 5 == 0:
            self.boss = Boss(SCREEN_WIDTH // 2, 150, self.difficulty)
            self.boss_spawned = True
            self.hud.add_message("WARNING: BOSS APPROACHING!", COLORS['RED'])
            self.audio_manager.play_sound("explosion.wav", volume=0.5)
        
        # Check boss defeat
        if self.boss and not self.boss.active:
            self.boss = None
            self.boss_spawned = False
            self.score += 1000
            self.wave += 1
            self.hud.add_message(f"BOSS DEFEATED! Wave {self.wave}", COLORS['GOLD'])
    
    def _check_collisions(self) -> None:
        """Check and handle all collisions."""
        # Player bullets hitting enemies
        player_bullets = [b for b in self.bullet_manager.bullets 
                         if b.type.name.startswith('PLAYER')]
        
        for bullet in player_bullets:
            if not bullet.active:
                continue
            
            # Check regular enemies
            for enemy in self.enemy_manager.enemies:
                if enemy.active and bullet.get_rect().colliderect(enemy.get_rect()):
                    bullet.deactivate()
                    
                    if enemy.take_damage(bullet.damage):
                        # Enemy destroyed
                        self.score += enemy.score_value
                        self.particle_manager.spawn_explosion(enemy.x, enemy.y, enemy.size)
                        self.audio_manager.play_sound("explosion.wav", volume=0.3)
                        
                        # Chance to spawn power-up
                        self.powerup_manager.try_spawn_from_enemy(enemy.x, enemy.y)
                    else:
                        # Enemy hit
                        self.particle_manager.spawn_hit(bullet.x, bullet.y)
                    
                    self.screen_shake.shake(2)
                    break
            
            # Check boss
            if self.boss and self.boss.active:
                if bullet.get_rect().colliderect(self.boss.get_rect()):
                    bullet.deactivate()
                    
                    if self.boss.take_damage(bullet.damage):
                        # Boss defeated
                        self.particle_manager.spawn_explosion(self.boss.x, self.boss.y, 100)
                        self.audio_manager.play_sound("explosion.wav", volume=0.8)
                        self.screen_shake.shake(10)
                    else:
                        self.particle_manager.spawn_hit(bullet.x, bullet.y)
        
        # Enemy bullets hitting player
        enemy_bullets = [b for b in self.bullet_manager.bullets 
                        if b.type.name.startswith('ENEMY') or b.type.name == 'BOSS']
        
        for bullet in enemy_bullets:
            if bullet.active and bullet.get_rect().colliderect(self.player.get_rect()):
                bullet.deactivate()
                
                if self.player.take_damage(bullet.damage):
                    # Game over handled in update
                    self.particle_manager.spawn_explosion(self.player.x, self.player.y, 50)
                    self.audio_manager.play_sound("explosion.wav", volume=0.5)
                    self.screen_shake.shake(15)
                else:
                    self.particle_manager.spawn_hit(bullet.x, bullet.y)
                    self.screen_shake.shake(5)
        
        # Enemies colliding with player
        for enemy in self.enemy_manager.enemies:
            if enemy.active and enemy.get_rect().colliderect(self.player.get_rect()):
                if self.player.take_damage(enemy.damage):
                    self.particle_manager.spawn_explosion(self.player.x, self.player.y, 50)
                    self.audio_manager.play_sound("explosion.wav", volume=0.5)
                
                enemy.active = False
                self.particle_manager.spawn_explosion(enemy.x, enemy.y, enemy.size)
                self.screen_shake.shake(8)
        
        # Power-ups
        collected = self.powerup_manager.check_collision_with_rect(self.player.get_rect())
        if collected:
            self.player.apply_powerup(collected.type, POWERUP_DURATION)
            self.hud.add_message(f"{collected.type.name.replace('_', ' ').title()}!", 
                               COLORS['GREEN'])
            self.audio_manager.play_sound("laser.wav", volume=0.2)
        
        # Wave progression
        if self.enemy_manager.wave_timer >= 30:
            self.wave = self.enemy_manager.wave_number
    
    def render(self) -> None:
        """Render the gameplay scene."""
        # Apply screen shake
        shake_x, shake_y = self.screen_shake.get_offset()
        
        # Background
        self.screen.blit(self.background, (shake_x, shake_y + self.bg_offset - SCREEN_HEIGHT))
        self.screen.blit(self.background, (shake_x, shake_y + self.bg_offset))
        
        # Particles (behind entities)
        self.particle_manager.render(self.screen)
        
        # Power-ups
        self.powerup_manager.render(self.screen)
        
        # Bullets
        self.bullet_manager.render(self.screen)
        
        # Enemies
        self.enemy_manager.render(self.screen)
        
        # Boss
        if self.boss:
            self.boss.render(self.screen)
        
        # Player
        self.player.render(self.screen)
        
        # HUD
        self.hud.render(self.screen, self.player, self.score, self.wave,
                       self.player.get_active_powerups_list())
    
    def pause(self) -> None:
        """Pause the game."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume the game."""
        self.paused = False
        # Reset timing
        self.last_shot_time = pygame.time.get_ticks()
    
    def get_state(self) -> dict:
        """Get current game state for save/load."""
        return {
            'score': self.score,
            'wave': self.wave,
            'player_health': self.player.health,
            'player_lives': self.player.lives,
            'difficulty': self.difficulty
        }
    
    def load_state(self, state: dict) -> None:
        """Load game state."""
        self.score = state.get('score', 0)
        self.wave = state.get('wave', 1)
        self.player.health = state.get('player_health', 100)
        self.player.lives = state.get('player_lives', 3)
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        self.score = 0
        self.wave = 1
        self.player.reset()
        self.enemy_manager.reset()
        self.bullet_manager.clear()
        self.powerup_manager.clear()
        self.particle_manager.clear()
        self.boss = None
        self.boss_spawned = False
        self.next_state = None


# Import at end to avoid circular imports
from effects import ParticleManager, ScreenShake
