"""
Optimized Morphle game service with O(1) optimizations
Uses preprocessing, caching, and graph-based optimizations to minimize loading times
"""
import random
import time
import uuid
import pickle
import os
from collections import deque, defaultdict
from typing import Dict, List, Optional, Tuple, Set
from nltk.corpus import brown
from nltk.probability import FreqDist

class OptimizedMorphleService:
    """High-performance Morphle service with O(1) optimizations"""
    
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
    
    # Cache file paths
    CACHE_DIR = "/app/data/morphle_cache"
    WORD_CACHE_FILE = "/app/data/morphle_cache/word_cache.pkl"
    GRAPH_CACHE_FILE = "/app/data/morphle_cache/graph_cache.pkl"
    PAIRS_CACHE_FILE = "/app/data/morphle_cache/pairs_cache.pkl"
    
    def __init__(self):
        self.active_games: Dict[str, Dict] = {}
        
        # O(1) lookup caches
        self.word_lists: Dict[int, Set[str]] = {}  # length -> word set
        self.adjacency_graphs: Dict[int, Dict[str, Set[str]]] = {}  # length -> adjacency graph
        self.precomputed_pairs: Dict[int, List[Tuple[str, str, List[str]]]] = {}  # length -> valid pairs
        self.distance_cache: Dict[Tuple[str, str], int] = {}  # (word1, word2) -> distance
        self.path_cache: Dict[Tuple[str, str], List[str]] = {}  # (word1, word2) -> path
        
        # Initialize caches
        self._ensure_cache_directory()
        self._load_or_build_caches()
    
    def _ensure_cache_directory(self):
        """Ensure cache directory exists"""
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def _load_or_build_caches(self):
        """Load caches from disk or build them if they don't exist"""
        try:
            # Try to load existing caches
            if (os.path.exists(self.WORD_CACHE_FILE) and 
                os.path.exists(self.GRAPH_CACHE_FILE) and 
                os.path.exists(self.PAIRS_CACHE_FILE)):
                
                print("Loading Morphle caches from disk...")
                self._load_caches_from_disk()
                print("Morphle caches loaded successfully!")
            else:
                print("Building Morphle performance caches...")
                self._build_all_caches()
                self._save_caches_to_disk()
                print("Morphle caches built and saved!")
        except Exception as e:
            print(f"Cache loading failed, rebuilding: {e}")
            self._build_all_caches()
            self._save_caches_to_disk()
    
    def _load_caches_from_disk(self):
        """Load precomputed caches from disk - O(1) initialization"""
        with open(self.WORD_CACHE_FILE, 'rb') as f:
            self.word_lists = pickle.load(f)
        
        with open(self.GRAPH_CACHE_FILE, 'rb') as f:
            self.adjacency_graphs = pickle.load(f)
        
        with open(self.PAIRS_CACHE_FILE, 'rb') as f:
            self.precomputed_pairs = pickle.load(f)
    
    def _save_caches_to_disk(self):
        """Save caches to disk for future O(1) loading"""
        with open(self.WORD_CACHE_FILE, 'wb') as f:
            pickle.dump(self.word_lists, f)
        
        with open(self.GRAPH_CACHE_FILE, 'wb') as f:
            pickle.dump(self.adjacency_graphs, f)
        
        with open(self.PAIRS_CACHE_FILE, 'wb') as f:
            pickle.dump(self.precomputed_pairs, f)
    
    def _build_all_caches(self):
        """Build all performance caches"""
        # Build word lists for each length
        for length in [4, 5, 6]:
            print(f"Building cache for {length}-letter words...")
            self.word_lists[length] = self._get_common_words(length)
            
            # Build adjacency graph for O(1) neighbor lookup
            self.adjacency_graphs[length] = self._build_adjacency_graph(self.word_lists[length])
            
            # Precompute valid game pairs
            self.precomputed_pairs[length] = self._precompute_valid_pairs(
                self.word_lists[length], length
            )
    
    def _get_common_words(self, length: int) -> Set[str]:
        """Get common words of specified length from NLTK Brown corpus"""
        try:
            tokens = [w.lower() for w in brown.words() if w.isalpha()]
            fdist = FreqDist(tokens)
            # Take top 1000 most common words of each length for better performance
            words = {w for w, freq in fdist.most_common() if len(w) == length and freq > 2}
            return words
        except Exception:
            # Fallback word lists for each length
            fallback_words = {
                4: {'word', 'game', 'play', 'time', 'move', 'step', 'path', 'goal', 'work', 'part',
                     'life', 'home', 'hand', 'head', 'year', 'back', 'turn', 'make', 'take', 'come',
                     'good', 'best', 'same', 'long', 'last', 'next', 'help', 'look', 'find', 'give'},
                5: {'words', 'games', 'plays', 'moves', 'steps', 'paths', 'goals', 'start', 'world',
                     'water', 'place', 'right', 'think', 'great', 'house', 'where', 'every', 'three',
                     'small', 'large', 'might', 'still', 'never', 'would', 'first', 'sound', 'white',
                     'black', 'night', 'light', 'about', 'after', 'again', 'below', 'state', 'story'},
                6: {'morphe', 'change', 'letter', 'puzzle', 'solver', 'winner', 'player', 'mother',
                     'father', 'friend', 'family', 'people', 'animal', 'garden', 'forest', 'stream',
                     'bridge', 'castle', 'golden', 'silver', 'purple', 'orange', 'yellow', 'bright',
                     'strong', 'simple', 'before', 'during', 'always', 'almost', 'around', 'school',
                     'number', 'answer', 'listen', 'follow', 'finger', 'breath', 'height', 'length'}
            }
            return fallback_words.get(length, set())
    
    def _build_adjacency_graph(self, word_list: Set[str]) -> Dict[str, Set[str]]:
        """Build adjacency graph for O(1) neighbor lookup"""
        graph = defaultdict(set)
        word_list_array = list(word_list)
        
        for i, word1 in enumerate(word_list_array):
            for j in range(i + 1, len(word_list_array)):
                word2 = word_list_array[j]
                if self._one_letter_diff(word1, word2):
                    graph[word1].add(word2)
                    graph[word2].add(word1)
        
        return dict(graph)
    
    def _precompute_valid_pairs(self, word_list: Set[str], length: int) -> List[Tuple[str, str, List[str]]]:
        """Precompute valid game pairs with their optimal paths"""
        valid_pairs = []
        words = list(word_list)
        graph = self.adjacency_graphs[length]
        
        # Limit to avoid excessive computation - sample random pairs
        max_pairs = min(500, len(words) * 2)  # Reasonable number of precomputed pairs
        attempts = 0
        
        while len(valid_pairs) < max_pairs and attempts < max_pairs * 3:
            w1, w2 = random.sample(words, 2)
            attempts += 1
            
            # Skip if already computed
            if any(pair[0] == w1 and pair[1] == w2 for pair in valid_pairs):
                continue
            
            path = self._find_shortest_path_optimized(w1, w2, graph)
            if path and self.IDEAL_STEPS[0] <= len(path) - 1 <= self.IDEAL_STEPS[1]:
                valid_pairs.append((w1, w2, path))
                # Also cache the path for O(1) lookup
                self.path_cache[(w1, w2)] = path
                self.path_cache[(w2, w1)] = path[::-1]
        
        return valid_pairs
    
    def _one_letter_diff(self, w1: str, w2: str) -> bool:
        """Check if two words differ by exactly one letter - O(n) where n is word length"""
        if len(w1) != len(w2):
            return False
        return sum(a != b for a, b in zip(w1, w2)) == 1
    
    def _find_shortest_path_optimized(self, start: str, end: str, graph: Dict[str, Set[str]]) -> Optional[List[str]]:
        """Find shortest path using precomputed adjacency graph - O(V + E) but with smaller graph"""
        if start == end:
            return [start]
        
        # Check cache first - O(1)
        cache_key = (start, end)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            # Use precomputed neighbors - O(1) lookup
            for neighbor in graph.get(current, set()):
                if neighbor == end:
                    result = path + [neighbor]
                    # Cache the result - O(1)
                    self.path_cache[cache_key] = result
                    return result
                    
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_random_pair_optimized(self, length: int) -> Tuple[str, str, List[str]]:
        """Get random word pair - O(1) using precomputed pairs"""
        if length not in self.precomputed_pairs or not self.precomputed_pairs[length]:
            raise ValueError(f"No precomputed pairs available for length {length}")
        
        return random.choice(self.precomputed_pairs[length])
    
    def suggest_hint_optimized(self, current_word: str, target_word: str, length: int) -> Optional[str]:
        """Get hint using cached paths - O(1) if path is cached"""
        cache_key = (current_word, target_word)
        
        # Check cache first
        if cache_key in self.path_cache:
            path = self.path_cache[cache_key]
            if len(path) > 1:
                return path[1]
        
        # If not cached, compute and cache
        graph = self.adjacency_graphs.get(length, {})
        path = self._find_shortest_path_optimized(current_word, target_word, graph)
        if path and len(path) > 1:
            return path[1]
        
        return None
    
    def validate_word_optimized(self, word: str, length: int) -> bool:
        """Validate word - O(1) using precomputed set"""
        return word in self.word_lists.get(length, set())
    
    def get_neighbors_optimized(self, word: str, length: int) -> Set[str]:
        """Get valid neighboring words - O(1) using adjacency graph"""
        return self.adjacency_graphs.get(length, {}).get(word, set())
    
    def calculate_time_bonus(self, seconds: int) -> int:
        """Calculate time bonus - O(1)"""
        for limit, bonus in self.TIME_BONUSES:
            if seconds <= limit:
                return bonus
        return 0
    
    def start_game(self, user_id: str, difficulty: str) -> Dict:
        """Start a new Morphle game - O(1) using precomputed data"""
        if difficulty not in self.DIFFICULTY_SETTINGS:
            raise ValueError("Invalid difficulty level")
        
        config = self.DIFFICULTY_SETTINGS[difficulty]
        length = config["length"]
        reward = config["reward"]
        
        # O(1) pair selection using precomputed pairs
        try:
            start_word, target_word, ideal_path = self.get_random_pair_optimized(length)
        except ValueError:
            raise ValueError(f"No valid word pairs available for difficulty {difficulty}")
        
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
        """Submit a move - O(1) validations using precomputed data"""
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
        
        # O(1) validations using precomputed data
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
        
        # O(1) one-letter difference check
        if not self._one_letter_diff(current_word, move):
            game["mistakes"] += 1
            return {
                "success": False,
                "message": "You can only change one letter at a time",
                "current_word": current_word,
                "move_count": game["move_count"],
                "is_complete": False,
                "game_over": False
            }
        
        # O(1) word validation using precomputed set
        if not self.validate_word_optimized(move, word_length):
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
        """Get a hint - O(1) using cached paths"""
        if game_id not in self.active_games:
            raise ValueError("Game not found")
        
        game = self.active_games[game_id]
        
        if game["user_id"] != user_id:
            raise ValueError("Unauthorized access to game")
        
        if game["is_complete"]:
            raise ValueError("Game is already complete")
        
        # O(1) hint generation using cached paths
        hint = self.suggest_hint_optimized(game["current_word"], game["target_word"], game["word_length"])
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
        """Get completion statistics - O(1)"""
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
        """Get current game state - O(1)"""
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
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        return {
            "word_lists_sizes": {length: len(words) for length, words in self.word_lists.items()},
            "adjacency_graph_sizes": {length: len(graph) for length, graph in self.adjacency_graphs.items()},
            "precomputed_pairs_count": {length: len(pairs) for length, pairs in self.precomputed_pairs.items()},
            "path_cache_size": len(self.path_cache),
            "active_games": len(self.active_games)
        }

# Create global optimized instance
optimized_morphle_service = OptimizedMorphleService()
