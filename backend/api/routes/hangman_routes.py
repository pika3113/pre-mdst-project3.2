"""
Hangman game API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from models.hangman_models import (
    StartHangmanRequest, StartHangmanResponse,
    SubmitGuessRequest, SubmitWordGuessRequest, HangmanGuessResponse,
    HangmanGameStateResponse, HangmanHintRequest, HangmanHintResponse
)
from services.hangman_service_wrapper import hangman_service
from services.auth_service import AuthManager
from core.database import db_manager

router = APIRouter(prefix="/api/hangman", tags=["hangman"])

# Initialize auth manager
auth_manager = AuthManager(db_manager.db_path)


@router.post("/start", response_model=StartHangmanResponse)
async def start_hangman_game(
    request: StartHangmanRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> StartHangmanResponse:
    """Start a new hangman game for the authenticated user"""
    try:
        game_data = hangman_service.start_new_game(current_user["id"], request.difficulty)
        return StartHangmanResponse(**game_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start hangman game: {str(e)}"
        )


@router.post("/guess", response_model=HangmanGuessResponse)
async def submit_letter_guess(
    request: SubmitGuessRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> HangmanGuessResponse:
    """Submit a letter guess for the hangman game"""
    try:
        result = hangman_service.submit_guess(request.game_id, request.guess, current_user["id"])
        return HangmanGuessResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit guess: {str(e)}"
        )


@router.post("/guess-word", response_model=HangmanGuessResponse)
async def submit_word_guess(
    request: SubmitWordGuessRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> HangmanGuessResponse:
    """Submit a full word guess for the hangman game"""
    try:
        result = hangman_service.guess_word(request.game_id, request.word_guess, current_user["id"])
        # Set word_guess instead of guess in response
        result["word_guess"] = result.get("word_guess")
        result["guess"] = None
        return HangmanGuessResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit word guess: {str(e)}"
        )


@router.get("/state/{game_id}", response_model=HangmanGameStateResponse)
async def get_hangman_game_state(
    game_id: str,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> HangmanGameStateResponse:
    """Get current state of a hangman game"""
    try:
        game_state = hangman_service.get_game_state(game_id, current_user["id"])
        return HangmanGameStateResponse(**game_state)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get game state: {str(e)}"
        )


@router.post("/hint", response_model=HangmanHintResponse)
async def get_hangman_hint(
    request: HangmanHintRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> HangmanHintResponse:
    """Get a hint for the hangman game (reveals a random letter)"""
    try:
        result = hangman_service.get_hint(request.game_id, current_user["id"])
        return HangmanHintResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hint: {str(e)}"
        )


@router.get("/debug/answer/{game_id}")
async def get_hangman_answer(
    game_id: str,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> Dict:
    """DEBUG ONLY: Get the answer for a hangman game (for development/debugging)"""
    try:
        # Check if game exists
        if game_id not in hangman_service.games:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        game = hangman_service.games[game_id]
        
        # Check authorization
        if game.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this game"
            )
        
        return {
            "game_id": game_id,
            "answer": game.word,  # Direct access to the word for debug purposes
            "difficulty": game.difficulty,
            "word_length": len(game.word),
            "remaining_guesses": game.remaining_guesses,
            "debug": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hangman answer: {str(e)}"
        )
