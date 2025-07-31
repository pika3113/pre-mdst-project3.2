"""
Word management service for the Wordle game
Handles word generation, validation, and NLTK integration
"""
import random
import ssl
from typing import Dict, List, Set
import nltk
from nltk.corpus import brown

from core.config import DIFFICULTY_WORD_LENGTHS


class WordService:
    """Service for managing game words and validation"""
    
    def __init__(self):
        self.word_lists: Dict[int, List[str]] = {}
        self.all_valid_words: Dict[int, Set[str]] = {}
        self._initialize_nltk()
        self._generate_word_lists()
    
    def _initialize_nltk(self):
        """Initialize NLTK data if not already present"""
        try:
            # Try to create unverified HTTPS context for NLTK downloads
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            # Download brown corpus if not present
            nltk.data.find('corpora/brown')
        except LookupError:
            nltk.download('brown', quiet=True)
    
    def _generate_word_lists(self):
        """Generate word lists for each difficulty level from NLTK Brown corpus"""
        try:
            # Get all English words from NLTK Brown corpus
            english_words = set(word.upper() for word in brown.words() if word.isalpha())
            
            # Filter words by length
            self.word_lists = {4: [], 5: [], 6: []}
            self.all_valid_words = {4: set(), 5: set(), 6: set()}
            
            for word in english_words:
                word_len = len(word)
                if word_len in [4, 5, 6]:
                    self.all_valid_words[word_len].add(word)
                    if len(self.word_lists[word_len]) < 3000:  # Limit to 3000 words per difficulty
                        self.word_lists[word_len].append(word)
            
            # Sort for consistency
            for length in self.word_lists:
                self.word_lists[length] = sorted(self.word_lists[length])
                
        except Exception as e:
            print(f"Error generating word lists from NLTK Brown corpus: {e}")
            # Fallback to basic word lists if NLTK fails
            self._use_fallback_words()
    
    def _use_fallback_words(self):
        """Fallback word lists if NLTK is unavailable"""
        self.word_lists = {
            4: ["WORD", "GAME", "PLAY", "BEST", "LOVE", "LIFE", "TIME", "GOOD", "MAKE", "WORK", "HELL", "BALL", "CALL", "FALL"],
            5: ["WORDS", "GAMES", "PLAYS", "LOVED", "LIVES", "TIMES", "GOODS", "MAKES", "WORKS", "STUDY", "HELLO", "BALLS", "CALLS", "FALLS"],
            6: ["WORDLE", "GAMING", "PLAYER", "LOVING", "LIVING", "TIMING", "MAKING", "WORKED", "STUDIED", "BETTER", "HELLOS", "CALLED", "FALLEN", "BALLED"]
        }
        
        self.all_valid_words = {
            4: set(self.word_lists[4]),
            5: set(self.word_lists[5]),
            6: set(self.word_lists[6])
        }
    
    def get_random_word(self, difficulty: str) -> str:
        """Get a random word for the specified difficulty"""
        word_length = DIFFICULTY_WORD_LENGTHS.get(difficulty, 5)
        words_list = self.word_lists.get(word_length, self.word_lists[5])
        
        if not words_list:
            # Fallback if no words available
            return ["WORD", "GAMES", "WORDLE"][word_length - 4]
        
        return random.choice(words_list)
    
    def is_valid_word(self, word: str, difficulty: str) -> bool:
        """Check if a word is valid for the given difficulty"""
        word = word.upper()
        word_length = DIFFICULTY_WORD_LENGTHS.get(difficulty, 5)
        
        if len(word) != word_length:
            return False
        
        valid_words = self.all_valid_words.get(word_length, set())
        return word in valid_words
    
    def get_word_lists(self) -> Dict[str, List[str]]:
        """Get all word lists organized by difficulty"""
        return {
            "easy": self.word_lists.get(4, []),
            "medium": self.word_lists.get(5, []),
            "hard": self.word_lists.get(6, [])
        }
    
    def get_word_list_stats(self) -> Dict[str, int]:
        """Get statistics about word list sizes"""
        return {
            "4_letter_words": len(self.word_lists.get(4, [])),
            "5_letter_words": len(self.word_lists.get(5, [])),
            "6_letter_words": len(self.word_lists.get(6, [])),
            "total_valid_4": len(self.all_valid_words.get(4, set())),
            "total_valid_5": len(self.all_valid_words.get(5, set())),
            "total_valid_6": len(self.all_valid_words.get(6, set()))
        }


# Global word service instance
word_service = WordService()
