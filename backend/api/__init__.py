"""
Main API router that combines all route modules
"""
from fastapi import APIRouter

from .routes import auth_routes, game_routes, user_routes, hangman_routes

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_routes.router)
api_router.include_router(game_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(hangman_routes.router)
