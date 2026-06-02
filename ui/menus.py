"""
Menu UI components.
"""

import pygame
from typing import List, Callable, Optional, Tuple
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.asset_loader import AssetLoader
from .buttons import AnimatedButton, Button


class MenuItem:
    """Menu item data structure."""
    
    def __init__(self, text: str, callback: Callable = None,
                 enabled: bool = True, icon: str = None):
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.icon = icon


class Menu:
    """Menu system with animated buttons."""
    
    def __init__(self, title: str = "", x: float = None, y: float = None,
                 width: int = 300, item_height: int = 50, spacing: int = 10):
        self.title = title
        self.x = x if x is not None else SCREEN_WIDTH // 2
        self.y = y if y is not None else SCREEN_HEIGHT // 2
        self.width = width
        self.item_height = item_height
        self.spacing = spacing
        
        self.items: List[MenuItem] = []
        self.buttons: List[AnimatedButton] = []
        self.font_title = AssetLoader.get_default_font(48)
        self.font_subtitle = AssetLoader.get_default_font(24)
        
        # Background
        self.background_alpha = 0
        self.show_background = True
        
        # Animation
        self.animation_offset = 50
        self.animation_progress = 0
    
    def add_item(self, text: str, callback: Callable = None, 
                 enabled: bool = True) -> 'Menu':
        """Add a menu item. Returns self for chaining."""
        self.items.append(MenuItem(text, callback, enabled))
        return self
    
    def build(self) -> 'Menu':
        """Build menu buttons."""
        self.buttons.clear()
        
        total_height = len(self.items) * (self.item_height + self.spacing)
        start_y = self.y - total_height // 2
        
        for i, item in enumerate(self.items):
            button = AnimatedButton(
                self.x,
                start_y + i * (self.item_height + self.spacing) + self.item_height // 2,
                self.width,
                self.item_height,
                text=item.text,
                font_size=24,
                color=COLORS['DARK_GRAY'],
                hover_color=COLORS['GRAY'],
                text_color=COLORS['WHITE'],
                border_color=COLORS['UI_HIGHLIGHT'],
                callback=item.callback
            )
            button.set_enabled(item.enabled)
            self.buttons.append(button)
        
        return self
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> Optional[str]:
        """Update menu. Returns selected item text if clicked."""
        selected = None
        
        # Animation
        self.animation_progress = min(1.0, self.animation_progress + dt * 5)
        
        # Update buttons
        for i, button in enumerate(self.buttons):
            # Staggered animation
            delay = i * 0.1
            if self.animation_progress > delay:
                button.update(dt, mouse_pos, mouse_pressed)
                
                if self.buttons[i].update(dt, mouse_pos, mouse_pressed):
                    selected = self.items[i].text
        
        return selected
    
    def render(self, screen: pygame.Surface) -> None:
        """Render menu."""
        # Background
        if self.show_background:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
        
        # Title
        if self.title:
            title_surface = self.font_title.render(self.title, True, COLORS['UI_HIGHLIGHT'])
            title_rect = title_surface.get_rect(center=(self.x, self.y - 150))
            
            # Shadow
            shadow = self.font_title.render(self.title, True, COLORS['BLACK'])
            screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
            screen.blit(title_surface, title_rect)
        
        # Render buttons
        for button in self.buttons:
            button.render(screen)
    
    def reset_animation(self) -> None:
        """Reset menu animation."""
        self.animation_progress = 0
    
    def set_enabled(self, index: int, enabled: bool) -> None:
        """Enable/disable a menu item."""
        if 0 <= index < len(self.buttons):
            self.buttons[index].set_enabled(enabled)
            self.items[index].enabled = enabled


