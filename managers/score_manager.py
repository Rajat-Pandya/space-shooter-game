"""
Score manager for high scores with JSON persistence.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from utils.constants import HIGHSCORE_FILE, MAX_HIGHSCORES


class ScoreManager:
    """Manages high scores with JSON persistence."""
    
    MAX_SCORES = 10
    
    def __init__(self):
        self.scores: List[Dict[str, Any]] = []
        self.load_scores()
    
    def load_scores(self) -> List[Dict[str, Any]]:
        """Load high scores from file."""
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    self.scores = json.load(f)
                    
                    # Validate entries
                    self.scores = [
                        s for s in self.scores 
                        if isinstance(s, dict) and 'score' in s and 'date' in s
                    ]
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading high scores: {e}")
            self.scores = []
        
        return self.scores
    
    def save_scores(self) -> bool:
        """Save high scores to file."""
        try:
            os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(self.scores[:self.MAX_SCORES], f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving high scores: {e}")
            return False
    
    def add_score(self, score: int, wave: int = 1) -> bool:
        """Add a new score. Returns True if it's a high score."""
        entry = {
            'score': score,
            'wave': wave,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M')
        }
        
        # Check if it's a high score
        is_high_score = self.is_high_score(score)
        
        # Add to list
        self.scores.append(entry)
        
        # Sort by score descending
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Trim to max
        self.scores = self.scores[:self.MAX_SCORES]
        
        # Save
        self.save_scores()
        
        return is_high_score
    
    def is_high_score(self, score: int) -> bool:
        """Check if score qualifies as a high score."""
        if len(self.scores) < self.MAX_SCORES:
            return True
        return score > self.scores[-1]['score']
    
    def get_high_scores(self) -> List[Dict[str, Any]]:
        """Get all high scores."""
        return self.scores.copy()
    
    def get_top_score(self) -> int:
        """Get the highest score."""
        if self.scores:
            return self.scores[0]['score']
        return 0
    
    def clear_high_scores(self) -> None:
        """Clear all high scores."""
        self.scores.clear()
        self.save_scores()
    
    def get_rank(self, score: int) -> int:
        """Get the rank of a score (1-indexed)."""
        for i, entry in enumerate(self.scores):
            if score >= entry['score']:
                return i + 1
        return len(self.scores) + 1 if len(self.scores) < self.MAX_SCORES else -1
