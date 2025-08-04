"""
Wordle game API routes
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
from services.balance_service import balance_service
from core.database import db_manager

router = APIRouter(prefix="/api/wordle", tags=["wordle"])

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
        
        # Award money if game is won
        if result.get("game_over") and result.get("won"):
            # Get game details for reward calculation
            game_state = game_service.get_game_state(request.game_id, current_user["id"])
            if game_state:
                difficulty = game_state.get("difficulty", "medium")
                guess_count = result.get("guess_count", 6)
                perfect_score = guess_count == 1  # Won in 1 guess
                
                # TODO: Get user's current streak from stats
                streak = 1  # Default to 1, should get from user stats
                
                # Calculate reward
                reward = balance_service.calculate_game_reward(
                    game_type="wordle",
                    won=True,
                    difficulty=difficulty,
                    perfect_score=perfect_score,
                    streak=streak
                )
                
                if reward > 0:
                    balance_service.add_balance(
                        current_user["id"],
                        reward,
                        "game_win",
                        "wordle",
                        f"Wordle win ({difficulty}): +${reward}"
                    )
                    
                    # Add reward info to result
                    result["reward_earned"] = reward
                    result["reward_description"] = f"Great job! You earned ${reward} for winning!"
        
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


@router.get("/debug/answer/{game_id}")
async def get_game_answer(
    game_id: int,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> Dict:
    """DEBUG ONLY: Get the answer for a game (for development/debugging)"""
    try:
        # Get the game from database including the target word
        game_state = game_service.get_game_answer(game_id, current_user["id"])
        
        if not game_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        return {
            "game_id": game_id,
            "answer": game_state.get("target_word", "Unknown"),
            "difficulty": game_state.get("difficulty", "Unknown"),
            "word_length": game_state.get("word_length", 0),
            "debug": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get game answer: {str(e)}"
        )
