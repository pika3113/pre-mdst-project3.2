"""
Statistics and user data API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from models.user_models import (
    UserStatistics, DetailedStatisticsResponse,
    GameHistoryResponse, UserProfileUpdate, PasswordChangeRequest
)
from models.auth_models import UserResponse
from services.stats_service import stats_service
from services.auth_service import AuthManager
from core.database import db_manager

router = APIRouter(prefix="/api/user", tags=["user"])

# Initialize auth manager
auth_manager = AuthManager(db_manager.db_path)


@router.get("/stats", response_model=UserStatistics)
async def get_user_statistics(
    current_user: dict = Depends(auth_manager.get_current_user)
) -> UserStatistics:
    """Get user's game statistics"""
    try:
        stats = stats_service.get_user_statistics(current_user["id"])
        return UserStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/detailed-stats", response_model=DetailedStatisticsResponse)
async def get_detailed_statistics(
    current_user: UserResponse = Depends(auth_manager.get_current_user)
) -> DetailedStatisticsResponse:
    """Get comprehensive user statistics with insights"""
    try:
        stats = stats_service.get_detailed_statistics(current_user.id)
        return DetailedStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detailed statistics: {str(e)}"
        )


@router.get("/game-history", response_model=GameHistoryResponse)
async def get_game_history(
    limit: int = Query(20, ge=1, le=100, description="Number of games to return"),
    current_user: dict = Depends(auth_manager.get_current_user)
) -> GameHistoryResponse:
    """Get user's game history"""
    try:
        history = stats_service.get_game_history(current_user["id"], limit)
        return GameHistoryResponse(
            games=history,
            total_count=len(history)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get game history: {str(e)}"
        )


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: dict = Depends(auth_manager.get_current_user)
) -> UserResponse:
    """Get user profile information"""
    return UserResponse(**current_user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(auth_manager.get_current_user)
) -> UserResponse:
    """Update user profile information"""
    # This would typically involve updating the database
    # For now, return the current user (placeholder implementation)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update not yet implemented"
    )


@router.post("/change-password")
async def change_password(
    password_request: PasswordChangeRequest,
    current_user: dict = Depends(auth_manager.get_current_user)
):
    """Change user password"""
    # This would typically involve validating current password and updating
    # For now, this is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password change not yet implemented"
    )
