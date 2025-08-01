"""
Hangman service wrapper - imports from organized game_logic structure
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from game_logic.hangman.hangman_service import hangman_service
except ImportError:
    # If import fails, keep the original service location
    from .hangman_service import hangman_service

__all__ = ['hangman_service']