class VerticalMenu:
    """Vertical menu with icons and descriptions."""
    
    def __init__(self, x: float, y: float, width: int = 400):
        self.x = x
        self.y = y
        self.width = width
        self.items: List[dict] = []
        self.selected_index = 0
        self.font = AssetLoader.get_default_font(24)
        self.font_small = AssetLoader.get_default_font(16)
    
    def add_item(self, text: str, description: str = "", 
                 callback: Callable = None) -> None:
        """Add menu item."""
        self.items.append({
            'text': text,
            'description': description,
            'callback': callback,
            'hovered': False
        })
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], 
               mouse_pressed: bool, keys: dict) -> Optional[int]:
        """Update menu. Returns selected index if clicked."""
        selected = None
        
        # Keyboard navigation
        if keys.get(pygame.K_UP):
            self.selected_index = max(0, self.selected_index - 1)
        if keys.get(pygame.K_DOWN):
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
        
        # Mouse navigation
        item_height = 50
        for i, item in enumerate(self.items):
            rect = pygame.Rect(self.x, self.y + i * item_height, self.width, item_height)
            item['hovered'] = rect.collidepoint(mouse_pos)
            
            if item['hovered']:
                self.selected_index = i
                if mouse_pressed:
                    selected = i
                    if item['callback']:
                        item['callback']()
        
        # Enter key
        if keys.get(pygame.K_RETURN) and not selected:
            selected = self.selected_index
            if self.items[selected]['callback']:
                self.items[selected]['callback']()
        
        return selected
    
    def render(self, screen: pygame.Surface) -> None:
        """Render vertical menu."""
        item_height = 50
        
        for i, item in enumerate(self.items):
            y = self.y + i * item_height
            rect = pygame.Rect(self.x, y, self.width, item_height - 5)
            
            # Background
            if i == self.selected_index:
                pygame.draw.rect(screen, COLORS['UI_HIGHLIGHT'], rect, border_radius=5)
                text_color = COLORS['BLACK']
            elif item['hovered']:
                pygame.draw.rect(screen, COLORS['GRAY'], rect, border_radius=5)
                text_color = COLORS['WHITE']
            else:
                pygame.draw.rect(screen, COLORS['DARK_GRAY'], rect, border_radius=5)
                text_color = COLORS['LIGHT_GRAY']
            
            # Text
            text_surface = self.font.render(item['text'], True, text_color)
            screen.blit(text_surface, (rect.x + 10, rect.centery - text_surface.get_height() // 2))
            
            # Description
            if item['description'] and (i == self.selected_index or item['hovered']):
                desc_surface = self.font_small.render(item['description'], True, 
                                                     COLORS['GRAY'] if i == self.selected_index else COLORS['LIGHT_GRAY'])
                screen.blit(desc_surface, (rect.x + 10, rect.bottom + 2))


class TabMenu:
    """Tab-based menu system."""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.tabs: List[str] = []
        self.tab_callbacks: List[Callable] = []
        self.active_tab = 0
        self.tab_height = 40
        
        self.font = AssetLoader.get_default_font(20)
    
    def add_tab(self, name: str, callback: Callable = None) -> None:
        """Add a tab."""
        self.tabs.append(name)
        self.tab_callbacks.append(callback)
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Update tabs. Returns True if tab changed."""
        changed = False
        
        if mouse_pressed:
            tab_width = self.width // len(self.tabs) if self.tabs else self.width
            
            for i, _ in enumerate(self.tabs):
                tab_rect = pygame.Rect(
                    self.x + i * tab_width,
                    self.y,
                    tab_width,
                    self.tab_height
                )
                
                if tab_rect.collidepoint(mouse_pos) and i != self.active_tab:
                    self.active_tab = i
                    changed = True
                    if self.tab_callbacks[i]:
                        self.tab_callbacks[i]()
        
        return changed
    
    def render(self, screen: pygame.Surface) -> None:
        """Render tab menu."""
        if not self.tabs:
            return
        
        tab_width = self.width // len(self.tabs)
        
        for i, tab in enumerate(self.tabs):
            x = self.x + i * tab_width
            
            # Tab background
            if i == self.active_tab:
                color = COLORS['UI_HIGHLIGHT']
                text_color = COLORS['BLACK']
            else:
                color = COLORS['DARK_GRAY']
                text_color = COLORS['WHITE']
            
            pygame.draw.rect(screen, color,
                           (x, self.y, tab_width - 2, self.tab_height), border_radius=5)
            
            # Tab text
            text = self.font.render(tab, True, text_color)
            text_rect = text.get_rect(center=(x + tab_width // 2, self.y + self.tab_height // 2))
            screen.blit(text, text_rect)
        
        # Content area border
        pygame.draw.rect(screen, COLORS['UI_HIGHLIGHT'],
                       (self.x, self.y + self.tab_height, self.width, self.height - self.tab_height), 2)
    
    def get_content_rect(self) -> pygame.Rect:
        """Get content area rectangle."""
        return pygame.Rect(
            self.x + 10,
            self.y + self.tab_height + 10,
            self.width - 20,
            self.height - self.tab_height - 20
        )
    
    def get_active_tab(self) -> int:
        """Get active tab index."""
        return self.active_tab
