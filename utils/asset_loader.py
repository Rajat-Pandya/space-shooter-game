"""
Asset loading and caching system.
"""

import os
import pygame
from typing import Dict, Optional
from .constants import IMAGES_DIR, SOUNDS_DIR, MUSIC_DIR, FONTS_DIR


class AssetLoader:
    """Centralized asset loading and caching system."""
    
    _images: Dict[str, pygame.Surface] = {}
    _sounds: Dict[str, pygame.mixer.Sound] = {}
    _fonts: Dict[tuple, pygame.font.Font] = {}
    _music_loaded: bool = False
    _current_music: Optional[str] = None
    
    @classmethod
    def load_image(cls, name: str, scale: tuple = None, convert_alpha: bool = True) -> pygame.Surface:
        """Load and cache an image."""
        cache_key = f"{name}_{scale}"
        
        if cache_key not in cls._images:
            # Try multiple locations in order
            possible_paths = [
                os.path.join(IMAGES_DIR, name),  # assets/images/
                os.path.join(os.path.dirname(IMAGES_DIR), name),  # assets/
                os.path.join(os.path.dirname(os.path.dirname(IMAGES_DIR)), name),  # root/
            ]
            
            path = None
            for p in possible_paths:
                if os.path.exists(p):
                    path = p
                    break
            
            if path is None:
                # Return a placeholder surface with the name on it
                surface = pygame.Surface((64, 64))
                surface.fill((255, 0, 255))  # Magenta placeholder
                cls._images[cache_key] = surface
                return surface
            
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
            
            if scale:
                image = pygame.transform.scale(image, scale)
            
            cls._images[cache_key] = image
        
        return cls._images[cache_key]
    
    @classmethod
    def load_sound(cls, name: str, volume: float = 1.0) -> Optional[pygame.mixer.Sound]:
        """Load and cache a sound effect."""
        if name not in cls._sounds:
            # Try multiple locations in order
            possible_paths = [
                os.path.join(SOUNDS_DIR, name),  # assets/sounds/
                os.path.join(os.path.dirname(SOUNDS_DIR), name),  # assets/
                os.path.join(os.path.dirname(os.path.dirname(SOUNDS_DIR)), name),  # root/
            ]
            
            path = None
            for p in possible_paths:
                if os.path.exists(p):
                    path = p
                    break
            
            if path is None:
                return None
            
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                cls._sounds[name] = sound
            except pygame.error:
                return None
        
        return cls._sounds.get(name)
    
    @classmethod
    def play_sound(cls, name: str, volume: float = 1.0) -> bool:
        """Play a sound effect."""
        sound = cls.load_sound(name, volume)
        if sound:
            sound.set_volume(clamp(volume, 0.0, 1.0))
            sound.play()
            return True
        return False
    
    @classmethod
    def load_music(cls, name: str) -> bool:
        """Load background music (does not play)."""
        # Try multiple locations in order
        possible_paths = [
            os.path.join(MUSIC_DIR, name),  # assets/music/
            os.path.join(os.path.dirname(MUSIC_DIR), name),  # assets/
            os.path.join(os.path.dirname(os.path.dirname(MUSIC_DIR)), name),  # root/
        ]
        
        path = None
        for p in possible_paths:
            if os.path.exists(p):
                path = p
                break
        
        if path is None:
            return False
        
        try:
            pygame.mixer.music.load(path)
            cls._current_music = name
            cls._music_loaded = True
            return True
        except pygame.error:
            return False
    
    @classmethod
    def play_music(cls, loops: int = -1, start: float = 0.0, fade_ms: int = 0) -> bool:
        """Play loaded music."""
        if cls._music_loaded:
            if fade_ms > 0:
                pygame.mixer.music.play(loops, start, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops, start)
            return True
        return False
    
    @classmethod
    def stop_music(cls, fadeout: bool = False, fade_ms: int = 500) -> None:
        """Stop music playback."""
        if fadeout:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
    
    @classmethod
    def set_music_volume(cls, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(clamp(volume, 0.0, 1.0))
    
    @classmethod
    def load_font(cls, name: str, size: int) -> pygame.font.Font:
        """Load and cache a font."""
        cache_key = (name, size)
        
        if cache_key not in cls._fonts:
            if name:
                path = os.path.join(FONTS_DIR, name)
                if os.path.exists(path):
                    font = pygame.font.Font(path, size)
                else:
                    font = pygame.font.SysFont(name, size)
            else:
                font = pygame.font.Font(None, size)
            
            cls._fonts[cache_key] = font
        
        return cls._fonts[cache_key]
    
    @classmethod
    def get_default_font(cls, size: int) -> pygame.font.Font:
        """Get the default system font."""
        return cls.load_font(None, size)
    
    @classmethod
    def create_font_texture(cls, text: str, font: pygame.font.Font, 
                           color: tuple = (255, 255, 255), 
                           bg_color: tuple = None) -> pygame.Surface:
        """Create a rendered text surface."""
        if bg_color:
            return font.render(text, True, color, bg_color)
        return font.render(text, True, color)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached assets."""
        cls._images.clear()
        cls._sounds.clear()
        cls._fonts.clear()
        cls._music_loaded = False
        cls._current_music = None
    
    @classmethod
    def get_cached_count(cls) -> dict:
        """Get count of cached assets."""
        return {
            'images': len(cls._images),
            'sounds': len(cls._sounds),
            'fonts': len(cls._fonts)
        }


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Helper function to clamp a value."""
    return max(min_val, min(value, max_val))
