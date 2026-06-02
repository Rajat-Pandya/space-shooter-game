"""
Game constants and enumerations.
"""

import os
from enum import Enum, auto

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Save file paths
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
HIGHSCORE_FILE = os.path.join(DATA_DIR, 'highscores.json')
PROGRESS_FILE = os.path.join(DATA_DIR, 'progress.json')

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Nebula Defender"

# Color palette
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 50, 50),
    'GREEN': (50, 255, 50),
    'BLUE': (50, 50, 255),
    'YELLOW': (255, 255, 50),
    'CYAN': (50, 255, 255),
    'MAGENTA': (255, 50, 255),
    'ORANGE': (255, 165, 0),
    'PURPLE': (128, 0, 128),
    'GOLD': (255, 215, 0),
    'DARK_GRAY': (64, 64, 64),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (200, 200, 200),
    'TRANSPARENT': (0, 0, 0, 0),
    'BACKGROUND': (10, 10, 30),
    'MENU_BG': (15, 15, 40),
    'UI_TEXT': (220, 220, 220),
    'UI_HIGHLIGHT': (255, 200, 50),
    'HEALTH_BAR_BG': (64, 64, 64),
    'HEALTH_BAR_FG': (50, 200, 50),
    'SHIELD_BAR_FG': (50, 150, 255),
}

# Game difficulty settings
DIFFICULTY_EASY = 'easy'
DIFFICULTY_MEDIUM = 'medium'
DIFFICULTY_HARD = 'hard'
DIFFICULTY_ENDLESS = 'endless'

DIFFICULTY_SETTINGS = {
    DIFFICULTY_EASY: {
        'enemy_speed': 1.5,
        'enemy_health': 1,
        'enemy_damage': 10,
        'spawn_rate': 2000,  # milliseconds
        'score_multiplier': 1.0,
    },
    DIFFICULTY_MEDIUM: {
        'enemy_speed': 2.5,
        'enemy_health': 2,
        'enemy_damage': 20,
        'spawn_rate': 1500,
        'score_multiplier': 1.5,
    },
    DIFFICULTY_HARD: {
        'enemy_speed': 4.0,
        'enemy_health': 3,
        'enemy_damage': 30,
        'spawn_rate': 1000,
        'score_multiplier': 2.0,
    },
    DIFFICULTY_ENDLESS: {
        'enemy_speed': 2.5,
        'enemy_health': 2,
        'enemy_damage': 20,
        'spawn_rate': 1500,
        'score_multiplier': 1.5,
    }
}

# Player settings
PLAYER_START_LIVES = 3
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_SHIELD = 100
PLAYER_SPEED_EASY = 5
PLAYER_SPEED_MEDIUM = 5
PLAYER_SPEED_HARD = 5
PLAYER_INVINCIBILITY_TIME = 2000  # milliseconds

# Enemy settings
ENEMY_SPAWN_MARGIN = 50
ENEMY_TYPES_COUNT = 4

# Bullet settings
BULLET_SPEED_PLAYER = 8
BULLET_SPEED_ENEMY = 4
BULLET_COOLDOWN_DEFAULT = 250  # milliseconds
BULLET_COOLDOWN_RAPID = 100
BULLET_COOLDOWN_LASER = 500

# Power-up settings
POWERUP_DURATION = 10000  # milliseconds
POWERUP_SPAWN_CHANCE = 0.15
POWERUP_TYPES = ['rapid_fire', 'double_bullets', 'shield', 'health', 'speed', 'laser']

# Particle settings
PARTICLE_LIFETIME = 1000  # milliseconds
MAX_PARTICLES = 200

# Wave settings
WAVE_DURATION = 30  # seconds
BOSS_WAVE_INTERVAL = 5

# High score settings
MAX_HIGHSCORES = 10


class GameState(Enum):
    """Game state enumeration."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SETTINGS = auto()
    HIGHSCORES = auto()
    CONTROLS = auto()
    QUIT = auto()


class PlayerState(Enum):
    """Player state enumeration."""
    ALIVE = auto()
    HIT = auto()
    INVINCIBLE = auto()
    DEAD = auto()


class PowerUpType(Enum):
    """Power-up type enumeration."""
    RAPID_FIRE = auto()
    DOUBLE_BULLETS = auto()
    SHIELD = auto()
    HEALTH = auto()
    SPEED = auto()
    LASER = auto()


class EnemyType(Enum):
    """Enemy type enumeration."""
    BASIC = auto()      # Basic enemy - straight movement
    FAST = auto()       # Fast enemy - quick horizontal movement
    TANK = auto()       # Tank enemy - slower, more health
    SHOOTER = auto()    # Shooter enemy - fires bullets
    DODGER = auto()     # Dodger enemy - moves away from player
    BOSS = auto()       # Boss enemy - special attacks and phases


class BulletType(Enum):
    """Bullet type enumeration."""
    PLAYER_NORMAL = auto()
    PLAYER_RAPID = auto()
    PLAYER_DOUBLE = auto()
    PLAYER_LASER = auto()
    ENEMY_NORMAL = auto()
    BOSS = auto()


class ParticleType(Enum):
    """Particle effect type enumeration."""
    EXPLOSION = auto()
    THRUST = auto()
    SPARKLE = auto()
    HIT = auto()
    POWERUP = auto()
