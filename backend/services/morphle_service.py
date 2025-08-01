"""
Morphle game service
"""
import random
import time
import uuid
from collections import deque
from typing import Dict, List, Optional, Tuple, Set
from nltk.corpus import brown
from nltk.probability import FreqDist

class MorphleService:
    """Service to handle Morphle game logic"""
    
    # Game Constants
    DIFFICULTY_SETTINGS = {
        "easy": {"length": 4, "reward": 30},
        "normal": {"length": 5, "reward": 40},
        "hard": {"length": 6, "reward": 50},
    }
    
    IDEAL_STEPS = (4, 6)
    TIME_BONUSES = [(20, 30), (60, 20), (120, 10)]
    STREAK_BONUS = 100
    HINT_COST_START = 10
    HINT_COST_INCREMENT = 10
    
    def __init__(self):
        self.active_games: Dict[str, Dict] = {}
        self.word_cache: Dict[int, Set[str]] = {}
    
    def get_common_words(self, length: int) -> Set[str]:
        """Get common words of specified length from NLTK Brown corpus"""
        if length in self.word_cache:
            return self.word_cache[length]
        
        try:
            tokens = [w.lower() for w in brown.words() if w.isalpha()]
            fdist = FreqDist(tokens)
            words = {w for w, _ in fdist.items() if len(w) == length}
            self.word_cache[length] = words
            return words
        except Exception:
            # Fallback word list if NLTK is not available
            fallback_words = {
                4: {'word', 'game', 'play', 'time', 'move', 'step', 'path', 'goal'},
                5: {'words', 'games', 'plays', 'moves', 'steps', 'paths', 'goals', 'start'},
                6: {'morphe', 'change', 'letter', 'puzzle', 'solver', 'winner', 'player'}
            }
            self.word_cache[length] = fallback_words.get(length, set())
            return self.word_cache[length]
    
    def one_letter_diff(self, w1: str, w2: str) -> bool:
        """Check if two words differ by exactly one letter"""
        return sum(a != b for a, b in zip(w1, w2)) == 1
    
    def find_shortest_path(self, start: str, end: str, word_list: Set[str]) -> Optional[List[str]]:
        """Find shortest path between two words using BFS"""
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            for i in range(len(current)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    if c != current[i]:
                        neighbor = current[:i] + c + current[i+1:]
                        if neighbor == end:
                            return path + [neighbor]
                        if neighbor in word_list and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_random_pair(self, word_list: Set[str], length: int) -> Tuple[str, str, List[str]]:
        """Get a random word pair with appropriate difficulty"""
        words = list(word_list)
        max_attempts = 100
        
        for _ in range(max_attempts):
            w1, w2 = random.sample(words, 2)
            path = self.find_shortest_path(w1, w2, word_list)
            if path and self.IDEAL_STEPS[0] <= len(path) - 1 <= self.IDEAL_STEPS[1]:
                return w1, w2, path
        
        # Fallback: just return any two words
        w1, w2 = random.sample(words, 2)
        path = self.find_shortest_path(w1, w2, word_list) or [w1, w2]
        return w1, w2, path
    
    def suggest_hint(self, current_word: str, target_word: str, word_list: Set[str]) -> Optional[str]:
        """Suggest next word in optimal path"""
        path = self.find_shortest_path(current_word, target_word, word_list)
        if path and len(path) > 1:
            return path[1]  # Return next word in path
        return None
    
    def calculate_time_bonus(self, seconds: int) -> int:
        """Calculate time bonus based on completion time"""
        for limit, bonus in self.TIME_BONUSES:
            if seconds <= limit:
                return bonus
        return 0
    
    def start_game(self, user_id: str, difficulty: str) -> Dict:
        """Start a new Morphle game"""
        if difficulty not in self.DIFFICULTY_SETTINGS:
            raise ValueError("Invalid difficulty level")
        
        config = self.DIFFICULTY_SETTINGS[difficulty]
        length = config["length"]
        reward = config["reward"]
        word_list = self.get_common_words(length)
        
        if len(word_list) < 2:
            raise ValueError("Not enough words available for this difficulty")
        
        start_word, target_word, ideal_path = self.get_random_pair(word_list, length)
        
        game_id = str(uuid.uuid4())
        game_data = {
            "game_id": game_id,
            "user_id": user_id,
            "start_word": start_word,
            "target_word": target_word,
            "current_word": start_word,
            "difficulty": difficulty,
            "word_length": length,
            "reward": reward,
            "ideal_path": ideal_path,
            "ideal_steps": len(ideal_path) - 1,
            "word_list": word_list,
            "move_count": 0,
            "hint_cost": self.HINT_COST_START,
            "hint_uses": 0,
            "mistakes": 0,
            "start_time": time.time(),
            "is_complete": False
        }
        
        self.active_games[game_id] = game_data
        
        return {
            "game_id": game_id,
            "start_word": start_word,
            "target_word": target_word,
            "difficulty": difficulty,
            "word_length": length,
            "ideal_steps": len(ideal_path) - 1,
            "reward": reward,
            "hint_cost": self.HINT_COST_START
        }
    
    def submit_move(self, game_id: str, move: str, user_id: str) -> Dict:
        """Submit a move in the game"""
        if game_id not in self.active_games:
            raise ValueError("Game not found")
        
        game = self.active_games[game_id]
        
        if game["user_id"] != user_id:
            raise ValueError("Unauthorized access to game")
        
        if game["is_complete"]:
            raise ValueError("Game is already complete")
        
        move = move.lower().strip()
        current_word = game["current_word"]
        word_length = game["word_length"]
        word_list = game["word_list"]
        
        # Validate move
        if len(move) != word_length or not move.isalpha():
            game["mistakes"] += 1
            return {
                "success": False,
                "message": f"Word must be exactly {word_length} letters",
                "current_word": current_word,
                "move_count": game["move_count"],
                "is_complete": False,
                "game_over": False
            }
        
        if not self.one_letter_diff(current_word, move):
            game["mistakes"] += 1
            return {
                "success": False,
                "message": "You can only change one letter at a time",
                "current_word": current_word,
                "move_count": game["move_count"],
                "is_complete": False,
                "game_over": False
            }
        
        if move not in word_list:
            game["mistakes"] += 1
            return {
                "success": False,
                "message": "Not a valid English word",
                "current_word": current_word,
                "move_count": game["move_count"],
                "is_complete": False,
                "game_over": False
            }
        
        # Valid move
        game["current_word"] = move
        game["move_count"] += 1
        
        # Check if game is complete
        if move == game["target_word"]:
            game["is_complete"] = True
            return {
                "success": True,
                "message": "Congratulations! You solved the puzzle!",
                "current_word": move,
                "move_count": game["move_count"],
                "is_complete": True,
                "game_over": True
            }
        
        return {
            "success": True,
            "message": "Valid move!",
            "current_word": move,
            "move_count": game["move_count"],
            "is_complete": False,
            "game_over": False
        }
    
    def get_hint(self, game_id: str, user_id: str) -> Dict:
        """Get a hint for the current game"""
        if game_id not in self.active_games:
            raise ValueError("Game not found")
        
        game = self.active_games[game_id]
        
        if game["user_id"] != user_id:
            raise ValueError("Unauthorized access to game")
        
        if game["is_complete"]:
            raise ValueError("Game is already complete")
        
        hint = self.suggest_hint(game["current_word"], game["target_word"], game["word_list"])
        cost = game["hint_cost"]
        
        if hint:
            game["hint_uses"] += 1
            game["hint_cost"] += self.HINT_COST_INCREMENT
            return {
                "hint": hint,
                "cost": cost,
                "message": f"Try '{hint.upper()}'"
            }
        else:
            return {
                "hint": None,
                "cost": 0,
                "message": "No hints available"
            }
    
    def get_game_completion_stats(self, game_id: str, user_id: str) -> Dict:
        """Get completion statistics for a finished game"""
        if game_id not in self.active_games:
            raise ValueError("Game not found")
        
        game = self.active_games[game_id]
        
        if game["user_id"] != user_id:
            raise ValueError("Unauthorized access to game")
        
        if not game["is_complete"]:
            raise ValueError("Game is not complete")
        
        duration = int(time.time() - game["start_time"])
        time_bonus = self.calculate_time_bonus(duration)
        streak_bonus = self.STREAK_BONUS if game["hint_uses"] == 0 and game["mistakes"] == 0 else 0
        total_earnings = game["reward"] + time_bonus + streak_bonus
        
        return {
            "success": True,
            "duration": duration,
            "move_count": game["move_count"],
            "ideal_steps": game["ideal_steps"],
            "base_reward": game["reward"],
            "time_bonus": time_bonus,
            "streak_bonus": streak_bonus,
            "total_earnings": total_earnings,
            "ideal_path": game["ideal_path"]
        }
    
    def get_game_state(self, game_id: str, user_id: str) -> Dict:
        """Get current game state"""
        if game_id not in self.active_games:
            raise ValueError("Game not found")
        
        game = self.active_games[game_id]
        
        if game["user_id"] != user_id:
            raise ValueError("Unauthorized access to game")
        
        return {
            "game_id": game_id,
            "start_word": game["start_word"],
            "target_word": game["target_word"],
            "current_word": game["current_word"],
            "difficulty": game["difficulty"],
            "move_count": game["move_count"],
            "hint_cost": game["hint_cost"],
            "hint_uses": game["hint_uses"],
            "mistakes": game["mistakes"],
            "start_time": game["start_time"],
            "is_complete": game["is_complete"]
        }

# Create global instance
morphle_service = MorphleService()
