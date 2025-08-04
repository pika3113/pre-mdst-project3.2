"""
Balance API models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BalanceResponse(BaseModel):
    """User balance information"""
    balance: int = Field(..., description="Current balance")
    total_earned: int = Field(..., description="Total amount earned")
    total_spent: int = Field(..., description="Total amount spent")
    created_at: Optional[str] = Field(None, description="Account creation date")
    updated_at: Optional[str] = Field(None, description="Last balance update")


class TransactionResponse(BaseModel):
    """Transaction history item"""
    amount: int = Field(..., description="Transaction amount (negative for spending)")
    transaction_type: str = Field(..., description="Type of transaction")
    game_type: Optional[str] = Field(None, description="Game that generated this transaction")
    description: Optional[str] = Field(None, description="Transaction description")
    created_at: str = Field(..., description="Transaction timestamp")


class TransactionHistoryResponse(BaseModel):
    """Transaction history response"""
    transactions: List[TransactionResponse] = Field(..., description="List of transactions")
    current_balance: int = Field(..., description="User's current balance")


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    username: str = Field(..., description="Username")
    balance: int = Field(..., description="Current balance")
    total_earned: int = Field(..., description="Total earned")


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    leaderboard: List[LeaderboardEntry] = Field(..., description="Top users by balance")


class GameRewardResponse(BaseModel):
    """Game completion reward response"""
    reward_amount: int = Field(..., description="Amount earned from the game")
    new_balance: int = Field(..., description="User's new balance after reward")
    description: str = Field(..., description="Description of the reward")
