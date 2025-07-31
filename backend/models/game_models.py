"""
Pydantic models for game-related API requests and responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StartGameRequest(BaseModel):
    difficulty: str = Field(..., description="Game difficulty: easy, medium, or hard")


class StartGameResponse(BaseModel):
    game_id: int
    difficulty: str
    word_length: int
    max_guesses: int
    guesses_made: int
    game_state: str


class SubmitGuessRequest(BaseModel):
    game_id: int
    guess: str = Field(..., min_length=4, max_length=6, description="Player's guess")


class GuessResult(BaseModel):
    guess: str
    result: List[str]  # List of colors: green, yellow, red
    timestamp: str


class SubmitGuessResponse(BaseModel):
    game_id: int
    guess: str
    result: List[str]
    guesses_made: int
    max_guesses: int
    game_state: str
    target_word: Optional[str] = None
    all_guesses: List[GuessResult]


class GameStateResponse(BaseModel):
    game_id: int
    difficulty: str
    word_length: int
    max_guesses: int
    guesses_made: int
    game_state: str
    target_word: Optional[str] = None
    all_guesses: List[GuessResult]


class ValidateWordRequest(BaseModel):
    word: str = Field(..., min_length=4, max_length=6)
    difficulty: str


class ValidateWordResponse(BaseModel):
    word: str
    is_valid: bool
    word_length: int


class WordListsResponse(BaseModel):
    easy: List[str]
    medium: List[str]
    hard: List[str]
    stats: Dict[str, int]
