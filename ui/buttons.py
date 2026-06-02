"""
Button UI elements with hover and click animations.
"""

import pygame
import math
from typing import Callable, Tuple, Optional
from utils.constants import COLORS
from utils.asset_loader import AssetLoader
from utils.helpers import clamp, lerp


class Button:
    """Simple button with hover and click effects."""
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 text: str = "", 
                 font_size: int = 24,
                 color: tuple = COLORS['DARK_GRAY'],
                 hover_color: tuple = COLORS['GRAY'],
                 text_color: tuple = COLORS['WHITE'],
                 border_color: tuple = COLORS['WHITE'],
                 border_width: int = 2,
                 callback: Callable = None):
        self.rect = pygame.Rect(x - width//2, y - height//2, width, height)
        self.text = text
        self.font = AssetLoader.get_default_font(font_size)
        
        # Colors
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.current_color = color
        
        # State
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self.visible = True
        
        # Animation
        self.border_width = border_width
        self.current_border_width = border_width
        self.alpha = 255
        
        # Callback
        self.callback = callback
        
        # Text rendering
        self._update_text_surface()
    
    def _update_text_surface(self) -> None:
        """Pre-render text surface."""
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Update button state. Returns True if clicked."""
        if not self.enabled or not self.visible:
            return False
        
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Hover effect
        if self.hovered:
            self.current_color = self.hover_color
            self.current_border_width = self.border_width + 2
        else:
            self.current_color = self.color
            self.current_border_width = self.border_width
        
        # Click handling
        clicked = False
        if self.hovered and mouse_pressed and not self.pressed:
            self.pressed = True
            clicked = True
            if self.callback:
                self.callback()
        elif not mouse_pressed:
            self.pressed = False
        
        return clicked
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the button."""
        if not self.visible:
            return
        
        # Draw button background
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=8)
        
        # Draw border
        if self.current_border_width > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, 
                           self.current_border_width, border_radius=8)
        
        # Draw text
        screen.blit(self.text_surface, self.text_rect)
    
    def set_text(self, text: str) -> None:
        """Update button text."""
        self.text = text
        self._update_text_surface()
    
    def set_position(self, x: float, y: float) -> None:
        """Set button position (center)."""
        self.rect.centerx = int(x)
        self.rect.centery = int(y)
        self.text_rect.center = self.rect.center
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable button."""
        self.enabled = enabled
        if not enabled:
            self.current_color = COLORS['DARK_GRAY']
    
    def get_rect(self) -> pygame.Rect:
        """Get button rectangle."""
        return self.rect


class AnimatedButton(Button):
    """Button with smooth animations."""
    
    def __init__(self, x: float, y: float, width: int, height: int,
                 text: str = "", font_size: int = 24,
                 color: tuple = COLORS['DARK_GRAY'],
                 hover_color: tuple = COLORS['GRAY'],
                 text_color: tuple = COLORS['WHITE'],
                 border_color: tuple = COLORS['WHITE'],
                 border_width: int = 2,
                 callback: Callable = None,
                 animation_speed: float = 10.0):
        super().__init__(x, y, width, height, text, font_size, color, 
                        hover_color, text_color, border_color, border_width, callback)
        
        # Animation
        self.animation_speed = animation_speed
        self.scale = 1.0
        self.target_scale = 1.0
        self.base_rect = self.rect.copy()
        
        # Glow effect
        self.glow_alpha = 0
        self.target_glow = 0
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Update animated button."""
        clicked = super().update(dt, mouse_pos, mouse_pressed)
        
        # Scale animation
        if self.hovered:
            self.target_scale = 1.1
            self.target_glow = 100
        else:
            self.target_scale = 1.0
            self.target_glow = 0
        
        # Smooth transitions
        self.scale = lerp(self.scale, self.target_scale, dt * self.animation_speed)
        self.glow_alpha = lerp(self.glow_alpha, self.target_glow, dt * self.animation_speed)
        
        # Update rect based on scale
        new_width = int(self.base_rect.width * self.scale)
        new_height = int(self.base_rect.height * self.scale)
        self.rect.width = new_width
        self.rect.height = new_height
        self.rect.center = self.base_rect.center
        
        # Update text position
        self.text_rect.center = self.rect.center
        
        return clicked
    
    def render(self, screen: pygame.Surface) -> None:
        """Render animated button."""
        if not self.visible:
            return
        
        # Draw glow
        if self.glow_alpha > 0:
            glow_surface = pygame.Surface(
                (self.rect.width + 20, self.rect.height + 20), 
                pygame.SRCALPHA
            )
            pygame.draw.rect(glow_surface, (*self.hover_color[:3], int(self.glow_alpha)),
                           (10, 10, self.rect.width, self.rect.height), 
                           border_radius=10)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10),
                       special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw main button
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=8)
        
        # Draw border
        if self.current_border_width > 0:
            pygame.draw.rect(screen, self.border_color, self.rect,
                           self.current_border_width, border_radius=8)
        
        # Draw text
        screen.blit(self.text_surface, self.text_rect)


