"""Test asset loading."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.constants import IMAGES_DIR, SOUNDS_DIR, MUSIC_DIR

print("Asset paths:")
print(f"  IMAGES_DIR: {IMAGES_DIR}")
print(f"  SOUNDS_DIR: {SOUNDS_DIR}")
print(f"  MUSIC_DIR: {MUSIC_DIR}")
print()

# Test paths
test_files = [
    ("001-arcade-game.png", "player"),
    ("001-ghost.png", "enemy"),
    ("001-bullet.png", "bullet"),
    ("spc.jpg", "background"),
    ("ufo.png", "icon"),
    ("laser.wav", "sound"),
    ("explosion.wav", "sound"),
    ("background.wav", "music"),
]

print("Checking files:")
for filename, filetype in test_files:
    if filetype == "sound":
        paths = [
            os.path.join(SOUNDS_DIR, filename),
            os.path.join(os.path.dirname(SOUNDS_DIR), filename),
            os.path.join(os.path.dirname(os.path.dirname(SOUNDS_DIR)), filename),
        ]
    elif filetype == "music":
        paths = [
            os.path.join(MUSIC_DIR, filename),
            os.path.join(os.path.dirname(MUSIC_DIR), filename),
            os.path.join(os.path.dirname(os.path.dirname(MUSIC_DIR)), filename),
        ]
    else:
        paths = [
            os.path.join(IMAGES_DIR, filename),
            os.path.join(os.path.dirname(IMAGES_DIR), filename),
            os.path.join(os.path.dirname(os.path.dirname(IMAGES_DIR)), filename),
        ]
    
    found = False
    for p in paths:
        if os.path.exists(p):
            print(f"  {filename}: FOUND at {p}")
            found = True
            break
    
    if not found:
        print(f"  {filename}: NOT FOUND")
