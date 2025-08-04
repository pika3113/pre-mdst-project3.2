"""
Main API router that combines all route modules
"""
from fastapi import APIRouter

from .routes import auth_routes, wordle_routes, user_routes, hangman_routes, morphle_routes, roulette_routes, balance_routes

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_routes.router)
api_router.include_router(wordle_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(hangman_routes.router)
api_router.include_router(morphle_routes.router)
api_router.include_router(roulette_routes.router)
api_router.include_router(balance_routes.router)