class ToggleButton(Button):
    """Button that toggles between two states."""
    
    def __init__(self, x: float, y: float, width: int, height: int,
                 text_on: str = "ON", text_off: str = "OFF",
                 initial_state: bool = False,
                 font_size: int = 24,
                 on_color: tuple = COLORS['GREEN'],
                 off_color: tuple = COLORS['RED'],
                 text_color: tuple = COLORS['WHITE'],
                 callback: Callable = None):
        super().__init__(x, y, width, height, text_off if not initial_state else text_on,
                        font_size, off_color if not initial_state else on_color,
                        off_color if not initial_state else on_color, text_color,
                        callback=callback)
        
        self.text_on = text_on
        self.text_off = text_off
        self.on_color = on_color
        self.off_color = off_color
        self.toggled = initial_state
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Update toggle button."""
        was_pressed = self.pressed
        clicked = super().update(dt, mouse_pos, mouse_pressed)
        
        if clicked:
            self.toggled = not self.toggled
            self._update_appearance()
        
        return clicked
    
    def _update_appearance(self) -> None:
        """Update appearance based on toggle state."""
        if self.toggled:
            self.color = self.on_color
            self.hover_color = self.on_color
            self.set_text(self.text_on)
        else:
            self.color = self.off_color
            self.hover_color = self.off_color
            self.set_text(self.text_off)
    
    def get_value(self) -> bool:
        """Get current toggle value."""
        return self.toggled
    
    def set_value(self, value: bool) -> None:
        """Set toggle value."""
        self.toggled = value
        self._update_appearance()


class Slider:
    """Horizontal slider for numeric values."""
    
    def __init__(self, x: float, y: float, width: int, height: int = 20,
                 min_value: float = 0.0, max_value: float = 1.0,
                 initial_value: float = 0.5,
                 bar_color: tuple = COLORS['DARK_GRAY'],
                 fill_color: tuple = COLORS['GREEN'],
                 handle_color: tuple = COLORS['WHITE']):
        self.rect = pygame.Rect(x, y - height//2, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = clamp(initial_value, min_value, max_value)
        
        # Colors
        self.bar_color = bar_color
        self.fill_color = fill_color
        self.handle_color = handle_color
        
        # Handle
        self.handle_radius = height
        self.handle_x = self._value_to_position(self.value)
        
        # State
        self.dragging = False
        self.hovered = False
    
    def _value_to_position(self, value: float) -> float:
        """Convert value to screen position."""
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.left + ratio * self.rect.width
    
    def _position_to_value(self, pos_x: float) -> float:
        """Convert screen position to value."""
        ratio = (pos_x - self.rect.left) / self.rect.width
        ratio = clamp(ratio, 0.0, 1.0)
        return self.min_value + ratio * (self.max_value - self.min_value)
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Update slider. Returns True if value changed."""
        changed = False
        
        # Check hover on handle
        handle_rect = pygame.Rect(
            self.handle_x - self.handle_radius,
            self.rect.centery - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2
        )
        self.hovered = handle_rect.collidepoint(mouse_pos)
        
        # Handle dragging
        if mouse_pressed:
            if self.hovered or self.dragging:
                self.dragging = True
                self.value = self._position_to_value(mouse_pos[0])
                self.handle_x = self._value_to_position(self.value)
                changed = True
        else:
            self.dragging = False
        
        return changed
    
    def render(self, screen: pygame.Surface) -> None:
        """Render slider."""
        # Draw bar background
        pygame.draw.rect(screen, self.bar_color, self.rect, border_radius=self.rect.height//2)
        
        # Draw fill
        fill_width = int(self.handle_x - self.rect.left)
        fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=self.rect.height//2)
        
        # Draw handle
        pygame.draw.circle(screen, self.handle_color, 
                         (int(self.handle_x), self.rect.centery), 
                         self.handle_radius)
        
        # Draw hover glow
        if self.hovered:
            pygame.draw.circle(screen, COLORS['WHITE'],
                             (int(self.handle_x), self.rect.centery),
                             self.handle_radius, 2)
    
    def set_value(self, value: float) -> None:
        """Set slider value."""
        self.value = clamp(value, self.min_value, self.max_value)
        self.handle_x = self._value_to_position(self.value)
    
    def get_value(self) -> float:
        """Get current value."""
        return self.value


# Import needed at end
from utils.helpers import clamp, lerp
