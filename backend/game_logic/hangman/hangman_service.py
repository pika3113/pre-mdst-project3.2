"""
Hangman game service
"""
import random
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import NLTK for word corpus
try:
    from nltk.corpus import brown
    import nltk
    # Download corpus if not already present
    try:
        list(brown.words())
    except LookupError:
        try:
            nltk.download('brown')
        except Exception as e:
            print(f"Warning: Could not download NLTK brown corpus: {e}")
            brown = None
except ImportError:
    # Fallback word lists if NLTK is not available
    print("Warning: NLTK not available, using fallback word lists")
    brown = None

@dataclass
class HangmanGameState:
    """Represents the current state of a hangman game"""
    game_id: str
    user_id: int
    word: str
    difficulty: str
    guessed_letters: set
    correct_guesses: set
    incorrect_guesses: set
    display_word: str
    remaining_guesses: int
    is_game_over: bool
    is_won: bool
    created_at: datetime

class HangmanService:
    """Service for managing hangman games"""
    
    def __init__(self):
        self.games: Dict[str, HangmanGameState] = {}
        self.difficulty_settings = {
            "easy": {"word_length": (4, 5), "max_guesses": 8},
            "medium": {"word_length": (6, 7), "max_guesses": 7},
            "hard": {"word_length": (8, 8), "max_guesses": 6},
            "extreme": {"word_length": (9, 15), "max_guesses": 5}
        }
        self._load_word_lists()
    
    def _load_word_lists(self):
        """Load word lists based on difficulty"""
        if brown:
            # Use NLTK brown corpus
            all_words = [word.upper() for word in brown.words() if word.isalpha()]
        else:
            # Fallback word lists
            all_words = [
                "PYTHON", "JAVASCRIPT", "COMPUTER", "PROGRAMMING", "DEVELOPER",
                "ALGORITHM", "DATABASE", "FUNCTION", "VARIABLE", "HANGMAN",
                "CHALLENGE", "WORD", "GUESS", "LETTER", "GAME", "CODE",
                "SOFTWARE", "HARDWARE", "INTERNET", "WEBSITE", "BROWSER",
                "KEYBOARD", "MONITOR", "MOUSE", "PROCESSOR", "MEMORY"
            ]
        
        self.word_lists = {}
        for difficulty, settings in self.difficulty_settings.items():
            min_len, max_len = settings["word_length"]
            self.word_lists[difficulty] = [
                word for word in all_words 
                if min_len <= len(word) <= max_len and len(word) >= 3
            ]
            
            # Ensure we have enough words for each difficulty
            if len(self.word_lists[difficulty]) < 10:
                # Add some fallback words if not enough found
                fallback_words = {
                    "easy": ["WORD", "GAME", "PLAY", "EASY", "HELP"],
                    "medium": ["PYTHON", "CODING", "GAMING", "SIMPLE"],
                    "hard": ["COMPUTER", "KEYBOARD", "FUNCTION", "VARIABLE"],
                    "extreme": ["PROGRAMMING", "JAVASCRIPT", "ALGORITHM", "CHALLENGE"]
                }
                self.word_lists[difficulty].extend(fallback_words.get(difficulty, []))
    
    def start_new_game(self, user_id: int, difficulty: str = "medium") -> Dict:
        """Start a new hangman game"""
        if difficulty not in self.difficulty_settings:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        
        # Select a random word
        word_list = self.word_lists[difficulty]
        if not word_list:
            raise ValueError(f"No words available for difficulty: {difficulty}")
        
        word = random.choice(word_list)
        game_id = str(uuid.uuid4())
        
        max_guesses = self.difficulty_settings[difficulty]["max_guesses"]
        
        game_state = HangmanGameState(
            game_id=game_id,
            user_id=user_id,
            word=word,
            difficulty=difficulty,
            guessed_letters=set(),
            correct_guesses=set(),
            incorrect_guesses=set(),
            display_word=self._create_display_word(word, set()),
            remaining_guesses=max_guesses,
            is_game_over=False,
            is_won=False,
            created_at=datetime.now()
        )
        
        self.games[game_id] = game_state
        
        return {
            "game_id": game_id,
            "display_word": game_state.display_word,
            "remaining_guesses": game_state.remaining_guesses,
            "difficulty": difficulty,
            "word_length": len(word),
            "guessed_letters": list(game_state.guessed_letters),
            "is_game_over": False,
            "is_won": False
        }
    
    def submit_guess(self, game_id: str, guess: str, user_id: int) -> Dict:
        """Submit a letter guess for the game"""
        if game_id not in self.games:
            raise ValueError("Game not found")
        
        game = self.games[game_id]
        
        if game.user_id != user_id:
            raise ValueError("Not authorized to play this game")
        
        if game.is_game_over:
            raise ValueError("Game is already over")
        
        guess = guess.upper().strip()
        
        if len(guess) != 1 or not guess.isalpha():
            raise ValueError("Guess must be a single letter")
        
        if guess in game.guessed_letters:
            raise ValueError("Letter already guessed")
        
        # Add to guessed letters
        game.guessed_letters.add(guess)
        
        # Check if letter is in word
        if guess in game.word:
            game.correct_guesses.add(guess)
            message = "Correct guess!"
        else:
            game.incorrect_guesses.add(guess)
            game.remaining_guesses -= 1
            message = "Incorrect guess!"
        
        # Update display word
        game.display_word = self._create_display_word(game.word, game.correct_guesses)
        
        # Check win condition
        if "_" not in game.display_word:
            game.is_game_over = True
            game.is_won = True
            message = "Congratulations! You won!"
        
        # Check lose condition
        elif game.remaining_guesses <= 0:
            game.is_game_over = True
            game.is_won = False
            message = f"Game over! The word was: {game.word}"
        
        return {
            "game_id": game_id,
            "guess": guess,
            "is_correct": guess in game.word,
            "display_word": game.display_word,
            "remaining_guesses": game.remaining_guesses,
            "guessed_letters": sorted(list(game.guessed_letters)),
            "is_game_over": game.is_game_over,
            "is_won": game.is_won,
            "message": message,
            "word": game.word if game.is_game_over else None
        }
    
    def guess_word(self, game_id: str, word_guess: str, user_id: int) -> Dict:
        """Submit a full word guess"""
        if game_id not in self.games:
            raise ValueError("Game not found")
        
        game = self.games[game_id]
        
        if game.user_id != user_id:
            raise ValueError("Not authorized to play this game")
        
        if game.is_game_over:
            raise ValueError("Game is already over")
        
        word_guess = word_guess.upper().strip()
        
        if word_guess == game.word:
            game.is_game_over = True
            game.is_won = True
            game.display_word = game.word
            message = "Congratulations! You guessed the word!"
        else:
            game.remaining_guesses -= 2  # Penalty for wrong word guess
            if game.remaining_guesses <= 0:
                game.is_game_over = True
                game.is_won = False
                message = f"Wrong word guess! Game over! The word was: {game.word}"
            else:
                message = f"Wrong word guess! You lose 2 guesses. {game.remaining_guesses} remaining."
        
        return {
            "game_id": game_id,
            "word_guess": word_guess,
            "is_correct": word_guess == game.word,
            "display_word": game.display_word,
            "remaining_guesses": game.remaining_guesses,
            "guessed_letters": sorted(list(game.guessed_letters)),
            "is_game_over": game.is_game_over,
            "is_won": game.is_won,
            "message": message,
            "word": game.word if game.is_game_over else None
        }
    
    def get_game_state(self, game_id: str, user_id: int) -> Dict:
        """Get current game state"""
        if game_id not in self.games:
            raise ValueError("Game not found")
        
        game = self.games[game_id]
        
        if game.user_id != user_id:
            raise ValueError("Not authorized to view this game")
        
        return {
            "game_id": game_id,
            "display_word": game.display_word,
            "remaining_guesses": game.remaining_guesses,
            "difficulty": game.difficulty,
            "word_length": len(game.word),
            "guessed_letters": sorted(list(game.guessed_letters)),
            "is_game_over": game.is_game_over,
            "is_won": game.is_won,
            "word": game.word if game.is_game_over else None
        }
    
    def _create_display_word(self, word: str, correct_guesses: set) -> str:
        """Create display word with guessed letters revealed"""
        return " ".join([letter if letter in correct_guesses else "_" for letter in word])
    
    def get_hint(self, game_id: str, user_id: int) -> Dict:
        """Get a hint for the current game (reveals a random unguessed letter)"""
        if game_id not in self.games:
            raise ValueError("Game not found")
        
        game = self.games[game_id]
        
        if game.user_id != user_id:
            raise ValueError("Not authorized to play this game")
        
        if game.is_game_over:
            raise ValueError("Game is already over")
        
        # Find unguessed letters in the word
        unguessed_letters = set(game.word) - game.correct_guesses
        
        if not unguessed_letters:
            raise ValueError("All letters already revealed")
        
        # Reveal a random letter
        hint_letter = random.choice(list(unguessed_letters))
        game.correct_guesses.add(hint_letter)
        game.guessed_letters.add(hint_letter)
        
        # Update display word
        game.display_word = self._create_display_word(game.word, game.correct_guesses)
        
        # Check win condition
        if "_" not in game.display_word:
            game.is_game_over = True
            game.is_won = True
            message = "Congratulations! You won with a hint!"
        else:
            message = f"Hint: The letter '{hint_letter}' is in the word!"
        
        return {
            "game_id": game_id,
            "hint_letter": hint_letter,
            "display_word": game.display_word,
            "remaining_guesses": game.remaining_guesses,
            "guessed_letters": sorted(list(game.guessed_letters)),
            "is_game_over": game.is_game_over,
            "is_won": game.is_won,
            "message": message,
            "word": game.word if game.is_game_over else None
        }

# Create global instance
hangman_service = HangmanService()
