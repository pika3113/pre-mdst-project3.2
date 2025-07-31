"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status

from models.auth_models import (
    UserCreate, UserLogin, UserResponse, Token,
    GoogleAuthRequest, GoogleCallbackRequest, GoogleAuthResponse
)
from services.auth_service import AuthManager
from services.google_auth_service import GoogleOAuthService
from core.database import db_manager

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Initialize services
auth_manager = AuthManager(db_manager.db_path)
google_service = GoogleOAuthService()


@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate) -> Token:
    """Register a new user and return access token (auto-login)"""
    try:
        user = auth_manager.create_user(user_data.username, user_data.email, user_data.password)
        
        # Create access token for auto-login after registration
        access_token = auth_manager.create_access_token(data={"sub": user["username"]})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin) -> Token:
    """Authenticate user and return access token"""
    try:
        user = auth_manager.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user["username"]})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/google")
async def google_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        auth_url = google_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Google auth URL: {str(e)}"
        )


@router.post("/google/callback", response_model=GoogleAuthResponse)
async def google_callback(request_data: GoogleCallbackRequest) -> GoogleAuthResponse:
    """Handle Google OAuth callback with authorization code"""
    try:
        code = request_data.code
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is required"
            )
        
        # Process Google OAuth with the authorization code
        result = google_service.process_google_auth(code)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code"
            )
        
        # Create or get user
        user = auth_manager.create_or_update_google_user(result)
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user["username"]})
        
        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(google_request: GoogleAuthRequest) -> GoogleAuthResponse:
    """Authenticate user with Google OAuth"""
    try:
        result = google_service.verify_google_token(google_request.credential)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google credential"
            )
        
        # Create or get user
        user = auth_manager.create_or_update_google_user(result)
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user["username"]})
        
        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout_user():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}


@router.get("/verify-token", response_model=UserResponse)
async def verify_token(current_user: dict = Depends(auth_manager.get_current_user)) -> UserResponse:
    """Verify the current access token and return user info"""
    return UserResponse(**current_user)
