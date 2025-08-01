"""
Morphle game data models
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class MorphleDifficulty(str, Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"

class StartMorphleGameRequest(BaseModel):
    difficulty: MorphleDifficulty

class StartMorphleGameResponse(BaseModel):
    game_id: str
    start_word: str
    target_word: str
    difficulty: str
    word_length: int
    ideal_steps: int
    reward: int
    hint_cost: int

class SubmitMorphleMoveRequest(BaseModel):
    game_id: str
    move: str

class SubmitMorphleMoveResponse(BaseModel):
    success: bool
    message: str
    current_word: str
    move_count: int
    is_complete: bool
    game_over: bool
    
class MorphleHintRequest(BaseModel):
    game_id: str

class MorphleHintResponse(BaseModel):
    hint: Optional[str]
    cost: int
    message: str

class CompleteMorphleGameResponse(BaseModel):
    success: bool
    duration: int
    move_count: int
    ideal_steps: int
    base_reward: int
    time_bonus: int
    streak_bonus: int
    total_earnings: int
    ideal_path: List[str]

class MorphleGameStateResponse(BaseModel):
    game_id: str
    start_word: str
    target_word: str
    current_word: str
    difficulty: str
    move_count: int
    hint_cost: int
    hint_uses: int
    mistakes: int
    start_time: float
    is_complete: bool
