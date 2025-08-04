"""
Balance API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from models.balance_models import (
    BalanceResponse, 
    TransactionHistoryResponse, 
    LeaderboardResponse,
    GameRewardResponse
)
from services.balance_service import balance_service
from services.auth_service import AuthManager
from core.database import db_manager

router = APIRouter(prefix="/api/balance", tags=["balance"])

# Initialize services
auth_manager = AuthManager(db_manager.db_path)


@router.get("/", response_model=BalanceResponse)
async def get_balance(current_user: dict = Depends(auth_manager.get_current_user)):
    """Get user's current balance and statistics"""
    try:
        print(f"DEBUG: current_user type: {type(current_user)}")
        print(f"DEBUG: current_user content: {current_user}")
        print(f"DEBUG: current_user.id: {current_user.get('id') if isinstance(current_user, dict) else getattr(current_user, 'id', 'No ID attr')}")
        
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user.id
        balance_info = balance_service.get_user_balance(user_id)
        return BalanceResponse(**balance_info)
    except Exception as e:
        import traceback
        print(f"ERROR in get_balance: {str(e)}")
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get balance: {str(e)}"
        )


@router.get("/history", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    limit: int = 50,
    current_user: dict = Depends(auth_manager.get_current_user)
):
    """Get user's transaction history"""
    try:
        print(f"DEBUG history: current_user type: {type(current_user)}")
        print(f"DEBUG history: current_user content: {current_user}")
        
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user.id
        transactions = balance_service.get_transaction_history(user_id, limit)
        balance_info = balance_service.get_user_balance(user_id)
        
        return TransactionHistoryResponse(
            transactions=transactions,
            current_balance=balance_info['balance']
        )
    except Exception as e:
        import traceback
        print(f"ERROR in get_transaction_history: {str(e)}")
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction history: {str(e)}"
        )


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(limit: int = 10):
    """Get balance leaderboard"""
    try:
        leaderboard = balance_service.get_leaderboard(limit)
        return LeaderboardResponse(leaderboard=leaderboard)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )
