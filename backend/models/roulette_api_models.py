"""
Roulette game models for API
"""
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any


class RouletteBet(BaseModel):
    """Individual roulette bet"""
    bet_type: str = Field(..., description="Type of bet (single, double, color, etc.)")
    amount: int = Field(..., gt=0, description="Bet amount (must be positive)")
    selection: Union[List[int], str] = Field(..., description="Numbers, color, or even/odd selection")


class RouletteGameRequest(BaseModel):
    """Request to play roulette"""
    bets: List[RouletteBet] = Field(..., min_items=1, description="List of bets to place")


class RouletteWinningBet(BaseModel):
    """Information about a winning bet"""
    type: str
    amount: int
    payout: int
    selection: Union[List[int], str]


class RouletteLosingBet(BaseModel):
    """Information about a losing bet"""
    type: str
    amount: int
    selection: Union[List[int], str]


class RouletteGameResponse(BaseModel):
    """Response from roulette game"""
    pocket: int = Field(..., description="Winning pocket number")
    color: str = Field(..., description="Color of winning pocket")
    total_winnings: int = Field(..., description="Total amount won")
    winning_bets: List[RouletteWinningBet] = Field(..., description="List of winning bets")
    losing_bets: List[RouletteLosingBet] = Field(..., description="List of losing bets")
    net_result: int = Field(..., description="Net result (winnings - total bet amount)")
    new_balance: int = Field(..., description="User's balance after the game")


class RouletteInfoResponse(BaseModel):
    """Information about roulette game"""
    multipliers: Dict[str, int] = Field(..., description="Payout multipliers for each bet type")
    wheel: Dict[int, str] = Field(..., description="Roulette wheel layout")
    bet_types: Dict[str, Any] = Field(..., description="Available bet types and descriptions")
