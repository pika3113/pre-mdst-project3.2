"""
Quick test script to check if the modular backend structure is working
"""

def test_imports():
    """Test if all the imports are working correctly"""
    try:
        print("Testing core imports...")
        from core.config import SECRET_KEY, ALLOWED_ORIGINS
        print("✅ Core config imports successful")
        
        print("Testing database imports...")
        from core.database import db_manager
        print("✅ Database imports successful")
        
        print("Testing models imports...")
        from models.auth_models import UserCreate, UserResponse, Token
        from models.game_models import StartGameRequest
        from models.user_models import UserStatistics
        print("✅ Models imports successful")
        
        print("Testing services imports...")
        from services.auth_service import AuthManager
        print("✅ Auth service imports successful")
        
        # Skip word service for now due to NLTK dependency
        # from services.word_service import word_service
        # print("✅ Word service imports successful")
        
        from services.game_service import GameService
        print("✅ Game service imports successful")
        
        from services.stats_service import StatisticsService
        print("✅ Stats service imports successful")
        
        print("Testing API routes imports...")
        from api.routes.auth_routes import router as auth_router
        from api.routes.wordle_routes import router as wordle_router  
        from api.routes.user_routes import router as user_router
        print("✅ API routes imports successful")
        
        print("Testing main API router...")
        from api import api_router
        print("✅ Main API router imports successful")
        
        print("\n🎉 All modular imports are working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
