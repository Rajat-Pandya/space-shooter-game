"""
Settings scene for game configuration.
"""

import pygame
from typing import Optional
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, GameState
from utils.asset_loader import AssetLoader
from ui import AnimatedButton, Slider, ToggleButton

# Lazy import
SettingsManager = None


def _import_settings_manager():
    global SettingsManager
    from managers import SettingsManager as SM
    SettingsManager = SM


class SettingsScene:
    """Settings menu for game configuration."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.running = True
        self.next_state: Optional[GameState] = None
        
        # Settings manager
        _import_settings_manager()
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        
        # Background
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        
        # Fonts
        self.title_font = AssetLoader.get_default_font(48)
        self.label_font = AssetLoader.get_default_font(24)
        
        # UI Elements
        self.sliders = {}
        self.toggles = {}
        self.buttons = []
        
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create settings UI elements."""
        center_x = SCREEN_WIDTH // 2
        start_y = 200
        spacing = 70
        
        # Volume slider
        self.sliders['volume'] = Slider(
            center_x + 100, start_y, 200, 20,
            min_value=0.0, max_value=1.0,
            initial_value=self.settings.get('volume', 0.5)
        )
        
        # Music volume slider
        self.sliders['music_volume'] = Slider(
            center_x + 100, start_y + spacing, 200, 20,
            min_value=0.0, max_value=1.0,
            initial_value=self.settings.get('music_volume', 0.5)
        )
        
        # SFX volume slider
        self.sliders['sfx_volume'] = Slider(
            center_x + 100, start_y + spacing * 2, 200, 20,
            min_value=0.0, max_value=1.0,
            initial_value=self.settings.get('sfx_volume', 0.5)
        )
        
        # Fullscreen toggle
        self.toggles['fullscreen'] = ToggleButton(
            center_x + 100, start_y + spacing * 3, 100, 40,
            text_on="ON", text_off="OFF",
            initial_state=self.settings.get('fullscreen', False),
            on_color=COLORS['GREEN'], off_color=COLORS['RED']
        )
        
        # VSync toggle
        self.toggles['vsync'] = ToggleButton(
            center_x + 100, start_y + spacing * 4, 100, 40,
            text_on="ON", text_off="OFF",
            initial_state=self.settings.get('vsync', True),
            on_color=COLORS['GREEN'], off_color=COLORS['RED']
        )
        
        # Buttons
        def save_and_exit():
            self._save_settings()
            self.next_state = GameState.MENU
        
        def cancel():
            self.next_state = GameState.MENU
        
        def reset_defaults():
            self.settings = self.settings_manager.get_default_settings()
            self._update_ui_values()
        
        self.buttons = [
            AnimatedButton(
                center_x - 150, 550, 140, 45,
                text="SAVE", font_size=22,
                color=COLORS['GREEN'], hover_color=(50, 200, 50),
                text_color=COLORS['WHITE'],
                callback=save_and_exit
            ),
            AnimatedButton(
                center_x, 550, 140, 45,
                text="DEFAULTS", font_size=22,
                color=COLORS['YELLOW'], hover_color=(200, 200, 50),
                text_color=COLORS['BLACK'],
                callback=reset_defaults
            ),
            AnimatedButton(
                center_x + 150, 550, 140, 45,
                text="CANCEL", font_size=22,
                color=COLORS['RED'], hover_color=(200, 50, 50),
                text_color=COLORS['WHITE'],
                callback=cancel
            ),
        ]
    
    def _update_ui_values(self) -> None:
        """Update UI elements with current settings."""
        self.sliders['volume'].set_value(self.settings.get('volume', 0.5))
        self.sliders['music_volume'].set_value(self.settings.get('music_volume', 0.5))
        self.sliders['sfx_volume'].set_value(self.settings.get('sfx_volume', 0.5))
        self.toggles['fullscreen'].set_value(self.settings.get('fullscreen', False))
        self.toggles['vsync'].set_value(self.settings.get('vsync', True))
    
    def _save_settings(self) -> None:
        """Save current settings."""
        self.settings['volume'] = self.sliders['volume'].get_value()
        self.settings['music_volume'] = self.sliders['music_volume'].get_value()
        self.settings['sfx_volume'] = self.sliders['sfx_volume'].get_value()
        self.settings['fullscreen'] = self.toggles['fullscreen'].get_value()
        self.settings['vsync'] = self.toggles['vsync'].get_value()
        
        self.settings_manager.save_settings(self.settings)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.QUIT:
            self._save_settings()
            self.next_state = GameState.QUIT
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save_settings()
                self.next_state = GameState.MENU
                return False
        
        return True
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update settings scene."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Update sliders
        for slider in self.sliders.values():
            slider.update(dt, mouse_pos, mouse_pressed)
        
        # Update toggles
        for toggle in self.toggles.values():
            toggle.update(dt, mouse_pos, mouse_pressed)
        
        # Update buttons
        for button in self.buttons:
            button.update(dt, mouse_pos, mouse_pressed)
        
        return self.next_state
    
    def render(self) -> None:
        """Render settings scene."""
        # Overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Title
        title = self.title_font.render("SETTINGS", True, COLORS['UI_HIGHLIGHT'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Settings labels and values
        center_x = SCREEN_WIDTH // 2
        start_y = 190
        spacing = 70
        
        labels = [
            "MASTER VOLUME",
            "MUSIC VOLUME",
            "SFX VOLUME",
            "FULLSCREEN",
            "VSYNC",
        ]
        
        slider_values = [
            int(self.sliders['volume'].get_value() * 100),
            int(self.sliders['music_volume'].get_value() * 100),
            int(self.sliders['sfx_volume'].get_value() * 100),
        ]
        
        for i, label in enumerate(labels):
            y = start_y + i * spacing
            
            # Label on the left
            label_surface = self.label_font.render(label, True, COLORS['WHITE'])
            self.screen.blit(label_surface, (center_x - 280, y - 10))
            
            # Value percentage on the right of the slider (not overlapping)
            if i < 3:  # Only for volume sliders
                value_text = f"{slider_values[i]}%"
                value_surface = self.label_font.render(value_text, True, COLORS['GOLD'])
                # Position to the right of the slider (slider ends at center_x + 300)
                self.screen.blit(value_surface, (center_x + 320, y - 10))
        
        # Render sliders
        for slider in self.sliders.values():
            slider.render(self.screen)
        
        # Render toggles
        for toggle in self.toggles.values():
            toggle.render(self.screen)
        
        # Render buttons
        for button in self.buttons:
            button.render(self.screen)
    
    def run(self) -> GameState:
        """Run the settings loop."""
        clock = pygame.time.Clock()
        
        while self.running and self.next_state is None:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if not self.handle_event(event):
                    break
            
            result = self.update(dt)
            if result:
                return result
            
            self.render()
            pygame.display.flip()
        
        return self.next_state or GameState.MENU


# SettingsManager imported lazily
