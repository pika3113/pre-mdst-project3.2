#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the word validation functions
import nltk
from nltk.corpus import words

# Generate word lists (simplified version of main.py logic)
def test_word_validation():
    try:
        # Get all English words from NLTK
        all_english_words = set(word.upper() for word in words.words() if word.isalpha())
        
        # Cache all valid words for efficient validation
        ALL_VALID_WORDS = {}
        for word in all_english_words:
            word_len = len(word)
            if word_len in [4, 5, 6]:
                if word_len not in ALL_VALID_WORDS:
                    ALL_VALID_WORDS[word_len] = set()
                ALL_VALID_WORDS[word_len].add(word)
        
        def is_valid_word(word: str, word_length: int) -> bool:
            """Check if a word is valid using cached word set"""
            word = word.upper()
            return word in ALL_VALID_WORDS.get(word_length, set())
        
        # Test words
        test_words = [
            ("HELL", 4),
            ("WORD", 4),
            ("HELLO", 5),
            ("WORLD", 5),
            ("PYTHON", 6),
            ("CODING", 6)
        ]
        
        print("Word Validation Test Results:")
        print("=" * 40)
        for word, length in test_words:
            result = is_valid_word(word, length)
            print(f"{word} (length {length}): {'✓ VALID' if result else '✗ INVALID'}")
        
        print(f"\nTotal words loaded:")
        for length in [4, 5, 6]:
            count = len(ALL_VALID_WORDS.get(length, set()))
            print(f"  {length}-letter words: {count}")
        
        return ALL_VALID_WORDS, is_valid_word
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None

if __name__ == "__main__":
    test_word_validation()
