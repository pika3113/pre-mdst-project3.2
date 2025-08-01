"""
Hangman game models
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class StartHangmanRequest(BaseModel):
    """Request model for starting a new hangman game"""
    difficulty: str = Field(..., description="Game difficulty: easy, medium, hard, extreme")

class StartHangmanResponse(BaseModel):
    """Response model for starting a new hangman game"""
    game_id: str
    display_word: str
    remaining_guesses: int
    difficulty: str
    word_length: int
    guessed_letters: List[str]
    is_game_over: bool
    is_won: bool

class SubmitGuessRequest(BaseModel):
    """Request model for submitting a letter guess"""
    game_id: str
    guess: str = Field(..., min_length=1, max_length=1, description="Single letter guess")

class SubmitWordGuessRequest(BaseModel):
    """Request model for submitting a word guess"""
    game_id: str
    word_guess: str = Field(..., min_length=1, description="Full word guess")

class HangmanGuessResponse(BaseModel):
    """Response model for hangman guesses"""
    game_id: str
    guess: Optional[str] = None
    word_guess: Optional[str] = None
    is_correct: bool
    display_word: str
    remaining_guesses: int
    guessed_letters: List[str]
    is_game_over: bool
    is_won: bool
    message: str
    word: Optional[str] = None

class HangmanGameStateResponse(BaseModel):
    """Response model for current hangman game state"""
    game_id: str
    display_word: str
    remaining_guesses: int
    difficulty: str
    word_length: int
    guessed_letters: List[str]
    is_game_over: bool
    is_won: bool
    word: Optional[str] = None

class HangmanHintRequest(BaseModel):
    """Request model for getting a hint"""
    game_id: str

class HangmanHintResponse(BaseModel):
    """Response model for hangman hint"""
    game_id: str
    hint_letter: str
    display_word: str
    remaining_guesses: int
    guessed_letters: List[str]
    is_game_over: bool
    is_won: bool
    message: str
    word: Optional[str] = None
