"""
Helper utility functions.
"""

import math
import random


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end."""
    return start + (end - start) * clamp(t, 0.0, 1.0)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degrees."""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def rect_collision(rect1, rect2) -> bool:
    """Check if two rectangles collide."""
    return (rect1.x < rect2.x + rect2.width and
            rect1.x + rect1.width > rect2.x and
            rect1.y < rect2.y + rect2.height and
            rect1.y + rect1.height > rect2.y)


def circle_collision(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float) -> bool:
    """Check if two circles collide."""
    return distance_2d(x1, y1, x2, y2) < (r1 + r2)


def random_position(screen_width: int, screen_height: int, margin: int = 0) -> tuple:
    """Generate a random position within screen bounds."""
    x = random.randint(margin, screen_width - margin)
    y = random.randint(margin, screen_height - margin)
    return x, y


def random_edge_position(screen_width: int, screen_height: int, margin: int = 50) -> tuple:
    """Generate a random position at the top edge of the screen."""
    x = random.randint(margin, screen_width - margin)
    y = -margin
    return x, y


def angle_to_target(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle in degrees from point 1 to point 2."""
    dx = x2 - x1
    dy = y2 - y1
    return math.degrees(math.atan2(dy, dx))


def direction_from_angle(angle: float) -> tuple:
    """Get direction vector from angle in degrees."""
    rad = math.radians(angle)
    return (math.cos(rad), math.sin(rad))


def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_score(score: int) -> str:
    """Format score with commas for readability."""
    return f"{score:,}"


def smooth_follow(current: float, target: float, speed: float, dt: float) -> float:
    """Smoothly follow a target value."""
    diff = target - current
    return current + diff * speed * dt


def pulse_value(min_val: float, max_val: float, period: float, elapsed: float) -> float:
    """Generate a pulsing value between min and max."""
    import math
    t = (elapsed % period) / period
    return min_val + (max_val - min_val) * (0.5 + 0.5 * math.sin(t * 2 * math.pi))


def random_color() -> tuple:
    """Generate a random RGB color."""
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))


def brightness(color: tuple, factor: float) -> tuple:
    """Adjust brightness of a color."""
    r, g, b = color[:3]
    r = int(clamp(r * factor, 0, 255))
    g = int(clamp(g * factor, 0, 255))
    b = int(clamp(b * factor, 0, 255))
    return (r, g, b)


def is_point_in_rect(x: float, y: float, rect) -> bool:
    """Check if a point is inside a rectangle."""
    return (rect.x <= x <= rect.x + rect.width and
            rect.y <= y <= rect.y + rect.height)


def approach(current: float, target: float, delta: float) -> float:
    """Move current value towards target by delta amount."""
    if current < target:
        return min(current + delta, target)
    elif current > target:
        return max(current - delta, target)
    return target


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Map a value from one range to another."""
    return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min)
