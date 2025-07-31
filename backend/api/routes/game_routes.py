"""
Game-related API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from models.game_models import (
    StartGameRequest, StartGameResponse,
    SubmitGuessRequest, SubmitGuessResponse,
    GameStateResponse, ValidateWordRequest, ValidateWordResponse,
    WordListsResponse
)
from models.auth_models import UserResponse
from services.game_service import game_service
from services.word_service import word_service
from services.auth_service import AuthManager
from core.database import db_manager

router = APIRouter(prefix="/api/game", tags=["game"])

# Initialize auth manager
auth_manager = AuthManager(db_manager.db_path)


@router.post("/start", response_model=StartGameResponse)
async def start_new_game(
    request: StartGameRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> StartGameResponse:
    """Start a new game for the authenticated user"""
    try:
        game_data = game_service.start_new_game(current_user["id"], request.difficulty)
        return StartGameResponse(**game_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start game: {str(e)}"
        )


@router.post("/guess", response_model=SubmitGuessResponse)
async def submit_guess(
    request: SubmitGuessRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> SubmitGuessResponse:
    """Submit a guess for the current game"""
    try:
        result = game_service.submit_guess(request.game_id, request.guess, current_user["id"])
        return SubmitGuessResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process guess: {str(e)}"
        )


@router.get("/state/{game_id}", response_model=GameStateResponse)
async def get_game_state(
    game_id: int,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> GameStateResponse:
    """Get the current state of a game"""
    game_state = game_service.get_game_state(game_id, current_user["id"])
    
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    return GameStateResponse(**game_state)


@router.post("/validate-word", response_model=ValidateWordResponse)
async def validate_word(request: ValidateWordRequest) -> ValidateWordResponse:
    """Validate if a word is acceptable for the given difficulty"""
    is_valid = word_service.is_valid_word(request.word, request.difficulty)
    
    return ValidateWordResponse(
        word=request.word.upper(),
        is_valid=is_valid,
        word_length=len(request.word)
    )


@router.get("/word-lists", response_model=WordListsResponse)
async def get_word_lists() -> WordListsResponse:
    """Get available word lists and statistics"""
    word_lists = word_service.get_word_lists()
    stats = word_service.get_word_list_stats()
    
    return WordListsResponse(
        easy=word_lists["easy"][:100],  # Return only first 100 for each difficulty
        medium=word_lists["medium"][:100],
        hard=word_lists["hard"][:100],
        stats=stats
    )
