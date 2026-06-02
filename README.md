# Nebula Defender

<p align="center">
  <img src="assets/images/ufo.png" alt="Nebula Defender Logo" width="128" height="128">
</p>

<h1 align="center">Nebula Defender</h1>

<p align="center">
  A polished, modern space shooter arcade game built with Python and Pygame
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#installation">Installation</a> •
  <a href="#controls">Controls</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Overview

**Nebula Defender** is a modern take on the classic space shooter genre. Built from a basic tutorial project into a professional, portfolio-quality arcade game, it demonstrates clean architecture, engaging gameplay, and polished visuals.

### Key Features

- **Multiple Game Modes**: Easy, Medium, Hard, and Endless modes
- **Diverse Enemy Types**: Basic, Fast, Tank, Shooter, and Dodger enemies with unique behaviors
- **Epic Boss Battles**: Multi-phase boss fights with complex attack patterns
- **Power-Up System**: Rapid fire, double bullets, shield, health, speed boost, and laser weapons
- **Progressive Difficulty**: Waves get progressively harder with dynamic spawn rates
- **Particle Effects**: Explosions, hit effects, and engine trails
- **Screen Shake**: Dynamic camera shake on impacts
- **Modern UI**: Animated menus, smooth transitions, and polished HUD
- **Save System**: Persistent settings and high scores
- **Audio System**: Background music and dynamic sound effects

---

## Screenshots

<p align="center">
  <em>Gameplay screenshots coming soon!</em>
</p>

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nebula-defender.git
   cd nebula-defender
   ```

2. **Install dependencies**
   ```bash
   pip install pygame
   ```

3. **Run the game**
   ```bash
   python main.py
   ```

### Development Setup

If you want to modify or extend the game:

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Controls

### Movement
| Key | Action |
|-----|--------|
| `←` / `A` | Move left |
| `→` / `D` | Move right |
| `↑` / `W` | Move up |
| `↓` / `S` | Move down |

### Actions
| Key | Action |
|-----|--------|
| `Space` | Shoot |
| `Esc` | Pause / Back |
| `Enter` | Select / Confirm |

---

## Game Architecture

```
SpaceShooterGame/
├── main.py                 # Entry point and game loop
│
├── assets/                 # Game assets
│   ├── images/            # Sprites and graphics
│   ├── sounds/            # Sound effects
│   ├── music/             # Background music
│   └── fonts/             # Custom fonts
│
├── entities/              # Game entities
│   ├── player.py         # Player ship with health/shields
│   ├── enemy.py          # Enemy types and AI
│   ├── bullet.py         # Projectile system
│   ├── boss.py           # Boss battles
│   └── powerup.py        # Power-up system
│
├── scenes/                # Game scenes
│   ├── menu.py           # Main menu
│   ├── gameplay.py       # Core gameplay
│   ├── pause.py          # Pause menu
│   ├── gameover.py       # Game over screen
│   ├── settings.py       # Settings menu
│   ├── controls.py       # Controls display
│   └── highscores.py     # High scores table
│
├── ui/                    # User interface
│   ├── buttons.py        # Interactive buttons
│   ├── hud.py            # In-game HUD
│   └── menus.py          # Menu components
│
├── effects/               # Visual effects
│   ├── particles.py      # Particle system
│   └── screen_shake.py   # Camera shake
│
├── managers/              # Game managers
│   ├── settings_manager.py   # Settings persistence
│   ├── score_manager.py      # High scores
│   └── audio_manager.py      # Audio control
│
├── utils/                 # Utilities
│   ├── constants.py     # Game constants
│   ├── helpers.py       # Utility functions
│   └── asset_loader.py  # Asset loading
│
├── data/                  # Save data (generated)
│   ├── settings.json
│   ├── highscores.json
│   └── progress.json
│
└── .gitignore            # Git ignore rules
```

---

## Technical Highlights

### Clean OOP Architecture
- Modular design with clear separation of concerns
- Entity-Component-System inspired structure
- Scene-based state management

### Performance Optimized
- Object pooling for particles
- Efficient collision detection
- Capped at 60 FPS with vsync

### Extensible Design
- Easy to add new enemy types
- Plugin-ready power-up system
- Configurable difficulty settings

### Modern Python Practices
- Type hints throughout
- Docstrings for all classes
- Clean code principles

---

## Roadmap

### Completed
- [x] Core gameplay mechanics
- [x] Multiple enemy types
- [x] Boss battles
- [x] Power-up system
- [x] Particle effects
- [x] Screen shake
- [x] Settings persistence
- [x] High score system
- [x] Professional UI

### Planned
- [ ] Additional boss types
- [ ] More power-ups
- [ ] Weapon upgrades
- [ ] Level progression
- [ ] Achievements system
- [ ] Controller support
- [ ] Online leaderboards

---

## Technologies Used

- **Python 3.8+**: Core language
- **Pygame 2.0+**: Game framework
- **JSON**: Save data format

---

## Credits

### Original Assets
- Spaceship, Enemy, and Bullet sprites
- Sound effects (laser.wav, explosion.wav)
- Background music (background.wav)
- Background image (spc.jpg)

### Development
Enhanced from a basic tutorial project into a professional arcade game.

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Contact

Created with passion for game development. Feel free to reach out with questions or suggestions!

<p align="center">
  <strong>Enjoy the game! 🚀</strong>
</p>
