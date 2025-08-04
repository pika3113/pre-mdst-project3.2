"""
Main FastAPI application with modular architecture
Wordle Game Backend Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import ALLOWED_ORIGINS
from core.database import db_manager
from api import api_router

# Create FastAPI application
app = FastAPI(
    title="WordGames API",
    description="A hub with 3 games",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],   
)

# Include API routes
app.include_router(api_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("Starting WordGames API...")
    print("Initializing database...")
    db_manager.init_database()
    
    # Also initialize auth tables
    from services.auth_service import AuthManager
    auth_manager = AuthManager(db_manager.db_path)
    auth_manager.init_auth_tables()
    
    print("Database initialized successfully")
    print("WordGames API is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down WordGames API...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "WordGames API",
        "version": "2.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the WordGames API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
