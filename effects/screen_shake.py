"""
Screen shake effect for impacts.
"""

import random
from typing import Tuple


class ScreenShake:
    """Manages screen shake effect."""
    
    def __init__(self, decay: float = 5.0):
        self.shake_amount = 0.0
        self.decay = decay
        self.offset_x = 0
        self.offset_y = 0
    
    def shake(self, amount: float, duration: float = None) -> None:
        """Trigger screen shake."""
        self.shake_amount = max(self.shake_amount, amount)
    
    def update(self, dt: float) -> None:
        """Update screen shake."""
        if self.shake_amount > 0:
            # Calculate random offset
            self.offset_x = random.uniform(-self.shake_amount, self.shake_amount)
            self.offset_y = random.uniform(-self.shake_amount, self.shake_amount)
            
            # Decay shake
            self.shake_amount -= self.decay * dt * 60
            if self.shake_amount < 0:
                self.shake_amount = 0
                self.offset_x = 0
                self.offset_y = 0
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def get_offset(self) -> Tuple[float, float]:
        """Get current shake offset."""
        return (self.offset_x, self.offset_y)
    
    def is_shaking(self) -> bool:
        """Check if screen is currently shaking."""
        return self.shake_amount > 0
    
    def stop(self) -> None:
        """Stop screen shake immediately."""
        self.shake_amount = 0
        self.offset_x = 0
        self.offset_y = 0
