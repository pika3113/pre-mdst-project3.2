"""
Game logic service for the Wordle game
Handles game state, guess processing, and game completion
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pytz

from core.database import db_manager
from core.config import MAX_GUESSES, DEFAULT_TIMEZONE
from .word_service import word_service


class GameService:
    """Service for managing game logic and state"""
    
    def start_new_game(self, user_id: int, difficulty: str) -> Dict:
        """Start a new game for the user"""
        # Get a random word for the difficulty
        target_word = word_service.get_random_word(difficulty)
        
        # Create game record in database
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO games (user_id, word, difficulty, guesses, guess_count, won)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, target_word, difficulty, "[]", 0, False))
            
            game_id = cursor.lastrowid
            conn.commit()
            
            return {
                "game_id": game_id,
                "difficulty": difficulty,
                "word_length": len(target_word),
                "max_guesses": MAX_GUESSES,
                "guesses_made": 0,
                "game_state": "active"
            }
        finally:
            conn.close()
    
    def submit_guess(self, game_id: int, guess: str, user_id: int) -> Dict:
        """Process a guess submission"""
        guess = guess.upper()
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current game state
            cursor.execute('''
                SELECT word, difficulty, guesses, guess_count, won, completed_at
                FROM games 
                WHERE id = ? AND user_id = ?
            ''', (game_id, user_id))
            
            game_row = cursor.fetchone()
            if not game_row:
                raise ValueError("Game not found")
            
            target_word, difficulty, guesses_json, guess_count, won, completed_at = game_row
            
            # Check if game is already completed
            if won or completed_at or guess_count >= MAX_GUESSES:
                raise ValueError("Game already completed")
            
            # Validate the guess
            if not word_service.is_valid_word(guess, difficulty):
                raise ValueError("Invalid word")
            
            # Process the guess
            guess_result = self._evaluate_guess(guess, target_word)
            
            # Update game state
            guesses_list = json.loads(guesses_json) if guesses_json else []
            guesses_list.append({
                "guess": guess,
                "result": guess_result,
                "timestamp": datetime.now(pytz.timezone(DEFAULT_TIMEZONE)).isoformat()
            })
            
            new_guess_count = guess_count + 1
            is_won = guess == target_word
            is_completed = is_won or new_guess_count >= MAX_GUESSES
            
            # Update database
            cursor.execute('''
                UPDATE games 
                SET guesses = ?, guess_count = ?, won = ?, completed_at = ?
                WHERE id = ?
            ''', (
                json.dumps(guesses_list),
                new_guess_count,
                is_won,
                datetime.now(pytz.timezone(DEFAULT_TIMEZONE)).isoformat() if is_completed else None,
                game_id
            ))
            
            conn.commit()
            
            # Update user statistics if game is completed
            if is_completed:
                self._update_user_statistics(user_id, difficulty, is_won, new_guess_count)
            
            # Convert color names to color codes that frontend expects
            color_map = {
                'green': '#1fdb0dff',  # correct
                'yellow': '#e4c53aff', # present
                'red': '#d71717ff'     # absent
            }
            cells = [color_map.get(color, '#d71717ff') for color in guess_result]
            
            # Prepare message for game over scenarios
            message = ""
            if is_completed:
                if is_won:
                    message = "🎉 Congratulations! You guessed it!"
                else:
                    message = f"Game over! The word was: {target_word}"
            
            return {
                "game_id": game_id,
                "guess": guess,
                "cells": cells,  # Frontend expects 'cells' with color codes
                "won": is_won,   # Frontend expects 'won' boolean
                "game_over": is_completed,  # Frontend expects 'game_over' boolean
                "word": target_word if is_completed else None,  # Frontend expects 'word'
                "message": message,  # Frontend expects 'message'
                "guesses_made": new_guess_count,
                "max_guesses": MAX_GUESSES,
                "game_state": "won" if is_won else "lost" if is_completed else "active",
                "target_word": target_word if is_completed else None,
                "all_guesses": guesses_list,
                "result": guess_result  # Keep original for backward compatibility
            }
            
        finally:
            conn.close()
    
    def _evaluate_guess(self, guess: str, target_word: str) -> List[str]:
        """Evaluate a guess and return color results"""
        result = ['red'] * len(guess)
        target_chars = list(target_word)
        guess_chars = list(guess)
        
        # First pass: mark exact matches (green)
        for i in range(len(guess)):
            if guess_chars[i] == target_chars[i]:
                result[i] = 'green'
                target_chars[i] = None  # Mark as used
                guess_chars[i] = None   # Mark as processed
        
        # Second pass: mark partial matches (yellow)
        for i in range(len(guess)):
            if guess_chars[i] is not None:  # Not already processed
                char = guess_chars[i]
                if char in target_chars:
                    result[i] = 'yellow'
                    target_chars[target_chars.index(char)] = None  # Mark as used
        
        return result
    
    def get_game_state(self, game_id: int, user_id: int) -> Optional[Dict]:
        """Get current game state"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT word, difficulty, guesses, guess_count, won, completed_at
                FROM games 
                WHERE id = ? AND user_id = ?
            ''', (game_id, user_id))
            
            game_row = cursor.fetchone()
            if not game_row:
                return None
            
            target_word, difficulty, guesses_json, guess_count, won, completed_at = game_row
            guesses_list = json.loads(guesses_json) if guesses_json else []
            
            is_completed = won or completed_at or guess_count >= MAX_GUESSES
            
            return {
                "game_id": game_id,
                "difficulty": difficulty,
                "word_length": len(target_word),
                "max_guesses": MAX_GUESSES,
                "guesses_made": guess_count,
                "game_state": "won" if won else "lost" if is_completed else "active",
                "target_word": target_word if is_completed else None,
                "all_guesses": guesses_list
            }
            
        finally:
            conn.close()

    def get_game_answer(self, game_id: int, user_id: int) -> Optional[Dict]:
        """DEBUG: Get game answer (including target word regardless of completion)"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT word, difficulty, guesses, guess_count, won, completed_at
                FROM games 
                WHERE id = ? AND user_id = ?
            ''', (game_id, user_id))
            
            game_row = cursor.fetchone()
            if not game_row:
                return None
            
            target_word, difficulty, guesses_json, guess_count, won, completed_at = game_row
            
            return {
                "game_id": game_id,
                "target_word": target_word,
                "difficulty": difficulty,
                "word_length": len(target_word),
                "guesses_made": guess_count,
                "won": won,
                "completed": bool(completed_at)
            }
            
        finally:
            conn.close()
    
    def _update_user_statistics(self, user_id: int, difficulty: str, won: bool, guess_count: int):
        """Update user statistics after game completion"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update overall statistics
            cursor.execute('''
                INSERT OR IGNORE INTO statistics (user_id) VALUES (?)
            ''', (user_id,))
            
            # Get current stats
            cursor.execute('''
                SELECT total_games, games_won, current_streak, max_streak, guess_distribution
                FROM statistics WHERE user_id = ?
            ''', (user_id,))
            
            stats_row = cursor.fetchone()
            if stats_row:
                total_games, games_won, current_streak, max_streak, guess_dist_json = stats_row
                guess_distribution = json.loads(guess_dist_json) if guess_dist_json else {}
            else:
                total_games = games_won = current_streak = max_streak = 0
                guess_distribution = {}
            
            # Update stats
            total_games += 1
            if won:
                games_won += 1
                current_streak += 1
                max_streak = max(max_streak, current_streak)
                
                # Update guess distribution
                guess_key = str(guess_count)
                guess_distribution[guess_key] = guess_distribution.get(guess_key, 0) + 1
            else:
                current_streak = 0
            
            # Update database
            cursor.execute('''
                UPDATE statistics 
                SET total_games = ?, games_won = ?, current_streak = ?, 
                    max_streak = ?, guess_distribution = ?, last_game_date = DATE('now')
                WHERE user_id = ?
            ''', (total_games, games_won, current_streak, max_streak, 
                  json.dumps(guess_distribution), user_id))
            
            # Update difficulty-specific statistics
            self._update_difficulty_statistics(cursor, user_id, difficulty, won, guess_count)
            
            conn.commit()
            
        finally:
            conn.close()
    
    def _update_difficulty_statistics(self, cursor, user_id: int, difficulty: str, won: bool, guess_count: int):
        """Update difficulty-specific statistics"""
        # Insert or ignore difficulty stats record
        cursor.execute('''
            INSERT OR IGNORE INTO difficulty_stats (user_id, difficulty) VALUES (?, ?)
        ''', (user_id, difficulty))
        
        # Get current difficulty stats
        cursor.execute('''
            SELECT total_games, games_won, current_streak, max_streak, guess_distribution, average_guesses
            FROM difficulty_stats WHERE user_id = ? AND difficulty = ?
        ''', (user_id, difficulty))
        
        diff_row = cursor.fetchone()
        if diff_row:
            total_games, games_won, current_streak, max_streak, guess_dist_json, avg_guesses = diff_row
            guess_distribution = json.loads(guess_dist_json) if guess_dist_json else {}
        else:
            total_games = games_won = current_streak = max_streak = avg_guesses = 0
            guess_distribution = {}
        
        # Update difficulty stats
        total_games += 1
        if won:
            games_won += 1
            current_streak += 1
            max_streak = max(max_streak, current_streak)
            
            # Update guess distribution and average
            guess_key = str(guess_count)
            guess_distribution[guess_key] = guess_distribution.get(guess_key, 0) + 1
            
            # Recalculate average guesses for won games
            total_guesses = sum(int(k) * v for k, v in guess_distribution.items())
            avg_guesses = total_guesses / games_won if games_won > 0 else 0
        else:
            current_streak = 0
        
        # Update database
        cursor.execute('''
            UPDATE difficulty_stats 
            SET total_games = ?, games_won = ?, current_streak = ?, 
                max_streak = ?, guess_distribution = ?, average_guesses = ?
            WHERE user_id = ? AND difficulty = ?
        ''', (total_games, games_won, current_streak, max_streak, 
              json.dumps(guess_distribution), avg_guesses, user_id, difficulty))


# Global game service instance
game_service = GameService()
