"""
Morphle game API routes with optimized service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from models.morphle_models import (
    StartMorphleGameRequest, StartMorphleGameResponse,
    SubmitMorphleMoveRequest, SubmitMorphleMoveResponse,
    MorphleHintRequest, MorphleHintResponse,
    CompleteMorphleGameResponse, MorphleGameStateResponse
)
from models.auth_models import UserResponse
from services.morphle_service_wrapper import optimized_morphle_service
from services.auth_service import AuthManager
from core.database import db_manager

router = APIRouter(prefix="/api/morphle", tags=["morphle"])

# Initialize auth manager
auth_manager = AuthManager(db_manager.db_path)


@router.post("/start", response_model=StartMorphleGameResponse)
async def start_morphle_game(
    request: StartMorphleGameRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> StartMorphleGameResponse:
    """Start a new Morphle game for the authenticated user"""
    try:
        game_data = optimized_morphle_service.start_game(current_user["id"], request.difficulty.value)
        return StartMorphleGameResponse(**game_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Morphle game: {str(e)}"
        )


@router.post("/move", response_model=SubmitMorphleMoveResponse)
async def submit_morphle_move(
    request: SubmitMorphleMoveRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> SubmitMorphleMoveResponse:
    """Submit a move in the Morphle game"""
    try:
        result = optimized_morphle_service.submit_move(request.game_id, request.move, current_user["id"])
        return SubmitMorphleMoveResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit move: {str(e)}"
        )


@router.post("/hint", response_model=MorphleHintResponse)
async def get_morphle_hint(
    request: MorphleHintRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> MorphleHintResponse:
    """Get a hint for the current Morphle game"""
    try:
        result = optimized_morphle_service.get_hint(request.game_id, current_user["id"])
        return MorphleHintResponse(**result)
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


@router.get("/game/{game_id}/state", response_model=MorphleGameStateResponse)
async def get_morphle_game_state(
    game_id: str,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> MorphleGameStateResponse:
    """Get current state of a Morphle game"""
    try:
        result = optimized_morphle_service.get_game_state(game_id, current_user["id"])
        return MorphleGameStateResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get game state: {str(e)}"
        )


@router.get("/game/{game_id}/completion", response_model=CompleteMorphleGameResponse)
async def get_morphle_completion_stats(
    game_id: str,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> CompleteMorphleGameResponse:
    """Get completion statistics for a finished Morphle game"""
    try:
        result = optimized_morphle_service.get_game_completion_stats(game_id, current_user["id"])
        return CompleteMorphleGameResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get completion stats: {str(e)}"
        )


@router.get("/cache/stats")
async def get_morphle_cache_stats(
    current_user: dict = Depends(auth_manager.get_current_user)
) -> Dict:
    """Get cache statistics for performance monitoring"""
    try:
        return optimized_morphle_service.get_cache_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )
