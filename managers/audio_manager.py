"""
Audio manager for centralized sound control.
"""

import pygame
from typing import Optional, Dict
from utils.constants import DIFFICULTY_SETTINGS


class AudioManager:
    """Centralized audio management system."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.master_volume = 0.7
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        self.muted = False
        
        # Sound cache
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
    
    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
    
    def _update_volumes(self) -> None:
        """Update all sound volumes."""
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume * self.master_volume)
    
    def play_music(self, filename: str, loops: int = -1, fade_ms: int = 500) -> bool:
        """Play background music."""
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self.current_music = filename
            return True
        except pygame.error as e:
            print(f"Error playing music: {e}")
            return False
    
    def stop_music(self, fadeout: bool = True) -> None:
        """Stop music."""
        if fadeout:
            pygame.mixer.music.fadeout(500)
        else:
            pygame.mixer.music.stop()
    
    def pause_music(self) -> None:
        """Pause music."""
        pygame.mixer.music.pause()
    
    def resume_music(self) -> None:
        """Resume music."""
        pygame.mixer.music.unpause()
    
    def play_sound(self, name: str, volume: float = 1.0) -> bool:
        """Play a sound effect."""
        from utils.asset_loader import AssetLoader
        
        if self.muted:
            return False
        
        final_volume = volume * self.sfx_volume * self.master_volume
        return AssetLoader.play_sound(name, final_volume)
    
    def toggle_mute(self) -> bool:
        """Toggle mute state."""
        self.muted = not self.muted
        
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        
        return self.muted
    
    def is_muted(self) -> bool:
        """Check if audio is muted."""
        return self.muted
