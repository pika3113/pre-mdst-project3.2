"""
Pydantic models for statistics and user data
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class GuessDistribution(BaseModel):
    """Distribution of guess counts for won games"""
    one: int = 0
    two: int = 0
    three: int = 0
    four: int = 0
    five: int = 0
    six: int = 0


class UserStatistics(BaseModel):
    total_games: int
    games_won: int
    games_lost: int
    win_rate: float
    current_streak: int
    max_streak: int
    average_guesses: float
    guess_distribution: Dict[str, int]


class DifficultyStatistics(BaseModel):
    easy: Optional[UserStatistics] = None
    medium: Optional[UserStatistics] = None
    hard: Optional[UserStatistics] = None


class GameHistoryItem(BaseModel):
    game_id: int
    word: str
    difficulty: str
    guess_count: int
    won: bool
    completed_at: str
    guesses: List[str]


class GameHistoryResponse(BaseModel):
    games: List[GameHistoryItem]
    total_count: int


class RecentPerformance(BaseModel):
    games_last_7_days: int
    wins_last_7_days: int
    win_rate_last_7_days: float


class StatisticsInsights(BaseModel):
    best_difficulty: Optional[str]
    worst_difficulty: Optional[str]
    most_common_guess_count: Optional[int]


class DetailedStatisticsResponse(BaseModel):
    overall: UserStatistics
    by_difficulty: Dict[str, UserStatistics]
    recent_performance: RecentPerformance
    insights: StatisticsInsights


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
