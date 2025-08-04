"""
User balance management service
"""
import sqlite3
from typing import Dict, Any, Optional, List
from core.database import db_manager
from datetime import datetime


class BalanceService:
    """Service to handle user balance and earnings"""
    
    def __init__(self):
        self.init_balance_tables()
    
    def init_balance_tables(self):
        """Initialize balance-related database tables"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # User balances table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    balance INTEGER DEFAULT 1000,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Transaction history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balance_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    game_type TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Game earnings configuration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_type TEXT UNIQUE NOT NULL,
                    base_reward INTEGER NOT NULL,
                    difficulty_multiplier TEXT DEFAULT '{}',
                    streak_bonus INTEGER DEFAULT 0,
                    perfect_bonus INTEGER DEFAULT 0
                )
            ''')
            
            # Insert default earning rates if not exists
            cursor.execute('SELECT COUNT(*) FROM game_earnings')
            if cursor.fetchone()[0] == 0:
                default_earnings = [
                    ('wordle', 50, '{"easy": 1.0, "medium": 1.2, "hard": 1.5}', 10, 25),
                    ('hangman', 30, '{"easy": 1.0, "medium": 1.3, "hard": 1.6}', 5, 15),
                    ('morphle', 40, '{"easy": 1.0, "medium": 1.4, "hard": 1.8}', 8, 20),
                    ('roulette', 0, '{}', 0, 0)  # Roulette is gambling, no base reward
                ]
                cursor.executemany('''
                    INSERT INTO game_earnings (game_type, base_reward, difficulty_multiplier, streak_bonus, perfect_bonus)
                    VALUES (?, ?, ?, ?, ?)
                ''', default_earnings)
            
            conn.commit()
        finally:
            conn.close()
    
    def get_user_balance(self, user_id: int) -> Dict[str, Any]:
        """Get user's current balance and statistics"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create balance record if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO user_balances (user_id, balance)
                VALUES (?, 1000)
            ''', (user_id,))
            
            # Get balance info
            cursor.execute('''
                SELECT balance, total_earned, total_spent, created_at, updated_at
                FROM user_balances
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                conn.commit()
                return {
                    'balance': row[0],
                    'total_earned': row[1],
                    'total_spent': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                }
            
            conn.commit()
            return {'balance': 1000, 'total_earned': 0, 'total_spent': 0}
        
        finally:
            conn.close()
    
    def add_balance(self, user_id: int, amount: int, transaction_type: str, 
                   game_type: str = None, description: str = None) -> bool:
        """Add money to user's balance"""
        if amount <= 0:
            return False
            
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create balance record if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO user_balances (user_id, balance)
                VALUES (?, 1000)
            ''', (user_id,))
            
            # Update balance
            cursor.execute('''
                UPDATE user_balances 
                SET balance = balance + ?,
                    total_earned = total_earned + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, amount, user_id))
            
            # Record transaction
            cursor.execute('''
                INSERT INTO balance_transactions 
                (user_id, amount, transaction_type, game_type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, transaction_type, game_type, description))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def subtract_balance(self, user_id: int, amount: int, transaction_type: str,
                        game_type: str = None, description: str = None) -> bool:
        """Subtract money from user's balance"""
        if amount <= 0:
            return False
            
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check current balance
            cursor.execute('SELECT balance FROM user_balances WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if not row or row[0] < amount:
                return False  # Insufficient funds
            
            # Update balance
            cursor.execute('''
                UPDATE user_balances 
                SET balance = balance - ?,
                    total_spent = total_spent + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, amount, user_id))
            
            # Record transaction
            cursor.execute('''
                INSERT INTO balance_transactions 
                (user_id, amount, transaction_type, game_type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, -amount, transaction_type, game_type, description))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def calculate_game_reward(self, game_type: str, won: bool, difficulty: str = "medium",
                             perfect_score: bool = False, streak: int = 0) -> int:
        """Calculate reward for completing a game"""
        if not won:
            return 0
            
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT base_reward, difficulty_multiplier, streak_bonus, perfect_bonus
                FROM game_earnings
                WHERE game_type = ?
            ''', (game_type,))
            
            row = cursor.fetchone()
            if not row:
                return 0
            
            base_reward, difficulty_mult_json, streak_bonus, perfect_bonus = row
            
            # Parse difficulty multiplier
            import json
            difficulty_multipliers = json.loads(difficulty_mult_json) if difficulty_mult_json else {}
            difficulty_mult = difficulty_multipliers.get(difficulty, 1.0)
            
            # Calculate total reward
            reward = int(base_reward * difficulty_mult)
            
            # Add streak bonus
            if streak > 1:
                reward += min(streak * streak_bonus, streak_bonus * 10)  # Cap streak bonus
            
            # Add perfect score bonus
            if perfect_score:
                reward += perfect_bonus
            
            return reward
            
        finally:
            conn.close()
    
    def get_transaction_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's recent transaction history"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT amount, transaction_type, game_type, description, created_at
                FROM balance_transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            return [
                {
                    'amount': row[0],
                    'transaction_type': row[1],
                    'game_type': row[2],
                    'description': row[3],
                    'created_at': row[4]
                }
                for row in cursor.fetchall()
            ]
            
        finally:
            conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by balance"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT u.username, ub.balance, ub.total_earned
                FROM user_balances ub
                JOIN users u ON ub.user_id = u.id
                ORDER BY ub.balance DESC
                LIMIT ?
            ''', (limit,))
            
            return [
                {
                    'username': row[0],
                    'balance': row[1],
                    'total_earned': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        finally:
            conn.close()


# Global balance service instance
balance_service = BalanceService()
