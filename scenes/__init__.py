"""
Scenes module for game states.
"""

from .menu import MainMenu
from .gameplay import GameplayScene
from .pause import PauseMenu
from .gameover import GameOverScene
from .settings import SettingsScene
from .controls import ControlsScene
from .highscores import HighScoresScene

__all__ = [
    'MainMenu',
    'GameplayScene',
    'PauseMenu',
    'GameOverScene',
    'SettingsScene',
    'ControlsScene',
    'HighScoresScene'
]
