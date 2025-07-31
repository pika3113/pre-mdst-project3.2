"""
Statistics service for user game statistics and history
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

from core.database import db_manager
from core.config import DEFAULT_TIMEZONE


class StatisticsService:
    """Service for managing user statistics and game history"""
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get comprehensive user statistics"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get overall statistics
            cursor.execute('''
                SELECT total_games, games_won, current_streak, max_streak, guess_distribution
                FROM statistics WHERE user_id = ?
            ''', (user_id,))
            
            stats_row = cursor.fetchone()
            if not stats_row:
                return self._get_empty_stats()
            
            total_games, games_won, current_streak, max_streak, guess_dist_json = stats_row
            guess_distribution = json.loads(guess_dist_json) if guess_dist_json else {}
            
            # Calculate win rate
            win_rate = (games_won / total_games * 100) if total_games > 0 else 0
            
            # Calculate average guesses (only for won games)
            total_guesses = sum(int(k) * v for k, v in guess_distribution.items())
            average_guesses = total_guesses / games_won if games_won > 0 else 0
            
            return {
                "total_games": total_games,
                "games_won": games_won,
                "games_lost": total_games - games_won,
                "win_rate": round(win_rate, 1),
                "current_streak": current_streak,
                "max_streak": max_streak,
                "average_guesses": round(average_guesses, 2),
                "guess_distribution": guess_distribution
            }
            
        finally:
            conn.close()
    
    def get_difficulty_statistics(self, user_id: int) -> Dict:
        """Get statistics broken down by difficulty"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT difficulty, total_games, games_won, current_streak, 
                       max_streak, guess_distribution, average_guesses
                FROM difficulty_stats WHERE user_id = ?
            ''', (user_id,))
            
            difficulty_stats = {}
            for row in cursor.fetchall():
                difficulty, total_games, games_won, current_streak, max_streak, guess_dist_json, avg_guesses = row
                guess_distribution = json.loads(guess_dist_json) if guess_dist_json else {}
                
                win_rate = (games_won / total_games * 100) if total_games > 0 else 0
                
                difficulty_stats[difficulty] = {
                    "total_games": total_games,
                    "games_won": games_won,
                    "games_lost": total_games - games_won,
                    "win_rate": round(win_rate, 1),
                    "current_streak": current_streak,
                    "max_streak": max_streak,
                    "average_guesses": round(avg_guesses, 2),
                    "guess_distribution": guess_distribution
                }
            
            return difficulty_stats
            
        finally:
            conn.close()
    
    def get_game_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get recent game history for the user"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, word, difficulty, guess_count, won, completed_at, guesses
                FROM games 
                WHERE user_id = ? AND completed_at IS NOT NULL
                ORDER BY completed_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                game_id, word, difficulty, guess_count, won, completed_at, guesses_json = row
                guesses = json.loads(guesses_json) if guesses_json else []
                
                # Parse completed_at datetime
                try:
                    completed_dt = datetime.fromisoformat(completed_at)
                    if completed_dt.tzinfo is None:
                        completed_dt = pytz.timezone(DEFAULT_TIMEZONE).localize(completed_dt)
                except:
                    completed_dt = datetime.now(pytz.timezone(DEFAULT_TIMEZONE))
                
                history.append({
                    "game_id": game_id,
                    "word": word,
                    "difficulty": difficulty,
                    "guess_count": guess_count,
                    "won": bool(won),
                    "completed_at": completed_dt.isoformat(),
                    "guesses": [guess["guess"] for guess in guesses]
                })
            
            return history
            
        finally:
            conn.close()
    
    def get_detailed_statistics(self, user_id: int) -> Dict:
        """Get comprehensive statistics including recent performance"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get overall stats
            overall_stats = self.get_user_statistics(user_id)
            difficulty_stats = self.get_difficulty_statistics(user_id)
            
            # Get recent performance (last 7 days)
            seven_days_ago = datetime.now(pytz.timezone(DEFAULT_TIMEZONE)) - timedelta(days=7)
            cursor.execute('''
                SELECT COUNT(*) as recent_games, SUM(CASE WHEN won THEN 1 ELSE 0 END) as recent_wins
                FROM games 
                WHERE user_id = ? AND completed_at >= ? AND completed_at IS NOT NULL
            ''', (user_id, seven_days_ago.isoformat()))
            
            recent_row = cursor.fetchone()
            recent_games = recent_row[0] if recent_row else 0
            recent_wins = recent_row[1] if recent_row else 0
            recent_win_rate = (recent_wins / recent_games * 100) if recent_games > 0 else 0
            
            # Get best and worst performing difficulties
            best_difficulty = None
            worst_difficulty = None
            best_win_rate = 0
            worst_win_rate = 100
            
            for difficulty, stats in difficulty_stats.items():
                if stats["total_games"] >= 3:  # Only consider difficulties with at least 3 games
                    if stats["win_rate"] > best_win_rate:
                        best_win_rate = stats["win_rate"]
                        best_difficulty = difficulty
                    if stats["win_rate"] < worst_win_rate:
                        worst_win_rate = stats["win_rate"]
                        worst_difficulty = difficulty
            
            return {
                "overall": overall_stats,
                "by_difficulty": difficulty_stats,
                "recent_performance": {
                    "games_last_7_days": recent_games,
                    "wins_last_7_days": recent_wins,
                    "win_rate_last_7_days": round(recent_win_rate, 1)
                },
                "insights": {
                    "best_difficulty": best_difficulty,
                    "worst_difficulty": worst_difficulty,
                    "most_common_guess_count": self._get_most_common_guess_count(overall_stats["guess_distribution"])
                }
            }
            
        finally:
            conn.close()
    
    def _get_empty_stats(self) -> Dict:
        """Return empty statistics structure"""
        return {
            "total_games": 0,
            "games_won": 0,
            "games_lost": 0,
            "win_rate": 0.0,
            "current_streak": 0,
            "max_streak": 0,
            "average_guesses": 0.0,
            "guess_distribution": {}
        }
    
    def _get_most_common_guess_count(self, guess_distribution: Dict) -> Optional[int]:
        """Get the most common number of guesses for won games"""
        if not guess_distribution:
            return None
        
        max_count = 0
        most_common = None
        
        for guess_count, count in guess_distribution.items():
            if count > max_count:
                max_count = count
                most_common = int(guess_count)
        
        return most_common


# Global statistics service instance
stats_service = StatisticsService()
