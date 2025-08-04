"""
Roulette game API routes
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from models.roulette_api_models import (
    RouletteGameRequest, RouletteGameResponse, RouletteInfoResponse,
    RouletteBet
)
from services.roulette_service import RouletteService

router = APIRouter(prefix="/api/roulette", tags=["roulette"])

# Initialize roulette service
roulette_service = RouletteService()


@router.post("/play", response_model=RouletteGameResponse)
async def play_roulette(game_request: RouletteGameRequest) -> RouletteGameResponse:
    """Play a round of roulette"""
    try:
        # Convert Pydantic models to the format expected by the service
        bets = []
        for bet in game_request.bets:
            if bet.bet_type in ["color", "evenodd"]:
                # For color and even/odd bets, selection is a string
                bet_list = [bet.bet_type, bet.amount, bet.selection]
            else:
                # For number-based bets, selection is a list of numbers
                if isinstance(bet.selection, list):
                    bet_list = [bet.bet_type, bet.amount] + bet.selection
                else:
                    bet_list = [bet.bet_type, bet.amount, bet.selection]
            
            # Validate the bet
            if not roulette_service.validate_bet(bet_list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid bet: {bet.bet_type} with selection {bet.selection}"
                )
            
            bets.append(bet_list)
        
        # Play the game
        result = roulette_service.play_roulette(bets)
        
        return RouletteGameResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Game failed: {str(e)}"
        )


@router.get("/info", response_model=RouletteInfoResponse)
async def get_roulette_info() -> RouletteInfoResponse:
    """Get roulette game information"""
    try:
        info = roulette_service.get_bet_types()
        
        # Add bet type descriptions
        bet_types = {
            "single": "Bet on a single number (0-36)",
            "double": "Bet on two adjacent numbers",
            "three": "Bet on three numbers in a row",
            "four": "Bet on four numbers in a square",
            "five": "Bet on five numbers (0, 00, 1, 2, 3)",
            "six": "Bet on six numbers in two rows",
            "dozens": "Bet on 12 numbers (1-12, 13-24, or 25-36)",
            "column": "Bet on one of three columns",
            "eighteens": "Bet on 1-18 or 19-36",
            "color": "Bet on red or black",
            "evenodd": "Bet on even or odd numbers"
        }
        
        return RouletteInfoResponse(
            multipliers=info["multipliers"],
            wheel=info["wheel"],
            bet_types=bet_types
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get game info: {str(e)}"
        )


@router.get("/")
async def roulette_status():
    """Get roulette game status"""
    return {
        "game": "roulette",
        "status": "active",
        "description": "European Roulette with numbers 0-36"
    }
