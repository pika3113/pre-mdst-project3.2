"""
Morphle service wrapper - imports from organized game_logic structure
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from game_logic.morphle.optimized_morphle_service import optimized_morphle_service
    
    # Export the service with the expected name for backward compatibility
    morphle_service = optimized_morphle_service
    
except ImportError:
    # Fallback to original service if the new structure fails
    from game_logic.morphle.morphle_service import morphle_service

__all__ = ['morphle_service', 'optimized_morphle_service']
