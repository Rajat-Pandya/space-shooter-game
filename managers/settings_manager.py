"""
Settings manager for saving and loading game settings.
"""

import json
import os
from typing import Dict, Any
from utils.constants import SETTINGS_FILE, SCREEN_WIDTH, SCREEN_HEIGHT, DIFFICULTY_MEDIUM


class SettingsManager:
    """Manages game settings with JSON persistence."""
    
    DEFAULT_SETTINGS = {
        'volume': 0.7,
        'music_volume': 0.5,
        'sfx_volume': 0.8,
        'fullscreen': False,
        'vsync': True,
        'difficulty': DIFFICULTY_MEDIUM,
        'screen_width': SCREEN_WIDTH,
        'screen_height': SCREEN_HEIGHT,
        'show_fps': False,
        'particles_enabled': True,
        'screen_shake_enabled': True,
    }
    
    def __init__(self):
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
        
        return self.settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save settings to file."""
        if settings:
            self.settings.update(settings)
        
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value) -> None:
        """Set a specific setting value."""
        self.settings[key] = value
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings."""
        return self.DEFAULT_SETTINGS.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
    
    def apply_to_pygame(self) -> None:
        """Apply settings to pygame."""
        from utils.asset_loader import AssetLoader
        
        # Update audio volumes
        AssetLoader.set_music_volume(self.settings['music_volume'])
