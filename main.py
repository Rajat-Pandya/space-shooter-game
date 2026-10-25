"""
Nebula Defender - A polished Space Shooter game in Python/Pygame.

A complete remake of the original space shooter with professional architecture,
modern visuals, and enhanced gameplay.

Author: Enhanced from original tutorial project
Version: 2.0.0
"""

import pygame # type: ignore
import sys
import os

# Ensure we can import from the project directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    GameState, DIFFICULTY_MEDIUM
)
from utils.asset_loader import AssetLoader
from managers import SettingsManager, AudioManager

# Import scenes
from scenes import (
    MainMenu,
    GameplayScene,
    PauseMenu,
    GameOverScene,
    SettingsScene,
    ControlsScene,
    HighScoresScene
)


class Game:
    """Main game class managing all scenes and game state."""
    
    def __init__(self):
        """Initialize the game."""
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Load settings
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        
        # Setup display
        self.screen_width = self.settings.get('screen_width', SCREEN_WIDTH)
        self.screen_height = self.settings.get('screen_height', SCREEN_HEIGHT)
        self.fullscreen = self.settings.get('fullscreen', False)
        self.vsync = self.settings.get('vsync', True)
        
        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            flags,
            vsync=self.vsync
        )
        
        pygame.display.set_caption(GAME_TITLE)
        
        # Try to load icon
        try:
            icon = AssetLoader.load_image("ufo.png", scale=(32, 32))
            pygame.display.set_icon(icon)
        except:
            pass
        
        # Clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_fps = self.settings.get('show_fps', False)
        
        # Game state
        self.current_state = GameState.MENU
        self.previous_state = None
        
        # Difficulty
        self.difficulty = self.settings.get('difficulty', DIFFICULTY_MEDIUM)
        
        # Score tracking for game over
        self.last_score = 0
        self.last_wave = 0
        self.is_new_high_score = False
        
        # Gameplay scene (persisted for pause/resume)
        self.gameplay_scene: GameplayScene = None
        
        # Audio manager
        self.audio_manager = AudioManager()
        self.audio_manager.set_master_volume(self.settings.get('volume', 0.7))
        self.audio_manager.set_music_volume(self.settings.get('music_volume', 0.5))
        self.audio_manager.set_sfx_volume(self.settings.get('sfx_volume', 0.8))
        
        # Start background music
        self._start_background_music()
    
    def _start_background_music(self) -> None:
        """Start playing background music."""
        try:
            AssetLoader.load_music("background.wav")
            AssetLoader.play_music(loops=-1, fade_ms=1000)
        except Exception as e:
            print(f"Could not load background music: {e}")
    
    def run(self) -> None:
        """Main game loop."""
        print(f"Starting game loop. Initial state: {self.current_state}")
        loop_count = 0
        while self.running:
            loop_count += 1
            print(f"\n--- Loop {loop_count}: current_state = {self.current_state} ---")
            
            # Handle state transitions
            if self.current_state == GameState.QUIT:
                print("State is QUIT, cleaning up...")
                self._cleanup()
                return
            
            elif self.current_state == GameState.MENU:
                print("Entering MENU state")
                self._run_menu()
                print("Exited MENU state")
            
            elif self.current_state == GameState.PLAYING:
                print("Entering PLAYING state")
                self._run_gameplay()
                print("Exited PLAYING state")
            
            elif self.current_state == GameState.PAUSED:
                print("Entering PAUSED state")
                self._run_pause()
                print("Exited PAUSED state")
            
            elif self.current_state == GameState.GAME_OVER:
                print("Entering GAME_OVER state")
                self._run_game_over()
                print("Exited GAME_OVER state")
            
            elif self.current_state == GameState.SETTINGS:
                print("Entering SETTINGS state")
                self._run_settings()
                print("Exited SETTINGS state")
            
            elif self.current_state == GameState.CONTROLS:
                print("Entering CONTROLS state")
                self._run_controls()
                print("Exited CONTROLS state")
            
            elif self.current_state == GameState.HIGHSCORES:
                print("Entering HIGHSCORES state")
                self._run_highscores()
                print("Exited HIGHSCORES state")
            
            else:
                print(f"WARNING: Unknown state {self.current_state}, defaulting to MENU")
                self.current_state = GameState.MENU
        
        print(f"Game loop ended. running={self.running}, state={self.current_state}")
    
    def _run_menu(self) -> None:
        """Run main menu scene."""
        menu = MainMenu(self.screen, self.settings)
        result = menu.run()
        
        if result:
            self.previous_state = self.current_state
            self.current_state = result
    
    def _run_gameplay(self) -> None:
        """Run gameplay scene."""
        # Create or reset gameplay scene
        if self.gameplay_scene is None:
            self.gameplay_scene = GameplayScene(self.screen, self.settings, self.difficulty)
        
        clock = pygame.time.Clock()
        
        while self.current_state == GameState.PLAYING:
            dt = clock.tick(FPS) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if not self.gameplay_scene.handle_event(event):
                    break
            
            # Update
            result = self.gameplay_scene.update(dt)
            
            if result:
                self.previous_state = self.current_state
                self.current_state = result
                
                if result == GameState.GAME_OVER:
                    self.last_score = self.gameplay_scene.score
                    self.last_wave = self.gameplay_scene.wave
                    
                    # Check for high score
                    from managers import ScoreManager
                    score_manager = ScoreManager()
                    self.is_new_high_score = score_manager.is_high_score(self.last_score)
                    if self.is_new_high_score:
                        score_manager.add_score(self.last_score, self.last_wave)
                
                break
            
            # Render
            self.gameplay_scene.render()
            
            # Show FPS
            if self.show_fps:
                self._draw_fps(clock.get_fps())
            
            pygame.display.flip()
    
    def _run_pause(self) -> None:
        """Run pause menu."""
        # Capture current screen for background
        background = self.screen.copy()
        
        pause = PauseMenu(self.screen, self.gameplay_scene)
        result = pause.run()
        
        if result:
            if result == GameState.PLAYING:
                # Resume gameplay
                self.current_state = GameState.PLAYING
                if self.gameplay_scene:
                    self.gameplay_scene.resume()
            else:
                self.previous_state = self.current_state
                self.current_state = result
                
                if result == GameState.MENU and self.gameplay_scene:
                    # Reset gameplay when returning to menu
                    self.gameplay_scene = None
    
    def _run_game_over(self) -> None:
        """Run game over scene."""
        game_over = GameOverScene(
            self.screen,
            self.last_score,
            self.last_wave,
            self.is_new_high_score
        )
        result = game_over.run()
        
        if result:
            if result == GameState.PLAYING:
                # Reset gameplay for new game
                self.gameplay_scene = GameplayScene(self.screen, self.settings, self.difficulty)
                self.current_state = GameState.PLAYING
            else:
                self.previous_state = self.current_state
                self.current_state = result
                self.gameplay_scene = None
    
    def _run_settings(self) -> None:
        """Run settings scene."""
        settings_scene = SettingsScene(self.screen)
        result = settings_scene.run()
        
        # Reload settings
        self.settings = self.settings_manager.load_settings()
        self.audio_manager.set_master_volume(self.settings.get('volume', 0.7))
        self.audio_manager.set_music_volume(self.settings.get('music_volume', 0.5))
        self.audio_manager.set_sfx_volume(self.settings.get('sfx_volume', 0.8))
        
        # Apply display mode changes immediately
        new_fullscreen = self.settings.get('fullscreen', False)
        new_vsync = self.settings.get('vsync', True)
        if new_fullscreen != self.fullscreen or new_vsync != self.vsync:
            self.fullscreen = new_fullscreen
            self.vsync = new_vsync
            flags = pygame.DOUBLEBUF
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                flags,
                vsync=self.vsync
            )
            if self.gameplay_scene:
                self.gameplay_scene.screen = self.screen
        
        if result:
            self.previous_state = self.current_state
            self.current_state = result
    
    def _run_controls(self) -> None:
        """Run controls scene."""
        controls_scene = ControlsScene(self.screen)
        result = controls_scene.run()
        
        # Debug output
        print(f"ControlsScene returned: {result}")
        
        # Explicitly handle the result
        if result == GameState.QUIT:
            print("Setting state to QUIT")
            self.current_state = GameState.QUIT
        elif result == GameState.MENU:
            print("Setting state to MENU")
            self.previous_state = self.current_state
            self.current_state = GameState.MENU
        elif result:
            print(f"Setting state to: {result}")
            self.previous_state = self.current_state
            self.current_state = result
        else:
            # Default to menu if no result
            print("No result, defaulting to MENU")
            self.previous_state = self.current_state
            self.current_state = GameState.MENU
    
    def _run_highscores(self) -> None:
        """Run high scores scene."""
        highscores_scene = HighScoresScene(self.screen)
        result = highscores_scene.run()
        
        if result:
            self.previous_state = self.current_state
            self.current_state = result
    
    def _draw_fps(self, fps: float) -> None:
        """Draw FPS counter."""
        font = AssetLoader.get_default_font(16)
        fps_text = font.render(f"FPS: {int(fps)}", True, (0, 255, 0))
        self.screen.blit(fps_text, (10, SCREEN_HEIGHT - 30))
    
    def _cleanup(self) -> None:
        """Cleanup before exiting."""
        pygame.quit()


def main():
    """Main entry point."""
    print("=" * 50)
    print(f"  {GAME_TITLE}")
    print("  A polished Python/Pygame space shooter")
    print("=" * 50)
    print()
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)
    
    print()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
